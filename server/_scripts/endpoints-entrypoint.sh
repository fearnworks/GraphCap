#!/bin/bash
# SPDX-License-Identifier: Apache-2.0

set -e  # Exit on error

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to log errors
error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ❌ ERROR: $1" >&2
}

# Function to check if dependencies need updating
check_dependencies() {
    # Only check dependencies if we're in development mode
    if [ "$NODE_ENV" != "production" ]; then
        log "Checking if dependencies need updating..."
        
        # Create new hash of current dependency files
        local NEW_HASH=$(cat /app/pyproject.toml /app/lib/pyproject.toml /app/server/pyproject.toml | md5sum)
        local OLD_HASH=""
        
        if [ -f /app/.dep_hash ]; then
            OLD_HASH=$(md5sum /app/.dep_hash | cut -d' ' -f1)
        fi
        
        # Compare hashes
        if [ "$NEW_HASH" != "$OLD_HASH" ]; then
            log "Dependencies changed, updating..."
            update_dependencies || return 1
        else
            log "Dependencies up to date"
        fi
    fi
}

# Function to install/update dependencies
update_dependencies() {
    log "Updating dependencies..."
    cd /app && \
    uv pip install  -e "lib[test]" && \
    uv pip install  -e "server[test]" || {
        error "Failed to install dependencies"
        return 1
    }
    
    # Update dependency hash
    cat /app/pyproject.toml /app/lib/pyproject.toml /app/server/pyproject.toml > /app/.dep_hash
    
    log "✅ Dependencies updated successfully"
}

# Add this after the log function
check_environment() {
    log "🔍 Checking Python environment..."
    log "Python path: $(which python)"
    log "Virtual env: $VIRTUAL_ENV"
    log "Installed packages:"
    pip list
}

# Main startup sequence
main() {
    cd /app/server
    
    log "🔍 Starting pre-flight checks..."
    check_environment
    
    # Check dependencies only in development
    check_dependencies || exit 1
    
    # Wait for services to initialize
    log "Waiting for services..."
    sleep 5
    
    log "Checking current directory files..."
    ls -la
    log "================================================"
    # Run database migrations
    log "Running database migrations..."
    cd /app/server
    uv run --active alembic upgrade head || {
        error "Migration failed with status $?"
        log "Checking database connection..."
        uv run --active python -c "
import asyncio
import asyncpg
async def test_db():
    try:
        conn = await asyncpg.connect('$DATABASE_URL')
        await conn.close()
        print('Database connection successful')
    except Exception as e:
        print(f'Database connection failed: {e}')
asyncio.run(test_db())
"
        exit 1
    }
    
    # Start the FastAPI server
    log "🚀 Starting uvicorn server..."
    uv run --active python -m uvicorn server.main:app \
        --host 0.0.0.0 \
        --port 32100 \
        --reload \
        --reload-dir /app/server/server \
        --reload-dir /app/lib \
        --reload-dir /workspace/config/workflows
}

# Trap errors
trap 'error "An error occurred. Exiting..."; exit 1' ERR

# Run main with error handling
main "$@" || {
    error "Startup failed"
    exit 1
}
