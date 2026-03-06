#!/bin/bash

# PackOptima Monitoring Infrastructure Setup Script
# This script sets up Prometheus, Grafana, AlertManager, and log aggregation

set -e

echo "========================================="
echo "PackOptima Monitoring Infrastructure Setup"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p prometheus/alerts
mkdir -p alertmanager
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards
mkdir -p grafana/dashboards
mkdir -p loki
mkdir -p promtail

# Set permissions
echo "Setting permissions..."
chmod -R 755 prometheus alertmanager grafana loki promtail

# Start monitoring stack
echo ""
echo "Starting monitoring stack..."
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo ""
echo "Waiting for services to start..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

# Check Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null; then
    echo "✓ Prometheus is healthy"
else
    echo "✗ Prometheus is not responding"
fi

# Check Grafana
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✓ Grafana is healthy"
else
    echo "✗ Grafana is not responding"
fi

# Check AlertManager
if curl -s http://localhost:9093/-/healthy > /dev/null; then
    echo "✓ AlertManager is healthy"
else
    echo "✗ AlertManager is not responding"
fi

# Check Loki
if curl -s http://localhost:3100/ready > /dev/null; then
    echo "✓ Loki is healthy"
else
    echo "✗ Loki is not responding"
fi

echo ""
echo "========================================="
echo "Monitoring Infrastructure Setup Complete!"
echo "========================================="
echo ""
echo "Access the following services:"
echo "  - Prometheus:    http://localhost:9090"
echo "  - Grafana:       http://localhost:3000 (admin/admin)"
echo "  - AlertManager:  http://localhost:9093"
echo "  - Loki:          http://localhost:3100"
echo ""
echo "Next steps:"
echo "  1. Configure AlertManager notifications (Slack, email, PagerDuty)"
echo "  2. Set up Sentry for error tracking"
echo "  3. Import additional Grafana dashboards"
echo "  4. Configure alert rules in prometheus/alerts/"
echo ""
echo "For more information, see docs/MONITORING_SETUP_GUIDE.md"
echo ""
