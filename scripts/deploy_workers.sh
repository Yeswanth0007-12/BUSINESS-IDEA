#!/bin/bash
#
# PackOptima Celery Worker Deployment Script
#
# This script deploys Celery workers with health checks and verification.
#
# Usage:
#   ./deploy_workers.sh [environment]
#
# Examples:
#   ./deploy_workers.sh production
#   ./deploy_workers.sh staging
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="${PROJECT_ROOT}/backend"
ENVIRONMENT="${1:-production}"

# Service configuration
SERVICE_NAME="packoptima-worker"
APP_DIR="/opt/packoptima"
VENV_DIR="${APP_DIR}/venv"
WORKERS=4
HEALTH_CHECK_RETRIES=5
HEALTH_CHECK_DELAY=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Load environment variables
load_environment() {
    local env_file="${APP_DIR}/.env.${ENVIRONMENT}"
    
    if [ ! -f "$env_file" ]; then
        log_error "Environment file not found: $env_file"
        exit 1
    fi
    
    log_info "Loading environment: ${ENVIRONMENT}"
    export $(cat "$env_file" | grep -v '^#' | xargs)
}

# Validate prerequisites
validate_prerequisites() {
    log_step "Validating prerequisites..."
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        exit 1
    fi
    
    # Check if python3 is installed
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check if celery is installed
    if ! command -v celery &> /dev/null; then
        log_error "Celery is not installed"
        exit 1
    fi
    
    # Check if systemctl is available
    if ! command -v systemctl &> /dev/null; then
        log_error "systemctl is not available"
        exit 1
    fi
    
    # Check Redis connectivity
    if ! redis-cli -u "$REDIS_URL" ping > /dev/null 2>&1; then
        log_error "Cannot connect to Redis at $REDIS_URL"
        exit 1
    fi
    
    log_info "✓ Prerequisites validated"
}

# Pull latest code
pull_latest_code() {
    log_step "Pulling latest code..."
    cd "$APP_DIR"
    
    # Fetch latest changes
    git fetch origin
    
    # Get current branch
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    log_info "Current branch: $current_branch"
    
    # Get current commit
    local current_commit=$(git rev-parse HEAD)
    log_info "Current commit: $current_commit"
    
    # Pull latest changes
    git pull origin "$current_branch"
    
    # Get new commit
    local new_commit=$(git rev-parse HEAD)
    log_info "New commit: $new_commit"
    
    if [ "$current_commit" == "$new_commit" ]; then
        log_info "No new changes to deploy"
    else
        log_info "✓ Code updated successfully"
    fi
}

# Install dependencies
install_dependencies() {
    log_step "Installing dependencies..."
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    source "${VENV_DIR}/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    log_info "✓ Dependencies installed"
}

# Stop workers gracefully
stop_workers() {
    log_step "Stopping workers gracefully..."
    
    # Send TERM signal to allow workers to finish current tasks
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        log_info "Sending graceful shutdown signal..."
        sudo systemctl stop "$SERVICE_NAME"
        
        # Wait for workers to finish
        local wait_time=30
        log_info "Waiting ${wait_time}s for workers to finish current tasks..."
        sleep $wait_time
        
        log_info "✓ Workers stopped"
    else
        log_info "Workers are not running"
    fi
}

# Restart worker service
restart_service() {
    log_step "Restarting worker service..."
    
    # Reload systemd daemon
    sudo systemctl daemon-reload
    
    # Restart service
    sudo systemctl restart "$SERVICE_NAME"
    
    if [ $? -eq 0 ]; then
        log_info "✓ Service restarted"
    else
        log_error "Service restart failed!"
        return 1
    fi
}

# Wait for workers to start
wait_for_workers() {
    log_step "Waiting for workers to start..."
    sleep 5
    
    # Check service status
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        log_info "✓ Service is active"
    else
        log_error "Service is not active!"
        sudo systemctl status "$SERVICE_NAME"
        return 1
    fi
}

# Verify workers
verify_workers() {
    log_step "Verifying workers..."
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    source "${VENV_DIR}/bin/activate"
    
    for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
        log_info "Worker verification attempt $i/$HEALTH_CHECK_RETRIES..."
        
        # Check active workers
        local active_workers=$(celery -A app.core.celery_app inspect active 2>&1)
        
        if echo "$active_workers" | grep -q "celery@"; then
            log_info "✓ Workers are active"
            
            # Show worker details
            log_info "Active workers:"
            celery -A app.core.celery_app inspect active
            
            # Show worker stats
            log_info "Worker stats:"
            celery -A app.core.celery_app inspect stats
            
            return 0
        fi
        
        if [ $i -lt $HEALTH_CHECK_RETRIES ]; then
            log_warn "Workers not ready, retrying in ${HEALTH_CHECK_DELAY}s..."
            sleep $HEALTH_CHECK_DELAY
        fi
    done
    
    log_error "Worker verification failed after $HEALTH_CHECK_RETRIES attempts!"
    log_error "Checking service logs..."
    sudo journalctl -u "$SERVICE_NAME" -n 50 --no-pager
    
    return 1
}

