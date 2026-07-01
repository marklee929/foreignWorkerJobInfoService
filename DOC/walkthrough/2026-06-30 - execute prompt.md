@GitHub

!wc-audit

AREA: CONTENT_CARD_GENERATION + CONTENT_QUEUE + LIVING_DOMAIN + TELEGRAM_REPORTING

MODE: READ_ONLY_AUDIT

PURPOSE FUNCTION:
Verify why living-info content candidates are not producing card generation reports or card image outputs even though living-info data and news posting are running.

FOCUS:
1. Inspect the full card generation path:
   - content.content_candidate
   - ContentService.telegram_review_card_preview()
   - build_content_card_preview()
   - render_content_card()
   - Telegram review dry-run/send path
   - Admin UI card preview/report display if any

2. Check whether card generation is automatically triggered when:
   - LIVING_INFO candidates are created
   - topic_cluster reaches ready state
   - content_candidate becomes READY_TO_REVIEW
   - Telegram review target is selected
   - content bot loop runs

3. Check whether card generation is only called on manual Telegram review request.

4. Check whether generated card files are saved but not reported:
   - storage/cache/content_cards
   - storage/generated
   - publish_log
   - content_candidate raw_payload
   - admin UI display

5. Check whether LIVING_INFO candidates fail card eligibility because of:
   - missing body_en / summary_en
   - fewer than 3 usable bullets
   - CARD_NOT_READY
   - INSUFFICIENT_VALID_CARD_POINTS
   - CARD_TEXT_OVERFLOW
   - CARD_TEXT_INVALID_LANGUAGE
   - single_news_public_card_not_ready
   - quality gate blocked
   - missing topic evidence

6. Compare news posting loop vs content card generation loop:
   - why news keeps posting
   - why living-info cards are not reported
   - whether they are separate pipelines

FORBIDDEN:
- Do not modify files.
- Do not run DB migration.
- Do not change scheduler.
- Do not change Facebook publisher.
- Do not change Telegram runtime/callback.
- Do not change auth/env/secrets.
- Do not send real Telegram or Facebook output.
- Do not generate production posts.

REPORT FORMAT:

## 1. 결론
- 카드 생성이 안 보이는 핵심 원인을 한 문단으로 판단.

## 2. Current card generation path
- 실제 코드 흐름을 함수 단위로 정리.

## 3. Trigger gap
- 어디서 자동 호출이 끊겼는지 정리.

## 4. Eligibility / failure conditions
- LIVING_INFO 후보가 카드 생성에 실패할 수 있는 조건 정리.

## 5. Reporting gap
- 카드가 생성돼도 보고가 안 되는지, 애초에 생성이 안 되는지 구분.

## 6. News loop comparison
- 뉴스 포스팅 루프와 카드 생성 루프가 어떻게 다른지 정리.

## 7. CODE_TASK_CANDIDATE
- 1단계: card generation audit/log/report 추가
- 2단계: LIVING_INFO READY_TO_REVIEW 후보에 대해 dry-run card preview 생성
- 3단계: Admin UI 또는 Telegram review report에 card status 표시

각 후보는 AREA / MODE / PURPOSE FUNCTION / ALLOWED / FORBIDDEN / VERIFICATION / STOP CONDITIONS 형식으로 작성.

## 8. 최종 판정
아래 중 하나로 끝내:
- CARD_GENERATION_CONNECTED_BUT_NOT_REPORTED
- CARD_GENERATION_MANUAL_ONLY
- CARD_GENERATION_DISCONNECTED
- CARD_GENERATION_BLOCKED_BY_ELIGIBILITY
- STOP_REQUIRES_USER_REVIEW

## Execution Result

- Status: COMPLETE
- AREA: `CONTENT_CARD_GENERATION + CONTENT_QUEUE + LIVING_DOMAIN + TELEGRAM_REPORTING`
- MODE: `READ_ONLY_AUDIT`
- Report: `DOC/walkthrough/execution-history/2026-06-30/living-info-card-generation-read-only-audit.md`
- Final judgment: `CARD_GENERATION_MANUAL_ONLY`
- Summary:
  - Card generation is implemented and connected to `send_content_review_to_telegram()`.
  - `LIVING_INFO` candidate creation, topic cluster preparation, and `sync_living_info()` do not automatically generate card previews.
  - Card preview reporting appears through `content.publish_log` only after Telegram review dry-run/send path records `content_card_preview`.
  - News posting and living-info card generation are separate paths.
- Restart / reload:
  - Backend restart: NO
  - Frontend dev server restart: NO
  - Browser hard refresh: NO
  - DB restart: NO
  - Scheduler/Bot restart: NO
  - External service restart: NO
