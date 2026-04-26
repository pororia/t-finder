# Release Notes — T-Finder

---

## 2026-04-24

### 인프라 구축 및 초기 배포

**프로젝트 초기 설정**
- `CLAUDE.md` 생성 — 빌드 명령어, 아키텍처 구조 문서화
- `README.md` 생성 — 로컬 실행, 외부 서비스 설정, 접속 방법 안내
- `.gitignore` 생성 — `.env`, `firebase-admin-sdk*.json`, `.next/` 등 제외
- GitHub 저장소 `https://github.com/pororia/t-finder.git` `dev` 브랜치 생성 및 초기 커밋

**Firebase App Hosting (프론트엔드)**
- `firebase.json`, `.firebaserc` 설정
- `web/apphosting.yaml` 환경변수 설정 (Firebase, Google Maps API 키 등)
- Firebase App Hosting 배포 완료
  - URL: `https://t-finder--t-finder-10310.us-central1.hosted.app`

**Google Cloud Run (백엔드)**
- `backend/Dockerfile` — `PORT` 환경변수 적용 (`${PORT:-8080}`)
- Cloud Run 배포 완료
  - URL: `https://tfinder-backend-848358983898.us-central1.run.app`
- Cloud Run 공개 접근 허용 (`allUsers` invoker 권한 부여)

**Cloud SQL (데이터베이스)**
- PostgreSQL 15 + PostGIS 3.4 인스턴스: `tfinder-db` (us-central1)
- Firebase Admin SDK — Application Default Credentials(ADC) 방식으로 Cloud Run 연동

---

### 버그 수정

**백엔드**

- `pyproject.toml` — `hatchling` 빌드 오류 수정 (`packages = ["app"]` 추가)
- `pyproject.toml` — `shapely>=2.0.0` 의존성 누락 추가
- `backend/app/core/firebase.py` — ADC fallback 추가 (로컬: credentials 파일, Cloud Run: ADC)
- `backend/app/db/session.py` — Cloud SQL Unix 소켓 연결 (`/cloudsql/...`) 지원
- `backend/app/config.py` — `CLOUD_SQL_INSTANCE` 환경변수 추가
- `backend/app/config.py` — `CORS_ORIGINS` 타입을 `List[str]`에서 `str`로 변경
  - pydantic-settings v2가 List 필드를 JSON으로 파싱 시도해 JSONDecodeError 발생
  - `cors_origins_list` property로 쉼표 구분 파싱

**프론트엔드**

- `web/src/app/search/page.tsx` — `useSearchParams()` Suspense boundary 오류 수정
  - `SearchContent` 컴포넌트 분리 후 `<Suspense>`로 감쌈
- `web/src/app/my/page.tsx` — SSR 오류 수정
  - `router.push('/login')`을 `useEffect` 안으로 이동
- `web/src/app/toilets/new/page.tsx` — SSR 오류 수정 (동일 패턴)
- `web/src/components/toilet/ToiletCard.tsx` — TypeScript 타입 오류 수정
  - `toilet: Toilet | ToiletNearby` union 타입으로 변경, `in` 연산자로 타입 가드

**SQLAlchemy Enum 타입명 불일치**
- `backend/app/db/models/user.py` — `Enum(UserRole, name="user_role", create_type=False)`
- `backend/app/db/models/toilet.py` — `Enum(PaymentType, name="payment_type", create_type=False)`
- SQLAlchemy 자동 생성 타입명(`userrole`, `paymenttype`)이 DB 스키마(`user_role`, `payment_type`)와 불일치하던 문제 해결

**CORS 오류**
- Cloud Run `CORS_ORIGINS` 환경변수에 `hosted.app` 도메인 추가
  - `https://t-finder--t-finder-10310.us-central1.hosted.app`
  - `https://t-finder-10310.web.app`

---

## 2026-04-25

### 버그 수정

**백엔드**

- `backend/app/api/v1/router.py` — 라우터 등록 순서 수정
  - `search.router`를 `toilets.router`보다 먼저 등록
  - `/{toilet_id}` (UUID) 패턴이 `/in-bounds`, `/nearby`, `/search`를 가로채 422 반환하던 문제 해결

- `backend/app/repositories/toilet_repository.py` — GeoAlchemy2 캐시 키 오류 수정
  - `Toilet.location.ST_Intersects(envelope)` → `func.ST_Intersects(Toilet.location, envelope)`
  - `func.ST_MakeEnvelope` 사용으로 SQLAlchemy `_static_cache_key` AttributeError 해결
  - `.order_by("distance_m")` → `.order_by(text("distance_m"))`

- `backend/app/api/v1/search.py` — in-bounds 응답에 `cost` 필드 누락 추가
  - `formatCost(undefined)` 호출로 인한 프론트엔드 TypeError 방지

- `backend/app/api/v1/toilets.py`, `search.py` — `payment_type` 직렬화 수정
  - `str(t.payment_type)` → `t.payment_type.value` (Python 3.11 enum 직렬화 호환)

**DATABASE_URL 수정**
- Cloud Run 환경변수 `DATABASE_URL` 수정: `tfinder_db` → `tfinder`

---

### 기능 추가

**지도 클릭 시 주소 자동 입력 (역지오코딩)**
- `web/src/app/toilets/new/page.tsx` — 지도 클릭 시 `google.maps.Geocoder`로 역지오코딩
- `web/src/components/toilet/ToiletForm.tsx` — `autoAddress` prop 추가, `useEffect`로 주소 필드 자동 반영

**위도/경도 좌표 표시**
- 화장실 등록 폼 — 지도 클릭 후 선택된 좌표를 지도 하단에 표시
- 화장실 상세 페이지 — 저장된 위도/경도 좌표 표시

---

## 2026-04-26

### 기능 추가

**성별 구분 화장실 정보**
- DB 컬럼 추가: `male_seat_count`, `male_urinal_count`, `female_seat_count`
- `backend/app/db/models/toilet.py` — 3개 컬럼 추가
- `backend/app/schemas/toilet.py` — `ToiletCreate`, `ToiletUpdate`, `ToiletResponse`에 필드 추가
- `web/src/types/toilet.ts` — `Toilet` 타입에 성별 구분 필드 추가
- 화장실 등록 폼 — 남녀 공용 여부에 따라 UI 분기
  - 공용: 기존 좌변기/소변기 수 입력
  - 비공용: 남자(🚹 좌변기+소변기), 여자(🚺 좌변기) 구분 입력
- 화장실 상세 페이지 — 성별 구분 정보 표시 (남자: 파란 배경, 여자: 분홍 배경)

### 버그 수정

- `web/src/lib/utils/format.ts` — `formatCost` undefined 안전 처리 (`cost == null` 체크)
- 화장실 상세 페이지 클릭 시 "Application error" 수정
  - in-bounds API 응답 `cost` 필드 누락이 원인
