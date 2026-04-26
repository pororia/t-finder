# T-Finder 프로그램 명세서

**버전**: v1.0.0  
**작성일**: 2026-04-26  
**상태**: 운영 배포 완료

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 서비스명 | T-Finder (티파인더) |
| 설명 | 화장실 위치 공유 서비스 — 주변 공중화장실을 지도에서 찾고, 사용자가 직접 등록·리뷰할 수 있는 플랫폼 |
| 저장소 | https://github.com/pororia/t-finder.git (dev 브랜치) |
| 프론트엔드 URL | https://t-finder--t-finder-10310.us-central1.hosted.app |
| 백엔드 URL | https://tfinder-backend-848358983898.us-central1.run.app |

---

## 2. 시스템 아키텍처

```
사용자 (브라우저)
    │
    ▼
Firebase App Hosting (Next.js 14)
    │  Bearer JWT
    ▼
Google Cloud Run (FastAPI)
    │  asyncpg
    ▼
Cloud SQL (PostgreSQL 15 + PostGIS 3.4)

Firebase Auth  ──→  백엔드 ID 토큰 검증
Firebase Storage ──→  화장실 사진 저장
Google Maps API ──→  지도 렌더링, 역지오코딩
```

### 레이어 구조 (백엔드)

```
API Routes (app/api/v1/)
    → Services (app/services/)
        → Repositories (app/repositories/)
            → SQLAlchemy 2.0 Async
                → PostgreSQL + PostGIS
```

---

## 3. 기술 스택

### 백엔드

| 항목 | 기술 |
|------|------|
| 언어 | Python 3.11 |
| 프레임워크 | FastAPI |
| ORM | SQLAlchemy 2.0 (async) + asyncpg |
| 지리공간 | GeoAlchemy2 + PostGIS 3.4 |
| 인증 | Firebase Admin SDK + JWT (HS256) |
| 파일 저장 | Firebase Storage |
| 암호화 | Fernet 대칭 암호화 (비밀번호 필드) |
| Rate Limiting | slowapi |
| 배포 | Google Cloud Run |

### 프론트엔드

| 항목 | 기술 |
|------|------|
| 언어 | TypeScript |
| 프레임워크 | Next.js 14 (App Router) |
| 서버 상태 | TanStack Query v5 |
| 전역 상태 | Zustand |
| HTTP 클라이언트 | Axios (인터셉터: JWT 자동 첨부, 401 자동 재시도) |
| 지도 | Google Maps JavaScript API |
| 스타일 | Tailwind CSS |
| 폼 검증 | React Hook Form + Zod |
| 알림 | react-hot-toast |
| 배포 | Firebase App Hosting |

### 인프라

| 항목 | 기술 |
|------|------|
| 데이터베이스 | Cloud SQL (PostgreSQL 15 + PostGIS 3.4) |
| 인스턴스명 | `tfinder-db` (us-central1) |
| DB명 | `tfinder` |
| 인증 | Firebase Authentication (Google OAuth) |
| 스토리지 | Firebase Storage (화장실 사진) |

---

## 4. 인증 플로우

1. 클라이언트: Firebase Google 로그인 → Firebase ID 토큰 획득
2. 클라이언트: `POST /v1/auth/google` with `id_token`
3. 백엔드: Firebase Admin SDK로 ID 토큰 검증 → 사용자 조회/생성
4. 백엔드: JWT access token + refresh token 발급 후 응답
5. 클라이언트: Axios 인터셉터가 모든 요청에 `Authorization: Bearer {access_token}` 자동 첨부
6. 401 수신 시: `POST /v1/auth/refresh` 호출 후 원본 요청 자동 재시도

---

## 5. API 명세

모든 응답 형식: `{"success": bool, "data": ..., "error": ...}`

Base URL: `https://tfinder-backend-848358983898.us-central1.run.app/v1`

### 5.1 인증 (`/auth`)

| 메서드 | 경로 | 인증 필요 | 설명 |
|--------|------|-----------|------|
| POST | `/auth/google` | 불필요 | Firebase ID 토큰으로 로그인. 응답: `access_token`, `refresh_token`, `user` |
| POST | `/auth/refresh` | Refresh Token | Access Token 갱신 |
| GET | `/auth/me` | 필요 | 현재 로그인 사용자 정보 조회 |
| POST | `/auth/logout` | 필요 | 로그아웃 |

