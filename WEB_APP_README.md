# Holly Search Web Application

Sacred Texts RAG sistemi için modern web arayüzü.

## Hızlı Başlangıç

### 1. Docker Servislerini Başlat

```bash
docker compose up -d
```

Bu komut PostgreSQL (port 54322) ve Qdrant (port 6333) başlatır.

### 2. Backend'i Başlat

```bash
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend: http://localhost:8000
API Docs: http://localhost:8000/docs

### 3. Frontend'i Başlat

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Tek Komutla Başlatma

```bash
chmod +x scripts/dev.sh
./scripts/dev.sh
```

## Environment Variables

`.env` dosyasında ayarlanması gerekenler:

```env
# Google OAuth (opsiyonel)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# JWT Secret (production için değiştirin)
JWT_SECRET_KEY=your-secret-key
```

## API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/auth/register` | POST | Kayıt |
| `/api/auth/login` | POST | Giriş |
| `/api/auth/google` | POST | Google OAuth |
| `/api/search/quran` | POST | Kuran'da ara |
| `/api/search/bible` | POST | İncil'de ara |
| `/api/stream/search` | GET | SSE streaming arama |
| `/api/compare/` | POST | Karşılaştırmalı analiz |

## Tech Stack

- **Frontend:** Vue 3 + Vite + Tailwind CSS + Pinia
- **Backend:** FastAPI + SQLAlchemy + JWT
- **Database:** PostgreSQL + Qdrant
