# T-Finder

화장실 위치 공유 서비스 (Toilet Location Sharing Service)

---

## 목차

1. [사전 요구사항](#사전-요구사항)
2. [외부 서비스 설정](#외부-서비스-설정)
3. [환경 변수 설정](#환경-변수-설정)
4. [DB 시작](#db-시작)
5. [Backend 시작](#backend-시작)
6. [Frontend 시작](#frontend-시작)
7. [접속 방법](#접속-방법)

---

## 사전 요구사항

| 도구 | 버전 |
|------|------|
| Docker & Docker Compose | 최신 |
| Python | 3.11 이상 |
| Node.js | 18 이상 |

---

## 외부 서비스 설정

### 1. Firebase 설정

**Firebase Console** (https://console.firebase.google.com) 에서:

1. 새 프로젝트 생성
2. **Authentication** → 로그인 제공업체 → **Google** 활성화
3. **Storage** → 시작하기 (버킷 생성됨, 예: `your-project.appspot.com`)
4. **프로젝트 설정** → **서비스 계정** → **새 비공개 키 생성** → JSON 다운로드
   - 다운로드한 파일을 `backend/firebase-admin-sdk.json` 으로 저장
5. **프로젝트 설정** → **일반** → 하단 **웹 앱 추가** → SDK 구성 복사
   - `NEXT_PUBLIC_FIREBASE_*` 환경 변수에 사용

### 2. Google Maps Platform 설정

**Google Cloud Console** (https://console.cloud.google.com) 에서:

1. 프로젝트 선택 (Firebase와 동일 프로젝트 권장)
2. **API 및 서비스** → **라이브러리** → 아래 API 활성화:
   - Maps JavaScript API
   - Places API
   - Geocoding API
3. **사용자 인증 정보** → **사용자 인증 정보 만들기** → **API 키** 생성
   - 생성된 키를 `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` 에 사용

---

## 환경 변수 설정

### Backend

```bash
cd backend
cp .env.example .env
```

`.env` 파일을 열어 아래 항목을 채웁니다:

```env
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://tfinder:tfinder_dev_password@localhost:5432/tfinder

# JWT: 32자 이상의 랜덤 문자열
JWT_SECRET_KEY=your_secret_key_here_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Firebase: 다운로드한 JSON 파일 경로
FIREBASE_CREDENTIALS_PATH=./firebase-admin-sdk.json
# Firebase Storage 버킷 이름
FIREBASE_STORAGE_BUCKET=your-project.appspot.com

# 화장실 잠금 비밀번호 암호화 키 (Fernet 32바이트 base64)
# 생성 방법: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
PASSWORD_ENCRYPTION_KEY=your_32_byte_fernet_key_here_b64=

CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend

```bash
cd web
cp .env.local.example .env.local
```

`.env.local` 파일을 열어 아래 항목을 채웁니다:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/v1

# Google Maps
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Firebase (Firebase Console → 프로젝트 설정 → 웹 앱 SDK 구성)
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

---

## DB 시작

PostgreSQL 15 + PostGIS 3.4를 Docker로 실행합니다.  
최초 실행 시 `infra/init/` 의 SQL 스크립트가 자동으로 적용되어 PostGIS, UUID 익스텐션이 설치됩니다.

```bash
cd infra
docker-compose -f docker-compose.db.yml up -d
```

상태 확인:

```bash
docker ps
# tfinder-postgres 컨테이너가 healthy 상태인지 확인

docker logs tfinder-postgres
```

DB 직접 접속:

```bash
docker exec -it tfinder-postgres psql -U tfinder -d tfinder
```

---

## Backend 시작

### 의존성 설치

```bash
cd backend
pip install -e ".[dev]"
```

### Fernet 암호화 키 생성 (최초 1회)

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

출력된 키를 `.env`의 `PASSWORD_ENCRYPTION_KEY`에 입력합니다.

### 서버 실행

DB가 먼저 실행 중이어야 합니다.

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Frontend 시작

```bash
cd web
npm install
npm run dev
```

---

## 접속 방법

| 서비스 | URL |
|--------|-----|
| **Frontend** (Next.js) | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API 문서 (Swagger)** | http://localhost:8000/docs |
| **API 문서 (ReDoc)** | http://localhost:8000/redoc |
| **PostgreSQL** | localhost:5432 (user: `tfinder`, pw: `tfinder_dev_password`, db: `tfinder`) |

---

## 전체 스택 Docker 실행 (선택)

Backend까지 Docker로 함께 실행하려면 (`backend/firebase-admin-sdk.json` 이 있어야 합니다):

```bash
cd infra
docker-compose -f docker-compose.yml up -d
```
