# PHASE 1 - Card Preview Boundary Review

## 1. 결론

- Status: COMPLETE
- AREA: `CONTENT_CARD_GENERATION + CONTENT_QUEUE + LIVING_DOMAIN + ADMIN_UI`
- MODE: `READ_ONLY_AUDIT`
- Decision: existing schema is sufficient. No DB migration is needed.

## 2. 확인한 삽입 지점

- `SRC/foreign_worker_life_info_collector/api/admin_server.py`
  - existing Telegram path: `send_content_review_to_telegram(candidate, dry_run=None)`
  - current route: `POST /api/admin/content/candidates/{id}/send-telegram-review`
- `SRC/foreign_worker_life_info_collector/content/service.py`
  - existing card path: `ContentService.telegram_review_card_preview(candidate)`
  - implementation calls `build_content_card_preview(candidate)`
- `SRC/foreign_worker_life_info_collector/content/repository.py`
  - existing `content.publish_log` insert path: `record_telegram_review()`
  - existing detail loader already returns `publish_logs`
  - `publish_log_row()` already extracts `content_card_preview`
- `SRC/foreign_worker_life_info_collector/admin_ui/src/views/ContentManagementPage.vue`
  - existing detail panel already renders `log.content_card_preview`

## 3. 구현 판단

- Single endpoint can call `content_service().generate_card_preview_dry_run(id)`.
- Bulk endpoint can select `LIVING_INFO` candidates and reuse the same service helper.
- Logging should use separate channel `content_card_preview` to avoid changing Telegram runtime behavior.
- Status should be:
  - `CARD_PREVIEW_DRY_RUN` when preview result is ok
  - `CARD_PREVIEW_FAILED` when preview result is not ok
- `request_payload` and `response_payload` can store the full preview result without schema change.

## 4. 보호영역 확인

- DB/migration: not modified
- Facebook publisher: not modified
- Scheduler: not modified
- Telegram runtime send/callback: not modified
- Auth/env/config: not modified
- External API behavior: not modified

## 5. 재시작 / 재로딩 필요 여부

- Backend restart: NO
- Frontend dev server restart: NO
- Browser hard refresh: NO
- DB restart: NO
- Scheduler/Bot restart: NO
- Ollama restart: NO

## 6. 다음 PHASE 진행 여부

- Proceed: YES
- Next: PHASE 2 backend manual card preview dry-run endpoint
