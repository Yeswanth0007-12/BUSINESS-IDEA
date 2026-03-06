# Production Deployment Guide

Complete guide for deploying PackOptima to production with zero-downtime rolling updates.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Pre-Deployment Preparation](#pre-deployment-preparation)
4. [Deployment Process](#deployment-process)
5. [Post-Deployment Validation](#post-deployment-validation)
6. [Monitoring](#monitoring)
7. [Rollback Procedures](#rollback-procedures)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the complete production deployment process for the PackOptima Production Logistics Upgrade. The deployment includes:

- Enhanced data models with fragile/stackable flags
- Advanced 6-orientation packing algorithm
- Shipping cost calculator with volumetric weight
- Multi-product order packing with bin packing
- Asynchronous queue system with Celery and Redis
- Bulk order processing via CSV upload
- Advanced analytics with time-series trends
- Warehouse integration API with webhooks
- Comprehensive monitoring and alerting

**Deployment Strategy:** Zero-downtime rolling update

**Estimated Duration:** 30-60 minutes

**Rollback Time:** < 10 minutes

---

## Prerequisites

### Required Access
- SSH access to production servers
- Database admin credentials
- Docker registry access (if using)
- Monitoring system access (Grafana, Prometheus)
- Alert notification channels configured

### Required Tools
- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL client tools
- Redis client tools
- curl or httpie for API testing
- jq for JSON parsing (optional)

### Required Files
- `backend/.env.production` - Production environment variables
- `docker-compose.production.yml` - Production Docker Compose configuration
- `scripts/deploy_production.sh` - Automated deployment script
- `scripts/validate_production.sh` - Validation script
- `docs/PRODUCTION_DEPLOYMENT_CHECKLIST.md` - Deployment checklist

### Staging Validation
- [ ] Staging deployment completed successfully
- [ ] All tests passed on staging
- [ ] 24-hour monitoring period completed
- [ ] No critical issues found

---

## Pre-Deployment Preparation

### 1. Environment Configuration

Create `backend/.env.production` from the example:

```bash
cp backend/.env.production.example backend/.env.production
```

Configure all required variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@db-host:5432/packoptima_prod

# Redis
REDIS_URL=redis://redis-host:6379/0
CELERY_BROKER_URL=redis://redis-host:6379/0
CELERY_RESULT_BACKEND=redis://redis-host:6379/1

# Security
SECRET_KEY=<generate-secure-random-key-min-32-chars>
JWT_SECRET_KEY=<generate-secure-random-key-min-32-chars>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_V1_PREFIX=/api/v1
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Monitoring
SENTRY_DSN=<your-sentry-dsn>
PROMETHEUS_ENABLED=true

# Email (if applicable)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=<smtp-password>

# Warehouse Integration
WEBHOOK_SECRET_KEY=<generate-secure-random-key>

# Rate Limiting
RATE_LIMIT_STANDARD=100
RATE_LIMIT_PREMIUM=500
```

### 2. Generate Secrets

Generate secure random keys:

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate WEBHOOK_SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Database Backup

Create a backup of the current production database:

```bash
# Using Docker
docker exec packoptima-db-production pg_dump -U postgres packoptima > \
  backups/production_backup_$(date +%Y%m%d_%H%M%S).sql

# Or using pg_dump directly
pg_dump -h db-host -U postgres -d packoptima_prod > \
  backups/production_backup_$(date +%Y%m%d_%H%M%S).sql
```

Verify backup:

```bash
# Check file size
ls -lh backups/production_backup_*.sql

# Check backup integrity
head -n 20 backups/production_backup_*.sql
tail -n 20 backups/production_backup_*.sql
```

### 4. Team Notification

Notify stakeholders:

```
Subject: Production Deployment - PackOptima Logistics Upgrade

Team,

We will be deploying the Production Logistics Upgrade to PackOptima today.

Deployment Window: [START_TIME] - [END_TIME]
Expected Duration: 30-60 minutes
Expected Downtime: None (rolling update)

New Features:
- Enhanced packing algorithms with 6-orientation testing
- Shipping cost optimization
- Multi-product order packing
- Bulk order processing
- Advanced analytics
- Warehouse integration API

Monitoring:
- Grafana: https://grafana.yourdomain.com
- Status Page: https://status.yourdomain.com

Contact:
- Deployment Lead: [NAME] - [PHONE]
- On-Call Engineer: [NAME] - [PHONE]

Thank you,
DevOps Team
```

---

## Deployment Process

### Option 1: Automated Deployment (Recommended)

Use the automated deployment script:

```bash
# Make script executable
chmod +x scripts/deploy_production.sh

# Run deployment
bash scripts/deploy_production.sh
```

The script will:
1. Run pre-deployment checks
2. Create database backup
3. Run database migrations
4. Build Docker images
5. Deploy API servers (rolling update)
6. Deploy Celery workers
7. Run smoke tests
8. Run integration tests
9. Verify monitoring
10. Validate deployment

Monitor the deployment:

```bash
# Watch deployment log
tail -f logs/production_deployment_*.log

# In another terminal, watch containers
watch docker ps

# Watch API logs
docker-compose -f docker-compose.production.yml logs -f api
```

### Option 2: Manual Deployment

If you prefer manual control, follow these steps:

#### Step 1: Pre-Deployment Checks

```bash
# Verify staging success
cat logs/staging_deployment_success.flag

# Verify environment file
cat backend/.env.production | grep -v PASSWORD | grep -v SECRET

# Verify Docker
docker --version
docker-compose --version
```

#### Step 2: Database Backup

```bash
# Create backup
mkdir -p backups
docker exec packoptima-db-production pg_dump -U postgres packoptima > \
  backups/production_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh backups/
```

#### Step 3: Database Migrations

```bash
cd backend

# Load production environment
export $(grep -v '^#' .env.production | xargs)

# Check current version
alembic current

# Run migrations
alembic upgrade head

# Verify new version
alembic current

cd ..
```

#### Step 4: Build Docker Images

```bash
# Build API image
docker build -t packoptima-api:production-$(date +%Y%m%d) \
  -f backend/Dockerfile backend/

# Tag as latest
docker tag packoptima-api:production-$(date +%Y%m%d) \
  packoptima-api:production-latest

# Build worker image
docker build -t packoptima-worker:production-$(date +%Y%m%d) \
  -f backend/Dockerfile.worker backend/

# Tag as latest
docker tag packoptima-worker:production-$(date +%Y%m%d) \
  packoptima-worker:production-latest
```

#### Step 5: Deploy API Servers (Rolling Update)

```bash
# Scale up new instances
docker-compose -f docker-compose.production.yml up -d --scale api=2 --no-recreate

# Wait for health checks
sleep 10

# Verify health
curl -f http://localhost:8000/health

# Scale down old instances
docker-compose -f docker-compose.production.yml up -d --scale api=1

# Verify API is responding
curl -f http://localhost:8000/docs
```

#### Step 6: Deploy Celery Workers

```bash
# Gracefully stop old workers
docker-compose -f docker-compose.production.yml stop worker

# Start new workers
docker-compose -f docker-compose.production.yml up -d worker

# Verify workers
docker-compose -f docker-compose.production.yml logs worker | grep "celery@"
```

#### Step 7: Run Smoke Tests

```bash
# Run smoke tests
bash backend/smoke_tests/run_smoke_tests.sh production

# Or manual checks
curl -f http://localhost:8000/health
curl -f http://localhost:8000/docs
curl -f http://localhost:8000/metrics
```

#### Step 8: Run Integration Tests

```bash
cd backend

# Run integration tests (read-only)
pytest tests/test_integration_workflows.py -v

cd ..
```

#### Step 9: Verify Monitoring

```bash
# Check Prometheus
curl -f http://localhost:9090/-/healthy

# Check Grafana
curl -f http://localhost:3001/api/health

# Check AlertManager
curl -f http://localhost:9093/-/healthy
```

#### Step 10: Validate Deployment

```bash
# Run validation script
bash scripts/validate_production.sh
```

---

## Post-Deployment Validation

### Immediate Checks (0-15 minutes)

```bash
# 1. Verify all services running
docker ps

# 2. Check API health
curl http://localhost:8000/health

# 3. Check error rates
docker-compose -f docker-compose.production.yml logs api --tail=100 | grep ERROR

# 4. Check response times
time curl http://localhost:8000/health

# 5. Verify database connectivity
docker exec packoptima-db-production pg_isready

# 6. Verify Redis connectivity
docker exec packoptima-redis-production redis-cli ping

# 7. Check worker status
docker-compose -f docker-compose.production.yml logs worker --tail=50
```

### Short-term Monitoring (15-60 minutes)

Monitor these metrics in Grafana:

1. **API Performance**
   - Request rate
   - Response times (p50, p95, p99)
   - Error rate
   - Active connections

2. **Queue Metrics**
   - Queue depth
   - Task processing rate
   - Task success/failure rate
   - Worker count

3. **Database Metrics**
   - Connection count
   - Query duration
   - Transaction rate
   - Cache hit rate

4. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

### Medium-term Validation (1-4 hours)

1. **Performance Trends**
   - No degradation over time
   - Response times stable
   - Resource usage stable

2. **Error Analysis**
   - Error rate < 0.1%
   - No new error types
   - No error spikes

3. **User Feedback**
   - Monitor support channels
   - Check for user-reported issues
   - Review feedback forms

### Long-term Monitoring (4-24 hours)

1. **System Stability**
   - No memory leaks
   - No resource exhaustion
   - No intermittent failures

2. **Feature Adoption**
   - New features being used
   - No feature-specific errors
   - Performance acceptable

3. **Business Metrics**
   - Optimization count
   - User engagement
   - Cost savings metrics

---

## Monitoring

### Grafana Dashboards

Access Grafana at: `http://localhost:3001` (or your configured URL)

**Default Credentials:**
- Username: admin
- Password: (configured in .env)

**Key Dashboards:**

1. **API Performance Dashboard**
   - Request rate by endpoint
   - Response time percentiles
   - Error rate by status code
   - Active connections

2. **Queue Metrics Dashboard**
   - Queue depth over time
   - Task processing rate
   - Task duration distribution
   - Worker health status

3. **Database Metrics Dashboard**
   - Connection pool usage
   - Query duration
   - Transaction rate
   - Table sizes

4. **System Health Dashboard**
   - CPU usage by container
   - Memory usage by container
   - Disk usage
   - Network throughput

### Prometheus Queries

Access Prometheus at: `http://localhost:9090`

**Useful Queries:**

```promql
# API request rate
rate(http_requests_total[5m])

# API p95 response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Queue depth
celery_queue_length

# Database connections
pg_stat_database_numbackends

# Redis memory usage
redis_memory_used_bytes / redis_memory_max_bytes
```

### Alert Rules

Active alert rules (configured in `monitoring/prometheus/alerts/packoptima.yml`):

1. **HighAPIResponseTime** - API p95 > 1 second for 5 minutes
2. **HighErrorRate** - Error rate > 5% for 5 minutes
3. **HighQueueDepth** - Queue > 1000 tasks for 10 minutes
4. **HighDatabaseConnections** - Connections > 80% for 5 minutes
5. **CeleryWorkerDown** - Worker down for 2 minutes
6. **HighRedisMemory** - Memory > 80% for 5 minutes
7. **APIServerDown** - Server down for 1 minute

### Log Aggregation

View logs:

```bash
# API logs
docker-compose -f docker-compose.production.yml logs -f api

# Worker logs
docker-compose -f docker-compose.production.yml logs -f worker

# Database logs
docker logs -f packoptima-db-production

# Redis logs
docker logs -f packoptima-redis-production

# All logs
docker-compose -f docker-compose.production.yml logs -f
```

Search logs:

```bash
# Search for errors
docker-compose -f docker-compose.production.yml logs api | grep ERROR

# Search for specific endpoint
docker-compose -f docker-compose.production.yml logs api | grep "/api/v1/optimize"

# Count errors
docker-compose -f docker-compose.production.yml logs api | grep -c ERROR
```

---

## Rollback Procedures

### When to Rollback

Initiate rollback if:
- Error rate > 10% for > 5 minutes
- API unavailable for > 2 minutes
- Critical bug affecting all users
- Data corruption detected
- Security breach detected

### Automated Rollback

```bash
# Use rollback script
bash scripts/rollback_production.sh

# Specify rollback point
bash scripts/rollback_production.sh logs/rollback_point_20240306_143022.txt
```

### Manual Rollback

#### Step 1: Rollback API Servers

```bash
# Switch to previous image
export API_IMAGE=packoptima-api:production-previous

# Deploy previous version
docker-compose -f docker-compose.production.yml up -d api

# Verify health
curl -f http://localhost:8000/health
```

#### Step 2: Rollback Workers

```bash
# Switch to previous image
export WORKER_IMAGE=packoptima-worker:production-previous

# Deploy previous workers
docker-compose -f docker-compose.production.yml up -d worker
```

#### Step 3: Rollback Database (if needed)

```bash
# Stop API and workers
docker-compose -f docker-compose.production.yml stop api worker

# Restore database from backup
docker exec -i packoptima-db-production psql -U postgres -d packoptima < \
  backups/production_backup_20240306_140000.sql

# Restart services
docker-compose -f docker-compose.production.yml up -d
```

#### Step 4: Verify Rollback

```bash
# Run validation
bash scripts/validate_production.sh

# Check logs
docker-compose -f docker-compose.production.yml logs --tail=100
```

---

## Troubleshooting

### Issue: API Not Responding

**Symptoms:**
- Health endpoint returns 502/503
- Containers restarting
- High error rate

**Diagnosis:**

```bash
# Check container status
docker ps -a

# Check API logs
docker-compose -f docker-compose.production.yml logs api --tail=100

# Check resource usage
docker stats
```

**Solutions:**

1. **Database connection issues:**
   ```bash
   # Verify database connectivity
   docker exec packoptima-db-production pg_isready
   
   # Check connection string
   docker-compose -f docker-compose.production.yml exec api env | grep DATABASE_URL
   ```

2. **Memory issues:**
   ```bash
   # Increase memory limit in docker-compose.production.yml
   # Restart containers
   docker-compose -f docker-compose.production.yml restart api
   ```

3. **Configuration issues:**
   ```bash
   # Verify environment variables
   docker-compose -f docker-compose.production.yml config
   
   # Check for missing variables
   docker-compose -f docker-compose.production.yml exec api env
   ```

### Issue: High Response Times

**Symptoms:**
- API p95 > 1 second
- Slow page loads
- Timeout errors

**Diagnosis:**

```bash
# Check database query times
docker exec packoptima-db-production psql -U postgres -d packoptima -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Check Redis latency
docker exec packoptima-redis-production redis-cli --latency

# Check API metrics
curl http://localhost:8000/metrics | grep http_request_duration
```

**Solutions:**

1. **Database optimization:**
   ```bash
   # Add missing indexes
   # Optimize slow queries
   # Increase connection pool size
   ```

2. **Redis optimization:**
   ```bash
   # Increase Redis memory
   # Enable Redis persistence
   # Add Redis replicas
   ```

3. **API optimization:**
   ```bash
   # Increase worker count
   # Enable caching
   # Optimize algorithms
   ```

### Issue: Workers Not Processing Tasks

**Symptoms:**
- Queue depth increasing
- Tasks stuck in pending
- No task completions

**Diagnosis:**

```bash
# Check worker logs
docker-compose -f docker-compose.production.yml logs worker --tail=100

# Check Redis connectivity
docker exec packoptima-redis-production redis-cli ping

# Check queue depth
docker exec packoptima-redis-production redis-cli llen celery
```

**Solutions:**

1. **Worker connectivity:**
   ```bash
   # Restart workers
   docker-compose -f docker-compose.production.yml restart worker
   
   # Verify Redis connection
   docker-compose -f docker-compose.production.yml exec worker env | grep CELERY_BROKER_URL
   ```

2. **Worker capacity:**
   ```bash
   # Scale up workers
   docker-compose -f docker-compose.production.yml up -d --scale worker=3
   ```

3. **Task errors:**
   ```bash
   # Check for task failures
   docker-compose -f docker-compose.production.yml logs worker | grep ERROR
   
   # Purge failed tasks (if safe)
   docker exec packoptima-redis-production redis-cli flushdb
   ```

### Issue: Database Migration Failures

**Symptoms:**
- Migration command fails
- Database schema mismatch
- Application errors

**Diagnosis:**

```bash
# Check current migration version
cd backend
alembic current

# Check migration history
alembic history

# Check database schema
docker exec packoptima-db-production psql -U postgres -d packoptima -c "\dt"
```

**Solutions:**

1. **Rollback migration:**
   ```bash
   # Downgrade to previous version
   alembic downgrade -1
   
   # Verify
   alembic current
   ```

2. **Fix migration script:**
   ```bash
   # Edit migration file
   # Re-run migration
   alembic upgrade head
   ```

3. **Manual schema fix:**
   ```bash
   # Connect to database
   docker exec -it packoptima-db-production psql -U postgres -d packoptima
   
   # Run manual SQL commands
   # Stamp migration version
   alembic stamp head
   ```

---

## Support

### Emergency Contacts

- **Deployment Lead:** [NAME] - [PHONE] - [EMAIL]
- **On-Call Engineer:** [NAME] - [PHONE] - [EMAIL]
- **Database Admin:** [NAME] - [PHONE] - [EMAIL]
- **Security Team:** [EMAIL]

### Documentation

- **API Documentation:** http://localhost:8000/docs
- **Monitoring Guide:** docs/MONITORING_SETUP_GUIDE.md
- **Rollback Procedures:** docs/ROLLBACK_PROCEDURES.md
- **Warehouse Integration:** docs/WAREHOUSE_INTEGRATION_GUIDE.md

### Useful Commands

```bash
# Quick health check
curl http://localhost:8000/health

# View all containers
docker ps -a

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Restart service
docker-compose -f docker-compose.production.yml restart api

# Scale workers
docker-compose -f docker-compose.production.yml up -d --scale worker=3

# Database backup
docker exec packoptima-db-production pg_dump -U postgres packoptima > backup.sql

# Database restore
docker exec -i packoptima-db-production psql -U postgres -d packoptima < backup.sql
```

---

## Completion

After successful deployment:

1. ✅ Mark deployment as complete in tracking system
2. ✅ Update status page
3. ✅ Notify stakeholders of completion
4. ✅ Schedule post-deployment review meeting
5. ✅ Document lessons learned
6. ✅ Update runbooks with any new procedures

**Deployment completed successfully!** 🎉
