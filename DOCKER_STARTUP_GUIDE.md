# Docker Desktop Startup Guide

## ❌ ERROR: Docker Desktop Not Running

The error you're seeing means Docker Desktop is not started on your Windows machine.

```
error during connect: ... open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified
```

---

## ✅ SOLUTION: Start Docker Desktop

### Step 1: Launch Docker Desktop

1. **Click Windows Start Menu**
2. **Search for "Docker Desktop"**
3. **Click on Docker Desktop** to launch it
4. **Wait for Docker to start** (you'll see a whale icon in system tray)
5. **Wait until the whale icon stops animating** (means Docker is ready)

**This usually takes 30-60 seconds**

### Step 2: Verify Docker is Running

Open PowerShell or Command Prompt and run:

```bash
docker --version
```

You should see something like:
```
Docker version 24.0.x, build xxxxx
```

Then check if Docker daemon is running:

```bash
docker ps
```

If Docker is running, you'll see a table (even if empty). If not, you'll see the same error.

---

## 🚀 STEP-BY-STEP: Complete Deployment

### 1. Start Docker Desktop
- Open Docker Desktop application
- Wait for it to fully start (whale icon stops animating)

### 2. Navigate to Project Directory
```bash
cd D:\Saas\startup
```

### 3. Build and Start Containers
```bash
docker compose up -d --build
```

**Expected output**:
```
[+] Building ...
[+] Running 3/3
 ✔ Container packoptima-db        Started
 ✔ Container packoptima-backend   Started
 ✔ Container packoptima-frontend  Started
```

### 4. Wait for Startup (15 seconds)
```bash
# Wait 15 seconds for all services to initialize
timeout /t 15
```

### 5. Verify Containers are Running
```bash
docker ps
```

You should see 3 containers:
- `packoptima-frontend` (port 8080)
- `packoptima-backend` (port 8000)
- `packoptima-db` (port 5432)

### 6. Test Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy"}
```

### 7. Open Application
Open your browser and go to:
```
http://localhost:8080
```

---

## 📁 Upload Sample Data

### Upload Products (20 items)

1. **Login** to the application
2. **Go to Products page**
3. **Click "Bulk Upload CSV"** (green button)
4. **Select file**: `D:\Saas\startup\sample_data\products_sample.csv`
5. **Click "Upload"**
6. **Verify**: "Successfully uploaded 20 products"

### Upload Boxes (20 items)

1. **Go to Boxes page**
2. **Click "Bulk Upload CSV"** (green button)
3. **Select file**: `D:\Saas\startup\sample_data\boxes_sample.csv`
4. **Click "Upload"**
5. **Verify**: "Successfully uploaded 20 boxes"

---

## 🔧 Troubleshooting

### Issue: Docker Desktop won't start

**Solutions**:
1. **Restart your computer**
2. **Check if Hyper-V is enabled** (Windows feature)
3. **Check if WSL 2 is installed** (required for Docker Desktop)
4. **Reinstall Docker Desktop** if necessary

### Issue: "Port already in use"

**Solution**:
```bash
# Stop all containers
docker compose down

# Wait 5 seconds
timeout /t 5

# Start again
docker compose up -d
```

### Issue: Containers keep restarting

**Check logs**:
```bash
# Backend logs
docker logs packoptima-backend

# Frontend logs
docker logs packoptima-frontend

# Database logs
docker logs packoptima-db
```

### Issue: Can't access http://localhost:8080

**Solutions**:
1. **Check if frontend container is running**: `docker ps`
2. **Check frontend logs**: `docker logs packoptima-frontend`
3. **Try different port**: Check if 8080 is already in use
4. **Clear browser cache**: Ctrl+Shift+Delete

---

## 📋 Complete Command Sequence

Copy and paste these commands one by one:

```bash
# 1. Navigate to project
cd D:\Saas\startup

# 2. Stop any existing containers
docker compose down

# 3. Build and start fresh
docker compose up -d --build

# 4. Wait for startup
timeout /t 15

# 5. Check containers
docker ps

# 6. Check backend health
curl http://localhost:8000/health

# 7. Check frontend (open in browser)
start http://localhost:8080
```

---

## ✅ Success Indicators

You'll know everything is working when:

1. ✅ Docker Desktop shows "Engine running" (green)
2. ✅ `docker ps` shows 3 containers running
3. ✅ `curl http://localhost:8000/health` returns `{"status":"healthy"}`
4. ✅ Browser opens http://localhost:8080 and shows login page
5. ✅ Can login successfully
6. ✅ Can upload CSV files without errors
7. ✅ Products and boxes appear in tables

---

## 🎯 Quick Reference

| Command | Purpose |
|---------|---------|
| `docker --version` | Check Docker is installed |
| `docker ps` | List running containers |
| `docker compose up -d` | Start containers in background |
| `docker compose down` | Stop all containers |
| `docker compose up -d --build` | Rebuild and start |
| `docker logs <container>` | View container logs |
| `docker restart <container>` | Restart a container |

---

## 📞 Still Having Issues?

### Check Docker Desktop Status

1. Open Docker Desktop
2. Look at bottom left corner
3. Should say "Engine running" in green
4. If red or yellow, Docker is not ready

### Check Windows Services

1. Press `Win + R`
2. Type `services.msc`
3. Look for "Docker Desktop Service"
4. Should be "Running"
5. If not, right-click → Start

### Check System Requirements

Docker Desktop requires:
- Windows 10/11 Pro, Enterprise, or Education
- Hyper-V enabled
- WSL 2 installed
- At least 4GB RAM
- Virtualization enabled in BIOS

---

## 🎉 Next Steps After Successful Startup

1. ✅ Upload sample products (20 items)
2. ✅ Upload sample boxes (20 items)
3. ✅ Run optimization test
4. ✅ Check analytics dashboard
5. ✅ View optimization history
6. ✅ Test all features

---

**Remember**: Always start Docker Desktop BEFORE running docker commands!

**Sample Data Location**:
- Products: `D:\Saas\startup\sample_data\products_sample.csv`
- Boxes: `D:\Saas\startup\sample_data\boxes_sample.csv`
