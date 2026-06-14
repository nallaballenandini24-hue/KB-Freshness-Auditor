"""Pydantic schemas for API validation"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime


class ArticleBase(BaseModel):
    """Base article schema"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[str] = None


class ArticleCreate(ArticleBase):
    """Schema for creating article"""

    file_name: str
    content: str


class ArticleUpdate(BaseModel):
    """Schema for updating article"""

    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None


class ArticleResponse(ArticleBase):
    """Schema for article response"""

    id: str
    file_path: str
    file_name: str
    created_at: datetime
    updated_at: datetime
    last_reviewed_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    """Base ticket schema"""

    ticket_id: str
    subject: str
    category: Optional[str] = None


class TicketCreate(TicketBase):
    """Schema for creating ticket"""

    description: Optional[str] = None
    article_id: Optional[str] = None
    created_at: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class TicketResponse(TicketBase):
    """Schema for ticket response"""

    id: str
    description: Optional[str]
    article_id: Optional[str]
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime]
    imported_at: datetime

    class Config:
        from_attributes = True


class AuditResultResponse(BaseModel):
    """Schema for audit result response"""

    id: str
    article_id: str
    freshness_score: float
    status: str
    article_age_days: int
    ticket_count: int
    days_since_last_update: int
    audit_date: datetime

    class Config:
        from_attributes = True


class AIRecommendationCreate(BaseModel):
    """Schema for creating AI recommendation"""

    recommendation_type: str
    original_content: str
    recommended_content: str
    confidence_score: float


class AIRecommendationResponse(BaseModel):
    """Schema for AI recommendation response"""

    id: str
    article_id: str
    recommendation_type: str
    original_content: str
    recommended_content: str
    confidence_score: float
    accepted: bool
    rejected: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AIRecommendationUpdate(BaseModel):
    """Schema for updating recommendation"""

    accepted: Optional[bool] = None
    rejected: Optional[bool] = None


class DashboardStats(BaseModel):
    """Dashboard statistics"""

    total_articles: int
    fresh_articles: int
    warning_articles: int
    stale_articles: int
    recent_audits_count: int


class AuditJobResponse(BaseModel):
    """Schema for audit job response"""

    id: str
    workflow_id: Optional[str]
    status: str
    total_articles: int
    processed_articles: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Schema for file upload response"""

    file_name: str
    file_path: str
    size: int
    upload_time: datetime


class SearchQuery(BaseModel):
    """Schema for search query"""

    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class BulkDeleteRequest(BaseModel):
    """Schema for bulk delete"""

    ids: List[str] = Field(..., min_items=1, max_items=1000)


class BulkDeleteResponse(BaseModel):
    """Schema for bulk delete response"""

    deleted_count: int
    failed_count: int
    total_count: int
