# GUARDED_FIX REPORT: `ContentService.sync_living_info()`

## 1. Pre-Review

- AREA: `LIVING_DOMAIN + CONTENT_QUEUE`
- MODE: `GUARDED_FIX`
- PURPOSE FUNCTION: WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.
- Risk: MEDIUM
- Decision: `PROCEED_WITH_LIMITS`
- Protected areas touched: NO
- Files inspected:
  - `DOC/walkthrough/2026-06-28 - execute prompt.md`
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-sync-living-info-path-audit-report.md`
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/content/repository.py`
  - `SRC/foreign_worker_life_info_collector/living_info/repository.py`
  - `SRC/foreign_worker_life_info_collector/living_info/service.py`
- Files modified:
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/living_info/repository.py`
  - `SRC/foreign_worker_life_info_collector/living_info/service.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_living_info_service.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_living_info_repository.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_content_sync_living_info.py`

## 2. 구현 내용

- `ContentService.sync_living_info(limit=100)`를 추가했습니다.
- `sync_living_info()`는 명시 호출 전용입니다.
- `sync_all()`에는 연결하지 않았습니다.
- scheduler에는 연결하지 않았습니다.
- `LivingInfoRepository`에 read-only 조회 메서드를 추가했습니다.
  - `list_ready_topic_clusters(limit=100)`
  - `topic_cluster_evidence(topic_cluster_id, limit=10)`
- `LivingInfoService`에 topic cluster payload 변환을 추가했습니다.
  - `list_ready_topic_clusters(...)`
  - `topic_cluster_evidence(...)`
  - `topic_cluster_to_content_candidate_payload(...)`

## 3. 후보 생성 규칙

`content.content_candidate` 생성 identity:

```text
raw_ref_table = "living_info.topic_cluster"
raw_ref_id = topic_cluster.id
source_domain = "LIVING_INFO"
content_type = "LIVING_GUIDE"
```

생성 상태:

```text
status = "READY_TO_REVIEW"
review_required_yn = True
sensitive_yn = False
```

기존 `ContentRepository.upsert_candidate(payload)`의 `ON CONFLICT (raw_ref_table, raw_ref_id)`를 그대로 사용합니다.

## 4. Community-only 차단

아래 조건은 content candidate로 승격하지 않습니다.

- `public_candidate_ready_yn != 'Y'`
- `validation_status NOT IN ('VALIDATED', 'READY')`
- `cluster_status NOT IN ('OPEN', 'READY')`
- `readiness_score < 60`
- `source_count < 1`
- `evidence_count < 1`
- normalized evidence row 없음
- 대표 evidence URL 없음

`source_signal_id`만 있는 community/trend signal은 `topic_cluster_evidence(...)` 조회 대상에서 제외됩니다.

## 5. 테스트 / 검증

- `python -m py_compile foreign_worker_life_info_collector\content\service.py foreign_worker_life_info_collector\living_info\service.py foreign_worker_life_info_collector\living_info\repository.py foreign_worker_life_info_collector\tests\test_living_info_service.py foreign_worker_life_info_collector\tests\test_living_info_repository.py foreign_worker_life_info_collector\tests\test_content_sync_living_info.py foreign_worker_life_info_collector\tests\test_content_sync_living_split.py`
  - Result: PASS
- `python -m pytest foreign_worker_life_info_collector\tests\test_living_info_service.py foreign_worker_life_info_collector\tests\test_living_info_repository.py foreign_worker_life_info_collector\tests\test_content_sync_living_info.py foreign_worker_life_info_collector\tests\test_content_sync_living_split.py -q`
  - Result: `19 passed in 0.09s`
- `python -m pytest foreign_worker_life_info_collector\tests\test_content_exclusion_gate.py foreign_worker_life_info_collector\tests\test_content_review_dedupe.py foreign_worker_life_info_collector\tests\test_content_card_generator.py foreign_worker_life_info_collector\tests\test_content_card_payload_generator.py -q`
  - Result: `36 passed in 18.59s`

## 6. 보존한 경계

- FacebookPublisher: NOT MODIFIED
- Facebook token validation: NOT MODIFIED
- scheduler: NOT MODIFIED
- Telegram runtime/callback: NOT MODIFIED
- auth/env/config: NOT MODIFIED
- DB migration: NOT MODIFIED
- destructive DB operation: NOT PERFORMED
- actual external API call: NOT PERFORMED
- auto-publish: NOT ENABLED
- `sync_all()`: NOT MODIFIED to include `sync_living_info()`

## 7. 재시작 / 재로딩 필요 여부

- Backend restart: YES
  - 이유: `ContentService`, `LivingInfoRepository`, `LivingInfoService` runtime code가 변경되었습니다.
- Frontend dev server restart: NO
  - 이유: Admin UI 파일은 수정하지 않았습니다.
- Browser hard refresh: NO
  - 이유: UI 변경이 없습니다.
- DB restart: NO
  - 이유: DB schema/migration 변경이 없습니다.
- Scheduler/Bot restart: MAYBE
  - 이유: scheduler/bot 코드 자체는 수정하지 않았지만, backend 프로세스 내부에서 함께 실행 중이면 backend restart에 포함됩니다.
- External service restart: NO
  - 대상: Telegram/Facebook/Ollama
  - 이유: 외부 서비스 runtime 코드를 수정하지 않았습니다.
- 사용자가 직접 해야 할 작업:
  1. backend 재시작
  2. 필요 시 수동으로 `ContentService.sync_living_info()` 호출 경로를 통해 ready cluster 승격 확인
  3. `sync_all()`/scheduler 연결 여부는 별도 TASK로 결정

## 8. 남은 위험

- `living_info.topic_cluster`를 생성/갱신하는 clusterer는 아직 구현되지 않았습니다.
- 현재 local DB에는 ready topic cluster row가 없을 수 있습니다.
- Admin UI에서 `sync_living_info()`를 직접 호출하는 버튼/API는 아직 없습니다.
- `content.content_candidate`로 생성된 living guide는 Telegram/Admin review 이후에만 운영 판단이 가능합니다.

## 9. Next CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: `LIVING_DOMAIN + CONTENT_QUEUE + ADMIN_UI`
MODE: `GUARDED_FIX`
FOCUS: Add a local/admin-only trigger or API to call `ContentService.sync_living_info()` and show result counts.
WHY: `sync_living_info()` exists but is not wired to an operator action.
RISK: MEDIUM
PROTECTED AREA: scheduler, publisher, Telegram runtime, auth/env/config
FILES LIKELY INVOLVED:
- `SRC/foreign_worker_life_info_collector/admin_server.py`
- `SRC/foreign_worker_life_info_collector/admin_ui/src/...`
RECOMMENDED NEXT PROMPT: Implement an admin-only manual sync action for `living_info.topic_cluster -> content.content_candidate` without scheduler or publisher changes.

## 10. Closeout

- execute prompt updated: YES
- `[WC_EXECUTION_COMPLETE]` exact count: 1
- legacy decorated Korean completion marker count: 0
- loose completion marker count: 0
- final line is `[WC_EXECUTION_COMPLETE]`: YES
- remaining queue under marker: NO
