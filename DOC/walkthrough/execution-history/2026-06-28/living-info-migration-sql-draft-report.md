# GUARDED_FIX REPORT: LIVING_INFO Migration SQL Draft

## 1. Pre-Review

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM
- Protected areas touched: NO
- Files inspected:
  - `CODEX_BOOTSTRAP.md`
  - `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  - `DOC/walkthrough/2026-06-28 - execute prompt.md`
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-physical-schema-design-report.md`
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-server-integration-split-design-report.md`
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_06_immigration_info.sql`
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_07_content_candidate.sql`
- Files modified:
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql`
  - `DOC/walkthrough/2026-06-28 - execute prompt.md`
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-migration-sql-draft-report.md`

## 2. Migration Draft Created

- file path:
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql`
- tables included:
  - `living_info.source_item`
  - `living_info.normalized_item`
  - `living_info.source_signal`
  - `living_info.topic_cluster`
  - `living_info.topic_cluster_item`
- indexes included:
  - 25 `CREATE INDEX IF NOT EXISTS` / `CREATE UNIQUE INDEX IF NOT EXISTS` statements
- constraints included:
  - `ux_living_source_item_duplicate_key`
  - `ck_living_source_item_active_yn`
  - `ux_living_normalized_item_source`
  - `ck_living_normalized_validation_needed`
  - `ck_living_source_signal_validation_needed`
  - `ck_living_source_signal_count`
  - `ux_living_topic_cluster_identity`
  - `ck_living_topic_cluster_public_ready`
  - `ck_living_topic_cluster_source_count`
  - `ck_living_topic_cluster_evidence_count`
  - `ck_living_topic_cluster_community_count`
  - `ck_living_topic_cluster_official_count`
  - `ck_living_topic_cluster_secondary_count`
  - `ck_living_topic_cluster_spread_count`
  - `ck_living_topic_cluster_item_one_source`

## 3. Design Boundaries Preserved

- no runtime code changed: YES
- no DB migration executed: YES
- no backfill executed: YES
- no publisher/scheduler/Telegram/auth/env touched: YES
- `content.content_candidate` remains final review/publish owner: YES
- `living_info` does not publish directly: YES

The SQL file is an additive draft only. It does not alter `content.content_candidate`, `social_news.candidate`, scheduler, publisher, Telegram runtime, admin auth, or env/config.

## 4. Table Summary

### `living_info.source_item`

Stores source/domain evidence for living information. It preserves URL, source name/type, language, country, raw title/summary/body, trust level, privacy risk, duplicate key, content hash, source status, source reference, and raw payload.

It is not publishable content.

### `living_info.normalized_item`

Stores normalized category, source usage, info/signal type, target user, action type, topic key candidate, validation need, scoring, confidence, reason, and status for a single `source_item`.

It is domain meaning, not final public message text.

### `living_info.source_signal`

Stores community/trend/discovery demand signals. It keeps signal metadata, topic candidate, target user, pain point summary, signal count, privacy risk, access policy, validation flag, and raw payload.

It intentionally has no unique constraint yet because community/trend grouping is not stable.

### `living_info.topic_cluster`

Groups evidence and signals into potential living guide topics. It tracks source/evidence/community/official/secondary counts, source spread, readiness score, public-candidate flag, validation status, cluster status, and recent signal/evidence timestamps.

This is the first living-domain object that may later produce `content.content_candidate`.

### `living_info.topic_cluster_item`

Connects `topic_cluster` to either `normalized_item` or `source_signal`.

It has a PostgreSQL-compatible check constraint requiring exactly one of:

```text
normalized_item_id
source_signal_id
```

It also has partial unique indexes for normalized-item and source-signal membership.

## 5. Verification

Checks run:

