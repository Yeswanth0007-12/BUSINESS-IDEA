# Smoke Tests for PackOptima

Quick post-deployment verification tests to ensure critical functionality is working.

## Purpose

Smoke tests are designed to:
- Verify the application is running
- Check critical endpoints are accessible
- Validate database and Redis connectivity
- Ensure Celery workers are running
- Test basic authentication flow
- Verify response times are acceptable

## Running Smoke Tests

### Quick Run
```bash
cd backend/smoke_tests
python test_smoke.py
```

### Using the Runner Script
```bash
cd backend/smoke_tests
chmod +x run_smoke_tests.sh
./run_smoke_tests.sh
```

### Against Different Environment
```bash
BASE_URL=https://api.packoptima.com ./run_smoke_tests.sh
```

### With pytest Directly
```bash
pytest test_smoke.py -v -m smoke
```

## Test Categories

### 1. Health Checks
- `/health` endpoint responds
- Database connectivity
- Redis connectivity
- Celery workers running

### 2. Authentication
- Login endpoint responds
- Register endpoint responds
- Token generation works

### 3. Core Endpoints
- Products endpoint accessible
- Boxes endpoint accessible
- Optimization endpoint responds
- Analytics endpoint responds

### 4. Async Endpoints
- Async optimization endpoint responds
- Task status endpoint responds

### 5. Response Times
- Health check < 1 second
- Products list < 2 seconds
- Analytics < 2 seconds

### 6. Error Handling
- Invalid endpoints return 404
- Unauthorized requests return 401
- Invalid JSON returns 400

## Success Criteria

All smoke tests must pass for deployment to be considered successful:

- [ ] Health endpoint returns 200
- [ ] Database is connected
- [ ] Redis is connected
- [ ] At least one Celery worker is running
- [ ] Authentication endpoints respond
- [ ] Core endpoints are accessible
- [ ] Response times are acceptable
- [ ] Error handling works correctly

## When to Run Smoke Tests

### Required
- **After deployment**: Verify deployment was successful
- **After configuration changes**: Ensure changes didn't break anything
- **After infrastructure changes**: Verify connectivity

### Recommended
- **Before release**: Final check before going live
- **After database migrations**: Ensure migrations didn't break anything
- **After dependency updates**: Verify compatibility

### Optional
- **Daily**: As part of monitoring
- **Before major changes**: Baseline check

## Interpreting Results

### All Tests Pass ✓
```
✓ All smoke tests passed
Deployment verification successful!
System is ready for use.
```

**Action**: Deployment is successful, system is ready.

### Some Tests Fail ✗
```
✗ Some smoke tests failed
Deployment verification failed!
```

**Action**: Review failed tests and fix issues before proceeding.

## Common Issues and Solutions

### Service Not Responding
**Symptoms**: Health check fails, connection refused

**Solutions**:
1. Check if application is running: `ps aux | grep uvicorn`
2. Check application logs: `tail -f logs/app.log`
3. Verify port is correct: `netstat -tulpn | grep 8000`
4. Check firewall rules

### Database Connection Failed
**Symptoms**: Database health check fails

**Solutions**:
1. Check PostgreSQL is running: `systemctl status postgresql`
2. Verify connection string in `.env`
3. Check database credentials
4. Verify network connectivity
5. Check database logs

### Redis Connection Failed
**Symptoms**: Redis health check fails

**Solutions**:
1. Check Redis is running: `systemctl status redis`
2. Verify Redis URL in `.env`
3. Check Redis is accessible: `redis-cli ping`
4. Verify network connectivity

### No Celery Workers
**Symptoms**: Celery workers health check fails

**Solutions**:
1. Start Celery workers: `celery -A app.core.celery_app worker`
2. Check worker logs
3. Verify Redis connection
4. Check worker configuration

### Authentication Fails
**Symptoms**: Login/register tests fail

**Solutions**:
1. Check database migrations are applied
2. Verify JWT secret is set
3. Check user table exists
4. Review authentication logs

### Slow Response Times
**Symptoms**: Response time tests fail

**Solutions**:
1. Check database query performance
2. Verify adequate resources (CPU, memory)
3. Check for network latency
4. Review application logs for slow operations

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Smoke Tests

on:
  push:
    branches: [main]
  deployment:

jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest requests
      
      - name: Run smoke tests
        env:
          BASE_URL: ${{ secrets.PRODUCTION_URL }}
        run: |
          cd backend/smoke_tests
          python test_smoke.py
```

### Jenkins Example
```groovy
stage('Smoke Tests') {
    steps {
        sh '''
            cd backend/smoke_tests
            BASE_URL=${PRODUCTION_URL} ./run_smoke_tests.sh
        '''
    }
}
```

## Monitoring Integration

### Prometheus Metrics
Smoke tests can be integrated with Prometheus for monitoring:

```python
from prometheus_client import Counter, Histogram

smoke_test_failures = Counter('smoke_test_failures', 'Number of smoke test failures')
smoke_test_duration = Histogram('smoke_test_duration_seconds', 'Smoke test duration')
```

### Alerting
Set up alerts for smoke test failures:

```yaml
# Prometheus alert rule
- alert: SmokeTestsFailing
  expr: smoke_test_failures > 0
  for: 5m
  annotations:
    summary: "Smoke tests are failing"
    description: "Smoke tests have failed, deployment may be broken"
```

## Best Practices

1. **Keep tests fast**: Smoke tests should complete in < 1 minute
2. **Test critical paths only**: Don't test every feature
3. **Use realistic data**: Test with production-like data
4. **Run after every deployment**: Automate in CI/CD
5. **Monitor continuously**: Run periodically in production
6. **Alert on failures**: Set up notifications
7. **Document failures**: Keep a log of issues found

## Extending Smoke Tests

To add new smoke tests:

1. Add test method to appropriate class in `test_smoke.py`
2. Mark with `@pytest.mark.smoke` decorator
3. Keep test simple and fast
4. Test critical functionality only
5. Update this README with new test

Example:
```python
@pytest.mark.smoke
def test_new_critical_endpoint(self, auth_token):
    """Test that new critical endpoint responds"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/new-endpoint",
        headers=headers,
        timeout=5
    )
    
    assert response.status_code == 200
```

## Troubleshooting

### Tests Timeout
- Increase timeout: `TIMEOUT=60 ./run_smoke_tests.sh`
- Check network connectivity
- Verify service is not overloaded

### Authentication Issues
- Verify test user exists
- Check credentials in test file
- Review authentication logs

### Intermittent Failures
- Check for race conditions
- Verify service stability
- Review resource usage

## Contact

For issues with smoke tests, contact the DevOps team.
