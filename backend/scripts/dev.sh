#!/bin/bash
# Holly Search - Development Environment Startup

set -e

echo "🚀 Holly Search Development Environment"
echo "========================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Navigate to project root for docker-compose
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Start containers
echo -e "\n${BLUE}📦 Starting PostgreSQL and Qdrant...${NC}"
docker compose up -d

# Wait for PostgreSQL
echo -e "\n${BLUE}⏳ Waiting for PostgreSQL to be ready...${NC}"
until docker exec holly-postgres pg_isready -U postgres > /dev/null 2>&1; do
    sleep 1
done
echo -e "${GREEN}✅ PostgreSQL is ready${NC}"

# Wait for Qdrant
echo -e "\n${BLUE}⏳ Waiting for Qdrant to be ready...${NC}"
until curl -s http://localhost:6333/health > /dev/null 2>&1; do
    sleep 1
done
echo -e "${GREEN}✅ Qdrant is ready${NC}"

# Start backend with uv-managed .venv
echo -e "\n${BLUE}🔧 Starting FastAPI backend on http://localhost:8000${NC}"
cd "$PROJECT_ROOT/backend" && PYTHONPATH=. "$PROJECT_ROOT/backend/.venv/bin/uvicorn" app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!



echo -e "\n${GREEN}========================================"
echo -e "✅ All services started!"
echo -e "========================================"

echo -e "📍 Backend:  http://localhost:8000"
echo -e "📍 API Docs: http://localhost:8000/docs"
echo -e "📍 Qdrant:   http://localhost:6333/dashboard"
echo -e "========================================${NC}"
echo -e "\nPress Ctrl+C to stop all services"

# Trap Ctrl+C
trap "echo -e '\n${BLUE}Stopping services...${NC}'; kill $BACKEND_PID 2>/dev/null; docker compose stop; echo -e '${GREEN}✅ All services stopped${NC}'; exit 0" SIGINT

# Wait
wait
