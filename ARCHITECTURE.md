"""Architecture and Design Documentation"""

# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Single-Page Application (SPA)                         │ │
│  │ • HTML5 Templates  • CSS3 Styling  • JavaScript       │ │
│  │ • Bootstrap 5 UI   • Chart.js      • Responsive       │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────┬──────────────────────────────────────────────┘
               │ REST API Calls
               │ JSON / Form Data
               ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Route Handlers          │ Dependency Injection         ││
│  │ • /api/articles         │ • get_article_service()      ││
│  │ • /api/tickets          │ • get_audit_service()        ││
│  │ • /api/audits           │ • get_db_session()           ││
│  │ • /api/recommendations  │                              ││
│  └─────────────────────────────────────────────────────────┘│
└──────────────┬──────────────────────────────────────────────┘
               │ Query Objects
               │ ORM Calls
               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Business Logic                                         │ │
│  │ • ArticleService       • TicketService                 │ │
│  │ • AuditService         • RecommendationService         │ │
│  │ • FreshnessScoreCalculator  • GroqAIService            │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────┬──────────────────────────────────────────────┘
               │ Repository Calls
               │ LLM Requests
               │ Storage Operations
               ▼
┌──────────────────────┬───────────────────┬─────────────┐
│                      │                   │             │
▼                      ▼                   ▼             ▼
┌──────────────┐  ┌────────────┐    ┌──────────┐  ┌─────────┐
│ PostgreSQL   │  │   MinIO    │    │ Groq API │  │Temporal │
│ Database     │  │ Storage    │    │   LLM    │  │Workflows│
│              │  │            │    │          │  │         │
│ • Articles   │  │ • Files    │    │Generates │  │ • Tasks │
│ • Tickets    │  │ • Backups  │    │Recommen- │  │ • Jobs  │
│ • Results    │  │            │    │dations   │  │         │
│ • Recomm.   │  │            │    │          │  │         │
└──────────────┘  └────────────┘    └──────────┘  └─────────┘
```

## Data Flow

### Article Upload Flow
1. User uploads .md/.txt file via Frontend
2. Frontend sends to `/api/articles/upload` POST endpoint
3. ArticleService receives request
4. File uploaded to MinIO storage
5. Metadata saved to PostgreSQL
6. Response returned with article ID

### Audit Execution Flow
1. User clicks "Start Audit" button
2. Frontend calls `/api/audits/run` POST
3. AuditService creates job record
4. Workflow triggered asynchronously
5. For each article:
   - Calculate freshness score
   - Determine status (Fresh/Warning/Stale)
   - Store results in database
   - If stale, call Groq API for recommendations
6. Job status updated to "completed"
7. Frontend polls job status endpoint
8. Results displayed when complete

### Recommendation Acceptance Flow
1. User reviews AI recommendation
2. Clicks "Accept" button
3. Frontend POST to `/api/recommendations/{id}/accept`
4. RecommendationService marks as accepted
5. Article update timestamp reset (optional)
6. Dashboard updated with accepted count

## Design Patterns

### Repository Pattern
- **Purpose**: Abstract data access
- **Benefits**: Testability, easy to swap implementations
- **Example**:
```python
class ArticleRepository(BaseRepository[Article]):
    async def search_by_title(self, query: str):
        # SQL encapsulated here
        pass

# Usage in service
article = await self.repository.search_by_title("password")
```

### Service Layer Pattern
- **Purpose**: Centralize business logic
- **Benefits**: Reusability, consistency, easier testing
- **Example**:
```python
class ArticleService:
    async def create_article(self, data: ArticleCreate):
        # Orchestrates repository, storage, validation
        # Returns business model, not database model
        pass
```

### Dependency Injection
- **Purpose**: Loose coupling, testability
- **Implementation**: FastAPI's Depends()
- **Example**:
```python
@app.get("/")
async def get_item(service: ArticleService = Depends(get_article_service)):
    return await service.get_all()
```

### Async-First Architecture
- **Purpose**: Handle concurrency efficiently
- **Benefits**: Better resource utilization, handles I/O delays
- **All external calls are async**:
  - Database queries
  - MinIO operations
  - API calls to Groq

## Database Schema Design

### Normalized vs. Denormalized Trade-offs

**articles** table
- Normalized: Only contains metadata
- Stores full content for full-text search
- Foreign key targets from tickets, audit_results

**tickets** table
- FK to articles (nullable for correlation discovery)
- Separate table to handle many-to-one relationship
- Indexed on article_id for fast lookups

**audit_results** table
- Stores computed scores (denormalized for performance)
- Indexed on status for dashboard queries
- Indexed on article_id for audit history

**ai_recommendations** table
- Stores LLM outputs (immutable by design)
- Versioning via multiple records per article

### Key Indexes
```sql
CREATE INDEX idx_articles_active ON articles(is_active);
CREATE INDEX idx_audit_results_status ON audit_results(status);
CREATE INDEX idx_recommendations_accepted ON ai_recommendations(accepted, rejected);
```

## Freshness Score Algorithm

**Formula:**
```
Score = (article_age_days × 0.5) + (ticket_count × 0.3) + (days_since_last_update × 0.2)
```

**Classification Logic:**
```
if score < 30:
    status = "fresh"
