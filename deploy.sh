#!/bin/bash

# PackOptima AI - Deployment Script
# This script deploys the application using Docker Compose

set -e  # Exit on error

echo "=========================================="
echo "PackOptima AI - Deployment Script"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker is installed"
echo "✓ Docker Compose is installed"
echo ""

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true
echo ""

# Build images
echo "Building Docker images..."
docker-compose build --no-cache
echo ""

# Start services
echo "Starting services..."
docker-compose up -d
echo ""

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Check service status
echo ""
echo "=========================================="
echo "Service Status"
echo "=========================================="
docker-compose ps
echo ""

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✓ Services are running!"
    echo ""
    echo "=========================================="
    echo "Access Information"
    echo "=========================================="
    echo "Frontend:  http://localhost"
    echo "Backend:   http://localhost:8000"
    echo "API Docs:  http://localhost:8000/docs"
    echo "Database:  localhost:5432"
    echo ""
    echo "=========================================="
    echo "Default Credentials"
    echo "=========================================="
    echo "Database User: packoptima_user"
    echo "Database Name: packoptima_db"
    echo ""
    echo "⚠️  IMPORTANT: Change the default passwords in docker-compose.yml for production!"
    echo ""
    echo "=========================================="
    echo "Useful Commands"
    echo "=========================================="
    echo "View logs:        docker-compose logs -f"
    echo "Stop services:    docker-compose down"
    echo "Restart services: docker-compose restart"
    echo "View database:    docker-compose exec database psql -U packoptima_user -d packoptima_db"
    echo ""
else
    echo "❌ Error: Services failed to start"
    echo "Check logs with: docker-compose logs"
    exit 1
fi
