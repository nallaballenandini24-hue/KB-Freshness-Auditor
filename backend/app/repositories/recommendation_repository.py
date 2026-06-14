"""AI Recommendation repository"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.models import AIRecommendation
from app.repositories.base import BaseRepository


class AIRecommendationRepository(BaseRepository[AIRecommendation]):
    """Repository for AIRecommendation model"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, AIRecommendation)

    async def get_by_article_id(self, article_id: str) -> List[AIRecommendation]:
        """Get recommendations by article ID"""
        stmt = (
            select(self.model)
            .where(self.model.article_id == article_id)
            .order_by(desc(self.model.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_pending_recommendations(
        self, limit: int = 10, offset: int = 0
    ) -> List[AIRecommendation]:
        """Get pending recommendations"""
        stmt = (
            select(self.model)
            .where((self.model.accepted == False) & (self.model.rejected == False))
            .order_by(desc(self.model.confidence_score))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_pending_recommendations(self) -> int:
        """Count pending recommendations"""
        stmt = select(func.count(self.model.id)).where(
            (self.model.accepted == False) & (self.model.rejected == False)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_by_type(self, recommendation_type: str, limit: int = 10) -> List[AIRecommendation]:
        """Get recommendations by type"""
        stmt = (
            select(self.model)
            .where(self.model.recommendation_type == recommendation_type)
            .order_by(desc(self.model.confidence_score))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_accepted(self) -> int:
        """Count accepted recommendations"""
        stmt = select(func.count(self.model.id)).where(self.model.accepted == True)
        result = await self.session.execute(stmt)
        return result.scalar() or 0
