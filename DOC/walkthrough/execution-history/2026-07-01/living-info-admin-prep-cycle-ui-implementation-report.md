# Living Info Admin Prep-Cycle UI Implementation Report

## 1. 결론 요약

- Status: COMPLETE
- AREA: `LIVING_DOMAIN + CONTENT_QUEUE`
- MODE: `LOW_RISK_FIX`
- PURPOSE FUNCTION: Living Information pipeline이 운영자 수동 액션으로 `topic_cluster` 준비와 `content.content_candidate` 동기화까지 이어지게 한다.
- Earliest failing layer: Admin UI manual trigger

## 2. 구현 내용

Admin UI의 `Living info prepare` 버튼을 기존 `/api/admin/content/living-info/sync` 단독 호출에서 기존 `/api/admin/content/living-info/prep-cycle` 호출로 변경했다.

변경 후 흐름:

```text
operator click
-> runLivingInfoPrepCycle({ limit: 100, dryRun: false })
-> POST /api/admin/content/living-info/prep-cycle
-> prepare_living_info_topic_clusters(dry_run=False)
-> sync_living_info()
-> content.content_candidate READY_TO_REVIEW
```

기존 `/api/admin/content/living-info/sync` endpoint와 `syncLivingInfoContentCandidates()` API client 함수는 제거하지 않았다. 기존 수동 sync 경로를 보존하기 위해 남겼다.

## 3. 수정 파일

- `SRC/foreign_worker_life_info_collector/admin_ui/src/services/apiClient.js`
  - `runLivingInfoPrepCycle(payload)` 함수가 존재함을 확인했다.
- `SRC/foreign_worker_life_info_collector/admin_ui/src/views/ContentManagementPage.vue`
  - `Living info prepare` 액션이 `runLivingInfoPrepCycle({ limit: 100, dryRun: false })`를 호출하도록 변경했다.
  - 결과 메시지를 `prepare` / `sync` nested payload 구조에 맞게 변경했다.
- `SRC/foreign_worker_life_info_collector/tests/test_living_info_manual_sync_endpoint_contract.py`
  - API client가 `prep-cycle` 함수를 노출하는지 확인한다.
  - Content Management page의 `syncLivingInfo()`가 `prep-cycle`을 사용하고 기존 `syncLivingInfoContentCandidates`를 사용하지 않는지 확인한다.

## 4. 검증 결과

```text
python -m pytest foreign_worker_life_info_collector\tests\test_living_info_manual_sync_endpoint_contract.py foreign_worker_life_info_collector\tests\test_living_info_content_prep_scheduler_contract.py foreign_worker_life_info_collector\tests\test_content_card_preview_dry_run.py -q
```

Result: PASS, `15 passed in 0.09s`

```text
npm run build
```

Workdir: `SRC/foreign_worker_life_info_collector/admin_ui`

Result: PASS, `1773 modules transformed`

## 5. 보호 영역 확인

- production Telegram send: 변경 없음
- Telegram callback/runtime approval behavior: 변경 없음
- Facebook publisher: 변경 없음
- content publisher automatic selection: 변경 없음
- scheduler/bot state: 변경 없음
- auth/env/secrets/token: 변경 없음
- DB migration/destructive DB work: 변경 없음
- external API behavior: 변경 없음

이번 변경은 운영자가 Admin UI에서 수동으로 누르는 기존 준비 액션의 대상 endpoint만 바꾼다. 실제 외부 발송은 추가하지 않았다.

## 6. 재시작 / 리로드 필요 여부

- Backend restart: NO
  - 이유: backend runtime code는 변경하지 않았다.
- Frontend dev server restart: YES or Vite hot reload
  - 이유: `ContentManagementPage.vue`와 `apiClient.js` 변경 반영 필요.
- Browser hard refresh: YES
  - 이유: Admin UI 버튼 동작과 결과 메시지 갱신 필요.
- DB restart: NO
  - 이유: schema/migration 변경 없음.
- Scheduler/Bot restart: NO
  - 이유: scheduler/bot state 변경 없음.
- External service restart: NO
  - 대상: Telegram, Facebook, Ollama
  - 이유: 외부 서비스 동작 변경 없음.

## 7. 남은 위험

- `dryRun: false` 수동 prep-cycle은 운영자 클릭 시 기존 DB 테이블에 `topic_cluster`와 `content_candidate`를 쓸 수 있다. 이는 새 destructive DB 작업은 아니지만, 실제 로컬 DB 데이터셋에서 운영자가 결과를 확인해야 한다.
- Production Telegram send는 여전히 별도 보호 영역이다.
- Living Info 데이터 부족의 다음 원인이 source coverage 자체라면 별도 `READ_ONLY_AUDIT`가 필요하다.

## 8. 다음 CODE_TASK_CANDIDATE

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Verify the real local DB result after the operator runs Living info prepare and card preview from Admin UI.
FOCUS:
Check counts for living_info.source_item, living_info.normalized_item, living_info.topic_cluster, content.content_candidate, and content.publish_log content_card_preview.
WHY:
The UI path is now connected, but actual data volume and card eligibility need evidence from a local dataset.
ALLOWED:
- read code
- read docs
- read-only DB diagnostics if explicitly available
- Admin UI/API response inspection without external send
FORBIDDEN:
- production Telegram send
- Facebook publish
- scheduler/bot state changes
- auth/env/secrets changes
- destructive DB changes
- external API behavior changes
VERIFICATION:
- report DB counts and skipped reasons
- confirm no real Telegram/Facebook output
- generate a follow-up implementation candidate only if the earliest failing layer is proven
STOP CONDITIONS:
- DB credentials unavailable
- verification would require production Telegram/Facebook
- fix requires scheduler/publisher/auth/env changes
```

