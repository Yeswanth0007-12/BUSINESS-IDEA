#!/bin/bash
#
# PackOptima Staging Validation Script
#
# This script validates the staging deployment by running comprehensive checks
# on all system components, functionality, performance, and monitoring.
#
# Usage:
#   ./validate_staging.sh
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="${PROJECT_ROOT}/backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

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

log_check() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

# Check result tracking
check_passed() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    echo -e "${GREEN}✓${NC} $1"
}

check_failed() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    echo -e "${RED}✗${NC} $1"
}

check_warning() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    WARNING_CHECKS=$((WARNING_CHECKS + 1))
    echo -e "${YELLOW}⚠${NC} $1"
}

# Load environment
load_environment() {
    local env_file="${BACKEND_DIR}/.env.staging"
    
    if [ ! -f "$env_file" ]; then
        log_error "Staging environment file not found: $env_file"
        exit 1
    fi
    
    export $(cat "$env_file" | grep -v '^#' | xargs)
}

# Infrastructure checks
check_infrastructure() {
    echo ""
    log_check "=== Infrastructure Checks ==="
    echo ""
    
    # Database connectivity
    log_check "Checking database connectivity..."
    if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
        check_passed "Database connection successful"
    else
        check_failed "Cannot connect to database"
    fi
    
    # Redis connectivity
    log_check "Checking Redis connectivity..."
    if redis-cli -u "$REDIS_URL" ping > /dev/null 2>&1; then
        check_passed "Redis connection successful"
    else
        check_failed "Cannot connect to Redis"
    fi
    
    # Prometheus
    log_check "Checking Prometheus..."
    if curl -f -s "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
        check_passed "Prometheus is healthy"
    else
        check_warning "Prometheus is not accessible"
    fi
    
    # Grafana
    log_check "Checking Grafana..."
    if curl -f -s "http://localhost:3000/api/health" > /dev/null 2>&1; then
        check_passed "Grafana is healthy"
    else
        check_warning "Grafana is not accessible"
    fi
    
    # AlertManager
    log_check "Checking AlertManager..."
    if curl -f -s "http://localhost:9093/-/healthy" > /dev/null 2>&1; then
        check_passed "AlertManager is healthy"
    else
        check_warning "AlertManager is not accessible"
    fi
}

# Service checks
check_services() {
    echo ""
    log_check "=== Service Checks ==="
    echo ""
    
    local api_url="${API_URL:-http://localhost:8000}"
    
    # API health
    log_check "Checking API health..."
    if curl -f -s "${api_url}/health" > /dev/null 2>&1; then
        check_passed "API is healthy"
        
        local health_response=$(curl -s "${api_url}/health")
        log_info "Health response: $health_response"
    else
        check_failed "API health check failed"
    fi
    
    # API docs
    log_check "Checking API documentation..."
    if curl -f -s "${api_url}/docs" > /dev/null 2>&1; then
        check_passed "API documentation accessible"
    else
        check_warning "API documentation not accessible"
    fi
    
    # Metrics endpoint
    log_check "Checking metrics endpoint..."
    if curl -f -s "${api_url}/metrics" > /dev/null 2>&1; then
        check_passed "Metrics endpoint accessible"
        
        # Check for key metrics
        local metrics=$(curl -s "${api_url}/metrics")
        
        if echo "$metrics" | grep -q "http_requests_total"; then
            check_passed "HTTP request metrics present"
        else
            check_warning "HTTP request metrics not found"
        fi
        
        if echo "$metrics" | grep -q "celery_tasks_total"; then
            check_passed "Celery task metrics present"
        else
            check_warning "Celery task metrics not found"
        fi
    else
        check_warning "Metrics endpoint not accessible"
    fi
    
    # Celery workers
    log_check "Checking Celery workers..."
    cd "$BACKEND_DIR"
    
    local worker_check=$(celery -A app.core.celery_app inspect active 2>&1 || echo "error")
    if echo "$worker_check" | grep -q "celery@"; then
        check_passed "Celery workers are active"
        
        # Count workers
        local worker_count=$(echo "$worker_check" | grep -c "celery@" || echo "0")
        log_info "Active workers: $worker_count"
    else
        check_failed "Celery workers are not active"
    fi
    
    # Queue depth
    log_check "Checking queue depth..."
    local queue_depth=$(redis-cli -u "$REDIS_URL" llen celery 2>/dev/null || echo "0")
    log_info "Queue depth: $queue_depth tasks"
    
    if [ "$queue_depth" -lt 1000 ]; then
        check_passed "Queue depth is normal"
    else
        check_warning "Queue depth is high: $queue_depth tasks"
    fi
}

