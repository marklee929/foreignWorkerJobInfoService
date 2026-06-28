
!wc-audit

PURPOSE FUNCTION:
WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.

AREA:
SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE + TELEGRAM_REPORTING + CONTENT_PUBLISHER

MODE:
READ_ONLY_AUDIT

FOCUS:
Audit duplicate review/publish behavior across the full WorkConnect content pipeline.

The goal is to find why the same or semantically equivalent source item can be sent to Telegram review multiple times or published to Facebook multiple times.

This is an audit only. Do not modify code.

TIMEBOX:
60m

READ FIRST:

* CODEX_BOOTSTRAP.md or AGENTS.md if present
* DOC/architecture/05_CODEX_HARNESS_GUIDE.md
* DOC/architecture/06_WORK_AREA_REGISTRY.md
* DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
* DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
* DOC/architecture/03_SYSTEM_ARCHITECTURE.md
* DOC/walkthrough/YYYY-MM-DD - execute prompt.md
* recent DOC/correction-loop entries related to content duplicate, Telegram duplicate, Facebook duplicate, or card generation

BACKGROUND:
The operator observed multiple duplicate or near-duplicate cases.

Case A:
A ChosunBiz article was auto-published to Facebook twice.
The content appeared to have the same title/source/link/category/score but different Facebook post IDs.

Case B:
Ministry of Employment and Labor attachment notices were sent to Telegram review multiple times.
Examples:

* ID 58620
* ID 58622
* source_domain/category shown as `IMMIGRATION_INFO / IMMIGRATION_NOTICE / 고용노동부 외국인고용 관련 공지`
* format `LINK_OR_TEXT`
* template `ALERT_REVIEW`
* links have different `bbs_seq` values such as `19542` and `19543`
* preview text is nearly identical: `첨부파일 있음`
* attached ZIP files differ by filename/size
  This may not be exact URL duplication, but it appears to be semantic duplicate or attachment-level duplicate.

AUDIT SCOPE:
Inspect duplicate prevention at each stage:

1. Collector/raw source layer

* same source_url
* same canonical_url
* same bbs_seq
* same attachment group
* same title/source/date
* source-specific duplicate keys

2. Normalized/candidate layer

* hash_key
* title_hash
* similarity_key
* duplicate_group_id
* representative candidate selection
* same topic different attachment handling

3. Content queue layer

* content_candidate identity
* source_ref mapping
* same raw item becoming multiple content candidates
* content_type/source_domain/category mapping
* publish_log/review_log relationship

4. Telegram reporting layer

* telegram_review_key
* semantic_review_key
* content_candidate_id + message_preview
* duplicate suppression window
* whether different candidate IDs bypass suppression
* whether different `bbs_seq` but same notice preview bypasses suppression
* whether attachment filename/size is part of the key

5. Facebook publish layer

* same source_url already published
* same canonical_url already published
* same title/source already published
* same content fingerprint already published
* READY -> PUBLISHING atomic claim or equivalent
* race condition possibility between scheduler/manual publish/jobs
* whether Facebook post ID duplication prevention exists

6. Attachment notice handling

* whether a board notice with multiple attachments creates multiple separate review candidates
* whether `downloadAllZip.do` links are treated as content URLs
* whether individual attachment ZIP URLs should be grouped under one official notice candidate
* whether attachment-only preview text such as `첨부파일 있음` should be downgraded or grouped

IMPORTANT:
Do not treat all duplicates the same.

Classify duplicate type:

* exact duplicate
* same source URL duplicate
* same canonical URL duplicate
* same title/source duplicate
* same semantic preview duplicate
* same official notice with multiple attachments
* same topic from multiple sources
* same item sent multiple times due to Telegram suppression failure
* same item published multiple times due to publisher idempotency/race failure

QUESTIONS TO ANSWER:

1. Where is duplicate identity first created?
2. Where is duplicate identity lost?
3. Which duplicate checks currently exist?
4. Which duplicate checks only work for exact same URL?
5. Which checks fail when candidate_id differs but title/source/summary are the same?
6. Which checks fail when `bbs_seq` differs but the notice preview is identical?
7. Is there a representative candidate rule before Telegram review?
8. Is there a representative candidate rule before Facebook publish?
9. Can the system distinguish:

   * same notice with multiple attachments
   * multiple different notices from same board
   * same article collected twice
   * same topic from multiple trusted sources
10. Is there any race condition where two jobs can publish the same READY candidate?
11. Does publish success update state atomically before another job can read it?
12. Does Telegram review suppression happen before or after message composition?
13. Does attachment metadata affect duplicate grouping safely?

FORBIDDEN:

* No code modifications.
* No DB writes.
* No migrations.
* No scheduler changes.
* No Facebook publisher changes.
* No Telegram callback/runtime changes.
* No auth/env/config changes.
* No external API calls.
* No real Telegram messages.
* No real Facebook posts.
* Do not delete duplicate data.

OUTPUT REPORT IN KOREAN.
Technical identifiers, file paths, table names, class names, methods, enum/status values, and command names must remain in original form.

REPORT FORMAT:

# READ_ONLY_AUDIT REPORT: WorkConnect Duplicate Review/Publish Pipeline

## 1. Pre-Review

* AREA:
* MODE:
* Risk:
* Protected areas touched:
* Files inspected:

## 2. Duplicate Cases Observed

Summarize Case A and Case B.
Classify each as exact duplicate, semantic duplicate, attachment duplicate, Telegram duplicate, Facebook duplicate, or race-condition candidate.

## 3. Current Pipeline Duplicate Map

For each stage, list existing duplicate keys/checks:

* collector/raw source
* normalized candidate
* content queue
* Telegram review
* Facebook publish

## 4. Where Duplicate Identity Is Lost

Identify exact code paths where same/near-same item can receive a new candidate_id or bypass suppression.

## 5. Telegram Review Duplicate Audit

Explain how `telegram_review_key`, `semantic_review_key`, `content_candidate_id + message_preview`, and suppression window work.
Explain why different candidate IDs or different `bbs_seq` values may still create repeated Telegram messages.

## 6. Facebook Publish Idempotency Audit

Check whether same source/canonical/title/content can be published twice.
Check whether READY -> PUBLISHING or equivalent atomic claim exists.
Check race-condition risk.

## 7. Attachment Notice Grouping Audit

Check how official notices with ZIP/PDF attachments are represented.
Determine whether multiple attachments or `downloadAllZip.do` links should be grouped into one official notice candidate.

## 8. Recommended Fix Strategy

Do not implement.
Recommend staged fixes.

Suggested phases:

1. Add read-only duplicate diagnostics/admin visibility.
2. Add representative candidate grouping for attachment notices.
3. Strengthen Telegram semantic duplicate suppression.
4. Add pre-publish idempotency check by source/canonical/title/content fingerprint.
5. Add atomic READY -> PUBLISHING claim if missing.
6. Add duplicate reason logging.

For each phase:

* AREA
* MODE
* Risk
* likely files
* protected area involvement
* verification plan

## 9. CODE_TASK_CANDIDATE

Suggest next Codex tasks.

At minimum include:

1. Telegram duplicate suppression guarded fix
2. Attachment notice grouping audit/fix
3. Facebook publish idempotency read-only audit
4. Pre-publish duplicate check guarded fix
5. READY -> PUBLISHING race-condition audit

## 10. Stop Conditions Encountered

Record any point where publisher/scheduler/Telegram protected behavior would be required for implementation.

## 11. Final Recommendation

State the safest next implementation task.

## Execution Result - 2026-06-21 READ_ONLY_AUDIT

Status: COMPLETED

Report saved:

* `DOC/walkthrough/execution-history/2026-06-21/workconnect-duplicate-review-publish-pipeline-audit.md`

Summary:

* Case A was classified as `Facebook duplicate` / `race-condition candidate` / possible same URL identity split.
* Case B was classified as `semantic preview duplicate` / `attachment duplicate` / official notice grouping issue.
* `social_news.candidate` has representative and duplicate counters, but Facebook publish lacks a visible atomic `READY_TO_PUBLISH -> PUBLISHING` claim.
* `content.content_candidate` uniqueness is `raw_ref_table/raw_ref_id`, so same URL/title can receive a new `content_candidate_id` when the raw reference differs.
* Telegram suppression exists through `telegram_review_key`, `semantic_review_key`, and `content_candidate_id + message_preview`, but URL-first identity and a 6-hour window can miss different `bbs_seq` attachment-style notices.
* Recommended first implementation task: add read-only duplicate diagnostics/admin visibility before changing Telegram or Facebook runtime behavior.

Protected areas not touched:

* DB/migration
* Facebook publisher
* content publisher
* scheduler
* Telegram runtime/callback behavior
* auth/env/config
* external API behavior
* actual collection
* actual publishing

!wc-fix

PURPOSE FUNCTION:
Improve the WorkConnect Codex harness so ordinary user follow-up requests default to review-only behavior unless the user explicitly asks for implementation.

AREA:
CODEX_HARNESS_DOCS

MODE:
DOC_ONLY

FOCUS:
Add a default rule that individual user requests should be treated as READ_ONLY_AUDIT / review-only by default.

Codex must not edit code, DB, scheduler, publisher, Telegram runtime, auth, env/config, or external API behavior unless the user explicitly gives an implementation command such as `!wc-fix`, “수정해”, “구현해”, “코드 반영해”, or “패치해”.

TIMEBOX:
30m

READ FIRST:

* CODEX_BOOTSTRAP.md or AGENTS.md if present
* DOC/architecture/05_CODEX_HARNESS_GUIDE.md
* DOC/architecture/06_WORK_AREA_REGISTRY.md
* DOC/walkthrough/YYYY-MM-DD - execute prompt.md

TASK:
Documentation-only harness update.

Add a trigger/default rule:

TRIGGER CARD: INDIVIDUAL_REQUEST_DEFAULT_REVIEW

Condition:

* User gives an individual issue/request such as:

  * “이거 봐봐”
  * “이거 이상한데?”
  * “이거 검토하자”
  * “다음 요청”
  * “이거 왜 이럼?”
  * “이거 중복인 듯”
  * “이거 카테고리 맞나?”
  * “이거 내용 확인”
  * any similar issue-specific follow-up
* And the user does not explicitly request implementation.

Required behavior:

* Treat the request as READ_ONLY_AUDIT by default.
* Inspect and report only.
* Do not modify runtime code.
* Do not modify DB.
* Do not run migrations.
* Do not change scheduler, publisher, Telegram runtime/callback, auth, env/config, or external API behavior.
* Do not publish or send real external notifications.
* If a fix is needed, produce a CODE_TASK_CANDIDATE instead of implementing it.
* Ask for or wait for explicit `!wc-fix` / implementation approval before editing.

Explicit implementation triggers:

* `!wc-fix`
* “수정해”
* “구현해”
* “코드 반영해”
* “패치해”
* “바로 고쳐”
* “적용해”
* any clearly bounded implementation prompt with AREA/MODE/FOCUS

Rule:

* `!wc-audit` always means READ_ONLY_AUDIT.
* `!wc-fix` means implementation may proceed only inside the declared AREA/MODE and only after pre-review.
* Ambiguous requests must default to READ_ONLY_AUDIT, not GUARDed_FIX.
* If Codex is unsure whether the user wants code changes, it must stop and ask or produce a review report only.

Add closeout reinforcement:

* A chat-only response is incomplete for walkthrough-driven work.
* A report must be saved under `DOC/walkthrough/execution-history/YYYY-MM-DD/` when the request is handled through walkthrough.
* Today’s execute prompt must be updated.
* The WorkConnect completion marker must appear exactly once as the final line.
* `loose marker count` must be 0.
* If `loose marker count != 0`, fix the execute prompt marker state or record a harness closeout failure.

