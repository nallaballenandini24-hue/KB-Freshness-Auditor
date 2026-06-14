"""AI Recommendation API routes"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query

from app.services.recommendation_service import AIRecommendationService
from app.schemas.schemas import AIRecommendationResponse, AIRecommendationUpdate
from app.api.dependencies import get_recommendation_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{rec_id}", response_model=AIRecommendationResponse)
async def get_recommendation(
    rec_id: str, service: AIRecommendationService = Depends(get_recommendation_service)
):
    """Get recommendation"""
    rec = await service.get_recommendation(rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec


@router.get("", response_model=list[AIRecommendationResponse])
async def list_recommendations(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: AIRecommendationService = Depends(get_recommendation_service),
):
    """List recommendations"""
    return await service.list_recommendations(limit=limit, offset=offset)


@router.get("/article/{article_id}", response_model=list[AIRecommendationResponse])
async def get_recommendations_by_article(
    article_id: str, service: AIRecommendationService = Depends(get_recommendation_service)
):
    """Get recommendations for article"""
    return await service.get_by_article(article_id)


@router.get("/pending")
async def get_pending_recommendations(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: AIRecommendationService = Depends(get_recommendation_service),
):
    """Get pending recommendations"""
    return await service.get_pending_recommendations(limit=limit, offset=offset)


@router.put("/{rec_id}", response_model=AIRecommendationResponse)
async def update_recommendation(
    rec_id: str,
    update_data: AIRecommendationUpdate,
    service: AIRecommendationService = Depends(get_recommendation_service),
):
    """Update recommendation"""
    rec = await service.update_recommendation(rec_id, update_data)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec


@router.post("/{rec_id}/accept")
async def accept_recommendation(
    rec_id: str, service: AIRecommendationService = Depends(get_recommendation_service)
):
    """Accept recommendation"""
    rec = await service.accept_recommendation(rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec


@router.post("/{rec_id}/reject")
async def reject_recommendation(
    rec_id: str, service: AIRecommendationService = Depends(get_recommendation_service)
):
    """Reject recommendation"""
    rec = await service.reject_recommendation(rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec


@router.get("/count/pending")
async def count_pending(
    service: AIRecommendationService = Depends(get_recommendation_service),
):
    """Count pending recommendations"""
    count = await service.count_pending()
    return {"count": count}
