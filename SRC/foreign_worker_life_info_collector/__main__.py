from __future__ import annotations

import argparse
import json
from pathlib import Path

from .crew_team.research_manager import ResearchManager
from .storage.db_writer import SQLiteDBWriter


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect and normalize foreign worker life service information.")
    parser.add_argument("keyword", nargs="?", default="서울 외국인 지원센터", help="Search keyword to collect.")
    parser.add_argument("--db", default="", help="Optional SQLite database path.")
    args = parser.parse_args()

    db_path = Path(args.db) if args.db else None
    manager = ResearchManager(db_writer=SQLiteDBWriter(db_path) if db_path else None)
    result = manager.run_keyword(args.keyword)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
