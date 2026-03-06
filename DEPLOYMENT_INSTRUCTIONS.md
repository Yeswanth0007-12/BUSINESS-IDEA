# 🚀 PackOptima AI - Quick Deployment Instructions

## Deploy in 3 Simple Steps

### Step 1: Install Docker

**Windows/Mac**:
- Download Docker Desktop: https://www.docker.com/products/docker-desktop/
- Install and start Docker Desktop

**Linux (Ubuntu/Debian)**:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and log back in
```

### Step 2: Run Deployment Script

**Linux/Mac**:
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows (PowerShell)**:
```powershell
docker-compose up -d --build
```

**Windows (Git Bash)**:
```bash
bash deploy.sh
```

### Step 3: Access Application

Open your browser and go to:
- **Application**: http://localhost
- **API Docs**: http://localhost:8000/docs

---

## That's It! 🎉

Your PackOptima AI application is now running!

### First Time Setup

1. **Register an account**:
   - Go to http://localhost
   - Click "Register here"
   - Fill in email, password, and company name

2. **Add products**:
   - Navigate to "Products"
   - Click "Add Product"
   - Enter product details

3. **Add boxes**:
   - Navigate to "Boxes"
   - Click "Add Box"
   - Enter box dimensions and cost

4. **Run optimization**:
   - Navigate to "Optimize"
   - Click "Run Optimization"
   - View savings!

---

## Useful Commands

### View Logs
```bash
docker-compose logs -f
```

### Stop Application
```bash
docker-compose down
```

### Restart Application
```bash
docker-compose restart
```

### Check Status
```bash
docker-compose ps
```

---

## Need Help?

- **Full Guide**: See `DEPLOYMENT_GUIDE.md`
- **API Docs**: http://localhost:8000/docs
- **Logs**: `docker-compose logs -f`

---

## ⚠️ Important for Production

Before deploying to production, update these in `docker-compose.yml`:

1. **Database password** (line 11)
2. **SECRET_KEY** (line 28)
3. **ALLOWED_ORIGINS** (line 31)

Then enable HTTPS (see DEPLOYMENT_GUIDE.md)

---

## Troubleshooting

**Services won't start?**
```bash
docker-compose down
docker-compose up -d --build --force-recreate
```

**Port already in use?**
- Stop other services using ports 80, 8000, or 5432
- Or change ports in `docker-compose.yml`

**Need to reset everything?**
```bash
docker-compose down -v  # WARNING: Deletes all data!
docker-compose up -d --build
```

---

**Status**: ✅ Ready to Deploy!
