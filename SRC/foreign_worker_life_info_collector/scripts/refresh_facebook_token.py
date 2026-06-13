"""Refresh WorkConnect Facebook long-lived token config."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from ..social.facebook.token_manager import FacebookTokenManager
from ..storage.db.postgres import load_env_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Exchange Facebook user token and store long-lived page token config.")
    parser.add_argument("--force", action="store_true", help="Refresh even when existing config token is still usable.")
    parser.add_argument("--summary", action="store_true", help="Print safe config summary only.")
    args = parser.parse_args(argv)

    load_env_file()
    manager = FacebookTokenManager()
    if args.summary:
        print(json.dumps(manager.safe_config_summary(), ensure_ascii=False, indent=2))
        return 0

    selection = manager.get_page_token(allow_refresh=True, force_refresh=args.force)
    summary = manager.safe_config_summary()
    summary.update(
        {
            "selected_source": selection.source,
            "selected_page_id": selection.page_id,
            "selected_token_fingerprint": selection.token_fingerprint,
        }
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
