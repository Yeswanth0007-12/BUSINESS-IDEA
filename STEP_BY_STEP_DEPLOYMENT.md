# 🚀 PackOptima Docker Deployment - Step by Step Guide

## ✅ Prerequisites Check

Before starting, verify you have:

1. **Docker Desktop installed and running**
   - Windows: Docker Desktop for Windows
   - Check: Open Docker Desktop app - should show "Docker Desktop is running"

2. **Command line access**
   - Open PowerShell or Command Prompt
   - Navigate to your project folder

3. **Ports available**
   - 5432 (PostgreSQL)
   - 6379 (Redis)
   - 8000 (Backend API)
   - 8080 (Frontend)

---

## 📍 Step 1: Navigate to Project Directory

Open PowerShell or Command Prompt and navigate to your PackOptima project folder:

```powershell
cd C:\path\to\your\packoptima-project
```

**Verify you're in the right place:**
```powershell
dir
```

You should see:
- `docker-compose.yml`
- `Dockerfile.backend`
- `Dockerfile.frontend`
- `backend/` folder
- `frontend/` folder

---

## 🧹 Step 2: Clean Up Existing Containers (If Any)

If you've deployed before, clean up old containers:

```powershell
docker-compose down -v
```

**What this does:**
- Stops all running containers
- Removes containers
- Removes volumes (fresh database)
- Removes networks

**Expected output:**
```
[+] Running 6/6
 ✔ Container packoptima-frontend Removed
 ✔ Container packoptima-celery-worker Removed
 ✔ Container packoptima-backend Removed
 ✔ Container packoptima-redis Removed
 ✔ Container packoptima-db Removed
 ✔ Volume packoptima_postgres_data Removed
```

**⏱️ Time:** 10-30 seconds

---

## 🏗️ Step 3: Build and Start All Services

Build Docker images and start all services:

```powershell
docker-compose up --build -d
```

**What this does:**
- Builds backend Docker image (Python + FastAPI)
- Builds frontend Docker image (React + Nginx)
- Pulls PostgreSQL 14 image
- Pulls Redis 7 image
- Creates network
- Starts all 5 services
- Runs in background (-d = detached mode)

**Expected output:**
```
[+] Building 120.5s (25/25) FINISHED
[+] Running 6/6
 ✔ Network packoptima-network Created
 ✔ Container packoptima-db Started
 ✔ Container packoptima-redis Started
 ✔ Container packoptima-backend Started
 ✔ Container packoptima-celery-worker Started
 ✔ Container packoptima-frontend Started
```

**⏱️ Time:** 2-5 minutes (first build), 30-60 seconds (subsequent builds)

**What's happening behind the scenes:**
1. PostgreSQL starts and initializes database
2. Redis starts
3. Backend waits for database health check
4. Backend runs migrations (creates all tables)
5. Backend starts API server
6. Celery worker connects to Redis
7. Frontend serves static files via Nginx

---

## ✅ Step 4: Verify All Services Are Running

Check that all containers are up and healthy:

```powershell
docker-compose ps
```

**Expected output (ALL should show "Up"):**
```
NAME                        STATUS              PORTS
packoptima-backend          Up (healthy)        0.0.0.0:8000->8000/tcp
packoptima-celery-worker    Up                  
packoptima-db               Up (healthy)        0.0.0.0:5432->5432/tcp
packoptima-frontend         Up                  0.0.0.0:8080->80/tcp
packoptima-redis            Up (healthy)        0.0.0.0:6379->6379/tcp
```

**✅ Success indicators:**
- All 5 containers show "Up"
- Database shows "(healthy)"
- Backend shows "(healthy)"
- Redis shows "(healthy)"

**❌ If any container shows "Restarting" or "Exit":**
- Go to Step 10 (Troubleshooting)

---

## 📋 Step 5: Check Backend Logs

Verify the backend started successfully and migrations ran:

```powershell
docker-compose logs backend --tail=50
```

**Look for these SUCCESS messages:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Also look for migration messages:**
```
INFO  [alembic.runtime.migration] Running upgrade -> 001_initial_migration
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002_enterprise_upgrade
...
INFO  [alembic.runtime.migration] Running upgrade 010 -> 011_warehouse_integration
```

**✅ Success:** You see "Uvicorn running" and all 11 migrations applied

**❌ If you see errors:**
- Database connection errors → Wait 30 seconds, backend will retry
- Import errors → Check Step 10 (Troubleshooting)

---

## 🔍 Step 6: Verify Database Migrations

Check that all 11 migrations were applied:

```powershell
docker-compose exec backend alembic current
```

**Expected output:**
```
011_warehouse_integration (head)
```

**This confirms:**
- All 11 migrations applied successfully
- Database schema is complete
- All tables, indexes, and constraints created

**If you see a different migration number:**
- Run: `docker-compose exec backend alembic upgrade head`

---

## 🔧 Step 7: Check Celery Worker

Verify the Celery worker is connected and ready:

```powershell
docker-compose logs celery-worker --tail=30
```

