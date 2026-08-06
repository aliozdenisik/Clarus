

<div align="center">

# Clarus

**Motor de búsqueda RAG de máxima precisión para textos sagrados**

Análisis teológico comparativo entre el Corán y la Biblia con síntesis LLM multiagente,
búsqueda de palabras clave morfológicas, recuperación semántica multiconsulta con fusión RRF y localización completa en TR/EN.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&style=flat-square)](https://github.com/pre-commit/pre-commit)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000.svg?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-DC382D.svg?style=flat-square&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![Redis](https://img.shields.io/badge/Redis-DC382D.svg?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Sponsor](https://img.shields.io/badge/Sponsor-Polar.sh-6366F1.svg?style=flat-square)](https://polar.sh/claruss)

[✨ Características](#-features) · [🏗️ Arquitectura](#-architecture) · [📦 Colecciones](#-collections) · [🚀 Inicio rápido](#-quick-start) · [📖 Uso](#-usage) · [📡 Referencia de la API](#-api-reference) · [🛠️ Pila tecnológica](#-tech-stack) · [📊 Rendimiento](#-performance) · [🧪 Pruebas](#-testing) · [🤝 Contribuir](#-contributing)

</div>

---

![Hub Dashboard](docs/screenshots/readme-hub.png)

---

## Descripción general

Clarus es un sistema RAG de grado de producción diseñado para **máxima precisión de recuperación** en textos religiosos. Indexa ~123.000 vectores de versículos a través de 13 colecciones (8 traducciones del Corán + Antiguo/Testamento/NT/Apócrifos de la Biblia en inglés y turco), y luego utiliza búsqueda semántica multiconsulta con Fusión de Ranking Recíproco (RRF) para mostrar los pasajes más relevantes antes de entregarlos a un pipeline LLM de 5 agentes para síntesis teológica comparativa.

El sistema está diseñado para investigadores, desarrolladores y cualquier persona que desee un análisis intertextual de calidad académica sin el ruido de una búsqueda por palabras clave naive.

### ✦ Aspectos destacados

- **Búsqueda Semántica Multiconsulta** — Embeddings densos (text-embedding-3-large, 3072-dim) con 3-5 variantes de consulta generadas por LLM fusionadas mediante RRF (k=60) para lograr un recall que ninguna consulta individual logra por sí sola
- **Síntesis Multiagente** — 5 agentes especializados (Corán, AT, NT, Apócrifos, Resumen) se ejecutan en paralelo y convergen en un ensayo comparativo estructurado con citas en línea
- **Búsqueda Morfológica de Palabras Clave** — Extracción de raíces árabes a través de 1.651 raíces y 77.429 palabras; concordancia Strong's hebrea/griega para AT y NT
- **Puntuación de Confianza** — Puntuación calibrada sigmoidea en dos fases (escalado de Platt) que reemplaza los promedios ponderados naive para una confianza de recuperación calibrada
- **Segmentación Semántica** — Agrupación de versículos basada en embeddings que preserva los límites bíblicos en lugar de dividir por recuentos arbitrarios de tokens
- **Infraestructura de Producción** — Better Auth, caché semántica de Redis (reducción de costos del 60-80%), streaming SSE, circuit breakers, observabilidad con Sentry
- **i18n Completa** — Localización completa TR/EN con next-intl, detección Accept-Language y caché de respuestas LLM consciente de la localización
- **13 Colecciones** — ~123.000 vectores indexados en 8 traducciones del Corán + Biblia AT/NT/Apócrifos en EN+TR

---

## ✨ Características

### Búsqueda y recuperación

| Característica | Descripción |
|---------|-------------|
| **Búsqueda Semántica** | Embeddings densos (3072-dim, text-embedding-3-large) para recuperación contextual de versículos en todas las 13 colecciones |
| **Búsqueda Multiconsulta** | 3-5 variantes de consulta generadas por LLM buscadas en paralelo y fusionadas mediante RRF para mayor recall que una consulta única |
| **Segmentación Semántica** | Agrupa versículos semánticamente relacionados preservando los límites scripturales; implementaciones separadas para Corán y Biblia |
| **RAG Multiconsulta** | 3-5 variantes de consulta generadas por LLM por solicitud, todas fusionadas mediante RRF para máximo recall |
| **Mejora de Consulta** | Gemini 2.5 Flash expande consultas con sinónimos, conceptos relacionados y términos multilingües |
| **Fusión RRF** | Reciprocal Rank Fusion (k=60) fusiona resultados multiconsulta en una única lista ordenada |
| **Caché Semántico** | Caché de similitud de embeddings respaldado por Redis; reducción del 60-80% en los costos de la API de OpenAI |
| **Consultas Multilingües** | Consulta en 8 idiomas (TR, EN, ES, FR, IT, PT, AR, DE) con detección y traducción automática |

### Análisis comparativo multiagente

```
Consulta → [QuranAgent, OTAgent, NTAgent, ApocryphaAgent] → SummaryAgent → Ensayo
```

Cada agente busca en su propia colección de forma independiente, genera un comentario enfocado y pasa sus hallazgos al agente Resumen. El agente Resumen sintetiza las cuatro perspectivas en un ensayo comparativo estructurado de 5 párrafos con citas en línea. Los agentes se ejecutan en paralelo mediante `asyncio.gather` para mantener la latencia manejable.

| Agente | Colección | Rol |
|-------|------------|------|
| QuranAgent | `quran_tr_*` | Perspectiva y comentario coránico (Turco) |
| OldTestamentAgent | `bible_ot` | Torá, Profetas y Escritos (KJVA) |
| NewTestamentAgent | `bible_nt` | Evangelios y Epístolas (KJVA) |
| ApocryphaAgent | `bible_apocrypha` | Textos deuterocanónicos (KJVA) |
| SummaryAgent | -- | Sintetiza todas las perspectivas en un ensayo comparativo cohesivo |

### Búsqueda morfológica de palabras clave

Búsqueda basada en raíces que va más allá de la coincidencia de cadenas para encontrar todos los derivados morfológicos de una raíz a través del corpus.

| Escritura | Entrada | Enfoque |
|-----------|-------|----------|
| **Corán** | Árabe (كتب) o Latín Buckwalter (ktb) | Extracción de raíz vía búsqueda en PostgreSQL (77.429 palabras, 1.651 raíces) |
| **Biblia AT** | Hebreo o transliteración (torah, chesed) | Concordancia Strong's con raíces hebreas e indexación dual b/v |
| **Biblia NT** | Griego o transliteración (agape, logos) | Concordancia Strong's con mapeo de lemas griegos |

Los resultados incluyen gráficos de distribución de surah/capítulo, recuentos de frecuencia y contexto a nivel de versículo para cada ocurrencia.

### Base de datos de etimología

Clarus incluye una base de datos de etimología de raíces árabes que cubre las 1.651 raíces coránicas con definiciones, análisis morfológico y referencias cruzadas al Diccionario de Lane.

| Campo | Descripción | Fuente |
|-------|-------------|--------|
| **Raíz (Árabe)** | Raíz árabe original | Quranic Arabic Corpus v0.4 |
| **Raíz (Buckwalter)** | Transliteración latina | Quranic Arabic Corpus v0.4 |
| **Definición en Inglés** | Definición del Diccionario de Lane | Lane's Arabic-English Lexicon (1863) |
| **Definición en Turco** | Traducción en contexto coránico | Generada por LLM (Gemini 2.5 Flash) |
| **Formas Morfológicas** | Análisis de patrones verbo/sustantivo | Extraído de `qm_words` |
| **Frecuencia Coránica** | Recuento de ocurrencias en el Corán | Quranic Arabic Corpus v0.4 |

**Fuentes de datos y citas académicas:**

- **Quranic Arabic Corpus v0.4** — Universidad de Leeds (GNU GPL)
  - Dukes, K. & Habash, N. (2010). "Anotación Morfológica del Árabe Coránico." *LREC 2010*.
  - 77.429 palabras, 1.651 raíces únicas
- **Diccionario Árabe-Inglés de Lane** — Edward William Lane (1863), digitalizado por Perseus/Universidad Tufts (GPL-3.0)
  - 47.919 entradas, 5.160 raíces en PostgreSQL
  - Coincide con 1.337 de las 1.651 raíces coránicas (81%)
- **Definiciones en Turco** — Generadas vía Google Gemini 2.5 Flash (OpenRouter)
  - Incluyen puntuaciones de confianza (0.0-1.0) por traducción
  - Las tradiciones utilizan terminología turca coránica/islámica
  - 314 raíces exclusivas del corpus reciben definiciones generadas por LLM (no hay fuente en inglés disponible)
  - No verificado manualmente por eruditos humanos

> **Nota:** Los datos de etimología están bajo licencia GPL debido a las licencias de origen del Quranic Arabic Corpus y el Diccionario de Lane.

### Internacionalización (i18n)

Localización completa en Turco/Inglés en toda la pila:

| Componente | Implementación |
|-----------|----------------|
| **Frontend** | next-intl con catálogos de mensajes basados en namespaces (TR/EN) |
| **Backend** | Mensajes de error conscientes de localización con soporte para cabecera Accept-Language |
| **Caché LLM** | Claves de caché conscientes de localización que evitan coincidencias de caché entre idiomas |
| **SEO** | Etiquetas hreflang, metadatos conscientes de localización y navegación de cambio de idioma |
| **Pruebas** | Verificaciones de completitud y calidad de traducción |

### Infraestructura de producción

- **Autenticación** — [Better Auth](https://www.better-auth.com/) con JWT + OAuth de Google + soporte para claves API para acceso CLI
- **Caché** — Redis Stack 7.2 con caché semántico LLM, caché de embeddings y resiliencia fail-open (la aplicación funciona sin Redis)
- **Streaming** — Server-Sent Events para entrega de respuesta token por token con indicadores de progreso en tiempo real
- **Observabilidad** — Registro estructurado con IDs de correlación, seguimiento de errores con Sentry, spans de rendimiento
- **Resiliencia** — Circuit breakers (pybreaker) + reintentos tenacity para todas las llamadas a servicios externos
- **Calidad de Código** — 11 hooks pre-commit (Ruff, ESLint, Prettier, Pyright, TypeScript, gitleaks, codespell)
- **CI/CD** — GitHub Actions con puertas de lint, formato, typecheck y pruebas en cada push y PR

---

## 🏗️ Arquitectura

```mermaid
graph LR
  subgraph Frontend
    A[Next.js 16 / React 19] --> B[TanStack Query]
    B --> C[SSE Streaming]
  end
  subgraph Backend
    D[FastAPI] --> E[Query Enhancement]
    E --> F[Multi-Query 3-5x]
    F --> G[Parallel Search]
    G --> H[RRF Fusion k=60]
    H --> I[Multi-Agent System]
  end
  subgraph Data
    J[(Qdrant - 123K vectors)]
    K[(PostgreSQL - Morphology)]
    L[(Redis - Cache/Rate)]
  end
  C --> D
  G --> J
  I --> K
  D --> L
```

### Pipeline RAG (Paso a paso)

```
Consulta del Usuario
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Mejora de Consulta (Gemini 2.5 Flash)                   │
│     Expandir con sinónimos, conceptos relacionados,         │
│     términos multilingües                                    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Generación Multiconsulta (3-5 variantes)                │
│     Formas diversas de fraseo para maximizar el recall      │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Búsqueda Semántica Paralela (todas las colecciones)     │
│     Vectores densos (text-embedding-3-large, 3072-dim)      │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Fusión RRF (k=60)                                       │
│     Fusionar resultados multiconsulta en una lista única    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Síntesis Multiagente (Gemini 2.5 Flash)                 │
│     [QuranAgent, OTAgent, NTAgent, ApocryphaAgent]          │
│                         │                                   │
│                    SummaryAgent                             │
│                         │                                   │
│                  Ensayo Comparativo                         │
└─────────────────────────────────────────────────────────────┘
```

### Pipeline de 5 agentes

```
                    ┌─────────────────┐
                    │   Consulta      │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │ QuranAgent  │   │  OTAgent    │   │  NTAgent    │
   │ quran_tr_*  │   │  bible_ot   │   │  bible_nt   │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │                  │                  │
          │         ┌────────┴────────┐         │
          │         │ ApocryphaAgent  │         │
          │         │ bible_apocrypha │         │
          │         └────────┬────────┘         │
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  SummaryAgent   │
                    │  (sintetiza)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Ensayo          │
                    │ Comparativo (5) │
                    └─────────────────┘
```

---

## 📦 Colecciones

| Colección | Versículos | Idioma | Fuente |
|------------|--------|----------|--------|
| `quran_tr_diyanet` | 6.236 | Turco | Traducción Diyanet Isleri |
| `quran_tr_yazir` | 6.236 | Turco | Elmalili Hamdi Yazir |
| `quran_tr_ates` | 6.236 | Turco | Suleyman Ates |
| `quran_tr_bulac` | 6.236 | Turco | Ali Bulac |
| `quran_tr_ozturk` | 6.236 | Turco | Yasar Nuri Ozturk |
| `quran_tr_vakfi` | 6.236 | Turco | Diyanet Vakfi |
| `quran_tr_yildirim` | 6.236 | Turco | Suat Yildirim |
| `quran_tr_yuksel` | 6.236 | Turco | Edip Yuksel |
| `bible_ot` | 23.145 | Inglés | Antiguo Testamento (KJVA) |
| `bible_nt` | 7.957 | Inglés | Nuevo Testamento (KJVA) |
| `bible_apocrypha` | 5.717 | Inglés | Apócrifos (KJVA) |
| `bible_tr_ot` | 22.724 | Turco | Antiguo Testamento (Turco) |
| `bible_tr_nt` | 7.458 | Turco | Nuevo Testamento (Turco) |

**Total: ~123.000 vectores indexados en 13 colecciones**

---

## 🚀 Inicio rápido

### Prerrequisitos

| Requisito | Versión | Propósito |
|-------------|---------|---------|
| Python | 3.11+ | Runtime del backend |
| Node.js | 18+ | Runtime del frontend |
| Docker | Última | Qdrant, PostgreSQL, Redis |
| [uv](https://docs.astral.sh/uv/) | Última | Gestor de paquetes de Python |

### 1. Clonar e instalar

```bash
git clone https://github.com/aliozdenisik/Clarus.git
cd Clarus

# Backend
cd backend
uv sync
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### 2. Configurar el entorno

Crea `backend/.env`:

```env
# Requerido
OPENROUTER_API_KEY=your-openrouter-key

# Base de datos (los valores por defecto de Docker funcionan directamente)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:54322/postgres

# Better Auth (para autenticación de la IU web)
BETTER_AUTH_JWKS_URL=http://localhost:3000/api/auth/jwks
BETTER_AUTH_ISSUER=http://localhost:3000

# Limitación de tasa (el valor por defecto en la config del backend es true)
# Establecer en false localmente si necesitas desactivar los límites durante desarrollo/pruebas
RATE_LIMIT_ENABLED=false
```

Crea `frontend/.env.local`:

```env
BETTER_AUTH_DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres

# Genera un secreto aleatorio de 32+ caracteres para firma de sesiones
# Ejecuta: openssl rand -base64 32
BETTER_AUTH_SECRET=your-random-secret-replace-with-generated-value

NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Opcional: OAuth de Google
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Generar el secreto de autenticación:**

```bash
# macOS/Linux
openssl rand -base64 32

# O usa Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

### 3. Iniciar infraestructura

```bash
# Iniciar PostgreSQL + Qdrant + Redis
docker compose up -d

# Indexar todas las colecciones (solo la primera vez, ~2 minutos)
cd backend
uv run python scripts/setup_all_collections.py

# Verificar
uv run python main.py info
```

### 4. Ejecutar

```bash
# Opción A: Pila completa (API + IU Web)
cd backend && uvicorn app.main:app --reload &
cd frontend && npm run dev &

# Opción B: Solo CLI
cd backend
uv run python main.py search "sabir ve namaz"
```

| Servicio | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Docs API (Swagger) | http://localhost:8000/docs |
| Panel Qdrant | http://localhost:6333/dashboard |
| Redis Insight | http://localhost:8001 |

---

## 📖 Uso

### CLI

```bash
cd backend

# Búsqueda
uv run python main.py search "sabir ve namaz"                    # Corán (por defecto: Diyanet)
uv run python main.py search --translator yazir "sabir"          # Corán (traducción Yazir)
uv run python main.py search-bible "love your neighbor"          # Biblia (KJVA)

# Preguntas y Respuestas
uv run python main.py ask "Islam'da sabir nedir?"                # P&R Corán
uv run python main.py ask-bible "What is love?"                  # P&R Biblia

# Análisis Comparativo
uv run python main.py compare "The concept of forgiveness"       # Ensayo único
uv run python main.py compare --multi-agent "The creation story" # Análisis 5 agentes

# Búsqueda Morfológica de Palabras Clave
uv run python main.py keyword-search "كتب"                      # Raíz árabe
uv run python main.py keyword-search "ktb"                       # Latín Buckwalter
uv run python main.py bible-keyword-search "torah"               # Transliteración hebrea
uv run python main.py bible-keyword-search "G2316"               # Número Strong's griego

# Sistema
uv run python main.py info                                       # Estadísticas de colecciones
uv run python main.py cache-info                                 # Estadísticas de caché
uv run python main.py cache-clear                                # Limpiar caché
```

### API de Python

```python
import asyncio
from src.ultimate_rag import UltimateRAG
from src.comparative_rag import ComparativeRAG

async def main():
    # Búsqueda semántica
    rag = UltimateRAG(enable_semantic_chunks=True)
    results = await rag.search_quran("intercession concept", top_k=5)
    answer = await rag.ask_bible("What is forgiveness?")

    # Análisis comparativo multiagente
    comp = ComparativeRAG()
    result = await comp.compare_multi_agent("Creation and the origin of humanity")
    print(result["paragraphs"])

asyncio.run(main())
```

### Capturas de pantalla

<table>
  <tr>
    <td align="center"><strong>Búsqueda Semántica</strong></td>
    <td align="center"><strong>Análisis Comparativo</strong></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/readme-search.png" alt="Búsqueda" width="500"/></td>
    <td><img src="docs/screenshots/readme-compare.png" alt="Comparar" width="500"/></td>
  </tr>
  <tr>
    <td align="center"><strong>Búsqueda Morfológica de Palabras</strong></td>
    <td align="center"><strong>Navegación Coránica</strong></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/readme-keyword-search.png" alt="Búsqueda de Palabras Clave" width="500"/></td>
    <td><img src="docs/screenshots/readme-quran-browse.png" alt="Navegación Coránica" width="500"/></td>
  </tr>
</table>

---

## 📡 Referencia de la API

La documentación OpenAPI completa está disponible en `/docs` cuando el servidor está en ejecución.

### Búsqueda

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|------|
| `/api/search/quran` | POST | Búsqueda semántica del Corán con selección de traductor | Sí |
| `/api/search/bible` | POST | Búsqueda semántica de la Biblia (AT/NT/Apócrifos) | Sí |
| `/api/stream/search` | GET | Búsqueda con streaming SSE | Sí |
| `/api/enhance/` | POST | Vista previa de mejora de consulta | Sí |

### Comparar

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|------|
| `/api/compare/` | POST | Análisis comparativo multiagente | Sí |
| `/api/stream/compare` | GET | Comparación con streaming SSE | Sí |

### Palabras Clave y Morfología

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|------|
| `/api/search/keyword/` | POST | Búsqueda morfológica de raíces del Corán | -- |
| `/api/search/keyword/roots` | GET | Listar todas las raíces árabes (paginado) | -- |
| `/api/search/bible-keyword/` | POST | Búsqueda morfológica de la Biblia | -- |
| `/api/etymology/` | GET | Etimología de raíces árabes del Diccionario de Lane | -- |

### Búsqueda de Versículos

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|------|
| `/api/verse-lookup/` | POST | Buscar versículo por referencia | Sí |
| `/api/verse-translations/` | GET | Obtener versículo en las 8 traducciones del Corán | Sí |

### Autenticación y Usuario

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/auth/api-key` | POST | Generar clave API para CLI |
| `/api/auth/me` | GET | Información del usuario actual |
| `/api/auth/rate-limit` | GET | Estado del límite de tasa |

### Metadatos y Estado

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/metadata/collections` | GET | Estadísticas de colecciones Qdrant |
| `/api/metadata/quran/surahs` | GET | Las 114 surahs |
| `/api/metadata/bible/books` | GET | Todos los libros de la Biblia |
| `/api/health` | GET | Verificación de estado (Qdrant, Redis, event loop) |
| `/docs` | GET | OpenAPI / Swagger UI |

---

## 🛠️ Pila tecnológica

### Backend

| Componente | Tecnología |
|-----------|------------|
| Framework | FastAPI (async) + SQLAlchemy 2.0 |
| Runtime | Python 3.11+ con [uv](https://docs.astral.sh/uv/) |
| Vector DB | Qdrant (HNSW + Scalar Quantization) |
| Base de Datos | PostgreSQL 15 |
| Caché | Redis Stack 7.2 (caché semántico LLM, caché de búsqueda, lista negra JWT) |
| Encoder | OpenAI text-embedding-3-large (3072-dim) |
| LLM (Mejora) | Gemini 2.5 Flash vía OpenRouter |
| LLM (Generación) | Gemini 2.5 Flash vía OpenRouter |
| LLM (Traducción) | Gemini 2.5 Flash Lite vía OpenRouter |
| Autenticación | Better Auth (JWT + OAuth de Google + JWKS) |
| Observabilidad | Sentry + registro estructurado + IDs de correlación |
| Resiliencia | Circuit breakers (pybreaker) + reintentos tenacity |

### Frontend

| Componente | Tecnología |
|-----------|------------|
| Framework | Next.js 16 (App Router) |
| Runtime | React 19, TypeScript 5 |
| Estilos | Tailwind CSS 4 + primitivos Radix UI |
| Animación | Framer Motion 12 |
| Estado | Zustand 5 + TanStack Query 5 + nuqs |
| Cliente API | Generado vía @hey-api/openapi-ts |
| UI de Auth | @daveyplate/better-auth-ui |
| Pruebas | Vitest 4 + React Testing Library (228+ pruebas) |
| E2E | Playwright |
| Gráficos | Recharts 3 |
| i18n | next-intl (EN, TR) |

### Infraestructura

| Componente | Tecnología |
|-----------|------------|
| Contenedores | Docker Compose (PostgreSQL + Qdrant + Redis) |
| CI | GitHub Actions (lint, formato, typecheck, pruebas) |
| Pre-commit | 11 hooks (Ruff, ESLint, Prettier, gitleaks, codespell, etc.) |
| Linting | Ruff (20 conjuntos de reglas) + ESLint 9 |
| Formato | Ruff (Python) + Prettier (TypeScript) |
| Verificación de Tipos | Pyright + TypeScript estricto |

---

## 📊 Rendimiento

| Métrica | Valor |
|--------|-------|
| Recall del Corán | **80%+** |
| Recall de la Biblia | **100%** |
| Puntuación de Confianza | **96%** |
| Latencia Multiagente | ~40s |
| Costo por Consulta | ~$0.013 (con caché semántico) |
| Tasa de Aciertos de Caché | Reducción del 60-80% en costos de API |
| Vectores Indexados | ~123.000 en 13 colecciones |
| Base de Datos de Morfología | 77.429 palabras, 1.651 raíces |

El recall se mide contra un conjunto de datos de verdad terreno (`backend/tests/test_data.json`) usando la puntuación F1. La caché semántica es el mayor palanca de costo: las consultas repetidas o semánticamente similares omiten el LLM por completo y devuelven resultados en caché en milisegundos.

---

## 🧪 Pruebas

### Frontend

```bash
cd frontend
npm test                          # Vitest (228+ pruebas, 21 archivos)
npm run test:e2e                  # Playwright E2E
npx tsc --noEmit                  # Verificación de tipos
```

### Backend

```bash
cd backend
uv run pytest tests/ -v           # Pruebas unitarias
uv run ruff check .               # Lint
uv run ruff format --check .      # Verificación de formato
uv run pyright                    # Verificación de tipos
```

### Hooks Pre-commit

```bash
# Instalar (una sola vez)
pre-commit install
pre-commit install --hook-type pre-push

# Ejecutar en todos los archivos
pre-commit run --all-files
```

El套件 pre-commit ejecuta 11 hooks: lint y formato con Ruff, ESLint, Prettier, Pyright, TypeScript `noEmit`, gitleaks (escaneo de secretos), codespell y verificaciones de espacios finales. Todos los hooks se ejecutan en cada commit; los hooks de push ejecutan la suite completa de verificación de tipos.

---

## 📁 Estructura del proyecto

```
Clarus/
├── backend/                        # Python FastAPI + pipeline RAG
│   ├── main.py                     # Punto de entrada CLI (formato Rich, 1.871 líneas)
│   ├── app/                        # Aplicación FastAPI
│   │   ├── main.py                 # Servidor ASGI
│   │   ├── api/                    # Manejadores de rutas (15 endpoints)
│   │   ├── auth/                   # Validador JWKS + autenticación clave API
│   │   ├── i18n/                   # Detección de localización + catálogos de mensajes
│   │   ├── middleware/             # CORS, ID de correlación, manejo de errores
│   │   ├── schemas/                # Modelos Pydantic (4 archivos)
│   │   └── config.py               # Configuración
│   ├── src/                        # Módulos del pipeline RAG (29 archivos)
│   │   ├── ultimate_rag.py         # Pipeline RAG principal (1.447 líneas)
│   │   ├── comparative_rag.py      # Búsqueda paralela 4 colecciones + RRF (1.414 líneas)
│   │   ├── multi_agent_answer_generator.py  # Sistema 5 agentes (805 líneas)
│   │   ├── bible_morphology.py     # Búsqueda Strong's hebrea/griega (1.900 líneas)
│   │   ├── search.py               # Búsqueda semántica Qdrant (880 líneas)
│   │   ├── quran_morphology.py     # Búsqueda morfológica de raíces árabes (607 líneas)
│   │   ├── query_enhancer.py       # Expansión de consulta LLM (729 líneas)
│   │   ├── query_translator.py     # Traducción multilingüe, 8 idiomas (613 líneas)
│   │   ├── embeddings.py           # Encoder denso OpenAI (570 líneas)
│   │   ├── confidence_scorer.py    # Puntuación calibrada sigmoidea en dos fases (376 líneas)
│   │   ├── semantic_chunker.py     # Agrupación de versículos del Corán (638 líneas)
│   │   ├── bible_semantic_chunker.py  # Agrupación de versículos de la Biblia (499 líneas)
│   │   └── ...                     # 17 módulos más
│   ├── data/                       # Datos de origen (quran_tr.json, bible_kjva.json)
│   ├── tests/                      # Pytest + benchmarks de precisión
│   └── scripts/                    # Scripts de configuración y migración
├── frontend/                       # Next.js 16 + React 19
│   ├── app/                        # App Router con [locale] (17 rutas)
│   ├── components/                 # Componentes UI (60+ archivos)
│   │   ├── ui/                     # Primitivos Radix (33 archivos)
│   │   ├── compare/                # IU de análisis comparativo (7 archivos)
│   │   ├── keyword-search/         # IU de búsqueda morfológica (12 archivos)
│   │   ├── quran/                  # Componentes específicos del Corán
│   │   ├── verse-lookup/           # Búsqueda de referencias de versículos
│   │   └── search/                 # Componentes de búsqueda
│   ├── lib/                        # Cliente API, hooks, stores (35 archivos)
│   │   ├── api/                    # Cliente TypeScript generado (tipos de 2.054 líneas)
│   │   ├── stores/                 # Gestión de estado Zustand
│   │   ├── auth/                   # Integración Better Auth
│   │   └── i18n/                   # Configuración next-intl
│   ├── messages/                   # Archivos de traducción TR/EN
│   └── __tests__/                  # Vitest + RTL (21 archivos, 228+ pruebas)
├── docs/
│   ├── screenshots/                # Capturas de pantalla de la IU
│   └── technical/                  # Documentación técnica
├── docker-compose.yml              # PostgreSQL + Qdrant + Redis
├── .pre-commit-config.yaml         # 11 hooks para calidad de código
├── .github/workflows/              # Pipelines CI
└── memory-bank/                    # Contexto del proyecto y decisiones
```

---

## 🔧 Variables de entorno

### Backend (`backend/.env`)

| Variable | Requerido | Por defecto | Descripción |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Sí | -- | Clave API de OpenRouter para todas las llamadas LLM |
| `DATABASE_URL` | Sí | -- | Cadena de conexión de PostgreSQL (asyncpg) |
| `BETTER_AUTH_JWKS_URL` | -- | `http://localhost:3000/api/auth/jwks` | Endpoint JWKS de Better Auth |
| `BETTER_AUTH_ISSUER` | -- | `http://localhost:3000` | URL de emisor JWT |
| `REDIS_URL` | -- | `redis://localhost:6379` | Cadena de conexión Redis |
| `RATE_LIMIT_PER_DAY` | -- | `50` | Consultas por usuario por día |
| `RATE_LIMIT_ENABLED` | -- | `true` | Interruptor de limitación de tasa |
| `LOG_LEVEL` | -- | `INFO` | Nivel de registro |
| `LOG_FORMAT` | -- | `console` | `console` (dev) o `json` (prod) |
| `SENTRY_DSN_BACKEND` | -- | -- | DSN de Sentry para seguimiento de errores del backend |

### Frontend (`frontend/.env.local`)

| Variable | Requerido | Por defecto | Descripción |
|----------|----------|---------|-------------|
| `BETTER_AUTH_DATABASE_URL` | Sí | -- | Conexión PostgreSQL para Better Auth |
| `BETTER_AUTH_SECRET` | Sí | -- | Secreto aleatorio de 32+ caracteres para firma de sesiones |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | -- | `http://localhost:3000` | URL base de Better Auth |
| `GOOGLE_CLIENT_ID` | -- | -- | ID de cliente OAuth de Google |
| `GOOGLE_CLIENT_SECRET` | -- | -- | Secreto de cliente OAuth de Google |
| `NEXT_PUBLIC_SENTRY_DSN` | -- | -- | DSN de Sentry para seguimiento de errores del frontend |

---

## 📚 Documentación técnica

Documentos de profundización que cubren los algoritmos y decisiones de diseño detrás de Clarus:

| Documento | Descripción |
|----------|-------------|
| [Búsqueda Multiconsulta y Fusión RRF](docs/technical/hybrid-search-and-rrf-fusion.md) | Fundamentos matemáticos de la búsqueda de vectores semánticos y la Fusión de Ranking Recíproco |
| [Sistema de Puntuación de Confianza](docs/technical/confidence-scoring-system.md) | Puntuación calibrada sigmoidea en dos fases con escalado de Platt |
| [Pipeline de Análisis Morfológico](docs/technical/morphological-analysis-pipeline.md) | Lingüística computacional para textos sagrados árabes, hebreos y griegos |
| [Arquitectura RAG Multiagente](docs/technical/multi-agent-rag-architecture.md) | Diseño del sistema de búsqueda y síntesis paralela de 5 agentes |
| [Algoritmos de Segmentación Semántica](docs/technical/semantic-chunking-algorithms.md) | Agrupación de versículos basada en embeddings con detección de límites |
| [Patrones de Caché y Resiliencia](docs/technical/caching-and-resilience-patterns.md) | Arquitectura de Redis, circuit breakers y diseño fail-open |

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. El proyecto utiliza una aplicación estricta de calidad de código mediante hooks pre-commit y puertas CI.

### Configuración

```bash
# Instalar hooks pre-commit (se ejecuta automáticamente en cada commit)
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push
```

### Flujo de trabajo

1. Haz un fork del repositorio
2. Crea una rama de característica (`git checkout -b feature/tu-caracteristica`)
3. Realiza cambios (los hooks pre-commit aplican formato y lint automáticamente)
4. Ejecuta pruebas (`cd frontend && npm test` y `cd backend && uv run pytest`)
5. Haz push y abre un Pull Request

### Estándares de Código

- **Python**: Ruff (20 conjuntos de reglas), Pyright estricto, diseño async-first
- **TypeScript**: ESLint 9, Prettier, verificación de tipos estricta `noEmit`
- Sin `any` en TypeScript; sin `# type: ignore` en Python sin justificación
- Solo registro estructurado -- sin `console.log` ni `print()` sueltos en código de producción
- Todas las llamadas Qdrant/LLM/Redis deben ser async con manejo de errores explícito

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT -- consulta el archivo [LICENSE](LICENSE) para más detalles.

La base de datos de etimología (raíces árabes, datos del Diccionario de Lane) está bajo licencia GPL debido a las licencias de las fuentes aguas arriba.

---

<div align="center">

Construido con [Qdrant](https://qdrant.tech), [FastAPI](https://fastapi.tiangolo.com), [Next.js](https://nextjs.org) y [OpenRouter](https://openrouter.ai)

**[Volver al inicio](#clarus)**

</div>
