# PackOptima AI - Deployment Guide

## Single Host Deployment with Docker

This guide will help you deploy the entire PackOptima AI application (backend + frontend + database) on a single host using Docker.

---

## Prerequisites

Before deploying, ensure you have:

1. **Docker** installed (version 20.10 or higher)
   - Download from: https://docs.docker.com/get-docker/
   
2. **Docker Compose** installed (version 2.0 or higher)
   - Usually comes with Docker Desktop
   - Or install separately: https://docs.docker.com/compose/install/

3. **Minimum System Requirements**:
   - 2 CPU cores
   - 4 GB RAM
   - 10 GB disk space
   - Linux, macOS, or Windows with WSL2

---

## Quick Start (Automated Deployment)

### Option 1: Using the Deployment Script (Recommended)

1. **Make the script executable** (Linux/macOS):
   ```bash
   chmod +x deploy.sh
   ```

2. **Run the deployment script**:
   ```bash
   ./deploy.sh
   ```

   On Windows (Git Bash or WSL):
   ```bash
   bash deploy.sh
   ```

3. **Wait for deployment to complete** (2-5 minutes)

4. **Access the application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Manual Deployment

1. **Build and start all services**:
   ```bash
   docker-compose up -d --build
   ```

2. **Check service status**:
   ```bash
   docker-compose ps
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f
   ```

---

## Configuration

### Environment Variables

Before deploying to production, update these values in `docker-compose.yml`:

#### Database Configuration
```yaml
POSTGRES_PASSWORD: your-secure-password-here
```

#### Backend Configuration
```yaml
DATABASE_URL: postgresql://packoptima_user:your-secure-password-here@database:5432/packoptima_db
SECRET_KEY: your-super-secret-key-minimum-32-characters-long
ALLOWED_ORIGINS: http://your-domain.com,https://your-domain.com
```

### Security Checklist

- [ ] Change database password
- [ ] Change SECRET_KEY (minimum 32 characters)
- [ ] Update ALLOWED_ORIGINS with your domain
- [ ] Enable HTTPS (see SSL/TLS section below)
- [ ] Set up firewall rules
- [ ] Configure backup strategy

---

## Service Management

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database
```

### Check Service Status
```bash
docker-compose ps
```

### Access Database
```bash
docker-compose exec database psql -U packoptima_user -d packoptima_db
```

---

## Accessing the Application

Once deployed, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost | Main application UI |
| Backend API | http://localhost:8000 | REST API |
| API Docs (Swagger) | http://localhost:8000/docs | Interactive API documentation |
| API Docs (ReDoc) | http://localhost:8000/redoc | Alternative API documentation |
| Database | localhost:5432 | PostgreSQL database |

---

## First Time Setup

### 1. Register a User

1. Open http://localhost in your browser
2. Click "Register here"
3. Fill in:
   - Email: your@email.com
   - Password: (minimum 6 characters)
   - Company Name: Your Company
4. Click "Register"

### 2. Add Products

1. Navigate to "Products" page
2. Click "Add Product"
3. Fill in product details
4. Click "Create"

### 3. Add Boxes

1. Navigate to "Boxes" page
2. Click "Add Box"
3. Fill in box dimensions and cost
4. Click "Create"

### 4. Run Optimization

1. Navigate to "Optimize" page
2. Click "Run Optimization"
3. View results and savings

---

## Production Deployment

### Using a Custom Domain

1. **Update docker-compose.yml**:
   ```yaml
   environment:
     ALLOWED_ORIGINS: https://your-domain.com
   ```

2. **Set up reverse proxy** (nginx or Caddy):
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:80;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
       }
   }
   ```

3. **Restart services**:
   ```bash
   docker-compose restart
   ```

### SSL/TLS Configuration

#### Option 1: Using Let's Encrypt (Recommended)

1. **Install Certbot**:
   ```bash
   sudo apt-get install certbot
   ```

2. **Get certificate**:
   ```bash
   sudo certbot certonly --standalone -d your-domain.com
   ```

3. **Configure nginx** (see above)

#### Option 2: Using Cloudflare

1. Point your domain to your server IP
2. Enable Cloudflare proxy
3. SSL/TLS will be handled by Cloudflare

---

## Backup and Restore

### Backup Database

```bash
# Create backup
docker-compose exec database pg_dump -U packoptima_user packoptima_db > backup_$(date +%Y%m%d).sql

# Or use docker-compose
docker-compose exec -T database pg_dump -U packoptima_user packoptima_db > backup.sql
```

### Restore Database

```bash
# Restore from backup
docker-compose exec -T database psql -U packoptima_user packoptima_db < backup.sql
```

