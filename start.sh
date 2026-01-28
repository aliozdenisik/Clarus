#!/bin/bash
# Holly Search - Tek Tuşla Başlatma Scripti

set -e

# Renkler
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Proje dizini
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════╗"
echo "║         Holly Search - Başlatılıyor           ║"
echo "╚═══════════════════════════════════════════════╝"
echo -e "${NC}"

# PID'leri sakla
BACKEND_PID=""
FRONTEND_PID=""

# Temizlik fonksiyonu
cleanup() {
    echo -e "\n${YELLOW}Servisler durduruluyor...${NC}"

    # Backend'i durdur
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null
        echo -e "${GREEN}✓ Backend durduruldu${NC}"
    fi

    # Frontend'i durdur
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null
        echo -e "${GREEN}✓ Frontend durduruldu${NC}"
    fi

    # Docker servislerini durdur
    docker compose stop 2>/dev/null
    echo -e "${GREEN}✓ Docker servisleri durduruldu${NC}"

    echo -e "\n${GREEN}Tüm servisler durduruldu.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Docker kontrolü
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker yüklü değil. Lütfen Docker'ı yükleyin.${NC}"
    exit 1
fi

# 1. Docker servislerini başlat
echo -e "${BLUE}[1/4] Docker servisleri başlatılıyor...${NC}"
docker compose up -d

# PostgreSQL'i bekle
echo -e "${BLUE}[2/4] PostgreSQL bekleniyor...${NC}"
until docker exec holly-postgres pg_isready -U postgres > /dev/null 2>&1; do
    sleep 1
done
echo -e "${GREEN}✓ PostgreSQL hazır${NC}"

# Qdrant'ı bekle
echo -e "${BLUE}[3/4] Qdrant bekleniyor...${NC}"
until curl -s http://localhost:6333/health > /dev/null 2>&1; do
    sleep 1
done
echo -e "${GREEN}✓ Qdrant hazır${NC}"

# Python venv aktive et
echo -e "${BLUE}[4/4] Uygulamalar başlatılıyor...${NC}"

if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Backend'i başlat
cd "$PROJECT_ROOT/backend"
PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend başlatıldı (PID: $BACKEND_PID)${NC}"

# Frontend'i başlat
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend başlatıldı (PID: $FRONTEND_PID)${NC}"

# Başarı mesajı
echo -e "\n${GREEN}"
echo "╔═══════════════════════════════════════════════╗"
echo "║           Tüm servisler çalışıyor!            ║"
echo "╠═══════════════════════════════════════════════╣"
echo "║  Frontend:  http://localhost:3000             ║"
echo "║  Backend:   http://localhost:8000             ║"
echo "║  API Docs:  http://localhost:8000/docs        ║"
echo "║  Qdrant:    http://localhost:6333/dashboard   ║"
echo "╠═══════════════════════════════════════════════╣"
echo "║  Durdurmak için: Ctrl+C                       ║"
echo "╚═══════════════════════════════════════════════╝"
echo -e "${NC}"

# Bekle
wait
