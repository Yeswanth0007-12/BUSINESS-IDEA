# PackOptima Monitoring and Alerting Setup Guide

## Overview

This guide provides comprehensive instructions for setting up monitoring, alerting, and observability for PackOptima production environments. It covers Prometheus metrics, Grafana dashboards, Sentry error tracking, log aggregation, and alerting rules.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prometheus Setup](#prometheus-setup)
3. [Grafana Setup](#grafana-setup)
4. [Sentry Error Tracking](#sentry-error-tracking)
5. [Log Aggregation](#log-aggregation)
6. [Alerting Rules](#alerting-rules)
7. [Health Check Endpoints](#health-check-endpoints)
8. [Performance Metrics](#performance-metrics)
9. [Dashboard Examples](#dashboard-examples)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  API Server │────▶│  Prometheus  │────▶│   Grafana   │
└─────────────┘     └──────────────┘     └─────────────┘
       │                                         │
       │                                         ▼
       │            ┌──────────────┐     ┌─────────────┐
       └───────────▶│    Sentry    │     │  Alerting   │
                    └──────────────┘     └─────────────┘
       │
       │            ┌──────────────┐
       └───────────▶│ ELK/Loki     │
                    └──────────────┘
```

### Components

- **Prometheus**: Metrics collection and storage
- **Grafana**: Metrics visualization and dashboards
- **Sentry**: Error tracking and performance monitoring
- **ELK/Loki**: Log aggregation and search
- **AlertManager**: Alert routing and notification

---

## Prometheus Setup

### Installation

```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64

# Create Prometheus user
sudo useradd --no-create-home --shell /bin/false prometheus

# Create directories
sudo mkdir -p /etc/prometheus /var/lib/prometheus

# Copy binaries
sudo cp prometheus promtool /usr/local/bin/
sudo cp -r consoles console_libraries /etc/prometheus/

# Set ownership
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus
```

### Configuration

**`/etc/prometheus/prometheus.yml`**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'packoptima-production'
    environment: 'production'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - localhost:9093

# Load alerting rules
rule_files:
  - "alerts/*.yml"

# Scrape configurations
scrape_configs:
  # API Servers
  - job_name: 'packoptima-api'
    static_configs:
      - targets:
          - '10.0.1.10:8000'
          - '10.0.1.11:8000'
          - '10.0.1.12:8000'
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Celery Workers
  - job_name: 'packoptima-workers'
    static_configs:
      - targets:
          - '10.0.2.10:9090'
          - '10.0.2.11:9090'
    metrics_path: '/metrics'
    scrape_interval: 15s

  # PostgreSQL
  - job_name: 'postgresql'
    static_configs:
      - targets:
          - '10.0.3.10:9187'
    scrape_interval: 30s

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets:
          - '10.0.4.10:9121'
    scrape_interval: 30s

  # Node Exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets:
          - '10.0.1.10:9100'
          - '10.0.1.11:9100'
          - '10.0.1.12:9100'
          - '10.0.2.10:9100'
          - '10.0.2.11:9100'
    scrape_interval: 30s
```

### Systemd Service

**`/etc/systemd/system/prometheus.service`**
```ini
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --storage.tsdb.retention.time=30d \
    --web.enable-lifecycle

Restart=always

[Install]
WantedBy=multi-user.target
```

### Start Prometheus

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start Prometheus
sudo systemctl start prometheus

# Enable on boot
sudo systemctl enable prometheus

# Check status
sudo systemctl status prometheus

# Access Prometheus UI
# http://localhost:9090
```

---

## Grafana Setup

### Installation

```bash
# Add Grafana repository
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

# Install Grafana
sudo apt-get update
sudo apt-get install grafana

# Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Access Grafana UI
# http://localhost:3000
# Default credentials: admin/admin
```

### Configure Prometheus Data Source

1. Log in to Grafana (http://localhost:3000)
2. Go to **Configuration** → **Data Sources**
3. Click **Add data source**
4. Select **Prometheus**
5. Configure:
   - Name: `Prometheus`
   - URL: `http://localhost:9090`
   - Access: `Server (default)`
6. Click **Save & Test**

### Import Dashboards

```bash
# Download PackOptima dashboards
curl -o /tmp/packoptima-api-dashboard.json \
    https://raw.githubusercontent.com/packoptima/monitoring/main/grafana/api-dashboard.json

# Import via Grafana UI:
# 1. Go to Dashboards → Import
# 2. Upload JSON file
# 3. Select Prometheus data source
# 4. Click Import
```

---

## Sentry Error Tracking

### Installation

```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]
```

### Configuration

**`backend/app/core/config.py`**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

# Initialize Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration()
        ],
        # Set release version
        release=f"packoptima@{settings.VERSION}",
        # Send PII (be careful with sensitive data)
        send_default_pii=False,
        # Before send callback to filter sensitive data
        before_send=filter_sensitive_data
    )

def filter_sensitive_data(event, hint):
    """Filter sensitive data from Sentry events."""
    # Remove API keys from headers
    if 'request' in event and 'headers' in event['request']:
        headers = event['request']['headers']
        if 'Authorization' in headers:
            headers['Authorization'] = '[Filtered]'
    
    # Remove sensitive query parameters
    if 'request' in event and 'query_string' in event['request']:
        # Filter sensitive params
        pass
    
    return event
```

### Environment Variables

```bash
# .env.production
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # Sample 10% of transactions
```

### Custom Error Context

```python
from sentry_sdk import capture_exception, set_context, set_tag

# Add custom context
set_context("optimization", {
    "product_ids": [1, 2, 3],
    "courier_rate": 2.5
})

# Add tags for filtering
set_tag("company_id", company_id)
set_tag("optimization_type", "multi_product")

# Capture exception
try:
    result = optimize_package(order)
except Exception as e:
    capture_exception(e)
    raise
```

---

## Log Aggregation

### Option 1: ELK Stack (Elasticsearch, Logstash, Kibana)

**Install Elasticsearch:**
```bash
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt-get update && sudo apt-get install elasticsearch
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch
```

**Install Logstash:**
```bash
sudo apt-get install logstash
```

**Logstash Configuration:**
```conf
# /etc/logstash/conf.d/packoptima.conf
input {
  file {
    path => "/var/log/packoptima/*.log"
    type => "packoptima"
    codec => json
  }
}

filter {
  if [type] == "packoptima" {
    json {
      source => "message"
    }
    
    # Parse timestamp
    date {
      match => ["timestamp", "ISO8601"]
    }
    
    # Add fields
    mutate {
      add_field => {
        "environment" => "production"
        "application" => "packoptima"
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "packoptima-%{+YYYY.MM.dd}"
  }
}
```

**Install Kibana:**
```bash
sudo apt-get install kibana
sudo systemctl start kibana
sudo systemctl enable kibana
# Access at http://localhost:5601
```

### Option 2: Grafana Loki (Lightweight Alternative)

**Install Loki:**
```bash
wget https://github.com/grafana/loki/releases/download/v2.8.0/loki-linux-amd64.zip
unzip loki-linux-amd64.zip
sudo mv loki-linux-amd64 /usr/local/bin/loki
```

**Loki Configuration:**
```yaml
# /etc/loki/config.yml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb:
    directory: /var/lib/loki/index
  filesystem:
    directory: /var/lib/loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h
```

**Install Promtail (Log Shipper):**
```bash
wget https://github.com/grafana/loki/releases/download/v2.8.0/promtail-linux-amd64.zip
unzip promtail-linux-amd64.zip
sudo mv promtail-linux-amd64 /usr/local/bin/promtail
```

**Promtail Configuration:**
```yaml
# /etc/promtail/config.yml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /var/lib/promtail/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
  - job_name: packoptima
    static_configs:
      - targets:
          - localhost
        labels:
          job: packoptima
          environment: production
          __path__: /var/log/packoptima/*.log
```

---

## Alerting Rules

### Prometheus Alert Rules

**`/etc/prometheus/alerts/packoptima.yml`**
```yaml
groups:
  - name: packoptima_api
    interval: 30s
    rules:
      # API Response Time
      - alert: HighAPIResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
          component: api
        annotations:
          summary: "High API response time"
          description: "API p95 response time is {{ $value }}s (threshold: 1s)"

      # Error Rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
          component: api
        annotations:
          summary: "High error rate"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

      # Queue Depth
      - alert: HighQueueDepth
        expr: celery_queue_length > 1000
        for: 10m
        labels:
          severity: warning
          component: queue
        annotations:
          summary: "High queue depth"
          description: "Queue depth is {{ $value }} tasks (threshold: 1000)"

      # Database Connections
      - alert: HighDatabaseConnections
        expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: warning
          component: database
        annotations:
          summary: "High database connection usage"
          description: "Database connections at {{ $value | humanizePercentage }} of pool"

      # Redis Memory
      - alert: HighRedisMemory
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.8
        for: 5m
        labels:
          severity: warning
          component: redis
        annotations:
          summary: "High Redis memory usage"
          description: "Redis memory at {{ $value | humanizePercentage }} of limit"

      # Celery Worker Down
      - alert: CeleryWorkerDown
        expr: up{job="packoptima-workers"} == 0
        for: 2m
        labels:
          severity: critical
          component: worker
        annotations:
          summary: "Celery worker is down"
          description: "Worker {{ $labels.instance }} is not responding"

      # API Server Down
      - alert: APIServerDown
        expr: up{job="packoptima-api"} == 0
        for: 1m
        labels:
          severity: critical
          component: api
        annotations:
          summary: "API server is down"
          description: "API server {{ $labels.instance }} is not responding"

      # Disk Space
      - alert: LowDiskSpace
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
        for: 5m
        labels:
          severity: warning
          component: infrastructure
        annotations:
          summary: "Low disk space"
          description: "Disk space on {{ $labels.instance }} is below 10%"

      # CPU Usage
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 10m
        labels:
          severity: warning
          component: infrastructure
        annotations:
          summary: "High CPU usage"
          description: "CPU usage on {{ $labels.instance }} is {{ $value }}%"

      # Memory Usage
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.9
        for: 5m
        labels:
          severity: warning
          component: infrastructure
        annotations:
          summary: "High memory usage"
          description: "Memory usage on {{ $labels.instance }} is {{ $value | humanizePercentage }}"
```

### AlertManager Configuration

**`/etc/alertmanager/alertmanager.yml`**
```yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    # Critical alerts to PagerDuty
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true
    
    # All alerts to Slack
    - match_re:
        severity: warning|critical
      receiver: 'slack'

receivers:
  - name: 'default'
    email_configs:
      - to: 'ops@packoptima.ai'
        from: 'alerts@packoptima.ai'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@packoptima.ai'
        auth_password: 'your-password'

  - name: 'slack'
    slack_configs:
      - channel: '#packoptima-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'your-pagerduty-service-key'
        description: '{{ .GroupLabels.alertname }}'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']
```

---

## Health Check Endpoints

### API Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "2.0.0",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "celery": "ok"
  }
}
```

### Detailed Health Check

**Endpoint:** `GET /health/detailed`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "2.0.0",
  "checks": {
    "database": {
      "status": "ok",
      "response_time_ms": 5,
      "connections": 10,
      "max_connections": 100
    },
    "redis": {
      "status": "ok",
      "response_time_ms": 2,
      "memory_used_mb": 150,
      "memory_max_mb": 2048
    },
    "celery": {
      "status": "ok",
      "active_workers": 4,
      "queue_depth": 25
    }
  }
}
```

---

## Performance Metrics

### Key Metrics to Monitor

**API Metrics:**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (%)
- Active connections

**Queue Metrics:**
- Queue depth
- Task processing rate
- Task success/failure rate
- Average task duration

**Database Metrics:**
- Connection pool usage
- Query duration
- Slow queries (> 1s)
- Deadlocks

**Redis Metrics:**
- Memory usage
- Hit rate
- Connected clients
- Commands/second

**System Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O

---

## Dashboard Examples

### API Performance Dashboard

**Panels:**
1. Request Rate (requests/second)
2. Response Time (p50, p95, p99)
3. Error Rate (%)
4. Active Connections
5. Top Endpoints by Request Count
6. Top Endpoints by Response Time
7. Error Distribution by Status Code
8. Request Distribution by Method

### Queue Performance Dashboard

**Panels:**
1. Queue Depth Over Time
2. Task Processing Rate
3. Task Success/Failure Rate
4. Average Task Duration
5. Active Workers
6. Task Distribution by Type
7. Failed Tasks by Error Type

### Infrastructure Dashboard

**Panels:**
1. CPU Usage by Server
2. Memory Usage by Server
3. Disk Usage by Server
4. Network I/O by Server
5. Database Connections
6. Redis Memory Usage
7. Load Average

---

## Troubleshooting

### High Response Times

**Check:**
1. Database query performance
2. Redis connection issues
3. CPU/memory usage
4. Network latency

**Actions:**
```bash
# Check slow queries
psql -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10"

# Check Redis latency
redis-cli --latency

# Check system resources
top
iostat
```

### High Error Rate

**Check:**
1. Application logs
2. Sentry error reports
3. Database connection errors
4. External API failures

**Actions:**
```bash
# Check recent errors
tail -f /var/log/packoptima/error.log

# Check Sentry dashboard
# https://sentry.io/organizations/packoptima/issues/

# Check database connections
psql -c "SELECT * FROM pg_stat_activity"
```

### Queue Backup

**Check:**
1. Worker status
2. Task failure rate
3. Redis memory
4. Task complexity

**Actions:**
```bash
# Check worker status
celery -A app.core.celery_app inspect active

# Check queue depth
redis-cli llen celery

# Purge queue (if needed)
celery -A app.core.celery_app purge

# Scale workers
sudo systemctl start packoptima-worker@{2..4}
```

---

## Support

For monitoring support:
- Email: monitoring@packoptima.ai
- Slack: #packoptima-monitoring
- Documentation: https://docs.packoptima.ai/monitoring

---

© 2024 PackOptima. All rights reserved.