```text
Test-Path SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql
Select-String CREATE SCHEMA IF NOT EXISTS living_info
Select-String CREATE TABLE IF NOT EXISTS living_info.source_item
Select-String CREATE TABLE IF NOT EXISTS living_info.normalized_item
Select-String CREATE TABLE IF NOT EXISTS living_info.source_signal
Select-String CREATE TABLE IF NOT EXISTS living_info.topic_cluster
Select-String CREATE TABLE IF NOT EXISTS living_info.topic_cluster_item
Select-String forbidden SQL keyword pattern: \b(DROP|TRUNCATE|DELETE|UPDATE|INSERT)\b
Select-String verification query snippets
git status --short
```

Results:

```text
exists=True
create_schema=1
source_item=1
normalized_item=1
source_signal=1
topic_cluster=1
topic_cluster_item=1
forbidden_sql_keywords=0
index_count=25
constraint_count=15
verification_query_tables=1
verification_query_indexes=1
verification_query_constraints=1
```

No migration was executed.

## 6. Remaining Risks

- migration not executed yet
- backfill preview still needed
- repository/service not created yet
- social_news split not implemented yet
- topic clustering not implemented yet
- rollback remains manual and requires explicit approval because destructive rollback is not automated

## 7. Next CODE_TASK_CANDIDATE

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY
MODE: GUARDED_FIX
FOCUS:
Create a read-only backfill preview utility for current `content.content_candidate` rows with `source_domain = 'LIVING_INFO'`.
WHY:
The migration draft exists, but current LIVING_INFO rows must be classified before any migration/backfill because they include duplicates, missing URLs, low-value categories, and already-posted rows.
RISK: MEDIUM
PROTECTED AREA:
DB mutation, migration execution, collector execution, publisher, scheduler, Telegram runtime, auth/env/config
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/living_info/backfill_preview.py
SRC/foreign_worker_life_info_collector/living_info/__init__.py
DOC/walkthrough/execution-history/2026-06-28/
RECOMMENDED NEXT PROMPT:
Implement a local read-only backfill preview utility that exports proposed actions to JSON/CSV and performs no INSERT, UPDATE, DELETE, migration execution, collector execution, or external notification.
```

Alternative next task only if explicitly approved:

```text
Apply the `living_info` migration to local PostgreSQL after backup/approval and run verification SQL.
```

## 8. Closeout

- report saved: YES
- execute prompt updated: YES
- marker verification passed: YES
- protected areas touched: NO


!wc-fix

PURPOSE FUNCTION:
WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.

AREA:
LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY

MODE:
GUARDED_FIX

FOCUS:
Implement a local read-only backfill preview utility for existing `content.content_candidate` rows where `source_domain = 'LIVING_INFO'`.

The utility must inspect current LIVING_INFO-labeled rows, join or reference their original `social_news.candidate` source rows when possible, classify each row into a proposed migration/backfill action, and export JSON/CSV preview files.

This task creates code for preview only.
It must not insert, update, delete, migrate, publish, send Telegram messages, run collectors, or execute scheduler jobs.

TIMEBOX:
90m

READ FIRST:

* CODEX_BOOTSTRAP.md or AGENTS.md if present
* DOC/architecture/00_PRODUCT_NORTH_STAR.md
* DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
* DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
* DOC/architecture/03_SYSTEM_ARCHITECTURE.md
* DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
* DOC/architecture/05_CODEX_HARNESS_GUIDE.md
* DOC/architecture/06_WORK_AREA_REGISTRY.md
* DOC/database/01_CURRENT_DB_MAP.md
* DOC/database/03_CONTENT_CURRENT.md
* DOC/database/06_DOMAIN_DATA_CURRENT.md
* DOC/walkthrough/execution-history/2026-06-28/living-info-physical-schema-design-report.md if present
* DOC/walkthrough/execution-history/2026-06-28/living-info-server-integration-split-design-report.md if present
* DOC/walkthrough/execution-history/2026-06-28/living-info-migration-sql-draft-report.md if present
* `SRC/foreign_worker_life_info_collector/content/service.py`
* `SRC/foreign_worker_life_info_collector/content/repository.py`
* `SRC/foreign_worker_life_info_collector/storage/db/postgres.py`
* `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql`
* `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py` if needed

BACKGROUND:
A migration SQL draft for `living_info` now exists but has not been executed.

Current state:

* `living_info` physical tables are not created yet.
* Existing LIVING_INFO data is currently represented as `content.content_candidate.source_domain = 'LIVING_INFO'`.
* Existing source reference is usually:

  * `raw_ref_table = 'social_news.candidate'`
  * `raw_ref_id = social_news.candidate.id`
* Earlier audit observed around 54 current LIVING_INFO rows.
* Some rows include duplicates, missing URLs, low-value travel/culture/local event categories, and already-posted rows.

Goal:
Create a safe utility that produces a migration/backfill preview before any DB schema execution or data migration.

TARGET OUTPUT:
Create a local utility such as:

```text
SRC/foreign_worker_life_info_collector/living_info/backfill_preview.py
```

Also create package init if needed:

```text
SRC/foreign_worker_life_info_collector/living_info/__init__.py
```

The utility should output preview files only, for example:

```text
storage/generated/living_info/backfill_preview.json
storage/generated/living_info/backfill_preview.csv
storage/generated/living_info/backfill_summary.json
```

If the project has an existing generated/output directory convention, follow it.

REQUIRED BEHAVIOR:
The utility must:

1. Connect to local PostgreSQL using existing `storage.db.postgres.connect()`.
2. Run SELECT-only queries.
3. Read current `content.content_candidate` rows where:

```sql
source_domain = 'LIVING_INFO'
```

4. Prefer rows with:

```sql
raw_ref_table = 'social_news.candidate'
```

5. Join or fetch related `social_news.candidate` rows using `raw_ref_id` when possible.
6. Classify each row into one proposed backfill action:

```text
MIGRATE_SOURCE_ITEM
MIGRATE_NORMALIZED_ITEM
DUPLICATE_SKIP
LOW_VALUE_ARCHIVE
NEEDS_MANUAL_REVIEW
DO_NOT_MIGRATE
```

7. Produce a row-level preview with fields needed to later create:

   * `living_info.source_item`
   * `living_info.normalized_item`

8. Produce summary counts:

   * total rows inspected
   * action counts
   * category counts
   * status counts
   * duplicate URL counts
   * missing URL count
   * low-value category count
   * already-posted count
   * manual-review count

9. Do not require `living_info` tables to exist.

10. If `living_info` tables do not exist, utility must still run because it previews from current content/social tables.

STRICT READ-ONLY SAFETY:
The utility must not contain or execute:

* `INSERT`
* `UPDATE`
* `DELETE`
* `TRUNCATE`
* `DROP`
* `ALTER`
* `CREATE TABLE`
* `CREATE SCHEMA`
* migration execution
* collector execution
* scheduler execution
* Telegram send
* Facebook publish
* external API call

Use SELECT only.

CLASSIFICATION RULES:

## A. `DO_NOT_MIGRATE`

Use when:

* no usable title and no usable summary/body
* source link is missing and source cannot be traced
* contains system/diagnostic text only
* obvious broken parser output
* non-Korea/global-only content
* dangerous/private/PII-like content if found

## B. `LOW_VALUE_ARCHIVE`

Use when:

* generic travel
* generic tourism
* generic culture/entertainment
* generic local event
* generic lifestyle
* generic economy/stock/crypto
* domestic politics without foreign resident actionability
* broad safety news without clear action for foreign residents

Candidate categories:

* `travel`
* `culture`
* `local_events`
* `lifestyle`
* broad `safety` when non-actionable

## C. `DUPLICATE_SKIP`

Use when:

* same effective URL as another row and this is not representative
* same normalized title + source + summary hash as another row
* same `raw_ref_table/raw_ref_id` appears more than once
* missing URL group has repeated same generated title/summary

Representative priority:

1. usable URL exists
2. status is not `ARCHIVED`
3. highest `final_publish_score`
4. more complete body/summary
5. latest collected/updated timestamp
6. lowest id as final tie-breaker

## D. `NEEDS_MANUAL_REVIEW`

Use when:

* URL missing but title/summary may be useful
* category is broad or ambiguous
* status is already `POSTED` but value is unclear
* item is sensitive labor/health/legal/finance but validation source is unclear
* duplicate relation is unclear
* source URL points to search/RSS/root/redirect rather than article/page

## E. `MIGRATE_SOURCE_ITEM`

Use when:

* valid source URL or canonical URL exists
* useful title exists
* item can be preserved as source evidence
* but not enough confidence for normalized living guide usage yet

## F. `MIGRATE_NORMALIZED_ITEM`

Use when:

* valid source evidence exists
* practical category is clear
* source usage can be assigned
* info/signal type can be assigned
* actionability/repeatability is not zero
* no duplicate/low-value/block reason applies

NORMALIZATION PREVIEW FIELDS:
For each row, output:

Source preview:

* `content_candidate_id`
* `raw_ref_table`
* `raw_ref_id`
* `source_url`
* `canonical_url`
* `effective_url`
* `source_name`
* `source_type`
* `language`
* `raw_title`
* `raw_summary`
* `raw_body_available_yn`
* `published_at`
* `collected_at`
* `source_trust_level`
* `privacy_risk_level`
* `duplicate_key`
* `content_hash`

Normalized preview:

* `normalized_primary_category`
* `normalized_secondary_category`
* `source_usage`
* `info_signal_type`
* `target_user`
* `action_type`
* `topic_key_candidate`
* `validation_needed_yn`
* `validation_source_type`
* `actionability_score`
* `repeatability_score`
* `source_reliability_score`
* `normalization_confidence`
* `normalization_reason`
* `backfill_action`
* `backfill_reason`

Original/current metadata:

* `current_category`
* `current_source_domain`
* `current_content_type`
* `current_status`
* `final_publish_score`
* `quality_score`
* `practical_value_score`
* `facebook_post_url`
* `published_state_yn`

CATEGORY MAPPING:
Map current categories to normalized categories.

Examples:

* `housing` -> `HOUSING`
* `banking` / `finance` -> `BANKING_FINANCE`
* `healthcare` -> `HEALTHCARE`
* `insurance` -> `HEALTHCARE` or `BANKING_FINANCE` depending on text, otherwise `HEALTHCARE`
* `transportation` -> `TRANSPORTATION`
* `korean_language` / `education` -> `EDUCATION_LANGUAGE`
* `local_community` / `settlement_life` -> `DAILY_LIFE` or `REGIONAL_SUPPORT`
* `safety` -> `SAFETY_SCAM` only if actionable, otherwise `LOW_VALUE_NOISE`
* `travel` / `culture` / `local_events` / `lifestyle` -> usually `LOW_VALUE_NOISE` unless practical foreign-resident support exists

SOURCE USAGE MAPPING:
Assign one of:

```text
PUBLIC_GUIDE_CANDIDATE
CARD_CANDIDATE
TEXT_REVIEW_ONLY
SOURCE_EVIDENCE
OFFICIAL_VALIDATION_SOURCE
COMMUNITY_SIGNAL
TREND_SIGNAL
TOPIC_CLUSTER_MATERIAL
ATTACHMENT_REVIEW_REQUIRED
DOCUMENT_EXTRACTION_REQUIRED
LOW_VALUE_ARCHIVE
BLOCK_PUBLIC_CONTENT
```

For this utility:

* most usable rows should be `SOURCE_EVIDENCE` or `TOPIC_CLUSTER_MATERIAL`
* avoid `PUBLIC_GUIDE_CANDIDATE` unless clearly official/secondary and actionable
* community/social rows should be `COMMUNITY_SIGNAL` only if present
* low-value rows should be `LOW_VALUE_ARCHIVE`
* blocked rows should be `BLOCK_PUBLIC_CONTENT`

INFO/SIGNAL TYPE:
Assign one of:

```text
INFORMATIONAL
TREND_SIGNAL
NEWS_EVENT
OFFICIAL_UPDATE
ATTACHMENT_ONLY
LOW_VALUE_NOISE
```

CLI REQUIREMENTS:
Support command line options:

```text
--limit 500
--output-dir storage/generated/living_info
--format both
```

Allowed formats:

* `json`
* `csv`
* `both`

If command line parsing is too much for first version, implement simple defaults and document limitation.

TESTS:
Add tests if project test convention supports it.

Suggested test file:

```text
SRC/foreign_worker_life_info_collector/tests/test_living_info_backfill_preview.py
```

Test deterministic classifier functions without DB.

Test cases:

* housing row with valid URL -> migrate or normalized item candidate
* travel row -> low value archive
* duplicate URL lower score -> duplicate skip
* missing URL useful title -> manual review
* system text -> do not migrate
* safety row with no actionability -> low value archive
* healthcare row -> healthcare informational evidence

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

* utility requires DB writes
* utility requires migration execution
* utility requires `living_info` tables to exist
* utility requires collector/scheduler execution
* utility requires Telegram/Facebook runtime changes
* classification cannot be implemented without guessing beyond preview level
* existing table names/columns are too different from expected and need DB metadata clarification

VERIFICATION:
Run safe checks only.

Required:

* `python -m py_compile` for new files
* unit tests if added
* inspect file for forbidden SQL keywords:

  * `INSERT`
  * `UPDATE`
  * `DELETE`
  * `TRUNCATE`
  * `DROP`
  * `ALTER`
  * `CREATE TABLE`
  * `CREATE SCHEMA`
* If running utility is safe and DB access is local:

  * run with small `--limit 20`
  * verify JSON/CSV output generated
  * verify no DB writes occurred
* If DB access is not available:

  * do not fail implementation
  * report utility not executed due to DB unavailable

FORBIDDEN:

* No DB writes.
* No migration execution.
* No collector execution.
* No scheduler changes.
* No publisher changes.
* No Telegram runtime/callback changes.
* No auth/env/config changes.
* No external API calls.
* No real Telegram/Facebook output.
* Do not modify `content.content_candidate`.
* Do not modify `social_news.candidate`.
* Do not apply migration.

CLOSEOUT REQUIRED:
This is walkthrough-driven Codex work.

At completion:

* Save final report under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
* Update today’s `DOC/walkthrough/YYYY-MM-DD - execute prompt.md`
* If a harness miss or recurring issue is found, update `DOC/correction-loop/`
* Verify exact `[WC_EXECUTION_COMPLETE]` count = 1
* Verify old decorated Korean completion marker count = 0
* Verify loose completion marker count = 0
* Verify final line is `[WC_EXECUTION_COMPLETE]`
* State protected areas touched or not touched

OUTPUT REPORT IN KOREAN.
Technical identifiers, file paths, table names, column names, SQL snippets, CLI commands, enum values, and command names must remain in original form.

REPORT FORMAT:

# GUARDED_FIX REPORT: LIVING_INFO Backfill Preview Utility

## 1. Pre-Review

* AREA:
* MODE:
* Risk:
* Protected areas touched:
* Files inspected:
* Files modified:

## 2. Utility Created

* file path:
* CLI:
* output files:
* read-only safety:

## 3. Classification Rules Implemented

Summarize:

* `MIGRATE_SOURCE_ITEM`
* `MIGRATE_NORMALIZED_ITEM`
* `DUPLICATE_SKIP`
* `LOW_VALUE_ARCHIVE`
* `NEEDS_MANUAL_REVIEW`
* `DO_NOT_MIGRATE`

## 4. Output Schema

List JSON/CSV fields.

## 5. Verification

List:

* py_compile
* tests
* forbidden SQL keyword scan
* sample run result if executed
* output file path if generated

## 6. Protected Areas

Confirm:

* DB writes not performed
* migration not executed
* scheduler not touched
* publisher not touched
* Telegram runtime not touched
* auth/env/config not touched
* external API not called

## 7. Remaining Risks

Mention:

* preview only
* migration still not executed
* repository/service still not created
* social_news split not implemented
* manual review still needed before backfill

## 8. Next CODE_TASK_CANDIDATE

Recommend next task:

* apply migration after explicit approval
  or
* review backfill preview output first

## 9. Closeout

Confirm report saved, execute prompt updated, and marker verification passed.

# WORKCONNECT LIVING_INFO IMPLEMENTATION QUEUE

GLOBAL RULE:
Execute only one task per run.

After each task:

* save report under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
* update today’s execute prompt
* verify `[WC_EXECUTION_COMPLETE]`
* stop and wait for user review
* do not automatically continue to the next task

Do not skip phases.
Do not bundle multiple implementation phases into one run.

---

## TASK 1: LIVING_INFO Backfill Preview Utility

COMMAND:
`!wc-fix`

AREA:
`LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY`

MODE:
`GUARDED_FIX`

FOCUS:
Create a local read-only backfill preview utility for existing `content.content_candidate` rows where `source_domain = 'LIVING_INFO'`.

Purpose:
Classify current LIVING_INFO-labeled rows before migration/backfill.

Required output:

* JSON preview
* CSV preview
* summary JSON

Allowed:

* SELECT-only DB read
* local output file generation
* deterministic row classification

Forbidden:

* DB write
* migration execution
* collector execution
* scheduler changes
* publisher changes
* Telegram runtime changes
* external API calls

Stop after report.

---

## TASK 2: Review Backfill Preview Output

COMMAND:
`!wc-audit`

AREA:
`LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY`

MODE:
`READ_ONLY_AUDIT`

FOCUS:
Analyze the generated backfill preview output.

Questions:

* How many rows are worth migrating?
* How many are duplicate/noise?
* How many have missing URL?
* How many are low-value travel/culture/local event items?
* Which rows should be `MIGRATE_SOURCE_ITEM`?
* Which rows should be `MIGRATE_NORMALIZED_ITEM`?
* Which rows should be `DUPLICATE_SKIP`, `LOW_VALUE_ARCHIVE`, `DO_NOT_MIGRATE`, or `NEEDS_MANUAL_REVIEW`?

Allowed:

* read generated JSON/CSV
* inspect only
* produce migration recommendation

Forbidden:

* DB write
* migration execution
* code modification

Stop after report.

---

## TASK 3: Apply `living_info` Migration Only After Explicit Approval

COMMAND:
`!wc-fix`

AREA:
`LIVING_DOMAIN + DATA_SOURCE_QUALITY`

MODE:
`GUARDED_FIX`

FOCUS:
Apply the reviewed `living_info` migration to local PostgreSQL only after explicit user approval.

Precondition:
User must explicitly say:
`승인. living_info migration 실행해.`

Allowed:

* execute additive migration only
* run verification SQL
* report before/after schema state

Forbidden:

* data backfill
* runtime code changes
* scheduler changes
* publisher changes
* Telegram runtime changes
* destructive DDL

Verification:

* `living_info.source_item` exists
* `living_info.normalized_item` exists
* `living_info.source_signal` exists
* `living_info.topic_cluster` exists
* `living_info.topic_cluster_item` exists
* indexes exist
* constraints exist

Stop after report.

---

## TASK 4: Create `living_info` Repository Skeleton

COMMAND:
`!wc-fix`

AREA:
`LIVING_DOMAIN + DATA_SOURCE_QUALITY`

MODE:
`GUARDED_FIX`

FOCUS:
Create `living_info` repository/models skeleton after migration is applied.

Files likely:

* `SRC/foreign_worker_life_info_collector/living_info/__init__.py`
* `SRC/foreign_worker_life_info_collector/living_info/models.py`
* `SRC/foreign_worker_life_info_collector/living_info/repository.py`
* tests

Allowed:

* table-level repository methods
* schema readiness check
* read/write methods for future use
* tests with mocked/local DB where safe

Forbidden:

* modifying `sync_social_news()`
* scheduler changes
* publisher changes
* Telegram runtime changes
* auto backfill
* auto ingestion

Stop after report.

---

## TASK 5: Manual/Dev-Only Backfill Into `living_info`

COMMAND:
`!wc-fix`

AREA:
`LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY`

MODE:
`GUARDED_FIX`

FOCUS:
After preview approval and migration, implement a manual/dev-only backfill tool for approved rows.

Precondition:
User must explicitly approve which preview actions can be inserted.

Allowed:

* insert only approved preview rows into `living_info.source_item`
* insert matching `living_info.normalized_item`
* limited row count
* dry-run mode required
* before/after counts required

Forbidden:

* automatic backfill
* content candidate creation
* scheduler changes
* publisher changes
* Telegram runtime changes
* deleting old rows

Stop after report.

---

## TASK 6: Split `sync_social_news()` Living Rows

COMMAND:
`!wc-fix`

AREA:
`LIVING_DOMAIN + CONTENT_QUEUE + SOCIAL_NEWS_CANDIDATE`

MODE:
`GUARDED_FIX`

FOCUS:
Modify `ContentService.sync_social_news()` so living-classified rows no longer directly become `content.content_candidate`.

Target behavior:

* non-living social news:

  * keep current `SOCIAL_NEWS / NEWS_ARTICLE` path
* living-classified rows:

  * ingest into `living_info.source_item`
  * normalize into `living_info.normalized_item`
  * do not create `content.content_candidate` directly

Allowed:

* modify content sync boundary
* call `LivingInfoService.ingest_from_social_news_candidate(...)`
* add tests proving non-living path still works

Forbidden:

* publisher changes
* scheduler changes
* Telegram runtime changes
* deleting existing content rows
* creating public content from living rows

Stop after report.

---

## TASK 7: Audit `sync_living_info()` Content Candidate Path

COMMAND:
`!wc-audit`

AREA:
`LIVING_DOMAIN + CONTENT_QUEUE`

MODE:
`READ_ONLY_AUDIT`

FOCUS:
Design how future `living_info.topic_cluster` should become `content.content_candidate`.

Questions:

* What readiness fields are required?
* How should `raw_ref_table = 'living_info.topic_cluster'` work?
* What payload fields are required for Telegram/card preview?
* How to prevent community-only signal from becoming public content?
* How to preserve `content.content_candidate` as final review/publish owner?

Forbidden:

* code changes
* DB writes
* publisher/Telegram/scheduler changes

Stop after report.

---

## TASK 8: Implement `sync_living_info()` After Audit Approval

COMMAND:
`!wc-fix`

AREA:
`LIVING_DOMAIN + CONTENT_QUEUE`

MODE:
`GUARDED_FIX`

FOCUS:
Implement `ContentService.sync_living_info()` only after the previous audit is approved.

Target behavior:

* read ready `living_info.topic_cluster`
* create `content.content_candidate`
* use:

  * `raw_ref_table = 'living_info.topic_cluster'`
  * `raw_ref_id = topic_cluster.id`
  * `source_domain = 'LIVING_INFO'`
  * `content_type = 'LIVING_GUIDE'`
* no auto-publish
* Telegram review remains normal content candidate review

Forbidden:

* Facebook publisher changes
* scheduler changes
* Telegram callback/runtime changes
* community-only content candidate creation

Stop after report.