### 5.2 사용자 (`/users`)

| 메서드 | 경로 | 인증 필요 | 설명 |
|--------|------|-----------|------|
| GET | `/users/me` | 필요 | 내 프로필 조회 |

### 5.3 화장실 검색 (`/toilets` — 검색)

> 주의: 이 라우터는 `/{toilet_id}` 패턴보다 먼저 등록되어야 함

| 메서드 | 경로 | 인증 필요 | 설명 |
|--------|------|-----------|------|
| GET | `/toilets/nearby` | 불필요 | 반경 내 화장실 조회. 파라미터: `lat`, `lng`, `radius`(m, 기본 1000) |
| GET | `/toilets/search` | 불필요 | 키워드 검색. 파라미터: `q` |
| GET | `/toilets/in-bounds` | 불필요 | 지도 뷰포트 범위 내 화장실 조회. 파라미터: `min_lat`, `min_lng`, `max_lat`, `max_lng` |

### 5.4 화장실 CRUD (`/toilets`)

| 메서드 | 경로 | 인증 필요 | 설명 |
|--------|------|-----------|------|
| GET | `/toilets` | 불필요 | 화장실 목록 (페이지네이션: `offset`, `limit`) |
| POST | `/toilets` | 필요 | 화장실 등록 (Rate limit: 5회/분) |
| GET | `/toilets/{id}` | 선택 | 화장실 상세 조회. 로그인 시 비밀번호 복호화 값 포함 |
| PUT | `/toilets/{id}` | 필요 | 화장실 수정 (등록자만 가능) |
| DELETE | `/toilets/{id}` | 필요 | 화장실 삭제 (등록자 또는 ADMIN) |
| GET | `/toilets/{id}/history` | 불필요 | 변경 이력 조회 |

### 5.5 사진 (`/toilets/{id}/photos`)

| 메서드 | 경로 | 인증 필요 | 설명 |
|--------|------|-----------|------|
| POST | `/toilets/{id}/photos` | 필요 | 사진 업로드. 형식: jpeg/png/webp, 최대 5MB, 최대 5장/화장실 |
| DELETE | `/toilets/{id}/photos/{photo_id}` | 필요 | 사진 삭제 (업로더만 가능) |

### 5.6 리뷰

| 메서드 | 경로 | 인증 필요 | 설명 |
|--------|------|-----------|------|
| GET | `/toilets/{id}/reviews` | 불필요 | 리뷰 목록 조회 |
| POST | `/toilets/{id}/reviews` | 필요 | 리뷰 등록 (화장실당 1인 1개) |
| PUT | `/reviews/{review_id}` | 필요 | 리뷰 수정 (본인만) |
| DELETE | `/reviews/{review_id}` | 필요 | 리뷰 삭제 (본인만) |

---

## 6. 데이터베이스 스키마

### `users`

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID (PK) | 사용자 고유 ID |
| google_uid | VARCHAR(128) UNIQUE | Firebase UID |
| email | VARCHAR(255) UNIQUE | 이메일 |
| nickname | VARCHAR(50) | 닉네임 |
| profile_image_url | TEXT | 프로필 이미지 URL |
| role | ENUM('USER','ADMIN') | 역할 (DB 타입명: `user_role`) |
| is_active | BOOLEAN | 활성 여부 |
| created_at | TIMESTAMPTZ | 가입일 |
| updated_at | TIMESTAMPTZ | 수정일 |
| last_login_at | TIMESTAMPTZ | 마지막 로그인 |

