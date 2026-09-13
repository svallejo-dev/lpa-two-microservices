CREATE TABLE IF NOT EXISTS users (
    id         UUID        PRIMARY KEY,
    name       TEXT        NOT NULL CHECK (length(trim(name)) > 0),
    email      TEXT        NOT NULL UNIQUE CHECK (email = lower(email)),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS users_created_at_idx ON users (created_at DESC);