**Look for these SUCCESS messages:**
```
[tasks]
  . app.tasks.optimization_tasks.optimize_packaging_task
  . app.tasks.optimization_tasks.process_bulk_upload_task

celery@... ready.
```

**✅ Success:** You see "ready" and task list

**❌ If worker keeps restarting:**
- Check Redis is running: `docker-compose ps redis`
- Check logs: `docker-compose logs redis`

---

## 🌐 Step 8: Test Backend API

Test the API is responding:

**Option A: Using PowerShell**
```powershell
Invoke-WebRequest -Uri http://localhost:8000/docs -UseBasicParsing
```

**Option B: Using your browser**
Open: http://localhost:8000/docs

**✅ Success:** You see the Swagger UI with API documentation

**What you should see:**
- Interactive API documentation
- List of all endpoints (auth, products, boxes, optimization, etc.)
- "Authorize" button at top right

---

## 🎨 Step 9: Test Frontend

Open your browser and navigate to:

```
http://localhost:8080
```

**✅ Success:** You see the PackOptima login page

**What you should see:**
- Clean login form
- "Register" link
- PackOptima branding
- No console errors (press F12 to check)

**Try registering a new account:**
1. Click "Register"
2. Fill in email, password, company name
3. Click "Register"
4. You should be redirected to dashboard

---

## 🎉 Step 10: Success! Your Application is Running

**Congratulations!** All services are deployed and running.

### 🔗 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8080 | Main web application |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Backend API** | http://localhost:8000 | REST API endpoints |

### 📊 What's Running

```
┌─────────────────────────────────────────────┐
│         PackOptima System Architecture       │
├─────────────────────────────────────────────┤
│                                             │
│  Frontend (React + Nginx)                   │
│  └─ http://localhost:8080                   │
│                                             │
│  Backend API (FastAPI + Python)             │
│  └─ http://localhost:8000                   │
│                                             │
│  Celery Worker (Async Tasks)                │
│  └─ Processes optimization & bulk uploads   │
│                                             │
│  PostgreSQL Database                        │
│  └─ Stores all application data             │
│                                             │
│  Redis Cache & Queue                        │
│  └─ Task queue & caching                    │
│                                             │
└─────────────────────────────────────────────┘
```

### ✅ Deployment Checklist

- [x] All 5 containers running
- [x] Backend shows "Uvicorn running"
- [x] All 11 migrations applied
- [x] Celery worker shows "ready"
- [x] Frontend loads at http://localhost:8080
- [x] API docs load at http://localhost:8000/docs

---

## 🧪 Step 11: Run Tests (Optional but Recommended)

Verify everything works correctly by running the test suite:

```powershell
# Run all tests
docker-compose exec backend pytest tests/ -v

# Run specific test suites
docker-compose exec backend pytest tests/test_packing_algorithms.py -v
docker-compose exec backend pytest tests/test_shipping_costs.py -v
docker-compose exec backend pytest tests/test_multi_product_packing.py -v
docker-compose exec backend pytest tests/test_property_based.py -v

# Run smoke tests
docker-compose exec backend python smoke_tests/test_smoke.py
```

**Expected:** Most tests should pass (200+ tests)

---

## 📚 Step 12: Load Sample Data (Optional)

To test with sample data:

### Option A: Using the Web Interface
1. Go to http://localhost:8080
2. Login with your account
3. Navigate to "Products" → "Import CSV"
4. Upload `sample_data/products_sample.csv`
5. Navigate to "Boxes" → "Import CSV"
6. Upload `sample_data/boxes_sample.csv`

### Option B: Using Docker Commands
```powershell
# Copy sample files into container
docker cp sample_data/products_sample.csv packoptima-backend:/tmp/
docker cp sample_data/boxes_sample.csv packoptima-backend:/tmp/

# Assign current boxes to products (for savings calculation)
docker-compose exec backend python assign_current_boxes_in_container.py
```

---

## 🔄 Common Operations

### View Logs (Real-time)
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs backend -f
docker-compose logs celery-worker -f
docker-compose logs frontend -f
```

**Press Ctrl+C to stop viewing logs**

### Restart Services
```powershell
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart celery-worker
```

### Stop Services
```powershell
# Stop all (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

### Start Services Again
```powershell
# Start without rebuilding
docker-compose up -d

# Start with rebuild
docker-compose up --build -d
```

### Access Container Shell
```powershell
# Backend shell
docker-compose exec backend bash

# Database shell
docker-compose exec database psql -U packoptima_user -d packoptima_db

# Redis shell
docker-compose exec redis redis-cli
```

---

## 🆘 Troubleshooting

### Problem 1: Backend keeps restarting

**Symptoms:**
```
packoptima-backend    Restarting
```

**Solution:**
```powershell
# Check logs
docker-compose logs backend --tail=100

# Common causes:
# 1. Database not ready - wait 30 seconds
# 2. Migration error - check migration logs
# 3. Import error - check Python syntax

# Try restarting
docker-compose restart backend
```