FORBIDDEN:

* No runtime code changes.
* No DB changes.
* No migration.
* No scheduler changes.
* No Facebook publisher changes.
* No Telegram runtime/callback changes.
* No auth/env/config changes.
* No external API calls.

OUTPUT REPORT IN KOREAN.
Technical identifiers, command names, file paths, and trigger names must remain in original form.

REPORT FORMAT:

# DOC_ONLY REPORT: Individual Request Default Review Rule

## 1. Pre-Review

* AREA:
* MODE:
* Risk:
* Protected areas touched:
* Files inspected:
* Files modified:

## 2. Changes Made

List the exact documents and sections updated.

## 3. Default Review Rule Added

Explain how ordinary individual requests now default to READ_ONLY_AUDIT.

## 4. Explicit Fix Triggers

List commands/phrases that allow implementation.

## 5. Closeout Reinforcement

Explain marker/report persistence requirements, including `loose marker count = 0`.

## 6. Verification

Confirm:

* trigger card exists
* default ambiguous request behavior is READ_ONLY_AUDIT
* `!wc-fix` remains the explicit implementation path
* protected areas were not touched
* WorkConnect completion marker state is valid

## 7. Final Recommendation

State how future individual user requests should be handled.

ADDITIONAL REQUIRED UPDATE:

Add a trigger/rule for official notice ZIP attachment handling.

TRIGGER CARD: OFFICIAL_NOTICE_ATTACHMENT_REVIEW_REQUIRED

Condition:

* A collected official notice contains a ZIP attachment.
* The source/menu label implies immigration, foreign employment, or foreign-worker relevance.
* The generated review content only says generic text such as `첨부파일 있음`.
* The system cannot confirm the actual file contents inside the ZIP.
* The notice is classified as `IMMIGRATION_INFO / IMMIGRATION_NOTICE` only because of source/menu/category label.

Required behavior:

* Do not treat ZIP attachment existence as publishable content.
* Do not classify the notice as immigration/foreign-worker content only from menu/source label.
* Do not generate public content from `첨부파일 있음`.
* Do not send or promote the ZIP as a public content artifact before its contents are inspected.
* Keep the original source notice and ZIP metadata as source evidence.
* Mark the item as `ATTACHMENT_REVIEW_REQUIRED`, `EVIDENCE_ONLY`, or the closest existing non-public review state.
* Inspect ZIP metadata first:

  * attachment filename
  * file size
  * file extension
  * source notice title
  * original notice URL
  * bbs_seq / bbs_id
  * attachment count if available
* If ZIP contains PDF/HWP/HWPX/DOC/DOCX/XLS/XLSX, inspect or extract text from the actual document before domain classification.
* Classify based on document content, not source menu alone.
* If the document is not about foreign hiring, foreign worker rights, visa, stay status, immigration, employment permit system, or settlement-relevant labor rights, do not promote it as WorkConnect public content.
* If the document is general labor policy, small-business support, youth training, social insurance, or domestic employment support, downgrade or reclassify accordingly.

Specific classification guidance:

* K-New Deal Academy / youth training notices:

  * not `IMMIGRATION_INFO`
  * not `FOREIGN_WORKER_HIRING`
  * likely `EMPLOYMENT_INFO / TRAINING_PROGRAM`
  * publish only if eligibility for foreign residents, international students, or visa holders is confirmed
* Small business labor-management / AI labor law consultation / fake 3.3 contract notices:

  * not `IMMIGRATION_INFO`
  * may be `LABOR_RIGHTS` only if it provides practical worker-rights guidance relevant to foreign workers
  * otherwise store as source evidence or low-priority policy reference
* Generic MOEL press releases:

  * do not become public WorkConnect content unless they pass target-user/actionability gates

