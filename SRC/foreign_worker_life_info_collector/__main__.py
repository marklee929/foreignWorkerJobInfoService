from __future__ import annotations

import argparse
import json

from .research.pipeline import ResearchManager


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect and normalize foreign worker life service information.")
    parser.add_argument("keyword", nargs="?", default="서울 외국인 지원센터", help="Search keyword to collect.")
    args = parser.parse_args()

    manager = ResearchManager()
    result = manager.run_keyword(args.keyword, persist=False)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

