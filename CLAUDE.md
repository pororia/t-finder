# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

T-Finder is a toilet location sharing service (화장실 위치 공유 서비스). Monorepo with a FastAPI backend and Next.js frontend, backed by PostGIS for geospatial queries and Firebase for auth/storage.

## Commands

### Backend (`/backend`)

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pytest
black .
ruff check .
mypy app
```

### Frontend (`/web`)

```bash
npm install
npm run dev
npm run build
npm run lint
```

### Infrastructure

```bash
# Full stack
cd infra && docker-compose -f docker-compose.yml up -d

# DB only (PostgreSQL 15 + PostGIS 3.4)
docker-compose -f docker-compose.db.yml up -d
```

## Architecture

### Backend — Layered

`API routes` → `Services` → `Repositories` → `SQLAlchemy async` → `PostgreSQL + PostGIS`

- **`app/api/v1/`** — route handlers, thin; delegate to services
- **`app/services/`** — business logic (auth, toilet CRUD, file uploads, audit)
- **`app/repositories/`** — DB queries via SQLAlchemy 2.0 async
- **`app/db/models/`** — ORM models; `Toilet` uses PostGIS `POINT` for geography
- **`app/core/`** — JWT security, dependency injection, Firebase client

All API responses follow: `{"success": bool, "data": ..., "error": ...}`

### Frontend — State Layers

- **TanStack Query** — server state (toilet data, reviews); bounds-based queries fetch only markers visible in the map viewport
- **Zustand** — global auth/user state
- **`lib/api/client.ts`** — Axios instance with interceptors: auto-attaches JWT, handles 401 → token refresh → retry

### Authentication Flow

1. Firebase Google sign-in → ID token
2. POST `/v1/auth/google` → backend verifies with Google, returns JWT access + refresh tokens
3. Axios interceptor attaches Bearer token; on 401 calls `/v1/auth/refresh` and retries once

### Geospatial

- Toilets stored with PostGIS `Geography(POINT)` column
- Nearby search: `ST_Distance` with radius (meters)
- Bounds search: `ST_Within` using map viewport bounding box
- Client-side distance display uses Haversine formula (`web/src/lib/utils/distance.ts`)

### Toilet Passwords

Some toilets have access codes — these are encrypted at rest with Fernet symmetric encryption (`app/utils/encryption.py`). The encryption key is set via `PASSWORD_ENCRYPTION_KEY` env var.

### Audit Trail

`ToiletHistory` model records snapshots and change types (CREATE/UPDATE/DELETE) for every toilet mutation, written by `history_service.py`.

## Key Environment Variables

**Backend** (`.env`):
```
DATABASE_URL=postgresql+asyncpg://tfinder:tfinder_dev_password@localhost:5432/tfinder
JWT_SECRET_KEY=...
FIREBASE_CREDENTIALS_PATH=./firebase-admin-sdk.json
FIREBASE_STORAGE_BUCKET=t-finder.appspot.com
PASSWORD_ENCRYPTION_KEY=<32-byte base64 fernet key>
CORS_ORIGINS=["http://localhost:3000"]
```

**Frontend** (`.env.local`):
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/v1
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=...
NEXT_PUBLIC_FIREBASE_*=...
```

## Database Init

`infra/init/01_extensions.sql` installs PostGIS and UUID extensions. Run this before any migrations. Alembic is configured but migrations must be generated manually.
