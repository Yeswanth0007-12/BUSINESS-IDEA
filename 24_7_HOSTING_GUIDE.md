# 24/7 Hosting Guide for PackOptima

Complete guide for hosting your PackOptima platform 24/7 on various cloud providers.

---

## Table of Contents

1. [🆓 FREE Hosting Options](#-free-hosting-options)
2. [💰 PAID Hosting Options Overview](#hosting-options-overview)
3. [Option 1: DigitalOcean (Recommended for Beginners)](#option-1-digitalocean-recommended)
4. [Option 2: AWS (Amazon Web Services)](#option-2-aws)
5. [Option 3: Google Cloud Platform](#option-3-google-cloud-platform)
6. [Option 4: Azure](#option-4-azure)
7. [Option 5: Heroku (Easiest but More Expensive)](#option-5-heroku)
8. [Domain Setup](#domain-setup)
9. [SSL Certificate Setup](#ssl-certificate-setup)
10. [Automated Backups](#automated-backups)
11. [Cost Estimates](#cost-estimates)

---

## 🆓 FREE Hosting Options

### ⚠️ IMPORTANT: Understanding "Free" Hosting

**Free hosting has limitations:**
- Apps may sleep after inactivity (NOT true 24/7)
- Limited resources (RAM, CPU, storage)
- Slower performance
- Free credits run out quickly with 24/7 usage

**For TRUE 24/7 hosting with good performance, you need a PAID plan.**

---

### Option A: Render.com (FREE TIER)

**Best for:** Testing, demos, personal projects

#### Pros:
- ✅ Native Docker support
- ✅ Easy deployment (connect GitHub)
- ✅ Free SSL certificate
- ✅ Simple interface
- ✅ No credit card required for free tier

#### Cons:
- ❌ Apps sleep after 15 minutes of inactivity
- ❌ 30-60 second wake-up time
- ❌ Limited to 512MB RAM
- ❌ Slower performance
- ❌ NOT true 24/7 (sleeps when inactive)

#### Cost:
- **Free Tier:** $0/month (with sleep)
- **Paid Tier:** $7/month per service (no sleep, 512MB RAM)
- **For PackOptima:** ~$28/month (4 services: API, Frontend, DB, Redis)

#### Setup Steps:

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Deploy Database**
   - Click "New +" → "PostgreSQL"
   - Name: packoptima-db
   - Plan: Free (expires after 90 days) or Starter $7/month
   - Create Database

3. **Deploy Redis**
   - Click "New +" → "Redis"
   - Name: packoptima-redis
   - Plan: Free (25MB) or Starter $10/month
   - Create Redis

4. **Deploy Backend API**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     - **Name:** packoptima-api
     - **Environment:** Docker
     - **Dockerfile Path:** backend/Dockerfile
     - **Plan:** Free (sleeps) or Starter $7/month
   - Environment Variables:
     ```
     DATABASE_URL=<from-render-postgres>
     REDIS_URL=<from-render-redis>
     SECRET_KEY=<generate-random>
     JWT_SECRET_KEY=<generate-random>
     ```
   - Deploy

5. **Deploy Frontend**
   - Click "New +" → "Static Site"
   - Connect your GitHub repository
   - Settings:
     - **Name:** packoptima-frontend
     - **Build Command:** cd frontend && npm install && npm run build
     - **Publish Directory:** frontend/dist
   - Environment Variables:
     ```
     VITE_API_URL=https://packoptima-api.onrender.com
     ```
   - Deploy

#### Limitations:
- **Free tier apps sleep after 15 minutes** of no activity
- First request after sleep takes 30-60 seconds to wake up
- **NOT suitable for production** if you need instant response
- Good for demos and testing only

---

### Option B: Railway.app (FREE $5 CREDIT)

**Best for:** Development, testing

#### Pros:
- ✅ Native Docker support
- ✅ Very easy deployment
- ✅ Good performance
- ✅ No sleep (while credit lasts)

#### Cons:
- ❌ $5 free credit runs out in ~1 week with 24/7 usage
- ❌ After credit: ~$10-20/month
- ❌ Requires credit card

#### Cost:
- **Free:** $5 credit (runs out quickly)
- **After credit:** Pay-as-you-go (~$10-20/month)

#### Setup Steps:

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub
   - Add credit card (required)

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Add Services**
   - Add PostgreSQL database
   - Add Redis
   - Add your application

4. **Configure Environment**
   - Railway auto-detects Docker
   - Add environment variables
   - Deploy

#### Note:
- $5 credit = ~150 hours of runtime
- With 4 services running 24/7: credit lasts ~1.5 days
- **You'll need to pay after free credit runs out**

---

### Option C: Fly.io (FREE TIER)

**Best for:** Small apps, testing

#### Pros:
- ✅ Native Docker support
- ✅ True 24/7 (no sleep)
- ✅ Good performance
- ✅ Free tier includes 3 VMs

#### Cons:
- ❌ Very limited RAM (256MB per VM)
- ❌ Limited to 3 VMs total
- ❌ Requires credit card
- ❌ Complex setup

#### Cost:
- **Free Tier:** 3 shared-cpu VMs (256MB RAM each)
- **Paid:** $1.94/month per 256MB RAM

#### Setup Steps:

1. **Install Fly CLI**
   ```bash
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Deploy Application**
   ```bash
   cd /path/to/packoptima
   fly launch
   ```

4. **Add Database**
   ```bash
   fly postgres create
   ```

5. **Add Redis**
   ```bash
   fly redis create
   ```

#### Limitations:
- 256MB RAM is very limited for PackOptima
- May need to upgrade to paid tier
- Free tier good for testing only

---

### Option D: Docker on Your Own Computer (FREE but NOT 24/7)

**Best for:** Local development only

#### Pros:
- ✅ Completely free
- ✅ Full control
- ✅ Fast performance

#### Cons:
- ❌ NOT 24/7 (only when your computer is on)
- ❌ No public access (only localhost)
- ❌ No SSL certificate
- ❌ Not suitable for production

#### Setup:
```bash
# Just run locally
docker-compose up -d
```

Access at: http://localhost:3000

**This is NOT hosting** - it's only for development.

---

### 🎯 FREE HOSTING RECOMMENDATION

**For Testing/Demos:**
- Use **Render.com Free Tier**
- Accept that apps will sleep
- Good for showing to clients/investors

**For Real 24/7 Hosting:**
- **You MUST pay** for a hosting plan
- Minimum: $7-10/month (Render Starter)
- Recommended: $24-48/month (DigitalOcean)

**Why Free Doesn't Work for 24/7:**
1. Apps sleep after inactivity
2. Very limited resources
3. Slow performance
4. Not reliable for production

---

### 💡 BEST VALUE: Render.com Paid Plan

If you want cheap 24/7 hosting:

**Render.com Starter Plan:**
- **Cost:** $7/month per service
- **Total for PackOptima:** ~$28/month (4 services)
- **Includes:**
  - No sleep
  - 512MB RAM per service
  - Free SSL
  - Automatic deployments
  - Better than free tier

**Setup:**
1. Follow Render.com free tier steps above
2. Upgrade each service to "Starter" plan
3. Your app runs 24/7 without sleeping

---

## Hosting Options Overview

### Quick Comparison

| Provider | Difficulty | Monthly Cost | True 24/7 | Best For |
|----------|-----------|--------------|-----------|----------|
| **Render Free** | Very Easy | $0 | ❌ (sleeps) | Testing/Demos |
| **Render Paid** | Very Easy | $28 | ✅ | Budget 24/7 |
| **Railway** | Very Easy | $10-20 | ✅ | Development |
| **Fly.io Free** | Medium | $0 | ✅ | Testing (limited) |
| **DigitalOcean** | Easy | $24-48 | ✅ | Production (Recommended) |
| **AWS** | Medium | $30-60 | ✅ | Scalability, Enterprise |
| **Google Cloud** | Medium | $30-60 | ✅ | AI/ML features |
| **Azure** | Medium | $30-60 | ✅ | Microsoft ecosystem |
| **Heroku** | Very Easy | $50-100 | ✅ | Quick deployment |

### What You Need

- **Server (VPS):** To run Docker containers
- **Database:** PostgreSQL (can be on same server or managed)
- **Domain Name:** yourcompany.com ($10-15/year)
- **SSL Certificate:** Free with Let's Encrypt
- **Backup Storage:** For database backups

---

## Option 1: DigitalOcean (Recommended)

**Why DigitalOcean?**
- Simple interface
- Good documentation
- Affordable pricing
- Docker-friendly
- Great for beginners

### Step-by-Step Setup

#### 1. Create DigitalOcean Account

1. Go to https://www.digitalocean.com
2. Sign up for an account
3. Add payment method
4. Get $200 free credit (60 days) for new users

#### 2. Create a Droplet (Server)

1. Click "Create" → "Droplets"
2. Choose configuration:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic
   - **CPU Options:** Regular (Disk type: SSD)
   - **Size:** $24/month (2 GB RAM, 1 CPU, 50 GB SSD)
     - For production: $48/month (4 GB RAM, 2 CPUs, 80 GB SSD)
   - **Datacenter:** Choose closest to your users
   - **Authentication:** SSH Key (recommended) or Password
   - **Hostname:** packoptima-production

3. Click "Create Droplet"
4. Wait 1-2 minutes for creation
5. Note your server IP address (e.g., 123.45.67.89)

#### 3. Connect to Your Server

**Windows (PowerShell):**
```powershell
ssh root@YOUR_SERVER_IP
```

**Mac/Linux:**
```bash
ssh root@YOUR_SERVER_IP
```

#### 4. Install Docker on Server

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

#### 5. Upload Your Application

**Option A: Using Git (Recommended)**

```bash
# On server
cd /opt
git clone https://github.com/yourusername/packoptima.git
cd packoptima
```

**Option B: Using SCP (from your local machine)**

```bash
# From your local machine
scp -r /path/to/packoptima root@YOUR_SERVER_IP:/opt/
```

#### 6. Configure Environment

```bash
# On server
cd /opt/packoptima

# Create production environment file
cp backend/.env.example backend/.env.production

# Edit environment file
nano backend/.env.production
```

Update these critical values:
```bash
# Database
DATABASE_URL=postgresql://packoptima:STRONG_PASSWORD@localhost:5432/packoptima

# Security
SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Domain (update after domain setup)
CORS_ORIGINS=https://yourdomain.com

# Redis
REDIS_URL=redis://localhost:6379/0
```

Generate secure keys:
```bash
openssl rand -hex 32
```

#### 7. Deploy Application

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 8. Set Up Firewall

```bash
# Install UFW
apt install ufw -y

# Allow SSH
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

#### 9. Set Up Nginx Reverse Proxy

```bash
# Install Nginx
apt install nginx -y

# Create configuration
nano /etc/nginx/sites-available/packoptima
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
# Create symbolic link
ln -s /etc/nginx/sites-available/packoptima /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

#### 10. Set Up SSL Certificate (Free)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose redirect HTTP to HTTPS (option 2)

# Test auto-renewal
certbot renew --dry-run
```

#### 11. Set Up Automatic Backups

Create backup script:
```bash
nano /opt/backup-packoptima.sh
```

Add this content:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
docker exec packoptima-db pg_dump -U postgres packoptima > $BACKUP_DIR/db_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable and schedule:
```bash
chmod +x /opt/backup-packoptima.sh

# Add to crontab (daily at 2 AM)
crontab -e

# Add this line:
0 2 * * * /opt/backup-packoptima.sh >> /var/log/packoptima-backup.log 2>&1
```

#### 12. Set Up Monitoring

```bash
# Start monitoring stack
cd /opt/packoptima/monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana at: http://YOUR_SERVER_IP:3001
# Default login: admin/admin
```

#### 13. Enable Auto-Restart on Reboot

```bash
# Edit docker-compose.yml to add restart policy
nano docker-compose.yml
```

Add to each service:
```yaml
services:
  api:
    restart: unless-stopped
    # ... rest of config

  db:
    restart: unless-stopped
    # ... rest of config

  redis:
    restart: unless-stopped
    # ... rest of config

  worker:
    restart: unless-stopped
    # ... rest of config
```

Restart services:
```bash
docker-compose down
docker-compose up -d
```

---

## Option 2: AWS

### Quick Setup with AWS

#### 1. Create AWS Account
- Go to https://aws.amazon.com
- Sign up (12 months free tier)

#### 2. Launch EC2 Instance

1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Choose:
   - **Name:** packoptima-production
   - **AMI:** Ubuntu Server 22.04 LTS
   - **Instance Type:** t3.medium (2 vCPU, 4 GB RAM)
   - **Key Pair:** Create new or use existing
   - **Security Group:** Allow ports 22, 80, 443
4. Launch instance

#### 3. Connect and Deploy

```bash
# Connect to instance
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Follow same steps as DigitalOcean from step 4 onwards
```

#### 4. Use RDS for Database (Optional but Recommended)

1. Go to RDS Dashboard
2. Create PostgreSQL database
3. Choose:
   - **Engine:** PostgreSQL 15
   - **Template:** Free tier (or Production)
   - **DB Instance:** db.t3.micro (free tier)
4. Update DATABASE_URL in .env.production

#### 5. Use ElastiCache for Redis (Optional)

1. Go to ElastiCache Dashboard
2. Create Redis cluster
3. Update REDIS_URL in .env.production

---

## Option 3: Google Cloud Platform

### Quick Setup with GCP

#### 1. Create GCP Account
- Go to https://cloud.google.com
- Sign up ($300 free credit)

#### 2. Create VM Instance

1. Go to Compute Engine → VM Instances
2. Click "Create Instance"
3. Choose:
   - **Name:** packoptima-production
   - **Region:** Choose closest to users
   - **Machine Type:** e2-medium (2 vCPU, 4 GB RAM)
   - **Boot Disk:** Ubuntu 22.04 LTS, 50 GB
   - **Firewall:** Allow HTTP and HTTPS traffic
4. Create instance

#### 3. Connect and Deploy

```bash
# Use GCP Console SSH or:
gcloud compute ssh packoptima-production

# Follow same steps as DigitalOcean from step 4 onwards
```

---

## Option 4: Azure

### Quick Setup with Azure

#### 1. Create Azure Account
- Go to https://azure.microsoft.com
- Sign up ($200 free credit)

#### 2. Create Virtual Machine

1. Go to Virtual Machines
2. Click "Create"
3. Choose:
   - **Name:** packoptima-production
   - **Image:** Ubuntu Server 22.04 LTS
   - **Size:** Standard_B2s (2 vCPU, 4 GB RAM)
   - **Authentication:** SSH public key
4. Create VM

#### 3. Connect and Deploy

```bash
# Connect to VM
ssh azureuser@YOUR_VM_IP

# Follow same steps as DigitalOcean from step 4 onwards
```

---

## Option 5: Heroku

### Easiest but More Expensive

#### 1. Install Heroku CLI

```bash
# Windows
winget install Heroku.HerokuCLI

# Mac
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2. Login and Create App

```bash
heroku login
heroku create packoptima-production
```

#### 3. Add Addons

```bash
# PostgreSQL
heroku addons:create heroku-postgresql:mini

# Redis
heroku addons:create heroku-redis:mini
```

#### 4. Deploy

```bash
# Add Heroku remote
heroku git:remote -a packoptima-production

# Deploy
git push heroku main
```

**Note:** Heroku requires specific configuration. See Heroku documentation for Docker deployment.

---

## Domain Setup

### 1. Buy a Domain

Popular registrars:
- **Namecheap:** https://www.namecheap.com ($8-12/year)
- **GoDaddy:** https://www.godaddy.com ($10-15/year)
- **Google Domains:** https://domains.google ($12/year)

### 2. Configure DNS

Add these DNS records:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | YOUR_SERVER_IP | 3600 |
| A | www | YOUR_SERVER_IP | 3600 |
| CNAME | api | yourdomain.com | 3600 |

### 3. Wait for Propagation

DNS changes take 1-48 hours to propagate globally.

Check status:
```bash
nslookup yourdomain.com
```

---

## SSL Certificate Setup

### Using Let's Encrypt (Free)

Already covered in DigitalOcean setup above. For other providers:

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is set up automatically
```

### Using Cloudflare (Free + CDN)

1. Sign up at https://www.cloudflare.com
2. Add your domain
3. Update nameservers at your registrar
4. Enable "Full (strict)" SSL mode
5. Cloudflare provides free SSL automatically

---

## Automated Backups

### Database Backups

Already covered in DigitalOcean setup. Additional options:

#### Upload to Cloud Storage

**DigitalOcean Spaces:**
```bash
# Install s3cmd
apt install s3cmd -y

# Configure
s3cmd --configure

# Modify backup script to upload
s3cmd put $BACKUP_DIR/db_$DATE.sql.gz s3://your-bucket/backups/
```

**AWS S3:**
```bash
# Install AWS CLI
apt install awscli -y

# Configure
aws configure

# Upload
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://your-bucket/backups/
```

---

## Cost Estimates

### Monthly Costs Breakdown

#### Small Business (< 100 users)

**DigitalOcean:**
- Droplet (2 GB RAM): $24/month
- Backups: $5/month
- Domain: $1/month (amortized)
- **Total: ~$30/month**

**AWS:**
- EC2 t3.medium: $30/month
- RDS db.t3.micro: $15/month
- Data transfer: $5/month
- **Total: ~$50/month**

#### Medium Business (100-1000 users)

**DigitalOcean:**
- Droplet (4 GB RAM): $48/month
- Managed Database: $15/month
- Backups: $10/month
- **Total: ~$73/month**

**AWS:**
- EC2 t3.large: $60/month
- RDS db.t3.small: $30/month
- ElastiCache: $15/month
- Data transfer: $10/month
- **Total: ~$115/month**

#### Large Business (1000+ users)

**AWS/GCP/Azure:**
- Multiple servers: $200-500/month
- Managed databases: $100-200/month
- Load balancer: $20/month
- CDN: $50/month
- **Total: ~$370-770/month**

---

## Maintenance Checklist

### Daily
- [ ] Check application logs
- [ ] Monitor error rates in Grafana
- [ ] Verify backups completed

### Weekly
- [ ] Review performance metrics
- [ ] Check disk space usage
- [ ] Update dependencies if needed

### Monthly
- [ ] Review and optimize costs
- [ ] Test backup restoration
- [ ] Update SSL certificates (auto-renewed)
- [ ] Security updates

---

## Quick Start Commands

### Start Application
```bash
cd /opt/packoptima
docker-compose up -d
```

### Stop Application
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### Restart Application
```bash
docker-compose restart
```

### Update Application
```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check memory
free -h

# Restart Docker
systemctl restart docker
```

### Can't Access Website

```bash
# Check Nginx
systemctl status nginx
nginx -t

# Check firewall
ufw status

# Check DNS
nslookup yourdomain.com
```

### Database Issues

```bash
# Check database container
docker-compose logs db

# Connect to database
docker exec -it packoptima-db psql -U postgres -d packoptima

# Check connections
SELECT count(*) FROM pg_stat_activity;
```

---

## Support Resources

### DigitalOcean
- Documentation: https://docs.digitalocean.com
- Community: https://www.digitalocean.com/community
- Support: https://www.digitalocean.com/support

### AWS
- Documentation: https://docs.aws.amazon.com
- Forums: https://forums.aws.amazon.com
- Support: https://aws.amazon.com/support

### General
- Docker: https://docs.docker.com
- Nginx: https://nginx.org/en/docs
- Let's Encrypt: https://letsencrypt.org/docs

---

## Recommended: DigitalOcean Setup

For most users, I recommend starting with **DigitalOcean** because:

1. **Simple:** Easy-to-use interface
2. **Affordable:** $24-48/month for small-medium business
3. **Reliable:** 99.99% uptime SLA
4. **Scalable:** Easy to upgrade as you grow
5. **Support:** Great documentation and community

### Quick Start with DigitalOcean

1. Create account → Get $200 credit
2. Create Droplet ($24/month, 2 GB RAM)
3. Follow steps 3-13 in Option 1 above
4. Your app will be live 24/7!

**Total Time:** 1-2 hours  
**Monthly Cost:** $30-50  
**Difficulty:** Easy

---

## Next Steps

1. ✅ Choose your hosting provider
2. ✅ Create server/instance
3. ✅ Follow deployment steps
4. ✅ Set up domain and SSL
5. ✅ Configure backups
6. ✅ Set up monitoring
7. ✅ Test everything
8. ✅ Go live!

**Your PackOptima platform will be running 24/7!** 🚀
