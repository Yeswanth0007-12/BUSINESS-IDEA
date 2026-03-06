# Monitoring Integration Guide

This guide explains how to integrate the monitoring infrastructure with your PackOptima application.

## Prerequisites

- PackOptima application running
- Monitoring stack deployed (see README.md)
- Python packages installed: `prometheus-client`, `sentry-sdk`

## Step 1: Install Required Packages

Add to `backend/requirements.txt`:

```txt
prometheus-client==0.19.0
sentry-sdk[fastapi]==1.38.0
```

Install:

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Add Prometheus Middleware

The Prometheus middleware has been created at `backend/app/middleware/prometheus_middleware.py`.

### Integrate with FastAPI

Edit `backend/app/main.py`:

```python
from app.middleware.prometheus_middleware import (
    PrometheusMiddleware,
    metrics_endpoint
)
from fastapi import FastAPI

app = FastAPI()

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    return metrics_endpoint()
```

## Step 3: Configure Sentry

Edit `backend/app/core/config.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Sentry configuration
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "production"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    def init_sentry(self):
        """Initialize Sentry error tracking."""
        if self.SENTRY_DSN:
            sentry_sdk.init(
                dsn=self.SENTRY_DSN,
                environment=self.SENTRY_ENVIRONMENT,
                traces_sample_rate=self.SENTRY_TRACES_SAMPLE_RATE,
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                    CeleryIntegration()
                ],
                send_default_pii=False,
                before_send=self.filter_sensitive_data
            )
    
    @staticmethod
    def filter_sensitive_data(event, hint):
        """Filter sensitive data from Sentry events."""
        if 'request' in event and 'headers' in event['request']:
            headers = event['request']['headers']
            if 'Authorization' in headers:
                headers['Authorization'] = '[Filtered]'
        return event

# Initialize settings
settings = Settings()
settings.init_sentry()
```

### Environment Variables

Add to `.env`:

```bash
# Sentry Configuration
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

## Step 4: Add Health Check Endpoints

Create `backend/app/api/health.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.celery_app import celery_app
import redis
import time

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependency status."""
    checks = {}
    
    # Check database
    try:
        db.execute("SELECT 1")
        checks["database"] = {
            "status": "ok",
            "response_time_ms": 5
        }
    except Exception as e:
        checks["database"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check Redis
    try:
        from app.core.config import settings
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        info = r.info()
        checks["redis"] = {
            "status": "ok",
            "memory_used_mb": info.get("used_memory") / 1024 / 1024
        }
    except Exception as e:
        checks["redis"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check Celery
    try:
        inspect = celery_app.control.inspect()
        active = inspect.active()
        checks["celery"] = {
            "status": "ok",
            "active_workers": len(active) if active else 0
        }
    except Exception as e:
        checks["celery"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Overall status
    all_ok = all(check.get("status") == "ok" for check in checks.values())
    
    return {
        "status": "healthy" if all_ok else "degraded",
        "timestamp": time.time(),
        "checks": checks
    }
```

Register in `backend/app/main.py`:

```python
from app.api import health

app.include_router(health.router, tags=["health"])
```

## Step 5: Instrument Celery Tasks

Edit your Celery tasks to record metrics:

```python
from app.middleware.prometheus_middleware import record_celery_task_completion
import time

@celery_app.task
def optimize_packaging_task(task_id, company_id, request_data):
    start_time = time.time()
    status = "success"
    
    try:
        # Your task logic here
        result = perform_optimization(request_data)
        return result
        
    except Exception as e:
        status = "failure"
        raise
        
    finally:
        duration = time.time() - start_time
        record_celery_task_completion(
            task_name="optimize_packaging",
            duration=duration,
            status=status
        )
```

## Step 6: Configure Logging

Create `backend/app/core/logging_config.py`:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "company_id"):
            log_data["company_id"] = record.company_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        return json.dumps(log_data)


def setup_logging():
    """Configure application logging."""
    # Create logger
    logger = logging.getLogger("packoptima")
    logger.setLevel(logging.INFO)
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler("/var/log/packoptima/app.log")
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    return logger
```

Initialize in `backend/app/main.py`:

```python
from app.core.logging_config import setup_logging

logger = setup_logging()
```

## Step 7: Update Docker Compose

Add monitoring network to your main `docker-compose.yml`:

```yaml
services:
  backend:
    # ... existing configuration ...
    networks:
      - default
      - monitoring
    labels:
      - "prometheus.scrape=true"
      - "prometheus.port=8000"
      - "prometheus.path=/metrics"

networks:
  default:
  monitoring:
    external: true
    name: monitoring_monitoring
```

## Step 8: Verify Integration

### Test Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

You should see Prometheus metrics output.

### Test Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed
```

### Check Prometheus Targets

1. Open Prometheus UI: http://localhost:9090
2. Go to Status → Targets
3. Verify `packoptima-api` target is UP

### View Grafana Dashboards

1. Open Grafana: http://localhost:3000
2. Login with admin/admin
3. Navigate to Dashboards
4. Open "PackOptima API Performance"

## Step 9: Configure Alerts

### Test Alert Rules

```bash
# Check alert rules in Prometheus
curl http://localhost:9090/api/v1/rules

# Trigger a test alert (optional)
# Simulate high error rate by making failing requests
for i in {1..100}; do
  curl http://localhost:8000/api/v1/invalid-endpoint
done
```

### Configure Slack Notifications

Edit `monitoring/alertmanager/alertmanager.yml`:

```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'

receivers:
  - name: 'slack'
    slack_configs:
      - channel: '#packoptima-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

Restart AlertManager:

```bash
docker-compose -f monitoring/docker-compose.monitoring.yml restart alertmanager
```

## Step 10: Production Deployment

### Security Checklist

- [ ] Change Grafana admin password
- [ ] Configure authentication for Prometheus
- [ ] Set up TLS/SSL for monitoring endpoints
- [ ] Restrict network access to monitoring services
- [ ] Configure firewall rules
- [ ] Set up backup for monitoring data

### Performance Tuning

- [ ] Adjust Prometheus scrape intervals
- [ ] Configure appropriate retention periods
- [ ] Set up read replicas for high-traffic dashboards
- [ ] Optimize alert rules to reduce noise

### Documentation

- [ ] Document custom metrics
- [ ] Create runbooks for common alerts
- [ ] Train team on dashboard usage
- [ ] Set up on-call rotation for critical alerts

## Troubleshooting

### Metrics Not Appearing

1. Check if `/metrics` endpoint is accessible
2. Verify Prometheus can reach the backend
3. Check Prometheus logs for scrape errors
4. Verify network connectivity

### High Memory Usage

1. Reduce metrics cardinality (fewer labels)
2. Increase scrape interval
3. Reduce retention period
4. Use recording rules for expensive queries

### Alerts Not Firing

1. Check alert rules syntax
2. Verify AlertManager is receiving alerts
3. Test notification channels
4. Check alert inhibition rules

## Support

For integration support:
- Documentation: [docs/MONITORING_SETUP_GUIDE.md](../docs/MONITORING_SETUP_GUIDE.md)
- Monitoring README: [monitoring/README.md](README.md)
- Create an issue in the repository

## References

- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Sentry FastAPI Integration](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