- Verification:
  - `pytest test_content_card_generator.py test_living_info_telegram_review_flow.py`: `17 passed`
  - `py_compile content_card_renderer.py content/service.py api/admin_server.py`: PASS
- Protected areas:
  - Runtime code: not modified
  - DB/migration: not modified
  - Scheduler/Bot state: not modified
  - Facebook publisher: not modified
  - Telegram runtime/callback: not modified
  - auth/env/secrets: not modified

@GitHub

!wc-fix

QUEUE-DRAIN MODE:
이번 요청은 단일 확인이 아니라 전체 패치 실행이다.
PHASE 1부터 PHASE 6까지 순차 실행하고, 성공한 PHASE는 사용자에게 중간 확인을 요구하지 말고 계속 진행해라.
단, STOP CONDITIONS에 걸리면 즉시 stop report를 저장하고 멈춰라.

# Goal

`LIVING_INFO READY_TO_REVIEW` 후보가 Telegram review를 실제로 보내지 않아도, Admin에서 card preview dry-run을 생성하고, 결과를 `content.publish_log`와 Admin UI에서 확인할 수 있게 만든다.

현재 원인:

* card generation 기능은 있음.
* 하지만 `sync_living_info()`, `prepare_topic_clusters()`, `prep-cycle`, `READY_TO_REVIEW` 생성만으로는 카드가 자동 생성되지 않음.
* card PNG 생성은 현재 `send_content_review_to_telegram()` 안에서 `ContentService.telegram_review_card_preview()`가 호출될 때만 발생함.
* 따라서 최종 판정은 `CARD_GENERATION_MANUAL_ONLY`.

이번 패치 목표:

```text
content.content_candidate LIVING_INFO READY_TO_REVIEW
-> manual/admin-only card preview dry-run endpoint
-> build_content_card_preview()
-> PNG generated under storage/cache/content_cards
-> content.publish_log record with CARD_PREVIEW_DRY_RUN or CARD_PREVIEW_FAILED
-> Admin UI detail/list에서 card preview status/reason/image path 확인
```

# Global Safety Rules

FORBIDDEN:

* Do not send real Telegram messages.
* Do not post to Facebook.
* Do not change Facebook publisher.
* Do not change content publisher auto-selection.
* Do not change scheduler behavior.
* Do not enable automatic publishing.
* Do not change Telegram callback/runtime approval behavior.
* Do not change auth/device approval.
* Do not modify env/secrets/tokens.
* Do not run or add DB migration.
* Do not perform destructive DB operations.
* Do not weaken content quality gates.
* Do not bypass card text validation.
* Do not treat `CARD_NOT_READY` as success.

ALLOWED:

* Add manual/admin-only API endpoint for card preview dry-run.
* Generate card PNG files locally.
* Store card preview result in existing `content.publish_log`.
* Add Admin UI action/status display.
* Add tests.
* Add small helper functions if needed.
* Reuse existing `build_content_card_preview()`, `ContentService.telegram_review_card_preview()`, `record_telegram_review()` or repository logging path if safe.

External output rule:

* This patch may generate local PNG files.
* This patch may insert local DB log rows into existing `content.publish_log`.
* This patch must not call real Telegram API.
* This patch must not call real Facebook API.

# Read First

Read these before editing:

