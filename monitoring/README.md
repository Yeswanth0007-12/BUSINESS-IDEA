# PackOptima Monitoring Infrastructure

This directory contains the complete monitoring infrastructure for PackOptima, including Prometheus, Grafana, AlertManager, and log aggregation.

## Overview

The monitoring stack provides:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Metrics visualization with pre-built dashboards
- **AlertManager**: Alert routing and notification management
- **Loki**: Log aggregation (lightweight alternative to ELK)
- **Promtail**: Log shipping to Loki
- **Exporters**: PostgreSQL and Redis metrics exporters

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- PackOptima application running
- Network connectivity between monitoring stack and application

### Start Monitoring Stack

```bash
# Navigate to monitoring directory
cd monitoring

# Start all monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### Access Services

Once started, access the following services:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (default credentials: admin/admin)
- **AlertManager**: http://localhost:9093
- **Loki**: http://localhost:3100

## Directory Structure

```
monitoring/
├── prometheus/
│   ├── prometheus.yml          # Prometheus configuration
│   └── alerts/
│       └── packoptima.yml      # Alert rules
├── alertmanager/
│   └── alertmanager.yml        # AlertManager configuration
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/        # Data source configurations
│   │   └── dashboards/         # Dashboard provisioning
│   └── dashboards/             # Dashboard JSON files
│       ├── api-performance.json
│       ├── queue-metrics.json
│       └── database-metrics.json
├── loki/
│   └── loki-config.yml         # Loki configuration
├── promtail/
│   └── promtail-config.yml     # Promtail configuration
├── docker-compose.monitoring.yml
├── setup-monitoring.sh
└── README.md
```

## Configuration

### Prometheus

Edit `prometheus/prometheus.yml` to configure:
- Scrape intervals
- Target endpoints
- Alert rules
- Storage retention

### Grafana Dashboards

Pre-built dashboards are automatically provisioned:

1. **API Performance Dashboard**
   - Request rate
   - Response times (p50, p95, p99)
   - Error rates
   - Active connections

2. **Queue Metrics Dashboard**
   - Queue depth
   - Task processing rate
   - Task success/failure rates
   - Worker status

3. **Database Metrics Dashboard**
   - Connection pool usage
   - Query performance
   - Transaction rates
   - Cache hit ratios

### AlertManager

Configure notifications in `alertmanager/alertmanager.yml`:

```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - channel: '#packoptima-alerts'
        api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
```

Supported notification channels:
- Slack
- Email
- PagerDuty
- Webhook
- OpsGenie

## Alert Rules

Alert rules are defined in `prometheus/alerts/packoptima.yml`:

### Critical Alerts

- **APIServerDown**: API server not responding (1 minute)
- **CeleryWorkerDown**: Celery worker not responding (2 minutes)
- **HighErrorRate**: Error rate > 5% (5 minutes)

### Warning Alerts

- **HighAPIResponseTime**: p95 response time > 1s (5 minutes)
- **HighQueueDepth**: Queue depth > 1000 tasks (10 minutes)
- **HighDatabaseConnections**: DB connections > 80% of pool (5 minutes)
- **HighRedisMemory**: Redis memory > 80% of limit (5 minutes)

## Metrics Exposed

### API Metrics

```
http_requests_total                    # Total HTTP requests
http_request_duration_seconds          # Request duration histogram
http_active_connections                # Active connections
```

### Queue Metrics

```
celery_queue_length                    # Queue depth
celery_tasks_total                     # Total tasks processed
celery_task_duration_seconds           # Task duration histogram
celery_active_workers                  # Active worker count
```

### Database Metrics

```
pg_stat_database_numbackends           # Active connections
pg_stat_database_xact_commit           # Committed transactions
pg_database_size_bytes                 # Database size
```

### Redis Metrics

```
redis_memory_used_bytes                # Memory usage
redis_connected_clients                # Connected clients
redis_commands_processed_total         # Commands processed
```

## Sentry Integration

For error tracking, configure Sentry in your application:

### Installation

```bash
pip install sentry-sdk[fastapi]
```

### Configuration

Add to `backend/app/core/config.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    environment="production",
    traces_sample_rate=0.1,
    integrations=[FastApiIntegration()]
)
```

### Environment Variables

```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

## Log Aggregation

Logs are collected by Promtail and sent to Loki for aggregation.

### Viewing Logs in Grafana

1. Open Grafana (http://localhost:3000)
2. Go to Explore
3. Select "Loki" as data source
4. Use LogQL queries:

```logql
# All PackOptima logs
{job="packoptima"}

# Error logs only
{job="packoptima"} |= "ERROR"

# Logs from specific container
{container="packoptima-backend"}

# Logs with specific pattern
{job="packoptima"} |~ "optimization.*failed"
```

## Maintenance

### Backup Monitoring Data

```bash
# Backup Prometheus data
docker run --rm -v monitoring_prometheus-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup.tar.gz /data

# Backup Grafana data
docker run --rm -v monitoring_grafana-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/grafana-backup.tar.gz /data
```

### Update Services

```bash
# Pull latest images
docker-compose -f docker-compose.monitoring.yml pull

# Restart services
docker-compose -f docker-compose.monitoring.yml up -d
```

### Clean Up Old Data

Prometheus and Loki automatically clean up old data based on retention settings:

- Prometheus: 30 days (configurable in prometheus.yml)
- Loki: 30 days (configurable in loki-config.yml)

## Troubleshooting

### Prometheus Not Scraping Targets

1. Check target configuration in `prometheus/prometheus.yml`
2. Verify network connectivity: `docker network inspect monitoring`
3. Check Prometheus logs: `docker logs packoptima-prometheus`

### Grafana Dashboards Not Loading

1. Verify data source configuration
2. Check Prometheus is accessible from Grafana
3. Review Grafana logs: `docker logs packoptima-grafana`

### Alerts Not Firing

1. Check alert rules in Prometheus UI (http://localhost:9090/alerts)
2. Verify AlertManager configuration
3. Test alert routing: `amtool check-config alertmanager.yml`

### High Memory Usage

1. Reduce Prometheus retention period
2. Decrease scrape frequency
3. Limit number of metrics collected

## Performance Tuning

### Prometheus

```yaml
# Adjust scrape intervals
global:
  scrape_interval: 30s  # Increase for less frequent scraping
  
# Reduce retention
storage:
  tsdb:
    retention.time: 15d  # Reduce from 30d
```

### Loki

```yaml
# Adjust retention
limits_config:
  retention_period: 360h  # 15 days instead of 30
```

## Security

### Change Default Passwords

```bash
# Grafana
docker exec -it packoptima-grafana grafana-cli admin reset-admin-password <new-password>
```

### Enable Authentication

Configure authentication in `grafana/provisioning/datasources/prometheus.yml`:

```yaml
datasources:
  - name: Prometheus
    basicAuth: true
    basicAuthUser: admin
    secureJsonData:
      basicAuthPassword: your-password
```

### Network Isolation

Use Docker networks to isolate monitoring stack:

```yaml
networks:
  monitoring:
    internal: true  # No external access
```

## Support

For monitoring support:
- Documentation: [docs/MONITORING_SETUP_GUIDE.md](../docs/MONITORING_SETUP_GUIDE.md)
- Issues: Create an issue in the repository
- Email: monitoring@packoptima.ai

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [AlertManager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
