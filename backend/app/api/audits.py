"""Audit API routes"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
import asyncio

from app.services.audit_service import AuditService
from app.schemas.schemas import AuditResultResponse, AuditJobResponse
from app.api.dependencies import get_audit_service
from app.workflows.audit_workflow import AuditWorkflow
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/audits", tags=["audits"])


@router.post("/run")
async def run_audit(service: AuditService = Depends(get_audit_service)):
    """Run freshness audit"""
    try:
        # Create audit job
        job = await service.create_audit_job()

        # Start audit workflow in background
        async def execute_in_background():
            async with AsyncSessionLocal() as session:
                await AuditWorkflow.execute_audit(job.id, session)

        asyncio.create_task(execute_in_background())

        return job

    except Exception as e:
        logger.error(f"Error starting audit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=AuditJobResponse)
async def get_audit_status(
    job_id: str, service: AuditService = Depends(get_audit_service)
):
    """Get audit job status"""
    job = await service.get_audit_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Audit job not found")
    return job


@router.get("/results/{result_id}", response_model=AuditResultResponse)
async def get_audit_result(
    result_id: str, service: AuditService = Depends(get_audit_service)
):
    """Get audit result"""
    result = await service.get_audit_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Audit result not found")
    return result


@router.get("/article/{article_id}")
async def get_article_audits(
    article_id: str, service: AuditService = Depends(get_audit_service)
):
    """Get audits for article"""
    return await service.get_audit_results_by_article(article_id)


@router.get("/status/{status}")
async def get_audits_by_status(
    status: str = Query(..., regex="^(fresh|warning|stale)$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: AuditService = Depends(get_audit_service),
):
    """Get audits by status"""
    return await service.get_audit_results_by_status(status, limit=limit, offset=offset)


@router.get("/stale/top")
async def get_top_stale_articles(
    limit: int = Query(10, ge=1, le=100),
    service: AuditService = Depends(get_audit_service),
):
    """Get top stale articles"""
    return await service.get_top_stale_articles(limit=limit)


@router.get("/recent")
async def get_recent_audits(
    limit: int = Query(10, ge=1, le=100),
    service: AuditService = Depends(get_audit_service),
):
    """Get recent audits"""
    return await service.get_recent_audits(limit=limit)


@router.get("/dashboard/stats")
async def get_dashboard_stats(service: AuditService = Depends(get_audit_service)):
    """Get dashboard statistics"""
    return await service.get_dashboard_stats()
