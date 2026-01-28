#!/bin/bash

# Clarus - Stop Script
# Stops all running services

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

main() {
    log_info "Stopping Clarus services..."

    # Stop Backend (uvicorn)
    BACKEND_PIDS=$(lsof -ti:8000 2>/dev/null || true)
    if [ ! -z "$BACKEND_PIDS" ]; then
        log_info "Stopping Backend API (port 8000)..."
        kill $BACKEND_PIDS 2>/dev/null || true
        log_success "Backend stopped"
    else
        log_warn "Backend not running"
    fi

    # Stop Frontend (Next.js)
    FRONTEND_PIDS=$(lsof -ti:3000 2>/dev/null || true)
    if [ ! -z "$FRONTEND_PIDS" ]; then
        log_info "Stopping Frontend (port 3000)..."
        kill $FRONTEND_PIDS 2>/dev/null || true
        log_success "Frontend stopped"
    else
        log_warn "Frontend not running"
    fi

    # Stop Docker services
    log_info "Stopping Docker services..."
    docker compose down
    log_success "Docker services stopped"

    echo ""
    log_success "All services stopped"
}

main
