# 🚀 Docker Quick Start - 3 Commands

## Prerequisites
- ✅ Docker Desktop installed and running
- ✅ Navigate to project folder in PowerShell/CMD

---

## Deploy in 3 Commands

### 1️⃣ Clean Up (if needed)
```powershell
docker-compose down -v
```

### 2️⃣ Build & Start
```powershell
docker-compose up --build -d
```
⏱️ Wait 2-5 minutes for first build

### 3️⃣ Verify
```powershell
docker-compose ps
```

**Expected:** All 5 containers show "Up"

---

## Access Your App

| What | URL |
|------|-----|
| **Frontend** | http://localhost:8080 |
| **API Docs** | http://localhost:8000/docs |

---

## Quick Checks

```powershell
# View logs
docker-compose logs backend --tail=30

# Check migrations
docker-compose exec backend alembic current
# Should show: 011_warehouse_integration (head)

# Run tests
docker-compose exec backend pytest tests/ -v
```

---

## Common Commands

```powershell
# View all logs (real-time)
docker-compose logs -f

# Restart everything
docker-compose restart

# Stop everything
docker-compose down

# Fresh start (deletes data)
docker-compose down -v
docker-compose up --build -d
```

---

## Troubleshooting

### Backend won't start?
```powershell
docker-compose logs backend --tail=100
docker-compose restart backend
```

### Need fresh start?
```powershell
docker-compose down -v
docker-compose up --build -d
```

### Check health
```powershell
docker-compose ps
docker-compose logs -f
```

---

## Success Checklist

- [ ] All 5 containers running
- [ ] Frontend loads: http://localhost:8080
- [ ] API docs load: http://localhost:8000/docs
- [ ] Can register and login
- [ ] Can upload products/boxes

---

**For detailed guide, see:** STEP_BY_STEP_DEPLOYMENT.md
