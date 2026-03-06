# PackOptima Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying PackOptima v2.0 to production environments. It covers database migrations, API server deployment, Celery worker deployment, and rollback procedures.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Database Migration](#database-migration)
4. [Redis Setup](#redis-setup)
5. [API Server Deployment](#api-server-deployment)
6. [Celery Worker Deployment](#celery-worker-deployment)
7. [Rolling Updates](#rolling-updates)
8. [Rollback Procedures](#rollback-procedures)
9. [Post-Deployment Validation](#post-deployment-validation)
10. [Monitoring Setup](#monitoring-setup)

---

## Prerequisites

### System Requirements

**API Servers:**
- CPU: 4+ cores
- RAM: 8GB+ per server
- OS: Ubuntu 20.04 LTS or later
- Python: 3.9+
- PostgreSQL: 13+
- Redis: 6+

**Celery Workers:**
- CPU: 2+ cores
- RAM: 4GB+ per worker
- OS: Ubuntu 20.04 LTS or later
- Python: 3.9+

### Software Dependencies

```bash
# System packages
sudo apt-get update
sudo apt-get install -y \
    python3.9 \
    python3.9-venv \
    python3-pip \
    postgresql-client \
    redis-tools \
    nginx \
    supervisor
```

### Network Requirements

- API servers accessible on port 8000 (or configured port)
- Redis accessible on port 6379
- PostgreSQL accessible on port 5432
- Load balancer configured for API servers
- Firewall rules configured

---

## Environment Configuration

### Environment Variables

Create environment-specific configuration files:

**`.env.production`**
```bash
# Database
DATABASE_URL=postgresql://user:password@db-host:5432/packoptima_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://redis-host:6379/0
CELERY_BROKER_URL=redis://redis-host:6379/1
CELERY_RESULT_BACKEND=redis://redis-host:6379/2

# API Configuration
API_SECRET_KEY=your-secret-key-min-32-chars-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=https://app.packoptima.ai,https://www.packoptima.ai

# Feature Flags
ENABLE_QUEUE_SYSTEM=true
ENABLE_BULK_UPLOAD=true
ENABLE_WEBHOOKS=true
ENABLE_WAREHOUSE_API=true

# Optimization Defaults
DEFAULT_COURIER_RATE=2.5
MAX_BULK_UPLOAD_SIZE_MB=10
MAX_BULK_UPLOAD_ROWS=10000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STANDARD_RPM=100
RATE_LIMIT_PREMIUM_RPM=500
RATE_LIMIT_ENTERPRISE_RPM=2000

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Workers
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_MAX_TASKS_PER_CHILD=1000
```

**`.env.staging`**
```bash
# Similar to production but with staging values
DATABASE_URL=postgresql://user:password@staging-db:5432/packoptima_staging
REDIS_URL=redis://staging-redis:6379/0
SENTRY_ENVIRONMENT=staging
LOG_LEVEL=DEBUG
```

### Configuration Management

**Using Environment Variables:**
```bash
# Load environment variables
export $(cat .env.production | xargs)

# Verify configuration
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

**Using Secrets Manager (AWS Secrets Manager example):**
```bash
# Retrieve secrets
aws secretsmanager get-secret-value \
    --secret-id packoptima/production/database \
    --query SecretString \
    --output text > /tmp/db_secret.json

# Parse and export
export DATABASE_URL=$(jq -r '.url' /tmp/db_secret.json)
```

---

## Database Migration

### Pre-Migration Checklist

- [ ] Backup production database
- [ ] Test migrations in staging environment
- [ ] Review migration scripts for data integrity
- [ ] Schedule maintenance window (if needed)
- [ ] Notify users of potential downtime
- [ ] Prepare rollback plan

### Backup Database

```bash
#!/bin/bash
# backup_database.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="packoptima_backup_${TIMESTAMP}.sql"

echo "Creating database backup: ${BACKUP_FILE}"

pg_dump \
    -h db-host \
    -U packoptima_user \
    -d packoptima_prod \
    -F c \
    -f "/backups/${BACKUP_FILE}"

# Verify backup
if [ $? -eq 0 ]; then
    echo "Backup created successfully"
    # Upload to S3 or backup storage
    aws s3 cp "/backups/${BACKUP_FILE}" "s3://packoptima-backups/${BACKUP_FILE}"
else
    echo "Backup failed!"
    exit 1
fi
```

### Run Migrations

```bash
#!/bin/bash
# deploy_migrations.sh

set -e  # Exit on error

echo "=== PackOptima Database Migration ==="
echo "Environment: ${ENVIRONMENT:-production}"
echo "Database: ${DATABASE_URL}"
echo ""

# 1. Backup database
echo "Step 1: Creating backup..."
./backup_database.sh

# 2. Check current migration version
echo "Step 2: Checking current migration version..."
cd backend
alembic current

# 3. Show pending migrations
echo "Step 3: Showing pending migrations..."
alembic history

# 4. Run migrations
echo "Step 4: Running migrations..."
alembic upgrade head

# 5. Verify migration success
if [ $? -eq 0 ]; then
    echo "✓ Migrations completed successfully"
    alembic current
else
    echo "✗ Migration failed!"
    echo "Rolling back..."
    alembic downgrade -1
    exit 1
fi

echo ""
echo "=== Migration Complete ==="
```

### Migration Verification

```bash
# Verify new tables exist
psql -h db-host -U packoptima_user -d packoptima_prod -c "\dt"

# Verify new columns
psql -h db-host -U packoptima_user -d packoptima_prod -c "\d products"
psql -h db-host -U packoptima_user -d packoptima_prod -c "\d boxes"

# Check data integrity
psql -h db-host -U packoptima_user -d packoptima_prod -c "
SELECT COUNT(*) as total_products,
       COUNT(CASE WHEN fragile IS NULL THEN 1 END) as null_fragile
FROM products;
"
```

### Rollback Migration

```bash
#!/bin/bash
# rollback_migration.sh

echo "=== Rolling Back Migration ==="

# Downgrade one version
cd backend
alembic downgrade -1

# Or downgrade to specific version
# alembic downgrade <revision_id>

# Verify rollback
alembic current

echo "=== Rollback Complete ==="
```

---

## Redis Setup

### Installation

```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
```

### Redis Configuration

**`/etc/redis/redis.conf`**
```conf
# Network
bind 0.0.0.0
port 6379
protected-mode yes
requirepass your-redis-password

# Memory
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Performance
tcp-backlog 511
timeout 0
tcp-keepalive 300
```

### Start Redis

```bash
# Start Redis service
sudo systemctl start redis-server

# Enable on boot
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli -a your-redis-password ping
# Expected output: PONG

# Check Redis info
redis-cli -a your-redis-password info
```

### Redis Monitoring

```bash
# Monitor Redis commands
redis-cli -a your-redis-password monitor

# Check memory usage
redis-cli -a your-redis-password info memory

# Check connected clients
redis-cli -a your-redis-password client list
```

---

## API Server Deployment

### Deployment Script

```bash
#!/bin/bash
# deploy_api.sh

set -e

echo "=== PackOptima API Server Deployment ==="

# Configuration
APP_DIR="/opt/packoptima"
VENV_DIR="${APP_DIR}/venv"
SERVICE_NAME="packoptima-api"
WORKERS=4
PORT=8000

# 1. Pull latest code
echo "Step 1: Pulling latest code..."
cd ${APP_DIR}
git pull origin main

# 2. Activate virtual environment
echo "Step 2: Activating virtual environment..."
source ${VENV_DIR}/bin/activate

# 3. Install dependencies
echo "Step 3: Installing dependencies..."
cd backend
pip install -r requirements.txt

# 4. Run database migrations
echo "Step 4: Running database migrations..."
alembic upgrade head

# 5. Collect static files (if applicable)
echo "Step 5: Preparing application..."
# Any pre-deployment tasks

# 6. Restart API service
echo "Step 6: Restarting API service..."
sudo systemctl restart ${SERVICE_NAME}

# 7. Wait for service to start
echo "Step 7: Waiting for service to start..."
sleep 5

# 8. Health check
echo "Step 8: Running health check..."
curl -f http://localhost:${PORT}/health || {
    echo "Health check failed!"
    sudo systemctl status ${SERVICE_NAME}
    exit 1
}

echo "✓ API server deployed successfully"
echo ""
echo "=== Deployment Complete ==="
```

### Systemd Service Configuration

**`/etc/systemd/system/packoptima-api.service`**
```ini
[Unit]
Description=PackOptima API Server
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=packoptima
Group=packoptima
WorkingDirectory=/opt/packoptima/backend
Environment="PATH=/opt/packoptima/venv/bin"
EnvironmentFile=/opt/packoptima/.env.production
ExecStart=/opt/packoptima/venv/bin/gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --graceful-timeout 30 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile /var/log/packoptima/access.log \
    --error-logfile /var/log/packoptima/error.log \
    --log-level info \
    app.main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration

**`/etc/nginx/sites-available/packoptima`**
```nginx
upstream packoptima_api {
    least_conn;
    server 10.0.1.10:8000 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8000 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.packoptima.ai;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.packoptima.ai;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.packoptima.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.packoptima.ai/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Logging
    access_log /var/log/nginx/packoptima_access.log;
    error_log /var/log/nginx/packoptima_error.log;
    
    # Client body size (for CSV uploads)
    client_max_body_size 10M;
    
    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;
    
    # Proxy to API servers
    location / {
        proxy_pass http://packoptima_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check endpoint (bypass proxy)
    location /health {
        proxy_pass http://packoptima_api/health;
        access_log off;
    }
}
```

---

## Celery Worker Deployment

### Deployment Script

```bash
#!/bin/bash
# deploy_workers.sh

set -e

echo "=== PackOptima Celery Worker Deployment ==="

# Configuration
APP_DIR="/opt/packoptima"
VENV_DIR="${APP_DIR}/venv"
SERVICE_NAME="packoptima-worker"
WORKERS=4

# 1. Pull latest code
echo "Step 1: Pulling latest code..."
cd ${APP_DIR}
git pull origin main

# 2. Activate virtual environment
echo "Step 2: Activating virtual environment..."
source ${VENV_DIR}/bin/activate

# 3. Install dependencies
echo "Step 3: Installing dependencies..."
cd backend
pip install -r requirements.txt

# 4. Restart worker service
echo "Step 4: Restarting worker service..."
sudo systemctl restart ${SERVICE_NAME}

# 5. Wait for workers to start
echo "Step 5: Waiting for workers to start..."
sleep 5

# 6. Verify workers are running
echo "Step 6: Verifying workers..."
celery -A app.core.celery_app inspect active || {
    echo "Worker verification failed!"
    sudo systemctl status ${SERVICE_NAME}
    exit 1
}

echo "✓ Celery workers deployed successfully"
echo ""
echo "=== Deployment Complete ==="
```

### Systemd Service Configuration

**`/etc/systemd/system/packoptima-worker.service`**
```ini
[Unit]
Description=PackOptima Celery Worker
After=network.target redis.service postgresql.service

[Service]
Type=forking
User=packoptima
Group=packoptima
WorkingDirectory=/opt/packoptima/backend
Environment="PATH=/opt/packoptima/venv/bin"
EnvironmentFile=/opt/packoptima/.env.production
ExecStart=/opt/packoptima/venv/bin/celery \
    -A app.core.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --time-limit=300 \
    --soft-time-limit=270 \
    --logfile=/var/log/packoptima/celery-worker.log \
    --pidfile=/var/run/packoptima/celery-worker.pid

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Supervisor Configuration (Alternative)

**`/etc/supervisor/conf.d/packoptima-worker.conf`**
```ini
[program:packoptima-worker]
command=/opt/packoptima/venv/bin/celery -A app.core.celery_app worker --loglevel=info --concurrency=4
directory=/opt/packoptima/backend
user=packoptima
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/packoptima/celery-worker.log
environment=PATH="/opt/packoptima/venv/bin"
```

### Flower Monitoring (Optional)

```bash
# Install Flower
pip install flower

# Start Flower
celery -A app.core.celery_app flower --port=5555

# Access at http://localhost:5555
```

---

## Rolling Updates

### Zero-Downtime Deployment

```bash
#!/bin/bash
# rolling_update.sh

set -e

echo "=== PackOptima Rolling Update ==="

# Configuration
SERVERS=("10.0.1.10" "10.0.1.11" "10.0.1.12")
HEALTH_CHECK_URL="http://localhost:8000/health"
HEALTH_CHECK_RETRIES=10
HEALTH_CHECK_DELAY=5

# Function to deploy to single server
deploy_to_server() {
    local server=$1
    echo "Deploying to ${server}..."
    
    # 1. Remove from load balancer
    echo "  Removing ${server} from load balancer..."
    # nginx: mark server as down
    # or use load balancer API
    
    # 2. Wait for connections to drain
    echo "  Waiting for connections to drain..."
    sleep 10
    
    # 3. Deploy to server
    echo "  Deploying application..."
    ssh packoptima@${server} "cd /opt/packoptima && ./deploy_api.sh"
    
    # 4. Health check
    echo "  Running health check..."
    for i in $(seq 1 ${HEALTH_CHECK_RETRIES}); do
        if ssh packoptima@${server} "curl -f ${HEALTH_CHECK_URL}"; then
            echo "  ✓ Health check passed"
            break
        fi
        
        if [ $i -eq ${HEALTH_CHECK_RETRIES} ]; then
            echo "  ✗ Health check failed after ${HEALTH_CHECK_RETRIES} attempts"
            return 1
        fi
        
        echo "  Retry $i/${HEALTH_CHECK_RETRIES}..."
        sleep ${HEALTH_CHECK_DELAY}
    done
    
    # 5. Add back to load balancer
    echo "  Adding ${server} back to load balancer..."
    # nginx: mark server as up
    # or use load balancer API
    
    echo "✓ Deployment to ${server} complete"
}

# Deploy to each server sequentially
for server in "${SERVERS[@]}"; do
    deploy_to_server ${server} || {
        echo "Deployment to ${server} failed!"
        echo "Stopping rolling update"
        exit 1
    }
    echo ""
done

echo "=== Rolling Update Complete ==="
```

---

## Rollback Procedures

### Quick Rollback

```bash
#!/bin/bash
# rollback.sh

set -e

echo "=== PackOptima Rollback ==="

# Configuration
PREVIOUS_VERSION="v1.9.0"
APP_DIR="/opt/packoptima"

# 1. Stop services
echo "Step 1: Stopping services..."
sudo systemctl stop packoptima-api
sudo systemctl stop packoptima-worker

# 2. Checkout previous version
echo "Step 2: Rolling back code to ${PREVIOUS_VERSION}..."
cd ${APP_DIR}
git checkout ${PREVIOUS_VERSION}

# 3. Rollback database migration
echo "Step 3: Rolling back database..."
cd backend
source ${APP_DIR}/venv/bin/activate
alembic downgrade -1

# 4. Restart services
echo "Step 4: Restarting services..."
sudo systemctl start packoptima-api
sudo systemctl start packoptima-worker

# 5. Health check
echo "Step 5: Running health check..."
sleep 5
curl -f http://localhost:8000/health || {
    echo "Health check failed!"
    exit 1
}

echo "✓ Rollback complete"
echo ""
echo "=== Rollback Complete ==="
```

### Feature Flag Rollback

```bash
# Disable new features without full rollback
export ENABLE_QUEUE_SYSTEM=false
export ENABLE_BULK_UPLOAD=false
export ENABLE_WEBHOOKS=false

# Restart services
sudo systemctl restart packoptima-api
sudo systemctl restart packoptima-worker
```

---

## Post-Deployment Validation

### Smoke Tests

```bash
#!/bin/bash
# smoke_tests.sh

echo "=== Running Smoke Tests ==="

API_URL="https://api.packoptima.ai"
TEST_USER_EMAIL="test@packoptima.ai"
TEST_USER_PASSWORD="test_password"

# 1. Health check
echo "Test 1: Health check..."
curl -f ${API_URL}/health || exit 1

# 2. Authentication
echo "Test 2: Authentication..."
TOKEN=$(curl -s -X POST ${API_URL}/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${TEST_USER_EMAIL}\",\"password\":\"${TEST_USER_PASSWORD}\"}" \
    | jq -r '.access_token')

if [ -z "$TOKEN" ]; then
    echo "Authentication failed!"
    exit 1
fi

# 3. List products
echo "Test 3: List products..."
curl -f -H "Authorization: Bearer ${TOKEN}" \
    ${API_URL}/products || exit 1

# 4. List boxes
echo "Test 4: List boxes..."
curl -f -H "Authorization: Bearer ${TOKEN}" \
    ${API_URL}/boxes || exit 1

# 5. Run optimization
echo "Test 5: Run optimization..."
curl -f -X POST -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    ${API_URL}/optimize \
    -d '{"product_ids":[1,2]}' || exit 1

echo "✓ All smoke tests passed"
```

### Performance Validation

```bash
# Run load test
cd backend/load_tests
locust -f locustfile.py --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --host https://api.packoptima.ai
```

---

## Monitoring Setup

See [MONITORING_SETUP_GUIDE.md](./MONITORING_SETUP_GUIDE.md) for detailed monitoring configuration.

### Quick Monitoring Checklist

- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards configured
- [ ] Sentry error tracking active
- [ ] Log aggregation configured
- [ ] Alerting rules configured
- [ ] On-call rotation configured

---

## Troubleshooting

### API Server Won't Start

```bash
# Check logs
sudo journalctl -u packoptima-api -n 100

# Check configuration
python -c "from app.core.config import settings; print(settings)"

# Check database connection
psql ${DATABASE_URL} -c "SELECT 1"

# Check Redis connection
redis-cli -u ${REDIS_URL} ping
```

### Celery Workers Not Processing Tasks

```bash
# Check worker status
celery -A app.core.celery_app inspect active

# Check Redis queue
redis-cli -u ${REDIS_URL} llen celery

# Check worker logs
sudo journalctl -u packoptima-worker -n 100

# Restart workers
sudo systemctl restart packoptima-worker
```

### Database Migration Failed

```bash
# Check migration status
alembic current

# Check migration history
alembic history

# Rollback migration
alembic downgrade -1

# Restore from backup
pg_restore -h db-host -U packoptima_user -d packoptima_prod /backups/backup.sql
```

---

## Support

For deployment support:
- Email: devops@packoptima.ai
- Slack: #packoptima-deployments
- On-call: +1 (555) 123-4567

---

## Changelog

### v2.0.0 (2024-01-15)
- Added Celery worker deployment
- Added Redis setup instructions
- Added rolling update procedure
- Added comprehensive rollback procedures

### v1.0.0 (2023-12-01)
- Initial deployment guide

---

© 2024 PackOptima. All rights reserved.
