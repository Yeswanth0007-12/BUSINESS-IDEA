# Load Testing for PackOptima

This directory contains load testing scripts for PackOptima using both Locust and k6.

## Prerequisites

### For Locust
```bash
pip install locust
```

### For k6
Download and install from: https://k6.io/docs/getting-started/installation/

## Test Scenarios

### Scenario 1: Optimization Load
- **Users**: 100 concurrent users
- **Requests**: 10 optimization requests per user
- **Target**: < 100ms per single product optimization

### Scenario 2: Bulk Upload Load
- **Users**: 10 concurrent users
- **Orders**: 500 orders per upload
- **Target**: < 30 seconds to queue all orders

### Scenario 3: Dashboard Load
- **Users**: 50 concurrent users
- **Requests**: Multiple analytics queries
- **Target**: < 200ms per analytics query

### Scenario 4: Warehouse API Load
- **Users**: Variable
- **Target**: < 500ms at p95

## Running Load Tests

### Using Locust

#### Run all scenarios:
```bash
cd backend/load_tests
locust -f locustfile.py --host=http://localhost:8000
```

Then open http://localhost:8089 in your browser to configure and start the test.

#### Run specific scenario:
```bash
# Optimization load
locust -f locustfile.py --host=http://localhost:8000 --tags optimization

# Bulk upload load
locust -f locustfile.py --host=http://localhost:8000 --tags bulk_upload

# Dashboard load
locust -f locustfile.py --host=http://localhost:8000 --tags dashboard

# Warehouse API load
locust -f locustfile.py --host=http://localhost:8000 --tags warehouse
```

#### Headless mode (no web UI):
```bash
locust -f locustfile.py --host=http://localhost:8000 \
    --users 100 --spawn-rate 10 --run-time 5m --headless
```

### Using k6

#### Run all scenarios:
```bash
cd backend/load_tests
k6 run k6_load_test.js
```

#### Run specific scenario:
```bash
# Optimization load
k6 run --env SCENARIO=optimization k6_load_test.js

# Bulk upload load
k6 run --env SCENARIO=bulk_upload k6_load_test.js

# Dashboard load
k6 run --env SCENARIO=dashboard k6_load_test.js
```

#### Custom configuration:
```bash
# 200 users for 10 minutes
k6 run --vus 200 --duration 10m k6_load_test.js

# Against different host
k6 run --env BASE_URL=https://api.packoptima.com k6_load_test.js
```

## Performance Targets

| Operation | Target | Metric |
|-----------|--------|--------|
| Single product optimization | < 100ms | p95 |
| Multi-product order (10 items) | < 500ms | p95 |
| Bulk upload (100 orders) | < 30s | Total time |
| Analytics queries | < 200ms | p95 |
| Warehouse API | < 500ms | p95 |

## Interpreting Results

### Locust Results
- **RPS (Requests Per Second)**: Higher is better
- **Response Time**: Check p50, p95, p99 percentiles
- **Failure Rate**: Should be < 1%

### k6 Results
- **http_req_duration**: Check p(95) threshold
- **http_req_failed**: Should be < 1%
- **Custom metrics**: optimization_duration, analytics_duration

## Test Data Setup

Before running load tests, ensure:

1. **Database is populated** with test data:
   - At least 100 products
   - At least 20 boxes
   - Test user account exists

2. **Services are running**:
   - FastAPI backend
   - PostgreSQL database
   - Redis (for queue system)
   - Celery workers (for async tasks)

3. **Environment is configured**:
   - `.env` file with correct settings
   - Database migrations applied
   - Test user created

## Setup Test Data

```bash
# Run test data setup script
python setup_test_data.py
```

## Monitoring During Load Tests

Monitor these metrics during load tests:

1. **Application Metrics**:
   - Response times (p50, p95, p99)
   - Error rates
   - Throughput (requests/second)

2. **System Metrics**:
   - CPU usage
   - Memory usage
   - Database connections
   - Redis memory

3. **Queue Metrics**:
   - Queue depth
   - Task processing rate
   - Worker utilization

## Troubleshooting

### High Error Rates
- Check application logs
- Verify database connections
- Check Redis connectivity
- Ensure Celery workers are running

### Slow Response Times
- Check database query performance
- Monitor CPU and memory usage
- Check for database connection pool exhaustion
- Verify Redis performance

### Connection Errors
- Increase connection pool size
- Check network configuration
- Verify firewall rules
- Check rate limiting settings

## Best Practices

1. **Start small**: Begin with low user counts and gradually increase
2. **Monitor continuously**: Watch system metrics during tests
3. **Test in isolation**: Run one scenario at a time initially
4. **Use realistic data**: Test with production-like data volumes
5. **Test regularly**: Run load tests before each release

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Load Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install k6
        run: |
          sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      - name: Run load tests
        run: k6 run backend/load_tests/k6_load_test.js
```

## Results Storage

Load test results should be stored for trend analysis:

- **Locust**: Export results as CSV or use Locust's built-in charts
- **k6**: Use k6 Cloud, InfluxDB, or Grafana for result storage

## Contact

For questions about load testing, contact the DevOps team.
