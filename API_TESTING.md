"""Comprehensive API Testing Guide with Examples"""

# API Testing Guide

## Running the Application

```bash
# Start services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Verify backend is running
curl http://localhost:8000/health
```

## Accessing API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Try all endpoints directly in the UI with request/response visualization.

## Authentication

Currently no authentication required (add OAuth2 in production).

```bash
# Add to all requests if implementing authentication:
-H "Authorization: Bearer YOUR_TOKEN"
```

## Article Management Endpoints

### Upload Article

```bash
# Create test file
echo "# Test Article

This is a test article for KB Freshness Auditor.

## Features
- Automatic auditing
- AI recommendations
- Real-time updates
" > test_article.md

# Upload
curl -X POST http://localhost:8000/api/articles/upload \
  -F "file=@test_article.md" \
  -F "title=How to Reset Password" \
  -F "description=Step-by-step password reset guide" \
  -F "tags=password,authentication,account"

# Response:
# {
#   "id": "550e8400-e29b-41d4-a716-446655440000",
#   "title": "How to Reset Password",
#   "file_path": "articles/550e8400-e29b-41d4-a716-446655440000/test_article.md",
#   "created_at": "2024-01-15T10:00:00Z",
#   "is_active": true
# }
```

### List Articles

```bash
curl -X GET "http://localhost:8000/api/articles?skip=0&limit=10"

# Query parameters:
# - skip: Offset (default 0)
# - limit: Items per page (default 10)
```

### Get Single Article

```bash
curl -X GET "http://localhost:8000/api/articles/{article_id}"
```

### Search Articles

```bash
# Full-text search
curl -X GET "http://localhost:8000/api/articles/search/query?q=password&skip=0&limit=10"

# Results include all matching articles by title, description, tags
```

### Update Article

```bash
curl -X PUT "http://localhost:8000/api/articles/{article_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "description": "New description",
    "tags": "new,tags"
  }'
```

### Delete Article

```bash
# Soft delete (marks as_active = false)
curl -X DELETE "http://localhost:8000/api/articles/{article_id}"
```

## Ticket Management Endpoints

### Import Tickets from CSV

```bash
# Create test CSV
cat > tickets.csv << 'EOF'
ticket_id,subject,description,category,article_id,created_at,resolved,resolved_at
TICK-001,Password Reset Error,User cannot complete password reset,account-access,,2024-01-10T15:30:00Z,false,
TICK-002,Login Issues,Cannot log in,authentication,,2024-01-11T09:00:00Z,true,2024-01-12T10:00:00Z
EOF

# Import
curl -X POST http://localhost:8000/api/tickets/upload-csv \
  -F "file=@tickets.csv"
```

### List Tickets

```bash
curl -X GET "http://localhost:8000/api/tickets?skip=0&limit=10"
```

### Get Tickets for Article

```bash
curl -X GET "http://localhost:8000/api/tickets/article/{article_id}"

# Returns all tickets linked to that article
```

### Search Tickets

```bash
curl -X GET "http://localhost:8000/api/tickets/search/query?q=password"
```

## Audit Endpoints

### Start Audit

```bash
curl -X POST http://localhost:8000/api/audits/run

# Response:
# {
#   "job_id": "abc123",
#   "status": "running",
#   "message": "Audit job started"
# }
```

### Check Audit Status

```bash
# Poll every 5 seconds
curl -X GET "http://localhost:8000/api/audits/status/{job_id}"

# Response:
# {
#   "id": "abc123",
#   "status": "running",
#   "total_articles": 250,
#   "processed_articles": 125,
#   "percent_complete": 50
# }
```

### Get Dashboard Statistics

```bash
curl -X GET http://localhost:8000/api/audits/dashboard/stats

# Response:
# {
#   "total_articles": 250,
#   "fresh_articles": 80,
#   "warning_articles": 100,
#   "stale_articles": 70,
#   "recent_audits_count": 5
# }
```

### Get Top Stale Articles

```bash
curl -X GET "http://localhost:8000/api/audits/stale/top?limit=10"

# Returns articles ranked by freshness score (highest first)
```

### Get Recent Audits

```bash
curl -X GET "http://localhost:8000/api/audits/recent?limit=5"

# Returns last N audit jobs
```

### Get Audit Result Details

```bash
curl -X GET "http://localhost:8000/api/audits/results/{audit_id}"

# Shows detailed freshness analysis for that result
```

## Recommendation Endpoints

### Get All Recommendations

```bash
curl -X GET "http://localhost:8000/api/recommendations?skip=0&limit=10"
```

### Get Pending Recommendations

```bash
curl -X GET "http://localhost:8000/api/recommendations/pending?limit=20"

# Returns only recommendations not yet accepted/rejected
```

### Get Recommendations for Article

```bash
curl -X GET "http://localhost:8000/api/recommendations/article/{article_id}"

# All recommendations generated for that article
```

### Get Single Recommendation

```bash
curl -X GET "http://localhost:8000/api/recommendations/{recommendation_id}"

# Shows complete recommendation including original and suggested content
```

### Accept Recommendation

```bash
curl -X POST "http://localhost:8000/api/recommendations/{recommendation_id}/accept"

# Marks recommendation as accepted
# Optionally triggers article update
```

### Reject Recommendation

```bash
curl -X POST "http://localhost:8000/api/recommendations/{recommendation_id}/reject"

# Marks recommendation as rejected
```

## End-to-End Testing Workflow

