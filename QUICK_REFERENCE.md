# PackOptima AI - Quick Reference Card

## 🎯 Test Results
✅ **ALL 22 TESTS PASSED** - Application is fully operational!

---

## 🚀 Quick Start Commands

```bash
# Start application
docker compose up -d

# Stop application
docker compose down

# Restart application
docker compose restart

# View logs
docker logs packoptima-backend
docker logs packoptima-frontend

# Rebuild after changes
docker compose up -d --build
```

---

## 🌐 Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:8080 | Main web application |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | Backend health status |

---

## 🔐 First Time Setup

1. **Start services**: `docker compose up -d`
2. **Open browser**: http://localhost:8080
3. **Register account**:
   - Email: your@email.com
   - Company: Your Company
   - Password: min 8 characters
4. **Start using!**

---

## 📊 Complete Workflow

```
1. Register/Login
   ↓
2. Add Products (Products tab)
   ↓
3. Add Boxes (Boxes tab)
   ↓
4. Run Optimization (Optimize tab)
   ↓
5. View Results (Dashboard/History/Leakage tabs)
```

---

## 🎯 Navigation Tabs

| Tab | Purpose |
|-----|---------|
| **Dashboard** | Overview metrics and KPIs |
| **Products** | Manage product catalog |
| **Boxes** | Manage box sizes |
| **Optimize** | Run optimization algorithm |
| **History** | View past optimization runs |
| **Leakage** | Analyze cost leakage by category |

---

## 📝 Example Data

### Example Product
```
SKU: LAPTOP-001
Name: Gaming Laptop
Category: Electronics
Dimensions: 40cm × 30cm × 5cm
Weight: 3.5 kg
Monthly Volume: 100
```

### Example Box
```
Name: Medium Box
Dimensions: 35cm × 25cm × 15cm
Cost: $2.50
```

---

## 🔧 Common Commands

### Check Container Status
```bash
docker ps
```

### View Backend Logs
```bash
docker logs packoptima-backend --tail 50
```

### Check Backend Health
```bash
# PowerShell
Invoke-WebRequest http://localhost:8000/health

# Bash
curl http://localhost:8000/health
```

### Run Tests
```bash
python FINAL_COMPREHENSIVE_TEST_SUITE.py
```

### Access Database
```bash
docker exec -it packoptima-db psql -U packoptima_user -d packoptima_db
```

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Containers not starting | `docker compose down && docker compose up -d --build` |
| Frontend not loading | Check `docker logs packoptima-frontend` |
| Login not working | Verify password is 8+ characters |
| Backend errors | Check `docker logs packoptima-backend` |
| Port conflicts | Change ports in `docker-compose.yml` |

---

## 📚 Documentation Files

- **COMPLETE_USER_GUIDE.md** - Full user guide (this is the main guide!)
- **APPLICATION_COMPLETE.md** - Quick start
- **FINAL_DEPLOYMENT_STATUS.md** - Technical details
- **USER_GUIDE.md** - Feature documentation

---

## ✅ System Status

- **Backend**: ✅ Healthy (http://localhost:8000/health)
- **Frontend**: ✅ Running (http://localhost:8080)
- **Database**: ✅ Connected
- **Authentication**: ✅ Working
- **All Features**: ✅ Operational

---

## 🎊 You're Ready!

Your PackOptima AI platform is fully operational. Open http://localhost:8080 and start optimizing your packaging costs!

**Need help?** Read the **COMPLETE_USER_GUIDE.md** for detailed instructions.
