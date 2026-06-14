# KB Freshness Auditor

A production-grade enterprise knowledge base auditing system designed for Service Desk teams to automatically identify stale KB articles and generate AI-powered update recommendations.

## Team Information

**Team Name:** KB-Freshness-Auditor  

**Team Members:**
- Nallaballe Nandini
- Nayanavari Jyoshna
- Neravati Vyshnavi
- Mukkamalla Mamatha Reddy

A production-grade enterprise knowledge base auditing system...

## Overview

Organizations maintain hundreds or thousands of Knowledge Base articles that become outdated over time, causing repeated support tickets and poor customer experience. The KB Freshness Auditor automatically:

- **Scans** all KB articles for staleness indicators
- **Calculates** freshness scores using multiple factors
- **Generates** AI-powered update recommendations using Groq LLM
- **Tracks** ticket correlations to relevant articles
- **Provides** an intuitive enterprise dashboard for Service Desk teams

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI 0.104+ |
| Database | PostgreSQL 15 |
| Document Storage | MinIO S3-compatible |
| AI/LLM | Groq API (Mixtral 8x7b) |
| Workflow Engine | Temporal (async processing) |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Containerization | Docker & Docker Compose |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |

## Project Structure

```
KB-Freshness-Auditor/
├── backend/
│   ├── app/
│   │   ├── api/                # API endpoints
│   │   │   ├── articles.py
│   │   │   ├── tickets.py
│   │   │   ├── audits.py
│   │   │   ├── recommendations.py
│   │   │   └── dependencies.py
│   │   ├── core/               # Core infrastructure
│   │   │   ├── config.py       # Settings & configuration
│   │   │   ├── database.py     # Database session management
│   │   │   ├── storage.py      # MinIO storage client
│   │   │   └── logging_config.py
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic validation schemas
│   │   ├── repositories/       # Data access layer
│   │   ├── services/           # Business logic layer
│   │   ├── workflows/          # Temporal workflow definitions
│   │   ├── utils/              # Helper functions
│   │   └── main.py             # FastAPI application entry
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── templates/
│   │   └── index.html          # Single-page application
│   └── static/
│       ├── css/
│       │   └── main.css        # Tailored styling
│       └── js/
│           ├── main.js         # Core app logic
│           ├── dashboard.js    # Dashboard page
│           ├── knowledge-base.js
│           └── audit.js        # Audit & recommendations
├── database/
│   └── init.sql                # Schema initialization
├── docker/
│   ├── Dockerfile
│   └── Dockerfile.frontend
├── docker-compose.yml          # Multi-container orchestration
└── README.md                   # This file
```

## Features

### Dashboard
- **Real-time Statistics**: Total, fresh, warning, and stale article counts
- **Freshness Distribution Chart**: Visual breakdown of article health
- **Recent Audits Timeline**: Latest audit results
- **Top 10 Stale Articles**: Priority list for remediation

### Knowledge Base Management
- **File Upload**: Drag-and-drop interface for .md/.txt files
- **Full-text Search**: Search articles by title, description, tags
- **Metadata Editing**: Update article tags, descriptions
- **Soft Delete**: Non-destructive removal of articles

### Ticket Management
- **CSV Import**: Bulk import support ticket data
- **Ticket Correlation**: Automatically link tickets to articles
- **Status Tracking**: Monitor resolved vs. open tickets
- **Category Filtering**: Filter tickets by category

### Freshness Audit
- **Automated Scoring**: Calculate freshness based on formula:
  ```
  Score = (article_age_days × 0.5) + (ticket_count × 0.3) + (days_since_last_update × 0.2)
  ```
- **Status Classification**:
  - 🟢 **Fresh** (Score < 30): Recently updated, low ticket references
  - 🟡 **Warning** (Score 30-60): Moderately aged, growing concerns
  - 🔴 **Stale** (Score > 60): Outdated, high ticket correlation
- **Progress Tracking**: Real-time audit execution monitoring
- **Workflow Integration**: Async processing via Temporal

### AI Recommendation Center
- **Missing Information Analysis**: Identify gaps using Groq LLM
- **Update Suggestions**: AI-generated improvement recommendations
- **Draft Content**: Complete rewritten article versions
- **Acceptance Workflow**: Accept/reject recommendations with tracking

## Installation

### Prerequisites

