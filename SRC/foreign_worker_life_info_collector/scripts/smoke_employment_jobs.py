from __future__ import annotations

import json
import os
from pathlib import Path

from ..jobs.employment_collector import EmploymentJobCollector
from ..jobs.repository import JobCollectorRepository


def load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


def main() -> int:
    load_env_file()
    repository = JobCollectorRepository()
    result = EmploymentJobCollector(repository).run(display=10, start_page_from=1, start_page_to=1, sort_order_by="DESC", delay_seconds=0.5)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"COMPLETED", "PARTIAL_FAILED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