Attachment review rule:

* ZIP attachments must not be sent repeatedly to Telegram as independent review items if they belong to the same official notice group.
* Multiple `bbs_seq` items with nearly identical title/source/preview should be audited for attachment-group duplication.
* Prefer grouping under one official notice candidate using future keys such as:

  * `official_notice_key`
  * `attachment_group_key`
  * `notice_title_hash`
  * `source_name + notice_date + normalized_title`
* Until grouping exists, keep such items as review-only / evidence-only and do not publicize.

Add to default review behavior:

* If the user asks about ZIP/PDF official notice relevance, default to READ_ONLY_AUDIT.
* Do not implement changes unless the user explicitly provides `!wc-fix`.

Recommended future CODE_TASK_CANDIDATE:

1. READ_ONLY_AUDIT: MOEL/MOJ/Hikorea attachment notice classification path
2. GUARDED_FIX: Prevent ZIP-only `첨부파일 있음` from becoming Facebook Format Preview
3. GUARDED_FIX: Add attachment metadata review fields to Telegram review message
4. READ_ONLY_AUDIT: Design `official_notice_key` / `attachment_group_key`
5. READ_ONLY_AUDIT: PDF/HWP attachment extraction pipeline for official notices

## Execution Result - 2026-06-21 DOC_ONLY

Status: COMPLETED

Report saved:

* `DOC/walkthrough/execution-history/2026-06-21/individual-request-default-review-rule-doc-only-report.md`

Files modified:

