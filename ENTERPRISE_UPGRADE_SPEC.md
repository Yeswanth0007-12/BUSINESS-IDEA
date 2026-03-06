# PackOptima AI SaaS - Enterprise Infrastructure Upgrade

## 🎯 Objective

Transform PackOptima from MVP to production-ready SaaS with enterprise-grade infrastructure:
- Role-Based Access Control (RBAC)
- Multi-tier subscription system
- Usage tracking and enforcement
- Audit logging
- Performance optimization
- Monitoring and observability
- Data export capabilities
- Enhanced security
- Analytics snapshots

---

## 📊 Updated Database Schema

### New Tables

```sql
-- Subscription Plans
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    price_monthly DECIMAL(10,2) NOT NULL,
    max_products INTEGER,
    max_boxes INTEGER,
    max_optimizations_per_month INTEGER,
    max_csv_uploads_per_month INTEGER,
    features JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Company Subscriptions
CREATE TABLE company_subscriptions (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    plan_id INTEGER REFERENCES subscription_plans(id),
    status VARCHAR(20) DEFAULT 'active',
    started_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    auto_renew BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User Roles (RBAC)
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, role)
);

-- Usage Tracking
CREATE TABLE usage_records (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    action_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_count INTEGER DEFAULT 1,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usage_company_date ON usage_records(company_id, created_at);
CREATE INDEX idx_usage_action_type ON usage_records(action_type);

-- Audit Logs
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_company_date ON audit_logs(company_id, created_at);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);

-- Monthly Analytics Snapshots
CREATE TABLE monthly_snapshots (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    month DATE NOT NULL,
    total_products INTEGER,
    total_boxes INTEGER,
    optimization_runs INTEGER,
    total_cost_savings DECIMAL(12,2),
    avg_space_utilization DECIMAL(5,2),
    top_product_category VARCHAR(100),
    most_used_box VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, month)
);

CREATE INDEX idx_snapshots_company_month ON monthly_snapshots(company_id, month);

-- Rate Limit Tracking
CREATE TABLE rate_limits (
    id SERIAL PRIMARY KEY,
    identifier VARCHAR(100) NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    request_count INTEGER DEFAULT 1,
    window_start TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(identifier, endpoint, window_start)
);

CREATE INDEX idx_rate_limits_lookup ON rate_limits(identifier, endpoint, window_start);
```

### Updated Existing Tables

```sql
-- Add indexes to existing tables for performance
CREATE INDEX idx_products_company ON products(company_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_sku ON products(sku);

CREATE INDEX idx_boxes_company ON boxes(company_id);
CREATE INDEX idx_boxes_cost ON boxes(cost_per_unit);

CREATE INDEX idx_optimization_runs_company ON optimization_runs(company_id);
CREATE INDEX idx_optimization_runs_date ON optimization_runs(created_at);

CREATE INDEX idx_optimization_results_run ON optimization_results(optimization_run_id);

-- Add soft delete support
ALTER TABLE products ADD COLUMN deleted_at TIMESTAMP;
ALTER TABLE boxes ADD COLUMN deleted_at TIMESTAMP;

-- Add metadata columns
ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP;
ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0;
ALTER TABLE companies ADD COLUMN settings JSONB DEFAULT '{}';
```

---

## 🏗️ Implementation Plan

### Phase 1: Database & Models (Priority: Critical)
1. Create migration for new tables
2. Add indexes to existing tables
3. Create new SQLAlchemy models
4. Update existing models

### Phase 2: RBAC System (Priority: Critical)
1. Role enum and permissions
2. Role middleware
3. Role decorators
4. Admin endpoints

### Phase 3: Subscription System (Priority: High)
1. Subscription plans seeding
2. Usage tracking service
3. Plan enforcement middleware
4. Subscription management API

### Phase 4: Audit & Monitoring (Priority: High)
1. Audit logging service
2. Structured logging
3. Performance monitoring
4. Health checks enhancement

### Phase 5: Security Hardening (Priority: High)
1. Enhanced rate limiting
2. Input validation
3. CORS tightening
4. SQL injection protection

### Phase 6: Data Export (Priority: Medium)
1. CSV export endpoints
2. PDF report generation
3. Bulk export utilities

### Phase 7: Analytics Snapshots (Priority: Medium)
1. Snapshot generation service
2. Scheduled jobs
3. Snapshot API endpoints

