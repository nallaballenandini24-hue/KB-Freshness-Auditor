"""Audit result repository"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime

from app.models.models import AuditResult
from app.repositories.base import BaseRepository


class AuditResultRepository(BaseRepository[AuditResult]):
    """Repository for AuditResult model"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditResult)

    async def get_by_article_id(self, article_id: str) -> List[AuditResult]:
        """Get audit results by article ID"""
        stmt = select(self.model).where(self.model.article_id == article_id).order_by(desc(self.model.audit_date))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_latest_by_article_id(self, article_id: str) -> Optional[AuditResult]:
        """Get latest audit result for article"""
        stmt = (
            select(self.model)
            .where(self.model.article_id == article_id)
            .order_by(desc(self.model.audit_date))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_status(self, status: str, limit: int = 100, offset: int = 0) -> List[AuditResult]:
        """Get audit results by status"""
        stmt = (
            select(self.model)
            .where(self.model.status == status)
            .order_by(desc(self.model.audit_date))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_status(self, status: str) -> int:
        """Count audit results by status"""
        stmt = select(func.count(self.model.id)).where(self.model.status == status)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_top_stale_articles(self, limit: int = 10) -> List[AuditResult]:
        """Get top stale articles"""
        stmt = (
            select(self.model)
            .order_by(desc(self.model.freshness_score))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_recent_audits(self, limit: int = 10) -> List[AuditResult]:
        """Get recent audits"""
        stmt = (
            select(self.model)
            .order_by(desc(self.model.audit_date))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
