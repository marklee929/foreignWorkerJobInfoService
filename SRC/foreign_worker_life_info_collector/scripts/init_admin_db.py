"""Initialize the PostgreSQL admin database for the life info collector.

Connection is read from POSTGRES_DSN first. If it is not set, the script uses
PGHOST, PGPORT, PGDATABASE, PGUSER, and PGPASSWORD-compatible environment
variables. No credentials are stored in this file.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION_DIR = ROOT / "storage" / "db" / "migrations"
SCHEMA_FILE = MIGRATION_DIR / "admin_postgres_schema.sql"
SEED_FILE = MIGRATION_DIR / "seed_admin_config.sql"
DEFAULT_DATABASE = "foreign_worker_job_info"
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def quote_identifier(identifier: str) -> str:
    if not IDENTIFIER_PATTERN.match(identifier):
        raise ValueError(f"Unsafe PostgreSQL identifier: {identifier!r}")
    return f'"{identifier}"'


def build_dsn(database: str | None = None) -> str:
    explicit = os.environ.get("POSTGRES_DSN")
    if explicit and database is None:
        return explicit

    host = os.environ.get("PGHOST", "localhost")
    port = os.environ.get("PGPORT", "5432")
    database = database or os.environ.get("PGDATABASE", DEFAULT_DATABASE)
    user = os.environ.get("PGUSER", "postgres")
    password = os.environ.get("PGPASSWORD")

    if password:
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return f"postgresql://{user}@{host}:{port}/{database}"


def admin_dsn() -> str:
    return build_dsn(os.environ.get("PGADMIN_DATABASE", "postgres"))


def target_database_name(args_database: str | None) -> str:
    if args_database:
        return args_database
    if os.environ.get("POSTGRES_DSN"):
        return os.environ.get("PGDATABASE", DEFAULT_DATABASE)
    return os.environ.get("PGDATABASE", DEFAULT_DATABASE)


def read_sql_files() -> str:
    return "\n\n".join(
        [
            SCHEMA_FILE.read_text(encoding="utf-8"),
            SEED_FILE.read_text(encoding="utf-8"),
        ]
    )


def run_with_psycopg(dsn: str, sql: str) -> bool:
    try:
        import psycopg  # type: ignore
    except ImportError:
        psycopg = None

    if psycopg is not None:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        return True

    try:
        import psycopg2  # type: ignore
    except ImportError:
        return False

    conn = psycopg2.connect(dsn)
    try:
        cur = conn.cursor()
        try:
            cur.execute(sql)
        finally:
            cur.close()
        conn.commit()
    finally:
        conn.close()
    return True


def ensure_database(database: str) -> bool:
    try:
        import psycopg  # type: ignore
    except ImportError:
        psycopg = None

    if psycopg is not None:
        conn = psycopg.connect(admin_dsn(), autocommit=True)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
                exists = cur.fetchone() is not None
                if not exists:
                    cur.execute(f"CREATE DATABASE {quote_identifier(database)}")
            return True
        finally:
            conn.close()

    try:
        import psycopg2  # type: ignore
    except ImportError:
        return False

    conn = psycopg2.connect(admin_dsn())
    conn.autocommit = True
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
            exists = cur.fetchone() is not None
            if not exists:
                cur.execute(f"CREATE DATABASE {quote_identifier(database)}")
        finally:
            cur.close()
        return True
    finally:
        conn.close()


def run_with_psql(dsn: str) -> bool:
    psql = shutil.which("psql")
    if not psql:
        return False

    for sql_file in (SCHEMA_FILE, SEED_FILE):
        completed = subprocess.run(
            [psql, dsn, "-v", "ON_ERROR_STOP=1", "-f", str(sql_file)],
            check=False,
            text=True,
        )
        if completed.returncode != 0:
            raise SystemExit(completed.returncode)
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Initialize PostgreSQL admin database, schemas, and seed module config.")
    parser.add_argument("--dsn", help="PostgreSQL DSN. Defaults to POSTGRES_DSN or PG* environment variables.")
    parser.add_argument("--database", default=None, help=f"Target database to create/use. Defaults to {DEFAULT_DATABASE}.")
    parser.add_argument("--schema-only", action="store_true", help="Apply schema DDL only, without seed data.")
    args = parser.parse_args(argv)

    database = target_database_name(args.database)
    if not args.dsn and not os.environ.get("POSTGRES_DSN"):
        if not ensure_database(database):
            print(
                "PostgreSQL driver not found for database creation. Install psycopg/psycopg2 "
                "or create the database manually, then rerun with --dsn.",
                file=sys.stderr,
            )
            return 2

    dsn = args.dsn or build_dsn(database)
    sql = SCHEMA_FILE.read_text(encoding="utf-8") if args.schema_only else read_sql_files()

    if run_with_psycopg(dsn, sql):
        print(f"Initialized PostgreSQL database {database} with admin and social_news schemas using psycopg.")
        return 0

    if run_with_psql(dsn):
        print(f"Initialized PostgreSQL database {database} with admin and social_news schemas using psql.")
        return 0

    print(
        "PostgreSQL driver not found. Install psycopg/psycopg2 or add psql to PATH, "
        "then rerun this script.",
        file=sys.stderr,
    )
    print(f"Schema file: {SCHEMA_FILE}", file=sys.stderr)
    print(f"Seed file: {SEED_FILE}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
