# Test Fix & Login Navigation Plan

## Current Status
- ✅ 117 tests passing
- ❌ 23 tests failing
- ⚠️ 80 tests with errors (setup issues)

## Issues to Fix

### 1. Test Setup Errors (80 tests)
**Problem:** Services require `db` parameter but tests instantiate without it

**Affected Services:**
- `OptimizationEngine()` - needs `db` parameter
- `BulkUploadService()` - needs `db` parameter  
- `AuthService()` - needs `db` parameter
- `WarehouseService()` - needs `db` parameter

**Solution:** Update `conftest.py` to provide mock database sessions

### 2. CSV Parsing Type Error (21 tests)
**Problem:** `BulkUploadService.parse_bulk_upload_csv()` expects string but tests pass StringIO

**Error:** `TypeError: initial_value must be str or None, not _io.StringIO`

**Solution:** Fix the service to accept StringIO or fix tests to pass strings

### 3. E2E Test Failure (1 test)
**Problem:** Registration endpoint returns 404 instead of 201

**Solution:** Check if auth routes are properly registered

### 4. Property-Based Test Health Check (1 test)
**Problem:** Hypothesis filtering too much data

**Solution:** Adjust test strategy

### 5. Login Navigation Issue
**Problem:** After login, user doesn't navigate to dashboard

**Solution:** Check AuthContext and routing logic

## Execution Order
1. Fix conftest.py to provide database fixtures
2. Fix CSV parsing type issue
3. Fix E2E registration route
4. Fix property-based test
5. Fix login navigation
6. Rebuild container and verify all tests pass
