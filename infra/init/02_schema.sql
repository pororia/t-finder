-- ENUM 타입
CREATE TYPE user_role AS ENUM ('USER', 'ADMIN');
CREATE TYPE payment_type AS ENUM ('FREE', 'PAID');
CREATE TYPE toilet_type AS ENUM ('간이', '개방', '공중', '이동');

-- users 테이블
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    google_uid      VARCHAR(128) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    nickname        VARCHAR(50) NOT NULL,
    profile_image_url TEXT,
    role            user_role NOT NULL DEFAULT 'USER',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ
);

CREATE INDEX idx_users_google_uid ON users(google_uid);
CREATE INDEX idx_users_email ON users(email);

-- toilets 테이블
CREATE TABLE toilets (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    toilet_type                 toilet_type,
    location                    GEOGRAPHY(POINT, 4326) NOT NULL,
    address                     VARCHAR(500) NOT NULL,
    address_jibun               VARCHAR(500),
    address_detail              VARCHAR(200),
    name                        VARCHAR(200),
    cleanliness                 SMALLINT NOT NULL CHECK (cleanliness BETWEEN 1 AND 5),
    description                 TEXT,
    has_password                BOOLEAN NOT NULL DEFAULT FALSE,
    password_value              VARCHAR(100),
    is_unisex                   BOOLEAN NOT NULL DEFAULT FALSE,
    is_accessible               BOOLEAN NOT NULL DEFAULT FALSE,
    seat_count                  SMALLINT NOT NULL DEFAULT 0 CHECK (seat_count >= 0),
    urinal_count                SMALLINT NOT NULL DEFAULT 0 CHECK (urinal_count >= 0),
    male_seat_count             SMALLINT NOT NULL DEFAULT 0,
    male_urinal_count           SMALLINT NOT NULL DEFAULT 0,
    male_disabled_seat_count    SMALLINT NOT NULL DEFAULT 0,
    male_disabled_urinal_count  SMALLINT NOT NULL DEFAULT 0,
    male_children_seat_count    SMALLINT NOT NULL DEFAULT 0,
    male_children_urinal_count  SMALLINT NOT NULL DEFAULT 0,
    female_seat_count           SMALLINT NOT NULL DEFAULT 0,
    female_disabled_seat_count  SMALLINT NOT NULL DEFAULT 0,
    female_children_seat_count  SMALLINT NOT NULL DEFAULT 0,
    open_hours                  VARCHAR(200),
    has_emergency_bell          BOOLEAN NOT NULL DEFAULT FALSE,
    emergency_bell_location     VARCHAR(200),
    has_entrance_cctv           BOOLEAN NOT NULL DEFAULT FALSE,
    has_diaper_table            BOOLEAN NOT NULL DEFAULT FALSE,
    diaper_table_location       VARCHAR(200),
    remodeling_date             VARCHAR(7),
    payment_type                payment_type NOT NULL DEFAULT 'FREE',
    cost                        INTEGER CHECK (cost IS NULL OR cost >= 0),
    created_by                  UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    is_deleted                  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_cost_required CHECK (
        (payment_type = 'FREE' AND cost IS NULL) OR
        (payment_type = 'PAID' AND cost IS NOT NULL)
    ),
    CONSTRAINT chk_password_required CHECK (
        (has_password = FALSE) OR
        (has_password = TRUE AND password_value IS NOT NULL)
    )
);

CREATE INDEX idx_toilets_location ON toilets USING GIST(location);
CREATE INDEX idx_toilets_created_by ON toilets(created_by);
CREATE INDEX idx_toilets_is_deleted ON toilets(is_deleted) WHERE is_deleted = FALSE;
CREATE INDEX idx_toilets_cleanliness ON toilets(cleanliness);
CREATE INDEX idx_toilets_address_trgm ON toilets USING gin(address gin_trgm_ops);
CREATE INDEX idx_toilets_name_trgm ON toilets USING gin(name gin_trgm_ops);

-- toilet_photos 테이블
CREATE TABLE toilet_photos (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    toilet_id       UUID NOT NULL REFERENCES toilets(id) ON DELETE CASCADE,
    image_url       TEXT NOT NULL,
    storage_path    TEXT NOT NULL,
    display_order   SMALLINT NOT NULL DEFAULT 0,
    uploaded_by     UUID NOT NULL REFERENCES users(id),
    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_toilet_photos_toilet_id ON toilet_photos(toilet_id);

CREATE OR REPLACE FUNCTION check_max_photos()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM toilet_photos WHERE toilet_id = NEW.toilet_id) >= 5 THEN
        RAISE EXCEPTION '화장실당 최대 5장의 사진만 등록할 수 있습니다.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_max_photos
    BEFORE INSERT ON toilet_photos
    FOR EACH ROW
    EXECUTE FUNCTION check_max_photos();

-- toilet_history 테이블
CREATE TABLE toilet_history (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    toilet_id       UUID NOT NULL REFERENCES toilets(id) ON DELETE CASCADE,
    snapshot        JSONB NOT NULL,
    changed_fields  TEXT[],
    change_type     VARCHAR(20) NOT NULL,
    changed_by      UUID NOT NULL REFERENCES users(id),
    changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_toilet_history_toilet_id ON toilet_history(toilet_id);
CREATE INDEX idx_toilet_history_changed_at ON toilet_history(changed_at DESC);

-- reviews 테이블
CREATE TABLE reviews (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    toilet_id       UUID NOT NULL REFERENCES toilets(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating          SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment         TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (toilet_id, user_id)
);

CREATE INDEX idx_reviews_toilet_id ON reviews(toilet_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);

-- updated_at 자동 갱신 함수/트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_toilets_updated_at BEFORE UPDATE ON toilets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- toilet_with_rating 뷰
CREATE OR REPLACE VIEW toilet_with_rating AS
SELECT
    t.*,
    COALESCE(AVG(r.rating)::NUMERIC(2,1), t.cleanliness) AS avg_rating,
    COUNT(r.id) AS review_count
FROM toilets t
LEFT JOIN reviews r ON r.toilet_id = t.id
WHERE t.is_deleted = FALSE
GROUP BY t.id;
