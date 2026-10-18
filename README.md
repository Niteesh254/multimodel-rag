# Multimodal RAG App

An end-to-end Retrieval-Augmented Generation (RAG) application that answers questions over a collection of public healthcare documents (CMS coverage policies, prior-authorization rules, FDA drug labels), grounding every answer in cited sources.

Built as a hands-on project following a production-style engineering workflow: containerized services, environment-based configuration, health checks, branch → pull request → merge.

## Status

- ✅ **Phase 1 – Foundation:** Docker Compose stack (PostgreSQL + Redis), FastAPI app, `/health` endpoint
- ⏳ Phase 2 – Document ingestion and chunking
- ⏳ Phase 3 – Hybrid retrieval (BM25 + vector) with RRF, answer generation with citations
- ⏳ Phase 4 – Redis caching, tests, retrieval evaluation
- ⏳ Phase 5 – Containerized API and a simple chat UI
- ⏳ Phase 6 – Multimodal ingestion (images, charts, scanned pages)
- ⏳ Phase 7 – Kubernetes deployment

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API | FastAPI + Pydantic, served by Uvicorn |
| Database | PostgreSQL 18 via ParadeDB (`pg_search` for BM25, `pgvector` for embeddings) |
| Cache | Redis 7 |
| Package management | uv |
| Containers | Docker + Docker Compose |
| Dev environment | Windows + WSL2 (Ubuntu 24.04), VS Code |
| Linting / formatting | Ruff |

## Project structure

```
app/
  api/          # HTTP routes and request/response schemas
  ingestion/    # load → chunk → embed → store documents
  retrieval/    # keyword search, vector search, rank fusion
  generation/   # prompt building and LLM calls
  cache/        # Redis caching
  db/           # database setup (init.sql)
  config.py     # settings loaded from environment / .env
  main.py       # FastAPI application entry point
tests/          # automated tests
docker-compose.yml
pyproject.toml / uv.lock   # dependencies (exact versions pinned in uv.lock)
.env.example    # template for required environment variables
```

## Prerequisites

- Windows 10/11 with **WSL2** and **Ubuntu 24.04** (or any Linux / macOS machine)
- **Docker Desktop** with WSL integration enabled for your Ubuntu distro
- **uv** (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Git**

Clone the repo into your Linux home directory (`~/`), not under `/mnt/c`, for performance.

## Getting started

```bash
# 1. Clone
git clone git@github.com:Niteesh254/multimodel-rag.git
cd multimodel-rag

# 2. Configure: copy the template and fill in real values
cp .env.example .env
#    generate a database password with: openssl rand -hex 16
#    and use it in BOTH POSTGRES_PASSWORD and DATABASE_URL

# 3. Install Python dependencies (creates .venv)
uv sync

# 4. Start PostgreSQL and Redis
docker compose up -d
docker compose ps          # both services should show (healthy)

# 5. Run the API
uv run uvicorn app.main:app --reload --port 8000
```

## Verify it works

```bash
curl -i localhost:8000/health
```

Expected when everything is up — **HTTP 200**:

```json
{"status": "ok", "checks": {"postgres": "ok", "redis": "ok"}}
```

If a dependency is down, the endpoint returns **HTTP 503** with `"status": "degraded"` and names the failing check.

Interactive API docs (Swagger UI): http://localhost:8000/docs

## Configuration

All configuration comes from environment variables (loaded from `.env` locally). See `.env.example`.

| Variable | Purpose |
|---|---|
| `POSTGRES_PASSWORD` | Password Docker uses to create the database user (first start only) |
| `DATABASE_URL` | Connection string the app uses: `postgresql://user:password@host:port/db` |
| `REDIS_URL` | Redis connection string |
| `OPENAI_API_KEY` | API key for embeddings and generation |
| `LLM_MODEL` | Generation model name |
| `EMBEDDING_MODEL` | Embedding model name (changing it requires re-embedding all documents) |

`.env` is git-ignored and must never be committed.

## Development workflow

- Branch from `main` for every change: `git switch -c feat/<name>`
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`)
- Open a pull request, review the diff, merge, delete the branch
- Before committing: `uv run ruff format app/ && uv run ruff check app/`

## Troubleshooting

| Problem | Fix |
|---|---|
| `password authentication failed` after changing `POSTGRES_PASSWORD` | The password is only applied when the volume is first created. Reset with `docker compose down -v` (**deletes all data**) and start again. |
| Changes to `app/db/init.sql` have no effect | Same cause — it only runs on a fresh volume. |
| Browser can't reach the API from Windows | Use `http://localhost:8000` (with `http://`), or start uvicorn with `--host 0.0.0.0`. |
| `no configuration file provided` | Run `docker compose` from the repo root, where `docker-compose.yml` lives. |