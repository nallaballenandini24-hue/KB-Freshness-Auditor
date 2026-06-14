"""API dependencies"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_db_session
from app.services.article_service import ArticleService
from app.services.ticket_service import TicketService
from app.services.audit_service import AuditService
from app.services.recommendation_service import AIRecommendationService


async def get_article_service(session: AsyncSession = Depends(get_db_session)):
    """Get article service"""
    return ArticleService(session)


async def get_ticket_service(session: AsyncSession = Depends(get_db_session)):
    """Get ticket service"""
    return TicketService(session)


async def get_audit_service(session: AsyncSession = Depends(get_db_session)):
    """Get audit service"""
    return AuditService(session)


async def get_recommendation_service(session: AsyncSession = Depends(get_db_session)):
    """Get recommendation service"""
    return AIRecommendationService(session)
