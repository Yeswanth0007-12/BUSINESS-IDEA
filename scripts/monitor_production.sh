#!/bin/bash

################################################################################
# Production Monitoring Script for PackOptima
#
# This script provides continuous monitoring of production deployment health
# and generates periodic status reports.
#
# Usage: bash scripts/monitor_production.sh [duration_hours]
# Example: bash scripts/monitor_production.sh 24
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
DURATION_HOURS=${1:-24}
CHECK_INTERVAL=300  # 5 minutes
API_URL="${API_URL:-http://localhost:8000}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
MONITORING_LOG="$PROJECT_ROOT/logs/production_monitoring_$(date +%Y%m%d_%H%M%S).log"

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$MONITORING_LOG"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} $1" | tee -a "$MONITORING_LOG"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} $1" | tee -a "$MONITORING_LOG"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠${NC} $1" | tee -a "$MONITORING_LOG"
}

# Metrics tracking
declare -A ERROR_COUNTS
declare -A WARNING_COUNTS
declare -A RESPONSE_TIMES
CHECK_COUNT=0

################################################################################
# Health Check Functions
################################################################################

check_api_health() {
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health" 2>/dev/null || echo "000")
    
    if [ "$status_code" = "200" ]; then
        return 0
    else
        return 1
    fi
}

measure_response_time() {
    local start_time=$(date +%s%N)
    curl -f -s "$API_URL/health" >/dev/null 2>&1
    local end_time=$(date +%s%N)
    local response_time=$(( (end_time - start_time) / 1000000 ))
    echo $response_time
}

check_error_rate() {
    local error_count=$(docker-compose -f docker-compose.production.yml logs api --tail=100 --since 5m 2>/dev/null | grep -c ERROR || echo 0)
    echo $error_count
}

check_container_status() {
    local container=$1
    if docker ps | grep -q "$container"; then
        return 0
    else
        return 1
    fi
}

check_resource_usage() {
    local container=$1
    local cpu=$(docker stats --no-stream --format "{{.CPUPerc}}" "$container" 2>/dev/null | sed 's/%//' || echo "0")
    local mem=$(docker stats --no-stream --format "{{.MemPerc}}" "$container" 2>/dev/null | sed 's/%//' || echo "0")
    echo "$cpu,$mem"
}

################################################################################
# Monitoring Check
################################################################################

