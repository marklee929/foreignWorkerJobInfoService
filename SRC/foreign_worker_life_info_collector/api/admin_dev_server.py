"""Development runner for the admin API with file-change reload."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


WATCH_EXTENSIONS = {".py", ".sql"}
WATCH_FILE_NAMES = {".env"}
SKIP_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".pytest_cache",
    "admin_ui",
    "cache",
    "dist",
    "logs",
    "node_modules",
    "raw",
}


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def iter_watch_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name not in WATCH_FILE_NAMES and path.suffix not in WATCH_EXTENSIONS:
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        yield path


def snapshot(root: Path) -> dict[Path, int]:
    state: dict[Path, int] = {}
    for path in iter_watch_files(root):
        try:
            state[path] = path.stat().st_mtime_ns
        except OSError:
            continue
    return state


def changed_paths(previous: dict[Path, int], current: dict[Path, int]) -> list[Path]:
    changed: list[Path] = []
    for path, modified_at in current.items():
        if previous.get(path) != modified_at:
            changed.append(path)
    for path in previous:
        if path not in current:
            changed.append(path)
    return changed


def start_server(server_args: list[str]) -> subprocess.Popen:
    command = [sys.executable, "-m", "foreign_worker_life_info_collector.api.admin_server", *server_args]
    print("[admin-dev] Starting API server:", " ".join(command), flush=True)
    return subprocess.Popen(command, cwd=Path.cwd(), env=os.environ.copy())


def stop_server(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run admin API with development auto-reload.")
    parser.add_argument("--reload-interval", type=float, default=1.0)
    args, server_args = parser.parse_known_args(argv)

    root = package_root()
    previous = snapshot(root)
    process = start_server(server_args)
    print(f"[admin-dev] Watching for changes: {root}", flush=True)

    try:
        while True:
            time.sleep(args.reload_interval)
            exit_code = process.poll()
            if exit_code is not None:
                print(f"[admin-dev] API server exited with code {exit_code}. Restarting.", flush=True)
                process = start_server(server_args)
                previous = snapshot(root)
                continue

            current = snapshot(root)
            changed = changed_paths(previous, current)
            if changed:
                print("[admin-dev] File change detected. Restarting API server.", flush=True)
                for path in changed[:5]:
                    print(f"[admin-dev] - {path.relative_to(root)}", flush=True)
                if len(changed) > 5:
                    print(f"[admin-dev] - and {len(changed) - 5} more", flush=True)
                stop_server(process)
                process = start_server(server_args)
                previous = snapshot(root)
    except KeyboardInterrupt:
        print("[admin-dev] Stop requested.", flush=True)
    finally:
        stop_server(process)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