---

### Problem 2: Database connection error

**Symptoms:**
```
could not connect to server: Connection refused
sqlalchemy.exc.OperationalError
```

**Solution:**
```powershell
# Check database is running
docker-compose ps database

# Check database logs
docker-compose logs database --tail=50

# Restart database
docker-compose restart database

# Wait 10 seconds for health check
Start-Sleep -Seconds 10

# Restart backend
docker-compose restart backend
```

---

### Problem 3: Port already in use

**Symptoms:**
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
# Change "8000:8000" to "8001:8000"
```

---

### Problem 4: Celery worker not processing tasks

**Symptoms:**
- Tasks stuck in "pending" state
- Worker logs show connection errors

**Solution:**
```powershell
# Check Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis --tail=50

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# Restart worker
docker-compose restart celery-worker
```

---

### Problem 5: Frontend shows blank page

**Symptoms:**
- White screen
- No content loads

**Solution:**
```powershell
# Check frontend logs
docker-compose logs frontend --tail=50

# Check browser console (F12)
# Look for API connection errors

# Rebuild frontend
docker-compose up --build frontend -d

# Clear browser cache
# Press Ctrl+Shift+Delete
```

---

### Problem 6: Migrations not applied

**Symptoms:**
```
alembic current shows: (empty)
```

**Solution:**
```powershell
# Manually run migrations
docker-compose exec backend alembic upgrade head

# Check current version
docker-compose exec backend alembic current

# Should show: 011_warehouse_integration (head)
```

---

### Problem 7: Need fresh start

**When to use:** Everything is broken, start over

**Solution:**
```powershell
# Stop and remove everything
docker-compose down -v

# Remove all images (optional)
docker-compose down --rmi all -v

# Rebuild and start
docker-compose up --build -d

# Wait 60 seconds for everything to start
Start-Sleep -Seconds 60

# Check status
docker-compose ps
```

---

## 🔍 Health Checks

### Check Backend Health
```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/monitoring/health -UseBasicParsing
```

**Expected:** Status 200, JSON response

### Check Database Health
```powershell
docker-compose exec database pg_isready -U packoptima_user
```

**Expected:** `packoptima_user:5432 - accepting connections`

### Check Redis Health
```powershell
docker-compose exec redis redis-cli ping
```

**Expected:** `PONG`

### Check All Services
```powershell
docker-compose ps
```

**Expected:** All show "Up" or "Up (healthy)"

---

## 📊 Monitoring

### View Resource Usage
```powershell
docker stats
```

**Shows:**
- CPU usage per container
- Memory usage per container
- Network I/O
- Disk I/O

**Press Ctrl+C to exit**

### View Container Details
```powershell
docker-compose ps -a
```

### View Networks
```powershell
docker network ls
```

### View Volumes
```powershell
docker volume ls
```

---

## 🎯 Next Steps

Now that your application is deployed:

### 1. Create Your First Admin User
- Go to http://localhost:8080
- Click "Register"
- Fill in details
- Login

### 2. Import Sample Data
- Navigate to Products → Import CSV
- Upload `sample_data/products_sample.csv`
- Navigate to Boxes → Import CSV
- Upload `sample_data/boxes_sample.csv`

### 3. Run Your First Optimization
- Go to "Optimize" page
- Select a product
- Click "Optimize"
- View recommendations

### 4. Test Multi-Product Orders
- Go to "Orders" page
- Create new order
- Add multiple products
- Run optimization
- View packing plan

### 5. Try Bulk Upload
- Go to "Bulk Upload" page
- Upload CSV with multiple products
- Monitor progress
- View results

---

## 📖 Additional Documentation

For more details, see:

- **API_DOCUMENTATION.md** - Complete API reference
- **DOCKER_DEPLOYMENT_GUIDE.md** - Detailed deployment guide
- **docs/WAREHOUSE_INTEGRATION_GUIDE.md** - Warehouse API integration
- **docs/DEPLOYMENT_GUIDE.md** - Production deployment
- **docs/MONITORING_SETUP_GUIDE.md** - Monitoring setup

---

## 🎉 Congratulations!

Your PackOptima v2.0 system is now fully deployed and running!

**System Status:** ✅ OPERATIONAL

**Services Running:**
- ✅ PostgreSQL Database
- ✅ Redis Cache & Queue
- ✅ FastAPI Backend
- ✅ Celery Worker
- ✅ React Frontend

**Features Available:**
- ✅ User Authentication
- ✅ Product & Box Management
- ✅ Single Product Optimization
- ✅ Multi-Product Order Packing
- ✅ Bulk CSV Upload
- ✅ Async Task Processing
- ✅ Advanced Analytics
- ✅ Warehouse API Integration
- ✅ Webhook Notifications

**Database:**
- ✅ 11 Migrations Applied
- ✅ All Tables Created
- ✅ All Indexes Created

---

**Deployment Guide Version:** 2.0
**Last Updated:** 2026-03-05
**Status:** ✅ PRODUCTION READY