### Automated Backups

Create a cron job for daily backups:

```bash
# Edit crontab
crontab -e

# Add this line for daily backup at 2 AM
0 2 * * * cd /path/to/packoptima && docker-compose exec -T database pg_dump -U packoptima_user packoptima_db > backups/backup_$(date +\%Y\%m\%d).sql
```

---

## Monitoring

### View Resource Usage

```bash
docker stats
```

### Check Disk Usage

```bash
docker system df
```

### View Container Logs

```bash
# Real-time logs
docker-compose logs -f --tail=100

# Last 100 lines
docker-compose logs --tail=100
```

---

## Troubleshooting

### Services Won't Start

1. **Check if ports are already in use**:
   ```bash
   # Check port 80
   sudo lsof -i :80
   
   # Check port 8000
   sudo lsof -i :8000
   
   # Check port 5432
   sudo lsof -i :5432
   ```

2. **View detailed logs**:
   ```bash
   docker-compose logs
   ```

3. **Rebuild containers**:
   ```bash
   docker-compose down
   docker-compose up -d --build --force-recreate
   ```

### Database Connection Issues

1. **Check database is running**:
   ```bash
   docker-compose ps database
   ```

2. **Check database logs**:
   ```bash
   docker-compose logs database
   ```

3. **Test database connection**:
   ```bash
   docker-compose exec database psql -U packoptima_user -d packoptima_db -c "SELECT 1;"
   ```

### Frontend Not Loading

1. **Check frontend logs**:
   ```bash
   docker-compose logs frontend
   ```

2. **Rebuild frontend**:
   ```bash
   docker-compose up -d --build frontend
   ```

3. **Check nginx configuration**:
   ```bash
   docker-compose exec frontend nginx -t
   ```

### Backend API Errors

1. **Check backend logs**:
   ```bash
   docker-compose logs backend
   ```

2. **Check database migrations**:
   ```bash
   docker-compose exec backend alembic current
   ```

3. **Run migrations manually**:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

---

## Updating the Application

### Update Code

1. **Pull latest changes**:
   ```bash
   git pull origin main
   ```

2. **Rebuild and restart**:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### Update Dependencies

1. **Backend dependencies**:
   - Update `backend/requirements.txt`
   - Rebuild: `docker-compose up -d --build backend`

2. **Frontend dependencies**:
   - Update `frontend/package.json`
   - Rebuild: `docker-compose up -d --build frontend`

---

## Scaling

### Increase Resources

Edit `docker-compose.yml` to add resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Multiple Backend Instances

Use a load balancer (nginx) to distribute traffic across multiple backend containers.

---

## Uninstalling

### Remove All Services and Data

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: This deletes all data!)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

### Remove Only Containers (Keep Data)

```bash
docker-compose down
```

---

## Support

### Logs Location

- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`
- Database logs: `docker-compose logs database`

### Common Issues

1. **Port already in use**: Change ports in `docker-compose.yml`
2. **Out of memory**: Increase Docker memory limit
3. **Disk space**: Clean up with `docker system prune`

### Getting Help

- Check logs: `docker-compose logs`
- Check status: `docker-compose ps`
- Restart services: `docker-compose restart`

---

## Performance Optimization

### Database Optimization

1. **Increase shared_buffers**:
   ```yaml
   database:
     command: postgres -c shared_buffers=256MB -c max_connections=200
   ```

2. **Enable connection pooling** in backend

### Frontend Optimization

- Already configured with:
  - Gzip compression
  - Static asset caching
  - Minified builds

### Backend Optimization

- Use production ASGI server (already using uvicorn)
- Enable response caching
- Use CDN for static assets

---

## Security Best Practices

1. ✅ Change all default passwords
2. ✅ Use strong SECRET_KEY (32+ characters)
3. ✅ Enable HTTPS in production
4. ✅ Set up firewall rules
5. ✅ Regular security updates
6. ✅ Monitor logs for suspicious activity
7. ✅ Regular database backups
8. ✅ Use environment variables for secrets
9. ✅ Limit database access
10. ✅ Enable rate limiting (already configured)

---

## Next Steps

After successful deployment:

1. ✅ Test all features
2. ✅ Set up monitoring
3. ✅ Configure backups
4. ✅ Set up SSL/TLS
5. ✅ Configure domain
6. ✅ Set up logging
7. ✅ Performance testing
8. ✅ Security audit

---

## Conclusion

Your PackOptima AI application is now deployed and running! 🎉

Access it at: **http://localhost**

For production deployment, remember to:
- Change all default passwords
- Enable HTTPS
- Set up backups
- Configure monitoring
