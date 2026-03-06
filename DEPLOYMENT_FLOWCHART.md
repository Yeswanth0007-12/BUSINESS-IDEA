# 🚀 PackOptima Deployment Flowchart

## Visual Deployment Process

```
┌─────────────────────────────────────────────────────────────┐
│                    START DEPLOYMENT                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Prerequisites Check                                 │
│  ✓ Docker Desktop installed?                                 │
│  ✓ Docker Desktop running?                                   │
│  ✓ In project directory?                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Clean Up (Optional)                                 │
│  Command: docker-compose down -v                             │
│  ⏱️ Time: 10-30 seconds                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Build & Start Services                              │
│  Command: docker-compose up --build -d                       │
│  ⏱️ Time: 2-5 minutes (first time)                          │
│                                                              │
│  What happens:                                               │
│  1. Builds backend image (Python + FastAPI)                  │
│  2. Builds frontend image (React + Nginx)                    │
│  3. Pulls PostgreSQL 14 image                                │
│  4. Pulls Redis 7 image                                      │
│  5. Creates network                                          │
│  6. Starts all 5 containers                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Verify Services                                     │
│  Command: docker-compose ps                                  │
│                                                              │
│  Expected:                                                   │
│  ✓ packoptima-db          Up (healthy)                       │
│  ✓ packoptima-redis       Up (healthy)                       │
│  ✓ packoptima-backend     Up (healthy)                       │
│  ✓ packoptima-celery-worker Up                               │
│  ✓ packoptima-frontend    Up                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────┴───────┐
                    │  All Up?      │
                    └───────┬───────┘
                            │
                ┌───────────┴───────────┐
                │                       │
               YES                     NO
                │                       │
                ▼                       ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│  STEP 5: Check Logs       │  │  TROUBLESHOOTING         │
│  Command:                 │  │  Check logs:             │
│  docker-compose logs      │  │  docker-compose logs -f  │
│  backend --tail=50        │  │                          │
│                           │  │  Common issues:          │
│  Look for:                │  │  • Database not ready    │
│  ✓ "Uvicorn running"      │  │  • Port conflicts        │
│  ✓ Migrations applied     │  │  • Build errors          │
└───────────────────────────┘  └──────────────────────────┘
                │                       │
                │                       │
                │          ┌────────────┘
                │          │ Fixed?
                │          └────────────┐
                │                       │
                ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: Verify Migrations                                   │
│  Command: docker-compose exec backend alembic current        │
│                                                              │
│  Expected: 011_warehouse_integration (head)                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: Check Celery Worker                                 │
│  Command: docker-compose logs celery-worker --tail=30        │
│                                                              │
│  Look for: "celery@... ready."                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 8: Test Backend API                                    │
│  Open: http://localhost:8000/docs                            │
│                                                              │
│  Expected: Swagger UI with API documentation                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 9: Test Frontend                                       │
│  Open: http://localhost:8080                                 │
│                                                              │
│  Expected: PackOptima login page                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 10: Run Tests (Optional)                               │
│  Command: docker-compose exec backend pytest tests/ -v       │
│                                                              │
│  Expected: 200+ tests pass                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    ✅ DEPLOYMENT COMPLETE                    │
│                                                              │
│  Your application is running at:                             │
│  • Frontend: http://localhost:8080                           │
│  • API Docs: http://localhost:8000/docs                      │
│  • Backend: http://localhost:8000                            │
└─────────────────────────────────────────────────────────────┘
```

---

## System Architecture After Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                            │
│                  (packoptima-network)                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Frontend Container (packoptima-frontend)          │    │
│  │  • React Application                               │    │
│  │  • Nginx Web Server                                │    │
│  │  • Port: 8080 → 80                                 │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          │ HTTP Requests                     │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Backend Container (packoptima-backend)            │    │
│  │  • FastAPI Application                             │    │
│  │  • Python 3.11                                     │    │
│  │  • Uvicorn Server                                  │    │
│  │  • Port: 8000 → 8000                               │    │
│  └────────────────────────────────────────────────────┘    │
│                │                    │                        │
│                │                    │                        │
│                ▼                    ▼                        │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │  Database Container  │  │  Redis Container     │        │
│  │  (packoptima-db)     │  │  (packoptima-redis)  │        │
│  │  • PostgreSQL 14     │  │  • Redis 7           │        │
│  │  • Port: 5432        │  │  • Port: 6379        │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                      │                       │
│                                      │ Task Queue            │
│                                      ▼                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Celery Worker Container                           │    │
│  │  (packoptima-celery-worker)                        │    │
│  │  • Async Task Processing                           │    │
│  │  • Optimization Jobs                               │    │
│  │  • Bulk Upload Processing                          │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
┌──────────┐
│  User    │
└────┬─────┘
     │
     │ 1. Opens browser
     ▼
