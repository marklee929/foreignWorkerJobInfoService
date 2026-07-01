# Card Preview Dry-Run Final Report

## 1. Final Status

- Status: COMPLETE
- Final output: `CARD_PREVIEW_PATCH_COMPLETE_READY_FOR_GITHUB_REVIEW`
- Branch: `main`
- Commit: not created
- Push: not executed

## 2. Implemented Endpoints

- `POST /api/admin/content/candidates/{id}/card-preview-dry-run`
  - Generates a card preview for one selected candidate.
  - Does not send Telegram.
  - Does not publish Facebook.
  - Logs result to `content.publish_log`.

- `POST /api/admin/content/living-info/card-preview-dry-run`
  - Generates card previews for recent `LIVING_INFO` candidates.
  - Default status filter: `READY_TO_REVIEW`
  - Logs one result per processed candidate.

## 3. Modified Files

- `SRC/foreign_worker_life_info_collector/api/admin_server.py`
- `SRC/foreign_worker_life_info_collector/content/service.py`
- `SRC/foreign_worker_life_info_collector/content/repository.py`
- `SRC/foreign_worker_life_info_collector/admin_ui/src/services/apiClient.js`
- `SRC/foreign_worker_life_info_collector/admin_ui/src/views/ContentManagementPage.vue`
- `SRC/foreign_worker_life_info_collector/tests/test_content_card_preview_dry_run.py`
- `DOC/walkthrough/execution-history/2026-06-30/phase-01-card-preview-boundary-review.md`
- `DOC/walkthrough/execution-history/2026-06-30/phase-02-card-preview-dry-run-endpoint-result.md`
- `DOC/walkthrough/execution-history/2026-06-30/phase-03-living-info-bulk-card-preview-result.md`
- `DOC/walkthrough/execution-history/2026-06-30/phase-04-admin-card-preview-ui-result.md`
- `DOC/walkthrough/execution-history/2026-06-30/phase-05-card-preview-tests-e2e-result.md`
- `DOC/walkthrough/execution-history/2026-06-30/card-preview-dry-run-final-report.md`

## 4. Current Card Generation Path After Patch

```text
Admin UI
-> POST /api/admin/content/candidates/{id}/card-preview-dry-run
-> ContentService.generate_card_preview_dry_run()
-> ContentService.telegram_review_card_preview()
-> build_content_card_preview()
-> PNG under storage/cache/content_cards when eligible
-> ContentRepository.record_content_card_preview()
-> content.publish_log channel content_card_preview
-> Admin UI detail publishLogs content_card_preview display
```

## 5. Single Candidate Card Preview Flow

- Candidate is loaded by id.
- Missing candidate returns `NOT_FOUND` with HTTP 404.
- Eligible candidate returns:
  - `status = CARD_PREVIEW_DRY_RUN`
  - `content_card_preview.status = CARD_PREVIEW_GENERATED`
  - `image_path` and `image_name`
- Ineligible candidate returns:
  - `status = CARD_PREVIEW_FAILED`
  - `content_card_preview.status`
  - `content_card_preview.reason`
- Both success and failure are logged with `dry_run = TRUE`.

## 6. Bulk LIVING_INFO Card Preview Flow

- Endpoint selects recent `content.content_candidate` rows where:
  - `source_domain = 'LIVING_INFO'`
  - status matches requested status, default `READY_TO_REVIEW`
  - status is not `POSTED`
  - status is not `ARCHIVED`
- Each candidate uses the same single dry-run helper.
- Response includes:
  - `seen_count`
  - `generated_count`
  - `failed_count`
  - `skipped_count`
  - per-item `preview_status`, `reason`, `image_path`, `image_name`, `template_type`, `log_id`

## 7. Admin UI Changes

- Added API client functions:
  - `generateContentCandidateCardPreview(candidateId)`
  - `generateLivingInfoCardPreviews(payload)`
- Added top action:
  - `Living info card preview`
- Added detail action:
  - `Card preview`
- Added visible status:
  - latest card preview status
  - reason
  - template
  - image name
  - local image path
- Browser rendering of local PNG is intentionally not added in this phase.

## 8. Tests / Checks Run

```text
python -m py_compile foreign_worker_life_info_collector\api\admin_server.py foreign_worker_life_info_collector\content\service.py foreign_worker_life_info_collector\content\repository.py foreign_worker_life_info_collector\utils\content_card_renderer.py
```

Result: PASS

```text
python -m pytest foreign_worker_life_info_collector\tests\test_content_card_preview_dry_run.py foreign_worker_life_info_collector\tests\test_content_card_generator.py foreign_worker_life_info_collector\tests\test_living_info_telegram_review_flow.py -q
```

Result: `22 passed`

```text
npm run build
```

Result: PASS

## 9. External Output Safety Result

- Real Telegram message send: not added
- `send_content_review_to_telegram()`: not called by new card preview endpoint
- `telegram_api()` / `telegram_api_multipart()`: not called by new card preview endpoint
- Facebook publisher: not modified
- Real Facebook publish: not added
- Scheduler behavior: not modified
- Auth/env/secrets: not modified

## 10. DB Effects

- DB migration: none
- Schema change: none
- Runtime endpoint effect when used:
  - inserts `content.publish_log` row
  - `channel = 'content_card_preview'`
  - `dry_run = TRUE`
  - `status = CARD_PREVIEW_DRY_RUN` or `CARD_PREVIEW_FAILED`
  - preview payload stored in existing JSON fields

## 11. Remaining Risks

- `content.publish_log` can grow if operators repeatedly click dry-run; no dedupe was added for card preview logs in this patch.
- Admin UI shows local `image_path` as text only; browser image preview needs a safe static file serving decision later.
- Bulk endpoint uses existing quality/card validation, so many `LIVING_INFO` candidates may still return `CARD_NOT_READY` or `INSUFFICIENT_VALID_CARD_POINTS`.

## 12. Restart / Reload Requirements

- Backend restart: YES
  - Reason: `admin_server.py`, `content/service.py`, and `content/repository.py` changed.
- Frontend dev server restart: YES or Vite hot reload plus browser hard refresh
  - Reason: `apiClient.js` and `ContentManagementPage.vue` changed.
- Browser hard refresh: YES
  - Reason: new Admin UI buttons and latest preview state must be loaded.
- DB restart: NO
  - Reason: no schema/migration change.
- Scheduler/Bot restart: NO or included in backend restart if running in the same backend process.
  - Reason: scheduler/publisher behavior was not changed.
- Ollama restart: NO
  - Reason: no Ollama code or model configuration changed.

## 13. Reviewer Checklist

```text
@GitHub

Review the latest WorkConnect card preview dry-run patch.

Verify:
- single candidate endpoint exists
- bulk LIVING_INFO endpoint exists
- both generate card preview without Telegram send
- preview result is logged in content.publish_log
- Admin UI shows card preview status/reason/image path
- no real Telegram call was introduced
- no Facebook publisher change was introduced
- no scheduler behavior changed
- no auth/env/secrets/DB migration changed
- tests cover generated and failed card preview cases
```

## 14. Protected Area Confirmation

- DB/migration: not modified
- Publisher: not modified
- Scheduler: not modified
- Telegram runtime behavior: not modified
- Auth/env/config: not modified
- External API behavior: not modified
- Actual publish/collection: not executed
