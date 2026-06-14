# Quick Start Guide - KB Freshness Auditor

## 🚀 Start in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- Groq API key (free from https://console.groq.com)

### Step 1: Get API Key
```bash
# Visit https://console.groq.com and create account
# Generate an API key (copy it)
```

### Step 2: Configure
```bash
cd KB-Freshness-Auditor
cp backend/.env.example backend/.env

# Edit backend/.env and add:
# GROQ_API_KEY=your_api_key_here
```

### Step 3: Start Services
```bash
docker-compose up -d

# Wait 30 seconds for services to be healthy
docker-compose ps
```

### Step 4: Access Application
```
Dashboard: http://localhost:8000
API Docs: http://localhost:8000/docs
MinIO Console: http://localhost:9001 (user: minioadmin / pass: minioadmin)
```

### Step 5: Test It

#### Upload a Test Article
1. Go to http://localhost:8000
2. Click "Knowledge Base" in sidebar
3. Create a test file:
   ```
   # How to Reset Password
   
   Step 1: Click "Forgot Password"
   Step 2: Check email
   Step 3: Set new password
   ```
4. Drag-drop or click upload
5. Fill in title, description, tags
6. Click Upload

#### Import Test Tickets
1. Create `tickets.csv`:
   ```csv
   ticket_id,subject,description,category,article_id,created_at,resolved,resolved_at
   TICK-001,Password Reset,User can't reset,account-access,,2024-01-15T10:00:00Z,false,
   ```
2. In "Tickets" section, drag-drop CSV file

#### Run Audit
1. Click "Audit" in sidebar
2. Click "Start Audit" button
3. Watch progress bar
4. When done, see results and recommendations

#### Review Results
1. Go back to Dashboard
2. See updated statistics
3. Check "Recommendations" tab for AI suggestions
4. Accept/Reject recommendations

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview, installation, features |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Developer setup and guidelines |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment checklist |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture details |
| [API_TESTING.md](API_TESTING.md) | API testing with curl examples |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | What was built and status |

## 🔧 Common Commands

### Docker Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart service
docker-compose restart backend

# Clean everything
docker-compose down -v
```

### Database Access
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U user -d kb_auditor

# List tables
\dt

# Query articles
SELECT * FROM articles;
```

### API Testing
```bash
# Check health
curl http://localhost:8000/health

# Get dashboard stats
curl http://localhost:8000/api/audits/dashboard/stats | jq

# List articles
curl http://localhost:8000/api/articles | jq
```

## 🎯 What This Application Does

```
┌─ User Uploads KB Articles
│
├─ System Analyzes Freshness
│  ├─ Article Age
│  ├─ Related Support Tickets
│  └─ Last Update Date
│
├─ Generates Freshness Score
│  └─ Fresh (🟢) | Warning (🟡) | Stale (🔴)
│
├─ AI Analyzes Stale Articles
│  ├─ Identifies Missing Information
│  ├─ Generates Update Suggestions
│  └─ Creates Improved Versions
│
└─ Service Desk Team Reviews
   ├─ Accepts AI Recommendations
   ├─ Updates KB Articles
   └─ Reduces Support Tickets
```

## 📊 Key Features

✅ **Automatic Freshness Auditing** - Identifies outdated KB articles  
✅ **AI-Powered Recommendations** - Uses Groq LLM for content suggestions  
✅ **Dashboard Analytics** - Real-time statistics and charts  
✅ **Ticket Correlation** - Links support tickets to articles  
✅ **CSV Bulk Import** - Import thousands of tickets at once  
✅ **Enterprise UI** - Professional, responsive interface  
✅ **REST API** - Integrate with existing systems  

## 🔍 Freshness Score Formula

```
Score = (article_age_days × 0.5) + (ticket_count × 0.3) + (days_since_last_update × 0.2)

Fresh:   Score < 30
Warning: Score 30-60
Stale:   Score > 60
```

## 🚨 Troubleshooting

### Services won't start
```bash
# Check ports not in use
lsof -i :8000
lsof -i :5432
lsof -i :9000

# Or use docker ps
docker ps -a
```

### API errors
```bash
# Check logs
docker-compose logs -f backend

# Verify Groq API key
echo $GROQ_API_KEY

# Check database connectivity
docker-compose logs -f postgres
```

### Audit stuck
```bash
# Wait up to 2 minutes for large datasets
# Check Groq API rate limits
# Restart backend service
docker-compose restart backend
```

## 📞 Support

### Getting Help
- Check [README.md](README.md) for overview
- See [DEVELOPMENT.md](DEVELOPMENT.md) for setup issues
- Review [API_TESTING.md](API_TESTING.md) for API problems
- Check logs: `docker-compose logs -f`

### Documentation Structure
```
┌─ README.md ─────────────────── Start here
│
├─ DEVELOPMENT.md ──────────── Local development
├─ DEPLOYMENT.md ──────────── Production setup
├─ ARCHITECTURE.md ─────────── Technical details
├─ API_TESTING.md ───────────── API examples
│
├─ IMPLEMENTATION_SUMMARY.md ── What was built
├─ API_EXAMPLES.md ──────────── Response formats
├─ SAMPLE_DATA.md ────────────── Import examples
│
└─ This file ──────────────── Quick reference
```

## 🎓 Learning Path

1. **First Time?**
   - Read this file
   - Run `docker-compose up`
   - Test with sample data
   - Check Dashboard

2. **Want to Understand?**
   - Read [README.md](README.md)
   - Review [ARCHITECTURE.md](ARCHITECTURE.md)
   - Check code comments

3. **Ready to Develop?**
   - See [DEVELOPMENT.md](DEVELOPMENT.md)
   - Set up local environment
   - Review code structure

4. **Going to Production?**
   - Check [DEPLOYMENT.md](DEPLOYMENT.md)
   - Review security settings
   - Set up monitoring

## 💡 Pro Tips

**Tip 1: Use Swagger UI**
- Go to http://localhost:8000/docs
- Test all endpoints directly
- See request/response examples

**Tip 2: Check MinIO Console**
- Go to http://localhost:9001
- Log in (minioadmin / minioadmin)
- Browse uploaded article files

**Tip 3: Query Database**
- Connect to PostgreSQL
- Check table contents
- Verify data integrity

**Tip 4: Monitor Logs**
- Watch logs during audit: `docker-compose logs -f backend`
- Use timestamps to find errors
- Check database logs too

**Tip 5: Test API with curl**
```bash
# Create alias for quick testing
alias api='curl -s http://localhost:8000/api'

# Now use:
api/articles
api/audits/dashboard/stats
api/recommendations/pending
```

## 🎉 Success Indicators

✅ Docker services are running  
✅ Can access http://localhost:8000  
✅ Can upload article files  
✅ Can import tickets from CSV  
✅ Can start audit and see progress  
✅ Can see dashboard statistics  
✅ Can view AI recommendations  
✅ API documentation loads at /docs  

## 🚀 Next Steps

1. ✅ Start services (`docker-compose up -d`)
2. ✅ Upload sample article
3. ✅ Import sample tickets
4. ✅ Run first audit
5. ✅ Review recommendations
6. ✅ Read full documentation
7. ✅ Plan production deployment

---

**Questions?** Check the documentation files listed above.  
**Ready to deploy?** See DEPLOYMENT.md  
**Want to develop?** See DEVELOPMENT.md  

**Happy auditing! 🎯**
