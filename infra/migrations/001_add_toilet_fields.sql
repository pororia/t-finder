-- 마이그레이션: 화장실 정보 항목 확장
-- 추가 항목: 구분, 지번주소, 장애인/어린이 변기수, 개방시간, 비상벨, CCTV, 기저귀교환대, 리모델링연월

BEGIN;

-- toilet_type ENUM 생성
CREATE TYPE toilet_type AS ENUM ('간이', '개방', '공중', '이동');

-- 신규 컬럼 추가
ALTER TABLE toilets
    ADD COLUMN toilet_type               toilet_type,
    ADD COLUMN address_jibun             VARCHAR(500),
    ADD COLUMN male_disabled_seat_count  SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN male_disabled_urinal_count SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN male_children_seat_count  SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN male_children_urinal_count SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN female_disabled_seat_count SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN female_children_seat_count SMALLINT NOT NULL DEFAULT 0,
    ADD COLUMN open_hours                VARCHAR(200),
    ADD COLUMN has_emergency_bell        BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN emergency_bell_location   VARCHAR(200),
    ADD COLUMN has_entrance_cctv         BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN has_diaper_table          BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN diaper_table_location     VARCHAR(200),
    ADD COLUMN remodeling_date           VARCHAR(7);

COMMIT;
