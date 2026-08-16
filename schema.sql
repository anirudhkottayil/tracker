PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS topics (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY,
    topic_id   INTEGER NOT NULL REFERENCES topics(id),
    start_time TEXT NOT NULL,        -- ISO 8601, e.g. 2026-08-13T09:14:03
    end_time   TEXT NOT NULL,        -- ISO 8601
    CHECK (end_time > start_time)
);

CREATE INDEX IF NOT EXISTS idx_sessions_topic_id   ON sessions(topic_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time);
