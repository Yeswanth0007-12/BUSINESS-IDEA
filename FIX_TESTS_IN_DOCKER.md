# 🔧 Fix: Tests Not Found in Docker Container

## Problem

When you run `docker-compose exec backend pytest tests/ -v`, it shows:
```
collected 0 items
```

This means pytest found no test files.

## Root Cause

The test files exist on your host machine in `backend/tests/` but they weren't copied into the Docker container when it was built. The container was built before the test files were created.

## Solution: Rebuild the Container

You need to rebuild the backend container to include the test files.

---

## Quick Fix (Rebuild Backend Only)

```powershell
# Rebuild and restart just the backend container
docker-compose up --build -d backend

# Wait 10 seconds for it to start
Start-Sleep -Seconds 10

# Verify tests are now available
docker-compose exec backend pytest tests/ -v
```

**Time:** 1-2 minutes

---

## Complete Fix (Rebuild Everything)

If the quick fix doesn't work, rebuild all containers:

```powershell
# Stop all containers
docker-compose down

# Rebuild and start all containers
docker-compose up --build -d

# Wait 30 seconds for everything to start
Start-Sleep -Seconds 30

# Verify tests are now available
docker-compose exec backend pytest tests/ -v
```

**Time:** 3-5 minutes

---

## Verify Test Files Are Copied

After rebuilding, check that test files are in the container:

```powershell
# List test files in container
docker-compose exec backend ls -la tests/

# You should see:
# test_analytics.py
# test_bulk_upload.py
# test_csv_parsing.py
# test_end_to_end_workflows.py
# test_integration_workflows.py
# test_multi_product_packing.py
# test_optimization_engine.py
# test_packing_algorithms.py
# test_performance_benchmarks.py
# test_property_based.py
# test_security.py
# test_shipping_costs.py
# test_warehouse_auth.py
# conftest.py
```

---

## Run Tests

Once the container is rebuilt, run the tests:

```powershell
# Run all tests
docker-compose exec backend pytest tests/ -v

# Run specific test file
docker-compose exec backend pytest tests/test_packing_algorithms.py -v

# Run with more detail
docker-compose exec backend pytest tests/ -vv

# Run and show print statements
docker-compose exec backend pytest tests/ -v -s
```

---

## Expected Output

After rebuilding, you should see:

```
collected 200+ items

tests/test_analytics.py::test_analytics_summary PASSED
tests/test_bulk_upload.py::test_csv_validation PASSED
tests/test_packing_algorithms.py::test_basic_packing PASSED
...
```

---

## Why This Happened

Docker builds an image from your code at a specific point in time. When you run `docker-compose up --build`, it:

1. Copies files from `backend/` into the image
2. Installs dependencies
3. Creates the container

If you add new files after building (like test files), they won't be in the container until you rebuild.

---

## Prevention

Whenever you add new files to the backend, rebuild:

```powershell
docker-compose up --build -d backend
```

Or use Docker volumes to mount the code (for development):

```yaml
# In docker-compose.yml (for development only)
backend:
  volumes:
    - ./backend:/app
```

**Note:** We don't use volumes in production because it's slower and less secure.

---

## Alternative: Copy Files Manually (Temporary)

If you don't want to rebuild, you can copy files manually:

```powershell
# Copy all test files into the running container
docker cp backend/tests/. packoptima-backend:/app/tests/

# Verify
docker-compose exec backend ls -la tests/

# Run tests
docker-compose exec backend pytest tests/ -v
```

**Note:** This is temporary - files will be lost when container restarts. Rebuilding is the proper solution.

---

## Summary

**Quick Fix:**
```powershell
docker-compose up --build -d backend
docker-compose exec backend pytest tests/ -v
```

**Complete Fix:**
```powershell
docker-compose down
docker-compose up --build -d
docker-compose exec backend pytest tests/ -v
```

**Expected Result:** 200+ tests collected and run

---

**Status:** Ready to fix
**Time Required:** 2-5 minutes
**Last Updated:** 2026-03-05
