"""Article repository"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.models import Article
from app.repositories.base import BaseRepository


class ArticleRepository(BaseRepository[Article]):
    """Repository for Article model"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Article)

    async def search_by_title_or_tags(
        self, query: str, limit: int = 10, offset: int = 0
    ) -> List[Article]:
        """Search articles by title or tags"""
        search_pattern = f"%{query}%"
        stmt = (
            select(self.model)
            .where(
                (self.model.title.ilike(search_pattern))
                | (self.model.tags.ilike(search_pattern))
                | (self.model.description.ilike(search_pattern))
            )
            .where(self.model.is_active == True)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_active_articles(self, limit: int = 100, offset: int = 0) -> List[Article]:
        """Get active articles"""
        stmt = (
            select(self.model)
            .where(self.model.is_active == True)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_active_articles(self) -> int:
        """Count active articles"""
        stmt = select(func.count(self.model.id)).where(self.model.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_by_file_name(self, file_name: str) -> Optional[Article]:
        """Get article by file name"""
        stmt = select(self.model).where(self.model.file_name == file_name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_file_path(self, file_path: str) -> Optional[Article]:
        """Get article by file path"""
        stmt = select(self.model).where(self.model.file_path == file_path)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete(self, id: str) -> bool:
        """Soft delete article"""
        entity = await self.update(id, is_active=False)
        return entity is not None