### Phase 8: Frontend Integration (Priority: Medium)
1. Role-based UI
2. Subscription display
3. Usage meters
4. Admin panel

---

## 📁 File Structure

```
backend/
├── app/
│   ├── models/
│   │   ├── subscription.py          # NEW
│   │   ├── user_role.py             # NEW
│   │   ├── usage_record.py          # NEW
│   │   ├── audit_log.py             # NEW
│   │   ├── monthly_snapshot.py      # NEW
│   │   └── rate_limit.py            # NEW
│   ├── schemas/
│   │   ├── subscription.py          # NEW
│   │   ├── role.py                  # NEW
│   │   ├── usage.py                 # NEW
│   │   ├── audit.py                 # NEW
│   │   └── export.py                # NEW
│   ├── services/
│   │   ├── rbac_service.py          # NEW
│   │   ├── subscription_service.py  # NEW
│   │   ├── usage_service.py         # NEW
│   │   ├── audit_service.py         # NEW
│   │   ├── export_service.py        # NEW
│   │   └── snapshot_service.py      # NEW
│   ├── middleware/
│   │   ├── rbac_middleware.py       # NEW
│   │   ├── usage_middleware.py      # NEW
│   │   ├── audit_middleware.py      # NEW
│   │   └── enhanced_rate_limit.py   # UPDATED
│   ├── api/
│   │   ├── admin.py                 # NEW
│   │   ├── subscriptions.py         # NEW
│   │   ├── export.py                # NEW
│   │   └── monitoring.py            # NEW
│   ├── core/
│   │   ├── permissions.py           # NEW
│   │   ├── enums.py                 # NEW
│   │   └── monitoring.py            # NEW
│   └── alembic/
│       └── versions/
│           └── 002_enterprise_upgrade.py  # NEW

frontend/
├── src/
│   ├── contexts/
│   │   └── SubscriptionContext.tsx  # NEW
│   ├── components/
│   │   ├── UsageMeter.tsx           # NEW
│   │   ├── RoleGuard.tsx            # NEW
│   │   └── SubscriptionBanner.tsx   # NEW
│   ├── pages/
│   │   ├── AdminPanel.tsx           # NEW
│   │   ├── SubscriptionPage.tsx     # NEW
│   │   └── AuditLogPage.tsx         # NEW
│   └── services/
│       ├── rbac.ts                  # NEW
│       └── subscription.ts          # NEW
```

---

## 🔐 Role-Based Access Control

### Roles

```python
class UserRole(str, Enum):
    ADMIN = "admin"        # Full access
    ANALYST = "analyst"    # Read + Optimize
    VIEWER = "viewer"      # Read only
```

### Permissions Matrix

| Action | Admin | Analyst | Viewer |
|--------|-------|---------|--------|
| View Products/Boxes | ✅ | ✅ | ✅ |
| Create Products/Boxes | ✅ | ✅ | ❌ |
| Edit Products/Boxes | ✅ | ✅ | ❌ |
| Delete Products/Boxes | ✅ | ❌ | ❌ |
| Run Optimization | ✅ | ✅ | ✅ |
| View Analytics | ✅ | ✅ | ✅ |
| Manage Users | ✅ | ❌ | ❌ |
| Manage Subscription | ✅ | ❌ | ❌ |
| View Audit Logs | ✅ | ❌ | ❌ |
| Export Data | ✅ | ✅ | ❌ |

---

## 💳 Subscription Tiers

### Free Plan
- Max 50 products
- Max 10 boxes
- 10 optimizations/month
- 5 CSV uploads/month
- Basic analytics
- Email support

### Pro Plan ($49/month)
- Max 500 products
- Max 50 boxes
- 100 optimizations/month
- 50 CSV uploads/month
- Advanced analytics
- Priority support
- Data export

### Enterprise Plan ($199/month)
- Unlimited products
- Unlimited boxes
- Unlimited optimizations
- Unlimited CSV uploads
- Custom analytics
- Dedicated support
- API access
- Audit logs
- White-label option

---

## 📈 Usage Tracking

### Tracked Actions

```python
class UsageAction(str, Enum):
    OPTIMIZATION_RUN = "optimization_run"
    CSV_UPLOAD = "csv_upload"
    PRODUCT_CREATE = "product_create"
    BOX_CREATE = "box_create"
    DATA_EXPORT = "data_export"
    API_CALL = "api_call"
```

### Enforcement Points

