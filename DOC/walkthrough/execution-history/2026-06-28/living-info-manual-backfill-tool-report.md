# GUARDED_FIX REPORT: Manual/Dev-Only `living_info` Backfill Tool

## 1. 결론 요약

- AREA: `LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- PURPOSE FUNCTION: preview-approved rows를 `living_info`에 수동/dev-only backfill할 수 있는 dry-run-first tool 구현
- Decision: `SAFE_TO_PROCEED`
- Result: tool implemented, dry-run verified, no DB rows inserted

## 2. 수정 파일

- `SRC/foreign_worker_life_info_collector/tools/living_info_backfill_apply.py`
- `SRC/foreign_worker_life_info_collector/tests/test_living_info_backfill_apply.py`
- `DOC/walkthrough/2026-06-28 - execute prompt.md`
- `DOC/walkthrough/execution-history/2026-06-28/living-info-manual-backfill-tool-report.md`

## 3. 구현 내용

Added CLI:

```text
python -m foreign_worker_life_info_collector.tools.living_info_backfill_apply
```

Safety defaults:

- default is dry-run
- no DB write unless `--execute` is explicitly passed
- approved candidate IDs required unless `--allow-all-matching` is explicitly passed
- `--source-only-candidate-ids` supports source evidence migration without creating `normalized_item`
- writes only through `LivingInfoRepository`

Dry-run command used:

```text
python -m foreign_worker_life_info_collector.tools.living_info_backfill_apply --candidate-ids 109268,73215 --source-only-candidate-ids 135992,146984,96225,35578 --allowed-actions MIGRATE_NORMALIZED_ITEM --limit 20
```

Dry-run result:

```json
{
  "ok": true,
  "dry_run": true,
  "execute": false,
  "selected_count": 6,
  "planned_count": 6,
  "skipped_count": 0,
  "inserted_count": 0
}
```

Generated result:

- `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_apply_result.json`

## 4. Verification

```text
python -m py_compile foreign_worker_life_info_collector\tools\living_info_backfill_apply.py foreign_worker_life_info_collector\tests\test_living_info_backfill_apply.py
```

Result: PASS

```text
python -m pytest foreign_worker_life_info_collector\tests\test_living_info_backfill_apply.py -q
```

Result:

```text
6 passed in 0.04s
```

Before/after counts:

```text
before_counts={'normalized_item': 0, 'source_item': 0, 'source_signal': 0, 'topic_cluster': 0, 'topic_cluster_item': 0}
after_counts={'normalized_item': 0, 'source_item': 0, 'source_signal': 0, 'topic_cluster': 0, 'topic_cluster_item': 0}
```

## 5. 보호영역 확인

Not touched:

- automatic backfill
- content candidate creation
- scheduler
- publisher
- Telegram runtime behavior
- deleting old rows
- auth/env/config
- external API behavior

DB write:

- NO during this run
- tool can write only when `--execute` is explicitly passed

## 6. 재시작 / 재로딩 필요 여부

- Backend restart:
  - NO
  - 이유: local CLI tool만 추가했고 runtime server에는 연결하지 않았습니다.

- Frontend dev server restart:
  - NO
  - 이유: UI 변경 없음

- Browser hard refresh:
  - NO
  - 이유: UI 변경 없음

- DB restart:
  - NO
  - 이유: dry-run만 실행했고 DB restart가 필요 없습니다.

- Scheduler/Bot restart:
  - NO
  - 이유: scheduler/bot runtime 변경 없음

- External service restart:
  - NO
  - 대상: 없음
  - 이유: external API behavior 변경 없음

- 사용자가 직접 해야 할 작업:
  1. 실제 backfill insert가 필요하면 별도 `--execute` 실행 여부 결정
  2. `TASK 6` sync boundary 변경 결과 확인

## 7. 남은 위험

- 실제 insert는 아직 수행하지 않음
- `sync_social_news()`는 아직 living rows를 직접 `content.content_candidate`로 만들 수 있음
- `TASK 6`에서 ingestion boundary를 분리해야 함
