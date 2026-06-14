"""AI recommendation service"""
import uuid
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AIRecommendation
from app.schemas.schemas import AIRecommendationCreate, AIRecommendationResponse, AIRecommendationUpdate
from app.repositories.recommendation_repository import AIRecommendationRepository

logger = logging.getLogger(__name__)


class AIRecommendationService:
    """Service for managing AI recommendations"""

    def __init__(self, session: AsyncSession):
        self.repository = AIRecommendationRepository(session)
        self.session = session

    async def create_recommendation(
        self, article_id: str, rec_data: AIRecommendationCreate
    ) -> AIRecommendationResponse:
        """Create new recommendation"""
        recommendation = AIRecommendation(
            id=str(uuid.uuid4()),
            article_id=article_id,
            recommendation_type=rec_data.recommendation_type,
            original_content=rec_data.original_content,
            recommended_content=rec_data.recommended_content,
            confidence_score=rec_data.confidence_score,
        )

        try:
            created_rec = await self.repository.create(recommendation)
            await self.repository.commit()
            logger.info(f"Recommendation created: {recommendation.id}")
            return AIRecommendationResponse.model_validate(created_rec)

        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Error creating recommendation: {e}")
            raise

    async def get_recommendation(self, rec_id: str) -> Optional[AIRecommendationResponse]:
        """Get recommendation by ID"""
        recommendation = await self.repository.get_by_id(rec_id)
        return AIRecommendationResponse.model_validate(recommendation) if recommendation else None

    async def list_recommendations(
        self, limit: int = 100, offset: int = 0
    ) -> List[AIRecommendationResponse]:
        """List recommendations"""
        recommendations = await self.repository.get_all(limit=limit, offset=offset)
        return [AIRecommendationResponse.model_validate(r) for r in recommendations]

    async def get_by_article(self, article_id: str) -> List[AIRecommendationResponse]:
        """Get recommendations by article"""
        recommendations = await self.repository.get_by_article_id(article_id)
        return [AIRecommendationResponse.model_validate(r) for r in recommendations]

    async def get_pending_recommendations(
        self, limit: int = 10, offset: int = 0
    ) -> List[AIRecommendationResponse]:
        """Get pending recommendations"""
        recommendations = await self.repository.get_pending_recommendations(
            limit=limit, offset=offset
        )
        return [AIRecommendationResponse.model_validate(r) for r in recommendations]

    async def update_recommendation(
        self, rec_id: str, update_data: AIRecommendationUpdate
    ) -> Optional[AIRecommendationResponse]:
        """Update recommendation"""
        try:
            update_dict = update_data.model_dump(exclude_unset=True)
            updated_rec = await self.repository.update(rec_id, **update_dict)
            await self.repository.commit()

            if updated_rec:
                logger.info(f"Recommendation updated: {rec_id}")
                return AIRecommendationResponse.model_validate(updated_rec)
            return None

        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Error updating recommendation: {e}")
            raise

    async def accept_recommendation(self, rec_id: str) -> Optional[AIRecommendationResponse]:
        """Accept recommendation"""
        try:
            from datetime import datetime
            updated_rec = await self.repository.update(
                rec_id, accepted=True, rejected=False, accepted_at=datetime.utcnow()
            )
            await self.repository.commit()

            if updated_rec:
                logger.info(f"Recommendation accepted: {rec_id}")
                return AIRecommendationResponse.model_validate(updated_rec)
            return None

        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Error accepting recommendation: {e}")
            raise

    async def reject_recommendation(self, rec_id: str) -> Optional[AIRecommendationResponse]:
        """Reject recommendation"""
        try:
            updated_rec = await self.repository.update(rec_id, rejected=True, accepted=False)
            await self.repository.commit()

            if updated_rec:
                logger.info(f"Recommendation rejected: {rec_id}")
                return AIRecommendationResponse.model_validate(updated_rec)
            return None

        except Exception as e:
            await self.repository.rollback()
            logger.error(f"Error rejecting recommendation: {e}")
            raise

    async def count_pending(self) -> int:
        """Count pending recommendations"""
        return await self.repository.count_pending_recommendations()

    async def count_accepted(self) -> int:
        """Count accepted recommendations"""
        return await self.repository.count_accepted()
