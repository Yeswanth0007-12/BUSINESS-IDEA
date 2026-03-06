# Docker Deployment Guide - Step by Step

## Prerequisites

Before starting, ensure you have:
- ✅ Docker Desktop installed and running
- ✅ Docker Compose installed (comes with Docker Desktop)
- ✅ At least 4GB RAM available for Docker
- ✅ Ports 5432, 6379, 8000, 8080 available

## Step-by-Step Deployment

### Step 1: Stop Any Running Containers

First, clean up any existing containers:

```bash
docker-compose down -v
```

**What this does:**
- Stops all running containers
- Removes containers
- Removes volumes (fresh database)

**Expected output:**
```
[+] Running X/X
 ✔ Container packoptima-frontend Removed
 ✔ Container packoptima-backend Removed
 ✔ Container packoptima-celery-worker Removed
 ✔ Container packoptima-db Removed
 ✔ Container packoptima-redis Removed
 ✔ Volume removed
 ✔ Network removed
```

---

### Step 2: Build and Start All Services

Build Docker images and start all services:

```bash
docker-compose up --build -d
```

**What this does:**
- Builds Docker images for backend and frontend
- Starts PostgreSQL database
- Starts Redis cache/queue
- Starts backend API
- Starts Celery worker
- Starts frontend
- Runs in detached mode (-d)

**Expected output:**
```
[+] Building X.Xs
[+] Running 6/6
 ✔ Network packoptima-network Created
 ✔ Container packoptima-db Started
 ✔ Container packoptima-redis Started
 ✔ Container packoptima-backend Started
 ✔ Container packoptima-celery-worker Started
 ✔ Container packoptima-frontend Started
```

**Time:** 2-5 minutes (first build takes longer)

---

### Step 3: Verify All Services Are Running

Check that all containers are healthy:

```bash
docker-compose ps
```

**Expected output:**
```
NAME                        STATUS              PORTS
packoptima-backend          Up (healthy)        0.0.0.0:8000->8000/tcp
packoptima-celery-worker    Up                  
packoptima-db               Up (healthy)        0.0.0.0:5432->5432/tcp
packoptima-frontend         Up                  0.0.0.0:8080->80/tcp
packoptima-redis            Up (healthy)        0.0.0.0:6379->6379/tcp
```

**All containers should show "Up" status**

---

### Step 4: Check Backend Logs

Verify the backend started successfully:

```bash
docker-compose logs backend --tail=50
```

**Look for:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**If you see errors, check Step 10 (Troubleshooting)**

---

### Step 5: Check Database Migrations

Verify all migrations were applied:

```bash
docker-compose exec backend alembic current
```

**Expected output:**
```
011_warehouse_integration (head)
```

**This confirms all 11 migrations are applied**

---

### Step 6: Check Celery Worker

Verify the Celery worker is connected:

```bash
docker-compose logs celery-worker --tail=30
```

**Look for:**
```
[tasks]
  . app.tasks.optimization_tasks.optimize_packaging_task

celery@... ready.
```

---

### Step 7: Test Backend API

Test the API is responding:

```bash
curl http://localhost:8000/docs
```

**Or open in browser:**
```
http://localhost:8000/docs
```

**You should see the Swagger UI documentation**

---

### Step 8: Test Frontend

Open the frontend in your browser:

```
http://localhost:8080
```

**You should see the PackOptima login page**

---

### Step 9: Create Sample Data (Optional)

Load sample products and boxes:

```bash
# Copy sample data into container
docker cp sample_data/products_sample.csv packoptima-backend:/tmp/
docker cp sample_data/boxes_sample.csv packoptima-backend:/tmp/

# Import data (if you have import scripts)
docker-compose exec backend python scripts/import_sample_data.py
```

---

### Step 10: Run Tests

Execute the test suite to verify everything works:

```bash
# Run all tests
docker-compose exec backend pytest tests/ -v

# Run specific test suites
docker-compose exec backend pytest tests/test_packing_algorithms.py -v
docker-compose exec backend pytest tests/test_shipping_costs.py -v
docker-compose exec backend pytest tests/test_property_based.py -v

# Run smoke tests
docker-compose exec backend python smoke_tests/test_smoke.py
```

---

## Quick Reference Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs backend -f
docker-compose logs celery-worker -f
docker-compose logs database -f
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart celery-worker
```

### Stop Services
```bash
# Stop all (keeps data)
docker-compose stop

# Stop and remove (keeps data)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

### Access Container Shell
```bash
# Backend shell
docker-compose exec backend bash

# Database shell
docker-compose exec database psql -U packoptima_user -d packoptima_db

# Redis shell
docker-compose exec redis redis-cli
```

### Database Operations
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# Check current migration
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history
```

---

## Troubleshooting

### Problem: Backend keeps restarting

**Check logs:**
```bash
docker-compose logs backend --tail=100
```

**Common causes:**
1. Database not ready - wait 30 seconds and check again
2. Migration error - check migration logs
3. Import error - check Python syntax

**Solution:**
```bash
docker-compose down
docker-compose up --build -d
```

---

### Problem: Database connection error

**Error message:**
```
could not connect to server: Connection refused
```

**Solution:**
```bash
# Check database is running
docker-compose ps database

# Restart database
docker-compose restart database

# Wait for health check
docker-compose ps
```

---

### Problem: Port already in use

**Error message:**
```
Error: port is already allocated
```

**Solution:**
```bash
# Find what's using the port
netstat -ano | findstr :8000

# Stop the process or change port in docker-compose.yml
```

---

### Problem: Celery worker not processing tasks

**Check:**
```bash
docker-compose logs celery-worker --tail=50
```

**Solution:**
```bash
# Restart worker
docker-compose restart celery-worker

# Check Redis connection
docker-compose exec redis redis-cli ping
```

---

### Problem: Frontend shows blank page

**Check:**
```bash
docker-compose logs frontend --tail=50
```

**Solution:**
```bash
# Rebuild frontend
docker-compose up --build frontend -d

# Check browser console for errors
```

---

## Service URLs

Once deployed, access services at:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:8080 | Web application |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache/Queue |

---

## Health Checks

### Backend Health
```bash
curl http://localhost:8000/api/v1/monitoring/health
```

### Database Health
```bash
docker-compose exec database pg_isready -U packoptima_user
```

### Redis Health
```bash
docker-compose exec redis redis-cli ping
```

---

## Production Deployment Notes

For production deployment:

1. **Change default passwords** in docker-compose.yml:
   - POSTGRES_PASSWORD
   - SECRET_KEY

2. **Use environment files:**
   ```bash
   cp backend/.env.example backend/.env.production
   # Edit .env.production with production values
   ```

3. **Enable HTTPS:**
   - Add SSL certificates
   - Configure reverse proxy (Nginx/Traefik)

4. **Set up monitoring:**
   - Prometheus for metrics
   - Grafana for dashboards
   - Sentry for error tracking

5. **Configure backups:**
   - Database backups (daily)
   - Volume backups
   - Configuration backups

---

## Next Steps

After successful deployment:

1. ✅ Create admin user
2. ✅ Import sample data
3. ✅ Test all features
4. ✅ Run performance tests
5. ✅ Set up monitoring
6. ✅ Configure backups

---

## Support

If you encounter issues:

1. Check logs: `docker-compose logs [service]`
2. Check service status: `docker-compose ps`
3. Restart services: `docker-compose restart`
4. Rebuild if needed: `docker-compose up --build -d`

---

**Deployment Status:** ✅ READY
**Last Updated:** 2026-03-05
**Version:** 2.0 (Production Logistics Upgrade)

