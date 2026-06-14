"""Database models"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ArticleStatus(str, enum.Enum):
    """Article freshness status"""

    FRESH = "fresh"
    WARNING = "warning"
    STALE = "stale"


class Article(Base):
    """Knowledge Base Article model"""

    __tablename__ = "articles"

    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=False, unique=True)
    file_name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(500), nullable=True)  # Comma-separated
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_reviewed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    audit_results = relationship("AuditResult", back_populates="article")
    recommendations = relationship("AIRecommendation", back_populates="article")

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title})>"


class Ticket(Base):
    """Support Ticket model"""

    __tablename__ = "tickets"

    id = Column(String(36), primary_key=True)
    ticket_id = Column(String(100), nullable=False, unique=True)
    article_id = Column(String(36), ForeignKey("articles.id"), nullable=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    imported_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Ticket(id={self.id}, ticket_id={self.ticket_id})>"


class AuditResult(Base):
    """Audit Result model"""

    __tablename__ = "audit_results"

    id = Column(String(36), primary_key=True)
    article_id = Column(String(36), ForeignKey("articles.id"), nullable=False)
    freshness_score = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)  # fresh, warning, stale
    article_age_days = Column(Integer, nullable=False)
    ticket_count = Column(Integer, default=0, nullable=False)
    days_since_last_update = Column(Integer, nullable=False)
    audit_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    article = relationship("Article", back_populates="audit_results")

    def __repr__(self):
        return f"<AuditResult(id={self.id}, article_id={self.article_id}, score={self.freshness_score})>"


class AIRecommendation(Base):
    """AI-generated Recommendation model"""

    __tablename__ = "ai_recommendations"

    id = Column(String(36), primary_key=True)
    article_id = Column(String(36), ForeignKey("articles.id"), nullable=False)
    recommendation_type = Column(String(50), nullable=False)  # missing_info, updated_steps, etc.
    original_content = Column(Text, nullable=False)
    recommended_content = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    accepted = Column(Boolean, default=False)
    rejected = Column(Boolean, default=False)
    accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    article = relationship("Article", back_populates="recommendations")

    def __repr__(self):
        return f"<AIRecommendation(id={self.id}, article_id={self.article_id})>"


class AuditJob(Base):
    """Audit Job tracking model"""

    __tablename__ = "audit_jobs"

    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False)  # pending, running, completed, failed
    total_articles = Column(Integer, default=0)
    processed_articles = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AuditJob(id={self.id}, status={self.status})>"