perform_monitoring_check() {
    ((CHECK_COUNT++))
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    
    log "========================================="
    log "Monitoring Check #$CHECK_COUNT - $timestamp"
    log "========================================="
    
    local issues=0
    
    # 1. API Health
    if check_api_health; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        ((issues++))
        ERROR_COUNTS["api_health"]=$((${ERROR_COUNTS["api_health"]:-0} + 1))
    fi
    
    # 2. Response Time
    local response_time=$(measure_response_time)
    RESPONSE_TIMES["check_$CHECK_COUNT"]=$response_time
    
    if [ $response_time -lt 100 ]; then
        log_success "Response time excellent: ${response_time}ms"
    elif [ $response_time -lt 500 ]; then
        log_success "Response time good: ${response_time}ms"
    elif [ $response_time -lt 1000 ]; then
        log_warning "Response time acceptable: ${response_time}ms"
        WARNING_COUNTS["response_time"]=$((${WARNING_COUNTS["response_time"]:-0} + 1))
    else
        log_error "Response time high: ${response_time}ms"
        ((issues++))
        ERROR_COUNTS["response_time"]=$((${ERROR_COUNTS["response_time"]:-0} + 1))
    fi
    
    # 3. Error Rate
    local error_count=$(check_error_rate)
    if [ $error_count -eq 0 ]; then
        log_success "No errors in last 5 minutes"
    elif [ $error_count -lt 5 ]; then
        log_warning "Low error count: $error_count errors"
        WARNING_COUNTS["errors"]=$((${WARNING_COUNTS["errors"]:-0} + 1))
    else
        log_error "High error count: $error_count errors"
        ((issues++))
        ERROR_COUNTS["errors"]=$((${ERROR_COUNTS["errors"]:-0} + 1))
    fi
    
    # 4. Container Status
    for container in packoptima-api-production packoptima-worker-production packoptima-db-production packoptima-redis-production; do
        if check_container_status "$container"; then
            log_success "Container running: $container"
        else
            log_error "Container not running: $container"
            ((issues++))
            ERROR_COUNTS["container_$container"]=$((${ERROR_COUNTS["container_$container"]:-0} + 1))
        fi
    done
    
    # 5. Resource Usage
    for container in packoptima-api-production packoptima-worker-production; do
        if docker ps | grep -q "$container"; then
            local usage=$(check_resource_usage "$container")
            local cpu=$(echo $usage | cut -d, -f1)
            local mem=$(echo $usage | cut -d, -f2)
            
            if (( $(echo "$cpu < 70" | bc -l 2>/dev/null || echo 1) )); then
                log_success "$container CPU: ${cpu}%"
            else
                log_warning "$container CPU high: ${cpu}%"
                WARNING_COUNTS["cpu_$container"]=$((${WARNING_COUNTS["cpu_$container"]:-0} + 1))
            fi
            
            if (( $(echo "$mem < 70" | bc -l 2>/dev/null || echo 1) )); then
                log_success "$container Memory: ${mem}%"
            else
                log_warning "$container Memory high: ${mem}%"
                WARNING_COUNTS["mem_$container"]=$((${WARNING_COUNTS["mem_$container"]:-0} + 1))
            fi
        fi
    done
    
    # 6. Database Connectivity
    if docker exec packoptima-db-production pg_isready -U postgres >/dev/null 2>&1; then
        log_success "Database accepting connections"
    else
        log_error "Database not accepting connections"
        ((issues++))
        ERROR_COUNTS["database"]=$((${ERROR_COUNTS["database"]:-0} + 1))
    fi
    
    # 7. Redis Connectivity
    if docker exec packoptima-redis-production redis-cli ping 2>/dev/null | grep -q PONG; then
        log_success "Redis responding"
    else
        log_error "Redis not responding"
        ((issues++))
        ERROR_COUNTS["redis"]=$((${ERROR_COUNTS["redis"]:-0} + 1))
    fi
    
    # Summary
    if [ $issues -eq 0 ]; then
        log_success "Check #$CHECK_COUNT: All systems healthy"
    else
        log_error "Check #$CHECK_COUNT: $issues issues detected"
    fi
    
    return $issues
}

################################################################################
# Generate Report
################################################################################

