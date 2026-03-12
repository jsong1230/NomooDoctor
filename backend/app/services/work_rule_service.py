# 취업규칙 서비스
from typing import Optional, Any
from datetime import datetime, date
import uuid
import os
import json

from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis

from app.db.models.work_rule import WorkRule
from app.repositories.work_rule_repo import WorkRuleRepository
from app.repositories.company_repo import CompanyRepository
from app.core.exceptions import (
    ValidationError,
    NotFoundError,
    ForbiddenError,
)
from app.services.work_rule_templates import get_template, get_all_templates


class WorkRuleService:
    """취업규칙 관련 비즈니스 로직"""

    def __init__(self, db: AsyncSession, redis: aioredis.Redis) -> None:
        self.db = db
        self.repo = WorkRuleRepository(db)
        self.company_repo = CompanyRepository(db)
        self.redis = redis

    async def create_work_rule(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        industry_type: str,
        effective_date: Optional[date] = None
    ) -> dict[str, Any]:
        """
        취업규칙 초안 생성 (템플릿 기반)

        Args:
            company_id: 사업장 ID
            user_id: 사용자 ID
            industry_type: 업종
            effective_date: 효력 발생일

        Returns:
            생성된 취업규칙 데이터

        Raises:
            ValidationError: 잘못된 업종
            NotFoundError: 사업장 없음
        """
        # 사업장 확인
        company = await self.company_repo.get_by_id(company_id)
        if not company:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        # 업종 템플릿 로드
        template = get_template(industry_type)
        if not template:
            raise ValidationError(
                message="지원하지 않는 업종입니다.",
                details=[{"field": "industry_type", "message": f"지원 업종: manufacturing, food_service, service, it"}]
            )

        # 14개 법정 섹션 초기화
        sections = []
        for section in template["sections"]:
            sections.append({
                "section_number": section["section_number"],
                "title": section["title"],
                "content_html": section.get("content_template", f"<p>{section['title']} 내용</p>"),
                "is_required": True,
                "law_reference": section["description"]
            })

        content = {"sections": sections}

        # 최신 버전 조회
        latest_version = await self.repo.get_latest_version(company_id)

        # 취업규칙 생성
        work_rule = await self.repo.create(
            company_id=company_id,
            version=latest_version,
            status="draft",
            content=content,
            industry_type=industry_type,
            effective_date=effective_date
        )

        await self.db.commit()

        return self._work_rule_to_dict(work_rule)

    async def get_work_rules(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        status: Optional[str] = None,
        limit: int = 20,
        skip: int = 0
    ) -> dict[str, Any]:
        """
        취업규칙 목록 조회

        Args:
            company_id: 사업장 ID
            user_id: 사용자 ID
            status: 상태 필터
            limit: 한 번에 조회할 개수
            skip: 건너뛸 개수

        Returns:
            취업규칙 목록 및 페이지네이션 정보
        """
        # 사업장 확인
        company = await self.company_repo.get_by_id(company_id)
        if not company:
            raise NotFoundError("사업장을 찾을 수 없습니다.")

        # 목록 조회
        work_rules = await self.repo.list_by_company(
            company_id=company_id,
            status=status,
            skip=skip,
            limit=limit
        )

        # 전체 개수 조회
        total_count = await self.repo.count_by_company(company_id, status)

        return {
            "data": [self._work_rule_to_list_item(wr) for wr in work_rules],
            "pagination": {
                "limit": limit,
                "skip": skip,
                "total": total_count,
                "hasNext": (skip + limit) < total_count
            }
        }

    async def get_work_rule(
        self,
        work_rule_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> dict[str, Any]:
        """
        취업규칙 상세 조회

        Args:
            work_rule_id: 취업규칙 ID
            company_id: 사업장 ID
            user_id: 사용자 ID

        Returns:
            취업규칙 상세 정보

        Raises:
            NotFoundError: 취업규칙 없음
        """
        work_rule = await self.repo.get_by_id_and_company(work_rule_id, company_id)
        if not work_rule:
            raise NotFoundError("취업규칙을 찾을 수 없습니다.")

        return self._work_rule_to_dict(work_rule)

    async def update_work_rule(
        self,
        work_rule_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        content: Optional[dict] = None,
        effective_date: Optional[date] = None,
        status: Optional[str] = None,
        worker_consent_count: Optional[int] = None,
        total_worker_count: Optional[int] = None,
        approval_date: Optional[date] = None
    ) -> dict[str, Any]:
        """
        취업규칙 수정

        Args:
            work_rule_id: 취업규칙 ID
            company_id: 사업장 ID
            user_id: 사용자 ID
            content: 수정 내용
            effective_date: 효력 발생일
            status: 상태
            worker_consent_count: 근로자 동의 수
            total_worker_count: 전체 근로자 수
            approval_date: 승인일

        Returns:
            수정된 취업규칙

        Raises:
            NotFoundError: 취업규칙 없음
            ValidationError: 수정 불가 상태
        """
        work_rule = await self.repo.get_by_id_and_company(work_rule_id, company_id)
        if not work_rule:
            raise NotFoundError("취업규칙을 찾을 수 없습니다.")

        # draft/under_review 상태에서만 수정 가능
        if work_rule.status not in ["draft", "under_review"]:
            raise ValidationError(
                message="draft 또는 under_review 상태에서만 수정 가능합니다.",
                details=[{"field": "status", "message": f"현재 상태: {work_rule.status}"}]
            )

        # 수정
        work_rule = await self.repo.update(
            work_rule,
            content=content,
            effective_date=effective_date,
            status=status,
            worker_consent_count=worker_consent_count,
            total_worker_count=total_worker_count,
            approval_date=approval_date
        )

        await self.db.commit()

        return self._work_rule_to_dict(work_rule)

    async def delete_work_rule(
        self,
        work_rule_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> None:
        """
        취업규칙 삭제

        Args:
            work_rule_id: 취업규칙 ID
            company_id: 사업장 ID
            user_id: 사용자 ID

        Raises:
            NotFoundError: 취업규칙 없음
            ValidationError: 삭제 불가 상태 (draft만 가능)
        """
        work_rule = await self.repo.get_by_id_and_company(work_rule_id, company_id)
        if not work_rule:
            raise NotFoundError("취업규칙을 찾을 수 없습니다.")

        # draft 상태에서만 삭제 가능
        if work_rule.status != "draft":
            raise ValidationError(
                message="draft 상태의 취업규칙만 삭제 가능합니다.",
                details=[{"field": "status", "message": f"현재 상태: {work_rule.status}"}]
            )

        await self.repo.delete(work_rule)
        await self.db.commit()

    async def generate_ai_draft(
        self,
        work_rule_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        industry_type: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> dict[str, Any]:
        """
        AI 초안 생성

        Args:
            work_rule_id: 취업규칙 ID
            company_id: 사업장 ID
            user_id: 사용자 ID
            industry_type: 업종 (선택)
            additional_context: 추가 컨텍스트

        Returns:
            생성된 AI 초안

        Raises:
            NotFoundError: 취업규칙 없음
            ValidationError: draft 상태가 아님
        """
        work_rule = await self.repo.get_by_id_and_company(work_rule_id, company_id)
        if not work_rule:
            raise NotFoundError("취업규칙을 찾을 수 없습니다.")

        # draft 상태에서만 가능
        if work_rule.status != "draft":
            raise ValidationError(
                message="draft 상태의 취업규칙만 AI 생성 가능합니다.",
                details=[{"field": "status", "message": f"현재 상태: {work_rule.status}"}]
            )

        # 업종 확인
        use_industry_type = industry_type or work_rule.industry_type
        template = get_template(use_industry_type)
        if not template:
            raise ValidationError("지원하지 않는 업종입니다.")

        # 회사 정보 조회
        company = await self.company_repo.get_by_id(company_id)

        # AI 생성 로직 (현재는 Mock 구현)
        ai_generated_content = await self._call_claude_api(
            industry_type=use_industry_type,
            company_name=company.business_name,
            employee_count=company.employee_count,
            additional_context=additional_context
        )

        # 취업규칙 업데이트
        work_rule = await self.repo.update(
            work_rule,
            content=ai_generated_content,
            ai_generated=True,
            ai_model="claude-sonnet-4-20250514"
        )

        await self.db.commit()

        return self._work_rule_to_dict(work_rule)

    async def revise_work_rule(
        self,
        work_rule_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        revision_reason: str,
        effective_date: Optional[date] = None
    ) -> dict[str, Any]:
        """
        취업규칙 개정 (새 버전 생성)

        Args:
            work_rule_id: 기존 취업규칙 ID (active만 가능)
            company_id: 사업장 ID
            user_id: 사용자 ID
            revision_reason: 개정 사유
            effective_date: 효력 발생일

        Returns:
            새로 생성된 draft 버전

        Raises:
            NotFoundError: 취업규칙 없음
            ValidationError: active 상태가 아님
        """
        work_rule = await self.repo.get_by_id_and_company(work_rule_id, company_id)
        if not work_rule:
            raise NotFoundError("취업규칙을 찾을 수 없습니다.")

        # active 상태만 개정 가능
        if work_rule.status != "active":
            raise ValidationError(
                message="active 상태의 취업규칙만 개정 가능합니다.",
                details=[{"field": "status", "message": f"현재 상태: {work_rule.status}"}]
            )

        # 기존 버전을 superseded로 변경
        work_rule = await self.repo.update(
            work_rule,
            status="superseded"
        )

        # 새 버전 생성
        latest_version = await self.repo.get_latest_version(company_id)
        new_work_rule = await self.repo.create(
            company_id=company_id,
            version=latest_version,
            status="draft",
            content=work_rule.content,
            industry_type=work_rule.industry_type,
            effective_date=effective_date,
            revision_reason=revision_reason,
            total_worker_count=work_rule.total_worker_count
        )

        await self.db.commit()

        return self._work_rule_to_dict(new_work_rule)

    async def generate_download(
        self,
        work_rule_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        file_type: str
    ) -> dict[str, Any]:
        """
        취업규칙 다운로드 (Word/PDF)

        Args:
            work_rule_id: 취업규칙 ID
            company_id: 사업장 ID
            user_id: 사용자 ID
            file_type: "docx" | "pdf"

        Returns:
            다운로드 URL 및 메타 정보

        Raises:
            NotFoundError: 취업규칙 없음
            ValidationError: 지원하지 않는 파일 타입
        """
        work_rule = await self.repo.get_by_id_and_company(work_rule_id, company_id)
        if not work_rule:
            raise NotFoundError("취업규칙을 찾을 수 없습니다.")

        if file_type not in ["docx", "pdf"]:
            raise ValidationError("지원하지 않는 파일 타입입니다.")

        # 현재는 Mock URL 반환
        company = await self.company_repo.get_by_id(company_id)
        filename = f"취업규칙_{company.business_name}_v{work_rule.version}.{file_type}"
        download_url = f"https://s3.example.com/work-rules/{work_rule.id}.{file_type}"

        expires_at = datetime.utcnow().isoformat() + "Z"

        return {
            "download_url": download_url,
            "filename": filename,
            "expires_at": expires_at
        }

    async def generate_cover_document(
        self,
        work_rule_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> dict[str, Any]:
        """
        고용노동부 신고용 커버 서류 생성

        Args:
            work_rule_id: 취업규칙 ID
            company_id: 사업장 ID
            user_id: 사용자 ID

        Returns:
            커버 서류 URL 및 메타 정보

        Raises:
            NotFoundError: 취업규칙 없음
            ValidationError: active 상태가 아님
        """
        work_rule = await self.repo.get_by_id_and_company(work_rule_id, company_id)
        if not work_rule:
            raise NotFoundError("취업규칙을 찾을 수 없습니다.")

        if work_rule.status != "active":
            raise ValidationError("active 상태의 취업규칙만 신고 가능합니다.")

        # 현재는 Mock URL 반환
        company = await self.company_repo.get_by_id(company_id)
        filename = f"취업규칙_신고서_{company.business_name}.docx"
        cover_url = f"https://s3.example.com/work-rules/cover_{work_rule.id}.docx"

        expires_at = datetime.utcnow().isoformat() + "Z"

        return {
            "cover_document_url": cover_url,
            "filename": filename,
            "expires_at": expires_at
        }

    def get_consent_checklist(self, employee_count: int) -> dict[str, Any]:
        """
        근로자 과반수 동의 절차 체크리스트

        Args:
            employee_count: 근로자 수

        Returns:
            체크리스트 및 동의 임계값
        """
        consent_threshold = (employee_count // 2) + 1
        consent_type = "majority"  # 과반수

        checklist = [
            {
                "step": 1,
                "title": "취업규칙 변경(안) 작성",
                "description": "변경할 내용을 명확히 작성합니다.",
                "law_reference": "근로기준법 제94조",
                "is_required": True
            },
            {
                "step": 2,
                "title": "근로자 의견 청취 / 동의 절차",
                "description": "불이익 변경 시 근로자 과반수 동의 필요, 비불이익 변경 시 의견 청취.",
                "law_reference": "근로기준법 제94조 제1항",
                "is_required": True
            },
            {
                "step": 3,
                "title": "고용노동부 신고",
                "description": "취업규칙을 작성/변경 시 관할 지방고용노동청에 신고합니다.",
                "law_reference": "근로기준법 제93조",
                "is_required": True
            }
        ]

        return {
            "checklist": checklist,
            "employee_count": employee_count,
            "consent_threshold": consent_threshold,
            "consent_type": consent_type
        }

    def get_templates(self, industry_type: Optional[str] = None) -> list[dict]:
        """
        업종별 템플릿 조회

        Args:
            industry_type: 업종 (선택, None이면 모두)

        Returns:
            템플릿 목록
        """
        if industry_type:
            template = get_template(industry_type)
            if not template:
                return []
            return [{
                "industry_type": industry_type,
                "industry_name": template["industry_name"],
                "description": template["description"],
                "sections": template["sections"]
            }]

        return get_all_templates()

    async def _call_claude_api(
        self,
        industry_type: str,
        company_name: str,
        employee_count: int,
        additional_context: Optional[str] = None
    ) -> dict:
        """
        Claude API 호출 (Mock 구현)

        현재는 기본 템플릿 반환. 실제 구현 시 Claude API 호출.
        """
        template = get_template(industry_type)
        if not template:
            raise ValidationError("지원하지 않는 업종입니다.")

        # Mock: 템플릿의 content_template을 content_html로 변환
        sections = []
        for section in template["sections"]:
            sections.append({
                "section_number": section["section_number"],
                "title": section["title"],
                "content_html": section.get("content_template", f"<p>{section['title']}</p>"),
                "is_required": True,
                "law_reference": section["description"]
            })

        return {"sections": sections}

    def _work_rule_to_dict(self, work_rule: WorkRule) -> dict[str, Any]:
        """취업규칙 모델을 딕셔너리로 변환"""
        return {
            "id": str(work_rule.id),
            "company_id": str(work_rule.company_id),
            "version": work_rule.version,
            "status": work_rule.status,
            "industry_type": work_rule.industry_type,
            "content": work_rule.content,
            "effective_date": work_rule.effective_date.isoformat() if work_rule.effective_date else None,
            "approval_date": work_rule.approval_date.isoformat() if work_rule.approval_date else None,
            "worker_consent_count": work_rule.worker_consent_count,
            "total_worker_count": work_rule.total_worker_count,
            "revision_reason": work_rule.revision_reason,
            "ai_generated": work_rule.ai_generated,
            "ai_model": work_rule.ai_model,
            "docx_url": work_rule.docx_url,
            "pdf_url": work_rule.pdf_url,
            "filed_at": work_rule.filed_at.isoformat() if work_rule.filed_at else None,
            "created_at": work_rule.created_at.isoformat(),
            "updated_at": work_rule.updated_at.isoformat()
        }

    def _work_rule_to_list_item(self, work_rule: WorkRule) -> dict[str, Any]:
        """취업규칙 모델을 목록 아이템으로 변환"""
        return {
            "id": str(work_rule.id),
            "version": work_rule.version,
            "status": work_rule.status,
            "industry_type": work_rule.industry_type,
            "effective_date": work_rule.effective_date.isoformat() if work_rule.effective_date else None,
            "approval_date": work_rule.approval_date.isoformat() if work_rule.approval_date else None,
            "worker_consent_count": work_rule.worker_consent_count,
            "ai_generated": work_rule.ai_generated,
            "filed_at": work_rule.filed_at.isoformat() if work_rule.filed_at else None,
            "created_at": work_rule.created_at.isoformat(),
            "updated_at": work_rule.updated_at.isoformat()
        }
