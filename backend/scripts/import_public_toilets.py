#!/usr/bin/env python3
"""공중화장실현황(제공표준).csv → toilets 테이블 bulk import

Usage:
    cd backend
    python scripts/import_public_toilets.py [CSV_PATH]

CSV_PATH 기본값: ./공중화장실현황(제공표준).csv
인코딩: CP949 (EUC-KR) 자동 처리
"""
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------
CSV_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("./공중화장실현황(제공표준).csv")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://tfinder:tfinder_dev_password@localhost:5432/tfinder",
)
BATCH_SIZE = 500

# CSV 구분 값 → Toilet.toilet_type enum 값
TOILET_TYPE_MAP = {
    "공중화장실": "공중",
    "개방화장실": "개방",
    "간이화장실": "간이",
    "이동화장실": "이동",
}

# ---------------------------------------------------------------------------
# 유틸
# ---------------------------------------------------------------------------

def to_psycopg2_dsn(url: str) -> str:
    return url.replace("postgresql+asyncpg://", "postgresql://")


def parse_yn(val) -> bool:
    return str(val).strip().upper() == "Y"


def safe_int(val, default: int = 0) -> int:
    try:
        v = int(float(str(val).strip()))
        return max(0, v)
    except (ValueError, TypeError):
        return default


def safe_str(val, max_len: int | None = None) -> str | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip()
    if not s or s.lower() == "nan":
        return None
    return s[:max_len] if max_len else s


# ---------------------------------------------------------------------------
# 시스템 사용자
# ---------------------------------------------------------------------------

def get_or_create_system_user(cur) -> str:
    cur.execute("SELECT id FROM users WHERE google_uid = 'csv_import_system'")
    row = cur.fetchone()
    if row:
        return str(row[0])
    uid = str(uuid.uuid4())
    cur.execute(
        """
        INSERT INTO users (id, google_uid, email, nickname, created_at, updated_at)
        VALUES (%s, 'csv_import_system', 'system@t-finder.dev', 'CSV 시스템', NOW(), NOW())
        """,
        (uid,),
    )
    return uid


# ---------------------------------------------------------------------------
# 행 변환
# ---------------------------------------------------------------------------

def build_row(row: pd.Series, system_user_id: str, now: datetime) -> tuple | None:
    try:
        lat_raw = row.get("위도")
        lng_raw = row.get("경도")
        if pd.isna(lat_raw) or pd.isna(lng_raw):
            return None
        lat = float(lat_raw)
        lng = float(lng_raw)
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return None
    except (ValueError, TypeError):
        return None

    toilet_type_raw = safe_str(row.get("구분")) or ""
    toilet_type = TOILET_TYPE_MAP.get(toilet_type_raw, "공중")

    male_seat         = safe_int(row.get("남성용-대변기수"))
    male_urinal       = safe_int(row.get("남성용-소변기수"))
    male_dis_seat     = safe_int(row.get("남성용-장애인용대변기수"))
    male_dis_urinal   = safe_int(row.get("남성용-장애인용소변기수"))
    male_child_seat   = safe_int(row.get("남성용-어린이용대변기수"))
    male_child_urinal = safe_int(row.get("남성용-어린이용소변기수"))
    female_seat       = safe_int(row.get("여성용-대변기수"))
    female_dis_seat   = safe_int(row.get("여성용-장애인용대변기수"))
    female_child_seat = safe_int(row.get("여성용-어린이용대변기수"))

    is_accessible = (male_dis_seat + male_dis_urinal + female_dis_seat) > 0

    address = (
        safe_str(row.get("소재지도로명주소"), 500)
        or safe_str(row.get("소재지지번주소"), 500)
        or "주소 미상"
    )

    wkt = f"POINT({lng} {lat})"  # ST_GeomFromText 템플릿에서 처리

    return (
        str(uuid.uuid4()),                          # id
        toilet_type,                                # toilet_type
        wkt,                                        # location (WKT → ST_GeomFromText)
        address,                                    # address
        safe_str(row.get("소재지지번주소"), 500),   # address_jibun
        safe_str(row.get("화장실명"), 200),         # name
        3,                                          # cleanliness (기본값)
        False,                                      # has_password
        parse_yn(row.get("남녀공용화장실여부")),    # is_unisex
        is_accessible,                              # is_accessible
        male_seat + female_seat,                    # seat_count
        male_urinal,                                # urinal_count
        male_seat,                                  # male_seat_count
        male_urinal,                                # male_urinal_count
        male_dis_seat,                              # male_disabled_seat_count
        male_dis_urinal,                            # male_disabled_urinal_count
        male_child_seat,                            # male_children_seat_count
        male_child_urinal,                          # male_children_urinal_count
        female_seat,                                # female_seat_count
        female_dis_seat,                            # female_disabled_seat_count
        female_child_seat,                          # female_children_seat_count
        safe_str(row.get("개방시간"), 200),         # open_hours
        parse_yn(row.get("비상벨설치여부")),        # has_emergency_bell
        safe_str(row.get("비상벨설치장소"), 200),   # emergency_bell_location
        parse_yn(row.get("화장실입구cctv설치여부")),# has_entrance_cctv
        parse_yn(row.get("기저귀교환대유무")),      # has_diaper_table
        safe_str(row.get("기저귀교환대장소"), 200), # diaper_table_location
        safe_str(row.get("리모델링연월"), 7),       # remodeling_date
        "FREE",                                     # payment_type
        False,                                      # is_deleted
        system_user_id,                             # created_by
        now,                                        # created_at
        now,                                        # updated_at
    )


