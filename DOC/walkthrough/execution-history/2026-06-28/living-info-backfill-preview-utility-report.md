# GUARDED_FIX REPORT: LIVING_INFO Backfill Preview Utility

## 1. 결론 요약

- AREA: `LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- PURPOSE FUNCTION: 기존 `content.content_candidate` 중 `source_domain = 'LIVING_INFO'` rows를 migration/backfill 전에 분류하는 local read-only preview utility 생성
- Decision: `SAFE_TO_PROCEED`
- 결과: `tools/living_info_backfill_preview.py` 생성, JSON/CSV/summary preview 생성 확인

## 2. 수정 파일

- `SRC/foreign_worker_life_info_collector/tools/living_info_backfill_preview.py`
- `SRC/foreign_worker_life_info_collector/tests/test_living_info_backfill_preview.py`
- `DOC/walkthrough/2026-06-28 - execute prompt.md`
- `DOC/walkthrough/execution-history/2026-06-28/living-info-backfill-preview-utility-report.md`
- `DOC/correction-loop/2026-06-28_EXECUTE_PROMPT_MARKER_CLOSEOUT_REPAIR.md`

## 3. 생성 output

- `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_preview.json`
- `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_preview.csv`
- `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_summary.json`

Generated output은 `git status`에 잡히지 않았습니다.

## 4. Utility 기능

- 기존 `storage.db.postgres.connect()` 사용
- `content.content_candidate`에서 `source_domain = 'LIVING_INFO'` rows SELECT
- `raw_ref_table = 'social_news.candidate'` 및 `raw_ref_id`가 있을 때 `social_news.candidate` SELECT join
- `living_info` tables 존재 여부와 무관하게 동작
- deterministic classifier로 row별 `backfill_action` 산출
- 지원 CLI:

```text
python -m foreign_worker_life_info_collector.tools.living_info_backfill_preview --limit 20 --format both
python -m foreign_worker_life_info_collector.tools.living_info_backfill_preview --sample --format both
```

## 5. backfill_action 분류

- `MIGRATE_SOURCE_ITEM`
- `MIGRATE_NORMALIZED_ITEM`
- `DUPLICATE_SKIP`
- `LOW_VALUE_ARCHIVE`
- `NEEDS_MANUAL_REVIEW`
- `DO_NOT_MIGRATE`

Preview fields include:

- `content_candidate_id`
- `raw_ref_table`
- `raw_ref_id`
- `source_url`
- `canonical_url`
- `effective_url`
- `source_name`
- `source_type`
- `language`
- `raw_title`
- `raw_summary`
- `raw_body_available_yn`
- `published_at`
- `collected_at`
- `source_trust_level`
- `privacy_risk_level`
- `duplicate_key`
- `content_hash`
- `normalized_primary_category`
- `normalized_secondary_category`
- `source_usage`
- `info_signal_type`
- `target_user`
- `action_type`
- `topic_key_candidate`
- `validation_needed_yn`
- `validation_source_type`
- `actionability_score`
- `repeatability_score`
- `source_reliability_score`
- `normalization_confidence`
- `normalization_reason`
- `backfill_action`
- `backfill_reason`
- `current_category`
- `current_source_domain`
- `current_content_type`
- `current_status`
- `final_publish_score`
- `quality_score`
- `practical_value_score`
- `facebook_post_url`
- `published_state_yn`

## 6. 실행 결과

Command:

```text
python -m foreign_worker_life_info_collector.tools.living_info_backfill_preview --limit 20 --format both
```

Result:

```json
{
  "ok": true,
  "sample_mode": false,
  "row_count": 20,
  "action_counts": {
    "DO_NOT_MIGRATE": 1,
    "LOW_VALUE_ARCHIVE": 3,
    "MIGRATE_NORMALIZED_ITEM": 11,
    "NEEDS_MANUAL_REVIEW": 5
  },
  "missing_url_count": 5,
  "already_posted_count": 13,
  "manual_review_count": 5
}
```

## 7. 검증 결과

```text
python -m py_compile SRC\foreign_worker_life_info_collector\tools\living_info_backfill_preview.py SRC\foreign_worker_life_info_collector\tests\test_living_info_backfill_preview.py
```

Result: PASS

```text
python -m pytest SRC\foreign_worker_life_info_collector\tests\test_living_info_backfill_preview.py -q
```

Result:

```text
5 passed in 0.02s
```

Forbidden SQL keyword scan:

```text
INSERT / UPDATE / DELETE / TRUNCATE / DROP / ALTER / CREATE TABLE / CREATE SCHEMA
```

Result: no match in `SRC/foreign_worker_life_info_collector/tools/living_info_backfill_preview.py`.

## 8. 보호영역 확인

- DB write: NO
- migration execution: NO
- collector execution: NO
- scheduler changes: NO
- publisher changes: NO
- Telegram runtime changes: NO
- external API calls: NO
- auth/env/config changes: NO
- `content.content_candidate` data mutation: NO
- `social_news.candidate` data mutation: NO

## 9. 재시작 / 재로딩 필요 여부

- Backend restart:
  - NO
  - 이유: runtime server code가 바뀌지 않았고 local utility만 추가되었습니다.

- Frontend dev server restart:
  - NO
  - 이유: Admin UI 파일 변경이 없습니다.

- Browser hard refresh:
  - NO
  - 이유: UI 변경이 없습니다.

- DB restart:
  - NO
  - 이유: DB schema/migration 변경과 DB write가 없습니다.

- Scheduler/Bot restart:
  - NO
  - 이유: scheduler/bot runtime을 수정하지 않았습니다.

- External service restart:
  - NO
  - 대상: PostgreSQL 외 외부 서비스 없음
  - 이유: external API behavior를 수정하지 않았습니다.

- 사용자가 직접 해야 할 작업:
  1. 필요 시 `backfill_preview.json` 또는 `backfill_preview.csv`를 열어 `TASK 2` review 기준으로 확인
  2. 다음 queue 실행 전 `TASK 2: Review Backfill Preview Output` 진행 여부 판단

## 10. 남은 위험

- `LIVING_INFO` rows의 실제 source 품질은 preview output 기반으로 별도 review 필요
- `social_news.candidate`와 `content.content_candidate` ownership은 아직 변경하지 않음
- `living_info` migration은 적용하지 않음
- execute prompt marker closeout miss는 수리했고 correction-loop에 기록함

## 11. 다음 CODE_TASK_CANDIDATE

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY
MODE: READ_ONLY_AUDIT
FOCUS: Analyze generated LIVING_INFO backfill preview output.
WHY: Decide which rows are worth migrating before any DB schema/data changes.
RISK: LOW
PROTECTED AREA: DB write, migration execution, scheduler, publisher, Telegram runtime
FILES LIKELY INVOLVED:
- SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_preview.json
- SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_preview.csv
- SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_summary.json
RECOMMENDED NEXT PROMPT: Execute TASK 2 from DOC/walkthrough/2026-06-28 - execute prompt.md.
```