# Functional checks
check_functionality() {
    echo ""
    log_check "=== Functional Checks ==="
    echo ""
    
    local api_url="${API_URL:-http://localhost:8000}"
    
    # Authentication endpoint
    log_check "Checking authentication endpoint..."
    local auth_status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${api_url}/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"test"}')
    
    if [ "$auth_status" == "401" ] || [ "$auth_status" == "422" ]; then
        check_passed "Authentication endpoint responding (status: $auth_status)"
    else
        check_warning "Authentication endpoint returned unexpected status: $auth_status"
    fi
    
    # Products endpoint
    log_check "Checking products endpoint..."
    local products_status=$(curl -s -o /dev/null -w "%{http_code}" "${api_url}/api/v1/products")
    
    if [ "$products_status" == "401" ] || [ "$products_status" == "200" ]; then
        check_passed "Products endpoint accessible (status: $products_status)"
    else
        check_warning "Products endpoint returned unexpected status: $products_status"
    fi
    
    # Boxes endpoint
    log_check "Checking boxes endpoint..."
    local boxes_status=$(curl -s -o /dev/null -w "%{http_code}" "${api_url}/api/v1/boxes")
    
    if [ "$boxes_status" == "401" ] || [ "$boxes_status" == "200" ]; then
        check_passed "Boxes endpoint accessible (status: $boxes_status)"
    else
        check_warning "Boxes endpoint returned unexpected status: $boxes_status"
    fi
    
    # Analytics endpoint
    log_check "Checking analytics endpoint..."
    local analytics_status=$(curl -s -o /dev/null -w "%{http_code}" "${api_url}/api/v1/analytics/summary")
    
    if [ "$analytics_status" == "401" ] || [ "$analytics_status" == "200" ]; then
        check_passed "Analytics endpoint accessible (status: $analytics_status)"
    else
        check_warning "Analytics endpoint returned unexpected status: $analytics_status"
    fi
}

# Performance checks
check_performance() {
    echo ""
    log_check "=== Performance Checks ==="
    echo ""
    
    local api_url="${API_URL:-http://localhost:8000}"
    
    # Health endpoint response time
    log_check "Checking health endpoint response time..."
    local health_time=$(curl -s -o /dev/null -w "%{time_total}" "${api_url}/health")
    local health_time_ms=$(echo "$health_time * 1000" | bc)
    
    log_info "Health endpoint response time: ${health_time_ms}ms"
    
    if (( $(echo "$health_time < 0.1" | bc -l) )); then
        check_passed "Health endpoint response time < 100ms"
    else
        check_warning "Health endpoint response time > 100ms"
    fi
    
    # Docs endpoint response time
    log_check "Checking docs endpoint response time..."
    local docs_time=$(curl -s -o /dev/null -w "%{time_total}" "${api_url}/docs")
    local docs_time_ms=$(echo "$docs_time * 1000" | bc)
    
    log_info "Docs endpoint response time: ${docs_time_ms}ms"
    
    if (( $(echo "$docs_time < 2.0" | bc -l) )); then
        check_passed "Docs endpoint response time < 2s"
    else
        check_warning "Docs endpoint response time > 2s"
    fi
}

# Database checks
check_database() {
    echo ""
    log_check "=== Database Checks ==="
    echo ""
    
    # Migration version
    log_check "Checking migration version..."
    cd "$BACKEND_DIR"
    local migration_version=$(alembic current 2>&1 | grep -oP '[a-f0-9]{12}' | head -1 || echo "unknown")
    log_info "Current migration version: $migration_version"
    
    if [ "$migration_version" != "unknown" ]; then
        check_passed "Migration version identified"
    else
        check_warning "Could not identify migration version"
    fi
    
    # Table counts
    log_check "Checking database tables..."
    local table_count=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'" 2>/dev/null || echo "0")
    log_info "Database tables: $table_count"
    
    if [ "$table_count" -gt 10 ]; then
        check_passed "Database has expected tables"
    else
        check_warning "Database may be missing tables"
    fi
    
    # Connection pool
    log_check "Checking database connections..."
    local active_connections=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM pg_stat_activity WHERE datname = current_database()" 2>/dev/null || echo "0")
    log_info "Active connections: $active_connections"
    
    if [ "$active_connections" -lt 50 ]; then
        check_passed "Database connections within limits"
    else
        check_warning "High number of database connections: $active_connections"
    fi
}

