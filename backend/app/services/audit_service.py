"""Audit service"""
import uuid
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AuditResult, AuditJob
from app.schemas.schemas import AuditResultResponse, AuditJobResponse
from app.repositories.audit_repository import AuditResultRepository
from app.repositories.job_repository import AuditJobRepository
from app.repositories.article_repository import ArticleRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.freshness_service import FreshnessScoreCalculator

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit operations"""

    def __init__(self, session: AsyncSession):
        self.audit_repo = AuditResultRepository(session)
        self.job_repo = AuditJobRepository(session)
        self.article_repo = ArticleRepository(session)
        self.ticket_repo = TicketRepository(session)
        self.session = session

    async def create_audit_result(
        self,
        article_id: str,
        freshness_score: float,
        status: str,
        article_age_days: int,
        ticket_count: int,
        days_since_last_update: int,
    ) -> AuditResultResponse:
        """Create audit result"""
        audit_result = AuditResult(
            id=str(uuid.uuid4()),
            article_id=article_id,
            freshness_score=freshness_score,
            status=status,
            article_age_days=article_age_days,
            ticket_count=ticket_count,
            days_since_last_update=days_since_last_update,
        )

        try:
            created_result = await self.audit_repo.create(audit_result)
            await self.audit_repo.commit()
            return AuditResultResponse.model_validate(created_result)

        except Exception as e:
            await self.audit_repo.rollback()
            logger.error(f"Error creating audit result: {e}")
            raise

    async def get_audit_result(self, result_id: str) -> Optional[AuditResultResponse]:
        """Get audit result"""
        result = await self.audit_repo.get_by_id(result_id)
        return AuditResultResponse.model_validate(result) if result else None

    async def get_audit_results_by_article(self, article_id: str) -> List[AuditResultResponse]:
        """Get audit results for article"""
        results = await self.audit_repo.get_by_article_id(article_id)
        return [AuditResultResponse.model_validate(r) for r in results]

    async def get_audit_results_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> List[AuditResultResponse]:
        """Get audit results by status"""
        results = await self.audit_repo.get_by_status(status, limit=limit, offset=offset)
        return [AuditResultResponse.model_validate(r) for r in results]

    async def get_top_stale_articles(self, limit: int = 10) -> List[AuditResultResponse]:
        """Get top stale articles"""
        results = await self.audit_repo.get_top_stale_articles(limit=limit)
        return [AuditResultResponse.model_validate(r) for r in results]

    async def get_recent_audits(self, limit: int = 10) -> List[AuditResultResponse]:
        """Get recent audits"""
        results = await self.audit_repo.get_recent_audits(limit=limit)
        return [AuditResultResponse.model_validate(r) for r in results]

    async def count_by_status(self, status: str) -> int:
        """Count results by status"""
        return await self.audit_repo.count_by_status(status)

    async def get_dashboard_stats(self):
        """Get dashboard statistics"""
        fresh_count = await self.audit_repo.count_by_status("fresh")
        warning_count = await self.audit_repo.count_by_status("warning")
        stale_count = await self.audit_repo.count_by_status("stale")
        total_articles = await self.article_repo.count_active_articles()
        recent_audits = await self.audit_repo.get_recent_audits(limit=5)

        return {
            "total_articles": total_articles,
            "fresh_articles": fresh_count,
            "warning_articles": warning_count,
            "stale_articles": stale_count,
            "recent_audits_count": len(recent_audits),
        }

    async def create_audit_job(self, total_articles: int = 0) -> AuditJobResponse:
        """Create audit job"""
        job = AuditJob(
            id=str(uuid.uuid4()),
            status="pending",
            total_articles=total_articles,
        )

        try:
            created_job = await self.job_repo.create(job)
            await self.job_repo.commit()
            return AuditJobResponse.model_validate(created_job)

        except Exception as e:
            await self.job_repo.rollback()
            logger.error(f"Error creating audit job: {e}")
            raise

    async def get_audit_job(self, job_id: str) -> Optional[AuditJobResponse]:
        """Get audit job"""
        job = await self.job_repo.get_by_id(job_id)
        return AuditJobResponse.model_validate(job) if job else None

    async def update_audit_job(self, job_id: str, **kwargs) -> Optional[AuditJobResponse]:
        """Update audit job"""
        try:
            updated_job = await self.job_repo.update(job_id, **kwargs)
            await self.job_repo.commit()
            return AuditJobResponse.model_validate(updated_job) if updated_job else None

        except Exception as e:
            await self.job_repo.rollback()
            logger.error(f"Error updating audit job: {e}")
            raise

    async def get_latest_audit_job(self) -> Optional[AuditJobResponse]:
        """Get latest audit job"""
        job = await self.job_repo.get_latest_job()
        return AuditJobResponse.model_validate(job) if job else None
