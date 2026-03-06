# 📇 Quick Reference Card - PackOptima Deployment

## 🚀 Deploy Commands

```powershell
# Clean up
docker-compose down -v

# Build & start
docker-compose up --build -d

# Verify
docker-compose ps
```

---

## 🌐 Access URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8080 |
| API Docs | http://localhost:8000/docs |
| Backend | http://localhost:8000 |

---

## ✅ Verify Commands

```powershell
# Check services
docker-compose ps

# Check backend logs
docker-compose logs backend --tail=30

# Check migrations
docker-compose exec backend alembic current

# Run tests
docker-compose exec backend pytest tests/ -v
```

---

## 🔄 Common Operations

```powershell
# View logs (real-time)
docker-compose logs -f

# View specific service logs
docker-compose logs backend -f

# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend

# Stop (keep data)
docker-compose down

# Stop (delete data)
docker-compose down -v

# Start
docker-compose up -d

# Rebuild & start
docker-compose up --build -d
```

---

## 🆘 Troubleshooting

```powershell
# Container won't start
docker-compose logs [service] --tail=100
docker-compose restart [service]

# Database connection error
docker-compose restart database
Start-Sleep -Seconds 10
docker-compose restart backend

# Fresh start
docker-compose down -v
docker-compose up --build -d

# Check health
docker-compose ps
docker stats
```

---

## 🔍 Inspection Commands

```powershell
# Access backend shell
docker-compose exec backend bash

# Access database
docker-compose exec database psql -U packoptima_user -d packoptima_db

# Access Redis
docker-compose exec redis redis-cli

# Check resource usage
docker stats

# List containers
docker-compose ps -a

# List networks
docker network ls

# List volumes
docker volume ls
```

---

## 📊 Expected Status

```
NAME                        STATUS
packoptima-backend          Up (healthy)
packoptima-celery-worker    Up
packoptima-db               Up (healthy)
packoptima-frontend         Up
packoptima-redis            Up (healthy)
```

---

## ✅ Success Indicators

- [ ] All 5 containers "Up"
- [ ] Backend: "Uvicorn running"
- [ ] Migrations: "011_warehouse_integration"
- [ ] Frontend loads: http://localhost:8080
- [ ] API docs load: http://localhost:8000/docs

---

## 📚 Documentation

| Guide | Time | Best For |
|-------|------|----------|
| DOCKER_QUICK_START.md | 5 min | Quick deploy |
| STEP_BY_STEP_DEPLOYMENT.md | 20 min | Beginners |
| DEPLOYMENT_FLOWCHART.md | 15 min | Visual |
| DOCKER_DEPLOYMENT_GUIDE.md | 30+ min | Complete |

---

## 🎯 Ports

| Port | Service |
|------|---------|
| 5432 | PostgreSQL |
| 6379 | Redis |
| 8000 | Backend |
| 8080 | Frontend |

---

## 📦 Services

```
PostgreSQL 14      → Database
Redis 7            → Cache & Queue
FastAPI Backend    → API Server
Celery Worker      → Async Tasks
React Frontend     → Web UI
```

---

**Print this card for quick reference!**
