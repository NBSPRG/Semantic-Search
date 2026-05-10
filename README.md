# Semantic Search

A small semantic similarity system built with FastAPI, SentenceTransformers, and pgvector. It accepts text, creates embeddings, stores them, and returns the most semantically similar records for a query.

The project also includes a simple browser UI so the API can be tested without Postman.

## Features

- `POST /ingest` stores text, metadata, and a vector embedding.
- `POST /search` returns top-K semantically similar records.
- `GET /health` reports service, model, and storage status.
- Local pre-trained embedding model: `sentence-transformers/all-MiniLM-L6-v2`.
- Production storage path: PostgreSQL with `pgvector`.
- Temporary local testing path: in-memory vector store, no Docker required.
- Simple UI at `/`.
- Unit tests for routes and embedding logic.
- Optional Colab fine-tuning/evaluation script.

## Tech Stack

- Python 3.11
- FastAPI
- SentenceTransformers
- PostgreSQL + pgvector
- asyncpg
- Docker Compose
- HTML/CSS/JavaScript frontend
- pytest

## Project Structure

```text
app/
  main.py
  static/
    index.html
    styles.css
    app.js
  core/
    config.py
  db/
    connection.py
    migrations/init.sql
  models/
    schemas.py
  routes/
    ingest.py
    search.py
  services/
    embedder.py
    vector_store.py
tests/
  conftest.py
  test_embedder.py
  test_ingest.py
  test_search.py
colab_training.py
docker-compose.yml
Dockerfile
requirements.txt
```

## Quick Start Without Docker

Use this mode when Docker Desktop or PostgreSQL is unavailable. Records are stored in memory and disappear when the server stops.

```powershell
Copy-Item .env.local.example .env -Force
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open the UI:

```text
http://127.0.0.1:8000
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

The local `.env` should contain:

```text
STORAGE_BACKEND=memory
```

## Run With Docker And pgvector

Use this mode for the production-like setup.

```bash
cp .env.example .env
docker-compose up --build
```

The API and UI run at:

```text
http://localhost:8000
```

The database migration in `app/db/migrations/init.sql` creates:

- `records` table
- `VECTOR(384)` embedding column
- HNSW cosine index

## How To Test In The UI

Open `http://127.0.0.1:8000`, then insert the following sample records one by one.

### Sample Records

Text:

```text
B2B fintech lead generation for SaaS companies
```

Metadata:

```json
{"source":"manual","category":"fintech","id":"r1"}
```

Text:

```text
AI chatbot for customer support automation
```

Metadata:

```json
{"source":"manual","category":"support","id":"r2"}
```

Text:

```text
Real estate property listings and buyer leads
```

Metadata:

```json
{"source":"manual","category":"real_estate","id":"r3"}
```

Text:

```text
Healthcare appointment scheduling for clinics
```

Metadata:

```json
{"source":"manual","category":"healthcare","id":"r4"}
```

Text:

```text
Restaurant food delivery and online menu ordering
```

Metadata:

```json
{"source":"manual","category":"restaurant","id":"r5"}
```

### Search Queries

Try these queries with `Top K = 3`:

```text
fintech SaaS sales prospects
```

```text
customer service chatbot automation
```

```text
property buyer database
```

```text
clinic patient booking system
```

```text
online food ordering menu
```

## API Usage

### Health

```bash
curl http://localhost:8000/health
```

Example response:

```json
{
  "status": "ok",
  "database": true,
  "model_loaded": true,
  "storage_backend": "memory"
}
```

### Ingest

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"text":"B2B fintech lead generation for SaaS companies","metadata":{"source":"manual","category":"fintech"}}'
```

Example response:

```json
{
  "id": 1,
  "message": "Stored successfully"
}
```

### Search

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"fintech SaaS sales prospects","top_k":3}'
```

Example response:

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

## Configuration

Environment variables:

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@db:5432/mini_ml` |
| `MODEL_NAME` | SentenceTransformer model | `sentence-transformers/all-MiniLM-L6-v2` |
| `EMBEDDING_TIMEOUT_SECONDS` | Model inference timeout | `3` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `STORAGE_BACKEND` | `memory` or `postgres` | `memory` |

## Run Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Current test status:

```text
5 passed
```

## Colab Fine-Tuning

The production app does not require fine-tuning. It uses the pre-trained `all-MiniLM-L6-v2` model.

Use `colab_training.py` only if you have labeled domain sentence pairs and want to test whether fine-tuning improves retrieval quality. With tiny or synthetic data, fine-tuning can reduce quality, so the base model is the safer default for this assessment.

## Production Notes

- pgvector is the persistent production storage backend.
- Memory mode is only for demos and local testing.
- Embeddings are normalized before storage/search.
- Cosine similarity is used for semantic matching.
- HNSW indexing is configured for faster approximate nearest-neighbor search.
- Auth is intentionally skipped for assessment scope; API key auth would be the next production hardening step.
