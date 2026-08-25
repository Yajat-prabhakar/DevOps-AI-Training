-- Runs once, on first container start, via /docker-entrypoint-initdb.d/
CREATE TABLE IF NOT EXISTS visits (
    id SERIAL PRIMARY KEY,
    visited_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
