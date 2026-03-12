# WorkRule Repository
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import uuid

from app.db.models.work_rule import WorkRule


class WorkRuleRepository:
    """WorkRule CRUD 작업을 담당하는 Repository"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, work_rule_id: uuid.UUID | str) -> Optional[WorkRule]:
        """ID로 취업규칙 조회"""
        if isinstance(work_rule_id, str):
            work_rule_id = uuid.UUID(work_rule_id)

        stmt = select(WorkRule).where(WorkRule.id == work_rule_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_company(
        self, work_rule_id: uuid.UUID | str, company_id: uuid.UUID | str
    ) -> Optional[WorkRule]:
        """ID와 company_id로 취업규칙 조회"""
        if isinstance(work_rule_id, str):
            work_rule_id = uuid.UUID(work_rule_id)
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)

        stmt = select(WorkRule).where(
            WorkRule.id == work_rule_id,
            WorkRule.company_id == company_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_company(
        self,
        company_id: uuid.UUID | str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[WorkRule]:
        """사업장별 취업규칙 목록 조회"""
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)

        stmt = select(WorkRule).where(WorkRule.company_id == company_id)

        if status:
            stmt = stmt.where(WorkRule.status == status)

        stmt = stmt.order_by(WorkRule.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_company(
        self, company_id: uuid.UUID | str, status: Optional[str] = None
    ) -> int:
        """사업장별 취업규칙 수 조회"""
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)

        stmt = select(func.count(WorkRule.id)).where(WorkRule.company_id == company_id)

        if status:
            stmt = stmt.where(WorkRule.status == status)

        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def get_active_by_company(self, company_id: uuid.UUID | str) -> Optional[WorkRule]:
        """사업장의 active 취업규칙 조회"""
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)

        stmt = select(WorkRule).where(
            WorkRule.company_id == company_id,
            WorkRule.status == "active"
        ).order_by(WorkRule.version.desc()).limit(1)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_version(self, company_id: uuid.UUID | str) -> int:
        """사업장의 최신 버전 조회"""
        if isinstance(company_id, str):
            company_id = uuid.UUID(company_id)

        stmt = select(func.max(WorkRule.version)).where(WorkRule.company_id == company_id)
        result = await self.db.execute(stmt)
        return (result.scalar() or 0) + 1

    async def create(
        self,
        company_id: uuid.UUID,
        version: int = 1,
        status: str = "draft",
        content: dict | None = None,
        industry_type: str = "other",
        effective_date: Optional[date] = None,
        approval_date: Optional[date] = None,
        worker_consent_count: Optional[int] = None,
        total_worker_count: Optional[int] = None,
        ai_generated: bool = False,
        ai_model: Optional[str] = None,
        revision_reason: Optional[str] = None,
        cover_docx_url: Optional[str] = None
    ) -> WorkRule:
        """취업규칙 생성"""
        work_rule = WorkRule(
            company_id=company_id,
            version=version,
            status=status,
            content=content or {},
            industry_type=industry_type,
            effective_date=effective_date,
            approval_date=approval_date,
            worker_consent_count=worker_consent_count,
            total_worker_count=total_worker_count,
            ai_generated=ai_generated,
            ai_model=ai_model,
            revision_reason=revision_reason,
            cover_docx_url=cover_docx_url
        )
        self.db.add(work_rule)
        await self.db.flush()
        await self.db.refresh(work_rule)
        return work_rule

    async def update(
        self,
        work_rule: WorkRule,
        content: Optional[dict] = None,
        status: Optional[str] = None,
        effective_date: Optional[date] = None,
        approval_date: Optional[date] = None,
        worker_consent_count: Optional[int] = None,
        total_worker_count: Optional[int] = None,
        ai_generated: Optional[bool] = None,
        ai_model: Optional[str] = None,
        revision_reason: Optional[str] = None,
        cover_docx_url: Optional[str] = None,
        docx_url: Optional[str] = None,
        pdf_url: Optional[str] = None,
        filed_at: Optional[object] = None
    ) -> WorkRule:
        """취업규칙 수정"""
        if content is not None:
            work_rule.content = content
        if status is not None:
            work_rule.status = status
        if effective_date is not None:
            work_rule.effective_date = effective_date
        if approval_date is not None:
            work_rule.approval_date = approval_date
        if worker_consent_count is not None:
            work_rule.worker_consent_count = worker_consent_count
        if total_worker_count is not None:
            work_rule.total_worker_count = total_worker_count
        if ai_generated is not None:
            work_rule.ai_generated = ai_generated
        if ai_model is not None:
            work_rule.ai_model = ai_model
        if revision_reason is not None:
            work_rule.revision_reason = revision_reason
        if cover_docx_url is not None:
            work_rule.cover_docx_url = cover_docx_url
        if docx_url is not None:
            work_rule.docx_url = docx_url
        if pdf_url is not None:
            work_rule.pdf_url = pdf_url
        if filed_at is not None:
            work_rule.filed_at = filed_at

        await self.db.flush()
        await self.db.refresh(work_rule)
        return work_rule

    async def delete(self, work_rule: WorkRule) -> None:
        """취업규칙 삭제"""
        await self.db.delete(work_rule)
        await self.db.flush()
