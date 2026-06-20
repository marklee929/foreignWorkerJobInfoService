# GUARDED_FIX REPORT: Official Notice Attachment Review Guardrail

## 1. Pre-Review

* AREA: `IMMIGRATION_DOMAIN + CONTENT_QUEUE + TELEGRAM_REPORTING`
* MODE: `GUARDED_FIX`
* Risk: `MEDIUM`
* Protected areas touched: 없음
* Files inspected:
  * `CODEX_BOOTSTRAP.md`
  * `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
  * `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
  * `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  * `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  * `DOC/walkthrough/2026-06-21 - execute prompt.md`
  * `DOC/walkthrough/execution-history/2026-06-21/workconnect-duplicate-review-publish-pipeline-audit.md`
  * `DOC/walkthrough/execution-history/2026-06-21/individual-request-default-review-rule-doc-only-report.md`
  * `SRC/foreign_worker_life_info_collector/content/service.py`
  * `SRC/foreign_worker_life_info_collector/api/admin_server.py`
  * `SRC/foreign_worker_life_info_collector/immigration/collectors.py`
  * `SRC/foreign_worker_life_info_collector/immigration/normalizer.py`
  * `SRC/foreign_worker_life_info_collector/immigration/repository.py`
  * `SRC/foreign_worker_life_info_collector/tests/test_content_exclusion_gate.py`
* Files modified:
  * `SRC/foreign_worker_life_info_collector/content/service.py`
  * `SRC/foreign_worker_life_info_collector/tests/test_content_exclusion_gate.py`
  * `DOC/walkthrough/2026-06-21 - execute prompt.md`
  * `DOC/walkthrough/execution-history/2026-06-21/official-notice-attachment-review-guardrail-report.md`

## 2. Current Cause

ZIP-only official notices were reaching Telegram review because `immigration_payload()` always mapped official notice rows to `source_domain = IMMIGRATION_INFO` and usually `content_type = IMMIGRATION_NOTICE`.

Then `content_quality_gate()` treated `source_domain == IMMIGRATION_INFO` as review-eligible even when the useful body/summary was only generic attachment text such as `attachment exists` or an attachment ZIP download link like `downloadAllZip.do`.

That meant source/menu label plus a valid link could be enough to produce a normal `[Facebook Format Preview]`, even before actual ZIP/PDF/HWP contents were inspected.

## 3. Changes Made

### `SRC/foreign_worker_life_info_collector/content/service.py`

* Added attachment review constants:
  * `ATTACHMENT_REVIEW_REQUIRED`
  * `EVIDENCE_ONLY`
  * `DOCUMENT_EXTRACTION_REQUIRED`
  * attachment-only terms and attachment file terms
* Added `official_attachment_review_required()`.
  * Detects official notice items with attachment evidence.
  * Checks source body/summary, not generated `why_it_matters_en`, so template text cannot rescue attachment-only source content.
* Added `public_body_text()` and `raw_payload_text()`.
  * Preserves source evidence while separating it from publishable content.
* Updated `content_quality_gate()`.
  * Attachment-only official notices now return `ATTACHMENT_REVIEW_REQUIRED`.
  * `review_eligible = False`.
  * `publish_eligible = False`.
* Updated `apply_content_quality_gate()`.
  * Converts content queue candidate to `content_type = DOCUMENT_EXTRACTION_REQUIRED`.
  * Converts `priority_group = EVIDENCE_ONLY`.
  * Adds raw payload diagnostics:
    * `attachment_review_state`
    * `classification_status = CLASSIFICATION_PENDING`
    * `evidence_only_yn = True`
    * `public_preview_allowed_yn = False`
    * `telegram_review_suppression_reason = zip_attachment_evidence_only`
    * `attachment_review_reason = attachment_content_not_inspected`
* Added `build_attachment_metadata_review_message()`.
  * If called directly for an attachment-only official notice, it creates metadata-only review text.
  * It does not include `[Facebook Format Preview]`.
  * It includes source/title/link/`bbs_seq`/`bbs_id`/attachment filename/size/reason.

### `SRC/foreign_worker_life_info_collector/tests/test_content_exclusion_gate.py`

* Added mock ZIP-only official notice test.
* Added metadata-only review message test.
* Existing HiKorea official lookup review eligibility test remains passing.

## 4. Collection Coverage

MOEL/MOJ/Hikorea official notice collection was not reduced.

