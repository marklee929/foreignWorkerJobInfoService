# GUARDED_FIX REPORT: Apply `living_info` Migration

## 1. 결론 요약

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- PURPOSE FUNCTION: reviewed `living_info` additive migration을 local PostgreSQL에 적용하고 schema state를 검증
- Decision: `SAFE_TO_PROCEED`
- Result: migration applied successfully

User queue-drain instruction was treated as explicit approval for this additive local migration. Destructive DDL and data backfill were still forbidden and were not performed.

## 2. 대상 migration

- `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql`

Destructive keyword scan:

```text
DROP / TRUNCATE / DELETE / UPDATE / INSERT / ALTER
```

Result: no match.

## 3. Before schema state

Connection:

```text
host=localhost port=5432 database=foreign_worker_job_info user=postgres
```

Before:

```text
before_tables=
before_indexes=
before_constraints=
```

## 4. After schema state

Tables:

```text
normalized_item
source_item
source_signal
topic_cluster
topic_cluster_item
```

Required tables missing:

```text
none
```

Index count:

```text
33
```

Constraint count:

```text
111
```

Column counts:

```text
normalized_item: 19
source_item: 27
source_signal: 21
topic_cluster: 20
topic_cluster_item: 7
```

Row counts:

```text
source_item_count=0
normalized_item_count=0
source_signal_count=0
topic_cluster_count=0
topic_cluster_item_count=0
```

## 5. Verification Result

Required checks:

- `living_info.source_item` exists: PASS
- `living_info.normalized_item` exists: PASS
- `living_info.source_signal` exists: PASS
- `living_info.topic_cluster` exists: PASS
- `living_info.topic_cluster_item` exists: PASS
- indexes exist: PASS
- constraints exist: PASS
- data backfill not executed: PASS

## 6. 보호영역 확인

Not touched:

- data backfill
- runtime code
- scheduler
- publisher
- Telegram runtime behavior
- auth/env/config
- external API behavior
- actual publish/collection execution

Changed:

- local PostgreSQL schema: additive `living_info` schema/tables/indexes/constraints created

## 7. 재시작 / 재로딩 필요 여부

- Backend restart:
  - MAYBE
  - 이유: schema만 추가됐고 기존 runtime path는 변경하지 않았습니다. 새 repository skeleton을 연결하기 전까지 필수는 아닙니다.

- Frontend dev server restart:
  - NO
  - 이유: UI 변경 없음

- Browser hard refresh:
  - NO
  - 이유: UI 변경 없음

- DB restart:
  - NO
  - 이유: DDL 적용 후 DB restart는 필요 없습니다.

- Scheduler/Bot restart:
  - NO
  - 이유: scheduler/bot runtime 변경 없음

- External service restart:
  - NO
  - 대상: 없음
  - 이유: external API behavior 변경 없음

- 사용자가 직접 해야 할 작업:
  1. `TASK 4` repository skeleton 생성 결과 확인
  2. 실제 data backfill 전 candidate ID/action set 최종 확인

## 8. 남은 위험

- schema는 적용됐지만 repository/runtime integration은 아직 없음
- data backfill은 아직 없음
- `TASK 5`는 approved candidate/action set이 필요함
