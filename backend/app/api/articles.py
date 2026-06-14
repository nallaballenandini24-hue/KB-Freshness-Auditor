"""Article API routes"""
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.article_service import ArticleService
from app.schemas.schemas import ArticleCreate, ArticleResponse, ArticleUpdate, SearchQuery
from app.api.dependencies import get_article_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/upload", response_model=ArticleResponse)
async def upload_article(
    title: str,
    file: UploadFile = File(...),
    description: str = None,
    tags: str = None,
    service: ArticleService = Depends(get_article_service),
):
    """Upload a KB article"""
    try:
        content = await file.read()
        article_data = ArticleCreate(
            title=title,
            file_name=file.filename,
            content=content.decode("utf-8"),
            description=description,
            tags=tags,
        )
        return await service.create_article(article_data, content)
    except Exception as e:
        logger.error(f"Error uploading article: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: str, service: ArticleService = Depends(get_article_service)
):
    """Get article by ID"""
    article = await service.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("", response_model=list[ArticleResponse])
async def list_articles(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ArticleService = Depends(get_article_service),
):
    """List articles"""
    return await service.list_articles(limit=limit, offset=offset)


@router.get("/search/query", response_model=list[ArticleResponse])
async def search_articles(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ArticleService = Depends(get_article_service),
):
    """Search articles"""
    return await service.search_articles(q, limit=limit, offset=offset)


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: str,
    update_data: ArticleUpdate,
    service: ArticleService = Depends(get_article_service),
):
    """Update article"""
    article = await service.update_article(article_id, update_data)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/{article_id}")
async def delete_article(
    article_id: str, service: ArticleService = Depends(get_article_service)
):
    """Delete article"""
    success = await service.delete_article(article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"detail": "Article deleted"}


@router.get("/count/total")
async def count_articles(service: ArticleService = Depends(get_article_service)):
    """Count total articles"""
    count = await service.count_articles()
    return {"count": count}