### Test Flow:
```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api"

# 1. Upload test articles
echo "1. Uploading articles..."
ARTICLE_ID=$(curl -s -X POST "$BASE_URL/articles/upload" \
  -F "file=@test_article.md" \
  -F "title=Test Article" \
  -F "description=Test description" \
  -F "tags=test" | jq -r '.id')

echo "Article ID: $ARTICLE_ID"

# 2. Import tickets
echo "2. Importing tickets..."
curl -s -X POST "$BASE_URL/tickets/upload-csv" \
  -F "file=@tickets.csv" | jq

# 3. Get initial dashboard stats
echo "3. Initial stats:"
curl -s -X GET "$BASE_URL/audits/dashboard/stats" | jq

# 4. Start audit
echo "4. Starting audit..."
JOB_ID=$(curl -s -X POST "$BASE_URL/audits/run" | jq -r '.job_id')
echo "Audit Job ID: $JOB_ID"

# 5. Poll audit status
echo "5. Checking audit progress..."
for i in {1..60}; do
  STATUS=$(curl -s -X GET "$BASE_URL/audits/status/$JOB_ID" | jq -r '.status')
  PROGRESS=$(curl -s -X GET "$BASE_URL/audits/status/$JOB_ID" | jq '.percent_complete')
  echo "Attempt $i - Status: $STATUS - Progress: $PROGRESS%"
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  
  sleep 2
done

# 6. Get final stats
echo "6. Final stats:"
curl -s -X GET "$BASE_URL/audits/dashboard/stats" | jq

# 7. Get top stale articles
echo "7. Top stale articles:"
curl -s -X GET "$BASE_URL/audits/stale/top?limit=5" | jq

# 8. Get pending recommendations
echo "8. Pending recommendations:"
RECS=$(curl -s -X GET "$BASE_URL/recommendations/pending?limit=5" | jq)
echo "$RECS" | jq

# 9. Accept first recommendation
REC_ID=$(echo "$RECS" | jq -r '.[0].id')
if [ ! -z "$REC_ID" ] && [ "$REC_ID" != "null" ]; then
  echo "9. Accepting recommendation $REC_ID..."
  curl -s -X POST "$BASE_URL/recommendations/$REC_ID/accept" | jq
fi
```

## Performance Testing

### Load Testing with Apache Bench

```bash
# Test dashboard stats endpoint
ab -n 1000 -c 10 http://localhost:8000/api/audits/dashboard/stats

# Results will show response time distribution
```

### Load Testing with wrk

```bash
# Install wrk
# brew install wrk (macOS)
# apt-get install wrk (Linux)

wrk -t12 -c400 -d30s http://localhost:8000/api/audits/dashboard/stats
```

## Error Testing

### Invalid Request

```bash
# Missing required fields
curl -X POST http://localhost:8000/api/articles/upload \
  -F "title=Test"
# Returns 422 - Validation Error
```

### Not Found

```bash
curl -X GET "http://localhost:8000/api/articles/invalid-id"
# Returns 404 - Not Found
```

### Invalid CSV Format

```bash
echo "invalid,csv,format" > bad.csv
curl -X POST http://localhost:8000/api/tickets/upload-csv \
  -F "file=@bad.csv"
# Returns 400 - Bad Request with error details
```

## Integration Testing Checklist

- [ ] Upload article via API
- [ ] Search for uploaded article
- [ ] Import tickets via CSV
- [ ] Start audit workflow
- [ ] Poll audit status until completion
- [ ] Verify dashboard stats updated
- [ ] Get top stale articles
- [ ] Get pending recommendations
- [ ] Accept/reject recommendations
- [ ] Update article based on recommendation
- [ ] Verify search works across all new data

## Debugging

### Enable Request Logging

```bash
# See all API requests and responses
docker-compose logs -f backend | grep api
```

### Check Database Directly

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U user -d kb_auditor

# In psql:
\dt                    # List tables
SELECT * FROM articles;
SELECT * FROM audit_results;
SELECT * FROM ai_recommendations;
```

### Check MinIO Storage

```bash
# Access MinIO console
# http://localhost:9001
# Username: minioadmin
# Password: minioadmin

# Or use AWS CLI with MinIO
aws s3 ls s3://kb-articles/ --endpoint-url http://localhost:9000
```

## Common Issues & Solutions

### Articles not appearing after upload

```bash
# Check MinIO connectivity
curl -I http://localhost:9000/minio/health/live

# Check database
docker-compose exec postgres psql -U user -d kb_auditor \
  -c "SELECT count(*) FROM articles;"
```

### Audit stuck in "running" status

```bash
# Check backend logs
docker-compose logs -f backend

# Restart audit job
docker-compose restart backend

# Check Groq API status
curl https://api.groq.com/status
```

### High API response times

```bash
# Check database connection pool
docker-compose logs backend | grep "pool"

# Check MinIO performance
aws s3 ls s3://kb-articles/ --endpoint-url http://localhost:9000

# Profile endpoint
curl -X GET "http://localhost:8000/api/audits/dashboard/stats"
```

## Useful jq Filters

```bash
# Extract field from JSON response
curl -s http://localhost:8000/api/audits/dashboard/stats | jq '.total_articles'

# Filter recommendations by type
curl -s http://localhost:8000/api/recommendations/pending | jq '.[] | select(.recommendation_type=="missing_info")'

# Get article titles
curl -s http://localhost:8000/api/articles | jq '.[] | .title'

# Count stale articles
curl -s http://localhost:8000/api/audits/stale/top | jq 'length'
```

## Next Steps

1. Run the end-to-end workflow
2. Monitor real-time responses in Swagger UI
3. Check MinIO console for uploaded files
4. Query PostgreSQL for data verification
5. Review API response times
6. Test error scenarios
7. Load test the API
8. Plan production deployment

See DEPLOYMENT.md for production testing procedures.
