"""PostgreSQL connection helpers for WorkConnect runtime storage."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_DSN = "postgresql://postgres@localhost:5432/foreign_worker_job_info"


def load_env_file() -> None:
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[2] / ".env",
    ]
    for env_path in candidates:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ[key] = value


def build_dsn() -> str:
    explicit = os.environ.get("POSTGRES_DSN")
    if explicit:
        return explicit

    host = os.environ.get("PGHOST", "localhost")
    port = os.environ.get("PGPORT", "5432")
    database = os.environ.get("PGDATABASE", "foreign_worker_job_info")
    user = os.environ.get("PGUSER", "postgres")
    password = os.environ.get("PGPASSWORD")
    if password:
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return f"postgresql://{user}@{host}:{port}/{database}"


def safe_connection_summary() -> str:
    parsed = urlparse(build_dsn())
    user = parsed.username or os.environ.get("PGUSER", "postgres")
    host = parsed.hostname or os.environ.get("PGHOST", "localhost")
    port = parsed.port or int(os.environ.get("PGPORT", "5432"))
    database = parsed.path.lstrip("/") or os.environ.get("PGDATABASE", "foreign_worker_job_info")
    return f"host={host} port={port} database={database} user={user}"


def connect():
    try:
        import psycopg  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PostgreSQL 연결에 필요한 psycopg 패키지가 설치되어 있지 않습니다.") from exc

    return psycopg.connect(build_dsn())