- Docker & Docker Compose 2.0+
- Python 3.11+ (for local development)
- Groq API Key ([Get free credits](https://console.groq.com))

### Quick Start with Docker

```bash
# 1. Clone repository
git clone <repository-url>
cd KB-Freshness-Auditor

# 2. Configure environment
cp backend/.env.example backend/.env

# 3. Add your Groq API key
# Edit backend/.env and set GROQ_API_KEY=your_key_here

# 4. Start services
docker-compose up -d

# 5. Initialize database
docker-compose exec backend python app/core/database.py

# 6. Access application
# Dashboard: http://localhost:8000
# MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
# API Docs: http://localhost:8000/docs
```

### Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Configure .env file
cp backend/.env.example backend/.env

# 4. Start PostgreSQL & MinIO (with Docker)
docker-compose up postgres minio -d

# 5. Run database migrations
python backend/app/core/database.py

# 6. Start FastAPI server
cd backend
python -m uvicorn app.main:app --reload

# 7. Open http://localhost:8000 in browser
```

## Configuration

### Environment Variables

Create `backend/.env` file:

```env
# Application
APP_NAME=KB Freshness Auditor
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/kb_auditor

# MinIO Storage
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=kb-articles

# Groq LLM
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768

# Freshness Scoring
ARTICLE_AGE_WEIGHT=0.5
TICKET_COUNT_WEIGHT=0.3
DAYS_SINCE_UPDATE_WEIGHT=0.2

# Thresholds
FRESH_THRESHOLD=30.0
WARNING_THRESHOLD=60.0
STALE_THRESHOLD=100.0
```

## Database Schema

### Core Tables

**articles** - Knowledge base articles
- `id`: UUID primary key
- `title`: Article title
- `content`: Full article text
- `file_path`: MinIO storage path
- `tags`: Searchable tags
- `created_at`, `updated_at`: Timestamps
- `is_active`: Soft delete flag

**tickets** - Support tickets
- `id`: UUID primary key
- `ticket_id`: External ticket reference
- `article_id`: FK to articles
- `subject`: Ticket subject
- `resolved`: Status flag
- `created_at`, `resolved_at`: Timestamps

**audit_results** - Audit execution results
- `id`: UUID primary key
- `article_id`: FK to articles
- `freshness_score`: Calculated score
- `status`: fresh | warning | stale
- `article_age_days`: Days since creation
- `ticket_count`: Related tickets
- `audit_date`: When audit ran

**ai_recommendations** - LLM-generated suggestions
- `id`: UUID primary key
- `article_id`: FK to articles
- `recommendation_type`: missing_info | updated_steps | improvements
- `original_content`: Current article text
- `recommended_content`: AI-generated suggestion
- `confidence_score`: LLM confidence (0-1)
- `accepted`: Recommendation status

**audit_jobs** - Workflow tracking
- `id`: UUID primary key
- `workflow_id`: Temporal workflow reference
- `status`: pending | running | completed | failed
- `total_articles`: Articles to process
- `processed_articles`: Completed count
- `error_message`: Failure details

## API Endpoints

### Articles
```
POST   /api/articles/upload         - Upload article file
GET    /api/articles                - List articles
GET    /api/articles/{id}           - Get article details
PUT    /api/articles/{id}           - Update article metadata
DELETE /api/articles/{id}           - Soft delete article
GET    /api/articles/search/query   - Full-text search
```

### Tickets
```
POST   /api/tickets/upload-csv      - Import tickets from CSV
GET    /api/tickets                 - List tickets
GET    /api/tickets/{id}            - Get ticket details
GET    /api/tickets/article/{id}    - Get tickets for article
```

### Audits
```
POST   /api/audits/run              - Start freshness audit
GET    /api/audits/status/{job_id}  - Check audit progress
GET    /api/audits/results/{id}     - Get audit result
GET    /api/audits/dashboard/stats  - Dashboard statistics
GET    /api/audits/stale/top        - Top stale articles
GET    /api/audits/recent           - Recent audits
```

### Recommendations
```
GET    /api/recommendations                - List recommendations
GET    /api/recommendations/{id}           - Get recommendation
GET    /api/recommendations/article/{id}   - Get article recommendations
GET    /api/recommendations/pending        - Get pending recommendations
PUT    /api/recommendations/{id}           - Update recommendation
POST   /api/recommendations/{id}/accept    - Accept recommendation
POST   /api/recommendations/{id}/reject    - Reject recommendation
```

## Architecture Patterns

### Repository Pattern
Data access abstraction through repository layer:
```python
class ArticleRepository(BaseRepository[Article]):
    async def search_by_title_or_tags(self, query: str) -> List[Article]: ...
```

### Service Layer
Business logic encapsulation:
```python
class ArticleService:
    def __init__(self, session: AsyncSession):
        self.repository = ArticleRepository(session)
        
    async def create_article(self, data: ArticleCreate) -> ArticleResponse: ...
```

### Dependency Injection
FastAPI's DI for clean testability:
```python
async def get_article_service(session: AsyncSession = Depends(get_db_session)):
    return ArticleService(session)
```

### Async-First Design
All I/O operations are async:
```python
async def get_article(self, article_id: str) -> Optional[ArticleResponse]:
    article = await self.repository.get_by_id(article_id)
    return ArticleResponse.model_validate(article) if article else None
```

## Deployment

### Production Considerations

1. **Environment Variables**: Use secrets management (HashiCorp Vault, AWS Secrets Manager)
2. **Database Backups**: Configure PostgreSQL automated backups
3. **TLS/HTTPS**: Deploy behind reverse proxy with SSL (nginx, Caddy)
4. **Scaling**: Use Kubernetes or ECS for multi-instance deployments
5. **Monitoring**: Integrate with Prometheus/Grafana for observability
6. **Logging**: Centralized logging with ELK or Datadog

### Docker Compose Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Kubernetes Deployment

Use provided Helm charts or manifests for production-grade deployment with auto-scaling, health checks, and persistent storage.

## Performance Tuning

1. **Database Indexing**: Indexes created on frequent query columns
2. **Connection Pooling**: SQLAlchemy pool size configured for concurrency
3. **Caching**: Redis layer for frequently accessed data (future enhancement)
4. **MinIO Multipart Upload**: Large files streamed efficiently
5. **API Rate Limiting**: Implement with FastAPI middleware (future)

## Security

- **Input Validation**: Pydantic schemas validate all inputs
- **SQL Injection Prevention**: Parameterized queries via ORM
- **CORS Configuration**: Restricted origins in production
- **API Key Management**: Groq API key via environment variables
- **Database Credentials**: Never committed to repository

## Development Standards

### Code Style
- Python 3.11+ with type hints
- Black for formatting
- isort for import organization
- Flake8 for linting

### Testing
- Unit tests for services
- Integration tests for repositories
- Endpoint tests for API routes

### Documentation
- Docstrings on all public functions
- Type hints on all parameters
- README with examples
- API documentation via FastAPI/Swagger

## Troubleshooting

### Common Issues

**Database connection refused**
```bash
docker-compose logs postgres
docker-compose restart postgres
```

**MinIO connection error**
```bash
docker-compose logs minio
# Verify MINIO_ENDPOINT in .env matches docker service
```

**Groq API errors**
- Verify API key: `echo $GROQ_API_KEY`
- Check rate limits on Groq dashboard
- Ensure model name is correct

### Debug Mode

Enable debug mode in `.env`:
```env
DEBUG=True
DB_ECHO=True  # Log all SQL queries
```

## Performance Metrics

- Dashboard loads: < 500ms
- Article search: < 1s (1000 articles)
- Audit run: ~5-10 seconds per 1000 articles (depends on Groq latency)
- File upload: Streaming for large files

## Future Enhancements

- [ ] Redis caching layer
- [ ] Elasticsearch for full-text search
- [ ] Advanced ML-based freshness prediction
- [ ] Slack/Teams integration for notifications
- [ ] Article version history and rollback
- [ ] Bulk recommendation acceptance
- [ ] Export recommendations as PDF reports
- [ ] SAML/OAuth2 authentication
- [ ] Custom freshness formula builder
- [ ] GraphQL API option

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Create Pull Request with description

## License

All rights reserved. This is a proprietary enterprise application.

## Support

For issues and support:
- Email: support@example.com
- Documentation: [https://docs.example.com](https://docs.example.com)
- Issues: GitHub Issues

## Changelog

### v1.0.0 (2024)
- Initial release
- Core audit functionality
- Dashboard & reporting
- Groq LLM integration
- MinIO document storage
- CSV ticket import
## AI Capability Demonstrated

This project demonstrates:
- **Agent Loop**: The system reads KB articles, checks their age and related tickets, sends them to an AI model, gets back a draft, and saves the result.
- **External API Integration**: We use the Groq AI API to generate the article suggestions.

## Assumptions & Limitations

- This project was tested with Python 3.11/3.12. On newer Python versions (like 3.14), some packages (pydantic, sqlalchemy) may need to be upgraded.
- The psycopg2-binary package is not required since we use SQLite.
- AI-generated drafts are suggestions only and should be reviewed by a human before publishing.