elif score < 60:
    status = "warning"
else:
    status = "stale"
```

**Rationale:**
- **Article Age (50%)**: Primary factor - older articles more likely stale
- **Ticket Count (30%)**: Indirect stale indicator - support tickets reference old info
- **Days Since Update (20%)**: Direct maintenance indicator - updates = care

## API Design

### RESTful Principles
- Resource-based URLs: `/articles`, `/tickets`, `/audits`
- Standard HTTP verbs:
  - POST: Create
  - GET: Read
  - PUT: Update
  - DELETE: Delete
- Status codes:
  - 200: Success
  - 201: Created
  - 400: Bad request
  - 404: Not found
  - 500: Server error

### Request/Response Format
```json
// POST /api/articles/upload
{
  "title": "How to Reset Password",
  "description": "Step-by-step guide",
  "tags": "password,authentication",
  "file": <binary>
}

// Response 201
{
  "id": "uuid",
  "title": "How to Reset Password",
  "file_path": "articles/uuid/guide.md",
  "created_at": "2024-01-15T10:00:00Z",
  "is_active": true
}
```

## Frontend Architecture

### Single-Page Application (SPA)
- **Framework**: Vanilla JavaScript (no heavy dependencies)
- **Routing**: Client-side navigation with URL fragments
- **State**: Minimal - fetches fresh data on each page load
- **Templating**: HTML fragments injected into DOM

### Component Structure
```
main.js (core logic)
  ├── navigation setup
  ├── API utilities
  └── common helpers
dashboard.js (dashboard page)
  ├── loadDashboard()
  ├── renderCharts()
  └── fetchStats()
knowledge-base.js (KB management)
  ├── loadKnowledgeBase()
  ├── searchArticles()
  └── uploadArticle()
audit.js (audit functionality)
  ├── loadAudit()
  ├── runAudit()
  └── pollAuditStatus()
```

## Security Architecture

### Authentication (Future Enhancement)
- OAuth2 with Google/Microsoft AD
- JWT tokens with 1-hour expiry
- Refresh token rotation

### Authorization
- Role-based access (Admin, Manager, Viewer)
- Resource-level permissions
- API rate limiting per user

### Data Protection
- TLS/HTTPS in transit
- Encryption at rest for sensitive data
- PostgreSQL encryption for backups

### Input Validation
- Pydantic schema validation
- Sanitization of file uploads
- SQL injection prevention via ORM

## Performance Considerations

### Caching Strategy
- Static assets: Browser cache, CDN (1 year)
- Dashboard stats: 5-minute TTL
- Article list: Per-request (no cache due to frequent updates)

### Database Optimization
- Connection pooling: 20 connections
- Query optimization: Strategic indexing
- Pagination: 10-100 items per page

### API Optimization
- Async all I/O operations
- Streaming file uploads/downloads
- Gzip response compression

## Monitoring & Observability

### Metrics
- Request latency (p50, p95, p99)
- Error rate by endpoint
- Database connection pool usage
- Groq API latency and rate limits

### Logging
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized aggregation (ELK/Datadog)

### Tracing
- Request ID correlation
- Distributed tracing for workflow execution
- Performance bottleneck identification

## Scaling Strategy

### Horizontal Scaling
- Multiple FastAPI instances behind load balancer
- Read replicas for PostgreSQL
- MinIO clustering for storage

### Vertical Scaling
- Increase server resources
- Database connection pool optimization
- Memory allocation for caching

### Async Processing
- Temporal workflows for long-running audits
- Job queue for recommendations
- Background task execution

## Disaster Recovery

### Backup Strategy
- Daily PostgreSQL backups (AWS RDS)
- MinIO cross-region replication
- Point-in-time recovery capability

### Failover
- Database replication with automatic failover
- Multi-AZ deployment
- Load balancer health checks

### Recovery Procedures
- RTO: 4 hours
- RPO: 1 hour
- Monthly disaster recovery drills

## Technology Justifications

| Technology | Why Chosen |
|-----------|-----------|
| FastAPI | Modern, async, auto-documentation, fast |
| PostgreSQL | ACID compliance, reliability, maturity |
| MinIO | S3-compatible, self-hosted, scalable |
| Groq | Fast inference, cost-effective, accessible API |
| Pydantic | Type validation, excellent DX, performance |
| SQLAlchemy | ORM best practices, async support |
| Bootstrap 5 | Responsive, accessible, minimal customization |
| Docker | Reproducible environments, easy deployment |

## Future Architecture Improvements

1. **Elasticsearch**: Full-text search for 100K+ articles
2. **Redis**: Caching layer for performance
3. **Kafka**: Event streaming for real-time updates
4. **GraphQL**: Flexible querying for complex scenarios
5. **Kubernetes**: Container orchestration for scaling
6. **gRPC**: High-performance internal service communication
7. **Circuit Breaker**: Groq API reliability patterns
8. **Distributed Tracing**: Jaeger/Zipkin for debugging
