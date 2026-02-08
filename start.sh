#!/bin/bash

# Clarus - One-Command Startup Script
# Starts: Docker (Qdrant + PostgreSQL) → Backend API → Frontend Dev Server

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Cleanup function
cleanup() {
    log_warn "Shutting down services..."

    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    log_info "Services stopped. Docker containers still running (use 'docker compose down' to stop)"
    exit 0
}

trap cleanup INT TERM

# Check if ports are available
check_port() {
    local port=$1
    local service=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_error "Port $port is already in use (required for $service)"
        log_info "Find process: lsof -i :$port"
        return 1
    fi
    return 0
}

# Main startup sequence
main() {
    log_info "Starting Clarus Application..."

    # Step 1: Check required ports
    log_info "Checking port availability..."
    check_port 6333 "Qdrant" || exit 1
    check_port 54322 "PostgreSQL" || exit 1
    check_port 8000 "Backend API" || exit 1
    check_port 3000 "Frontend" || exit 1
    log_success "All ports available"

    # Step 2: Start Docker services
    log_info "Starting Docker services (Qdrant + PostgreSQL)..."
    docker compose up -d

    if [ $? -ne 0 ]; then
        log_error "Failed to start Docker services"
        exit 1
    fi

    log_success "Docker services started"
    log_info "Waiting for services to be ready..."
    sleep 3

    # Step 3: Check backend .env
    if [ ! -f backend/.env ]; then
        log_error "backend/.env not found"
        log_info "Create backend/.env with OPENROUTER_API_KEY"
        exit 1
    fi

    # Step 4: Start Backend API
    log_info "Starting Backend API on :8000..."

    cd backend

    # Start uvicorn in background using uv-managed .venv
    ../.venv/bin/uvicorn app.main:app --reload > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..

    log_success "Backend API started (PID: $BACKEND_PID)"
    log_info "Backend logs: tail -f logs/backend.log"
    sleep 2

    # Step 5: Start Frontend
    log_info "Starting Frontend on :3000..."

    cd frontend

    # Install dependencies if node_modules missing
    if [ ! -d node_modules ]; then
        log_warn "node_modules not found, running npm install..."
        npm install
    fi

    # Start Next.js dev server in background
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..

    log_success "Frontend started (PID: $FRONTEND_PID)"
    log_info "Frontend logs: tail -f logs/frontend.log"

    # Step 6: Summary
    echo ""
    log_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_success "✓ Clarus is running!"
    log_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "  ${BLUE}Frontend:${NC}  http://localhost:3000"
    echo -e "  ${BLUE}Backend:${NC}   http://localhost:8000"
    echo -e "  ${BLUE}API Docs:${NC}  http://localhost:8000/docs"
    echo -e "  ${BLUE}Qdrant:${NC}    http://localhost:6333/dashboard"
    echo ""
    log_info "Press Ctrl+C to stop all services"
    echo ""

    # Keep script running
    wait
}

# Create logs directory
mkdir -p logs

# Run main
main
