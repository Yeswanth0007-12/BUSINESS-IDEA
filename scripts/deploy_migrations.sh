#!/bin/bash
#
# PackOptima Database Migration Deployment Script
# 
# This script safely deploys database migrations with backup and rollback capability.
#
# Usage:
#   ./deploy_migrations.sh [environment]
#
# Examples:
#   ./deploy_migrations.sh production
#   ./deploy_migrations.sh staging
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="${PROJECT_ROOT}/backend"
BACKUP_DIR="${PROJECT_ROOT}/backups"
ENVIRONMENT="${1:-production}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment variables
load_environment() {
    local env_file="${BACKEND_DIR}/.env.${ENVIRONMENT}"
    
    if [ ! -f "$env_file" ]; then
        log_error "Environment file not found: $env_file"
        exit 1
    fi
    
    log_info "Loading environment: ${ENVIRONMENT}"
    export $(cat "$env_file" | grep -v '^#' | xargs)
}

# Validate prerequisites
validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    # Check if alembic is installed
    if ! command -v alembic &> /dev/null; then
        log_error "Alembic is not installed. Please install: pip install alembic"
        exit 1
    fi
    
    # Check if pg_dump is installed
    if ! command -v pg_dump &> /dev/null; then
        log_error "pg_dump is not installed. Please install PostgreSQL client tools"
        exit 1
    fi
    
    # Check if DATABASE_URL is set
    if [ -z "${DATABASE_URL:-}" ]; then
        log_error "DATABASE_URL is not set"
        exit 1
    fi
    
    log_info "✓ Prerequisites validated"
}

# Create backup directory
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        log_info "Creating backup directory: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
}

# Backup database
backup_database() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${BACKUP_DIR}/packoptima_${ENVIRONMENT}_${timestamp}.sql"
    
    log_info "Creating database backup: $(basename $backup_file)"
    
    # Extract database connection details from DATABASE_URL
    # Format: postgresql://user:password@host:port/database
    local db_url="${DATABASE_URL}"
    
    # Use pg_dump with custom format for better compression and restore options
    pg_dump "$db_url" -F c -f "$backup_file"
    
    if [ $? -eq 0 ]; then
        log_info "✓ Backup created successfully: $backup_file"
        
        # Compress backup
        log_info "Compressing backup..."
        gzip "$backup_file"
        
        # Store backup path for potential rollback
        echo "$backup_file.gz" > "${BACKUP_DIR}/latest_backup.txt"
        
        log_info "✓ Backup compressed: ${backup_file}.gz"
        
        # Optional: Upload to S3 or backup storage
        if command -v aws &> /dev/null && [ -n "${BACKUP_S3_BUCKET:-}" ]; then
            log_info "Uploading backup to S3..."
            aws s3 cp "${backup_file}.gz" "s3://${BACKUP_S3_BUCKET}/migrations/${ENVIRONMENT}/"
            log_info "✓ Backup uploaded to S3"
        fi
    else
        log_error "Backup failed!"
        exit 1
    fi
}

# Check current migration version
check_current_version() {
    log_info "Checking current migration version..."
    cd "$BACKEND_DIR"
    
    local current_version=$(alembic current 2>&1)
    log_info "Current version: $current_version"
}

# Show pending migrations
show_pending_migrations() {
    log_info "Showing pending migrations..."
    cd "$BACKEND_DIR"
    
    alembic history | head -20
}

# Run migrations
run_migrations() {
    log_info "Running database migrations..."
    cd "$BACKEND_DIR"
    
    # Run migrations with verbose output
    alembic upgrade head
    
    if [ $? -eq 0 ]; then
        log_info "✓ Migrations completed successfully"
    else
        log_error "Migration failed!"
        return 1
    fi
}

# Verify migration
verify_migration() {
    log_info "Verifying migration..."
    cd "$BACKEND_DIR"
    
    # Check current version
    local new_version=$(alembic current 2>&1)
    log_info "New version: $new_version"
    
    # Run basic database connectivity test
    python3 << EOF
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM alembic_version"))
        count = result.scalar()
        print(f"✓ Database connection successful")
        print(f"✓ Alembic version table exists with {count} record(s)")
        sys.exit(0)
except Exception as e:
    print(f"✗ Database verification failed: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        log_info "✓ Migration verified successfully"
    else
        log_error "Migration verification failed!"
        return 1
    fi
}

# Rollback migration
rollback_migration() {
    log_error "Rolling back migration..."
    cd "$BACKEND_DIR"
    
    # Downgrade one version
    alembic downgrade -1
    
    if [ $? -eq 0 ]; then
        log_info "✓ Rollback completed"
    else
        log_error "Rollback failed! Manual intervention required."
        exit 1
    fi
}

# Restore from backup
restore_from_backup() {
    local backup_file=$(cat "${BACKUP_DIR}/latest_backup.txt" 2>/dev/null)
    
    if [ -z "$backup_file" ] || [ ! -f "$backup_file" ]; then
        log_error "No backup file found for restoration"
        exit 1
    fi
    
    log_warn "Restoring database from backup: $(basename $backup_file)"
    log_warn "This will overwrite the current database!"
    
    read -p "Are you sure you want to restore? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_info "Restore cancelled"
        exit 0
    fi
    
    # Decompress backup
    log_info "Decompressing backup..."
    gunzip -k "$backup_file"
    local uncompressed_file="${backup_file%.gz}"
    
    # Restore database
    log_info "Restoring database..."
    pg_restore -d "$DATABASE_URL" -c "$uncompressed_file"
    
    if [ $? -eq 0 ]; then
        log_info "✓ Database restored successfully"
        rm "$uncompressed_file"
    else
        log_error "Database restoration failed!"
        exit 1
    fi
}

# Main execution
main() {
    echo "========================================="
    echo "  PackOptima Database Migration"
    echo "  Environment: ${ENVIRONMENT}"
    echo "========================================="
    echo ""
    
    # Load environment
    load_environment
    
    # Validate prerequisites
    validate_prerequisites
    
    # Create backup directory
    create_backup_dir
    
    # Check current version
    check_current_version
    
    # Show pending migrations
    show_pending_migrations
    
    # Confirm migration
    echo ""
    log_warn "This will run database migrations on ${ENVIRONMENT} environment"
    read -p "Do you want to continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "Migration cancelled"
        exit 0
    fi
    
    # Backup database
    backup_database
    
    # Run migrations
    if run_migrations; then
        # Verify migration
        if verify_migration; then
            echo ""
            log_info "========================================="
            log_info "  Migration Completed Successfully!"
            log_info "========================================="
            exit 0
        else
            log_error "Migration verification failed!"
            log_warn "Initiating rollback..."
            rollback_migration
            exit 1
        fi
    else
        log_error "Migration failed!"
        log_warn "Initiating rollback..."
        rollback_migration
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --restore)
        load_environment
        restore_from_backup
        ;;
    --rollback)
        load_environment
        rollback_migration
        ;;
    *)
        main
        ;;
esac
