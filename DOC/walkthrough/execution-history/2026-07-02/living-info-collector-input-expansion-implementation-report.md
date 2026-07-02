# Living Information Collector Input Expansion Implementation Report

Date: 2026-07-02

## Scope

This implements the safe fix selected by `living-info-data-quality-audit-report.md`.

Changed area:
- `SOCIAL_NEWS_COLLECTOR`
- `LIVING_DOMAIN`
- Admin manual lifestyle bot collection input

Protected areas not touched:
- Scheduler frequency/state
- Production Telegram send
- Facebook/content publisher behavior
- Auth/env/secrets/token handling
- Destructive database behavior
- Private/community scraping

## Root Cause Addressed

The Living Information card path is blocked because current data is too weak for public-ready topic clusters:

- `living_info.topic_cluster` has 0 rows.
- Dry-run cluster preparation sees 55 normalized rows but creates 0 public-ready clusters.
- Current source evidence has 0 primary/official rows.
- The manual lifestyle bot previously used only 3 broad keywords and fixed `limit = 1`.

This implementation addresses the earliest safe collection-volume bottleneck: manual lifestyle bot input breadth.

## Code Changes

File:
- `SRC/foreign_worker_life_info_collector/api/admin_server.py`

Changes:
- Added `LIFESTYLE_BOT_KEYWORDS` as a named default keyword list.
- Expanded default keywords from 3 generic queries to 13 queries.
- Added official/public-source-oriented queries for:
  - Seoul city
  - Seoul Global Center
  - NHIS
  - National Pension Service
  - MOEL
  - HiKorea
  - Gov.kr
  - regional foreign resident support
  - housing/banking/transport/mobile daily-life topics
- Added `LIFESTYLE_BOT_DEFAULT_MAX_KEYWORDS = 8`.
- Added `LIFESTYLE_BOT_DEFAULT_PER_KEYWORD_LIMIT = 3`.
- Changed manual lifestyle bot execution to use:
  - `LIFESTYLE_BOT_KEYWORDS[:max_keywords]`
  - env override `LIFESTYLE_BOT_MAX_KEYWORDS`
  - env override `LIFESTYLE_BOT_PER_KEYWORD_LIMIT`
  - `limit=per_keyword_limit`
- Kept `dry_run=True`.
- Added `keyword_count`, `per_keyword_limit`, and per-keyword `limit` to the in-memory result payload.

## Tests Added

File:
- `SRC/foreign_worker_life_info_collector/tests/test_living_info_manual_sync_endpoint_contract.py`

Added tests:
- `test_lifestyle_bot_default_collection_inputs_are_source_expanded`
- `test_lifestyle_bot_uses_configurable_manual_limits_without_external_publish`

The tests verify:
- default keyword count is expanded
- official/public-source-oriented queries exist
- manual limits are configurable
- `dry_run=True` remains fixed
- no direct Telegram review send or publisher call is introduced
- old fixed `limit=1` is removed from the lifestyle bot run block

## Verification

Commands run:

```powershell
python -m pytest SRC\foreign_worker_life_info_collector\tests\test_living_info_manual_sync_endpoint_contract.py
python -m py_compile SRC\foreign_worker_life_info_collector\api\admin_server.py
```

Result:
- 6 tests passed.
- `admin_server.py` compiled successfully.

No external collection or publishing run was executed during verification.

## Remaining Known Gap

This change improves the manual collection input. It does not by itself guarantee immediate card creation because the topic-cluster readiness gate still requires enough trusted/official evidence and readiness score >= 60.

Next recommended task:

`CODE_TASK_CANDIDATE: Add a read-only Living Information readiness diagnostic endpoint/panel that shows source count, primary evidence count, would-be topic clusters, public-ready count, and top skip reasons after a prep-cycle dry run.`