### `toilets`

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID (PK) | 화장실 고유 ID |
| location | Geography(POINT, 4326) | 위경도 (PostGIS) |
| address | VARCHAR(500) | 도로명 주소 |
| address_detail | VARCHAR(200) | 상세 주소 |
| name | VARCHAR(200) | 화장실 이름 (선택) |
| cleanliness | SMALLINT | 청결도 1~5 (CHECK 제약) |
| description | TEXT | 설명 |
| has_password | BOOLEAN | 비밀번호 여부 |
| password_value | VARCHAR(100) | 비밀번호 (Fernet 암호화) |
| is_unisex | BOOLEAN | 남녀 공용 여부 |
| is_accessible | BOOLEAN | 장애인 이용 가능 여부 |
| seat_count | SMALLINT | 좌변기 수 (공용) |
| urinal_count | SMALLINT | 소변기 수 (공용) |
| male_seat_count | SMALLINT | 남자 좌변기 수 |
| male_urinal_count | SMALLINT | 남자 소변기 수 |
| female_seat_count | SMALLINT | 여자 좌변기 수 |
| payment_type | ENUM('FREE','PAID') | 이용 요금 유형 (DB 타입명: `payment_type`) |
| cost | INTEGER | 이용 요금 (원, 유료일 때) |
| created_by | UUID (FK → users) | 등록자 |
| is_deleted | BOOLEAN | 소프트 삭제 여부 |
| created_at | TIMESTAMPTZ | 등록일 |
| updated_at | TIMESTAMPTZ | 수정일 |

### `toilet_photos`

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID (PK) | 사진 고유 ID |
| toilet_id | UUID (FK → toilets) | 화장실 ID |
| image_url | TEXT | Firebase Storage 공개 URL |
| storage_path | TEXT | Firebase Storage 내부 경로 |
| display_order | SMALLINT | 표시 순서 |
| uploaded_by | UUID (FK → users) | 업로더 |
| created_at | TIMESTAMPTZ | 업로드일 |

### `reviews`

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID (PK) | 리뷰 고유 ID |
| toilet_id | UUID (FK → toilets) | 화장실 ID |
| user_id | UUID (FK → users) | 작성자 |
| rating | SMALLINT | 평점 1~5 |
| comment | TEXT | 리뷰 내용 |
| created_at | TIMESTAMPTZ | 작성일 |
| updated_at | TIMESTAMPTZ | 수정일 |

> 제약: 사용자당 화장실 1개에 1개의 리뷰만 작성 가능

### `toilet_history`

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID (PK) | 이력 고유 ID |
| toilet_id | UUID (FK → toilets) | 화장실 ID |
| snapshot | JSONB | 변경 시점 전체 데이터 스냅샷 |
| changed_fields | TEXT[] | 변경된 필드 목록 |
| change_type | VARCHAR | CREATE / UPDATE / DELETE |
| changed_by | UUID (FK → users) | 변경자 |
| changed_at | TIMESTAMPTZ | 변경 시각 |

---

## 7. 주요 기능 명세

### 7.1 지도 (메인 화면)

- Google Maps 기반 지도 렌더링
- 지도 뷰포트(Bounds) 변경 시 `GET /toilets/in-bounds` 자동 호출 (TanStack Query bounds-based fetch)
- 화장실 마커: 청결도(1~5) 숫자를 원형 아이콘으로 표시
- 마커 클릭 시 화장실 상세 페이지로 이동

### 7.2 화장실 등록

- 지도 클릭으로 위치 선택
- 위치 선택 시 Google Maps Geocoder API로 역지오코딩 → 주소 자동 입력
- 선택된 위도/경도 좌표를 지도 하단에 표시
- 남녀 공용 여부에 따라 변기 수 입력 UI 분기:
  - 공용: 좌변기/소변기 (단일 섹션)
  - 비공용: 남자(파란색 — 좌변기+소변기) / 여자(분홍색 — 좌변기) 구분 입력
- 유료인 경우 금액(원) 추가 입력
- 비밀번호 있음 체크 시 비밀번호 입력 (Fernet 암호화 저장)
- Rate Limit: 분당 5회 등록 제한

### 7.3 화장실 상세

- 사진 캐러셀 (최대 5장)
- 청결도 별점 + 평균 평점 / 리뷰 수 표시
- 시설 배지: 장애인 가능, 남녀 공용, 비밀번호 있음, 무료/유료
- 비밀번호: 로그인한 사용자에게만 복호화된 값 표시
- 남녀 구분 변기 수: 공용/비공용에 따라 UI 분기 (파란/분홍 카드)
- 등록일 및 위도/경도 좌표 표시
- 길 찾기 버튼: Google Maps 앱으로 연결
- 등록자에게만 수정/삭제 버튼 표시
- 변경 이력 보기 링크

### 7.4 주변 검색