# Security checks
check_security() {
    echo ""
    log_check "=== Security Checks ==="
    echo ""
    
    # Environment variables
    log_check "Checking security environment variables..."
    
    if [ -n "${API_SECRET_KEY:-}" ] && [ "${#API_SECRET_KEY}" -ge 32 ]; then
        check_passed "API_SECRET_KEY is set and strong"
    else
        check_failed "API_SECRET_KEY is not set or too weak"
    fi
    
    if [ -n "${JWT_SECRET_KEY:-}" ] && [ "${#JWT_SECRET_KEY}" -ge 32 ]; then
        check_passed "JWT_SECRET_KEY is set and strong"
    else
        check_failed "JWT_SECRET_KEY is not set or too weak"
    fi
    
    # HTTPS enforcement
    log_check "Checking HTTPS configuration..."
    if [ "${ENABLE_SECURITY_HEADERS:-false}" == "true" ]; then
        check_passed "Security headers enabled"
    else
        check_warning "Security headers not enabled"
    fi
    
    # Debug mode
    log_check "Checking debug mode..."
    if [ "${DEBUG:-true}" == "false" ]; then
        check_passed "Debug mode is disabled"
    else
        check_failed "Debug mode is enabled in staging!"
    fi
}

# Monitoring checks
check_monitoring() {
    echo ""
    log_check "=== Monitoring Checks ==="
    echo ""
    
    # Prometheus targets
    log_check "Checking Prometheus targets..."
    if curl -f -s "http://localhost:9090/api/v1/targets" > /dev/null 2>&1; then
        local targets=$(curl -s "http://localhost:9090/api/v1/targets" | grep -o '"health":"up"' | wc -l)
        log_info "Active Prometheus targets: $targets"
        
        if [ "$targets" -gt 0 ]; then
            check_passed "Prometheus has active targets"
        else
            check_warning "No active Prometheus targets"
        fi
    else
        check_warning "Cannot check Prometheus targets"
    fi
    
    # Grafana datasources
    log_check "Checking Grafana datasources..."
    if curl -f -s "http://localhost:3000/api/datasources" > /dev/null 2>&1; then
        check_passed "Grafana datasources accessible"
    else
        check_warning "Cannot check Grafana datasources"
    fi
    
    # Alert rules
    log_check "Checking alert rules..."
    if curl -f -s "http://localhost:9090/api/v1/rules" > /dev/null 2>&1; then
        local rules=$(curl -s "http://localhost:9090/api/v1/rules" | grep -o '"name"' | wc -l)
        log_info "Configured alert rules: $rules"
        
        if [ "$rules" -gt 0 ]; then
            check_passed "Alert rules configured"
        else
            check_warning "No alert rules configured"
        fi
    else
        check_warning "Cannot check alert rules"
    fi
}

# Generate report
generate_report() {
    echo ""
    echo "========================================="
    echo "  Staging Validation Report"
    echo "========================================="
    echo ""
    echo "Total Checks: $TOTAL_CHECKS"
    echo -e "${GREEN}Passed: $PASSED_CHECKS${NC}"
    echo -e "${YELLOW}Warnings: $WARNING_CHECKS${NC}"
    echo -e "${RED}Failed: $FAILED_CHECKS${NC}"
    echo ""
    
    local pass_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    echo "Pass Rate: ${pass_rate}%"
    echo ""
    
    if [ "$FAILED_CHECKS" -eq 0 ]; then
        echo -e "${GREEN}✓ Staging validation PASSED${NC}"
        echo ""
        echo "The staging environment is ready for use."
        echo "Continue monitoring for 24 hours before production deployment."
        return 0
    else
        echo -e "${RED}✗ Staging validation FAILED${NC}"
        echo ""
        echo "Please address the failed checks before proceeding."
        echo "Review the output above for details."
        return 1
    fi
}

# Main execution
main() {
    echo ""
    echo "========================================="
    echo "  PackOptima Staging Validation"
    echo "  $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================="
    echo ""
    
    # Load environment
    log_info "Loading staging environment..."
    load_environment
    
    # Run all checks
    check_infrastructure
    check_services
    check_functionality
    check_performance
    check_database
    check_security
    check_monitoring
    
    # Generate report
    generate_report
}

# Run main
main
