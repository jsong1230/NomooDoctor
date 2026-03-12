# Attorney Service
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.db.models.attorney import LaborAttorney, AttorneyCase, AttorneyReview
from app.repositories.attorney_repo import AttorneyRepository, CaseRepository, ReviewRepository
from app.schemas.attorney import (
    AttorneyResponse, AttorneyDetailResponse,
    CaseResponse, CaseCreateResult,
    ReviewResponse, ReviewCreateResult,
    CreateCaseRequest, CreateReviewRequest,
)
from app.core.exceptions import NotFoundError, ConflictError, ValidationError, AppError
from fastapi import status as http_status


# === 예외 클래스 ===
class AttorneyNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__(message="노무사를 찾을 수 없습니다.", code="E-8001")


class CaseNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__(message="케이스를 찾을 수 없습니다.", code="E-8002")


class ReviewAlreadyExistsError(ConflictError):
    def __init__(self) -> None:
        super().__init__(message="이미 리뷰를 작성하셨습니다.", code="E-8003")


class InvalidCaseStatusError(ValidationError):
    def __init__(self) -> None:
        super().__init__(message="현재 상태에서는 취소할 수 없습니다.", code="E-8004")


class AttorneyUsageLimitError(AppError):
    def __init__(self) -> None:
        super().__init__(
            message="이번 달 무료 노무사 상담 횟수를 초과했습니다.",
            code="E-8005",
            status_code=http_status.HTTP_403_FORBIDDEN,
        )


class InvalidRatingError(ValidationError):
    def __init__(self) -> None:
        super().__init__(message="평점은 1~5 사이여야 합니다.", code="E-8006")


def _attorney_to_response(a: LaborAttorney) -> AttorneyResponse:
    return AttorneyResponse(
        id=a.id,
        name=a.name,
        firm_name=a.firm_name,
        specialties=a.specialties,
        regions=a.regions,
        consultation_fee=a.consultation_fee,
        experience_years=a.experience_years,
        rating=float(a.rating),
        review_count=a.review_count,
        response_rate=int(a.response_rate),
        bio=a.bio,
        profile_image_url=a.profile_image_url,
        verified=a.verified,
    )


def _review_to_response(r: AttorneyReview) -> ReviewResponse:
    return ReviewResponse(
        id=r.id,
        rating=r.rating,
        comment=r.comment,
        user_name=r.user.name if r.user else "익명",
        created_at=r.created_at,
    )


