# Staging Deployment Guide

This guide provides step-by-step instructions for deploying PackOptima to the staging environment.

## Overview

The staging deployment process includes:
1. Pre-deployment preparation
2. Database migration
3. API server deployment
4. Celery worker deployment
5. Smoke testing
6. Integration testing
7. Monitoring verification
8. Rollback testing
9. Post-deployment validation

**Estimated Time:** 30-45 minutes

## Prerequisites

### Required Tools
- Git
- Python 3.9+
- PostgreSQL client tools (psql, pg_dump)
- Redis client (redis-cli)
- Celery
- curl
- bash

### Required Access
- SSH access to staging servers
- Database credentials
- Redis credentials
- Git repository access
- Monitoring dashboard access

### Environment Files
- `.env.staging` configured with staging credentials
- All secrets and API keys generated
- CORS origins configured

## Quick Start

### Option 1: Automated Deployment (Recommended)

Run the automated staging deployment script:

```bash
# Navigate to project root
cd /path/to/packoptima

# Run staging deployment
bash scripts/deploy_staging.sh
```

The script will:
- Perform pre-deployment checks
- Deploy all components
- Run all tests
- Verify monitoring
- Generate deployment report

### Option 2: Manual Deployment

If you prefer manual control, follow these steps:

#### Step 1: Pre-Deployment Checks

```bash
# Check database connectivity
psql $DATABASE_URL -c "SELECT 1"

# Check Redis connectivity
redis-cli -u $REDIS_URL ping

# Check monitoring
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health  # Grafana
```

#### Step 2: Deploy Database Migrations

```bash
# Run migration script
bash scripts/deploy_migrations.sh staging
```

This will:
- Create database backup
- Run migrations
- Verify migration success
- Provide rollback capability

#### Step 3: Deploy API Server

```bash
# Run API deployment script
bash scripts/deploy_api.sh staging
```

This will:
- Pull latest code
- Install dependencies
- Restart API service
- Run health checks
- Verify deployment

#### Step 4: Deploy Celery Workers

```bash
# Run worker deployment script
bash scripts/deploy_workers.sh staging
```

This will:
- Gracefully stop workers
- Deploy new code
- Restart workers
- Verify task processing

#### Step 5: Run Smoke Tests

```bash
# Navigate to backend
cd backend

# Run smoke tests
bash smoke_tests/run_smoke_tests.sh

# Or run with pytest
python -m pytest smoke_tests/test_smoke.py -v
```

#### Step 6: Run Integration Tests

```bash
# Run integration tests
python -m pytest tests/test_integration_workflows.py -v
python -m pytest tests/test_end_to_end_workflows.py -v
```

#### Step 7: Verify Monitoring

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check metrics endpoint
curl http://localhost:8000/metrics

# Access Grafana dashboards
open http://localhost:3000
```

#### Step 8: Validate Deployment

```bash
# Check API health
curl http://localhost:8000/health

# Check worker status
celery -A app.core.celery_app inspect active

# Check queue depth
redis-cli -u $REDIS_URL llen celery
```

## Detailed Deployment Steps

### 1. Environment Preparation

#### Create Staging Environment File

```bash
# Copy example file
cp backend/.env.staging.example backend/.env.staging

# Edit with staging credentials
nano backend/.env.staging
```

#### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@staging-db:5432/packoptima_staging

# Redis
REDIS_URL=redis://:pass@staging-redis:6379/0
CELERY_BROKER_URL=redis://:pass@staging-redis:6379/1
CELERY_RESULT_BACKEND=redis://:pass@staging-redis:6379/2

# Security
API_SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Application
ENVIRONMENT=staging
DEBUG=false

# Feature Flags
ENABLE_QUEUE_SYSTEM=true
ENABLE_BULK_UPLOAD=true
ENABLE_WEBHOOKS=true
ENABLE_WAREHOUSE_API=true
```

#### Generate Secrets

