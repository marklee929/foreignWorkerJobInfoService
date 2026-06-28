# GUARDED_FIX REPORT: `living_info` Repository Skeleton

## 1. 결론 요약

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- PURPOSE FUNCTION: migration 적용 후 `living_info` table-level repository/models skeleton 생성
- Decision: `SAFE_TO_PROCEED`
- Result: package/model/repository/test skeleton created

## 2. 수정 파일

- `SRC/foreign_worker_life_info_collector/living_info/__init__.py`
- `SRC/foreign_worker_life_info_collector/living_info/models.py`
- `SRC/foreign_worker_life_info_collector/living_info/repository.py`
- `SRC/foreign_worker_life_info_collector/tests/test_living_info_repository.py`
- `DOC/walkthrough/2026-06-28 - execute prompt.md`
- `DOC/walkthrough/execution-history/2026-06-28/living-info-repository-skeleton-report.md`

## 3. 구현 내용

Added models:

- `LivingSourceItem`
- `LivingNormalizedItem`
- `LivingSourceSignal`
- `LivingTopicCluster`

Added repository:

- `LivingInfoRepository.schema_state()`
- `LivingInfoRepository.require_schema_ready()`
- `LivingInfoRepository.counts()`
- `LivingInfoRepository.upsert_source_item(...)`
- `LivingInfoRepository.upsert_normalized_item(...)`
- `LivingInfoRepository.insert_source_signal(...)`
- `LivingInfoRepository.upsert_topic_cluster(...)`
- `LivingInfoRepository.list_source_items(...)`

Important boundary:

- repository does not auto-run migration
- repository is not wired into scheduler
- repository is not wired into `sync_social_news()`
- repository does not trigger publisher or Telegram runtime

## 4. Verification

```text
python -m py_compile foreign_worker_life_info_collector\living_info\__init__.py foreign_worker_life_info_collector\living_info\models.py foreign_worker_life_info_collector\living_info\repository.py foreign_worker_life_info_collector\tests\test_living_info_repository.py
```

Result: PASS

```text
python -m pytest foreign_worker_life_info_collector\tests\test_living_info_repository.py -q
```

Result:

```text
5 passed in 0.03s
```

Schema readiness smoke:

```text
ready=True
missing=
tables=normalized_item,source_item,source_signal,topic_cluster,topic_cluster_item
index_count=33
constraint_count=111
counts={'normalized_item': 0, 'source_item': 0, 'source_signal': 0, 'topic_cluster': 0, 'topic_cluster_item': 0}
```

## 5. 보호영역 확인

Not touched:

- `sync_social_news()`
- scheduler
- publisher
- Telegram runtime behavior
- auth/env/config
- auto backfill
- auto ingestion
- external API behavior

## 6. 재시작 / 재로딩 필요 여부

- Backend restart:
  - NO
  - 이유: 새 package가 추가됐지만 runtime에 연결하지 않았습니다.

- Frontend dev server restart:
  - NO
  - 이유: UI 변경 없음

- Browser hard refresh:
  - NO
  - 이유: UI 변경 없음

- DB restart:
  - NO
  - 이유: repository skeleton은 DB restart를 요구하지 않습니다.

- Scheduler/Bot restart:
  - NO
  - 이유: scheduler/bot runtime 변경 없음

- External service restart:
  - NO
  - 대상: 없음
  - 이유: external API behavior 변경 없음

- 사용자가 직접 해야 할 작업:
  1. `TASK 5` dry-run output 확인
  2. 실제 insert 실행 여부는 separate explicit `--execute`로만 진행

## 7. 남은 위험

- repository write methods exist but are not connected to runtime
- data backfill tool still required
- preview classification should be strict before any insert
