# Monitoring Quick Start Guide

Get PackOptima monitoring up and running in 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- PackOptima application running

## Step 1: Start Monitoring Stack (2 minutes)

```bash
# Navigate to monitoring directory
cd monitoring

# Start all services
docker-compose -f docker-compose.monitoring.yml up -d

# Verify services are running
docker-compose -f docker-compose.monitoring.yml ps
```

Expected output:
```
NAME                              STATUS
packoptima-prometheus             Up
packoptima-grafana                Up
packoptima-alertmanager           Up
packoptima-loki                   Up
packoptima-promtail               Up
packoptima-postgres-exporter      Up
packoptima-redis-exporter         Up
```

## Step 2: Access Dashboards (1 minute)

Open in your browser:

1. **Grafana**: http://localhost:3000
   - Username: `admin`
   - Password: `admin`
   - Change password when prompted

2. **Prometheus**: http://localhost:9090
   - No authentication required (configure in production)

3. **AlertManager**: http://localhost:9093
   - No authentication required (configure in production)

## Step 3: View Pre-built Dashboards (1 minute)

In Grafana:

1. Click "Dashboards" in the left sidebar
2. You'll see three pre-built dashboards:
   - **PackOptima API Performance**
   - **PackOptima Queue Metrics**
   - **PackOptima Database Metrics**

3. Click on any dashboard to view metrics

## Step 4: Verify Metrics Collection (1 minute)

### Check Prometheus Targets

1. Open Prometheus: http://localhost:9090
2. Go to **Status** → **Targets**
3. Verify all targets show "UP" status:
   - packoptima-api
   - packoptima-workers
   - postgresql
   - redis

### Check Metrics in Grafana

1. Open Grafana: http://localhost:3000
2. Open "PackOptima API Performance" dashboard
3. You should see:
   - Request rate graphs
   - Response time metrics
   - Error rate charts

If you see "No data", wait 1-2 minutes for metrics to be collected.

## Step 5: Test Alerting (Optional)

### View Alert Rules

1. Open Prometheus: http://localhost:9090
2. Go to **Alerts**
3. You'll see configured alert rules:
   - HighAPIResponseTime
   - HighErrorRate
   - HighQueueDepth
   - CeleryWorkerDown
   - APIServerDown

### Trigger Test Alert

```bash
# Simulate high error rate
for i in {1..50}; do
  curl http://localhost:8000/api/v1/nonexistent-endpoint
done
```

Wait 5 minutes, then check:
1. Prometheus Alerts page - alert should be "Firing"
2. AlertManager UI - alert should appear

## Common Issues

### Services Not Starting

```bash
# Check logs
docker-compose -f docker-compose.monitoring.yml logs

# Restart services
docker-compose -f docker-compose.monitoring.yml restart
```

### No Metrics in Grafana

1. Check Prometheus is scraping targets:
   - Open http://localhost:9090/targets
   - All should show "UP"

2. Check data source in Grafana:
   - Go to Configuration → Data Sources
   - Click "Prometheus"
   - Click "Test" - should show "Data source is working"

### Can't Access Grafana

```bash
# Check if Grafana is running
docker ps | grep grafana

# Check Grafana logs
docker logs packoptima-grafana

# Restart Grafana
docker-compose -f docker-compose.monitoring.yml restart grafana
```

## Next Steps

1. **Configure Alerts**: Edit `prometheus/alerts/packoptima.yml`
2. **Set Up Notifications**: Configure Slack/email in `alertmanager/alertmanager.yml`
3. **Customize Dashboards**: Create custom dashboards in Grafana
4. **Add Sentry**: Set up error tracking (see INTEGRATION_GUIDE.md)
5. **Production Setup**: Follow security best practices in README.md

## Quick Commands

```bash
# Start monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Stop monitoring
docker-compose -f docker-compose.monitoring.yml down

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f

# Restart all services
docker-compose -f docker-compose.monitoring.yml restart

# Update services
docker-compose -f docker-compose.monitoring.yml pull
docker-compose -f docker-compose.monitoring.yml up -d
```

## Support

- Full Documentation: [README.md](README.md)
- Integration Guide: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- Setup Guide: [../docs/MONITORING_SETUP_GUIDE.md](../docs/MONITORING_SETUP_GUIDE.md)

---

**Congratulations!** Your monitoring infrastructure is now running. 🎉

For production deployment, see the full [README.md](README.md) for security and performance tuning.