generate_monitoring_report() {
    local report_file="$PROJECT_ROOT/logs/production_monitoring_report_$(date +%Y%m%d_%H%M%S).md"
    
    log "Generating monitoring report: $report_file"
    
    # Calculate statistics
    local total_checks=$CHECK_COUNT
    local total_errors=0
    local total_warnings=0
    
    for key in "${!ERROR_COUNTS[@]}"; do
        total_errors=$((total_errors + ${ERROR_COUNTS[$key]}))
    done
    
    for key in "${!WARNING_COUNTS[@]}"; do
        total_warnings=$((total_warnings + ${WARNING_COUNTS[$key]}))
    done
    
    # Calculate average response time
    local total_response_time=0
    local response_count=0
    for key in "${!RESPONSE_TIMES[@]}"; do
        total_response_time=$((total_response_time + ${RESPONSE_TIMES[$key]}))
        ((response_count++))
    done
    local avg_response_time=$((response_count > 0 ? total_response_time / response_count : 0))
    
    # Generate report
    cat > "$report_file" <<EOF
# Production Monitoring Report

**Generated:** $(date)
**Monitoring Duration:** $DURATION_HOURS hours
**Total Checks:** $total_checks
**Check Interval:** $CHECK_INTERVAL seconds ($(($CHECK_INTERVAL / 60)) minutes)

## Summary

- **Total Errors:** $total_errors
- **Total Warnings:** $total_warnings
- **Average Response Time:** ${avg_response_time}ms
- **Success Rate:** $(( (total_checks - total_errors) * 100 / total_checks ))%

## Health Status

$(if [ $total_errors -eq 0 ]; then
    echo "✅ **HEALTHY** - No critical issues detected"
elif [ $total_errors -lt 5 ]; then
    echo "⚠️ **WARNING** - Minor issues detected"
else
    echo "❌ **CRITICAL** - Multiple issues detected"
fi)

## Error Breakdown

$(if [ $total_errors -eq 0 ]; then
    echo "No errors detected during monitoring period."
else
    echo "| Error Type | Count |"
    echo "|------------|-------|"
    for key in "${!ERROR_COUNTS[@]}"; do
        echo "| $key | ${ERROR_COUNTS[$key]} |"
    done
fi)

## Warning Breakdown

$(if [ $total_warnings -eq 0 ]; then
    echo "No warnings detected during monitoring period."
else
    echo "| Warning Type | Count |"
    echo "|--------------|-------|"
    for key in "${!WARNING_COUNTS[@]}"; do
        echo "| $key | ${WARNING_COUNTS[$key]} |"
    done
fi)

## Response Time Analysis

- **Average Response Time:** ${avg_response_time}ms
- **Total Measurements:** $response_count
- **Performance Rating:** $(if [ $avg_response_time -lt 100 ]; then echo "Excellent"; elif [ $avg_response_time -lt 500 ]; then echo "Good"; elif [ $avg_response_time -lt 1000 ]; then echo "Acceptable"; else echo "Poor"; fi)

## Recommendations

$(if [ $total_errors -eq 0 ] && [ $total_warnings -eq 0 ]; then
    echo "- System is operating normally"
    echo "- Continue monitoring for next 24 hours"
    echo "- No immediate action required"
elif [ $total_errors -eq 0 ] && [ $total_warnings -gt 0 ]; then
    echo "- Review warning logs for patterns"
    echo "- Consider resource optimization"
    echo "- Monitor for degradation"
elif [ $total_errors -lt 5 ]; then
    echo "- Investigate error logs immediately"
    echo "- Review system resources"
    echo "- Consider scaling if needed"
else
    echo "- **URGENT:** Investigate critical issues"
    echo "- Review rollback procedures"
    echo "- Contact on-call engineer"
    echo "- Prepare incident report"
fi)

## Next Steps

1. Review detailed logs: \`$MONITORING_LOG\`
2. Check Grafana dashboards for trends
3. Verify alert notifications working
4. Document any issues found
5. Update runbooks if needed

## Monitoring URLs

- **Grafana:** http://localhost:3001
- **Prometheus:** http://localhost:9090
- **API Health:** $API_URL/health
- **API Docs:** $API_URL/docs

## Full Log

See complete monitoring log: \`$MONITORING_LOG\`
EOF
    
    log_success "Monitoring report generated: $report_file"
    echo "$report_file"
}

################################################################################
# Main Monitoring Loop
################################################################################

main() {
    log "========================================="
    log "Production Monitoring Started"
    log "========================================="
    log "Duration: $DURATION_HOURS hours"
    log "Check Interval: $CHECK_INTERVAL seconds"
    log "Monitoring Log: $MONITORING_LOG"
    log "========================================="
    
    local end_time=$(($(date +%s) + DURATION_HOURS * 3600))
    local critical_issues=0
    
    while [ $(date +%s) -lt $end_time ]; do
        if ! perform_monitoring_check; then
            ((critical_issues++))
            
            # Alert if too many consecutive failures
            if [ $critical_issues -ge 3 ]; then
                log_error "========================================="
                log_error "CRITICAL: Multiple consecutive failures detected"
                log_error "Consider investigating immediately"
                log_error "========================================="
            fi
        else
            critical_issues=0
        fi
        
        # Calculate remaining time
        local remaining=$((end_time - $(date +%s)))
        local remaining_hours=$((remaining / 3600))
        local remaining_minutes=$(((remaining % 3600) / 60))
        
        log "Next check in $CHECK_INTERVAL seconds (${remaining_hours}h ${remaining_minutes}m remaining)"
        sleep $CHECK_INTERVAL
    done
    
    log "========================================="
    log "Monitoring Period Complete"
    log "========================================="
    
    # Generate final report
    local report_file=$(generate_monitoring_report)
    
    log "========================================="
    log "Monitoring Summary"
    log "========================================="
    log "Total Checks: $CHECK_COUNT"
    log "Total Errors: $(for key in "${!ERROR_COUNTS[@]}"; do echo ${ERROR_COUNTS[$key]}; done | awk '{s+=$1} END {print s}')"
    log "Total Warnings: $(for key in "${!WARNING_COUNTS[@]}"; do echo ${WARNING_COUNTS[$key]}; done | awk '{s+=$1} END {print s}')"
    log "Report: $report_file"
    log "========================================="
    
    log_success "Production monitoring completed successfully"
}

# Handle Ctrl+C gracefully
trap 'log "Monitoring interrupted by user"; generate_monitoring_report; exit 0' INT

# Run monitoring
main "$@"
