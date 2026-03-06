# 🔄 Fresh Start Deployment - Delete Everything & Redeploy

## Complete Fresh Start - Step by Step

Follow these commands **in order** to delete everything and start fresh.

---

## Step 1: Stop All Running Containers

```bash
docker-compose down
```

**What this does:**
- Stops all running containers
- Removes containers
- Keeps volumes (data)

**Expected output:**
```
[+] Running 6/6
 ✔ Container packoptima-frontend Removed
 ✔ Container packoptima-celery-worker Removed
 ✔ Container packoptima-backend Removed
 ✔ Container packoptima-redis Removed
 ✔ Container packoptima-db Removed
 ✔ Network removed
```

---

## Step 2: Delete All Containers AND Data (Fresh Database)

```bash
docker-compose down -v
```

**What this does:**
- Stops all containers
- Removes all containers
- **Deletes all volumes (DATABASE WILL BE EMPTY)**
- Removes networks

**⚠️ WARNING:** This deletes ALL your data! Use this for a completely fresh start.

**Expected output:**
```
[+] Running 7/7
 ✔ Container packoptima-frontend Removed
 ✔ Container packoptima-celery-worker Removed
 ✔ Container packoptima-backend Removed
 ✔ Container packoptima-redis Removed
 ✔ Container packoptima-db Removed
 ✔ Volume saasstartup_postgres_data Removed
 ✔ Network saasstartup_packoptima-network Removed
```

---

## Step 3: (Optional) Remove Old Images

If you want to rebuild everything from scratch:

```bash
docker-compose down -v --rmi all
```

**What this does:**
- Everything from Step 2
- **Also removes Docker images**
- Forces complete rebuild

**Or manually remove images:**
```bash
docker images
docker rmi packoptima-backend packoptima-frontend
```

---

## Step 4: Build Fresh Images and Start Everything

```bash
docker-compose up --build -d
```

**What this does:**
- Builds Docker images from scratch
- Creates new containers
- Creates fresh database
- Starts all services in background (-d)

**Expected output:**
```
[+] Building 120.5s (backend)
[+] Building 45.2s (frontend)
[+] Running 6/6
 ✔ Network packoptima-network Created
 ✔ Container packoptima-db Started
 ✔ Container packoptima-redis Started
 ✔ Container packoptima-backend Started
 ✔ Container packoptima-celery-worker Started
 ✔ Container packoptima-frontend Started
```

**⏱️ Time:** 3-5 minutes (building images takes time)

---

## Step 5: Wait for Services to Start

Wait 30-60 seconds for all services to initialize, then check:

```bash
docker-compose ps
```

**Expected output (all should show "Up"):**
```
NAME                        STATUS              PORTS
packoptima-backend          Up (healthy)        0.0.0.0:8000->8000/tcp
packoptima-celery-worker    Up                  
packoptima-db               Up (healthy)        0.0.0.0:5432->5432/tcp
packoptima-frontend         Up                  0.0.0.0:8080->80/tcp
packoptima-redis            Up (healthy)        0.0.0.0:6379->6379/tcp
```

---

## Step 6: Verify Backend Started Successfully

```bash
docker-compose logs backend --tail=50
```

**Look for this line:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**If you see errors, wait another 30 seconds and check again.**

---

## Step 7: Verify Database Migrations

```bash
docker-compose exec backend alembic current
```

**Expected output:**
```
011_warehouse_integration (head)
```

**This confirms all 11 migrations were applied successfully!**

---

## Step 8: Verify Celery Worker

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

## Step 9: Test the Application

### Test Backend API:
```bash
curl http://localhost:8000/docs
```

**Or open in browser:**
```
http://localhost:8000/docs
```

**You should see Swagger UI**

### Test Frontend:
**Open in browser:**
```
http://localhost:8080
```

**You should see the login page**

---

## Step 10: (Optional) Run Tests

```bash
docker-compose exec backend pytest tests/ -v
```

---

## 🎯 Complete Command Sequence (Copy & Paste)

Here's the complete sequence in one block:

```bash
# 1. Stop and delete everything
docker-compose down -v

# 2. Wait 5 seconds
sleep 5

# 3. Build and start fresh
docker-compose up --build -d

# 4. Wait 60 seconds for services to start
sleep 60

# 5. Check status
docker-compose ps

# 6. Check backend logs
docker-compose logs backend --tail=50

# 7. Verify migrations
docker-compose exec backend alembic current

# 8. Test API (open in browser)
echo "Open http://localhost:8000/docs"
echo "Open http://localhost:8080"
```

---

## 🔍 Troubleshooting

### Problem: Backend keeps restarting

**Check logs:**
```bash
docker-compose logs backend --tail=100
```

**Solution:** Wait 60 seconds, services need time to start

---

### Problem: "Connection refused" errors

**Cause:** Database not ready yet

**Solution:**
```bash
# Wait and restart backend
sleep 30
docker-compose restart backend
```

---

### Problem: Port already in use

**Error:**
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solution:**
```bash
# Find what's using the port
netstat -ano | findstr :8000

# Kill the process or stop other containers
docker ps -a
docker stop <container_id>
```

---

### Problem: Still having issues

**Nuclear option - delete EVERYTHING:**

```bash
# Stop all Docker containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all volumes
docker volume prune -f

# Remove all networks
docker network prune -f

# Remove all images (optional)
docker rmi $(docker images -q)

# Now start fresh
docker-compose up --build -d
```

---

## 📊 What Gets Deleted vs What Stays

### ❌ Gets Deleted (with `docker-compose down -v`):
- All containers
- All volumes (database data)
- All networks
- Container logs

### ✅ Stays (your code):
- All source code files
- docker-compose.yml
- Dockerfiles
- Configuration files
- Everything in your project folder

**Your code is safe! Only Docker containers and data are deleted.**

---

## 🎯 Quick Reference

| Command | What it does |
|---------|-------------|
| `docker-compose down` | Stop containers, keep data |
| `docker-compose down -v` | Stop containers, **delete data** |
| `docker-compose down -v --rmi all` | Delete everything including images |
| `docker-compose up --build -d` | Build fresh and start |
| `docker-compose ps` | Check status |
| `docker-compose logs [service]` | View logs |
| `docker-compose restart [service]` | Restart one service |

---

## ✅ Success Checklist

After fresh deployment, verify:

- [ ] All 5 containers show "Up" status
- [ ] Backend logs show "Uvicorn running"
- [ ] Migrations show "011_warehouse_integration (head)"
- [ ] Celery worker shows "ready"
- [ ] Frontend loads at http://localhost:8080
- [ ] API docs load at http://localhost:8000/docs
- [ ] No error messages in logs

---

## 🚀 You're Done!

Your system is now freshly deployed with:
- ✅ Clean database
- ✅ All migrations applied
- ✅ All services running
- ✅ Ready to use

**Next steps:**
1. Register a new user at http://localhost:8080
2. Add products and boxes
3. Run your first optimization!

---

**Fresh Start Guide**
**Version:** 2.0
**Last Updated:** 2026-03-05

