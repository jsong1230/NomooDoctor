# Attorney Repository
from typing import Optional
from uuid import UUID
from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.attorney import LaborAttorney, AttorneyCase, AttorneyReview


class AttorneyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_attorneys(
        self,
        specialty: Optional[str] = None,
        region: Optional[str] = None,
        sort: str = "rating",
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        query = select(LaborAttorney).where(LaborAttorney.is_active == True)

        if specialty:
            query = query.where(LaborAttorney.specialties.contains([specialty]))
        if region:
            query = query.where(LaborAttorney.regions.contains([region]))

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Sort
        if sort == "fee":
            query = query.order_by(asc(LaborAttorney.consultation_fee))
        elif sort == "experience":
            query = query.order_by(desc(LaborAttorney.experience_years))
        else:
            query = query.order_by(desc(LaborAttorney.rating))

        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        return {"attorneys": list(result.scalars().all()), "total_count": total}

    async def get_by_id(self, attorney_id: UUID) -> Optional[LaborAttorney]:
        result = await self.db.execute(
            select(LaborAttorney).where(LaborAttorney.id == attorney_id)
        )
        return result.scalar_one_or_none()

    async def update_rating(self, attorney_id: UUID) -> None:
        """리뷰 기반 평균 평점 재계산"""
        result = await self.db.execute(
            select(
                func.avg(AttorneyReview.rating),
                func.count(AttorneyReview.id)
            ).where(AttorneyReview.attorney_id == attorney_id)
        )
        row = result.one()
        avg_rating = float(row[0]) if row[0] else 0.0
        count = row[1] or 0

        attorney = await self.get_by_id(attorney_id)
        if attorney:
            attorney.rating = round(avg_rating, 1)
            attorney.review_count = count
            await self.db.flush()


class CaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, case: AttorneyCase) -> AttorneyCase:
        self.db.add(case)
        await self.db.flush()
        await self.db.refresh(case)
        return case

    async def get_by_id(self, case_id: UUID) -> Optional[AttorneyCase]:
        result = await self.db.execute(
            select(AttorneyCase).where(AttorneyCase.id == case_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        query = select(AttorneyCase).where(AttorneyCase.user_id == user_id)
        if status:
            query = query.where(AttorneyCase.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        query = query.order_by(desc(AttorneyCase.created_at)).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return {"cases": list(result.scalars().all()), "total_count": total}


class ReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, review: AttorneyReview) -> AttorneyReview:
        self.db.add(review)
        await self.db.flush()
        await self.db.refresh(review)
        return review

    async def get_by_case_id(self, case_id: UUID) -> Optional[AttorneyReview]:
        result = await self.db.execute(
            select(AttorneyReview).where(AttorneyReview.case_id == case_id)
        )
        return result.scalar_one_or_none()

    async def list_by_attorney(
        self,
        attorney_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        query = select(AttorneyReview).where(
            AttorneyReview.attorney_id == attorney_id
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        query = query.order_by(desc(AttorneyReview.created_at)).offset(offset).limit(limit)
        result = await self.db.execute(query)
        reviews = list(result.scalars().all())

        return {"reviews": reviews, "total_count": total}
