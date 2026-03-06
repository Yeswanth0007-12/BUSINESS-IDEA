# Quick Deployment Commands

## Step 1: Run Database Migrations

```bash
# Inside Docker container
docker-compose exec backend alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade 010 -> 011, warehouse integration
```

## Step 2: Restart Docker Services

```bash
# Stop all services
docker-compose down

# Rebuild and start all services
docker-compose up -d --build
```

Expected services:
- postgres (database)
- redis (cache and queue)
- backend (API server)
- celery_worker (async task processor)
- frontend (React application)

## Step 3: Verify Services

```bash
# Check all services are running
docker-compose ps

# Check backend logs
docker-compose logs -f backend

# Check worker logs
docker-compose logs -f celery_worker

# Check Redis
docker-compose logs redis
```

## Step 4: Test the Application

### Test Basic Functionality
1. Open browser: http://localhost:3000
2. Login with existing credentials
3. Navigate to Products page
4. Navigate to Boxes page
5. Run an optimization

### Test New Features

**Test Async Optimization:**
```bash
curl -X POST http://localhost:8000/api/v1/optimize/async \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1
  }'
```

**Test Bulk Upload:**
1. Navigate to Bulk Upload page
2. Upload a CSV file with orders
3. Monitor processing status

**Test Analytics:**
1. Navigate to Analytics Dashboard
2. View space utilization metrics
3. View box usage frequency
4. View shipping cost trends

**Test Warehouse API:**
1. Login to application
2. Navigate to Settings > API Keys
3. Create a new API key (save it!)
4. Test with cURL:

```bash
curl -X POST http://localhost:8000/api/v1/warehouse/optimize-package \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "TEST-001",
    "items": [
      {
        "sku": "PROD-123",
        "quantity": 2
      }
    ]
  }'
```

## Step 5: Run Tests (Optional)

```bash
# Run unit tests
docker-compose exec backend pytest tests/ -v

# Run integration tests
docker-compose exec backend pytest tests/test_integration_workflows.py -v

# Run performance tests
docker-compose exec backend pytest tests/test_performance_benchmarks.py -v

# Run smoke tests
docker-compose exec backend python smoke_tests/smoke_test.py
```

## Step 6: Monitor Performance

### Check API Health
```bash
curl http://localhost:8000/health
```

### Check Celery Worker
```bash
docker-compose exec celery_worker celery -A app.core.celery_app inspect active
```

### Check Redis
```bash
docker-compose exec redis redis-cli ping
```

### Check Database
```bash
docker-compose exec postgres psql -U packoptima -d packoptima -c "SELECT COUNT(*) FROM products;"
```

## Troubleshooting

### Migration Fails
```bash
# Check current migration version
docker-compose exec backend alembic current

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# Try upgrade again
docker-compose exec backend alembic upgrade head
```

### Service Won't Start
```bash
# Check logs
docker-compose logs backend
docker-compose logs celery_worker

# Restart specific service
docker-compose restart backend
docker-compose restart celery_worker
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping

# Restart Redis
docker-compose restart redis
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check database exists
docker-compose exec postgres psql -U packoptima -l

# Restart PostgreSQL
docker-compose restart postgres
```

## Production Deployment

For production deployment, see:
- `docs/DEPLOYMENT_GUIDE.md` - Complete deployment procedures
- `scripts/deploy_migrations.sh` - Database migration script
- `scripts/deploy_api.sh` - API server deployment script
- `scripts/deploy_workers.sh` - Celery worker deployment script
- `docs/ROLLBACK_PROCEDURES.md` - Rollback procedures

## Environment Variables

Make sure these are set in your `.env` file:

```bash
# Database
DATABASE_URL=postgresql://packoptima:password@postgres:5432/packoptima

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start all services |
| `docker-compose down` | Stop all services |
| `docker-compose ps` | Check service status |
| `docker-compose logs -f SERVICE` | View service logs |
| `docker-compose restart SERVICE` | Restart a service |
| `docker-compose exec SERVICE COMMAND` | Run command in service |

## Success Indicators

✅ All services show "Up" in `docker-compose ps`
✅ Backend logs show "Application startup complete"
✅ Worker logs show "celery@worker ready"
✅ Redis responds to PING with PONG
✅ Database migrations are at version 011
✅ Frontend loads at http://localhost:3000
✅ API docs available at http://localhost:8000/docs
✅ Health check returns 200 OK

---

**Ready to deploy!** 🚀

Follow these steps in order, and your PackOptima v2.0 upgrade will be complete.
