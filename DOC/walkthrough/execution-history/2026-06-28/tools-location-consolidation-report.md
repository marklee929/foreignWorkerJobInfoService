# GUARDED_FIX REPORT: Local Manual Utility Location Check

## 1. Pre-Review

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- Risk: LOW
- Protected areas touched: NO
- Files inspected:
  - `DOC/walkthrough/2026-06-28 - execute prompt.md`
  - `SRC/foreign_worker_life_info_collector/tools/`
  - `SRC/foreign_worker_life_info_collector/utils/`
  - `SRC/foreign_worker_life_info_collector/tools/generate_content_card_from_text.py`
  - `SRC/foreign_worker_life_info_collector/utils/content_card_payload_generator.py`
- Files modified:
  - `DOC/walkthrough/2026-06-28 - execute prompt.md`
  - `DOC/walkthrough/execution-history/2026-06-28/tools-location-consolidation-report.md`

## 2. Current `tools/` Files

Current files under `SRC/foreign_worker_life_info_collector/tools/`:

```text
__init__.py
generate_content_card_from_text.py
```

`generate_content_card_from_text.py` is a local/manual CLI entry point and is already in the correct `tools/` location.

## 3. Current `utils/` Files

Current files under `SRC/foreign_worker_life_info_collector/utils/`:

```text
__init__.py
content_card_payload_generator.py
content_card_renderer.py
date_utils.py
hash_utils.py
logging_utils.py
text_normalizer.py
url_normalizer.py
```

No new `utils/` file was added in this task.

## 4. Backfill Preview Utility Status

No current LIVING_INFO `backfill_preview` utility exists yet.

Search result:

```text
backfill_preview: not found
living_info backfill preview file: not found
```

Therefore, there was no wrongly placed file to move.

When implemented later, the LIVING_INFO backfill preview utility should be created under:

```text
SRC/foreign_worker_life_info_collector/tools/
```

Recommended future file:

```text
SRC/foreign_worker_life_info_collector/tools/living_info_backfill_preview.py
```

## 5. Existing `utils/content_card_payload_generator.py`

`SRC/foreign_worker_life_info_collector/utils/content_card_payload_generator.py` already exists and is imported by:

```text
SRC/foreign_worker_life_info_collector/tools/generate_content_card_from_text.py
SRC/foreign_worker_life_info_collector/content/card_payload_generator.py
SRC/foreign_worker_life_info_collector/tests/test_content_card_payload_generator.py
SRC/foreign_worker_life_info_collector/tests/test_llama_keep_alive_policy.py
```

It was not moved because that would require a separate import/refactor task and is outside this request.

## 6. Boundaries Preserved

- no runtime imports changed
- no Python runtime code changed
- no new `utils/` files added
- no duplicate `tools`/`utils` version created
- no DB migration executed
- no DB data changed
- no collector execution
- no scheduler, Telegram, Facebook, auth, env/config touched

## 7. Final Rule For Next Utility

For the upcoming LIVING_INFO backfill preview utility:

```text
manual/local utility -> SRC/foreign_worker_life_info_collector/tools/
reusable runtime helper -> SRC/foreign_worker_life_info_collector/utils/ only with explicit approval
```

## 8. Closeout

- report saved: YES
- execute prompt updated: YES
- marker verification required after update: YES
