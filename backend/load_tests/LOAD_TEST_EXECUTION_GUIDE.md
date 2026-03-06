# Load Test Execution Guide

This guide provides step-by-step instructions for running load tests and validating performance.

## Pre-Test Checklist

### 1. Environment Setup
- [ ] Application is running in production-like environment
- [ ] Database is populated with realistic test data
- [ ] Redis is running and accessible
- [ ] Celery workers are running (at least 4 workers)
- [ ] All services are healthy (check /health endpoint)

### 2. Baseline Metrics
Record baseline metrics before load testing:
- [ ] CPU usage: ____%
- [ ] Memory usage: ____%
- [ ] Database connections: ____
- [ ] Redis memory: ____MB

### 3. Monitoring Setup
- [ ] Application logs are being collected
- [ ] System metrics are being monitored
- [ ] Database performance metrics are available
- [ ] Error tracking is enabled (Sentry/similar)

## Test Execution Steps

### Step 1: Warm-up Test
Run a small warm-up test to ensure everything is working:

```bash
# Using Locust
locust -f locustfile.py --host=http://localhost:8000 \
    --users 10 --spawn-rate 2 --run-time 2m --headless

# Using k6
k6 run --vus 10 --duration 2m k6_load_test.js
```

**Validation**:
- [ ] No errors occurred
- [ ] Response times are reasonable
- [ ] All endpoints are accessible

### Step 2: Scenario 1 - Optimization Load
**Target**: 100 concurrent users, 10 requests each

```bash
# Using Locust
locust -f locustfile.py --host=http://localhost:8000 \
    --users 100 --spawn-rate 10 --run-time 5m \
    --tags optimization --headless \
    --html reports/scenario1_report.html

# Using k6
k6 run --env SCENARIO=optimization \
    --vus 100 --duration 5m \
    --out json=reports/scenario1_results.json \
    k6_load_test.js
```

**Performance Targets**:
- [ ] Single product optimization: p95 < 100ms
- [ ] Error rate: < 1%
- [ ] Throughput: > 50 requests/second

**Monitor**:
- CPU usage
- Memory usage
- Database query times
- Response time distribution

### Step 3: Scenario 2 - Bulk Upload Load
**Target**: 10 concurrent bulk uploads, 500 orders each

```bash
# Using Locust
locust -f locustfile.py --host=http://localhost:8000 \
    --users 10 --spawn-rate 2 --run-time 5m \
    --tags bulk_upload --headless \
    --html reports/scenario2_report.html

# Using k6
k6 run --env SCENARIO=bulk_upload \
    --vus 10 --duration 5m \
    --out json=reports/scenario2_results.json \
    k6_load_test.js
```

**Performance Targets**:
- [ ] CSV parsing: < 2 seconds for 1000 rows
- [ ] Task queuing: < 30 seconds for 100 orders
- [ ] Error rate: < 1%

**Monitor**:
- Queue depth
- Celery worker utilization
- Redis memory usage
- Task processing rate

### Step 4: Scenario 3 - Dashboard Load
**Target**: 50 concurrent users loading dashboard

```bash
# Using Locust
locust -f locustfile.py --host=http://localhost:8000 \
    --users 50 --spawn-rate 5 --run-time 5m \
    --tags dashboard --headless \
    --html reports/scenario3_report.html

# Using k6
k6 run --env SCENARIO=dashboard \
    --vus 50 --duration 5m \
    --out json=reports/scenario3_results.json \
    k6_load_test.js
```

**Performance Targets**:
- [ ] Analytics summary: p95 < 200ms
- [ ] Box usage query: p95 < 200ms
- [ ] Shipping cost query: p95 < 200ms
- [ ] Trends query: p95 < 200ms
- [ ] Error rate: < 1%

**Monitor**:
- Database connection pool usage
- Query execution times
- Cache hit rates (if caching enabled)

### Step 5: Combined Load Test
Run all scenarios simultaneously:

```bash
# Using Locust (all user types)
locust -f locustfile.py --host=http://localhost:8000 \
    --users 160 --spawn-rate 10 --run-time 10m --headless \
    --html reports/combined_report.html

# Using k6 (all scenarios)
k6 run --vus 160 --duration 10m \
    --out json=reports/combined_results.json \
    k6_load_test.js
```