class AttorneyService:
    """노무사 서비스"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.attorney_repo = AttorneyRepository(db)
        self.case_repo = CaseRepository(db)
        self.review_repo = ReviewRepository(db)

    async def list_attorneys(
        self,
        specialty: Optional[str] = None,
        region: Optional[str] = None,
        sort: str = "rating",
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        result = await self.attorney_repo.list_attorneys(
            specialty=specialty, region=region, sort=sort, limit=limit, offset=offset
        )
        attorneys = [_attorney_to_response(a) for a in result["attorneys"]]
        return {"attorneys": attorneys, "total_count": result["total_count"]}

    async def get_attorney(self, attorney_id: UUID) -> AttorneyDetailResponse:
        attorney = await self.attorney_repo.get_by_id(attorney_id)
        if not attorney:
            raise AttorneyNotFoundError()

        reviews_data = await self.review_repo.list_by_attorney(attorney_id, limit=5)
        recent_reviews = []
        for r in reviews_data["reviews"]:
            # 리뷰에서 user 이름 가져오기
            from sqlalchemy import select
            from app.db.models.user import User as UserModel
            user_result = await self.db.execute(
                select(UserModel.name).where(UserModel.id == r.user_id)
            )
            user_name = user_result.scalar_one_or_none() or "익명"
            recent_reviews.append(ReviewResponse(
                id=r.id,
                rating=r.rating,
                comment=r.comment,
                user_name=user_name,
                created_at=r.created_at,
            ))

        return AttorneyDetailResponse(
            attorney=_attorney_to_response(attorney),
            recent_reviews=recent_reviews,
        )

    async def create_case(
        self, user: User, data: CreateCaseRequest
    ) -> CaseCreateResult:
        # 노무사 존재 확인
        attorney = await self.attorney_repo.get_by_id(data.attorney_id)
        if not attorney:
            raise AttorneyNotFoundError()

        # AI 케이스 요약 생성
        case_summary = await self._generate_summary(data)

        case = AttorneyCase(
            user_id=user.id,
            attorney_id=data.attorney_id,
            company_id=data.company_id,
            chat_session_id=data.chat_session_id,
            case_summary=case_summary,
            case_type=data.case_type,
            urgency=data.urgency,
            consultation_type=data.consultation_type,
            preferred_schedule={"dates": data.preferred_schedule} if data.preferred_schedule else None,
            consultation_fee=attorney.consultation_fee,
        )

        case = await self.case_repo.create(case)
        await self.db.commit()

        return CaseCreateResult(
            case_id=case.id,
            case_summary=case.case_summary,
            status=case.status,
            consultation_fee=case.consultation_fee,
        )

    async def list_my_cases(
        self, user: User, status: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> dict:
        result = await self.case_repo.list_by_user(
            user_id=user.id, status=status, limit=limit, offset=offset
        )
        cases = []
        for c in result["cases"]:
            attorney = await self.attorney_repo.get_by_id(c.attorney_id)
            cases.append(CaseResponse(
                id=c.id,
                attorney_id=c.attorney_id,
                attorney_name=attorney.name if attorney else "알 수 없음",
                case_summary=c.case_summary,
                case_type=c.case_type,
                urgency=c.urgency,
                status=c.status,
                consultation_type=c.consultation_type,
                consultation_fee=c.consultation_fee,
                scheduled_at=c.scheduled_at,
                fee_paid=c.fee_paid,
                completed_at=c.completed_at,
                created_at=c.created_at,
            ))
        return {"cases": cases, "total_count": result["total_count"]}

    async def get_case(self, user: User, case_id: UUID) -> CaseResponse:
        case = await self.case_repo.get_by_id(case_id)
        if not case or case.user_id != user.id:
            raise CaseNotFoundError()

        attorney = await self.attorney_repo.get_by_id(case.attorney_id)
        return CaseResponse(
            id=case.id,
            attorney_id=case.attorney_id,
            attorney_name=attorney.name if attorney else "알 수 없음",
            case_summary=case.case_summary,
            case_type=case.case_type,
            urgency=case.urgency,
            status=case.status,
            consultation_type=case.consultation_type,
            consultation_fee=case.consultation_fee,
            scheduled_at=case.scheduled_at,
            fee_paid=case.fee_paid,
            completed_at=case.completed_at,
            created_at=case.created_at,
        )

    async def cancel_case(self, user: User, case_id: UUID) -> dict:
        case = await self.case_repo.get_by_id(case_id)
        if not case or case.user_id != user.id:
            raise CaseNotFoundError()

        if case.status not in ("pending", "accepted"):
            raise InvalidCaseStatusError()

        case.status = "cancelled"
        await self.db.commit()
        return {"status": "cancelled"}

    async def create_review(
        self, user: User, case_id: UUID, data: CreateReviewRequest
    ) -> ReviewCreateResult:
        case = await self.case_repo.get_by_id(case_id)
        if not case or case.user_id != user.id:
            raise CaseNotFoundError()

        if data.rating < 1 or data.rating > 5:
            raise InvalidRatingError()

        # 중복 리뷰 확인
        existing = await self.review_repo.get_by_case_id(case_id)
        if existing:
            raise ReviewAlreadyExistsError()

        review = AttorneyReview(
            case_id=case_id,
            user_id=user.id,
            attorney_id=case.attorney_id,
            rating=data.rating,
            comment=data.comment,
        )
        review = await self.review_repo.create(review)

        # 평점 업데이트
        await self.attorney_repo.update_rating(case.attorney_id)
        await self.db.commit()

        return ReviewCreateResult(review_id=review.id)

    async def list_reviews(
        self, attorney_id: UUID, limit: int = 20, offset: int = 0
    ) -> dict:
        attorney = await self.attorney_repo.get_by_id(attorney_id)
        if not attorney:
            raise AttorneyNotFoundError()

        result = await self.review_repo.list_by_attorney(attorney_id, limit=limit, offset=offset)
        reviews = []
        for r in result["reviews"]:
            from sqlalchemy import select
            from app.db.models.user import User as UserModel
            user_result = await self.db.execute(
                select(UserModel.name).where(UserModel.id == r.user_id)
            )
            user_name = user_result.scalar_one_or_none() or "익명"
            reviews.append(ReviewResponse(
                id=r.id,
                rating=r.rating,
                comment=r.comment,
                user_name=user_name,
                created_at=r.created_at,
            ))
        return {"reviews": reviews, "total_count": result["total_count"]}

    async def _generate_summary(self, data: CreateCaseRequest) -> str:
        """AI 케이스 요약 생성 (mock)"""
        # chat_session_id가 있으면 실제로는 Claude API로 요약 생성
        # 현재는 mock 반환
        if data.description:
            return data.description

        type_labels = {
            "dismissal": "해고/퇴직",
            "wage": "임금/수당",
            "leave": "휴가/휴직",
            "industrial_accident": "산업재해",
            "harassment": "직장 내 괴롭힘",
            "other": "기타 노무 상담",
        }
        urgency_labels = {
            "low": "일반",
            "medium": "주의",
            "high": "긴급",
            "emergency": "즉시 대응 필요",
        }
        return (
            f"[{type_labels.get(data.case_type, data.case_type)}] "
            f"긴급도: {urgency_labels.get(data.urgency, data.urgency)}. "
            f"AI 상담 세션 기반 케이스 요약이 자동 생성되었습니다."
        )