```bash
# Generate API secret key
openssl rand -hex 32

# Generate JWT secret key
openssl rand -hex 32
```

### 2. Database Migration

#### Backup Database

```bash
# Manual backup
pg_dump $DATABASE_URL -F c -f backup_$(date +%Y%m%d_%H%M%S).dump

# Compress backup
gzip backup_*.dump
```

#### Review Migrations

```bash
cd backend

# Check current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic upgrade head --sql > pending_migrations.sql
cat pending_migrations.sql
```

#### Run Migrations

```bash
# Run migrations
alembic upgrade head

# Verify migration
alembic current
```

#### Rollback (if needed)

```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision>
```

### 3. API Server Deployment

#### Pull Latest Code

```bash
cd /opt/packoptima
git fetch origin
git pull origin main
```

#### Install Dependencies

```bash
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Restart Service

```bash
# Using systemd
sudo systemctl restart packoptima-api

# Check status
sudo systemctl status packoptima-api

# View logs
sudo journalctl -u packoptima-api -f
```

#### Verify Health

```bash
# Health check
curl http://localhost:8000/health

# Check endpoints
curl http://localhost:8000/docs
```

### 4. Celery Worker Deployment

#### Stop Workers Gracefully

```bash
# Send TERM signal
sudo systemctl stop packoptima-worker

# Wait for tasks to finish (30 seconds)
sleep 30
```

#### Deploy Code

```bash
cd /opt/packoptima
git pull origin main

cd backend
source venv/bin/activate
pip install -r requirements.txt
```

#### Restart Workers

```bash
# Start workers
sudo systemctl start packoptima-worker

# Check status
sudo systemctl status packoptima-worker

# View logs
sudo journalctl -u packoptima-worker -f
```

#### Verify Workers

```bash
cd backend
source venv/bin/activate

# Check active workers
celery -A app.core.celery_app inspect active

# Check worker stats
celery -A app.core.celery_app inspect stats

# Ping workers
celery -A app.core.celery_app inspect ping
```

### 5. Testing

#### Smoke Tests

```bash
cd backend

# Run all smoke tests
python -m pytest smoke_tests/ -v

# Run specific test
python -m pytest smoke_tests/test_smoke.py::test_database_connection -v
```

#### Integration Tests

```bash
# Run integration tests
python -m pytest tests/test_integration_workflows.py -v --tb=short

# Run end-to-end tests
python -m pytest tests/test_end_to_end_workflows.py -v --tb=short
```

#### Manual Testing

```bash
# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Test product creation (with auth token)
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "sku": "TEST-001",
    "length_cm": 10,
    "width_cm": 10,
    "height_cm": 10,
    "weight_kg": 1.0
  }'
```

### 6. Monitoring Verification

#### Check Prometheus

```bash
# Check Prometheus health
curl http://localhost:9090/-/healthy

# Check targets
curl http://localhost:9090/api/v1/targets | jq

# Query metrics
curl 'http://localhost:9090/api/v1/query?query=up' | jq
```

#### Check Grafana

```bash
# Check Grafana health
curl http://localhost:3000/api/health

# Access dashboards
open http://localhost:3000/d/api-performance
open http://localhost:3000/d/queue-metrics
open http://localhost:3000/d/database-metrics
```

#### Check AlertManager

```bash
# Check AlertManager health
curl http://localhost:9093/-/healthy

# Check alerts
curl http://localhost:9093/api/v1/alerts | jq
```

#### Verify Metrics Collection

```bash
# Check metrics endpoint
curl http://localhost:8000/metrics

# Verify key metrics
curl http://localhost:8000/metrics | grep http_requests_total
curl http://localhost:8000/metrics | grep celery_tasks_total
curl http://localhost:8000/metrics | grep db_connections
```

### 7. Rollback Procedures

#### Database Rollback

```bash
# Rollback migration
bash scripts/deploy_migrations.sh staging --rollback