- `GET /toilets/nearby?lat=&lng=&radius=` — 반경 내 화장실 목록 (기본 1km)
- `GET /toilets/search?q=` — 주소/이름 키워드 검색
- 클라이언트 측 거리 계산: Haversine 공식 (`web/src/lib/utils/distance.ts`)

### 7.5 리뷰

- 로그인 사용자만 작성 가능
- 화장실당 1인 1개 제한
- 평점(1~5) + 텍스트 코멘트
- 작성자만 수정/삭제 가능
- 리뷰 평균이 `avg_rating`으로 상세 페이지에 표시

### 7.6 사진 업로드

- 로그인 사용자만 업로드 가능
- 지원 형식: JPEG, PNG, WebP
- 최대 파일 크기: 5MB
- 화장실당 최대 5장
- Firebase Storage에 저장, 공개 URL 반환

### 7.7 변경 이력 (감사 추적)

- 화장실 CREATE/UPDATE/DELETE 시 `toilet_history` 테이블에 자동 기록
- 전체 데이터 스냅샷(JSONB) + 변경된 필드 목록 저장
- 누구나 이력 조회 가능

---

## 8. 프론트엔드 페이지 구조

| 경로 | 페이지 | 설명 |
|------|--------|------|
| `/` | 메인 (지도) | 전체 지도, 뷰포트 기반 마커 표시 |
| `/search` | 검색 | 키워드/반경 검색 결과 목록 |
| `/toilets/new` | 화장실 등록 | 지도 클릭 위치 선택 + 정보 입력 폼 |
| `/toilets/[id]` | 화장실 상세 | 사진, 시설 정보, 리뷰, 길 찾기 |
| `/toilets/[id]/edit` | 화장실 수정 | 등록자만 접근 가능 |
| `/toilets/[id]/history` | 변경 이력 | 시간순 스냅샷 목록 |
| `/login` | 로그인 | Google OAuth (Firebase) |
| `/my` | 마이페이지 | 내 등록 화장실, 프로필 |

---

## 9. 환경 변수

### 백엔드 (Cloud Run 환경변수)

| 변수 | 설명 |
|------|------|
| `DATABASE_URL` | `postgresql+asyncpg://tfinder:...@localhost/tfinder?host=/cloudsql/...` |
| `CLOUD_SQL_INSTANCE` | Cloud SQL 인스턴스 연결명 |
| `JWT_SECRET_KEY` | JWT 서명 키 |
| `FIREBASE_CREDENTIALS_PATH` | Firebase Admin SDK JSON 경로 (로컬용) |
| `FIREBASE_STORAGE_BUCKET` | Firebase Storage 버킷명 |
| `PASSWORD_ENCRYPTION_KEY` | Fernet 32-byte base64 키 (비밀번호 필드 암호화) |
| `CORS_ORIGINS` | 허용 오리진 (쉼표 구분 문자열) |

### 프론트엔드 (Firebase App Hosting / `.env.local`)

| 변수 | 설명 |
|------|------|
| `NEXT_PUBLIC_API_BASE_URL` | 백엔드 API URL |
| `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | Google Maps JavaScript API 키 |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Firebase Web API 키 |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | Firebase Auth 도메인 |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Firebase 프로젝트 ID |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | Firebase Storage 버킷 |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | Firebase Messaging Sender ID |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | Firebase App ID |

---

## 10. 배포 정보

### 프론트엔드 — Firebase App Hosting

- GitHub `dev` 브랜치 push 시 자동 배포
- 설정 파일: `firebase.json`, `.firebaserc`, `web/apphosting.yaml`

### 백엔드 — Google Cloud Run

- 수동 배포:
  ```bash
  gcloud run deploy tfinder-backend --source ./backend --region us-central1
  ```
- 공개 접근: `allUsers` invoker 권한 부여
- Cloud SQL 연결: Unix 소켓 (`/cloudsql/{INSTANCE_NAME}`)
- Application Default Credentials(ADC)로 Firebase Admin SDK 인증

### 데이터베이스 초기화

```sql
-- infra/init/01_extensions.sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

Alembic으로 마이그레이션 관리 (수동 생성 필요):
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## 11. 버전 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| v1.0.0 | 2026-04-26 | 초기 운영 배포. 화장실 등록/검색/상세/리뷰/사진/이력 전 기능 구현. 성별 구분 화장실 정보 추가. 역지오코딩, 좌표 표시 기능 포함. |