1. **Before Optimization**: Check monthly limit
2. **Before CSV Upload**: Check monthly limit
3. **Before Product/Box Create**: Check total limit
4. **Before Export**: Check plan feature

---

## 🔍 Audit Logging

### Logged Actions

- User login/logout
- Product create/edit/delete
- Box create/edit/delete
- Subscription changes
- User role changes
- Settings modifications
- Data exports

### Audit Log Entry

```json
{
  "action": "product_delete",
  "user_id": 123,
  "resource_type": "product",
  "resource_id": 456,
  "old_values": {"name": "Old Name", "sku": "OLD-SKU"},
  "new_values": null,
  "ip_address": "192.168.1.1",
  "timestamp": "2026-03-03T10:30:00Z"
}
```

---

## ⚡ Performance Optimizations

### Database Indexes

- Company-based queries (most common)
- Date-range queries (analytics)
- SKU lookups (products)
- Category filtering (products)

### Query Optimization

- Eager loading relationships
- Pagination for large datasets
- Caching frequent queries
- Connection pooling

### API Pagination

```python
# Default: 50 items per page
# Max: 100 items per page
GET /products?page=1&per_page=50
```

---

## 📊 Monitoring & Observability

### Structured Logging

```python
logger.info("optimization_completed", extra={
    "company_id": 123,
    "user_id": 456,
    "products_count": 10,
    "boxes_count": 5,
    "total_cost": 125.50,
    "duration_ms": 1234
})
```

### Health Check Enhancement

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2026-03-03T10:30:00Z",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "disk_space": "healthy"
  },
  "metrics": {
    "uptime_seconds": 86400,
    "total_requests": 12345,
    "avg_response_time_ms": 45
  }
}
```

---

## 📤 Data Export

### CSV Export

- Products export
- Boxes export
- Optimization history export
- Analytics export

### PDF Reports

- Monthly summary report
- Cost savings report
- Optimization recommendations

---

## 🛡️ Security Enhancements

### Rate Limiting (Enhanced)

```python
# Per endpoint limits
/auth/login: 5 requests/minute
/optimize: 10 requests/hour
/products: 100 requests/minute
/boxes: 100 requests/minute
```

### Input Validation

- Pydantic models for all inputs
- SQL injection protection (ORM)
- XSS protection
- CSRF tokens

### CORS Tightening

```python
# Production CORS
ALLOWED_ORIGINS = [
    "https://app.packoptima.com",
    "https://www.packoptima.com"
]
```

---

## 📸 Monthly Snapshots

### Snapshot Data

```json
{
  "month": "2026-03",
  "total_products": 450,
  "total_boxes": 35,
  "optimization_runs": 87,
  "total_cost_savings": 12450.75,
  "avg_space_utilization": 78.5,
  "top_product_category": "Electronics",
  "most_used_box": "Medium Box"
}
```

### Generation Schedule

- Runs on 1st of each month
- Generates snapshot for previous month
- Cached for fast retrieval
- Used for trend analysis

---

## 🎯 Success Metrics

### Technical Metrics

- API response time < 200ms (p95)
- Database query time < 50ms (p95)
- Uptime > 99.9%
- Error rate < 0.1%

### Business Metrics

- User role adoption
- Subscription conversion rate
- Feature usage by plan
- Monthly active users

---

## 🚀 Deployment Strategy

### Phase 1: Database Migration
1. Run migration in staging
2. Test all queries
3. Run migration in production
4. Verify data integrity

### Phase 2: Backend Deployment
1. Deploy new services
2. Enable feature flags
3. Monitor error rates
4. Gradual rollout

### Phase 3: Frontend Deployment
1. Deploy new components
2. A/B test new features
3. Collect user feedback
4. Full rollout

---

## ✅ Testing Strategy

### Unit Tests
- RBAC permissions
- Subscription enforcement
- Usage tracking
- Audit logging

### Integration Tests
- End-to-end workflows
- Role-based access
- Plan limits
- Export functionality

### Performance Tests
- Load testing
- Stress testing
- Database performance
- API response times

---

This upgrade transforms PackOptima into an enterprise-ready SaaS platform with:
- ✅ Production-grade infrastructure
- ✅ Scalable architecture
- ✅ Security hardening
- ✅ Monitoring and observability
- ✅ Multi-tenancy support
- ✅ Subscription management
- ✅ Audit compliance

**Ready for implementation in phases with zero downtime.**
