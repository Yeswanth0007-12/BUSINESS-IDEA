# 🚀 Deploy PackOptima to Render.com

Complete step-by-step guide to deploy your PackOptima platform to Render.com for FREE internet access.

---

## What You'll Get

After deployment, you'll have:
- **Public URL**: `https://packoptima-frontend.onrender.com`
- **Works from anywhere**: Your friend can access from any device, any location
- **Always online**: Runs 24/7 (spins down after 15 min of inactivity on free tier)
- **HTTPS included**: Secure SSL certificate
- **Free tier**: No credit card required

---

## Prerequisites

1. **GitHub Account** (free): https://github.com
2. **Render Account** (free): https://render.com
3. **Git installed** on your computer

---

## Step 1: Push Your Code to GitHub

### 1.1 Check if Git is Initialized

```bash
git status
```

If you see "fatal: not a git repository", initialize git:

```bash
git init
```

### 1.2 Create .gitignore File

Make sure you have a `.gitignore` file to exclude sensitive files:

```bash
# Create .gitignore if it doesn't exist
cat > .gitignore << 'EOF'
# Environment files
.env
.env.local
.env.production
backend/.env
frontend/.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Node
node_modules/
dist/
build/
.npm
.eslintcache

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
postgres_data/

# Docker
.dockerignore

# Test files
.pytest_cache/
.coverage
htmlcov/

# Temporary files
*.tmp
*.bak
EOF
```

### 1.3 Add All Files

```bash
git add .
```

### 1.4 Commit Your Code

```bash
git commit -m "Initial commit - Ready for Render deployment"
```

### 1.5 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `packoptima` (or any name you like)
3. Description: "PackOptima - AI-Powered Logistics Optimization Platform"
4. **Keep it Private** (recommended) or Public
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

### 1.6 Push to GitHub

Copy the commands from GitHub (they look like this):

```bash
git remote add origin https://github.com/YOUR_USERNAME/packoptima.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

**Enter your GitHub credentials when prompted.**

---

## Step 2: Create Render Account

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with:
   - GitHub (recommended - easier integration)
   - GitLab
   - Email

---

## Step 3: Deploy PostgreSQL Database

### 3.1 Create Database

1. In Render Dashboard, click "New +" → "PostgreSQL"
2. **Name**: `packoptima-db`
3. **Database**: `packoptima_db`
4. **User**: `packoptima_user`
5. **Region**: Choose closest to you (e.g., Singapore, Oregon, Frankfurt)
6. **Plan**: **Free**
7. Click "Create Database"

### 3.2 Save Database URL

After creation, you'll see:
- **Internal Database URL**: Copy this (starts with `postgresql://`)
- **External Database URL**: Also copy this

**Save both URLs** - you'll need them in the next steps.

Example:
```
Internal: postgresql://packoptima_user:password@dpg-xxxxx/packoptima_db
External: postgresql://packoptima_user:password@dpg-xxxxx-a.singapore-postgres.render.com/packoptima_db
```

---

## Step 4: Deploy Redis

### 4.1 Create Redis Instance

1. Click "New +" → "Redis"
2. **Name**: `packoptima-redis`
3. **Region**: **Same as your database** (important!)
4. **Plan**: **Free**
5. **Maxmemory Policy**: `noeviction`
6. Click "Create Redis"

### 4.2 Save Redis URL

After creation, copy the **Internal Redis URL**:
```
redis://red-xxxxx:6379
```

---

## Step 5: Deploy Backend API

### 5.1 Create Web Service

1. Click "New +" → "Web Service"
2. Click "Connect a repository"
3. **Authorize Render** to access your GitHub
4. **Select your repository**: `packoptima`
5. Click "Connect"

### 5.2 Configure Backend Service

**Basic Settings:**
- **Name**: `packoptima-backend`
- **Region**: **Same as database and Redis**
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Environment**: `Docker`
- **Dockerfile Path**: `./Dockerfile.backend`
- **Docker Context**: `.`

**Instance Type:**
- **Plan**: **Free**

### 5.3 Add Environment Variables

Click "Advanced" → "Add Environment Variable"

Add these variables one by one:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Paste your **Internal Database URL** from Step 3.2 |
| `REDIS_URL` | Paste your **Internal Redis URL** from Step 4.2 |
| `CELERY_BROKER_URL` | Same as REDIS_URL |
| `CELERY_RESULT_BACKEND` | Same as REDIS_URL |
| `SECRET_KEY` | Click "Generate" button (Render will create a secure key) |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_HOURS` | `24` |
| `ALLOWED_ORIGINS` | `https://packoptima-frontend.onrender.com` |
| `ENVIRONMENT` | `production` |

**Important**: For `ALLOWED_ORIGINS`, you'll update this after deploying the frontend (Step 6).

### 5.4 Deploy Backend