* `CODEX_BOOTSTRAP.md`
* `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
* `DOC/architecture/06_WORK_AREA_REGISTRY.md`
* `SRC/foreign_worker_life_info_collector/content/service.py`
* `SRC/foreign_worker_life_info_collector/content/repository.py`
* `SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py`
* `SRC/foreign_worker_life_info_collector/api/admin_server.py`
* `SRC/foreign_worker_life_info_collector/admin_ui/src/services/apiClient.js`
* `SRC/foreign_worker_life_info_collector/admin_ui/src/views/ContentManagementPage.vue`
* existing tests:

  * `test_content_card_generator.py`
  * `test_living_info_telegram_review_flow.py`
  * `test_content_sync_living_info.py`

# PHASE 1 — Pre-Patch Boundary Review

AREA: CONTENT_CARD_GENERATION + CONTENT_QUEUE + LIVING_DOMAIN + ADMIN_UI

MODE: READ_ONLY_AUDIT

PURPOSE FUNCTION:
Confirm the exact safest insertion point for manual card preview dry-run without touching Telegram production send, Facebook publisher, scheduler, auth, or DB schema.

FOCUS:

1. Locate current `send_content_review_to_telegram()` behavior.
2. Locate current `ContentService.telegram_review_card_preview()`.
3. Locate current `ContentRepository.record_telegram_review()` or equivalent publish log insert path.
4. Locate existing Admin UI detail panel where `publishLogs` / `content_card_preview` is displayed.
5. Decide whether to reuse existing publish_log channel `telegram_review` with status `CARD_PREVIEW_DRY_RUN`, or introduce a separate channel such as `content_card_preview`.
6. Prefer minimal implementation with existing schema.

SUCCESS CRITERIA:

* Identify files to edit.
* Confirm no DB migration is needed.
* Confirm card preview can be generated without Telegram API.
* Confirm card preview result can be logged without schema change.

STOP CONDITIONS:

* If existing schema cannot store preview result without migration, stop.
* If safe logging requires Telegram runtime changes, stop.
* If implementation would touch Facebook publisher/scheduler/auth/env, stop.

REPORT:
Save `phase-01-card-preview-boundary-review.md`.

# PHASE 2 — Backend Manual Card Preview Dry-Run Endpoint

AREA: CONTENT_CARD_GENERATION + CONTENT_QUEUE

MODE: GUARDED_FIX

PURPOSE FUNCTION:
Add an explicit admin-only endpoint that generates a card preview dry-run for a selected content candidate without sending Telegram or Facebook output.

IMPLEMENTATION:
Add endpoint, preferred:

```text
POST /api/admin/content/candidates/{id}/card-preview-dry-run
```

Behavior:

1. Load candidate by id.
2. Return 404 if missing.
3. Call existing card preview generator path:

   * preferred: `content_service().telegram_review_card_preview(candidate)`
   * or direct `build_content_card_preview(candidate)` only if service path is unsuitable.
4. Do not call `send_content_review_to_telegram()`.
5. Do not call `telegram_api()` or `telegram_api_multipart()`.
6. Do not call Facebook publisher.
7. Store result in existing `content.publish_log`.

Suggested log shape:

* channel: `content_card_preview` or `telegram_review`
* status:

  * `CARD_PREVIEW_DRY_RUN` when preview ok
  * `CARD_PREVIEW_FAILED` when preview not ok
* dry_run: `TRUE`
* message_preview: short status/reason
* request_payload JSON includes:

  * `content_candidate_id`
  * `content_card_preview`
  * `card_preview_status`
  * `card_preview_reason`
  * `image_path`
  * `image_name`
  * `template_type`
  * `source`: `manual_card_preview_dry_run`
* response_payload JSON includes the raw preview result.

Expected success response:

```json
{
  "ok": true,
  "candidate_id": 123,
  "status": "CARD_PREVIEW_DRY_RUN",
  "content_card_preview": {
    "ok": true,
    "status": "CARD_PREVIEW_GENERATED",
    "template_type": "LIVING_IN_KOREA",
    "image_path": "...",
    "image_name": "workconnect-card-..."
  }
}
```

Expected failure response:

```json
{
  "ok": true,
  "candidate_id": 123,
  "status": "CARD_PREVIEW_FAILED",
  "content_card_preview": {
    "ok": false,
    "status": "CARD_NOT_READY",
    "reason": "single_news_public_card_not_ready"
  }
}
```

ALLOWED CHANGES:

* `api/admin_server.py`
* `content/service.py` helper only if needed
* `content/repository.py` helper only if needed
* tests

FORBIDDEN CHANGES:

* no Telegram real send
* no Facebook publish
* no scheduler
* no auth/env/secrets
* no DB migration
* no quality gate weakening

VERIFICATION:

* endpoint returns success/failure preview result.
* PNG file exists when `ok=true`.
* publish_log row exists with dry_run true.
* failure reason is preserved when `ok=false`.
* no Telegram API function is called.
* no Facebook client is called.

REPORT:
Save `phase-02-card-preview-dry-run-endpoint-result.md`.

# PHASE 3 — Bulk Living Info Card Preview Dry-Run

AREA: CONTENT_CARD_GENERATION + CONTENT_QUEUE + LIVING_DOMAIN

MODE: GUARDED_FIX

PURPOSE FUNCTION:
Allow operators to generate card preview dry-run results for multiple `LIVING_INFO READY_TO_REVIEW` candidates after living-info data has accumulated.

IMPLEMENTATION:
Add endpoint, preferred:

```text
POST /api/admin/content/living-info/card-preview-dry-run
```

Request body:

```json
{
  "limit": 20,
  "status": "READY_TO_REVIEW"
}
```

Behavior:

1. Select recent candidates from `content.content_candidate`.
2. Filter:

   * `source_domain = 'LIVING_INFO'`
   * status in `READY_TO_REVIEW`, optionally `SCORED` if explicitly requested
   * not `POSTED`
   * not `ARCHIVED`
3. For each candidate:

   * generate card preview dry-run
   * log result
   * preserve failure reason
4. Do not send Telegram.
5. Do not publish Facebook.
6. Return aggregate result.

Expected response:

```json
{
  "ok": true,
  "seen_count": 10,
  "generated_count": 4,
  "failed_count": 3,
  "skipped_count": 3,
  "items": [
    {
      "candidate_id": 1,
      "status": "CARD_PREVIEW_DRY_RUN",
      "preview_status": "CARD_PREVIEW_GENERATED",
      "image_path": "..."
    },
    {
      "candidate_id": 2,
      "status": "CARD_PREVIEW_FAILED",
      "preview_status": "INSUFFICIENT_VALID_CARD_POINTS",
      "reason": "Card requires at least 3 validated points before image generation."
    }
  ]
}
```

ALLOWED CHANGES:

* repository list helper if needed
* service bulk helper if needed
* admin endpoint
* tests

FORBIDDEN CHANGES:

* no scheduler
* no real Telegram
* no Facebook
* no DB migration
* no auto publish
* no sync_all behavior change

VERIFICATION:

* bulk endpoint processes only LIVING_INFO candidates.
* generated/failed/skipped counts are correct.
* card failure reasons are visible.
* no external output occurs.
* repeated runs do not duplicate uncontrolled Telegram review sends.

STOP CONDITIONS:

* If bulk logging needs new DB columns, stop and report.
* If candidate selection risks touching publisher behavior, stop.

REPORT:
Save `phase-03-living-info-bulk-card-preview-result.md`.

# PHASE 4 — Admin UI Card Preview Action and Status Display

AREA: ADMIN_UI + CONTENT_CARD_GENERATION + CONTENT_QUEUE

MODE: LOW_RISK_FIX

PURPOSE FUNCTION:
Make card preview dry-run visible to the operator in Admin UI.

IMPLEMENTATION:

1. Add apiClient functions:

   * `generateContentCandidateCardPreview(candidateId)`
   * `generateLivingInfoCardPreviews(payload)`
2. Add UI action in `ContentManagementPage.vue`:

   * candidate detail button: `카드 미리보기 생성`
   * living-info bulk button: `생활정보 카드 미리보기 생성`
3. Show loading state.
4. Show result:

   * `CARD_PREVIEW_GENERATED`
   * `CARD_NOT_READY`
   * `INSUFFICIENT_VALID_CARD_POINTS`
   * `CARD_TEXT_OVERFLOW`
   * `CARD_TEXT_INVALID_LANGUAGE`
   * `CARD_TEXT_FORBIDDEN_SYSTEM_TEXT`
5. In detail panel, show latest `content_card_preview` from `publishLogs`:

   * status
   * reason
   * template_type
   * image_path/image_name
   * if image path is local and cannot be rendered by browser, show text path only.
6. Do not require image serving endpoint in this phase unless an existing safe static route already exists.

ALLOWED CHANGES:

* `apiClient.js`
* `ContentManagementPage.vue`
* small UI helper formatting

FORBIDDEN CHANGES:

* no auth
* no external output
* no scheduler
* no publisher
* no DB migration

VERIFICATION:

* Admin UI build passes.
* Buttons call correct endpoints.
* Results render without crashing.
* Existing content sync UI still works.

REPORT:
Save `phase-04-admin-card-preview-ui-result.md`.

# PHASE 5 — Tests and E2E Dry-Run Verification

AREA: CONTENT_CARD_GENERATION + CONTENT_QUEUE + LIVING_DOMAIN + ADMIN_UI

MODE: GUARDED_FIX

PURPOSE FUNCTION:
Verify the complete non-external card preview flow.

TESTS:
Add or update tests for:

1. Single candidate card preview dry-run:

   * eligible `LIVING_INFO` candidate returns generated preview.
   * log contains `content_card_preview`.
   * no Telegram API call.
   * no Facebook client call.

2. Single candidate failure:

   * candidate with insufficient bullets returns failure.
   * failure is logged with reason.
   * no PNG required.

3. Bulk living-info dry-run:

   * processes only `LIVING_INFO`.
   * returns generated/failed/skipped counts.
   * logs per candidate.

4. UI/API contract:

   * apiClient path names correct.
   * mock response renders status/reason.

COMMANDS:
Run targeted checks:

```text
python -m py_compile foreign_worker_life_info_collector\api\admin_server.py foreign_worker_life_info_collector\content\service.py foreign_worker_life_info_collector\content\repository.py foreign_worker_life_info_collector\utils\content_card_renderer.py
python -m pytest foreign_worker_life_info_collector\tests\test_content_card_generator.py foreign_worker_life_info_collector\tests\test_living_info_telegram_review_flow.py -q
```

Also run new tests added in this phase.

If UI changed:

```text
npm run build
```

FORBIDDEN:

* no real Telegram
* no real Facebook
* no DB migration
* no env/secrets

REPORT:
Save `phase-05-card-preview-tests-e2e-result.md`.

# PHASE 6 — Final Report and Reviewer Checklist

AREA: CONTENT_CARD_GENERATION + CONTENT_QUEUE + LIVING_DOMAIN + ADMIN_UI

MODE: READ_ONLY_AUDIT

PURPOSE FUNCTION:
Write final integration report for the card preview patch and produce a GitHub reviewer checklist.

REPORT FILE:
Save:

```text
DOC/walkthrough/execution-history/YYYY-MM-DD/card-preview-dry-run-final-report.md
```

Report must include:

1. Final status
2. Implemented endpoints
3. Modified files
4. Current card generation path after patch
5. Single candidate card preview flow
6. Bulk living-info card preview flow
7. Admin UI changes
8. Tests/checks run
9. External output safety result
10. DB effects
11. Remaining risks
12. Restart/reload requirements
13. Exact commit/branch info if available
14. Reviewer checklist

Reviewer checklist must include:

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

FINAL OUTPUT:
End with one of:

```text
CARD_PREVIEW_PATCH_COMPLETE_READY_FOR_GITHUB_REVIEW
CARD_PREVIEW_PATCH_PARTIAL_READY_FOR_GITHUB_REVIEW
STOP_REQUIRES_USER_REVIEW
```

# Closeout

After all completed phases:

* Save each phase report.
* Update today execute prompt if this task is walkthrough-driven.
* Ensure the machine-readable completion marker count is exactly 1 if execute prompt closeout applies.
* Do not commit/push unless explicitly allowed by user or current project harness permits it.

## Execution Result

- Status: COMPLETE
- AREA: `CONTENT_CARD_GENERATION + CONTENT_QUEUE + LIVING_DOMAIN + ADMIN_UI`
- MODE: `QUEUE-DRAIN GUARDED_FIX`
- Final output: `CARD_PREVIEW_PATCH_COMPLETE_READY_FOR_GITHUB_REVIEW`
- Reports:
  - `DOC/walkthrough/execution-history/2026-06-30/phase-01-card-preview-boundary-review.md`
  - `DOC/walkthrough/execution-history/2026-06-30/phase-02-card-preview-dry-run-endpoint-result.md`
  - `DOC/walkthrough/execution-history/2026-06-30/phase-03-living-info-bulk-card-preview-result.md`
  - `DOC/walkthrough/execution-history/2026-06-30/phase-04-admin-card-preview-ui-result.md`
  - `DOC/walkthrough/execution-history/2026-06-30/phase-05-card-preview-tests-e2e-result.md`
  - `DOC/walkthrough/execution-history/2026-06-30/card-preview-dry-run-final-report.md`
- Implemented:
  - `POST /api/admin/content/candidates/{id}/card-preview-dry-run`
  - `POST /api/admin/content/living-info/card-preview-dry-run`
  - `content.publish_log` card preview dry-run logging through existing JSON payload fields
  - Admin UI single/bulk card preview actions
  - Admin UI latest card preview status/reason/image path display
  - non-external tests for generated/failure/bulk/UI contract paths
- Verification:
  - `python -m py_compile foreign_worker_life_info_collector\api\admin_server.py foreign_worker_life_info_collector\content\service.py foreign_worker_life_info_collector\content\repository.py foreign_worker_life_info_collector\utils\content_card_renderer.py`: PASS
  - `python -m pytest foreign_worker_life_info_collector\tests\test_content_card_preview_dry_run.py foreign_worker_life_info_collector\tests\test_content_card_generator.py foreign_worker_life_info_collector\tests\test_living_info_telegram_review_flow.py -q`: `22 passed`
  - `npm run build`: PASS
- Restart / reload:
  - Backend restart: YES
  - Frontend dev server restart: YES or Vite hot reload plus browser hard refresh
  - Browser hard refresh: YES
  - DB restart: NO
  - Scheduler/Bot restart: NO or included in backend restart if same process
  - Ollama restart: NO
- Protected areas:
  - DB/migration: not modified
  - Facebook publisher: not modified
  - Scheduler: not modified
  - Telegram runtime send/callback: not modified
  - Auth/env/config: not modified
  - Real Telegram/Facebook send: not executed
  - Actual collection/publish: not executed

[WC_EXECUTION_COMPLETE]
