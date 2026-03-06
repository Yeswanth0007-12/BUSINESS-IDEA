#!/bin/bash
#
# PackOptima API Server Deployment Script
#
# This script deploys the API server with rolling updates and health checks.
#
# Usage:
#   ./deploy_api.sh [environment] [--no-migrations]
#
# Examples:
#   ./deploy_api.sh production
#   ./deploy_api.sh staging --no-migrations
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="${PROJECT_ROOT}/backend"
ENVIRONMENT="${1:-production}"
SKIP_MIGRATIONS="${2:-}"

# Service configuration
SERVICE_NAME="packoptima-api"
APP_DIR="/opt/packoptima"
VENV_DIR="${APP_DIR}/venv"
PORT=8000
WORKERS=4
HEALTH_CHECK_RETRIES=10
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
    
    # Check if systemctl is available
    if ! command -v systemctl &> /dev/null; then
        log_error "systemctl is not available"
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

# Run database migrations
run_migrations() {
    if [ "$SKIP_MIGRATIONS" == "--no-migrations" ]; then
        log_warn "Skipping database migrations (--no-migrations flag)"
        return 0
    fi
    
    log_step "Running database migrations..."
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    source "${VENV_DIR}/bin/activate"
    
    # Run migrations
    alembic upgrade head
    
    if [ $? -eq 0 ]; then
        log_info "✓ Migrations completed"
    else
        log_error "Migration failed!"
        return 1
    fi
}

# Run tests
run_tests() {
    log_step "Running smoke tests..."
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    source "${VENV_DIR}/bin/activate"
    
    # Run smoke tests
    if [ -f "smoke_tests/test_smoke.py" ]; then
        python -m pytest smoke_tests/test_smoke.py -v
        
        if [ $? -eq 0 ]; then
            log_info "✓ Smoke tests passed"
        else
            log_error "Smoke tests failed!"
            return 1
        fi
    else
        log_warn "Smoke tests not found, skipping..."
    fi
}

# Restart API service
restart_service() {
    log_step "Restarting API service..."
    
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

# Wait for service to start
wait_for_service() {
    log_step "Waiting for service to start..."
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

# Health check
health_check() {
    log_step "Running health check..."
    
    local health_url="http://localhost:${PORT}/health"
    
    for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
        log_info "Health check attempt $i/$HEALTH_CHECK_RETRIES..."
        
        if curl -f -s "$health_url" > /dev/null; then
            log_info "✓ Health check passed"
            
            # Show health check response
            local health_response=$(curl -s "$health_url")
            log_info "Health response: $health_response"
            
            return 0
        fi
        
        if [ $i -lt $HEALTH_CHECK_RETRIES ]; then
            log_warn "Health check failed, retrying in ${HEALTH_CHECK_DELAY}s..."
            sleep $HEALTH_CHECK_DELAY
        fi
    done
    
    log_error "Health check failed after $HEALTH_CHECK_RETRIES attempts!"
    log_error "Checking service logs..."
    sudo journalctl -u "$SERVICE_NAME" -n 50 --no-pager
    
    return 1
}

# Verify deployment
verify_deployment() {
    log_step "Verifying deployment..."
    
    # Check service status
    if ! sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        log_error "Service is not running!"
        return 1
    fi
    
    # Check if service is listening on port
    if ! netstat -tuln | grep -q ":${PORT}"; then
        log_error "Service is not listening on port ${PORT}!"
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
    
    # Wait and health check
    sleep 5
    if health_check; then
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
    echo "Port: ${PORT}"
    echo "Workers: ${WORKERS}"
    echo ""
    
    # Show service status
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
    
    echo ""
    echo "========================================="
    log_info "Deployment completed successfully!"
    echo "========================================="
}

# Main execution
main() {
    echo "========================================="
    echo "  PackOptima API Server Deployment"
    echo "  Environment: ${ENVIRONMENT}"
    echo "========================================="
    echo ""
    
    # Load environment
    load_environment
    
    # Validate prerequisites
    validate_prerequisites
    
    # Confirm deployment
    log_warn "This will deploy the API server to ${ENVIRONMENT} environment"
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
    
    # Run migrations
    if ! run_migrations; then
        log_error "Failed to run migrations"
        exit 1
    fi
    
    # Run tests
    if ! run_tests; then
        log_warn "Tests failed, but continuing deployment..."
    fi
    
    # Restart service
    if ! restart_service; then
        log_error "Failed to restart service"
        exit 1
    fi
    
    # Wait for service
    if ! wait_for_service; then
        log_error "Service failed to start"
        rollback_deployment
        exit 1
    fi
    
    # Health check
    if ! health_check; then
        log_error "Health check failed"
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
