# Living Info Manual Prep Cycle Plan

## 1. 목표

Admin UI의 `Living info prepare` 액션을 실제 생활정보 준비 사이클에 연결합니다.

```text
operator click
-> POST /api/admin/content/living-info/prep-cycle
-> prepare_living_info_topic_clusters(dry_run=False)
-> sync_living_info()
-> content.content_candidate READY_TO_REVIEW
```

## 2. 수정 대상

- `SRC/foreign_worker_life_info_collector/admin_ui/src/services/apiClient.js`
- `SRC/foreign_worker_life_info_collector/admin_ui/src/views/ContentManagementPage.vue`
- `SRC/foreign_worker_life_info_collector/tests/test_living_info_manual_sync_endpoint_contract.py`

## 3. 보호영역

- production Telegram send: 수정하지 않음
- scheduler/bot auto-run: 수정하지 않음
- Facebook publisher: 수정하지 않음
- auth/env/secrets: 수정하지 않음
- DB migration: 수정하지 않음

## 4. 구현 우선순위

1. `apiClient.js`에 `runLivingInfoPrepCycle(payload)` 추가
2. `ContentManagementPage.vue`의 `syncLivingInfo()`를 prep-cycle 호출로 변경
3. UI 결과 메시지에 prepare/sync count를 분리 표시
4. contract test를 prep-cycle UI 연결 기준으로 갱신

## 5. 검증 기준

- frontend API client가 `/api/admin/content/living-info/prep-cycle`을 노출합니다.
- `ContentManagementPage.vue`의 `Living info prepare` 액션이 `dryRun: false`로 prep-cycle을 호출합니다.
- 기존 `/api/admin/content/living-info/sync` endpoint는 유지됩니다.
- 테스트는 Telegram/Facebook/scheduler 호출이 없음을 확인합니다.

## 6. 재시작 / 재로딩 필요 여부

- Backend restart: NO
  - 이유: 계획 단계에서는 runtime code를 수정하지 않았습니다.
- Frontend dev server restart: NO
  - 이유: 계획 단계에서는 Admin UI code를 수정하지 않았습니다.
- Browser hard refresh: NO
  - 이유: UI 변경 전입니다.
- DB restart: NO
  - 이유: DB schema/migration 변경이 없습니다.
- Scheduler/Bot restart: NO
  - 이유: scheduler/publisher/bot runtime을 수정하지 않습니다.
- Ollama restart: NO
  - 이유: Ollama 관련 변경이 없습니다.