**Performance Targets**:
- [ ] Overall p95 response time: < 500ms
- [ ] Error rate: < 1%
- [ ] No memory leaks observed
- [ ] System remains stable

## Performance Validation

### Response Time Validation

Check that response times meet targets:

| Endpoint | Target (p95) | Actual (p95) | Pass/Fail |
|----------|--------------|--------------|-----------|
| Single product optimization | < 100ms | ___ms | ___ |
| Multi-product order (10 items) | < 500ms | ___ms | ___ |
| Bulk upload queuing | < 30s | ___s | ___ |
| Analytics summary | < 200ms | ___ms | ___ |
| Box usage analytics | < 200ms | ___ms | ___ |
| Shipping cost analytics | < 200ms | ___ms | ___ |
| Trends analytics | < 200ms | ___ms | ___ |
| Warehouse API | < 500ms | ___ms | ___ |

### Error Rate Validation

- [ ] Overall error rate: ___% (target: < 1%)
- [ ] 4xx errors: ___% (should be minimal)
- [ ] 5xx errors: ___% (should be < 0.1%)
- [ ] Timeout errors: ___% (should be < 0.1%)

### Throughput Validation

- [ ] Peak requests/second: _____ (target: > 100)
- [ ] Average requests/second: _____ (target: > 50)
- [ ] Total requests processed: _____

### Resource Usage Validation

| Resource | Baseline | Peak | Acceptable? |
|----------|----------|------|-------------|
| CPU usage | ___% | ___% | < 80% |
| Memory usage | ___MB | ___MB | < 80% |
| Database connections | ___ | ___ | < pool size |
| Redis memory | ___MB | ___MB | < max memory |

### Memory Leak Check

Run extended test (30 minutes) and monitor memory:

```bash
locust -f locustfile.py --host=http://localhost:8000 \
    --users 50 --spawn-rate 5 --run-time 30m --headless
```

- [ ] Memory usage remains stable over time
- [ ] No continuous memory growth observed
- [ ] Memory returns to baseline after test

## Post-Test Analysis

### 1. Review Logs
- [ ] Check application logs for errors
- [ ] Review database slow query log
- [ ] Check Celery worker logs
- [ ] Review Redis logs

### 2. Analyze Bottlenecks
Identify any performance bottlenecks:
- [ ] Slow database queries
- [ ] High CPU usage
- [ ] Memory pressure
- [ ] Network latency
- [ ] Queue backlog

### 3. Generate Report
Create a summary report including:
- Test configuration
- Performance metrics
- Pass/fail status for each target
- Identified bottlenecks
- Recommendations

## Troubleshooting

### High Response Times
1. Check database query performance
2. Review application logs for slow operations
3. Check for resource contention
4. Verify network latency

### High Error Rates
1. Check application logs for error details
2. Verify database connectivity
3. Check Redis connectivity
4. Review rate limiting configuration

### Memory Issues
1. Check for memory leaks in application code
2. Review database connection pool settings
3. Check Redis memory usage
4. Monitor Celery worker memory

### Queue Backlog
1. Increase number of Celery workers
2. Check worker processing rate
3. Review task complexity
4. Verify Redis performance

## Success Criteria

Load tests are considered successful if:

- [ ] All performance targets are met
- [ ] Error rate is < 1%
- [ ] No memory leaks detected
- [ ] System remains stable under load
- [ ] Resource usage is within acceptable limits
- [ ] No critical errors in logs

## Next Steps

After successful load testing:

1. Document results in LOAD_TEST_RESULTS.md
2. Update performance baselines
3. Schedule regular load testing
4. Implement any identified optimizations
5. Re-test after optimizations

## Load Test Schedule

Recommended schedule for ongoing load testing:

- **Weekly**: Quick smoke test (10 users, 5 minutes)
- **Before each release**: Full load test suite
- **Monthly**: Extended load test (30+ minutes)
- **Quarterly**: Stress test (beyond normal capacity)
