# Mini ML Semantic Search System

## Interview Implementation Summary

This project is a lightweight semantic similarity engine. It accepts text through a REST API, converts the text into vector embeddings, stores the vectors, and retrieves the most semantically similar records for a query.

The implementation is intentionally simple, production-aware, and easy to explain in an interview.

---

## 1. System Goals

- Accept text input from API or browser UI.
- Generate semantic embeddings with a local pre-trained model.
- Store text, metadata, and embeddings.
- Search by semantic meaning rather than exact keywords.
- Return top-K similar records with similarity scores.
- Support both production-like pgvector storage and no-Docker local demo mode.

---

## 2. Architecture

```text
Browser UI / API Client
        |
        v
FastAPI Routes
        |
        v
Pydantic Validation
        |
        v
SentenceTransformer Embedder
        |
        v
Vector Store
   |              |
   v              v
pgvector       In-memory store
production     local testing
        |
        v
Ranked Similarity Results
```

---

## 3. Main Components

### FastAPI App

File: `app/main.py`

- Starts the application.
- Loads the embedding model once during startup.
- Connects to PostgreSQL only when `STORAGE_BACKEND=postgres`.
- Serves the browser UI from `/`.
- Exposes `/health`.

### API Routes

Files:

- `app/routes/ingest.py`
- `app/routes/search.py`

Endpoints:

- `POST /ingest`: generate embedding and store a record.
- `POST /search`: generate query embedding and retrieve similar records.
- `GET /health`: report service state.

### Pydantic Schemas

File: `app/models/schemas.py`

Responsibilities:

- Validate request payloads.
- Enforce text length and `top_k` bounds.
- Shape consistent API responses.

### Embedder Service

File: `app/services/embedder.py`

Model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Why this model:

- Runs locally.
- No API cost.
- Produces 384-dimensional embeddings.
- Good semantic quality for general text.
- Lightweight enough for a small service.

The model is loaded once and reused, avoiding repeated startup cost per request.

### Vector Store

File: `app/services/vector_store.py`

Two backends are supported:

- `postgres`: persistent pgvector storage.
- `memory`: temporary local testing mode.

This keeps the production design intact while allowing the UI and API to be tested without Docker or PostgreSQL.

---

## 4. Storage Design

Production storage uses PostgreSQL with pgvector.

Migration file:

```text
app/db/migrations/init.sql
```

Table:

```sql
CREATE TABLE IF NOT EXISTS records (
    id          SERIAL PRIMARY KEY,
    input_text  TEXT NOT NULL,
    embedding   VECTOR(384) NOT NULL,
    metadata    JSONB DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

Index:

```sql
CREATE INDEX IF NOT EXISTS records_embedding_hnsw_idx
ON records
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

Why pgvector:

- Keeps structured data and vector data in one database.
- Avoids extra vector database infrastructure.
- Supports cosine similarity search.
- Supports HNSW indexing for faster retrieval.

---

## 5. API Contract

### POST `/ingest`

Request:

```json
{
  "text": "B2B fintech lead generation for SaaS companies",
  "metadata": {
    "source": "manual",
    "category": "fintech"
  }
}
```

Response:

```json
{
  "id": 1,
  "message": "Stored successfully"
}
```

### POST `/search`

Request:

```json
{
  "query": "fintech SaaS sales prospects",
  "top_k": 3
}
```

Response:

```json
{
  "results": [
    {
      "id": 1,
      "text": "B2B fintech lead generation for SaaS companies",
      "similarity": 0.82,
      "metadata": {
        "source": "manual",
        "category": "fintech"
      }
    }
  ]
}
```

### GET `/health`

Response:

```json
{
  "status": "ok",
  "database": true,
  "model_loaded": true,
  "storage_backend": "memory"
}
```

---

## 6. Data Flow

### Ingestion Flow

```text
User enters text
    |
Pydantic validates input
    |
Embedder creates 384-dim vector
    |
Vector store saves text, metadata, embedding
    |
API returns stored record ID
```

### Search Flow

```text
User enters query
    |
Pydantic validates query and top_k
    |
Embedder creates query vector
    |
Vector store ranks records by cosine similarity
    |
API returns top-K matches
```

---

## 7. UI

Files:

- `app/static/index.html`
- `app/static/styles.css`
- `app/static/app.js`

The UI supports:

- Ingesting text and metadata.
- Searching with a query and `top_k`.
- Viewing similarity scores.
- Viewing metadata.
- Checking service readiness.

The UI is served by FastAPI at:

```text
http://localhost:8000
```

---

## 8. Configuration

Config file:

```text
app/core/config.py
```

Environment variables:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `MODEL_NAME` | Embedding model name |
| `EMBEDDING_TIMEOUT_SECONDS` | Model timeout guard |
| `LOG_LEVEL` | Application logging level |
| `STORAGE_BACKEND` | `memory` or `postgres` |

Local testing:

```text
STORAGE_BACKEND=memory
```

Production-like setup:

```text
STORAGE_BACKEND=postgres
```

---

## 9. Error Handling

| Scenario | Handling |
|---|---|
| Empty text | Pydantic returns `422` |
| Very large text | Pydantic rejects above configured max length |
| Invalid `top_k` | Pydantic returns `422` |
| Model timeout | API returns `503` |
| Database failure | API returns `503` |
| No matches | API returns `200` with an empty result list |

---

## 10. Testing Strategy

Tests are in:

```text
tests/
```

Covered areas:

- Embedder output shape and behavior.
- Ingest route validation and success path.
- Search route validation and success path.
- Test runtime mocks the model and database for speed.

Current result:

```text
5 passed
```

---

## 11. Evaluation Strategy

Recommended retrieval checks:

- Insert known positive pairs and verify correct top result.
- Query with paraphrases and check whether intended record ranks first.
- Query unrelated text and confirm low similarity.
- Track `Precision@K`, `MRR`, and latency.

Example positive pair:

```text
B2B fintech lead generation
fintech SaaS sales prospects
```

Example negative pair:

```text
B2B fintech lead generation
restaurant menu ordering
```

---

## 12. Scaling Plan

For small datasets:

- Exact or HNSW search in Postgres is enough.
- One FastAPI instance is sufficient.

For larger datasets:

- Tune HNSW parameters.
- Add connection pooling.
- Batch ingestion in a background worker.
- Cache repeated embeddings.
- Add read replicas for search traffic.
- Consider Qdrant, Weaviate, or Pinecone if vector search becomes the dominant workload.

---

## 13. Trade-Offs

| Decision | Benefit | Trade-off |
|---|---|---|
| Local MiniLM model | No API cost, simple deployment | First model load takes time |
| pgvector | One database for records and vectors | Less specialized than dedicated vector DBs |
| Memory mode | Easy local demo without Docker | Data is not persistent |
| Request-time embedding | Simple architecture | Can bottleneck at higher traffic |
| No auth | Keeps assessment scope focused | Would need API key/auth in production |

---

## 14. Fine-Tuning Position

Fine-tuning is not required for the main app. The base `all-MiniLM-L6-v2` model is a strong default for general semantic retrieval.

Fine-tuning should only be done when there are real labeled sentence pairs from the target domain. With tiny synthetic data, fine-tuning can reduce quality.

The file `colab_training.py` is included as an optional Colab experiment for domain-specific evaluation and fine-tuning.
