# 🚀 Run PackOptima Locally in VS Code

## 📋 Prerequisites

Make sure you have these installed:
- ✅ Docker Desktop (running)
- ✅ VS Code
- ✅ Git

---

## 🎯 STEP 1: Download Repository from GitHub (2 minutes)

### Option A: Clone Fresh Copy

Open a new terminal and run:

```bash
cd D:\
git clone https://github.com/Yeswanth0007-12/BUSINESS-IDEA.git PackOptima-Fresh
cd PackOptima-Fresh
code .
```

This will:
1. Download your repository from GitHub
2. Create a new folder `PackOptima-Fresh`
3. Open it in VS Code

### Option B: Use Current Folder

If you want to use your current folder, just make sure it's up to date:

```bash
git pull origin main
```

---

## 🎯 STEP 2: Start Docker Services (3 minutes)

Open VS Code terminal and run:

```bash
docker-compose up -d
```

This starts:
- ✅ PostgreSQL database (port 5432)
- ✅ Redis (port 6379)
- ✅ Backend API (port 8000)
- ✅ Frontend (port 8080)
- ✅ Celery worker (background tasks)

**Wait 30-60 seconds** for all services to start.

---

## 🎯 STEP 3: Check Services are Running (1 minute)

```bash
docker-compose ps
```

You should see all services with status "Up":
- `postgres` - Up
- `redis` - Up
- `backend` - Up
- `frontend` - Up
- `celery_worker` - Up

---

## 🎯 STEP 4: Run Database Migrations (1 minute)

```bash
docker-compose exec backend alembic upgrade head
```

This creates all database tables.

---

## 🎯 STEP 5: Open Your App! 🎉

Open your browser:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000/docs

---

## 📊 What's Running

| Service | Port | URL |
|---------|------|-----|
| Frontend | 8080 | http://localhost:8080 |
| Backend | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| Celery Worker | - | (background) |

---

## 🔧 Useful Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose down
docker-compose up -d --build
```

### Access Database
```bash
docker-compose exec postgres psql -U packoptima -d packoptima
```

### Access Redis CLI
```bash
docker-compose exec redis redis-cli
```

---

## 🆘 Troubleshooting

### "Port already in use"
Stop the service using that port:
```bash
# Stop all Docker containers
docker-compose down

# Or stop specific port (example for 8080)
netstat -ano | findstr :8080
taskkill /PID <PID_NUMBER> /F
```

### "Database connection error"
Make sure PostgreSQL is running:
```bash
docker-compose ps postgres
docker-compose logs postgres
```

### "Redis connection error"
Make sure Redis is running:
```bash
docker-compose ps redis
docker-compose logs redis
```

### Services won't start
```bash
# Clean everything and start fresh
docker-compose down -v
docker-compose up -d --build
```

---

## 🎯 Complete Fresh Start Commands

If you want to start completely fresh, run these commands in order:

```bash
# 1. Download repository
cd D:\
git clone https://github.com/Yeswanth0007-12/BUSINESS-IDEA.git PackOptima-Fresh
cd PackOptima-Fresh

# 2. Open in VS Code
code .

# 3. Start Docker services (in VS Code terminal)
docker-compose up -d

# 4. Wait 60 seconds, then run migrations
docker-compose exec backend alembic upgrade head

# 5. Open browser
# Go to: http://localhost:8080
```

---

## 📱 Access from Other Devices (Same Network)

If you want to access from your phone/tablet on the same WiFi:

1. Find your computer's IP address:
```bash
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter (e.g., 10.249.42.28)

2. Open on your phone:
```
http://10.249.42.28:8080
```

---

## ✅ What You Get with Docker

✅ **PostgreSQL**: Full database with all tables  
✅ **Redis**: For caching and background tasks  
✅ **Backend**: All 13 API endpoints  
✅ **Frontend**: All 12 pages  
✅ **Celery Worker**: Background optimization tasks  
✅ **Everything configured**: No manual setup needed  

---

## 🎊 Summary

**To run locally**:
1. Clone repo from GitHub
2. Open in VS Code
3. Run: `docker-compose up -d`
4. Run: `docker-compose exec backend alembic upgrade head`
5. Open: http://localhost:8080

**Everything runs in Docker - PostgreSQL, Redis, Backend, Frontend, Celery!** 🚀

