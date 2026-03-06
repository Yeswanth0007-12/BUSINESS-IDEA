#!/bin/bash

################################################################################
# Production Validation Script for PackOptima
#
# This script performs comprehensive validation of the production deployment
# to ensure all systems are functioning correctly.
#
# Usage: bash scripts/validate_production.sh
################################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
API_URL="${API_URL:-http://localhost:8000}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3001}"

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✓${NC} $1"
    ((PASSED_CHECKS++))
}

log_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ✗${NC} $1"
    ((FAILED_CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠${NC} $1"
    ((WARNING_CHECKS++))
}

check() {
    ((TOTAL_CHECKS++))
}

################################################################################
# API Health Checks
################################################################################

validate_api_health() {
    log "========================================="
    log "Validating API Health"
    log "========================================="
    
    # Health endpoint
    check
    log "Checking API health endpoint..."
    if curl -f -s "$API_URL/health" >/dev/null 2>&1; then
        log_success "API health endpoint responding"
    else
        log_error "API health endpoint not responding"
    fi
    
    # Docs endpoint
    check
    log "Checking API documentation..."
    if curl -f -s "$API_URL/docs" >/dev/null 2>&1; then
        log_success "API documentation accessible"
    else
        log_error "API documentation not accessible"
    fi
    
    # Metrics endpoint
    check
    log "Checking metrics endpoint..."
    if curl -f -s "$API_URL/metrics" >/dev/null 2>&1; then
        log_success "Metrics endpoint responding"
    else
        log_warning "Metrics endpoint not responding"
    fi
    
    # Response time check
    check
    log "Measuring API response time..."
    START_TIME=$(date +%s%N)
    curl -f -s "$API_URL/health" >/dev/null 2>&1
    END_TIME=$(date +%s%N)
    RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
    
    if [ $RESPONSE_TIME -lt 100 ]; then
        log_success "API response time excellent: ${RESPONSE_TIME}ms"
    elif [ $RESPONSE_TIME -lt 500 ]; then
        log_success "API response time good: ${RESPONSE_TIME}ms"
    elif [ $RESPONSE_TIME -lt 1000 ]; then
        log_warning "API response time acceptable: ${RESPONSE_TIME}ms"
    else
        log_error "API response time high: ${RESPONSE_TIME}ms"
    fi
}

################################################################################
# Database Connectivity
################################################################################

validate_database() {
    log "========================================="
    log "Validating Database Connectivity"
    log "========================================="
    
    check
    log "Checking database container..."
    if docker ps | grep -q packoptima-db-production; then
        log_success "Database container running"
    else
        log_error "Database container not found"
        return
    fi
    
    check
    log "Checking database connectivity..."
    if docker exec packoptima-db-production pg_isready -U postgres >/dev/null 2>&1; then
        log_success "Database accepting connections"
    else
        log_error "Database not accepting connections"
    fi
    
    check
    log "Checking database migrations..."
    cd "$PROJECT_ROOT/backend"
    CURRENT_VERSION=$(alembic current 2>/dev/null | grep -oP '(?<=\()[a-f0-9]+(?=\))' || echo "none")
    if [ "$CURRENT_VERSION" != "none" ]; then
        log_success "Database migrations current: $CURRENT_VERSION"
    else
        log_error "Database migrations not applied"
    fi
    cd "$PROJECT_ROOT"
}

################################################################################
# Redis Connectivity
################################################################################

validate_redis() {
    log "========================================="
    log "Validating Redis Connectivity"
    log "========================================="
    
    check
    log "Checking Redis container..."
    if docker ps | grep -q packoptima-redis-production; then
        log_success "Redis container running"
    else
        log_error "Redis container not found"
        return
    fi
    
    check
    log "Checking Redis connectivity..."
    if docker exec packoptima-redis-production redis-cli ping | grep -q PONG; then
        log_success "Redis responding to ping"
    else
        log_error "Redis not responding"
    fi
    
    check
    log "Checking Redis memory usage..."
    REDIS_MEMORY=$(docker exec packoptima-redis-production redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
    log_success "Redis memory usage: $REDIS_MEMORY"
}

################################################################################
# Celery Workers
################################################################################

validate_celery() {
    log "========================================="
    log "Validating Celery Workers"
    log "========================================="
    
    check
    log "Checking Celery worker containers..."
    WORKER_COUNT=$(docker ps | grep -c packoptima-worker-production || echo 0)
    if [ $WORKER_COUNT -gt 0 ]; then
        log_success "Celery workers running: $WORKER_COUNT"
    else
        log_error "No Celery workers found"
        return
    fi
    
    check
    log "Checking worker logs for errors..."
    ERROR_COUNT=$(docker-compose -f docker-compose.production.yml logs worker --tail=100 | grep -c ERROR || echo 0)
    if [ $ERROR_COUNT -eq 0 ]; then
        log_success "No errors in worker logs"
    else
        log_warning "Found $ERROR_COUNT errors in worker logs"
    fi
    
    check
    log "Checking worker connectivity..."
    if docker-compose -f docker-compose.production.yml logs worker --tail=50 | grep -q "celery@"; then
        log_success "Workers connected to broker"
    else
        log_warning "Worker connection status unclear"
    fi
}

################################################################################
# Monitoring Infrastructure
################################################################################

validate_monitoring() {
    log "========================================="
    log "Validating Monitoring Infrastructure"
    log "========================================="
    
    # Prometheus
    check
    log "Checking Prometheus..."
    if curl -f -s "$PROMETHEUS_URL/-/healthy" >/dev/null 2>&1; then
        log_success "Prometheus is healthy"
    else
        log_warning "Prometheus health check failed"
    fi
    
    check
    log "Checking Prometheus targets..."
    TARGETS_UP=$(curl -s "$PROMETHEUS_URL/api/v1/targets" | grep -o '"health":"up"' | wc -l || echo 0)
    if [ $TARGETS_UP -gt 0 ]; then
        log_success "Prometheus targets up: $TARGETS_UP"
    else
        log_warning "No Prometheus targets up"
    fi
    
    # Grafana
    check
    log "Checking Grafana..."
    if curl -f -s "$GRAFANA_URL/api/health" >/dev/null 2>&1; then
        log_success "Grafana is healthy"
    else
        log_warning "Grafana health check failed"
    fi
    
    # AlertManager
    check
    log "Checking AlertManager..."
    if curl -f -s "http://localhost:9093/-/healthy" >/dev/null 2>&1; then
        log_success "AlertManager is healthy"
    else
        log_warning "AlertManager health check failed"
    fi
}

################################################################################
# API Endpoints Validation
################################################################################

validate_api_endpoints() {
    log "========================================="
    log "Validating API Endpoints"
    log "========================================="
    
    # Auth endpoints
    check
    log "Checking auth endpoints..."
    if curl -f -s -X POST "$API_URL/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d '{}' 2>&1 | grep -q "422\|400"; then
        log_success "Auth endpoints responding (validation working)"
    else
        log_warning "Auth endpoints response unclear"
    fi
    
    # Products endpoint
    check
    log "Checking products endpoint..."
    if curl -s "$API_URL/api/v1/products" 2>&1 | grep -q "401\|403\|200"; then
        log_success "Products endpoint responding"
    else
        log_warning "Products endpoint response unclear"
    fi
    
    # Boxes endpoint
    check
    log "Checking boxes endpoint..."
    if curl -s "$API_URL/api/v1/boxes" 2>&1 | grep -q "401\|403\|200"; then
        log_success "Boxes endpoint responding"
    else
        log_warning "Boxes endpoint response unclear"
    fi
    
    # Optimization endpoint
    check
    log "Checking optimization endpoint..."
    if curl -s "$API_URL/api/v1/optimize" 2>&1 | grep -q "401\|403\|405\|200"; then
        log_success "Optimization endpoint responding"
    else
        log_warning "Optimization endpoint response unclear"
    fi
    
    # Analytics endpoint
    check
    log "Checking analytics endpoint..."
    if curl -s "$API_URL/api/v1/analytics/summary" 2>&1 | grep -q "401\|403\|200"; then
        log_success "Analytics endpoint responding"
    else
        log_warning "Analytics endpoint response unclear"
    fi
}

################################################################################
# Performance Metrics
################################################################################

validate_performance() {
    log "========================================="
    log "Validating Performance Metrics"
    log "========================================="
    
    # API response time (already checked above, but let's do more endpoints)
    check
    log "Measuring /docs response time..."
    START_TIME=$(date +%s%N)
    curl -f -s "$API_URL/docs" >/dev/null 2>&1
    END_TIME=$(date +%s%N)
    DOCS_TIME=$(( (END_TIME - START_TIME) / 1000000 ))
    
    if [ $DOCS_TIME -lt 500 ]; then
        log_success "Docs response time: ${DOCS_TIME}ms"
    else
        log_warning "Docs response time high: ${DOCS_TIME}ms"
    fi
    
    # Check CPU usage
    check
    log "Checking API container CPU usage..."
    API_CPU=$(docker stats --no-stream --format "{{.CPUPerc}}" packoptima-api-production 2>/dev/null | sed 's/%//' || echo "0")
    if [ -n "$API_CPU" ]; then
        if (( $(echo "$API_CPU < 80" | bc -l) )); then
            log_success "API CPU usage: ${API_CPU}%"
        else
            log_warning "API CPU usage high: ${API_CPU}%"
        fi
    else
        log_warning "Could not measure API CPU usage"
    fi
    
    # Check memory usage
    check
    log "Checking API container memory usage..."
    API_MEM=$(docker stats --no-stream --format "{{.MemPerc}}" packoptima-api-production 2>/dev/null | sed 's/%//' || echo "0")
    if [ -n "$API_MEM" ]; then
        if (( $(echo "$API_MEM < 80" | bc -l) )); then
            log_success "API memory usage: ${API_MEM}%"
        else
            log_warning "API memory usage high: ${API_MEM}%"
        fi
    else
        log_warning "Could not measure API memory usage"
    fi
}

################################################################################
# Security Checks
################################################################################

validate_security() {
    log "========================================="
    log "Validating Security Configuration"
    log "========================================="
    
    # Check HTTPS redirect (if applicable)
    check
    log "Checking security headers..."
    HEADERS=$(curl -s -I "$API_URL/health" || echo "")
    if echo "$HEADERS" | grep -q "X-Content-Type-Options"; then
        log_success "Security headers present"
    else
        log_warning "Security headers not found"
    fi
    
    # Check authentication requirement
    check
    log "Checking authentication enforcement..."
    if curl -s "$API_URL/api/v1/products" 2>&1 | grep -q "401\|403"; then
        log_success "Authentication enforced on protected endpoints"
    else
        log_warning "Authentication enforcement unclear"
    fi
    
    # Check rate limiting
    check
    log "Checking rate limiting..."
    RATE_LIMIT_HEADER=$(curl -s -I "$API_URL/health" | grep -i "X-RateLimit" || echo "")
    if [ -n "$RATE_LIMIT_HEADER" ]; then
        log_success "Rate limiting configured"
    else
        log_warning "Rate limiting headers not found"
    fi
}

################################################################################
# Log Analysis
################################################################################

validate_logs() {
    log "========================================="
    log "Validating Application Logs"
    log "========================================="
    
    # Check for errors in API logs
    check
    log "Checking API logs for errors..."
    API_ERRORS=$(docker-compose -f docker-compose.production.yml logs api --tail=100 | grep -c ERROR || echo 0)
    if [ $API_ERRORS -eq 0 ]; then
        log_success "No errors in API logs"
    else
        log_warning "Found $API_ERRORS errors in API logs"
    fi
    
    # Check for warnings
    check
    log "Checking API logs for warnings..."
    API_WARNINGS=$(docker-compose -f docker-compose.production.yml logs api --tail=100 | grep -c WARNING || echo 0)
    if [ $API_WARNINGS -lt 5 ]; then
        log_success "Minimal warnings in API logs: $API_WARNINGS"
    else
        log_warning "Found $API_WARNINGS warnings in API logs"
    fi
    
    # Check database logs
    check
    log "Checking database logs..."
    DB_ERRORS=$(docker logs packoptima-db-production --tail=100 2>&1 | grep -c ERROR || echo 0)
    if [ $DB_ERRORS -eq 0 ]; then
        log_success "No errors in database logs"
    else
        log_warning "Found $DB_ERRORS errors in database logs"
    fi
}

################################################################################
# Main Validation Flow
################################################################################

main() {
    log "========================================="
    log "PackOptima Production Validation"
    log "Started at: $(date)"
    log "========================================="
    
    # Run all validations
    validate_api_health
    validate_database
    validate_redis
    validate_celery
    validate_monitoring
    validate_api_endpoints
    validate_performance
    validate_security
    validate_logs
    
    # Summary
    log "========================================="
    log "Validation Summary"
    log "========================================="
    log "Total checks: $TOTAL_CHECKS"
    log_success "Passed: $PASSED_CHECKS"
    log_warning "Warnings: $WARNING_CHECKS"
    log_error "Failed: $FAILED_CHECKS"
    
    # Calculate success rate
    SUCCESS_RATE=$(( PASSED_CHECKS * 100 / TOTAL_CHECKS ))
    
    log ""
    if [ $FAILED_CHECKS -eq 0 ]; then
        log_success "========================================="
        log_success "VALIDATION PASSED (${SUCCESS_RATE}% success rate)"
        log_success "========================================="
        exit 0
    elif [ $FAILED_CHECKS -lt 3 ]; then
        log_warning "========================================="
        log_warning "VALIDATION PASSED WITH WARNINGS (${SUCCESS_RATE}% success rate)"
        log_warning "Review failed checks and warnings above"
        log_warning "========================================="
        exit 0
    else
        log_error "========================================="
        log_error "VALIDATION FAILED (${SUCCESS_RATE}% success rate)"
        log_error "Critical issues found - review logs above"
        log_error "========================================="
        exit 1
    fi
}

# Run validation
main "$@"
