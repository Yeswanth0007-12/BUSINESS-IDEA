#!/bin/bash
# Celery worker startup script for PackOptima

echo "Starting Celery worker for PackOptima..."

# Set Python path to include backend directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Celery worker with optimization queue
celery -A app.core.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --queues=optimization,bulk \
    --max-tasks-per-child=100 \
    --time-limit=300 \
    --soft-time-limit=240

# Notes:
# - concurrency=4: Run 4 worker processes
# - max-tasks-per-child=100: Restart worker after 100 tasks to prevent memory leaks
# - time-limit=300: Hard timeout of 5 minutes per task
# - soft-time-limit=240: Soft timeout of 4 minutes (allows graceful cleanup)
# - queues: Listen to optimization and bulk queues