1. Click "Create Web Service"
2. **Wait 5-10 minutes** for deployment
3. Watch the logs - you should see:
   ```
   ==> Running migrations...
   ==> Starting server...
   ==> Server started on port 8000
   ```

### 5.5 Save Backend URL

After deployment, your backend URL will be:
```
https://packoptima-backend.onrender.com
```

**Test it**: Open `https://packoptima-backend.onrender.com/docs` in your browser
- You should see the API documentation (Swagger UI)

---

## Step 6: Deploy Frontend

### 6.1 Update Frontend Environment Variable

First, we need to tell the frontend where the backend is.

**Edit `frontend/.env.production`** (create if it doesn't exist):

```bash
VITE_API_URL=https://packoptima-backend.onrender.com
```

**Commit and push this change:**

```bash
git add frontend/.env.production
git commit -m "Add production API URL"
git push
```

### 6.2 Create Frontend Web Service

1. Click "New +" → "Web Service"
2. **Connect same repository**: `packoptima`
3. Click "Connect"

### 6.3 Configure Frontend Service

**Basic Settings:**
- **Name**: `packoptima-frontend`
- **Region**: **Same as backend**
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Environment**: `Docker`
- **Dockerfile Path**: `./Dockerfile.frontend`
- **Docker Context**: `.`

**Instance Type:**
- **Plan**: **Free**

### 6.4 Add Environment Variable

Click "Advanced" → "Add Environment Variable":

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://packoptima-backend.onrender.com` |

### 6.5 Deploy Frontend

1. Click "Create Web Service"
2. **Wait 5-10 minutes** for deployment
3. Watch the logs

### 6.6 Get Your Public URL

After deployment, your frontend URL will be:
```
https://packoptima-frontend.onrender.com
```

**This is the URL you share with your friend!** 🎉

---

## Step 7: Update Backend CORS

Now that we have the frontend URL, we need to update the backend to allow requests from it.

### 7.1 Update Backend Environment Variable

1. Go to your **backend service** in Render Dashboard
2. Click "Environment" tab
3. Find `ALLOWED_ORIGINS`
4. Update the value to:
   ```
   https://packoptima-frontend.onrender.com
   ```
5. Click "Save Changes"
6. Backend will automatically redeploy (takes 2-3 minutes)

---

## Step 8: Test Your Deployment

### 8.1 Open Your App

Go to: `https://packoptima-frontend.onrender.com`

You should see the PackOptima login page!

### 8.2 Create First User

1. Click "Register"
2. Fill in:
   - **Email**: your-email@example.com
   - **Password**: (choose a strong password)
   - **Company Name**: Your Company
3. Click "Register"

### 8.3 Test Features

1. **Login** with your credentials
2. **Add Products**: Go to Products tab, add some products
3. **Add Boxes**: Go to Boxes tab, add some boxes
4. **Run Optimization**: Go to Optimize tab, run an optimization

**Everything should work!** ✅

---

## Step 9: Share with Your Friend

### 9.1 Send Them the URL

Share this URL with your friend:
```
https://packoptima-frontend.onrender.com
```

### 9.2 Create Account for Them

Option 1: **They create their own account**
- Send them the URL
- They click "Register"
- They create their own account

Option 2: **You create an account for them**
- Register with their email
- Give them the credentials
- They can change password later

### 9.3 Test from Different Location

Ask your friend to:
1. Open the URL on their device
2. Login or register
3. Test the features

**It should work from anywhere in the world!** 🌍

---

## Important Notes

### Free Tier Limitations

⚠️ **Spin Down**: Free services spin down after 15 minutes of inactivity
- First request after spin down takes 30-60 seconds to wake up
- Subsequent requests are fast

⚠️ **750 Hours/Month**: Free tier includes 750 hours/month
- Enough for 1 service running 24/7
- If you have multiple services, they share the 750 hours

⚠️ **Database**: Free PostgreSQL database
- 1 GB storage
- Expires after 90 days (you'll need to create a new one)

### Performance

- **Slower than local**: Free tier uses shared CPU
- **Good for**: Testing, demos, sharing with friends
- **Not good for**: Production business use, high traffic

### Upgrading

If you need better performance:
- **Starter Plan**: $7/month per service
- **No spin down**: Always online
- **More resources**: Better CPU and RAM
- **Persistent database**: No 90-day expiration

---

## Troubleshooting

### Problem 1: Backend Won't Start

**Check logs** in Render Dashboard:

**Common issues:**
- Database URL incorrect → Check Step 3.2
- Redis URL incorrect → Check Step 4.2
- Migration failed → Check database is running

**Solution:**
1. Go to backend service
2. Click "Logs" tab
3. Look for error messages
4. Fix the issue
5. Click "Manual Deploy" → "Deploy latest commit"

### Problem 2: Frontend Shows "Network Error"

**Cause**: Frontend can't reach backend

**Solution:**
1. Check backend is running (green status in Dashboard)
2. Check `VITE_API_URL` in frontend environment variables
3. Check `ALLOWED_ORIGINS` in backend environment variables
4. Make sure both match the actual URLs

### Problem 3: CORS Error

**Error**: "Access to XMLHttpRequest has been blocked by CORS policy"

**Solution:**
1. Go to backend service
2. Update `ALLOWED_ORIGINS` to include frontend URL
3. Save and wait for redeploy

### Problem 4: Database Connection Failed

**Error**: "could not connect to server"

**Solution:**
1. Check database is running (green status)
2. Check `DATABASE_URL` in backend environment variables
3. Make sure you're using the **Internal Database URL**
4. Restart backend service

### Problem 5: Slow First Load

**This is normal!** Free tier spins down after 15 minutes.

**Solutions:**
- Wait 30-60 seconds for first load
- Use a service like UptimeRobot to ping your app every 5 minutes (keeps it awake)
- Upgrade to paid plan ($7/month) for no spin down

---

## Monitoring Your App

### View Logs

1. Go to service in Dashboard
2. Click "Logs" tab
3. See real-time logs

### Check Status

Dashboard shows:
- 🟢 **Running**: Service is healthy
- 🟡 **Deploying**: Service is being deployed
- 🔴 **Failed**: Service has errors

### Metrics

Click "Metrics" tab to see:
- CPU usage
- Memory usage
- Request count
- Response times

---

## Updating Your App

### Make Changes Locally

1. Edit your code
2. Test locally with Docker
3. Commit changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```

### Auto-Deploy

Render automatically deploys when you push to GitHub!

**Watch deployment:**
1. Go to service in Dashboard
2. Click "Events" tab
3. See deployment progress

---

## Cost Breakdown

### Free Tier (What You're Using)

| Service | Cost | Limits |
|---------|------|--------|
| Web Service (Backend) | $0 | 750 hours/month, spins down after 15 min |
| Web Service (Frontend) | $0 | 750 hours/month, spins down after 15 min |
| PostgreSQL | $0 | 1 GB, expires after 90 days |
| Redis | $0 | 25 MB |
| **Total** | **$0/month** | Good for testing and demos |

### Paid Tier (If You Need More)

| Service | Cost | Benefits |
|---------|------|----------|
| Web Service (Starter) | $7/month each | No spin down, always online |
| PostgreSQL (Starter) | $7/month | 1 GB, no expiration |
| Redis (Starter) | $10/month | 100 MB |
| **Total** | **$31/month** | Good for small business |

---

## Security Best Practices

### 1. Use Strong Passwords

Generate a strong `SECRET_KEY`:
```bash
openssl rand -hex 32
```

### 2. Keep Secrets Secret

- Never commit `.env` files to GitHub
- Use Render's environment variables
- Use "Generate" button for sensitive values

### 3. Enable HTTPS Only

Render provides HTTPS by default - always use it!

### 4. Regular Updates

Keep dependencies updated:
```bash
# Backend
pip list --outdated

# Frontend
npm outdated
```

### 5. Monitor Logs

Check logs regularly for:
- Failed login attempts
- Errors
- Unusual activity

---

## Next Steps

### 1. Custom Domain (Optional)

Want `https://packoptima.yourcompany.com` instead of `.onrender.com`?

1. Buy a domain (Namecheap, GoDaddy, etc.)
2. In Render Dashboard → Service → Settings → Custom Domain
3. Add your domain
4. Update DNS records (Render provides instructions)

### 2. Set Up Monitoring

Use UptimeRobot (free) to:
- Ping your app every 5 minutes (keeps it awake)
- Get alerts if app goes down
- Track uptime

### 3. Backup Database

**Important**: Free database expires after 90 days!

**Set a reminder** to:
1. Export data before expiration
2. Create new database
3. Import data

Or upgrade to paid plan ($7/month) for no expiration.

### 4. Add More Features

Your app is live! Now you can:
- Add more users
- Customize branding
- Add more features
- Scale up as needed

---

## Summary

**What you did:**
1. ✅ Pushed code to GitHub
2. ✅ Created Render account
3. ✅ Deployed PostgreSQL database
4. ✅ Deployed Redis
5. ✅ Deployed backend API
6. ✅ Deployed frontend
7. ✅ Configured CORS
8. ✅ Tested deployment

**What you have:**
- **Public URL**: `https://packoptima-frontend.onrender.com`
- **Works from anywhere**: Internet access
- **Free hosting**: No cost
- **HTTPS included**: Secure

**Share with your friend:**
```
https://packoptima-frontend.onrender.com
```

**Your PackOptima is now live on the internet!** 🎉🚀

---

## Need Help?

### Render Documentation
- https://render.com/docs

### Render Community
- https://community.render.com

### PackOptima Issues
- Check logs in Render Dashboard
- Review this guide
- Test locally first with Docker

**Congratulations on deploying your app!** 🎊
