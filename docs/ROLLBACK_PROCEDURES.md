# PackOptima Rollback Procedures

## Overview

This document provides comprehensive rollback procedures for PackOptima v2.0 deployments. Use these procedures when a deployment fails or causes issues in production.

## Table of Contents

1. [Quick Rollback](#quick-rollback)
2. [Database Rollback](#database-rollback)
3. [Application Rollback](#application-rollback)
4. [Feature Flag Rollback](#feature-flag-rollback)
5. [Data Preservation](#data-preservation)
6. [Verification Steps](#verification-steps)
7. [Emergency Procedures](#emergency-procedures)

---

## Quick Rollback

### When to Use Quick Rollback

- Deployment causes critical errors
- Performance degradation detected
- Data integrity issues discovered
- Security vulnerability identified

### Quick Rollback Steps

```bash
# 1. Stop services
sudo systemctl stop packoptima-api
sudo systemctl stop packoptima-worker

# 2. Rollback code
cd /opt/packoptima
git checkout <previous_version_tag>

# 3. Rollback database (if needed)
cd backend
alembic downgrade -1

# 4. Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt

# 5. Restart services
sudo systemctl start packoptima-api
sudo systemctl start packoptima-worker

# 6. Verify health
curl -f http://localhost:8000/health
```

### Automated Quick Rollback

Use the rollback script:

```bash
./scripts/rollback.sh production
```

---

## Database Rollback

### Understanding Database Migrations

PackOptima v2.0 includes 11 database migrations:
- `004_enhanced_data_models.py` - Product and box enhancements
- `005_multi_product_orders.py` - Order tables
- `006_optimization_tasks.py` - Task tracking
- `007_bulk_uploads.py` - Bulk upload tables
- `008_analytics_tables.py` - Analytics snapshots
- `009_warehouse_integration.py` - API keys and webhooks
- `010_analytics_tables.py` - Additional analytics
- `011_warehouse_integration.py` - Webhook deliveries

### Rollback Single Migration

```bash
cd backend
source venv/bin/activate

# Check current version
alembic current

# Rollback one migration
alembic downgrade -1

# Verify rollback
alembic current
```

### Rollback to Specific Version

```bash
# Rollback to v1.x (before all v2.0 migrations)
alembic downgrade 003

# Or rollback to specific revision
alembic downgrade <revision_id>
```

### Rollback All v2.0 Migrations

```bash
# This rolls back to v1.x state
alembic downgrade 003
```

### Database Rollback Script

```bash
#!/bin/bash
# rollback_database.sh

set -e

ENVIRONMENT="${1:-production}"
TARGET_REVISION="${2:-003}"

echo "=== Database Rollback ==="
echo "Environment: $ENVIRONMENT"
echo "Target Revision: $TARGET_REVISION"

# Load environment
export $(cat .env.$ENVIRONMENT | grep -v '^#' | xargs)

# Backup current database
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="rollback_backup_${TIMESTAMP}.sql"

echo "Creating backup before rollback..."
pg_dump "$DATABASE_URL" -F c -f "/backups/${BACKUP_FILE}"

# Rollback database
echo "Rolling back database..."
cd backend
alembic downgrade "$TARGET_REVISION"

# Verify rollback
echo "Verifying rollback..."
alembic current

echo "✓ Database rollback complete"
```

### Data Preservation During Rollback

**Important:** Database rollbacks preserve data by default:

- **Downgrade removes tables/columns** but data is not deleted
- **Backup is created** before rollback
- **Foreign key constraints** are handled automatically
- **Indexes are dropped** during rollback

**Data Loss Scenarios:**

1. Rolling back `009_warehouse_integration.py`:
   - API keys will be lost (regenerate after rollback)
   - Webhook configurations will be lost (reconfigure after rollback)

2. Rolling back `006_optimization_tasks.py`:
   - Task history will be lost
   - Queue state will be lost

3. Rolling back `005_multi_product_orders.py`:
   - Order data will be lost
   - Order packing results will be lost

**Mitigation:**

```bash
# Export critical data before rollback
psql "$DATABASE_URL" -c "COPY api_keys TO '/tmp/api_keys_backup.csv' CSV HEADER"
psql "$DATABASE_URL" -c "COPY webhooks TO '/tmp/webhooks_backup.csv' CSV HEADER"
psql "$DATABASE_URL" -c "COPY orders TO '/tmp/orders_backup.csv' CSV HEADER"
```

---

## Application Rollback

### Code Rollback

```bash
#!/bin/bash
# rollback_application.sh

set -e

ENVIRONMENT="${1:-production}"
PREVIOUS_VERSION="${2:-v1.9.0}"

echo "=== Application Rollback ==="
echo "Environment: $ENVIRONMENT"
echo "Target Version: $PREVIOUS_VERSION"

# Stop services
echo "Stopping services..."
sudo systemctl stop packoptima-api
sudo systemctl stop packoptima-worker

# Rollback code
echo "Rolling back code to $PREVIOUS_VERSION..."
cd /opt/packoptima
git fetch --tags
git checkout "$PREVIOUS_VERSION"

# Reinstall dependencies
echo "Reinstalling dependencies..."
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Restart services
echo "Restarting services..."
sudo systemctl start packoptima-api
sudo systemctl start packoptima-worker

# Wait for services to start
sleep 5

# Health check
echo "Running health check..."
if curl -f http://localhost:8000/health; then
    echo "✓ Application rollback complete"
else
    echo "✗ Health check failed!"
    exit 1
fi
```

### Dependency Rollback

If new dependencies cause issues:

```bash
# Rollback to previous requirements.txt
cd backend
git show HEAD~1:requirements.txt > requirements.txt.old
pip install -r requirements.txt.old
```

### Configuration Rollback

```bash
# Restore previous configuration
cd /opt/packoptima
git show HEAD~1:backend/.env.production > backend/.env.production.rollback
cp backend/.env.production.rollback backend/.env.production
```

---

## Feature Flag Rollback

### Disable New Features Without Full Rollback

If you want to disable v2.0 features without rolling back code:

```bash
# Edit .env.production
ENABLE_QUEUE_SYSTEM=false
ENABLE_BULK_UPLOAD=false
ENABLE_WEBHOOKS=false
ENABLE_WAREHOUSE_API=false

# Restart services
sudo systemctl restart packoptima-api
sudo systemctl restart packoptima-worker
```

### Feature-Specific Rollback

**Disable Queue System:**
```bash
ENABLE_QUEUE_SYSTEM=false
# API will process requests synchronously
```

**Disable Bulk Upload:**
```bash
ENABLE_BULK_UPLOAD=false
# Bulk upload endpoints will return 503
```

**Disable Webhooks:**
```bash
ENABLE_WEBHOOKS=false
# Webhook deliveries will be skipped
```

**Disable Warehouse API:**
```bash
ENABLE_WAREHOUSE_API=false
# Warehouse endpoints will return 503
```

### Gradual Rollback Strategy

1. **Phase 1**: Disable new features via feature flags
2. **Phase 2**: Monitor for 24 hours
3. **Phase 3**: If stable, keep disabled; if issues persist, rollback code
4. **Phase 4**: If code rollback needed, rollback database

---

## Data Preservation

### Backup Before Rollback

**Always create backups before rollback:**

```bash
#!/bin/bash
# backup_before_rollback.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump "$DATABASE_URL" -F c -f "/backups/pre_rollback_${TIMESTAMP}.sql"

# Redis backup
redis-cli -u "$REDIS_URL" --rdb "/backups/redis_${TIMESTAMP}.rdb"

# Configuration backup
tar -czf "/backups/config_${TIMESTAMP}.tar.gz" \
    /opt/packoptima/backend/.env.production \
    /opt/packoptima/backend/alembic.ini

echo "✓ Backups created in /backups/"
```

### Data Export

Export critical data before rollback:

```bash
# Export API keys
psql "$DATABASE_URL" -c "\COPY api_keys TO '/tmp/api_keys.csv' CSV HEADER"

# Export webhooks
psql "$DATABASE_URL" -c "\COPY webhooks TO '/tmp/webhooks.csv' CSV HEADER"

# Export orders
psql "$DATABASE_URL" -c "\COPY orders TO '/tmp/orders.csv' CSV HEADER"

# Export analytics snapshots
psql "$DATABASE_URL" -c "\COPY analytics_snapshots TO '/tmp/analytics.csv' CSV HEADER"
```

### Data Restoration

After rollback, restore critical data:

```bash
# Restore API keys (after re-upgrading)
psql "$DATABASE_URL" -c "\COPY api_keys FROM '/tmp/api_keys.csv' CSV HEADER"

# Restore webhooks
psql "$DATABASE_URL" -c "\COPY webhooks FROM '/tmp/webhooks.csv' CSV HEADER"
```

---

## Verification Steps

### Post-Rollback Verification

```bash
#!/bin/bash
# verify_rollback.sh

echo "=== Rollback Verification ==="

# 1. Check service status
echo "1. Checking service status..."
sudo systemctl status packoptima-api --no-pager
sudo systemctl status packoptima-worker --no-pager

# 2. Health check
echo "2. Running health check..."
curl -f http://localhost:8000/health || exit 1

# 3. Database connectivity
echo "3. Checking database connectivity..."
psql "$DATABASE_URL" -c "SELECT 1" || exit 1

# 4. Redis connectivity
echo "4. Checking Redis connectivity..."
redis-cli -u "$REDIS_URL" ping || exit 1

# 5. Check migration version
echo "5. Checking migration version..."
cd backend
alembic current

# 6. Run smoke tests
echo "6. Running smoke tests..."
python smoke_tests/test_smoke.py || exit 1

# 7. Check error logs
echo "7. Checking recent error logs..."
sudo journalctl -u packoptima-api --since "5 minutes ago" | grep -i error

echo "✓ Rollback verification complete"
```

### Functional Testing

```bash
# Test authentication
curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"password"}'

# Test product listing
curl -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/products

# Test optimization
curl -X POST http://localhost:8000/optimize \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"product_ids":[1,2]}'
```

---

## Emergency Procedures

### Critical Failure Rollback

If production is completely down:

```bash
#!/bin/bash
# emergency_rollback.sh

set -e

echo "=== EMERGENCY ROLLBACK ==="

# 1. Stop all services immediately
sudo systemctl stop packoptima-api
sudo systemctl stop packoptima-worker

# 2. Restore from last known good backup
LATEST_BACKUP=$(ls -t /backups/*.sql | head -1)
echo "Restoring from: $LATEST_BACKUP"
pg_restore -d "$DATABASE_URL" -c "$LATEST_BACKUP"

# 3. Rollback code to last stable version
cd /opt/packoptima
git checkout v1.9.0  # Last stable version

# 4. Reinstall dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 5. Restart services
sudo systemctl start packoptima-api
sudo systemctl start packoptima-worker

# 6. Verify
sleep 10
curl -f http://localhost:8000/health || {
    echo "CRITICAL: Health check failed after emergency rollback!"
    echo "Manual intervention required!"
    exit 1
}

echo "✓ Emergency rollback complete"
```

### Partial Rollback

If only specific components are failing:

**Rollback API Server Only:**
```bash
sudo systemctl stop packoptima-api
cd /opt/packoptima
git checkout v1.9.0 -- backend/app/api/
sudo systemctl start packoptima-api
```

**Rollback Workers Only:**
```bash
sudo systemctl stop packoptima-worker
cd /opt/packoptima
git checkout v1.9.0 -- backend/app/tasks/
sudo systemctl start packoptima-worker
```

### Communication During Rollback

**Notify stakeholders:**

```bash
# Send alert to operations team
curl -X POST https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
    -H 'Content-Type: application/json' \
    -d '{
        "text": "🚨 ROLLBACK IN PROGRESS",
        "attachments": [{
            "color": "danger",
            "fields": [
                {"title": "Environment", "value": "Production", "short": true},
                {"title": "Reason", "value": "Critical errors detected", "short": true},
                {"title": "ETA", "value": "15 minutes", "short": true}
            ]
        }]
    }'
```

---

## Rollback Decision Matrix

| Issue | Severity | Recommended Action |
|-------|----------|-------------------|
| High error rate (> 10%) | Critical | Emergency rollback |
| Performance degradation (> 2x slower) | High | Feature flag rollback, monitor |
| Single feature failing | Medium | Disable feature flag |
| Minor bugs | Low | Fix forward, no rollback |
| Security vulnerability | Critical | Emergency rollback + patch |
| Data corruption | Critical | Restore from backup |

---

## Post-Rollback Actions

### 1. Root Cause Analysis

```markdown
## Rollback Incident Report

**Date:** YYYY-MM-DD
**Environment:** Production
**Rollback Type:** Full / Partial / Feature Flag

### Issue Description
[Describe what went wrong]

### Timeline
- HH:MM - Deployment started
- HH:MM - Issue detected
- HH:MM - Rollback initiated
- HH:MM - Rollback completed
- HH:MM - Services verified

### Root Cause
[What caused the issue]

### Impact
- Users affected: X
- Downtime: X minutes
- Data loss: Yes/No

### Prevention
[How to prevent this in the future]

### Action Items
- [ ] Fix identified issue
- [ ] Add test coverage
- [ ] Update deployment procedures
- [ ] Improve monitoring
```

### 2. Re-deployment Planning

After rollback:

1. **Identify root cause**
2. **Fix the issue**
3. **Add test coverage**
4. **Test in staging**
5. **Plan re-deployment**
6. **Communicate timeline**

### 3. Monitoring

After rollback, monitor:

- Error rates
- Response times
- Queue depth
- Database performance
- User reports

---

## Support

For rollback support:
- **Emergency Hotline:** +1 (555) 123-4567
- **Email:** ops@packoptima.ai
- **Slack:** #packoptima-ops

---

## Appendix: Rollback Checklist

### Pre-Rollback
- [ ] Identify issue severity
- [ ] Notify stakeholders
- [ ] Create backup
- [ ] Export critical data
- [ ] Document current state

### During Rollback
- [ ] Stop services
- [ ] Rollback code
- [ ] Rollback database (if needed)
- [ ] Reinstall dependencies
- [ ] Restart services

### Post-Rollback
- [ ] Verify health checks
- [ ] Run smoke tests
- [ ] Check error logs
- [ ] Monitor metrics
- [ ] Notify stakeholders
- [ ] Document incident
- [ ] Plan fix and re-deployment

---

© 2024 PackOptima. All rights reserved.
