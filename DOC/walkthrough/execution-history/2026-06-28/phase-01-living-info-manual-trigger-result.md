# PHASE 1 Result: Manual Living Info Preparation Trigger

## 1. 결론 요약

- AREA: `CONTENT_QUEUE + LIVING_DOMAIN + ADMIN_UI`
- MODE: `GUARDED_FIX`
- Result: COMPLETED
- 구현 상태: manual/admin-only trigger added
- Endpoint: `POST /api/admin/content/living-info/sync`
- Public output: NONE
- Scheduler change: NO
- `sync_all()` behavior change: NO

## 2. 구현 내용

추가된 manual trigger:

```text
POST /api/admin/content/living-info/sync
-> content_service().sync_living_info(limit=...)
-> living_info.topic_cluster
-> content.content_candidate READY_TO_REVIEW
```

Admin UI:

- `syncLivingInfoContentCandidates(...)` API client function 추가
- `ContentManagementPage.vue`에 `Living info prepare` 버튼 추가
- 결과 count 표시 추가:
  - `seen_count`
  - `synced_count`
  - `skipped_count`

## 3. 수정 파일

- `SRC/foreign_worker_life_info_collector/api/admin_server.py`
- `SRC/foreign_worker_life_info_collector/admin_ui/src/services/apiClient.js`
- `SRC/foreign_worker_life_info_collector/admin_ui/src/views/ContentManagementPage.vue`
- `SRC/foreign_worker_life_info_collector/tests/test_living_info_manual_sync_endpoint_contract.py`

## 4. 검증 결과

- `python -m py_compile foreign_worker_life_info_collector\api\admin_server.py foreign_worker_life_info_collector\content\service.py foreign_worker_life_info_collector\living_info\service.py foreign_worker_life_info_collector\living_info\repository.py foreign_worker_life_info_collector\tests\test_living_info_manual_sync_endpoint_contract.py`
  - Result: PASS
- `python -m pytest foreign_worker_life_info_collector\tests\test_living_info_manual_sync_endpoint_contract.py foreign_worker_life_info_collector\tests\test_content_sync_living_info.py -q`
  - Result: `4 passed in 0.04s`
- `npm run build`
  - Result: PASS
  - Vite modules transformed: `1773`

## 5. 보호영역 확인

- scheduler: NOT MODIFIED
- Facebook publisher: NOT MODIFIED
- content publisher auto-selection: NOT MODIFIED
- Telegram runtime/callback: NOT MODIFIED
- auth/env/secrets: NOT MODIFIED
- DB migration: NOT MODIFIED
- auto publish: NOT ENABLED
- `sync_all()`: NOT MODIFIED

## 6. 재시작 / 재로딩 필요 여부

- Backend restart: YES
  - 이유: `admin_server.py` route가 추가되었습니다.
- Frontend dev server restart: MAYBE
  - 이유: `apiClient.js`, `ContentManagementPage.vue`가 수정되었습니다. Vite hot reload가 잡을 수 있으나 hard refresh를 권장합니다.
- Browser hard refresh: YES
  - 이유: 새 버튼과 결과 표시 확인이 필요합니다.
- DB restart: NO
  - 이유: DB schema/migration 변경이 없습니다.
- Scheduler/Bot restart: NO
  - 이유: scheduler/bot state 변경이 없습니다.
- External service restart: NO
  - 대상: Telegram/Facebook/Ollama
  - 이유: 외부 연동 runtime을 수정하지 않았습니다.
- 사용자가 직접 해야 할 작업:
  1. backend 재시작
  2. Admin UI hard refresh
  3. `Content Management`에서 `Living info prepare` 버튼 확인

## 7. 남은 위험

- ready `living_info.topic_cluster`가 없으면 `seen_count = 0`일 수 있습니다.
- PHASE 2에서 endpoint/service E2E dry-run 검증이 필요합니다.
- PHASE 3에서 `source_item/normalized_item -> topic_cluster` 생성 경로가 필요합니다.

## 8. 다음 단계

PHASE 2: Manual Trigger E2E Dry-Run Verification
