# End-to-End Workflow Tests

## Overview

The end-to-end workflow tests in `test_end_to_end_workflows.py` validate complete user journeys through the PackOptima system. These tests ensure all components work together correctly from start to finish.

## Test Coverage

### 1. Complete User Workflow (`TestCompleteUserWorkflow`)
**Validates: Requirements 43.1, 43.2, 43.3, 43.4, 43.5**

Tests the basic optimization workflow:
1. Register user
2. Login
3. Create product
4. Create box
5. Optimize packaging
6. View results

**Verifies:**
- User authentication flow
- Product and box creation
- Optimization engine integration
- Result accuracy (space utilization, costs, orientation)

### 2. Complete Order Workflow (`TestCompleteOrderWorkflow`)
**Validates: Requirements 43.1, 43.2, 43.3, 43.4, 43.5**

Tests multi-product order packing:
1. Setup: Create user, products, and boxes
2. Create order with multiple items
3. Optimize order packing
4. View packing results

**Verifies:**
- Order creation with multiple items
- Bin packing algorithm execution
- All items are packed successfully
- Cost calculations are accurate

### 3. Complete Bulk Upload Workflow (`TestCompleteBulkUploadWorkflow`)
**Validates: Requirements 43.1, 43.2, 43.3, 43.4, 43.5**

Tests CSV bulk upload processing:
1. Setup: Create user, products, and boxes
2. Upload CSV with multiple orders
3. Track upload progress
4. View results

**Verifies:**
- CSV file upload and parsing
- Bulk order creation
- Asynchronous task queuing
- Progress tracking
- Status reporting

### 4. Complete Warehouse Integration Workflow (`TestCompleteWarehouseIntegrationWorkflow`)
**Validates: Requirements 43.1, 43.2, 43.3, 43.4, 43.5**

Tests warehouse API integration:
1. Setup: Create user, products, and boxes
2. Generate API key
3. Authenticate with API key
4. Optimize package via warehouse API
5. Register webhook
6. Verify webhook configuration

**Verifies:**
- API key generation and authentication
- Warehouse optimization endpoint
- Webhook registration
- Integration security

## Running the Tests

### Option 1: Docker Environment (Recommended)

```bash
# Start the Docker environment
docker-compose up -d

# Run tests in the backend container
docker exec packoptima-backend pytest tests/test_end_to_end_workflows.py -v -m e2e

# Or run specific test class
docker exec packoptima-backend pytest tests/test_end_to_end_workflows.py::TestCompleteUserWorkflow -v
```

### Option 2: Local Environment

**Requirements:**
- Python 3.11 or 3.12 (Python 3.14 has SQLAlchemy compatibility issues)
- PostgreSQL running
- Redis running
- All dependencies installed

```bash
# From backend directory
cd backend

# Run all e2e tests
pytest tests/test_end_to_end_workflows.py -v -m e2e

# Run specific test
pytest tests/test_end_to_end_workflows.py::TestCompleteUserWorkflow::test_complete_optimization_workflow -v
```

### Option 3: CI/CD Pipeline

```bash
# Set Hypothesis profile for CI
export HYPOTHESIS_PROFILE=ci

# Run with coverage
pytest tests/test_end_to_end_workflows.py -v -m e2e --cov=app --cov-report=html
```

## Test Data

Each test creates its own isolated test data:
- Unique email addresses to avoid conflicts
- Unique SKUs and order numbers
- Separate company contexts for multi-tenant isolation

## Expected Results

All tests should pass with:
- ✓ User authentication successful
- ✓ Products and boxes created
- ✓ Optimizations complete successfully
- ✓ Results contain expected fields
- ✓ Costs and metrics are positive and accurate

## Troubleshooting

### SQLAlchemy Compatibility Issues

If you see errors like:
```
AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'> directly inherits TypingOnly...
```

**Solution:** Use Python 3.11 or 3.12, or run tests in Docker.

### Database Connection Errors

Ensure PostgreSQL and Redis are running:
```bash
# Check services
docker-compose ps

# View logs
docker-compose logs database
docker-compose logs redis
```

### Authentication Failures

If tests fail at login:
- Check SECRET_KEY is set in environment
- Verify database migrations are up to date
- Check user table exists

### Timeout Issues

For bulk upload tests, increase timeout if needed:
```python
time.sleep(5)  # Increase from 2 to 5 seconds
```

## Performance Expectations

- User workflow: < 2 seconds
- Order workflow: < 3 seconds
- Bulk upload workflow: < 5 seconds (for small CSV)
- Warehouse workflow: < 2 seconds

## Integration with CI/CD

These tests should be run:
1. Before merging to main branch
2. After deployment to staging
3. As part of smoke tests in production

## Notes

- Tests use `@pytest.mark.e2e` marker for easy filtering
- Each test is independent and creates its own data
- Tests clean up after themselves (via database transactions)
- Helper function `create_test_user()` simplifies authentication