┌──────────────────┐
│  Frontend        │
│  localhost:8080  │
└────┬─────────────┘
     │
     │ 2. Makes API calls
     ▼
┌──────────────────┐
│  Backend API     │
│  localhost:8000  │
└────┬─────────────┘
     │
     │ 3. Queries/Updates
     ▼
┌──────────────────┐
│  PostgreSQL DB   │
│  localhost:5432  │
└──────────────────┘

     ┌─────────────────────────────┐
     │  For async operations:      │
     │                             │
     │  Backend → Redis Queue      │
     │  Celery Worker ← Redis      │
     │  Worker → Database          │
     └─────────────────────────────┘
```

---

## Container Startup Sequence

```
1. Network Creation
   └─ packoptima-network

2. Database Startup
   └─ PostgreSQL initializes
   └─ Health check passes

3. Redis Startup
   └─ Redis starts
   └─ Health check passes

4. Backend Startup (waits for DB & Redis)
   └─ Runs migrations (001 → 011)
   └─ Starts Uvicorn server
   └─ Health check passes

5. Celery Worker Startup (waits for DB & Redis)
   └─ Connects to Redis
   └─ Registers tasks
   └─ Ready to process jobs

6. Frontend Startup
   └─ Nginx serves static files
   └─ Ready to accept connections
```

---

## Health Check Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Docker Compose Health Checks                                │
└─────────────────────────────────────────────────────────────┘

Database Health Check (every 10s):
┌──────────────────────────────────────┐
│ pg_isready -U packoptima_user        │
│ └─ Success: Container marked healthy │
│ └─ Failure: Retry (max 5 times)     │
└──────────────────────────────────────┘

Redis Health Check (every 10s):
┌──────────────────────────────────────┐
│ redis-cli ping                       │
│ └─ Success: Container marked healthy │
│ └─ Failure: Retry (max 5 times)     │
└──────────────────────────────────────┘

Backend Health Check (every 30s):
┌──────────────────────────────────────┐
│ curl http://localhost:8000/health    │
│ └─ Success: Container marked healthy │
│ └─ Failure: Retry (max 5 times)     │
└──────────────────────────────────────┘
```

---

## Troubleshooting Decision Tree

```
                    ┌─────────────────┐
                    │  Issue?         │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Container     │   │ Connection    │   │ Application   │
│ Won't Start   │   │ Error         │   │ Error         │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                    │
        ▼                   ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Check logs:   │   │ Check health: │   │ Check logs:   │
│ docker-compose│   │ docker-compose│   │ docker-compose│
│ logs [service]│   │ ps            │   │ logs backend  │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                    │
        ▼                   ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Common fixes: │   │ Wait 30s for  │   │ Check:        │
│ • Port in use │   │ health checks │   │ • Migrations  │
│ • Build error │   │ Restart:      │   │ • Imports     │
│ • Missing dep │   │ docker-compose│   │ • Syntax      │
│               │   │ restart       │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## Quick Command Reference

```
┌─────────────────────────────────────────────────────────────┐
│  Essential Commands                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Deploy:                                                     │
│  └─ docker-compose up --build -d                             │
│                                                              │
│  Stop:                                                       │
│  └─ docker-compose down                                      │
│                                                              │
│  Fresh Start:                                                │
│  └─ docker-compose down -v                                   │
│  └─ docker-compose up --build -d                             │
│                                                              │
│  View Status:                                                │
│  └─ docker-compose ps                                        │
│                                                              │
│  View Logs:                                                  │
│  └─ docker-compose logs -f                                   │
│  └─ docker-compose logs [service] --tail=50                  │
│                                                              │
│  Restart:                                                    │
│  └─ docker-compose restart                                   │
│  └─ docker-compose restart [service]                         │
│                                                              │
│  Run Tests:                                                  │
│  └─ docker-compose exec backend pytest tests/ -v             │
│                                                              │
│  Check Migrations:                                           │
│  └─ docker-compose exec backend alembic current              │
│                                                              │
│  Access Shell:                                               │
│  └─ docker-compose exec backend bash                         │
│  └─ docker-compose exec database psql -U packoptima_user     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**For detailed instructions, see:** STEP_BY_STEP_DEPLOYMENT.md
**For quick start, see:** DOCKER_QUICK_START.md
