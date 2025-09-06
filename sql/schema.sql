CREATE TABLE IF NOT EXISTS listings (
  id BIGSERIAL PRIMARY KEY,
  source VARCHAR(32) NOT NULL DEFAULT 'rakumachi',
  source_id VARCHAR(128),
  url TEXT UNIQUE,
  title TEXT,
  address TEXT,
  prefecture TEXT,
  city TEXT,
  ward TEXT,
  station_name TEXT,
  station_walk_min INTEGER,
  price_yen BIGINT,
  area_m2 DOUBLE PRECISION,
  land_area_m2 DOUBLE PRECISION,
  floor_plan TEXT,
  built_year INTEGER,
  age_years DOUBLE PRECISION,
  structure TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  raw JSONB
);

CREATE INDEX IF NOT EXISTS idx_listings_source_id ON listings (source, source_id);
CREATE INDEX IF NOT EXISTS idx_listings_price ON listings (price_yen);
CREATE INDEX IF NOT EXISTS idx_listings_station ON listings (station_name);
CREATE INDEX IF NOT EXISTS idx_listings_city ON listings (city);

CREATE TABLE IF NOT EXISTS valuations (
  id BIGSERIAL PRIMARY KEY,
  listing_id BIGINT NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
  model_version TEXT NOT NULL,
  scored_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  y_true BIGINT,
  y_pred DOUBLE PRECISION,
  residual DOUBLE PRECISION,
  residual_pct DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_valuations_listing ON valuations (listing_id);
CREATE INDEX IF NOT EXISTS idx_valuations_resid ON valuations (residual_pct);
