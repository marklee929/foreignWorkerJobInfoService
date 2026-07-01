# PHASE 3 - Bulk LIVING_INFO Card Preview Dry-Run

## 1. 결론

- Status: COMPLETE
- Endpoint added: `POST /api/admin/content/living-info/card-preview-dry-run`
- External send: NONE
- DB schema change: NONE

## 2. 수정 파일

- `SRC/foreign_worker_life_info_collector/api/admin_server.py`
- `SRC/foreign_worker_life_info_collector/content/service.py`
- `SRC/foreign_worker_life_info_collector/content/repository.py`

## 3. 구현 내용

- `ContentRepository.list_living_info_card_preview_targets(limit, status)`
  - `source_domain = 'LIVING_INFO'`
  - requested status defaults to `READY_TO_REVIEW`
  - allowed statuses: `READY_TO_REVIEW`, `SCORED`, `READY_TO_PUBLISH`, `FAILED_RETRYABLE`
  - `POSTED` and `ARCHIVED` excluded
- `ContentService.generate_living_info_card_previews(limit, status)`
  - selected candidates are processed through `generate_card_preview_dry_run()`
  - success/failure reasons are preserved per item
  - non-`LIVING_INFO` candidates are skipped if ever returned by a fake/test repository
- API response includes:
  - `seen_count`
  - `generated_count`
  - `failed_count`
  - `skipped_count`
  - `items`

## 4. 안전성 확인

- This endpoint does not call `send_content_review_to_telegram()`.
- This endpoint does not call `telegram_api()` or `telegram_api_multipart()`.
- This endpoint does not call Facebook publisher.
- This endpoint does not update candidate publish status.
- This endpoint records only `content.publish_log` rows with `dry_run = TRUE`.

## 5. 검증 상태

- Code path review: PASS
- Compile/test: PHASE 5에서 통합 수행 예정

## 6. 보호영역 확인

- DB/migration: not modified
- Facebook publisher: not modified
- Scheduler: not modified
- Telegram runtime send/callback: not modified
- Auth/env/config: not modified
- External API behavior: not modified

## 7. 재시작 / 재로딩 필요 여부

- Backend restart: YES
  - Reason: new backend endpoint and service/repository helpers.
- Frontend dev server restart: NO
- Browser hard refresh: NO
- DB restart: NO
- Scheduler/Bot restart: NO or included in backend restart if running in the same process.
- Ollama restart: NO

## 8. 다음 PHASE 진행 여부

- Proceed: YES
- Next: PHASE 4 Admin UI action/status display