# Or manually
cd backend
alembic downgrade -1
```

#### API Server Rollback

```bash
# Rollback to previous commit
cd /opt/packoptima
git checkout HEAD~1

# Reinstall dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart packoptima-api
```

#### Worker Rollback

```bash
# Rollback to previous commit
cd /opt/packoptima
git checkout HEAD~1

# Reinstall dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Restart workers
sudo systemctl restart packoptima-worker
```

#### Feature Flag Rollback

```bash
# Disable new features in .env.staging
ENABLE_QUEUE_SYSTEM=false
ENABLE_BULK_UPLOAD=false
ENABLE_WEBHOOKS=false

# Restart services
sudo systemctl restart packoptima-api
sudo systemctl restart packoptima-worker
```

## Troubleshooting

### Common Issues

#### Database Connection Failed

```bash
# Check database is running
psql $DATABASE_URL -c "SELECT 1"

# Check connection string
echo $DATABASE_URL

# Check firewall rules
telnet staging-db-host 5432
```

#### Redis Connection Failed

```bash
# Check Redis is running
redis-cli -u $REDIS_URL ping

# Check connection string
echo $REDIS_URL

# Test connection
redis-cli -u $REDIS_URL info
```

#### API Health Check Failed

```bash
# Check service status
sudo systemctl status packoptima-api

# Check logs
sudo journalctl -u packoptima-api -n 100

# Check port binding
netstat -tuln | grep 8000

# Test locally
curl http://localhost:8000/health
```

#### Workers Not Processing Tasks

```bash
# Check worker status
sudo systemctl status packoptima-worker

# Check worker logs
sudo journalctl -u packoptima-worker -n 100

# Check Redis connection
redis-cli -u $REDIS_URL ping

# Check queue depth
redis-cli -u $REDIS_URL llen celery

# Inspect workers
celery -A app.core.celery_app inspect active
```

#### Migration Failed

```bash
# Check migration logs
cd backend
alembic history

# Check current version
alembic current

# Try manual migration
alembic upgrade head --sql

# Rollback if needed
alembic downgrade -1
```

### Getting Help

If you encounter issues:

1. Check the deployment log: `logs/staging_deployment_*.log`
2. Review service logs: `sudo journalctl -u <service-name>`
3. Check monitoring dashboards for anomalies
4. Consult the troubleshooting section in docs/DEPLOYMENT_GUIDE.md
5. Contact the DevOps team

## Post-Deployment

### Monitoring Plan

**First Hour:**
- Monitor error rates every 5 minutes
- Check response times
- Verify queue processing
- Watch for critical alerts

**First 24 Hours:**
- Review metrics hourly
- Check for memory leaks
- Verify data consistency
- Monitor alert frequency

**First Week:**
- Analyze performance trends
- Review error patterns
- Optimize slow queries
- Adjust alert thresholds

### Success Criteria

Deployment is successful when:
- ✓ All services running and healthy
- ✓ All tests passing
- ✓ Error rate < 0.1%
- ✓ Response times within targets
- ✓ No critical alerts
- ✓ Monitoring and alerting working
- ✓ Rollback procedure verified

### Next Steps

1. Monitor system for 24 hours
2. Collect user feedback
3. Review and address any issues
4. Update production deployment plan
5. Schedule production deployment
6. Conduct production deployment dry run

## Checklist

Use the comprehensive checklist in `docs/STAGING_DEPLOYMENT_CHECKLIST.md` to track deployment progress.

## References

- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Rollback Procedures](./ROLLBACK_PROCEDURES.md)
- [Monitoring Setup Guide](./MONITORING_SETUP_GUIDE.md)
- [Staging Deployment Checklist](./STAGING_DEPLOYMENT_CHECKLIST.md)

---

**Last Updated:** $(date '+%Y-%m-%d')
**Version:** 1.0
**Owner:** DevOps Team
