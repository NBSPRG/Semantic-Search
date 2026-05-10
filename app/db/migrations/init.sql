CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS records (
    id          SERIAL PRIMARY KEY,
    input_text  TEXT NOT NULL,
    embedding   VECTOR(384) NOT NULL,
    metadata    JSONB DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS records_embedding_hnsw_idx
ON records
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
