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
        local NEW_HASH=$(cat /app/pipelines/pyproject.toml | md5sum)
        local OLD_HASH=""
        
        if [ -f /app/pipelines/.dep_hash ]; then
            OLD_HASH=$(md5sum /app/pipelines/.dep_hash | cut -d' ' -f1)
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
    cd /app/pipelines && \
    uv pip install -e ".[dev]" || {
        error "Failed to install dependencies"
        return 1
    }
    
    # Update dependency hash
    cat /app/pipelines/pyproject.toml > /app/pipelines/.dep_hash
    
    log "✅ Dependencies updated successfully"
}

# Function to check Python environment
check_environment() {
    log "🔍 Checking Python environment..."
    log "Python path: $(which python)"
    log "Virtual env: $VIRTUAL_ENV"
    log "Installed packages:"
    pip list
}

# Main startup sequence
main() {
    log "🚀 Starting pipeline service..."
    
    # Check environment
    check_environment
    
    # Check dependencies only in development
    check_dependencies || exit 1
    
    # Wait for services to initialize
    log "Waiting for services..."
    sleep 5
    
    # Set Dagster home if not set
    if [ -z "$DAGSTER_HOME" ]; then
        export DAGSTER_HOME="/app/pipelines/.dagster"
        log "Setting DAGSTER_HOME to $DAGSTER_HOME"
    fi
    
    # Ensure Dagster directory exists
    mkdir -p "$DAGSTER_HOME"
    PORT=$DAGSTER_PORT
    log "Starting Dagster webserver..."
    cd /app/pipelines
    exec python -m dagster dev -h 0.0.0.0 -p $PORT
}

# Trap errors
trap 'error "An error occurred. Exiting..."; exit 1' ERR

# Run main with error handling
main "$@" || {
    error "Startup failed"
    exit 1
}
