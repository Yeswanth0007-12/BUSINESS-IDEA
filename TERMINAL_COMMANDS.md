# PackOptima AI - Terminal Commands for Deployment

## 🚀 Quick Deployment (Copy & Paste These Commands)

### Step 1: Open PowerShell
1. Press `Windows + X`
2. Click "Windows PowerShell" or "Terminal"

### Step 2: Navigate to Project Directory
```powershell
cd "D:\Saas  startup"
```

### Step 3: Make Sure Docker Desktop is Running
- Look for the whale icon in your system tray
- If not running, open Docker Desktop and wait for it to start

### Step 4: Stop Any Existing Containers (if running)
```powershell
docker compose down
```

### Step 5: Deploy the Application
```powershell
docker compose up -d --build
```

**What this does:**
- Builds the Docker images (first time takes 5-10 minutes)
- Starts all 3 services (database, backend, frontend)
- Runs in background mode

### Step 6: Wait for Services to Start
```powershell
Start-Sleep -Seconds 30
```

Or just wait 30 seconds manually.

### Step 7: Check if Everything is Running
```powershell
docker compose ps
```

**Expected output:** All 3 containers should show "Up" or "Running"

### Step 8: Test Backend Health
```powershell
curl http://localhost:8000/health
```

**Expected output:** `{"status":"healthy"}`

### Step 9: Open the Application
Open your web browser and go to:
```
http://localhost:8080
```

---

## 📋 All Commands in One Block (Copy & Paste)

```powershell
# Navigate to project
cd "D:\Saas  startup"

# Stop existing containers
docker compose down

# Deploy application
docker compose up -d --build

# Wait 30 seconds
Start-Sleep -Seconds 30

# Check status
docker compose ps

# Test backend
curl http://localhost:8000/health
```

Then open browser to: **http://localhost:8080**

---

## 🛠️ Useful Management Commands

### View Logs (Real-time)
```powershell
# All services
docker compose logs -f

# Press Ctrl+C to stop viewing logs

# Specific service only
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f database
```

### Check Service Status
```powershell
docker compose ps
```

### Restart Services
```powershell
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart frontend
docker compose restart database
```

### Stop Services
```powershell
# Stop all services (keeps data)
docker compose down

# Stop and remove all data (WARNING: deletes database!)
docker compose down -v
```

### Start Services Again (After Stopping)
```powershell
# Start without rebuilding
docker compose up -d

# Start with rebuild
docker compose up -d --build
```

### View Resource Usage
```powershell
docker stats
```

### Clean Rebuild (If Something Goes Wrong)
```powershell
# Stop everything
docker compose down -v

# Remove old images
docker system prune -a

# Rebuild from scratch
docker compose up -d --build
```

---

## 🔍 Verification Commands

### Check if Docker is Installed
```powershell
docker --version
docker compose version
```

### Check if Containers are Running
```powershell
docker ps
```

### Check Specific Container Status
```powershell
docker inspect packoptima-backend --format='{{.State.Status}}'
docker inspect packoptima-frontend --format='{{.State.Status}}'
docker inspect packoptima-db --format='{{.State.Status}}'
```

### Test Backend API
```powershell
# Health check
curl http://localhost:8000/health

# API documentation
Start-Process http://localhost:8000/docs
```

### Test Frontend
```powershell
Start-Process http://localhost:8080
```

---

## 🐛 Troubleshooting Commands

### If Backend Keeps Restarting
```powershell
# View backend logs
docker logs packoptima-backend --tail=50

# Check for errors
docker compose logs backend | Select-String -Pattern "error"
```

### If Frontend Not Accessible
```powershell
# Check frontend logs
docker logs packoptima-frontend --tail=50

# Check if port 8080 is in use
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
```

### If Database Connection Fails
```powershell
# Check database logs
docker logs packoptima-db --tail=50

# Check if database is healthy
docker inspect packoptima-db --format='{{.State.Health.Status}}'

# Access database directly
docker compose exec database psql -U packoptima_user -d packoptima_db
```

### Check What's Using a Port
```powershell
# Check port 80
Get-NetTCPConnection -LocalPort 80 -ErrorAction SilentlyContinue

# Check port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

# Check port 8080
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

# Check port 5432
Get-NetTCPConnection -LocalPort 5432 -ErrorAction SilentlyContinue
```

---

## 💾 Backup Commands

### Create Database Backup
```powershell
# Create backup with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
docker compose exec -T database pg_dump -U packoptima_user packoptima_db > "backup_$timestamp.sql"
```

### Restore Database Backup
```powershell
# Restore from backup file
Get-Content backup.sql | docker compose exec -T database psql -U packoptima_user packoptima_db
```

---

## 📊 Monitoring Commands

### View All Container Logs
```powershell
docker compose logs --tail=100
```

### View Logs for Last 5 Minutes
```powershell
docker compose logs --since 5m
```

### Follow Logs for Specific Service
```powershell
docker compose logs -f backend
```

### Check Disk Usage
```powershell
docker system df
```

### Check Container Resource Usage
```powershell
docker stats --no-stream
```

---

## 🔄 Update/Rebuild Commands

### Rebuild Specific Service
```powershell
# Rebuild backend only
docker compose up -d --build backend

# Rebuild frontend only
docker compose up -d --build frontend
```

### Pull Latest Images
```powershell
docker compose pull
```

### Rebuild Everything from Scratch
```powershell
# Stop and remove everything
docker compose down -v

# Remove all unused images
docker system prune -a

# Rebuild and start
docker compose up -d --build
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| **Deploy** | `docker compose up -d --build` |
| **Stop** | `docker compose down` |
| **Restart** | `docker compose restart` |
| **View Logs** | `docker compose logs -f` |
| **Check Status** | `docker compose ps` |
| **Backend Health** | `curl http://localhost:8000/health` |
| **Open Frontend** | `Start-Process http://localhost:8080` |
| **Open API Docs** | `Start-Process http://localhost:8000/docs` |
| **Clean Rebuild** | `docker compose down -v; docker compose up -d --build` |

---

## 🌐 Access URLs

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:8080 |
| **Backend API** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API Docs (ReDoc)** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |

---

## ✅ Success Indicators

After running `docker compose up -d --build`, you should see:

```
✔ Network saasstartup_packoptima-network Created
✔ Container packoptima-db Healthy
✔ Container packoptima-backend Started
✔ Container packoptima-frontend Started
```

After running `docker compose ps`, you should see:

```
NAME                   STATUS              PORTS
packoptima-backend     Up X minutes        0.0.0.0:8000->8000/tcp
packoptima-db          Up X minutes        0.0.0.0:5432->5432/tcp
packoptima-frontend    Up X minutes        0.0.0.0:8080->80/tcp
```

After running `curl http://localhost:8000/health`, you should see:

```json
{"status":"healthy"}
```

---

## 🎉 You're Done!

Once all commands complete successfully:

1. Open browser to **http://localhost:8080**
2. Click "Register here"
3. Create your account
4. Start using PackOptima AI!

---

**Last Updated:** March 3, 2026
**Version:** 1.0.0
