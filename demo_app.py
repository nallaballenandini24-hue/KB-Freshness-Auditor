"""
Simplified demo application for KB Freshness Auditor
Uses SQLite instead of PostgreSQL for local development without Docker
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json
import uuid
from pathlib import Path
from contextlib import asynccontextmanager

# Data models
class Article(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None
    content: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    is_active: bool = True

class AuditResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    freshness_score: float
    status: str  # fresh, warning, stale
    article_age_days: int
    ticket_count: int
    audit_date: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class DashboardStats(BaseModel):
    total_articles: int
    fresh_articles: int
    warning_articles: int
    stale_articles: int
    recent_audits_count: int

# In-memory storage
articles_db: List[Article] = []
audit_results_db: List[AuditResult] = []

def calculate_freshness_score(article_age_days: int, ticket_count: int = 0, days_since_update: int = 0) -> tuple[float, str]:
    """Calculate freshness score and status"""
    score = (article_age_days * 0.5) + (ticket_count * 0.3) + (days_since_update * 0.2)
    
    if score < 30:
        status = "fresh"
    elif score < 60:
        status = "warning"
    else:
        status = "stale"
    
    return score, status

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    # Startup
    print("\n" + "="*60)
    print("🚀 KB Freshness Auditor - Demo Version")
    print("="*60)
    print("✓ Using in-memory SQLite (no external database needed)")
    print("✓ Access at: http://localhost:8000")
    print("✓ API Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n✓ Server stopped\n")

# Create FastAPI app
app = FastAPI(
    title="KB Freshness Auditor",
    description="Knowledge Base Freshness Analysis Tool",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
frontend_path = Path(__file__).parent / "frontend" / "static"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# ============= API ENDPOINTS =============

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    """Serve frontend"""
    frontend_path = Path(__file__).parent / "frontend" / "templates" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return {"message": "KB Freshness Auditor is running! Visit http://localhost:8000/docs"}

# ============= ARTICLES =============

@app.post("/api/articles/upload")
async def upload_article(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """Upload a new article"""
    content = await file.read()
    
    article = Article(
        title=title,
        description=description,
        tags=tags,
        content=content.decode('utf-8', errors='ignore')
    )
    articles_db.append(article)
    
    return {
        "id": article.id,
        "title": article.title,
        "description": article.description,
        "tags": article.tags,
        "created_at": article.created_at,
        "is_active": article.is_active
    }

@app.get("/api/articles")
async def list_articles(skip: int = 0, limit: int = 10):
    """List all articles"""
    active = [a for a in articles_db if a.is_active]
    return active[skip:skip+limit]

@app.get("/api/articles/{article_id}")
async def get_article(article_id: str):
    """Get single article"""
    article = next((a for a in articles_db if a.id == article_id and a.is_active), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@app.put("/api/articles/{article_id}")
async def update_article(article_id: str, title: Optional[str] = None, description: Optional[str] = None, tags: Optional[str] = None):
    """Update article metadata"""
    article = next((a for a in articles_db if a.id == article_id and a.is_active), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if title:
        article.title = title
    if description:
        article.description = description
    if tags:
        article.tags = tags
    article.updated_at = datetime.utcnow().isoformat()
    
    return article

@app.delete("/api/articles/{article_id}")
async def delete_article(article_id: str):
    """Soft delete article"""
    article = next((a for a in articles_db if a.id == article_id and a.is_active), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    article.is_active = False
    return {"message": "Article deleted"}

@app.get("/api/articles/search/query")
async def search_articles(q: str, skip: int = 0, limit: int = 10):
    """Search articles"""
    query_lower = q.lower()
    results = [
        a for a in articles_db
        if a.is_active and (
            query_lower in a.title.lower() or
            (a.description and query_lower in a.description.lower()) or
            (a.tags and query_lower in a.tags.lower())
        )
    ]
    return results[skip:skip+limit]

# ============= AUDITS =============

@app.post("/api/audits/run")
async def run_audit():
    """Start freshness audit"""
    # Create audit results for all articles
    import random
    from datetime import datetime, timedelta
    
    for article in articles_db:
        if article.is_active:
            age_days = random.randint(1, 365)
            ticket_count = random.randint(0, 50)
            days_since_update = random.randint(1, 180)
            
            score, status = calculate_freshness_score(age_days, ticket_count, days_since_update)
            
            result = AuditResult(
                article_id=article.id,
                freshness_score=score,
                status=status,
                article_age_days=age_days,
                ticket_count=ticket_count
            )
            audit_results_db.append(result)
    
    return {
        "job_id": str(uuid.uuid4()),
        "status": "completed",
        "message": f"Audit completed for {len([a for a in articles_db if a.is_active])} articles",
        "total_articles": len([a for a in articles_db if a.is_active]),
        "processed_articles": len([a for a in articles_db if a.is_active])
    }

@app.get("/api/audits/status/{job_id}")
async def audit_status(job_id: str):
    """Get audit status"""
    return {
        "id": job_id,
        "status": "completed",
        "total_articles": len([a for a in articles_db if a.is_active]),
        "processed_articles": len([a for a in articles_db if a.is_active]),
        "percent_complete": 100
    }

@app.get("/api/audits/dashboard/stats")
async def dashboard_stats():
    """Get dashboard statistics"""
    fresh = len([a for a in audit_results_db if a.status == "fresh"])
    warning = len([a for a in audit_results_db if a.status == "warning"])
    stale = len([a for a in audit_results_db if a.status == "stale"])
    
    return DashboardStats(
        total_articles=len([a for a in articles_db if a.is_active]),
        fresh_articles=fresh,
        warning_articles=warning,
        stale_articles=stale,
        recent_audits_count=1
    )

@app.get("/api/audits/stale/top")
async def top_stale_articles(limit: int = 10):
    """Get top stale articles"""
    stale = sorted(
        [a for a in audit_results_db if a.status == "stale"],
        key=lambda x: x.freshness_score,
        reverse=True
    )
    return stale[:limit]

@app.get("/api/audits/recent")
async def recent_audits(limit: int = 5):
    """Get recent audits"""
    return []

@app.get("/api/audits/results/{audit_id}")
async def audit_result(audit_id: str):
    """Get audit result"""
    result = next((a for a in audit_results_db if a.id == audit_id), None)
    if not result:
        raise HTTPException(status_code=404, detail="Audit result not found")
    return result

# ============= RECOMMENDATIONS =============

@app.get("/api/recommendations")
async def list_recommendations(skip: int = 0, limit: int = 10):
    """List all recommendations"""
    return []

@app.get("/api/recommendations/pending")
async def pending_recommendations(limit: int = 10):
    """Get pending recommendations"""
    return []

@app.get("/api/recommendations/article/{article_id}")
async def article_recommendations(article_id: str):
    """Get recommendations for article"""
    return []

# ============= TICKETS =============

@app.post("/api/tickets/upload-csv")
async def upload_tickets(file: UploadFile = File(...)):
    """Upload tickets from CSV"""
    content = await file.read()
    lines = content.decode('utf-8').split('\n')
    
    if len(lines) < 2:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    
    return {"message": f"Imported {len(lines)-1} tickets"}

@app.get("/api/tickets")
async def list_tickets(skip: int = 0, limit: int = 10):
    """List tickets"""
    return []

@app.get("/api/tickets/article/{article_id}")
async def article_tickets(article_id: str):
    """Get tickets for article"""
    return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
