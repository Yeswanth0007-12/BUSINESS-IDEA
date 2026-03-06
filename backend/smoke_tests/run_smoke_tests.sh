#!/bin/bash

# Smoke Test Runner for PackOptima
# Quick post-deployment verification

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8000}"
TIMEOUT="${TIMEOUT:-30}"

echo "========================================="
echo "PackOptima Smoke Tests"
echo "========================================="
echo "Target: $BASE_URL"
echo "Timeout: ${TIMEOUT}s"
echo ""

# Function to check if service is up
check_service() {
    echo "Checking if service is up..."
    
    for i in {1..10}; do
        if curl -s -f "$BASE_URL/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Service is up${NC}"
            return 0
        fi
        
        echo "Waiting for service... ($i/10)"
        sleep 3
    done
    
    echo -e "${RED}✗ Service is not responding${NC}"
    return 1
}

# Check if service is up
if ! check_service; then
    echo ""
    echo "Service is not available. Please ensure:"
    echo "  1. Application is running"
    echo "  2. Database is accessible"
    echo "  3. Redis is running"
    echo "  4. Correct BASE_URL is set"
    exit 1
fi

echo ""
echo "========================================="
echo "Running Smoke Tests"
echo "========================================="
echo ""

# Run smoke tests
python test_smoke.py

EXIT_CODE=$?

echo ""
echo "========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All smoke tests passed${NC}"
    echo "========================================="
    echo ""
    echo "Deployment verification successful!"
    echo "System is ready for use."
else
    echo -e "${RED}✗ Some smoke tests failed${NC}"
    echo "========================================="
    echo ""
    echo "Deployment verification failed!"
    echo "Please review the test output above."
    echo ""
    echo "Common issues:"
    echo "  - Database not accessible"
    echo "  - Redis not running"
    echo "  - Celery workers not started"
    echo "  - Missing environment variables"
    echo "  - Database migrations not applied"
fi

echo ""

exit $EXIT_CODE