No collector files were modified. Raw notice/attachment metadata remains available for future document extraction and evidence review.

## 5. Attachment-Only Review Guard

ZIP-only official notices with generic body/summary now become non-public evidence items:

* `ATTACHMENT_REVIEW_REQUIRED`
* `DOCUMENT_EXTRACTION_REQUIRED`
* `EVIDENCE_ONLY`
* `CLASSIFICATION_PENDING`

They are not `review_eligible`, so normal Telegram review dispatch skips them. They are also not `publish_eligible`, so no normal Facebook Format Preview or public posting path should proceed from this content.

## 6. Classification Safety

Source/menu label alone no longer finalizes public review eligibility for attachment-only official notices.

The source evidence can still say MOEL/MOJ/Hikorea, but content queue classification is downgraded to `DOCUMENT_EXTRACTION_REQUIRED` / `EVIDENCE_ONLY` until actual attachment/body contents are inspected.

## 7. Telegram Review Suppression / Formatting

Normal Telegram review is suppressed because `requires_telegram_review()` depends on `content_quality_gate().review_eligible`, and attachment-only official notices now return false.

If `telegram_review_message()` is called directly for such an item, it returns metadata-only evidence text and does not include:

* `[Facebook Format Preview]`
* public hashtags
* normal public preview copy

ZIP files are not attached by the normal Telegram review path.

## 8. Verification

Commands run:

```text
python -m py_compile SRC\foreign_worker_life_info_collector\content\service.py SRC\foreign_worker_life_info_collector\tests\test_content_exclusion_gate.py
```

Result: PASS

```text
$env:PYTHONPATH='SRC'; python -m unittest foreign_worker_life_info_collector.tests.test_content_exclusion_gate
```

Result: PASS, `Ran 10 tests`

```text
$env:PYTHONPATH='SRC'; python -m unittest foreign_worker_life_info_collector.tests.test_content_review_dedupe
```

Result: PASS, `Ran 7 tests`

Notes:

* First unittest attempt failed because `PYTHONPATH` was not set to `SRC`; rerun with correct local package path passed.
* No external API calls were made.
* No real Telegram/Facebook output was sent.

## 9. Protected Areas

Confirmed:

* Facebook publisher not touched
* scheduler not touched
* Telegram callback/runtime not touched
* auth/env/config not touched
* DB/migration not touched
* external API not called
* no real publish/notification sent

## 10. Remaining Risks

* `official_notice_key` / `attachment_group_key` is still needed for durable grouping.
* PDF/HWP/HWPX/DOC/DOCX/XLS/XLSX extraction pipeline is still needed.
* True content-based reclassification is still pending.
* Existing rows need a future sync/refresh cycle to receive the new gate payload.

## 11. Next CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: `IMMIGRATION_DOMAIN + DATA_SOURCE_QUALITY`
MODE: `READ_ONLY_AUDIT`
FOCUS: Design `official_notice_key` / `attachment_group_key` for MOEL/MOJ/Hikorea attachment notices.
WHY: Different `bbs_seq` rows can still represent semantically related official notice attachment groups.
RISK: `LOW`
PROTECTED AREA: DB migration, scheduler, Telegram runtime, Facebook publisher.
FILES LIKELY INVOLVED: `immigration/collectors.py`, `immigration/normalizer.py`, `immigration/repository.py`, `content/service.py`.
RECOMMENDED NEXT PROMPT: Audit official notice attachment metadata and propose grouping keys without DB mutation.

CODE_TASK_CANDIDATE
AREA: `IMMIGRATION_DOMAIN + CONTENT_QUEUE`
MODE: `READ_ONLY_AUDIT`
FOCUS: PDF/HWP attachment extraction pipeline for official notices in review-only mode.
WHY: Attachment-only notices should be classified from document contents, not menu/source labels.
RISK: `MEDIUM`
PROTECTED AREA: External API behavior, scheduler, publisher, DB destructive migration.
FILES LIKELY INVOLVED: `immigration/`, `content/`, local extraction utilities.
RECOMMENDED NEXT PROMPT: Review local-only extraction options for PDF/HWP/HWPX/DOC/DOCX/XLS/XLSX and define review-only extraction flow.

## 12. Closeout

* report saved: YES
* execute prompt updated: YES
* correction-loop updated: NO, no new harness miss occurred
* WorkConnect completion marker verification passed: YES

