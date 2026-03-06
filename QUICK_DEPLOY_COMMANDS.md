# Quick Deploy Commands - Copy & Paste

## 🚀 Fresh Deployment (Start Here)

```bash
# Step 1: Clean up
docker-compose down -v

# Step 2: Build and start
docker-compose up --build -d

# Step 3: Wait 30 seconds, then check status
docker-compose ps

# Step 4: Check backend logs
docker-compose logs backend --tail=50

# Step 5: Verify migrations
docker-compose exec backend alembic current

# Step 6: Open in browser
# Frontend: http://localhost:8080
# API Docs: http://localhost:8000/docs
```

---

## ✅ Verification Commands

```bash
# Check all services are running
docker-compose ps

# Check backend is healthy
curl http://localhost:8000/docs

# Check database migrations
docker-compose exec backend alembic current

# Check Celery worker
docker-compose logs celery-worker --tail=20
```

---

## 🧪 Run Tests

```bash
# Run all tests
docker-compose exec backend pytest tests/ -v

# Run specific test file
docker-compose exec backend pytest tests/test_packing_algorithms.py -v

# Run property-based tests
docker-compose exec backend pytest tests/test_property_based.py -v

# Run smoke tests
docker-compose exec backend python smoke_tests/test_smoke.py

# Run with coverage
docker-compose exec backend pytest tests/ --cov=app --cov-report=html
```

---

## 📊 View Logs

```bash
# All services (live)
docker-compose logs -f

# Backend only
docker-compose logs backend -f

# Last 100 lines
docker-compose logs backend --tail=100

# Celery worker
docker-compose logs celery-worker -f

# Database
docker-compose logs database --tail=50
```

---

## 🔄 Restart Services

```bash
# Restart all
docker-compose restart

# Restart backend only
docker-compose restart backend

# Restart worker only
docker-compose restart celery-worker

# Rebuild and restart
docker-compose up --build -d
```

---

## 🛑 Stop Services

```bash
# Stop (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything (deletes data)
docker-compose down -v
```

---

## 🔧 Database Commands

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Check current migration
docker-compose exec backend alembic current

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# Access database shell
docker-compose exec database psql -U packoptima_user -d packoptima_db

# Backup database
docker-compose exec database pg_dump -U packoptima_user packoptima_db > backup.sql
```

---

## 🐚 Access Container Shells

```bash
# Backend shell
docker-compose exec backend bash

# Database shell
docker-compose exec database bash

# Redis CLI
docker-compose exec redis redis-cli

# Run Python in backend
docker-compose exec backend python
```

---

## 📦 Import Sample Data

```bash
# Copy CSV files to container
docker cp sample_data/products_sample.csv packoptima-backend:/tmp/
docker cp sample_data/boxes_sample.csv packoptima-backend:/tmp/

# Run import script (if available)
docker-compose exec backend python scripts/import_data.py
```

---

## 🔍 Debug Commands

```bash
# Check container resource usage
docker stats

# Inspect container
docker inspect packoptima-backend

# Check network
docker network inspect saasstartup_packoptima-network

# Check volumes
docker volume ls

# Remove unused resources
docker system prune -a
```

---

## 🚨 Emergency Commands

```bash
# Force rebuild everything
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Reset database only
docker-compose stop backend celery-worker
docker-compose rm -f database
docker volume rm saasstartup_postgres_data
docker-compose up -d

# View all container logs
docker-compose logs --tail=1000 > all_logs.txt
```

---

## 📱 Quick Health Checks

```bash
# Backend API
curl http://localhost:8000/docs

# Database
docker-compose exec database pg_isready -U packoptima_user

# Redis
docker-compose exec redis redis-cli ping

# All services
docker-compose ps
```

---

## 🎯 Common Workflows

### First Time Setup
```bash
docker-compose down -v
docker-compose up --build -d
sleep 30
docker-compose ps
docker-compose logs backend --tail=50
```

### After Code Changes
```bash
docker-compose down
docker-compose up --build -d
docker-compose logs backend -f
```

### Run Tests After Changes
```bash
docker-compose exec backend pytest tests/ -v --tb=short
```

### Check Everything is Working
```bash
docker-compose ps
docker-compose exec backend alembic current
curl http://localhost:8000/docs
```

---

## 💡 Pro Tips

1. **Always check logs first:**
   ```bash
   docker-compose logs backend --tail=100
   ```

2. **Use -f to follow logs in real-time:**
   ```bash
   docker-compose logs backend -f
   ```

3. **Rebuild when you change dependencies:**
   ```bash
   docker-compose up --build -d
   ```

4. **Use -v to see verbose test output:**
   ```bash
   docker-compose exec backend pytest tests/ -v
   ```

5. **Check service health:**
   ```bash
   docker-compose ps
   ```

---

## 📞 Quick Troubleshooting

| Problem | Command |
|---------|---------|
| Backend won't start | `docker-compose logs backend --tail=100` |
| Database error | `docker-compose restart database` |
| Port in use | `docker-compose down` then change port |
| Worker not processing | `docker-compose restart celery-worker` |
| Need fresh start | `docker-compose down -v && docker-compose up --build -d` |

---

**Quick Reference Card**
**Version:** 2.0
**Last Updated:** 2026-03-05

