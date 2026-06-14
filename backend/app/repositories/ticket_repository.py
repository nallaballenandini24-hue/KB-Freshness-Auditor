"""Ticket repository"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.models import Ticket
from app.repositories.base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    """Repository for Ticket model"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Ticket)

    async def get_by_article_id(self, article_id: str) -> List[Ticket]:
        """Get tickets by article ID"""
        stmt = select(self.model).where(self.model.article_id == article_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_article_id(self, article_id: str) -> int:
        """Count tickets by article ID"""
        stmt = select(func.count(self.model.id)).where(self.model.article_id == article_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_by_ticket_id(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ticket ID"""
        stmt = select(self.model).where(self.model.ticket_id == ticket_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_subject(self, query: str, limit: int = 10) -> List[Ticket]:
        """Search tickets by subject"""
        search_pattern = f"%{query}%"
        stmt = (
            select(self.model)
            .where(self.model.subject.ilike(search_pattern))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_all_tickets(self) -> int:
        """Count all tickets"""
        stmt = select(func.count(self.model.id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_unresolved_tickets(self) -> List[Ticket]:
        """Get unresolved tickets"""
        stmt = select(self.model).where(self.model.resolved == False)
        result = await self.session.execute(stmt)
        return result.scalars().all()