# ---------------------------------------------------------------------------
# INSERT SQL
# ---------------------------------------------------------------------------

INSERT_SQL = """
INSERT INTO toilets (
    id, toilet_type, location, address, address_jibun, name,
    cleanliness, has_password, is_unisex, is_accessible,
    seat_count, urinal_count,
    male_seat_count, male_urinal_count,
    male_disabled_seat_count, male_disabled_urinal_count,
    male_children_seat_count, male_children_urinal_count,
    female_seat_count, female_disabled_seat_count, female_children_seat_count,
    open_hours,
    has_emergency_bell, emergency_bell_location,
    has_entrance_cctv, has_diaper_table, diaper_table_location,
    remodeling_date, payment_type, is_deleted, created_by,
    created_at, updated_at
) VALUES %s
ON CONFLICT DO NOTHING
"""

# %s 순서는 build_row() 반환 튜플과 동일; location만 ST_GeomFromText 래핑
INSERT_TEMPLATE = (
    "(%s, %s::toilet_type,"
    " ST_GeomFromText(%s, 4326)::geography,"
    " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,"
    " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,"
    " %s::payment_type, %s, %s, %s, %s)"
)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    if not CSV_PATH.exists():
        print(f"[ERROR] CSV 파일 없음: {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    print(f"CSV 로드 중: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, encoding="cp949", dtype=str)
    print(f"총 {len(df):,}행 로드 완료 / 컬럼: {list(df.columns)}")

    dsn = to_psycopg2_dsn(DATABASE_URL)
    now = datetime.now(timezone.utc)

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            system_user_id = get_or_create_system_user(cur)
            conn.commit()
            print(f"시스템 사용자 ID: {system_user_id}")

            rows: list[tuple] = []
            skipped = 0

            for _, row in df.iterrows():
                r = build_row(row, system_user_id, now)
                if r is None:
                    skipped += 1
                    continue
                rows.append(r)

            print(f"변환 완료: {len(rows):,}행 삽입 예정, {skipped}행 위도/경도 없어 건너뜀")

            # 배치 단위로 bulk insert
            total_inserted = 0
            for start in range(0, len(rows), BATCH_SIZE):
                batch = rows[start : start + BATCH_SIZE]
                execute_values(cur, INSERT_SQL, batch, template=INSERT_TEMPLATE, page_size=BATCH_SIZE)
                total_inserted += len(batch)
                print(f"  {total_inserted:,} / {len(rows):,} 삽입 완료...")

            conn.commit()

    print(f"\n완료: {total_inserted:,}행 삽입 (건너뜀 {skipped}행)")


if __name__ == "__main__":
    main()
