import psycopg
import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import get_settings

app = FastAPI(title="Multimodel RAG App", version="0.1.0")


@app.get("/health")
def health() -> JSONResponse:
    s = get_settings()
    checks: dict[str, str] = {}

    try:
        with psycopg.connect(s.database_url, connect_timeout=2) as conn:
            conn.execute("SELECT 1")
        checks["postgres"] = "ok"
    except Exception as exc:
        checks["postgres"] = f"error: {type(exc).__name__}"

    try:
        redis.Redis.from_url(s.redis_url, socket_timeout=2).ping()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {type(exc).__name__}"

    healthy = all(v == "ok" for v in checks.values())
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={"status": "ok" if healthy else "degraded", "checks": checks},
    )
