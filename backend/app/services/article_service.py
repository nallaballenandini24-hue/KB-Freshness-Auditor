"""Article service"""
import uuid
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Article
from app.schemas.schemas import ArticleCreate, ArticleUpdate, ArticleResponse
from app.repositories.article_repository import ArticleRepository
from app.core.storage import get_storage_client

logger = logging.getLogger(__name__)


class ArticleService:
    """Service for managing articles"""

    def __init__(self, session: AsyncSession):
        self.repository = ArticleRepository(session)
        self.storage = get_storage_client()
        self.session = session

    async def create_article(
        self, article_data: ArticleCreate, file_content: bytes
    ) -> ArticleResponse:
        """Create new article"""
        article_id = str(uuid.uuid4())
        file_path = f"articles/{article_id}/{article_data.file_name}"

        try:
            # Upload to MinIO
            await self.storage.upload_file(
                file_path, file_content, content_type="text/plain"
            )

            # Create database record
            article = Article(
                id=article_id,
                title=article_data.title,
                description=article_data.description,
                file_path=file_path,
                file_name=article_data.file_name,
                content=article_data.content,
                tags=article_data.tags,
            )

            created_article = await self.repository.create(article)
            await self.repository.commit()

            logger.info(f"Article created: {article_id}")
            return ArticleResponse.model_validate(created_article)

        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Error creating article: {e}")
            raise

    async def get_article(self, article_id: str) -> Optional[ArticleResponse]:
        """Get article by ID"""
        article = await self.repository.get_by_id(article_id)
        return ArticleResponse.model_validate(article) if article else None

    async def list_articles(
        self, limit: int = 100, offset: int = 0
    ) -> List[ArticleResponse]:
        """List articles"""
        articles = await self.repository.get_active_articles(limit=limit, offset=offset)
        return [ArticleResponse.model_validate(a) for a in articles]

    async def search_articles(
        self, query: str, limit: int = 10, offset: int = 0
    ) -> List[ArticleResponse]:
        """Search articles"""
        articles = await self.repository.search_by_title_or_tags(
            query, limit=limit, offset=offset
        )
        return [ArticleResponse.model_validate(a) for a in articles]

    async def update_article(
        self, article_id: str, update_data: ArticleUpdate
    ) -> Optional[ArticleResponse]:
        """Update article"""
        try:
            update_dict = update_data.model_dump(exclude_unset=True)
            updated_article = await self.repository.update(article_id, **update_dict)
            await self.repository.commit()

            if updated_article:
                logger.info(f"Article updated: {article_id}")
                return ArticleResponse.model_validate(updated_article)
            return None

        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Error updating article: {e}")
            raise

    async def delete_article(self, article_id: str) -> bool:
        """Soft delete article"""
        try:
            success = await self.repository.soft_delete(article_id)
            await self.repository.commit()

            if success:
                logger.info(f"Article deleted: {article_id}")
            return success

        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Error deleting article: {e}")
            raise

    async def count_articles(self) -> int:
        """Count active articles"""
        return await self.repository.count_active_articles()

    async def mark_reviewed(self, article_id: str) -> Optional[ArticleResponse]:
        """Mark article as reviewed"""
        try:
            updated_article = await self.repository.update(
                article_id, last_reviewed_at=datetime.utcnow()
            )
            await self.repository.commit()
            return ArticleResponse.model_validate(updated_article) if updated_article else None

        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Error marking article as reviewed: {e}")
            raise
