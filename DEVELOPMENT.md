# Development Guide

## Setting Up Development Environment

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or Docker)
- MinIO (or Docker)
- Git

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd KB-Freshness-Auditor
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

### Step 4: Setup Database & Services

Using Docker:
```bash
docker-compose up -d postgres minio
```

Or local PostgreSQL:
```bash
# Create database
createdb kb_auditor

# Run migrations
python app/core/database.py
```

### Step 5: Configure Environment
```bash
cp .env.example .env

# Edit .env with your settings:
# - Set GROQ_API_KEY
# - Update database URLs if needed
```

### Step 6: Run Development Server
```bash
# From backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access at: http://localhost:8000

## Project Development Tips

### Adding New API Endpoint

1. **Create schema** in `app/schemas/schemas.py`:
```python
class MyDataCreate(BaseModel):
    name: str
    description: Optional[str] = None
```

2. **Create model** in `app/models/models.py`:
```python
class MyData(Base):
    __tablename__ = "my_data"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), required=True)
```

3. **Create repository** in `app/repositories/`:
```python
class MyDataRepository(BaseRepository[MyData]):
    async def find_by_name(self, name: str):
        ...
```

4. **Create service** in `app/services/`:
```python
class MyDataService:
    def __init__(self, session: AsyncSession):
        self.repository = MyDataRepository(session)
```

5. **Create API route** in `app/api/my_data.py`:
```python
@router.post("/", response_model=MyDataResponse)
async def create_my_data(data: MyDataCreate, service = Depends(get_my_data_service)):
    return await service.create(data)
```

6. **Register router** in `app/main.py`:
```python
app.include_router(my_data.router)
```

### Database Migrations

Using Alembic (recommended for production):

```bash
# Generate migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head
```

Manual migration:
```bash
# Edit database/init.sql
# Reconnect to database
```

### Testing

Create tests in `backend/tests/`:

```python
# tests/test_article_service.py
import pytest
from app.services.article_service import ArticleService

@pytest.fixture
async def article_service():
    session = AsyncSessionLocal()
    return ArticleService(session)

@pytest.mark.asyncio
async def test_create_article(article_service):
    result = await article_service.create_article(...)
    assert result.id is not None
```

Run tests:
```bash
pytest -v
pytest --cov=app tests/
```

### Debugging

Enable debug mode in `.env`:
```env
DEBUG=True
DB_ECHO=True
```

Then use Python debugger:
```python
import pdb; pdb.set_trace()
```

Or use IDE debugger with VS Code's Python extension configured.

### Code Style

Format code:
```bash
black backend/
isort backend/
```

Lint:
```bash
flake8 backend/
mypy backend/
```

## Common Development Tasks

### Add New Frontend Page

1. Create new HTML template in `frontend/templates/`
2. Add JavaScript file in `frontend/static/js/`
3. Add CSS in `frontend/static/css/`
4. Add navigation link in `index.html`
5. Implement page load function in JavaScript

### Update Database Schema

1. Edit `app/models/models.py`
2. Update `database/init.sql` for production reference
3. Create migration if using Alembic
4. Test with `docker-compose down -v && docker-compose up`

### Add New Service Integration

1. Create client class in `app/core/`
2. Implement service wrapper in `app/services/`
3. Add configuration to `app/core/config.py`
4. Use dependency injection in API routes

## Performance Profiling

```bash
# Profile API endpoint
python -m cProfile -s cumulative -m uvicorn app.main:app > profile.txt

# Analyze database queries
# Set DB_ECHO=True in .env to see all SQL queries

# Memory profiling
pip install memory-profiler
python -m memory_profiler app.main
```

## Docker Development

Build custom image:
```bash
docker build -t kb-auditor:dev -f docker/Dockerfile .
```

Run with volume mounts:
```bash
docker run -v $(pwd)/backend:/app -p 8000:8000 kb-auditor:dev
```

## Troubleshooting Development Issues

### Import errors
```bash
# Ensure you're in virtual environment
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database connection issues
```bash
# Check Docker services
docker ps
docker logs kb-auditor-postgres

# Test connection
psql -U user -d kb_auditor -h localhost
```

### MinIO connection issues
```bash
# Check MinIO
curl http://localhost:9000/minio/health/live

# Check credentials
docker logs kb-auditor-minio
```

### Frontend not updating
```bash
# Clear browser cache
# Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

# Check JavaScript console for errors
# Press F12 in browser
```

## Performance Optimization Tips

1. **Database**: Add indexes for frequently queried columns
2. **API**: Use response caching for read-heavy operations
3. **Frontend**: Lazy load images and components
4. **MinIO**: Use multipart uploads for large files
5. **LLM**: Cache Groq API responses when applicable

## Release Checklist

- [ ] Update version in `app/core/config.py`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release tag
- [ ] Build Docker images
- [ ] Update deployment docs

## Support & Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- Pydantic Docs: https://docs.pydantic.dev
- PostgreSQL Docs: https://www.postgresql.org/docs
- MinIO Docs: https://docs.min.io
- Groq Docs: https://console.groq.com/docs