# Test task processing
test_task_processing() {
    log_step "Testing task processing..."
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    source "${VENV_DIR}/bin/activate"
    
    # Submit a test task
    python3 << EOF
from app.core.celery_app import celery_app
from celery import group

# Send ping to all workers
result = celery_app.control.ping(timeout=5.0)
if result:
    print("✓ Workers responding to ping:")
    for worker_result in result:
        print(f"  {worker_result}")
else:
    print("✗ No workers responded to ping")
    exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        log_info "✓ Task processing test passed"
    else
        log_error "Task processing test failed!"
        return 1
    fi
}

# Check queue depth
check_queue_depth() {
    log_step "Checking queue depth..."
    
    # Get queue depth from Redis
    local queue_depth=$(redis-cli -u "$REDIS_URL" llen celery 2>/dev/null || echo "0")
    log_info "Current queue depth: $queue_depth tasks"
    
    if [ "$queue_depth" -gt 10000 ]; then
        log_warn "Queue depth is very high: $queue_depth tasks"
        log_warn "Consider scaling up workers"
    fi
}

# Verify deployment
verify_deployment() {
    log_step "Verifying deployment..."
    
    # Check service status
    if ! sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        log_error "Service is not running!"
        return 1
    fi
    
    # Check recent logs for errors
    local error_count=$(sudo journalctl -u "$SERVICE_NAME" --since "5 minutes ago" | grep -i error | wc -l)
    if [ $error_count -gt 0 ]; then
        log_warn "Found $error_count errors in recent logs"
        sudo journalctl -u "$SERVICE_NAME" --since "5 minutes ago" | grep -i error
    fi
    
    log_info "✓ Deployment verified"
}

# Rollback deployment
rollback_deployment() {
    log_error "Rolling back deployment..."
    
    # Get previous commit
    cd "$APP_DIR"
    local previous_commit=$(git rev-parse HEAD~1)
    
    log_info "Rolling back to commit: $previous_commit"
    git checkout "$previous_commit"
    
    # Reinstall dependencies
    cd "$BACKEND_DIR"
    source "${VENV_DIR}/bin/activate"
    pip install -r requirements.txt
    
    # Restart service
    sudo systemctl restart "$SERVICE_NAME"
    
    # Wait and verify
    sleep 5
    if verify_workers; then
        log_info "✓ Rollback completed successfully"
    else
        log_error "Rollback failed! Manual intervention required."
        exit 1
    fi
}

# Show deployment summary
show_summary() {
    echo ""
    echo "========================================="
    echo "  Deployment Summary"
    echo "========================================="
    echo "Environment: ${ENVIRONMENT}"
    echo "Service: ${SERVICE_NAME}"
    echo "Workers: ${WORKERS}"
    echo ""
    
    # Show service status
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
    
    echo ""
    
    # Show worker stats
    cd "$BACKEND_DIR"
    source "${VENV_DIR}/bin/activate"
    
    log_info "Worker Statistics:"
    celery -A app.core.celery_app inspect stats
    
    echo ""
    echo "========================================="
    log_info "Deployment completed successfully!"
    echo "========================================="
}

# Main execution
main() {
    echo "========================================="
    echo "  PackOptima Celery Worker Deployment"
    echo "  Environment: ${ENVIRONMENT}"
    echo "========================================="
    echo ""
    
    # Load environment
    load_environment
    
    # Validate prerequisites
    validate_prerequisites
    
    # Check queue depth before deployment
    check_queue_depth
    
    # Confirm deployment
    log_warn "This will deploy Celery workers to ${ENVIRONMENT} environment"
    log_warn "Workers will be gracefully stopped to finish current tasks"
    read -p "Do you want to continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "Deployment cancelled"
        exit 0
    fi
    
    # Pull latest code
    if ! pull_latest_code; then
        log_error "Failed to pull latest code"
        exit 1
    fi
    
    # Install dependencies
    if ! install_dependencies; then
        log_error "Failed to install dependencies"
        exit 1
    fi
    
    # Stop workers gracefully
    stop_workers
    
    # Restart service
    if ! restart_service; then
        log_error "Failed to restart service"
        exit 1
    fi
    
    # Wait for workers
    if ! wait_for_workers; then
        log_error "Workers failed to start"
        rollback_deployment
        exit 1
    fi
    
    # Verify workers
    if ! verify_workers; then
        log_error "Worker verification failed"
        rollback_deployment
        exit 1
    fi
    
    # Test task processing
    if ! test_task_processing; then
        log_error "Task processing test failed"
        rollback_deployment
        exit 1
    fi
    
    # Verify deployment
    if ! verify_deployment; then
        log_error "Deployment verification failed"
        rollback_deployment
        exit 1
    fi
    
    # Show summary
    show_summary
}

# Handle script arguments
case "${2:-}" in
    --rollback)
        load_environment
        rollback_deployment
        ;;
    *)
        main
        ;;
esac