* `CODEX_BOOTSTRAP.md`
* `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
* `DOC/architecture/06_WORK_AREA_REGISTRY.md`
* `DOC/walkthrough/2026-06-21 - execute prompt.md`
* `DOC/walkthrough/execution-history/2026-06-21/individual-request-default-review-rule-doc-only-report.md`

Summary:

* Added `TRIGGER CARD: INDIVIDUAL_REQUEST_DEFAULT_REVIEW`.
* Added `TRIGGER CARD: OFFICIAL_NOTICE_ATTACHMENT_REVIEW_REQUIRED`.
* Added the default rule that ambiguous individual requests are `READ_ONLY_AUDIT` unless an explicit implementation trigger is present.
* Added official notice ZIP/PDF attachment handling guidance for `IMMIGRATION_DOMAIN`.
* Reinforced closeout behavior for report persistence and loose marker repair.

Protected areas not touched:

* runtime code
* DB/migration
* scheduler
* Facebook publisher
* content publisher
* Telegram runtime/callback behavior
* auth/env/config
* external API behavior

!wc-fix

PURPOSE FUNCTION:
WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.

AREA:
IMMIGRATION_DOMAIN + CONTENT_QUEUE + TELEGRAM_REPORTING

MODE:
GUARDED_FIX

FOCUS:
Prevent MOEL/MOJ/Hikorea official notice ZIP attachments from being repeatedly sent to Telegram review or misclassified as `IMMIGRATION_INFO / IMMIGRATION_NOTICE` based only on source/menu labels.

This task must not reduce official notice collection.
It must only improve attachment review readiness, classification safety, and Telegram review suppression/formatting.

TIMEBOX:
60m

READ FIRST:

* CODEX_BOOTSTRAP.md or AGENTS.md if present
* DOC/architecture/05_CODEX_HARNESS_GUIDE.md
* DOC/architecture/06_WORK_AREA_REGISTRY.md
* DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
* DOC/architecture/03_SYSTEM_ARCHITECTURE.md
* DOC/walkthrough/YYYY-MM-DD - execute prompt.md
* DOC/walkthrough/execution-history/2026-06-21/workconnect-duplicate-review-publish-pipeline-audit.md if present
* DOC/walkthrough/execution-history/2026-06-21/individual-request-default-review-rule-doc-only-report.md if present

BACKGROUND:
The operator observed repeated Telegram review messages like:

```text
Source: IMMIGRATION_INFO / IMMIGRATION_NOTICE / 고용노동부 외국인고용 관련 공지
Format: LINK_OR_TEXT
Template: ALERT_REVIEW
Link: https://www.moel.go.kr/common/downloadAllZip.do?bbs_seq=19547&bbs_id=12
Facebook Format Preview:
첨부파일 있음
Attached file:
19547_20260621012124.zip
```

Problems:

1. ZIP attachment existence is being treated as reviewable content.
2. The source/menu label `고용노동부 외국인고용 관련 공지` causes `IMMIGRATION_INFO / IMMIGRATION_NOTICE` classification before document contents are inspected.
3. Preview text `첨부파일 있음` is not meaningful public/review content.
4. Different `bbs_seq` values repeatedly create similar Telegram messages.
5. Uploaded sample PDFs from these ZIPs were mostly not foreign hiring or immigration content:

   * K-New Deal Academy youth training notice
   * Small business/labor-management support notice
6. These should be collected as official source evidence, but not promoted or repeatedly sent as WorkConnect review content until their actual attachment contents are inspected.

IMPORTANT PRODUCT DECISION:
Do not block collection of official notices or ZIP attachments.

Official notice and attachment data may still be collected and stored as:

* raw source evidence
* official notice metadata
* attachment metadata
* future document extraction input
* evidence-only item

However:

* Do not generate public/review content only from `첨부파일 있음`.
* Do not classify as `IMMIGRATION_INFO / IMMIGRATION_NOTICE` only because the menu/source label says foreign employment.
* Do not repeatedly send ZIP files to Telegram before content inspection.
* Do not treat a ZIP file itself as publishable content.

TARGET BEHAVIOR:
For official notices with ZIP/PDF/HWP/HWPX/DOC/DOCX/XLS/XLSX attachments:

1. Collection remains enabled.
2. Raw notice and attachment metadata remain stored.
3. If the only usable body/summary is `첨부파일 있음` or equivalent attachment-only text:

   * do not create normal Facebook Format Preview
   * do not attach ZIP files repeatedly to Telegram review
   * mark or display as `ATTACHMENT_REVIEW_REQUIRED`, `EVIDENCE_ONLY`, `DOCUMENT_EXTRACTION_REQUIRED`, or closest existing non-public review state
4. Telegram review, if sent, should be metadata-only and non-public:

   * source name
   * notice title
   * bbs_seq / bbs_id
   * attachment filename
   * attachment size
   * reason: `attachment_content_not_inspected`
   * status: `evidence_only`
   * no Facebook post preview
   * no public hashtags
   * no attached ZIP file unless explicitly enabled for operator debugging
5. If the current flow cannot safely create a metadata-only review:

   * suppress Telegram review for ZIP-only attachment items
   * log/surface reason using existing diagnostics
6. Keep item available for future PDF/HWP extraction pipeline.

CLASSIFICATION SAFETY RULE:
If actual attachment/body contents are not inspected:

* Do not final-classify as `IMMIGRATION_INFO / IMMIGRATION_NOTICE`.
* Use a provisional state if available:

  * `ATTACHMENT_REVIEW_REQUIRED`
  * `EVIDENCE_ONLY`
  * `DOCUMENT_EXTRACTION_REQUIRED`
  * `CLASSIFICATION_PENDING`
* If no such state exists, use the closest existing review-only/non-public mechanism without DB migration.

If document content is later inspected:

* K-New Deal Academy / youth training notice:

  * not `IMMIGRATION_INFO`
  * not `FOREIGN_WORKER_HIRING`
  * likely `EMPLOYMENT_INFO / TRAINING_PROGRAM`
  * publish only if eligibility for foreign residents/international students/visa holders is confirmed
* Small business labor-management / AI labor law consultation / fake 3.3 notice:

  * not `IMMIGRATION_INFO`
  * may be `LABOR_RIGHTS` only if it provides practical worker-rights guidance relevant to foreign workers
  * otherwise evidence-only or low-priority policy reference

DUPLICATE / SPAM SUPPRESSION RULE:
Add deterministic suppression for attachment-only official notice reviews using existing fields only.

Do not require DB migration.

Recommended grouping keys using existing fields:

* `source_name + bbs_id + normalized_title`
* `source_name + normalized_title + notice_date`
* `downloadAllZip.do + bbs_id + normalized title`
* attachment filename/size only as secondary metadata, not primary content identity

If different `bbs_seq` items have:

* same source/menu
* same or near-same title
* same generic preview text such as `첨부파일 있음`
* same template/format
  then suppress repeated Telegram review or downgrade to evidence-only unless there is a meaningful content difference.

IMPLEMENTATION SCOPE:
Inspect and modify only the minimum necessary sections in likely files such as:

* `SRC/foreign_worker_life_info_collector/content/service.py`
* `SRC/foreign_worker_life_info_collector/content/repository.py`
* Telegram review/message builder file if present
* official notice collector/normalizer file only if needed for metadata classification
* related tests if they already exist

Allowed:

* Add deterministic attachment-only review guard.
* Add metadata-only Telegram review formatting if it can be done without changing callback/runtime behavior.
* Suppress repeated ZIP-only Telegram review using existing duplicate/suppression mechanisms.
* Add validation reason strings:

  * `attachment_content_not_inspected`
  * `zip_attachment_evidence_only`
  * `official_notice_attachment_review_required`
  * `generic_attachment_preview_not_publishable`
  * `source_menu_label_classification_pending`
* Add or update tests using local mock data only.

Forbidden:

* Do not reduce official notice collection coverage.
* Do not delete source data.
* Do not run DB migrations.
* Do not add destructive DB changes.
* Do not change scheduler behavior.
* Do not change Telegram approval/reject callback behavior.
* Do not change Telegram bot runtime state.
* Do not send real Telegram messages.
* Do not change Facebook publisher behavior.
* Do not change Facebook payload/token/retry/frequency.
* Do not publish to Facebook.
* Do not change auth/env/config.
* Do not call external APIs.

PRE-REVIEW REPORT BEFORE EDITING:
Print a short pre-review in Korean:

* AREA:
* MODE:
* Risk:
* Files inspected:
* Files planned to modify:
* Protected areas involved:
* Decision:
* Verification plan:

STOP CONDITIONS:
Stop and report if:

* the fix requires DB migration
* the fix requires scheduler changes
* the fix requires Telegram callback/runtime behavior changes
* the fix requires Facebook publisher changes
* the code cannot distinguish review message formatting from actual Telegram sending behavior
* attachment-only suppression cannot be implemented without guessing
* classification ownership is unclear between official notice collector and content queue
* source collection would need to be reduced

VERIFICATION:
Run safe local checks only.

Required if possible:

* mock official notice with ZIP attachment and preview `첨부파일 있음` -> no normal Facebook Format Preview
* mock official notice with ZIP attachment and no extracted body -> classification pending/evidence-only/review-required state
* mock repeated ZIP-only notices with same source/title/generic preview -> duplicate/suppression behavior triggers
* confirm ZIP attachment is not sent as Telegram file in normal review path unless explicit debug mode exists
* confirm official notice collection path not reduced
* confirm no DB migration
* confirm no protected area files changed
* confirm no external API calls
* confirm no real Telegram/Facebook output

CLOSEOUT REQUIRED:
This is walkthrough-driven Codex work.

At completion:

* Save final report under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
* Update today’s `DOC/walkthrough/YYYY-MM-DD - execute prompt.md`
* If a harness miss or recurring issue is found, update `DOC/correction-loop/`
* Verify exact WorkConnect completion marker count = 1
* Verify old decorated Korean completion marker count = 0
* Verify loose completion marker count = 0
* Verify final line is the WorkConnect completion marker
* State protected areas touched or not touched

OUTPUT REPORT IN KOREAN.
Technical identifiers, file paths, class names, function names, table names, enum/status values, and command names must remain in original form.

REPORT FORMAT:

# GUARDED_FIX REPORT: Official Notice Attachment Review Guardrail

## 1. Pre-Review

* AREA:
* MODE:
* Risk:
* Protected areas touched:
* Files inspected:
* Files modified:

## 2. Current Cause

Explain why ZIP-only official notices were classified/reviewed as `IMMIGRATION_INFO / IMMIGRATION_NOTICE` and repeatedly sent to Telegram.

## 3. Changes Made

List each changed file and exact behavior changed.

## 4. Collection Coverage

Confirm that MOEL/MOJ/Hikorea official notice and attachment collection was not reduced.

## 5. Attachment-Only Review Guard

Explain how `첨부파일 있음` / ZIP-only notices are now handled.

## 6. Classification Safety

Explain how source/menu label alone no longer finalizes immigration/foreign-worker classification before content inspection.

## 7. Telegram Review Suppression / Formatting

Explain whether repeated ZIP-only reviews are suppressed or converted to metadata-only review.
Confirm ZIP files are not repeatedly attached to normal Telegram review.

## 8. Verification

List tests/scripts/checks run and result.

## 9. Protected Areas

Confirm:

* Facebook publisher not touched
* scheduler not touched
* Telegram callback/runtime not touched
* auth/env/config not touched
* DB/migration not touched
* external API not called
* no real publish/notification sent

## 10. Remaining Risks

List remaining ambiguity, especially:

* official_notice_key / attachment_group_key still needed
* PDF/HWP extraction pipeline still needed
* true content-based reclassification still pending

## 11. Next CODE_TASK_CANDIDATE

Suggest the next safest task, likely:

* READ_ONLY_AUDIT: official notice attachment extraction pipeline
* READ_ONLY_AUDIT: official_notice_key / attachment_group_key design
* GUARDED_FIX: PDF text extraction for official notices in review-only mode

## 12. Closeout

Confirm:

* report saved
* execute prompt updated
* correction-loop updated if needed
* WorkConnect completion marker verification passed

## Execution Result - 2026-06-21 GUARDED_FIX

Status: COMPLETED

Report saved:

* `DOC/walkthrough/execution-history/2026-06-21/official-notice-attachment-review-guardrail-report.md`

Files modified:

* `SRC/foreign_worker_life_info_collector/content/service.py`
* `SRC/foreign_worker_life_info_collector/tests/test_content_exclusion_gate.py`
* `DOC/walkthrough/2026-06-21 - execute prompt.md`
* `DOC/walkthrough/execution-history/2026-06-21/official-notice-attachment-review-guardrail-report.md`

Summary:

* Added attachment-only official notice guard in `content_quality_gate()`.
* ZIP-only official notices now become `ATTACHMENT_REVIEW_REQUIRED`, `DOCUMENT_EXTRACTION_REQUIRED`, and `EVIDENCE_ONLY`.
* Normal Telegram review eligibility is false for attachment-only official notices.
* Direct review message generation now uses metadata-only evidence text and omits `[Facebook Format Preview]`.
* Official notice collection was not reduced.

Verification:

* `python -m py_compile SRC\foreign_worker_life_info_collector\content\service.py SRC\foreign_worker_life_info_collector\tests\test_content_exclusion_gate.py`: PASS
* `$env:PYTHONPATH='SRC'; python -m unittest foreign_worker_life_info_collector.tests.test_content_exclusion_gate`: PASS, `Ran 10 tests`
* `$env:PYTHONPATH='SRC'; python -m unittest foreign_worker_life_info_collector.tests.test_content_review_dedupe`: PASS, `Ran 7 tests`

Protected areas not touched:

* Facebook publisher
* scheduler
* Telegram callback/runtime behavior
* auth/env/config
* DB/migration
* external API behavior
* actual Telegram/Facebook output

[WC_EXECUTION_COMPLETE]
