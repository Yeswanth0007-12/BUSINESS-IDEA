# ⚡ Quick Start - Run Locally

## 🚀 4 Commands to Run Everything

```bash
# 1. Clone from GitHub
git clone https://github.com/Yeswanth0007-12/BUSINESS-IDEA.git PackOptima
cd PackOptima

# 2. Start all services (PostgreSQL, Redis, Backend, Frontend, Celery)
docker-compose up -d

# 3. Wait 60 seconds, then run migrations
docker-compose exec backend alembic upgrade head

# 4. Open browser
# http://localhost:8080
```

**Done! Everything is running!** ✅

---

## 📊 What's Running

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Celery Worker**: (background)

---

## 🔧 Common Commands

```bash
# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Restart
docker-compose restart

# Rebuild after changes
docker-compose up -d --build
```

---

## 🆘 Problems?

```bash
# Fresh start
docker-compose down -v
docker-compose up -d --build
docker-compose exec backend alembic upgrade head
```

---

**Full guide**: `RUN_LOCALLY_IN_VSCODE.md`

