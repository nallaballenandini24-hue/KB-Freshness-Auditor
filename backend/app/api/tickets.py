"""Ticket API routes"""
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ticket_service import TicketService
from app.schemas.schemas import TicketResponse
from app.api.dependencies import get_ticket_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/upload-csv")
async def upload_ticket_csv(
    file: UploadFile = File(...), service: TicketService = Depends(get_ticket_service)
):
    """Upload tickets from CSV"""
    try:
        content = await file.read()
        imported_count, skipped_count = await service.import_tickets_from_csv(content)
        return {
            "imported": imported_count,
            "skipped": skipped_count,
            "total": imported_count + skipped_count,
        }
    except Exception as e:
        logger.error(f"Error uploading tickets: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str, service: TicketService = Depends(get_ticket_service)
):
    """Get ticket by ID"""
    ticket = await service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: TicketService = Depends(get_ticket_service),
):
    """List tickets"""
    return await service.list_tickets(limit=limit, offset=offset)


@router.get("/article/{article_id}", response_model=list[TicketResponse])
async def get_tickets_by_article(
    article_id: str, service: TicketService = Depends(get_ticket_service)
):
    """Get tickets for an article"""
    return await service.get_tickets_by_article(article_id)


@router.get("/search/query", response_model=list[TicketResponse])
async def search_tickets(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    service: TicketService = Depends(get_ticket_service),
):
    """Search tickets"""
    return await service.search_tickets(q, limit=limit)


@router.get("/count/total")
async def count_tickets(service: TicketService = Depends(get_ticket_service)):
    """Count total tickets"""
    count = await service.count_total_tickets()
    return {"count": count}
