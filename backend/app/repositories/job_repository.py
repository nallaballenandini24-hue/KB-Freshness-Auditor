"""Audit job repository"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.models import AuditJob
from app.repositories.base import BaseRepository


class AuditJobRepository(BaseRepository[AuditJob]):
    """Repository for AuditJob model"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditJob)

    async def get_latest_job(self) -> Optional[AuditJob]:
        """Get latest audit job"""
        stmt = select(self.model).order_by(desc(self.model.created_at)).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_workflow_id(self, workflow_id: str) -> Optional[AuditJob]:
        """Get job by workflow ID"""
        stmt = select(self.model).where(self.model.workflow_id == workflow_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_status(self, status: str, limit: int = 10) -> List[AuditJob]:
        """Get jobs by status"""
        stmt = (
            select(self.model)
            .where(self.model.status == status)
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_recent_jobs(self, limit: int = 10) -> List[AuditJob]:
        """Get recent jobs"""
        stmt = select(self.model).order_by(desc(self.model.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
