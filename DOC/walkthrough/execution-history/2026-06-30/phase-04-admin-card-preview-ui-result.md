# PHASE 4 - Admin UI Card Preview Action and Status Display

## 1. 결론

- Status: COMPLETE
- Admin UI can call single and bulk card preview dry-run endpoints.
- Existing publish log card preview display is preserved.

## 2. 수정 파일

- `SRC/foreign_worker_life_info_collector/admin_ui/src/services/apiClient.js`
- `SRC/foreign_worker_life_info_collector/admin_ui/src/views/ContentManagementPage.vue`

## 3. 구현 내용

- Added API client functions:
  - `generateContentCandidateCardPreview(candidateId)`
  - `generateLivingInfoCardPreviews(payload)`
- Added top-level Admin UI action:
  - `Living info card preview`
- Added detail action:
  - `Card preview`
- Added result display:
  - bulk dry-run `seen/generated/failed/skipped`
  - latest `content_card_preview.status`
  - `reason`
  - `template_type`
  - `image_name`
  - `image_path`

## 4. UI 제한

- Local file image serving endpoint was not added.
- Browser shows local `image_path` and `image_name` as text.
- Existing publish log detail block remains the source of full card payload visibility.

## 5. 검증 상태

- Static code path review: PASS
- Build/test: PHASE 5에서 수행 예정

## 6. 보호영역 확인

- DB/migration: not modified
- Facebook publisher: not modified
- Scheduler: not modified
- Telegram runtime send/callback: not modified
- Auth/env/config: not modified
- External API behavior: not modified

## 7. 재시작 / 재로딩 필요 여부

- Backend restart: YES
  - Reason: backend endpoints changed in earlier phases.
- Frontend dev server restart: MAYBE
  - Reason: `apiClient.js` and `ContentManagementPage.vue` changed. Vite hot reload may apply, but restart or hard refresh is recommended.
- Browser hard refresh: YES
  - Reason: new Admin UI buttons and latest preview state need to be loaded.
- DB restart: NO
- Scheduler/Bot restart: NO or included in backend restart if running in the same process.
- Ollama restart: NO

## 8. 다음 PHASE 진행 여부

- Proceed: YES
- Next: PHASE 5 tests and E2E dry-run verification
