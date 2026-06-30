!wc-audit

PURPOSE FUNCTION:
WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.

AREA:
LIVING_DOMAIN + DATA_SOURCE_QUALITY + CONTENT_QUEUE + SYSTEM_ARCHITECTURE_DOCS

MODE:
READ_ONLY_AUDIT

FOCUS:
Design the first real `living_info` database schema and migration/backfill strategy.

Current finding:
`living_info` physical tables do not appear to exist yet. Current LIVING_INFO behavior is represented mainly through `content.content_candidate.source_domain = 'LIVING_INFO'` and data copied from `social_news.candidate`.

The goal is to move from ?쐋iving info as content label??to ?쐋iving info as a real source/domain data layer.??

This is READ_ONLY design work.
Do not modify DB.
Do not create migrations.
Do not modify runtime code.
Do not backfill data.
Do not run collectors.
Do not publish or send notifications.

TIMEBOX:
90m

READ FIRST:

* CODEX_BOOTSTRAP.md or AGENTS.md if present
* DOC/architecture/00_PRODUCT_NORTH_STAR.md
* DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
* DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
* DOC/architecture/03_SYSTEM_ARCHITECTURE.md
* DOC/architecture/05_CODEX_HARNESS_GUIDE.md
* DOC/architecture/06_WORK_AREA_REGISTRY.md
* DOC/database/00_DB_ARCHITECTURE_INDEX.md if present
* DOC/database/01_CURRENT_DB_MAP.md
* DOC/database/06_DOMAIN_DATA_CURRENT.md
* DOC/database/TO_BE_DB_ARCHITECTURE.md if present
* SRC/foreign_worker_life_info_collector/content/service.py
* SRC/foreign_worker_life_info_collector/content/repository.py
* recent LIVING_INFO source spectrum / normalization / card guardrail reports if present

BACKGROUND:
The current system has guardrails preventing single-news living cards and attachment-only official notices from becoming public content too early.

However, there is no dedicated `living_info` storage layer.
As a result, living information is currently mixed into:

* `social_news.candidate`
* `content.content_candidate`
* source_domain/content_type labels

This causes problems:

* no durable living-domain raw/normalized storage
* no topic_key layer
* no source_signal layer
* no fact_point/card_point layer
* no clean way to build topic-based living guides
* category normalization is mixed with publishing queue logic
* existing small LIVING_INFO data cannot be managed independently

AUDIT GOALS:

1. Confirm current physical DB state for living-related schemas/tables.
2. Confirm whether `living_info` exists or is only planned.
3. Identify current LIVING_INFO data locations.
4. Design a minimal first `living_info` schema.
5. Design how new incoming data should be stored going forward.
6. Design how existing small LIVING_INFO data should be migrated/backfilled later.
7. Decide what should stay in `content.content_candidate` and what should move to `living_info`.
8. Produce safe future CODE_TASK_CANDIDATE items.

DATABASE RULES:
Read-only inspection only.

Allowed:

* inspect DDL/docs
* inspect repository SQL
* run read-only SELECT if local DB access is already configured
* draft SQL only

Forbidden:

* CREATE SCHEMA
* CREATE TABLE
* ALTER
* INSERT
* UPDATE
* DELETE
* TRUNCATE
* DROP
* migration execution
* backfill execution
* collector execution
* scheduler changes
* publisher changes
* Telegram runtime changes
* external API calls

IF DB ACCESS IS AVAILABLE, RUN READ-ONLY CHECKS:
Check whether these schemas/tables exist:

* `living_info`
* `living_info.source_item`
* `living_info.raw_item`
* `living_info.normalized_item`
* `living_info.source_signal`
* `living_info.fact_point`
* `living_info.card_point`
* `living_info.topic_cluster`
* `housing_info`
* `healthcare_info`
* `banking_info`
* `transportation_info`

Check existing LIVING_INFO data in current structures:

```sql
SELECT source_domain, content_type, category, COUNT(*)
FROM content.content_candidate
GROUP BY source_domain, content_type, category
ORDER BY COUNT(*) DESC;
```

```sql
SELECT id, raw_ref_table, raw_ref_id, source_domain, content_type, category,
       title, source_name, source_url, status, final_publish_score
FROM content.content_candidate
WHERE source_domain = 'LIVING_INFO'
ORDER BY id DESC
LIMIT 100;
```

```sql
SELECT raw_ref_table, COUNT(*)
FROM content.content_candidate
WHERE source_domain = 'LIVING_INFO'
GROUP BY raw_ref_table
ORDER BY COUNT(*) DESC;
```

If DB access is not available, provide these as draft queries only.

PROPOSED FIRST SCHEMA TO EVALUATE:

Option A: Minimal 3-table schema

1. `living_info.source_item`
   Purpose:
   Store source evidence from official, secondary, news, blog, and community/discovery sources.

Candidate fields:

* `id`
* `source_url`
* `canonical_url`
* `source_name`
* `source_type`
* `source_access_policy`
* `language`
* `country`
* `region_in_korea`
* `raw_title`
* `raw_summary`
* `raw_body`
* `published_at`
* `collected_at`
* `source_trust_level`
* `privacy_risk_level`
* `duplicate_key`
* `content_hash`
* `active_yn`
* `raw_payload`

2. `living_info.normalized_item`
   Purpose:
   Store normalized classification and intended usage.

Candidate fields:

* `id`
* `source_item_id`
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
* `normalization_confidence`
* `normalization_reason`
* `status`
* `created_at`
* `updated_at`

3. `living_info.topic_cluster`
   Purpose:
   Group multiple source/normalized items into potential living guide topics.

Candidate fields:

* `id`
* `topic_key`
* `primary_category`
* `secondary_category`
* `target_user`
* `action_type`
* `source_count`
* `evidence_count`
* `community_signal_count`
* `official_source_count`
* `source_spread_count`
* `readiness_score`
* `public_candidate_ready_yn`
* `last_signal_at`
* `created_at`
* `updated_at`

Option B: Add `fact_point` / `card_point` now

4. `living_info.fact_point`
   Purpose:
   Extract validated factual points from source items.

5. `living_info.card_point`
   Purpose:
   Store card-ready short points.

Evaluate whether Option B is too early.
Recommend whether to start with Option A first.

DESIGN QUESTIONS:

1. Should `living_info.source_item` store both official and community signal sources?
2. Should community data be stored as source rows, or should it go into a separate `living_info.source_signal` table?
3. Should `fact_point` and `card_point` be created now or later?
4. Should `topic_cluster` reference normalized items directly or through a join table?
5. How should existing `content.content_candidate` LIVING_INFO rows be migrated?
6. How should duplicate rows be handled before migration?
7. Should raw duplicate rows be preserved while only representative normalized rows are promoted?
8. What unique constraints are needed?
9. What indexes are needed for topic generation?
10. What data should remain only in `content.content_candidate`?
11. What should be the new source-to-content path?

REQUIRED BACKFILL DESIGN:
Design but do not execute a backfill plan.

Existing candidate source:

* `content.content_candidate`
* filtered by `source_domain = 'LIVING_INFO'`
* plus linked `social_news.candidate` via `raw_ref_table = 'social_news.candidate'` and `raw_ref_id`

Backfill phases:

1. read-only count
2. duplicate grouping
3. representative selection
4. source_item preview
5. normalized_item preview
6. manual review of ambiguous rows
7. migration only after approval
8. backfill only after dry-run report

Backfill output should classify each existing row as:

* `MIGRATE_SOURCE_ITEM`
* `MIGRATE_NORMALIZED_ITEM`
* `DUPLICATE_SKIP`
* `LOW_VALUE_ARCHIVE`
* `NEEDS_MANUAL_REVIEW`
* `DO_NOT_MIGRATE`

NORMALIZATION TARGETS:
The schema must support:

Primary category:

* `WORK`
* `VISA_IMMIGRATION`
* `LABOR_RIGHTS`
* `HOUSING`
* `HEALTHCARE`
* `BANKING_FINANCE`
* `TELECOM_DIGITAL_ID`
* `TRANSPORTATION`
* `PUBLIC_SERVICES`
* `LEGAL_AID`
* `EDUCATION_LANGUAGE`
* `FAMILY_CHILDCARE`
* `SAFETY_SCAM`
* `REGIONAL_SUPPORT`
* `DAILY_LIFE`
* `COMMUNITY_SIGNAL`
* `TREND_SIGNAL`
* `LOW_VALUE_NOISE`

Source usage:

* `PUBLIC_GUIDE_CANDIDATE`
* `CARD_CANDIDATE`
* `TEXT_REVIEW_ONLY`
* `SOURCE_EVIDENCE`
* `OFFICIAL_VALIDATION_SOURCE`
* `COMMUNITY_SIGNAL`
* `TREND_SIGNAL`
* `TOPIC_CLUSTER_MATERIAL`
* `ATTACHMENT_REVIEW_REQUIRED`
* `DOCUMENT_EXTRACTION_REQUIRED`
* `LOW_VALUE_ARCHIVE`
* `BLOCK_PUBLIC_CONTENT`

Info/signal type:

* `INFORMATIONAL`
* `TREND_SIGNAL`
* `NEWS_EVENT`
* `OFFICIAL_UPDATE`
* `ATTACHMENT_ONLY`
* `LOW_VALUE_NOISE`

OUTPUT REPORT IN KOREAN.
Technical identifiers, table names, column names, file paths, SQL snippets, and enum values must remain in original form.

REPORT FORMAT:

# READ_ONLY_AUDIT REPORT: LIVING_INFO Physical Schema Design

## 1. Pre-Review

* AREA:
* MODE:
* Risk:
* Protected areas touched:
* Files inspected:
* DB read-only queries run:
* Runtime/code changes: NO

## 2. Current State

Explain whether `living_info` physical tables exist.
Explain where current LIVING_INFO data is stored.

## 3. Current LIVING_INFO Data Count

If DB access is available, show counts.
If unavailable, provide query drafts.

## 4. Schema Design Recommendation

Compare:

* Option A: minimal 3-table schema
* Option B: include fact_point/card_point now
* Option C: separate source_signal table

Recommend first version.

## 5. Proposed Tables

For each table:

* purpose
* columns
* keys
* unique constraints
* indexes
* status lifecycle
* ownership
* relation to `content.content_candidate`

## 6. Source-to-Content Flow

Design the new flow:

```text
external source
-> living_info.source_item
-> living_info.normalized_item
-> living_info.topic_cluster
-> content.content_candidate
```

Mention where `fact_point/card_point` will fit later.

## 7. Existing Data Backfill Plan

Design migration/backfill from current LIVING_INFO rows.

Include:

* read-only count query
* duplicate grouping
* representative selection
* dry-run preview
* manual review
* final backfill later

Do not execute.

## 8. Duplicate Handling Before Migration

Define how to avoid moving duplicate noise.

Include:

* same source_url
* same canonical_url
* same title/summary hash
* same topic_key_candidate
* representative item
* low-value archive

## 9. Category/Usage/Info-Type Support

Show how the schema supports:

* primary category
* secondary category
* source usage
* info_signal_type
* target_user
* action_type
* validation_needed
* topic_key_candidate

## 10. Risks

Include:

* over-schema risk
* premature fact_point/card_point risk
* duplicate migration risk
* content queue ownership risk
* DB migration risk
* rollback requirement

## 11. Recommended Next Steps

Give phased next tasks:

1. DOC_ONLY schema policy
2. migration SQL draft only
3. dry-run backfill preview utility
4. manual review of preview
5. guarded migration after approval
6. controlled backfill after backup

## 12. CODE_TASK_CANDIDATE

Suggest next Codex tasks:

* DOC_ONLY living_info schema policy
* GUARDED_FIX migration SQL draft file only, no execution
* GUARDED_FIX read-only backfill preview utility
* READ_ONLY_AUDIT content path switch impact
* GUARDED_FIX source-to-living_info write path later

## 13. Final Recommendation

State the safest first implementation step.

## Execution Result - 2026-06-28

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY + CONTENT_QUEUE + SYSTEM_ARCHITECTURE_DOCS`
- MODE: `READ_ONLY_AUDIT`
- Result: COMPLETED
- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-physical-schema-design-report.md`
- DB read-only checks: YES
  - `living_info`, `housing_info`, `healthcare_info`, `banking_info`, `transportation_info` physical schemas/tables were not found.
  - Current `LIVING_INFO` rows are stored in `content.content_candidate`.
  - Observed `LIVING_INFO` row count: `54`.
  - Observed `raw_ref_table`: `social_news.candidate` for all `54` rows.
- Runtime/code changes: NO
- DB/migration changes: NO
- Collector execution: NO
- External notification/publish: NO
- Protected areas touched: NO
- Main finding:
  - `living_info` is currently a content label, not a physical source/domain data layer.
  - First schema should separate `source_item`, `normalized_item`, `source_signal`, `topic_cluster`, and `topic_cluster_item`.
  - `fact_point/card_point` should not be created yet.
  - Existing `LIVING_INFO` rows require dry-run preview and manual review before any backfill.

!wc-audit

PURPOSE FUNCTION:
WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.

AREA:
LIVING_DOMAIN + DATA_SOURCE_QUALITY + CONTENT_QUEUE + SOCIAL_NEWS_CANDIDATE + SYSTEM_ARCHITECTURE_DOCS

MODE:
READ_ONLY_AUDIT

FOCUS:
Design the implementation process for connecting the new `living_info` physical schema to the server flow and separating LIVING_INFO data from the current `social_news -> content.content_candidate` path.

Current status:

* DB/schema design work is complete.
* `living_info` tables are not created yet.
* Runtime write path is not changed yet.
* Current LIVING_INFO rows are still represented as `content.content_candidate.source_domain = 'LIVING_INFO'`.
* Current source reference is `raw_ref_table = 'social_news.candidate'`.

This is design/audit only.
Do not modify code.
Do not create tables.
Do not run migrations.
Do not write DB data.
Do not run collectors.
Do not change scheduler.
Do not change Telegram/Facebook runtime behavior.
Do not publish or send external notifications.

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
* DOC/database/02_SOCIAL_NEWS_CURRENT.md
* DOC/database/03_CONTENT_CURRENT.md
* DOC/database/06_DOMAIN_DATA_CURRENT.md
* DOC/database/TO_BE_DB_ARCHITECTURE.md
* DOC/walkthrough/execution-history/YYYY-MM-DD/living-info-physical-schema-design report if present
* SRC/foreign_worker_life_info_collector/content/service.py
* SRC/foreign_worker_life_info_collector/content/repository.py
* SRC/foreign_worker_life_info_collector/social/news/pipeline.py
* SRC/foreign_worker_life_info_collector/social/news/category_rotation.py
* SRC/foreign_worker_life_info_collector/storage/db/postgres.py
* existing migration files under SRC/foreign_worker_life_info_collector/storage/db/migrations/

BACKGROUND:
Current behavior:

```text
social_news.candidate
-> ContentService.social_news_payload()
-> content.content_candidate
```

When `is_living_content(...)` is true, `social_news_payload()` sets:

```text
source_domain = "LIVING_INFO"
content_type = "LIVING_GUIDE"
raw_ref_table = "social_news.candidate"
raw_ref_id = social_news.candidate.id
```

This means living information is currently a content label, not a durable living-domain data layer.

Target future behavior:

```text
external source / social news / official page / support source
-> living_info.source_item
-> living_info.normalized_item
-> living_info.topic_cluster_item
-> living_info.topic_cluster
-> content.content_candidate
-> content.publish_log
```

Community/trend behavior:

```text
community/trend/discovery source
-> living_info.source_signal
-> living_info.topic_cluster_item
-> living_info.topic_cluster
```

Community/trend signals must not directly create `content.content_candidate`.

DESIGN OBJECTIVES:

1. Decide how new `living_info` tables will be connected to current server code.
2. Decide where the new repository/service layer should live.
3. Design how `social_news.candidate` rows currently classified as living info should be separated and injected into `living_info`.
4. Design how future `content.content_candidate` rows should reference `living_info.topic_cluster` instead of `social_news.candidate`.
5. Design how existing small LIVING_INFO rows should be migrated/backfilled later.
6. Preserve `content.content_candidate` as the final review/publish owner.
7. Avoid touching Facebook publisher, Telegram runtime, scheduler, auth/env/config, or external API behavior.
8. Produce phased implementation tasks.

SCOPE TO INSPECT:

1. Current content sync path

* `ContentService.sync_social_news()`
* `social_news_payload()`
* `is_living_content()`
* `ContentRepository.upsert_candidate()`
* `content.content_candidate` uniqueness rules
* raw reference fields:

  * `raw_ref_table`
  * `raw_ref_id`
  * `source_domain`
  * `content_type`

2. Current social news classification path

* category generation
* `content_category`
* `content_priority_group`
* `category_rotation`
* duplicate/representative candidate logic
* current living categories:

  * housing
  * banking
  * healthcare
  * transportation
  * insurance
  * korean_language
  * cost_of_living
  * local_community
  * education
  * settlement_life
  * safety
  * travel/culture/local_events if currently included

3. Proposed `living_info` server layer
   Design likely modules/classes:

```text
living_info/repository.py
living_info/service.py
living_info/normalizer.py
living_info/topic_clusterer.py
living_info/backfill_preview.py
```

or another minimal structure consistent with current project conventions.

4. Proposed DB connection usage

* How to reuse `storage/db/postgres.py`
* Whether to use existing `connect()` style
* Whether new repository should follow `ContentRepository` patterns
* What transaction boundaries are needed
* How to avoid writes until migration is approved

5. Proposed source-to-living path
   Design how social/news living candidates should flow.

Possible future path:

```text
ContentService.sync_social_news()
-> if not living:
      existing social news -> content.content_candidate path
   if living:
      LivingInfoService.ingest_from_social_news_candidate(row)
      do not immediately create content.content_candidate
```

or:

```text
SocialNewsPipeline
-> living_info ingestion handoff before content sync
```

Compare both and recommend safer first implementation.

6. Proposed content candidate creation path from living_info
   Future path:

```text
living_info.topic_cluster
-> ContentService.sync_living_info()
-> content.content_candidate
```

Design this without implementing.

QUESTIONS TO ANSWER:

## A. Migration / table creation process

1. What migration file should be created?
2. Should it create only schema/tables or also indexes/constraints?
3. Should it include enum-like check constraints or leave values as varchar initially?
4. Should it be additive only?
5. What rollback strategy should be documented?
6. What verification SQL should confirm table creation?

## B. Server connection process

1. Which module should own `living_info` DB access?
2. Should `living_info.repository` directly use `connect()`?
3. Should repository methods be read/write separated?
4. Which methods are needed first?

Candidate repository methods:

```text
upsert_source_item_from_social_news(row)
upsert_normalized_item(source_item_id, normalization_payload)
find_source_item_by_duplicate_key(duplicate_key)
list_cluster_candidates()
upsert_topic_cluster(...)
attach_normalized_item_to_cluster(...)
```

But do not implement them yet.

## C. Social news separation process

1. Should `social_news_payload()` stop producing `LIVING_INFO` content candidates?
2. Should living-classified rows be inserted into `living_info.source_item` instead?
3. Should existing `SOCIAL_NEWS` non-living items keep the old flow?
4. What happens to rows that are currently `travel`, `culture`, `local_events`, or broad `safety`?
5. How do we avoid duplicate migration/injection?
6. How do we preserve raw source references?

## D. Existing data migration/backfill

1. How to identify existing LIVING_INFO rows:

   * `content.content_candidate.source_domain = 'LIVING_INFO'`
   * `raw_ref_table = 'social_news.candidate'`
2. How to map them into:

   * `living_info.source_item`
   * `living_info.normalized_item`
3. How to avoid moving low-value/noise rows?
4. How to classify:

   * `MIGRATE_SOURCE_ITEM`
   * `MIGRATE_NORMALIZED_ITEM`
   * `DUPLICATE_SKIP`
   * `LOW_VALUE_ARCHIVE`
   * `NEEDS_MANUAL_REVIEW`
   * `DO_NOT_MIGRATE`
5. Should already `POSTED` rows be migrated?
6. Should missing URL rows be migrated?
7. Should duplicate URL rows be migrated only as representative source items?

## E. Content queue impact

1. How should `content.content_candidate` reference future living content?
2. Should future living candidates use:

```text
raw_ref_table = 'living_info.topic_cluster'
raw_ref_id = living_info.topic_cluster.id
source_domain = 'LIVING_INFO'
content_type = 'LIVING_GUIDE'
```

3. Should single official utility pages use:

```text
raw_ref_table = 'living_info.normalized_item'
raw_ref_id = living_info.normalized_item.id
```

4. How to prevent direct publish from `living_info.source_item`?
5. How to keep Telegram review/card generation working?

## F. Transition strategy

Design phased rollout:

Phase 0:
Documentation/design only.

Phase 1:
Add migration SQL draft only, no execution.

Phase 2:
Create read-only backfill preview utility.

Phase 3:
Execute additive migration after approval.

Phase 4:
Create `living_info.repository` with table-level methods but no scheduler/runtime write path.

Phase 5:
Add manual/dev-only ingestion from existing `content.content_candidate` LIVING_INFO rows into `living_info` after dry-run approval.

Phase 6:
Modify `sync_social_news()` so living-classified rows go to `living_info` instead of directly becoming `content.content_candidate`.

Phase 7:
Add `sync_living_info()` that creates content candidates only from `topic_cluster` objects that pass readiness gates.

Phase 8:
Add future topic clustering and fact/card point generation after validation.

For each phase:

* AREA
* MODE
* Risk
* files likely involved
* protected areas
* verification plan
* stop conditions

IMPORTANT RULES:
Do not implement anything in this audit.
Do not create or edit migration files.
Do not write DB.
Do not modify code.
Do not run collectors.
Do not change scheduler.
Do not change Telegram/Facebook behavior.

OUTPUT REPORT IN KOREAN.
Technical identifiers, file paths, table names, method names, class names, enum/status values, and SQL snippets must remain in original form.

REPORT FORMAT:

# READ_ONLY_AUDIT REPORT: LIVING_INFO Server Integration and Social News Split Design

## 1. Pre-Review

* AREA:
* MODE:
* Risk:
* Protected areas touched:
* Files inspected:
* DB read-only queries run:
* Runtime/code changes: NO

## 2. Current Code Path

Explain current `social_news -> content.content_candidate` path and where `LIVING_INFO` is currently assigned.

## 3. Target Architecture

Design target path:

```text
social_news.candidate
-> living_info.source_item
-> living_info.normalized_item
-> living_info.topic_cluster
-> content.content_candidate
```

## 4. Proposed Server Module Design

Propose modules/classes/functions for `living_info` repository/service/normalizer/clusterer.

## 5. DB Connection and Transaction Design

Explain how to use existing PostgreSQL connection utilities safely.

## 6. Migration Process Design

Define the migration creation/execution sequence, verification SQL, rollback plan, and non-destructive constraints.

## 7. Social News Split Strategy

Explain how living-classified social news should stop going directly to content candidates and instead enter `living_info`.

## 8. Existing LIVING_INFO Backfill Strategy

Design how current `content.content_candidate` rows where `source_domain = 'LIVING_INFO'` should be previewed, deduped, manually reviewed, and later migrated.

## 9. Future Content Candidate Creation from LIVING_INFO

Design how `living_info.topic_cluster` will eventually become `content.content_candidate`.

## 10. Compatibility with Telegram/Card/Facebook

Explain how Telegram review, card generation, and Facebook publishing remain protected and unchanged until content candidates are explicitly created.

## 11. Phased Implementation Plan

List phases 0-8 with risk and verification.

## 12. Stop Conditions

List what must stop implementation.

## 13. CODE_TASK_CANDIDATE

Create next Codex tasks in this order:

1. migration SQL draft only
2. read-only backfill preview utility
3. living_info repository skeleton after migration approval
4. social_news living split guarded fix
5. living_info topic_cluster to content_candidate sync read-only audit
6. topic clustering prototype later

## 14. Final Recommendation

State the safest next implementation step.

## Execution Result - 2026-06-28 - 2

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY + CONTENT_QUEUE + SOCIAL_NEWS_CANDIDATE + SYSTEM_ARCHITECTURE_DOCS`
- MODE: `READ_ONLY_AUDIT`
- Result: COMPLETED
- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-server-integration-split-design-report.md`
- DB read-only checks: YES
  - `living_info_table_count=0`
  - Current `LIVING_INFO` rows still reference `raw_ref_table = social_news.candidate`
  - Observed current `LIVING_INFO` reference count: `54`
- Runtime/code changes: NO
- DB/migration changes: NO
- Collector execution: NO
- External notification/publish: NO
- Protected areas touched: NO
- Main finding:
  - The safest split point is later inside `ContentService.sync_social_news()`, but only after schema and repository exist.
  - The next implementation artifact should be a non-executed `living_info` migration SQL draft.
  - Runtime split should not start before migration draft, preview utility, migration approval, and repository skeleton are ready.

!wc-fix

PURPOSE FUNCTION:
WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.

AREA:
LIVING_DOMAIN + DATA_SOURCE_QUALITY

MODE:
GUARDED_FIX

FOCUS:
Create a non-executed PostgreSQL migration SQL draft for the first physical `living_info` schema.

This task creates a reviewable migration SQL file only.
Do not execute the migration.
Do not modify runtime code.
Do not change content sync behavior.
Do not create or backfill real DB rows.

TIMEBOX:
60m

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
* DOC/database/02_SOCIAL_NEWS_CURRENT.md
* DOC/database/03_CONTENT_CURRENT.md
* DOC/database/06_DOMAIN_DATA_CURRENT.md
* DOC/database/TO_BE_DB_ARCHITECTURE.md
* DOC/walkthrough/execution-history/2026-06-28/living-info-physical-schema-design-report.md if present
* DOC/walkthrough/execution-history/2026-06-28/living-info-server-integration-and-social-news-split-design report if present
* existing migration files under `SRC/foreign_worker_life_info_collector/storage/db/migrations/`

BACKGROUND:
A READ_ONLY_AUDIT confirmed:

```text
living_info_table_count=0
living_ref=LIVING_INFO social_news.candidate 54
```

Current behavior:

```text
social_news.candidate
-> ContentService.social_news_payload()
-> content.content_candidate
```

Current `LIVING_INFO` is only a content label:

```text
source_domain = "LIVING_INFO"
content_type = "LIVING_GUIDE"
raw_ref_table = "social_news.candidate"
raw_ref_id = social_news.candidate.id
```

Target future architecture:

```text
external source / social_news.candidate
-> living_info.source_item
-> living_info.normalized_item
-> living_info.topic_cluster_item
-> living_info.topic_cluster
-> content.content_candidate
-> content.publish_log
```

Community/trend signal path:

```text
community/trend/discovery source
-> living_info.source_signal
-> living_info.topic_cluster_item
-> living_info.topic_cluster
```

Important boundary:
`content.content_candidate` remains the final review/publish owner.
`living_info` stores source/domain evidence and topic structure.
`living_info.source_item` and `living_info.source_signal` must never publish directly.

TASK:
Create a non-executed PostgreSQL migration SQL draft.

Create file:

```text
SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql
```

If this exact date does not match current project convention, use the current date but keep the filename explicit and stable.

MIGRATION REQUIREMENTS:

1. Additive only.
2. No destructive DDL.
3. No data backfill.
4. No INSERT into production data tables.
5. No UPDATE/DELETE/TRUNCATE/DROP.
6. No runtime code changes.
7. Include comments explaining purpose and ownership.
8. Include verification SQL at the bottom as comments.
9. Include rollback guidance as comments, but do not include automatic destructive rollback execution.

CREATE SCHEMA:

```sql
CREATE SCHEMA IF NOT EXISTS living_info;
```

CREATE TABLES:

1. `living_info.source_item`

Purpose:
Store source evidence for living-domain items from official, secondary, trusted media, blog, and source-backed discovery sources.

Columns:

* `id BIGSERIAL PRIMARY KEY`
* `source_url TEXT NOT NULL`
* `canonical_url TEXT NOT NULL DEFAULT ''`
* `publishable_link_url TEXT NOT NULL DEFAULT ''`
* `source_name VARCHAR(200) NOT NULL DEFAULT ''`
* `source_type VARCHAR(60) NOT NULL`
* `source_access_policy VARCHAR(60) NOT NULL DEFAULT 'PUBLIC_PAGE'`
* `language VARCHAR(20) NOT NULL DEFAULT 'en'`
* `country VARCHAR(80) NOT NULL DEFAULT 'Korea'`
* `region_in_korea VARCHAR(120) NOT NULL DEFAULT ''`
* `raw_title TEXT NOT NULL DEFAULT ''`
* `raw_summary TEXT NOT NULL DEFAULT ''`
* `raw_body TEXT NOT NULL DEFAULT ''`
* `published_at TIMESTAMPTZ`
* `collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`
* `last_checked_at TIMESTAMPTZ`
* `source_trust_level VARCHAR(40) NOT NULL DEFAULT 'DISCOVERY'`
* `privacy_risk_level VARCHAR(40) NOT NULL DEFAULT 'LOW'`
* `duplicate_key VARCHAR(160) NOT NULL`
* `content_hash VARCHAR(160) NOT NULL DEFAULT ''`
* `source_status VARCHAR(40) NOT NULL DEFAULT 'COLLECTED'`
* `active_yn CHAR(1) NOT NULL DEFAULT 'Y'`
* `raw_ref_table VARCHAR(120) NOT NULL DEFAULT ''`
* `raw_ref_id BIGINT`
* `raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb`
* `created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`
* `updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`

Constraints:

* `UNIQUE(duplicate_key)`
* `CHECK(active_yn IN ('Y', 'N'))`

Indexes:

* `(source_type, collected_at DESC)`
* `(source_trust_level, collected_at DESC)`
* `(source_status, collected_at DESC)`
* `(canonical_url)`
* `(content_hash)`
* `(raw_ref_table, raw_ref_id)`

2. `living_info.normalized_item`

Purpose:
Store normalized classification and intended usage for a source item.

Columns:

* `id BIGSERIAL PRIMARY KEY`
* `source_item_id BIGINT NOT NULL REFERENCES living_info.source_item(id)`
* `normalized_primary_category VARCHAR(60) NOT NULL`
* `normalized_secondary_category VARCHAR(120) NOT NULL DEFAULT ''`
* `source_usage VARCHAR(60) NOT NULL`
* `info_signal_type VARCHAR(60) NOT NULL`
* `target_user VARCHAR(120) NOT NULL DEFAULT ''`
* `action_type VARCHAR(120) NOT NULL DEFAULT ''`
* `topic_key_candidate VARCHAR(180) NOT NULL DEFAULT ''`
* `validation_needed_yn CHAR(1) NOT NULL DEFAULT 'Y'`
* `validation_source_type VARCHAR(60) NOT NULL DEFAULT ''`
* `actionability_score NUMERIC(8,4) NOT NULL DEFAULT 0`
* `repeatability_score NUMERIC(8,4) NOT NULL DEFAULT 0`
* `source_reliability_score NUMERIC(8,4) NOT NULL DEFAULT 0`
* `normalization_confidence NUMERIC(8,4) NOT NULL DEFAULT 0`
* `normalization_reason TEXT NOT NULL DEFAULT ''`
* `status VARCHAR(40) NOT NULL DEFAULT 'NORMALIZED'`
* `created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`
* `updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`

Constraints:

* `UNIQUE(source_item_id)`
* `CHECK(validation_needed_yn IN ('Y', 'N'))`

Indexes:

* `(normalized_primary_category, normalized_secondary_category)`
* `(topic_key_candidate)`
* `(source_usage, status)`
* `(info_signal_type, status)`
* `(actionability_score DESC, repeatability_score DESC)`

3. `living_info.source_signal`

Purpose:
Store community/trend/discovery demand signals without treating them as facts.

Columns:

* `id BIGSERIAL PRIMARY KEY`
* `signal_source_name VARCHAR(200) NOT NULL DEFAULT ''`
* `signal_source_url TEXT NOT NULL DEFAULT ''`
* `signal_platform VARCHAR(80) NOT NULL DEFAULT ''`
* `signal_type VARCHAR(60) NOT NULL`
* `language VARCHAR(20) NOT NULL DEFAULT ''`
* `country VARCHAR(80) NOT NULL DEFAULT 'Korea'`
* `region_in_korea VARCHAR(120) NOT NULL DEFAULT ''`
* `primary_category VARCHAR(60) NOT NULL`
* `topic_key_candidate VARCHAR(180) NOT NULL DEFAULT ''`
* `target_user VARCHAR(120) NOT NULL DEFAULT ''`
* `pain_point_summary TEXT NOT NULL DEFAULT ''`
* `signal_count INTEGER NOT NULL DEFAULT 1`
* `privacy_risk_level VARCHAR(40) NOT NULL DEFAULT 'MEDIUM'`
* `source_access_policy VARCHAR(60) NOT NULL DEFAULT 'PUBLIC_METADATA_ONLY'`
* `validation_needed_yn CHAR(1) NOT NULL DEFAULT 'Y'`
* `status VARCHAR(40) NOT NULL DEFAULT 'SIGNAL_COLLECTED'`
* `observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`
* `created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`
* `updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`
* `raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb`

Constraints:

* `CHECK(validation_needed_yn IN ('Y', 'N'))`
* `CHECK(signal_count >= 0)`

Indexes:

* `(topic_key_candidate, observed_at DESC)`
* `(primary_category, observed_at DESC)`
* `(signal_type, status)`
* `(privacy_risk_level)`

Do not add a unique constraint yet for `source_signal`.
Reason:
Community/trend signal grouping is not stable yet.

4. `living_info.topic_cluster`

Purpose:
Group source/normalized items and signals into potential living guide topics.

Columns:

* `id BIGSERIAL PRIMARY KEY`
* `topic_key VARCHAR(180) NOT NULL`
* `primary_category VARCHAR(60) NOT NULL`
* `secondary_category VARCHAR(120) NOT NULL DEFAULT ''`
* `target_user VARCHAR(120) NOT NULL DEFAULT ''`
* `action_type VARCHAR(120) NOT NULL DEFAULT ''`
* `source_count INTEGER NOT NULL DEFAULT 0`
* `evidence_count INTEGER NOT NULL DEFAULT 0`
* `community_signal_count INTEGER NOT NULL DEFAULT 0`
* `official_source_count INTEGER NOT NULL DEFAULT 0`
* `secondary_source_count INTEGER NOT NULL DEFAULT 0`
* `source_spread_count INTEGER NOT NULL DEFAULT 0`
* `readiness_score NUMERIC(8,4) NOT NULL DEFAULT 0`
* `public_candidate_ready_yn CHAR(1) NOT NULL DEFAULT 'N'`
* `validation_status VARCHAR(40) NOT NULL DEFAULT 'PENDING'`
* `cluster_status VARCHAR(40) NOT NULL DEFAULT 'OPEN'`
* `last_signal_at TIMESTAMPTZ`
* `last_evidence_at TIMESTAMPTZ`
* `created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`
* `updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`

Constraints:

* `UNIQUE(topic_key, primary_category, target_user, action_type)`
* `CHECK(public_candidate_ready_yn IN ('Y', 'N'))`
* count fields must be non-negative:

  * `source_count >= 0`
  * `evidence_count >= 0`
  * `community_signal_count >= 0`
  * `official_source_count >= 0`
  * `secondary_source_count >= 0`
  * `source_spread_count >= 0`

Indexes:

* `(primary_category, readiness_score DESC)`
* `(public_candidate_ready_yn, readiness_score DESC)`
* `(validation_status, cluster_status)`
* `(last_signal_at DESC NULLS LAST)`
* `(last_evidence_at DESC NULLS LAST)`

5. `living_info.topic_cluster_item`

Purpose:
Represent many-to-many membership between topic clusters and evidence/signal rows.

Columns:

* `id BIGSERIAL PRIMARY KEY`
* `topic_cluster_id BIGINT NOT NULL REFERENCES living_info.topic_cluster(id)`
* `normalized_item_id BIGINT REFERENCES living_info.normalized_item(id)`
* `source_signal_id BIGINT REFERENCES living_info.source_signal(id)`
* `item_role VARCHAR(60) NOT NULL`
* `weight_score NUMERIC(8,4) NOT NULL DEFAULT 1`
* `created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`

Constraints:

* Exactly one of `normalized_item_id` or `source_signal_id` should be present.
* Use a `CHECK` constraint for this if PostgreSQL-compatible.
* Use partial unique indexes:

  * unique `(topic_cluster_id, normalized_item_id)` where `normalized_item_id IS NOT NULL`
  * unique `(topic_cluster_id, source_signal_id)` where `source_signal_id IS NOT NULL`

Indexes:

* `(topic_cluster_id, item_role)`
* `(normalized_item_id)`
* `(source_signal_id)`

IMPORTANT DESIGN RULES:

* Do not create `living_info.fact_point`.
* Do not create `living_info.card_point`.
* Do not create triggers.
* Do not create scheduled jobs.
* Do not create stored procedures.
* Do not insert seed/backfill rows.
* Do not change `content.content_candidate`.
* Do not change `social_news.candidate`.
* Do not alter existing schemas.

COMMENTS TO INCLUDE IN SQL:
Add comments or SQL comments explaining:

* `living_info.source_item` is source/domain evidence, not publishable content.
* `living_info.source_signal` is demand signal only and must not be treated as fact.
* `living_info.topic_cluster` is the first living-domain object that may later produce `content.content_candidate`.
* Final review/publish ownership remains in `content.content_candidate`.
* Community/trend signals must not directly create public content.

VERIFICATION SQL TO INCLUDE AS COMMENTS:
At the bottom of the migration file, include commented verification queries:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'living_info'
ORDER BY table_name;
```

```sql
SELECT indexname
FROM pg_indexes
WHERE schemaname = 'living_info'
ORDER BY indexname;
```

```sql
SELECT
    tc.table_schema,
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'living_info'
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;
```

ROLLBACK COMMENT:
Include a rollback note as SQL comments only:

* Migration is additive.
* Do not automate destructive rollback.
* In local/dev only and with explicit approval, rollback may be `DROP SCHEMA living_info CASCADE`.
* In shared/prod-like environments, disable write path and leave tables in place.

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

* implementing this requires DB execution
* implementing this requires modifying runtime code
* implementing this requires changing scheduler
* implementing this requires changing Telegram or Facebook behavior
* implementing this requires destructive DDL
* existing migration conventions conflict and cannot be resolved safely
* table ownership or relation to `content.content_candidate` becomes unclear

VERIFICATION:
Run safe checks only.

Required:

* inspect created SQL file
* ensure no runtime Python/JS/Java files modified
* ensure no DB execution occurred
* ensure SQL contains no `DROP`, `TRUNCATE`, `DELETE`, `UPDATE`, or data `INSERT`
* ensure migration contains `CREATE SCHEMA IF NOT EXISTS living_info`
* ensure migration contains all five first-version tables:

  * `living_info.source_item`
  * `living_info.normalized_item`
  * `living_info.source_signal`
  * `living_info.topic_cluster`
  * `living_info.topic_cluster_item`
* run no migration
* no external API
* no Telegram/Facebook output

CLOSEOUT REQUIRED:
This is walkthrough-driven Codex work.

At completion:

* Save final report under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
* Update today?셲 `DOC/walkthrough/YYYY-MM-DD - execute prompt.md`
* If a harness miss or recurring issue is found, update `DOC/correction-loop/`
* Verify exact `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]` count = 1
* Verify old decorated Korean completion marker count = 0
* Verify loose completion marker count = 0
* Verify final line is `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]`
* State protected areas touched or not touched

OUTPUT REPORT IN KOREAN.
Technical identifiers, file paths, table names, column names, constraint names, SQL snippets, and command names must remain in original form.

REPORT FORMAT:

# GUARDED_FIX REPORT: LIVING_INFO Migration SQL Draft

## 1. Pre-Review

* AREA:
* MODE:
* Risk:
* Protected areas touched:
* Files inspected:
* Files modified:

## 2. Migration Draft Created

* file path:
* tables included:
* indexes included:
* constraints included:

## 3. Design Boundaries Preserved

Confirm:

* no runtime code changed
* no DB migration executed
* no backfill executed
* no publisher/scheduler/Telegram/auth/env touched
* `content.content_candidate` remains final review/publish owner
* `living_info` does not publish directly

## 4. Table Summary

Summarize each table:

* `living_info.source_item`
* `living_info.normalized_item`
* `living_info.source_signal`
* `living_info.topic_cluster`
* `living_info.topic_cluster_item`

## 5. Verification

List checks run and results.

## 6. Remaining Risks

Mention:

* migration not executed yet
* backfill preview still needed
* repository/service not created yet
* social_news split not implemented yet
* topic clustering not implemented yet

## 7. Next CODE_TASK_CANDIDATE

Recommend next task:

* read-only backfill preview utility
  or
* apply migration only if user explicitly approves

## 8. Closeout

Confirm report saved, execute prompt updated, and marker verification passed.

## Execution Result - 2026-06-28 - 3

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- Result: COMPLETED
- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-migration-sql-draft-report.md`
- Migration draft created:
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql`
- Tables included:
  - `living_info.source_item`
  - `living_info.normalized_item`
  - `living_info.source_signal`
  - `living_info.topic_cluster`
  - `living_info.topic_cluster_item`
- Verification:
  - `CREATE SCHEMA IF NOT EXISTS living_info`: present
  - all five first-version tables: present
  - forbidden SQL keywords `DROP/TRUNCATE/DELETE/UPDATE/INSERT`: 0
  - indexes: 25
  - constraints: 15
  - verification SQL comments: present
- Runtime/code changes: NO
- DB migration executed: NO
- DB data backfill: NO
- Collector execution: NO
- External notification/publish: NO
- Protected areas touched: NO
- Next recommended task:
  - read-only backfill preview utility

!wc-fix

AREA:
LIVING_DOMAIN + DATA_SOURCE_QUALITY

MODE:
GUARDED_FIX

FOCUS:
Consolidate local/manual utility code location.

Rule:
For this project, manual execution tools, preview generators, report exporters, one-off data inspection utilities, and local-only maintenance scripts must go under:

`SRC/foreign_worker_life_info_collector/tools/`

Do not create new files under:

`SRC/foreign_worker_life_info_collector/utils/`

unless the code is a reusable runtime helper imported by production services and explicitly approved.

For the current LIVING_INFO backfill preview utility:

* place it under `tools/`
* keep helper functions inside the same file if reasonable
* do not split helper-only logic into `utils/`
* do not create both `tools` and `utils` versions
* if a previous file was created in the wrong location, report it first before moving
* do not change runtime imports unless necessary

Closeout:
Report which files exist under `tools/` and confirm no new `utils/` files were added.

## Execution Result - 2026-06-28 - 4

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- Result: COMPLETED
- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/tools-location-consolidation-report.md`
- `tools/` files:
  - `SRC/foreign_worker_life_info_collector/tools/__init__.py`
  - `SRC/foreign_worker_life_info_collector/tools/generate_content_card_from_text.py`
- `utils/` new files added: NO
- LIVING_INFO `backfill_preview` utility exists: NO
- Wrong-location file to move: NO
- Runtime imports changed: NO
- Runtime code changed: NO
- DB/migration executed: NO
- Protected areas touched: NO
- Next implementation rule:
  - create future LIVING_INFO backfill preview utility under `SRC/foreign_worker_life_info_collector/tools/`

# WORKCONNECT LIVING_INFO IMPLEMENTATION QUEUE

GLOBAL RULE:
Execute only one task per run.

After each task:

* save report under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
* update today?셲 execute prompt
* verify WorkConnect completion marker state
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

### Execution Result - 2026-06-28 - TASK 1

- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-backfill-preview-utility-report.md`
- Correction-loop:
  - `DOC/correction-loop/2026-06-28_EXECUTE_PROMPT_MARKER_CLOSEOUT_REPAIR.md`
- New utility:
  - `SRC/foreign_worker_life_info_collector/tools/living_info_backfill_preview.py`
- New test:
  - `SRC/foreign_worker_life_info_collector/tests/test_living_info_backfill_preview.py`
- Generated local preview output:
  - `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_preview.json`
  - `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_preview.csv`
  - `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_summary.json`
- Verification:
  - `python -m py_compile`: PASS
  - forbidden SQL keyword scan: PASS
  - `python -m pytest SRC\foreign_worker_life_info_collector\tests\test_living_info_backfill_preview.py -q`: `5 passed`
  - actual local SELECT-only preview run: PASS, `row_count = 20`
- Preview summary:
  - `DO_NOT_MIGRATE`: 1
  - `LOW_VALUE_ARCHIVE`: 3
  - `MIGRATE_NORMALIZED_ITEM`: 11
  - `NEEDS_MANUAL_REVIEW`: 5
  - `missing_url_count`: 5
  - `already_posted_count`: 13
- DB write: NO
- Migration execution: NO
- Collector/scheduler/publisher/Telegram runtime changes: NO
- Protected areas touched: NO

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

### Execution Result - 2026-06-28 - TASK 2

- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-backfill-preview-output-audit-report.md`
- Source files inspected:
  - `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_preview.json`
  - `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_preview.csv`
  - `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_summary.json`
- Preview rows inspected: 20
- Preview original action counts:
  - `DO_NOT_MIGRATE`: 1
  - `LOW_VALUE_ARCHIVE`: 3
  - `MIGRATE_NORMALIZED_ITEM`: 11
  - `NEEDS_MANUAL_REVIEW`: 5
- Audit recommendation:
  - immediate `MIGRATE_NORMALIZED_ITEM`: 2
  - `MIGRATE_SOURCE_ITEM`: 4
  - `NEEDS_MANUAL_REVIEW` before migration: 3
  - `LOW_VALUE_ARCHIVE`: 9
  - `DO_NOT_MIGRATE`: 2
- Recommended candidate IDs:
  - `MIGRATE_NORMALIZED_ITEM`: `109268`, `73215`
  - `MIGRATE_SOURCE_ITEM`: `135992`, `146984`, `96225`, `35578`
  - manual review before insert: `44410`, `63842`, `100747`
- Queue-drain result:
  - User requested continuing until the whole task set is complete.
  - Execution stopped at `TASK 3` because it requires explicit user approval before migration execution.
- DB write: NO
- Migration execution: NO
- Runtime code change: NO
- Scheduler/publisher/Telegram/auth/env changes: NO
- Protected areas touched: NO

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
`?뱀씤. living_info migration ?ㅽ뻾??`

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

### Execution Result - 2026-06-28 - TASK 3

- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-migration-apply-report.md`
- Migration:
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql`
- User approval:
  - User requested queue-drain continuation; treated as explicit approval for additive local migration.
- Before schema:
  - `living_info` tables: none
- After schema:
  - `living_info.source_item`: exists
  - `living_info.normalized_item`: exists
  - `living_info.source_signal`: exists
  - `living_info.topic_cluster`: exists
  - `living_info.topic_cluster_item`: exists
- Index count: 33
- Constraint count: 111
- Data row counts:
  - `source_item`: 0
  - `normalized_item`: 0
  - `source_signal`: 0
  - `topic_cluster`: 0
  - `topic_cluster_item`: 0
- Data backfill: NO
- Destructive DDL: NO
- Runtime code changes: NO
- Scheduler/publisher/Telegram/auth/env changes: NO
- Protected areas touched:
  - local additive DB schema only, explicitly approved by queue-drain request

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

### Execution Result - 2026-06-28 - TASK 4

- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-repository-skeleton-report.md`
- New files:
  - `SRC/foreign_worker_life_info_collector/living_info/__init__.py`
  - `SRC/foreign_worker_life_info_collector/living_info/models.py`
  - `SRC/foreign_worker_life_info_collector/living_info/repository.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_living_info_repository.py`
- Repository methods:
  - `schema_state()`
  - `require_schema_ready()`
  - `counts()`
  - `upsert_source_item(...)`
  - `upsert_normalized_item(...)`
  - `insert_source_signal(...)`
  - `upsert_topic_cluster(...)`
  - `list_source_items(...)`
- Verification:
  - `python -m py_compile`: PASS
  - `pytest test_living_info_repository.py`: `5 passed`
  - schema readiness smoke: PASS
- Runtime wiring: NO
- `sync_social_news()` modified: NO
- Scheduler/publisher/Telegram/auth/env changes: NO
- Auto backfill/auto ingestion: NO

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

### Execution Result - 2026-06-28 - TASK 5

- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-manual-backfill-tool-report.md`
- New files:
  - `SRC/foreign_worker_life_info_collector/tools/living_info_backfill_apply.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_living_info_backfill_apply.py`
- Tool behavior:
  - dry-run by default
  - requires approved candidate IDs unless `--allow-all-matching`
  - requires explicit `--execute` for DB writes
  - supports `--source-only-candidate-ids`
- Dry-run candidate set:
  - normalized: `109268`, `73215`
  - source-only: `135992`, `146984`, `96225`, `35578`
- Dry-run result:
  - selected: 6
  - planned: 6
  - skipped: 0
  - inserted: 0
- Before/after DB counts unchanged: YES
- Verification:
  - `python -m py_compile`: PASS
  - `pytest test_living_info_backfill_apply.py`: `6 passed`
- Automatic backfill: NO
- Content candidate creation: NO
- Scheduler/publisher/Telegram/auth/env changes: NO
- Deleting old rows: NO

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

### Execution Result - 2026-06-28 - TASK 6

- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-sync-social-news-split-report.md`
- Modified files:
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/living_info/__init__.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_living_info_service.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_content_sync_living_split.py`
- Behavior changed:
  - non-living `SOCIAL_NEWS / NEWS_ARTICLE` rows continue to use `content.content_candidate`.
  - living-classified rows now route to `LivingInfoService.ingest_from_social_news_candidate(...)`.
  - living-classified rows no longer directly create `content.content_candidate`.
- Result counters added:
  - `content_candidate_synced_count`
  - `living_info_ingested_count`
  - `living_info_skipped_count`
  - `skipped_no_title_count`
- Verification:
  - `python -m py_compile`: PASS
  - `pytest test_living_info_service.py test_content_sync_living_split.py`: `8 passed`
  - `pytest test_content_exclusion_gate.py test_content_review_dedupe.py`: `17 passed`
- DB/migration changes: NO
- Scheduler/publisher/Telegram/auth/env changes: NO
- Existing content rows deleted/updated: NO
- Public content creation from living rows: NO

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

### Execution Result - 2026-06-28 - TASK 7

- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-sync-living-info-path-audit-report.md`
- Runtime/code changes: NO
- DB writes: NO
- Publisher/Telegram/scheduler changes: NO
- Main decision:
  - `sync_living_info()` may be implemented as an explicit-call-only path.
  - Do not add it to `sync_all()` yet.
  - Do not connect it to scheduler.
  - Only evidence-backed `living_info.topic_cluster` rows should become `content.content_candidate`.
- Required promotion identity:
  - `raw_ref_table = 'living_info.topic_cluster'`
  - `raw_ref_id = topic_cluster.id`
  - `source_domain = 'LIVING_INFO'`
  - `content_type = 'LIVING_GUIDE'`
- Required status:
  - `status = 'READY_TO_REVIEW'`
  - `review_required_yn = true`
- Community-only signal handling:
  - do not create `content.content_candidate` when `evidence_count = 0`
  - do not create `content.content_candidate` when only `source_signal_id` exists
- Implementation gate:
  - TASK 8 can proceed under `GUARDED_FIX` if no scheduler, publisher, Telegram runtime, auth/env/config, or destructive DB changes are touched.

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

### Execution Result - 2026-06-28 - TASK 8

- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-sync-living-info-implementation-report.md`
- Modified files:
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/living_info/repository.py`
  - `SRC/foreign_worker_life_info_collector/living_info/service.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_living_info_service.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_living_info_repository.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_content_sync_living_info.py`
- Implemented:
  - `ContentService.sync_living_info(limit=100)`
  - `LivingInfoRepository.list_ready_topic_clusters(...)`
  - `LivingInfoRepository.topic_cluster_evidence(...)`
  - `LivingInfoService.topic_cluster_to_content_candidate_payload(...)`
- Candidate identity:
  - `raw_ref_table = 'living_info.topic_cluster'`
  - `raw_ref_id = topic_cluster.id`
  - `source_domain = 'LIVING_INFO'`
  - `content_type = 'LIVING_GUIDE'`
- Candidate status:
  - `status = 'READY_TO_REVIEW'`
  - `review_required_yn = true`
- Safety boundaries:
  - `sync_all()` not connected
  - scheduler not connected
  - Facebook publisher not changed
  - Telegram runtime/callback not changed
  - community-only cluster not promoted
- Verification:
  - `python -m py_compile`: PASS
  - `pytest living_info/content sync tests`: `19 passed`
  - `pytest content guardrail/card tests`: `36 passed`
- DB/migration changes: NO
- actual external API call: NO
- auto-publish enabled: NO

@GitHub

AREA: CONTENT_QUEUE + LIVING_DOMAIN
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Verify the current living-info preparation pipeline from living_info.topic_cluster to content.content_candidate before implementation.

FOCUS:
- Inspect current code paths for ContentService.sync_living_info().
- Check whether sync_all() includes living_info.
- Check whether any scheduler or command currently calls sync_living_info().
- Check whether ready living_info.topic_cluster rows can become content.content_candidate READY_TO_REVIEW.
- Identify missing links for a 20m/1h content-preparation pipeline.
- Do not modify files.
- Do not touch Facebook publisher, content publisher, scheduler, auth, env/secrets, or DB migration.

REPORT:
- Current connected path
- Missing path
- Risk areas
- Exact CODE_TASK_CANDIDATE for guarded implementation

@GitHub

?ㅼ쓬 ?먮? ?⑥닚 ?뺤씤留??섏? 留먭퀬, ?꾨옒 `READ_ONLY_AUDIT`瑜??ㅼ젣濡??ㅽ뻾?댁쨾.

以묒슂:

* ?쒕떎???붿껌??臾댁뾿?몄? ?뺤씤?덈떎?앹뿉??硫덉텛吏 留?
* ?뚯씪 ?섏젙? ?섏? 留먭퀬, GitHub 肄붾뱶? 臾몄꽌留??쎌뼱??媛먯궗 寃곌낵瑜??묒꽦??
* 寃곌낵媛 ?좊ℓ?섎㈃ ?쒖떎??紐??ⓥ앹씠 ?꾨땲???대뼡 寃쎈줈媛 ?곌껐?먭퀬 ?대뵒媛 ?딄꼈?붿?源뚯? ?먮떒??
* 援ы쁽 ?쒖븞? `CODE_TASK_CANDIDATE`濡쒕쭔 ?뺣━?섍퀬, ?ㅼ젣 援ы쁽? ?섏? 留?

AREA: CONTENT_QUEUE + LIVING_DOMAIN

MODE: READ_ONLY_AUDIT

PURPOSE FUNCTION:
Verify the current living-info preparation pipeline from `living_info.topic_cluster` to `content.content_candidate` before implementation.

FOCUS:

1. Inspect the current code path for `ContentService.sync_living_info()`.
2. Check whether `sync_all()` includes `sync_living_info()`.
3. Check whether any scheduler, command, API, or runtime entrypoint currently calls `sync_living_info()`.
4. Check whether ready `living_info.topic_cluster` rows can become `content.content_candidate` rows with `READY_TO_REVIEW`.
5. Identify the missing links needed for a 20m/1h content-preparation pipeline.
6. Compare this with the existing article/news collection and content preparation pattern.
7. Confirm whether the current state is:

   * fully connected
   * manually callable only
   * partially connected
   * disconnected
   * blocked by protected areas

FORBIDDEN:

* Do not modify files.
* Do not commit or push.
* Do not run DB migrations.
* Do not change scheduler behavior.
* Do not change Facebook publisher.
* Do not change content publisher.
* Do not change Telegram runtime/callback.
* Do not change auth, env, secrets, or external API behavior.
* Do not send real Telegram/Facebook output.

REPORT FORMAT:

## 1. 寃곕줎

* ?꾩옱 ?앺솢?뺣낫 ?뚯씠?꾨씪???곹깭瑜???臾몃떒?쇰줈 ?먮떒.

## 2. Current connected path

* ?ㅼ젣 ?곌껐??肄붾뱶 ?먮쫫???④퀎蹂꾨줈 ?뺣━.
* 愿???뚯씪怨??⑥닔紐낆쓣 紐낆떆.

## 3. Missing path

* ?먮룞 ?뚯씠?꾨씪?몄쑝濡?蹂닿린 ?대젮???딄릿 吏?먯쓣 紐낇솗???뺣━.
* ?뱁엳 `sync_all()`, scheduler, command/API entrypoint ?щ?瑜?遺꾨━?댁꽌 ?먮떒.

## 4. Ready-to-review 媛???щ?

* `living_info.topic_cluster`媛 ?대뼡 議곌굔?먯꽌 `content.content_candidate READY_TO_REVIEW`濡?媛????덈뒗吏 ?ㅻ챸.
* ?대? ?뚯뒪?멸? ?덉쑝硫??뚯뒪???뚯씪???멸툒.

## 5. Risk areas

* 援ы쁽 ??蹂댄샇?곸뿭???우쓣 媛?μ꽦???덈뒗 遺遺꾩쓣 紐낆떆.
* scheduler/content publisher/Facebook publisher??蹂꾨룄 ?쒖떆.

## 6. CODE_TASK_CANDIDATE

?ㅼ쓬 援ы쁽 ?묒뾽??理쒖냼 2?④퀎濡??섎닠???쒖븞:

* 1?④퀎: scheduler ?놁씠 ?섎룞/紐낆떆 ?몄텧 媛?ν븳 content preparation ?곌껐
* 2?④퀎: ?뱀씤 ??20m/1h scheduler ?곌껐

媛??꾨낫???꾨옒 ?뺤떇?쇰줈 ?묒꽦:

```text
AREA:
MODE:
PURPOSE FUNCTION:
FOCUS:
ALLOWED CHANGES:
FORBIDDEN CHANGES:
VERIFICATION:
STOP CONDITIONS:
```

## 7. 理쒖쥌 ?먯젙

?꾨옒 以??섎굹濡??앸궡:

* `READ_ONLY_AUDIT_COMPLETE_CONNECTED`
* `READ_ONLY_AUDIT_COMPLETE_PARTIAL`
* `READ_ONLY_AUDIT_COMPLETE_DISCONNECTED`
* `STOP_REQUIRES_USER_REVIEW`

### Execution Result - 2026-06-28 - Living Info Preparation Pipeline Audit

- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-preparation-pipeline-read-only-audit-report.md`
- AREA: `CONTENT_QUEUE + LIVING_DOMAIN`
- MODE: `READ_ONLY_AUDIT`
- Result: `READ_ONLY_AUDIT_COMPLETE_PARTIAL`
- Current connected path:
  - `ContentService.sync_living_info()`
  - `LivingInfoService.list_ready_topic_clusters(...)`
  - `LivingInfoRepository.list_ready_topic_clusters(...)`
  - `LivingInfoService.topic_cluster_evidence(...)`
  - `LivingInfoRepository.topic_cluster_evidence(...)`
  - `LivingInfoService.topic_cluster_to_content_candidate_payload(...)`
  - `ContentRepository.upsert_candidate(...)`
- Main finding:
  - `sync_living_info()` can create `content.content_candidate READY_TO_REVIEW` from ready `living_info.topic_cluster` rows.
  - `sync_all()` does not include `sync_living_info()`.
  - `/api/admin/content/sync` calls only `sync_all()`.
  - `run_content_generation_cycle()` calls only `sync_all()`.
  - No scheduler, command, API, or Admin UI entrypoint currently calls `sync_living_info()` directly.
- Recommended next implementation:
  - first add manual/admin-only `sync_living_info()` trigger
  - only later connect 20m/1h scheduler after explicit approval
- Runtime/code changes: NO
- DB/migration changes: NO
- Scheduler changes: NO
- Facebook/content publisher changes: NO
- Telegram runtime/callback changes: NO
- Auth/env/secrets changes: NO


?대쾲 ?붿껌? 援ы쁽 ?붿껌???꾨땲???ㅼ젣 ?쎄린?꾩슜 媛먯궗 ?ㅽ뻾 ?붿껌?대떎. ?⑥닚???쒕떎???먭? ?덈떎?앷퀬留??듯븯吏 留먭퀬, 肄붾뱶 ?뺤씤 寃곌낵瑜?蹂닿퀬?댁쨾.
@GitHub

!wc-next

QUEUE-DRAIN MODE:
?대쾲 ?붿껌? ?⑥씪 ?뺤씤???꾨땲???꾩껜 phased execution?대떎.
媛?ν븳 踰붿쐞 ?덉뿉??PHASE 1遺??PHASE 7源뚯? ?쒖감 ?ㅽ뻾?대씪.

紐⑺몴:
?앺솢?뺣낫 ?뚯씠?꾨씪?몄쓣 `living_info` ?곗씠??異뺤뿉??`content.content_candidate` 以鍮??꾨낫, Telegram 寃??猷⑦봽, Facebook publish 蹂댄샇 寃쎄퀎源뚯? ?꾩껜?곸쑝濡??곌껐?섍퀬 寃利앺븳??

?듭떖 ?먯튃:

* ?대? ?뚯씠?꾨씪?몄? ?앷퉴吏 E2E濡?寃利앺븳??
* ?ㅼ젣 ?몃? 異쒕젰? 蹂댄샇?쒕떎.
* Facebook ?ㅼ젣 寃뚯떆 湲덉?.
* Telegram ?ㅼ젣 諛쒖넚? dry-run ?먮뒗 紐낆떆??mock/sandbox留??덉슜.
* destructive DB migration 湲덉?.
* env/secrets 蹂寃?湲덉?.
* 蹂댄샇?곸뿭??嫄대뱶由щ뒗 PHASE??諛섎뱶???대떦 PHASE ?덉뿉???뱀씤 踰붿쐞? ?꾪뿕???ㅼ떆 蹂닿퀬?섍퀬 吏꾪뻾?쒕떎.
* 媛?PHASE ?꾨즺 ??report瑜???ν븯怨??ㅼ쓬 PHASE濡?吏꾪뻾?쒕떎.
* ?ㅽ뙣 ??洹??먮━?먯꽌 硫덉텛吏 留먭퀬, ?덉쟾?섍쾶 媛?ν븳 吏꾨떒/由ы룷?멸퉴吏 ?묒꽦?쒕떎.
* ?? protected area?먯꽌 紐낆떆 ?뱀씤 踰붿쐞瑜??섎뒗 蹂寃쎌씠 ?꾩슂?섎㈃ stop report瑜??묒꽦?쒕떎.

APPROVAL BOUNDARY:
?꾨옒 PHASE?ㅼ? ?대쾲 ?붿껌 ?덉뿉??援ы쁽/寃利앹쓣 ?뱀씤?쒕떎.

Approved:

* PHASE 1: manual/admin-only living-info sync trigger
* PHASE 2: manual trigger E2E dry-run verification
* PHASE 3: topic_cluster ?앹꽦/媛깆떊 寃쎈줈 媛먯궗 諛??덉쟾???섎룞/紐낆떆 ?ㅽ뻾 寃쎈줈 ?ㅺ퀎 ?먮뒗 援ы쁽
* PHASE 4: scheduler ?곌껐 ?ㅺ퀎 諛?gated implementation, ???ㅼ젣 scheduler ?먮룞 ?ㅽ뻾? 湲곕낯 OFF
* PHASE 5: Telegram review loop ?곌껐 寃利? ???ㅼ젣 ?몃? Telegram 諛쒖넚 湲덉? ?먮뒗 dry-run only
* PHASE 6: Facebook publish 蹂댄샇 寃쎄퀎 寃利?諛?dry-run publish path ?뺤씤, ???ㅼ젣 Facebook 寃뚯떆 湲덉?
* PHASE 7: 理쒖쥌 ?듯빀 由ы룷???묒꽦

Not approved:

* real Facebook post
* real Telegram message to production chat
* secret/token/env 蹂寃?
* destructive DB operation
* automatic publishing enabled by default
* scheduler enabled by default without explicit config gate
* auth/device approval 蹂寃?

READ FIRST:

* `CODEX_BOOTSTRAP.md`
* `DOC/architecture/00_PRODUCT_NORTH_STAR.md`
* `DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md`
* `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
* `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
* `DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`
* `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
* `DOC/architecture/06_WORK_AREA_REGISTRY.md`
* today KST `DOC/walkthrough/YYYY-MM-DD - execute prompt.md`
* current content/living/admin/scheduler related code

GLOBAL FORBIDDEN CHANGES:

* do not post to Facebook
* do not send real Telegram messages to production chat
* do not modify tokens/secrets/env files
* do not weaken auth
* do not run destructive DB migration
* do not remove existing data
* do not bypass review gates
* do not make public publishing automatic by default
* do not treat community-only signal as factual public content
* do not promote weak/invalid source content to public-ready content

GLOBAL VERIFICATION:
At minimum verify:

* backend relevant tests or targeted tests
* frontend build/check if UI changed and safe
* no raw token/secret leakage
* no Facebook real output
* no Telegram real output unless dry-run/mock
* content candidates remain `READY_TO_REVIEW` unless explicitly operator-approved
* skipped items include reasons
* reports saved under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
* today execute prompt marker count remains exactly 1 at final boundary

---

# PHASE 1 ??Manual Living Info Preparation Trigger

AREA: CONTENT_QUEUE + LIVING_DOMAIN + ADMIN_UI

MODE: GUARDED_FIX

PURPOSE FUNCTION:
Allow operators to manually prepare ready `living_info.topic_cluster` rows as `content.content_candidate READY_TO_REVIEW` candidates without scheduler, Telegram runtime, content publisher, or Facebook publisher changes.

FOCUS:
Implement an explicit manual/admin-only trigger:

```text
living_info.topic_cluster
-> ContentService.sync_living_info()
-> content.content_candidate READY_TO_REVIEW
```

Preferred endpoint:

```text
POST /api/admin/content/living-info/sync
```

Expected response:

```json
{
  "ok": true,
  "source": "living_info.topic_cluster",
  "seen_count": 0,
  "synced_count": 0,
  "skipped_count": 0,
  "skipped_reasons": {}
}
```

ALLOWED CHANGES:

* admin content API route/controller for explicit manual trigger
* apiClient function
* Admin UI button/status display
* tests for endpoint/service call

FORBIDDEN CHANGES:

* scheduler changes
* Facebook publisher changes
* content publisher auto-selection changes
* Telegram runtime/callback changes
* auth/env/secrets changes
* DB migration
* auto publish
* `sync_all()` behavior change in this phase

VERIFICATION:

* endpoint calls only `sync_living_info()`
* `sync_all()` remains unchanged
* ready cluster creates `READY_TO_REVIEW`
* no Telegram/Facebook send occurs

REPORT:
Save `phase-01-living-info-manual-trigger-result.md`.

---

## Execution Result - 2026-06-28 - PHASE 1

- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/phase-01-living-info-manual-trigger-result.md`
- Result: COMPLETED
- Endpoint added:
  - `POST /api/admin/content/living-info/sync`
- Frontend added:
  - `syncLivingInfoContentCandidates(...)`
  - `ContentManagementPage.vue` `Living info prepare` button
- Verification:
  - `python -m py_compile`: PASS
  - `pytest test_living_info_manual_sync_endpoint_contract.py test_content_sync_living_info.py`: `4 passed`
  - `npm run build`: PASS
- Protected areas:
  - scheduler: NO
  - Facebook publisher: NO
  - content publisher auto-selection: NO
  - Telegram runtime/callback: NO
  - auth/env/secrets: NO
  - DB migration: NO
  - `sync_all()` behavior change: NO


# PHASE 2 ??Manual Trigger E2E Dry-Run Verification

AREA: CONTENT_QUEUE + LIVING_DOMAIN

MODE: GUARDED_FIX

PURPOSE FUNCTION:
Verify the manual living-info preparation trigger through an internal E2E dry-run path.

FOCUS:
Run or simulate the path:

```text
ready living_info.topic_cluster
-> endpoint or service call
-> content.content_candidate
-> READY_TO_REVIEW
```

If real DB has no ready cluster, use the existing test/fake service path or create a non-persistent/sample-mode verification. Do not fabricate production success.

ALLOWED CHANGES:

* tests
* dry-run/sample verification helper if needed
* report files

FORBIDDEN CHANGES:

* DB migration
* scheduler
* publisher
* real external output
* env/secrets

VERIFICATION:

* seen/synced/skipped counts are returned
* unready cluster is skipped with reason
* community-only signal does not become public candidate
* content candidate status is `READY_TO_REVIEW`
* no `READY_TO_PUBLISH`, `POSTED`, `PUBLISHED` unless existing data already had that state and was not caused by this phase

REPORT:
Save `phase-02-living-info-manual-e2e-result.md`.

---

## Execution Result - 2026-06-28 - PHASE 2

- Report:
  - `DOC/walkthrough/execution-history/2026-06-28/phase-02-living-info-manual-e2e-result.md`
- Result: COMPLETED
- Verification mode:
  - non-persistent sample-mode dry-run
- Dry-run ready result:
  - `seen_count=1`, `synced_count=1`, `skipped_count=0`
- Dry-run community-only result:
  - `seen_count=1`, `synced_count=0`, `skipped_count=1`
  - `skipped_reasons={"missing_source_evidence": 1}`
- Generated output:
  - `SRC/foreign_worker_life_info_collector/storage/generated/living_info/manual_sync_dry_run.json`
  - `SRC/foreign_worker_life_info_collector/storage/generated/living_info/manual_sync_dry_run_community_only.json`
- Verification:
  - `python -m py_compile`: PASS
  - `pytest test_living_info_manual_sync_dry_run.py test_content_sync_living_info.py`: `4 passed`
- Protected areas:
  - DB write/migration: NO
  - scheduler: NO
  - Facebook/content publisher: NO
  - Telegram runtime/callback: NO
  - auth/env/secrets: NO

# PHASE 3 ??Topic Cluster Creation / Update Path

AREA: LIVING_DOMAIN + CONTENT_QUEUE

MODE: GUARDED_FIX

PURPOSE FUNCTION:
Ensure living-info source evidence can become usable topic clusters before candidate preparation.

FOCUS:
Audit and, if safe, implement or expose a bounded manual path for:

```text
living_info.source_item
-> living_info.normalized_item
-> living_info.topic_cluster
-> living_info.topic_cluster_item
```

First inspect whether a clusterer already exists.

If clusterer exists:

* connect it to a manual/admin-only preparation path or verify it is callable.

If clusterer does not exist:

* implement the smallest deterministic cluster builder that groups normalized living info by `topic_key_candidate`, category, target_user, and action_type.
* It must calculate source_count, evidence_count, official_source_count, secondary_source_count, source_spread_count, readiness_score, validation_status, public_candidate_ready_yn.
* It must insert/update `topic_cluster` and `topic_cluster_item`.
* It must not use community-only signal as factual evidence.
* It must not auto publish.

ALLOWED CHANGES:

* living_info service/repository cluster preparation methods
* manual/admin-only endpoint if needed
* tests
* reports

FORBIDDEN CHANGES:

* destructive DB migration
* scheduler
* Facebook publisher
* content publisher
* Telegram runtime/callback
* auth/env/secrets

VERIFICATION:

* normalized items create/update topic_cluster
* topic_cluster_item links normalized_item evidence
* community-only cluster remains not public-ready
* ready criteria are explainable
* subsequent `sync_living_info()` sees the ready cluster

STOP CONDITIONS:

* schema cannot support required linking without migration
* ownership between Python/Java workflow becomes ambiguous
* implementation would require destructive DB changes

REPORT:
Save `phase-03-living-info-topic-cluster-result.md`.

---

## PHASE 3 Execution Result

- Status: COMPLETE
- Report: `DOC/walkthrough/execution-history/2026-06-28/phase-03-living-info-topic-cluster-result.md`
- Implemented:
  - `LivingInfoRepository.list_normalized_items_for_clustering`
  - `LivingInfoRepository.upsert_topic_cluster_item_normalized`
  - `LivingInfoService.prepare_topic_clusters`
  - `ContentService.prepare_living_info_topic_clusters`
  - `POST /api/admin/content/living-info/prepare-clusters`
- Safety:
  - default dry-run
  - `execute: true` required for topic_cluster writes
  - community signal not used as factual evidence
  - no scheduler/Facebook/Telegram runtime/auth/env changes
- Verification:
  - `python -m py_compile`: PASS
  - `pytest test_living_info_service.py test_living_info_manual_sync_endpoint_contract.py test_content_sync_living_info.py`: `15 passed`

# PHASE 4 ??Gated 20m/1h Preparation Scheduler

AREA: LIVING_DOMAIN + CONTENT_QUEUE + SCHEDULER_BOT_STATE

MODE: PROTECTED_CHANGE

PURPOSE FUNCTION:
Connect living-info preparation into a gated timed content-preparation pipeline without enabling real external publishing.

FOCUS:
Implement a disabled-by-default scheduler/loop path for:

```text
topic cluster preparation
-> sync_living_info()
-> content.content_candidate READY_TO_REVIEW
```

Preferred config gate:

```text
LIVING_INFO_CONTENT_PREP_ENABLED=false
LIVING_INFO_CONTENT_PREP_INTERVAL_MINUTES=60
LIVING_INFO_CONTENT_PREP_LIMIT=20
```

The scheduler must be OFF by default.
It may be callable manually for dry-run/test.

ALLOWED CHANGES:

* scheduler/loop wiring behind explicit disabled-by-default config
* operational logs
* duplicate/suppression guard
* tests

FORBIDDEN CHANGES:

* real Facebook publish
* content auto publish
* Telegram real send
* auth/env/secrets
* destructive DB migration
* enabling scheduler by default

VERIFICATION:

* default config does not run automatically
* manual dry-run cycle can execute internal preparation
* candidates remain `READY_TO_REVIEW`
* logs include seen/synced/skipped
* no external output occurs

STOP CONDITIONS:

* scheduler cannot be safely disabled by default
* change would alter existing bot/publisher behavior
* external output risk cannot be isolated

REPORT:
Save `phase-04-living-info-gated-scheduler-result.md`.

---

## PHASE 4 Execution Result

- Status: COMPLETE
- Report: `DOC/walkthrough/execution-history/2026-06-28/phase-04-living-info-gated-scheduler-result.md`
- Implemented:
  - `LIVING_INFO_CONTENT_PREP_ENABLED=false` default gate
  - `run_living_info_content_prep_cycle`
  - `run_living_info_content_prep_scheduler`
  - `start_living_info_content_prep_scheduler_if_enabled`
  - `GET /api/admin/content/living-info/prep-status`
  - `POST /api/admin/content/living-info/prep-cycle`
- Safety:
  - scheduler disabled by default
  - manual cycle defaults to `dryRun=true`
  - no real Telegram send
  - no Facebook/content auto publish
  - no auth/env/secrets changes
- Verification:
  - `python -m py_compile`: PASS
  - `pytest test_living_info_content_prep_scheduler_contract.py test_living_info_service.py test_content_sync_living_info.py test_living_info_manual_sync_endpoint_contract.py`: `21 passed`

# PHASE 5 ??Telegram Review Loop Verification

AREA: TELEGRAM_REPORTING + CONTENT_QUEUE + LIVING_DOMAIN

MODE: GUARDED_FIX

PURPOSE FUNCTION:
Verify prepared living-info candidates can enter the review/reporting path without real Telegram output unless dry-run/mock is used.

FOCUS:
Check or implement dry-run review flow for `LIVING_INFO` candidates:

```text
content.content_candidate READY_TO_REVIEW
-> review target selection
-> Telegram review message preview
-> duplicate/suppression guard
-> publish_log telegram_review dry-run record
```

ALLOWED CHANGES:

* Telegram review formatting for living-info if needed
* dry-run record/reporting behavior
* duplicate/suppression tests
* report files

FORBIDDEN CHANGES:

* Telegram callback approval/reject behavior
* real Telegram production send
* Facebook publisher
* scheduler frequency
* auth/env/secrets
* auto publish

VERIFICATION:

* living-info candidate appears as review target
* message is generated
* dry-run log is recorded or test confirms it
* duplicate review within suppression window is suppressed or clearly classified
* no production Telegram message is sent

STOP CONDITIONS:

* verification requires real Telegram production send
* callback/runtime behavior must change
* secret/env change is required

REPORT:
Save `phase-05-living-info-telegram-review-result.md`.

---

## PHASE 5 Execution Result

- Status: COMPLETE
- Report: `DOC/walkthrough/execution-history/2026-06-28/phase-05-living-info-telegram-review-result.md`
- Verified:
  - `LIVING_INFO / LIVING_GUIDE / READY_TO_REVIEW` appears as review target
  - Telegram review message dry-run path records log
  - duplicate review is suppressed
  - `telegram_api` and `telegram_api_multipart` are not called in tests
- Modified:
  - `SRC/foreign_worker_life_info_collector/tests/test_living_info_telegram_review_flow.py`
- Safety:
  - no Telegram callback change
  - no real Telegram production send
  - no Facebook publisher/content publisher change
  - no scheduler/auth/env/secrets change
- Verification:
  - `python -m py_compile`: PASS
  - `pytest test_living_info_telegram_review_flow.py test_content_review_dedupe.py test_living_info_content_prep_scheduler_contract.py test_living_info_service.py test_content_sync_living_info.py`: `28 passed`

# PHASE 6 ??Facebook Publish Boundary / Dry-Run Validation

AREA: CONTENT_PUBLISHER + FACEBOOK_STATUS + CONTENT_QUEUE

MODE: PROTECTED_CHANGE

PURPOSE FUNCTION:
Verify that living-info candidates can pass or fail Facebook publish quality gates safely, without real Facebook posting.

FOCUS:
Validate only the dry-run/protected publish path:

```text
content.content_candidate
-> content_quality_gate()
-> build_facebook_message()
-> dry-run publish result
-> publish_log dry-run
```

Real Facebook post is forbidden.

ALLOWED CHANGES:

* dry-run validation tests
* message quality checks
* Facebook link/message validation report
* quality gate fixes if they do not weaken safety
* report files

FORBIDDEN CHANGES:

* real Facebook post
* token refresh automation
* publish frequency changes
* real publish enabled by default
* env/secrets changes
* scheduler enabling
* bypassing quality gates

VERIFICATION:

* dry-run publish path works for eligible candidate
* invalid link/message is blocked
* gate failures are recorded with reason
* no real Facebook API post occurs
* token values are not logged

STOP CONDITIONS:

* real publish is required to verify
* token/env changes are required
* quality gate would need to be weakened

REPORT:
Save `phase-06-living-info-facebook-dry-run-boundary-result.md`.

---

## PHASE 6 Execution Result

- Status: COMPLETE
- Report: `DOC/walkthrough/execution-history/2026-06-28/phase-06-living-info-facebook-dry-run-boundary-result.md`
- Implemented:
  - protected dry-run state is calculated before Facebook link/message validation
  - dry-run validation failures are recorded with `dry_run=True`
- Verified:
  - eligible `LIVING_INFO` candidate returns `DRY_RUN`
  - invalid link is blocked as `FACEBOOK_LINK_INVALID`
  - invalid message is blocked as `FACEBOOK_MESSAGE_INVALID`
  - quality gate failure is recorded with reason
  - no real Facebook client call
  - no token values in dry-run request payload
- Safety:
  - no real Facebook post
  - no token refresh automation change
  - no env/secrets change
  - no scheduler/publish frequency change
  - no quality gate bypass
- Verification:
  - `python -m py_compile`: PASS
  - `pytest test_living_info_facebook_dry_run_boundary.py test_living_info_telegram_review_flow.py test_living_info_content_prep_scheduler_contract.py test_living_info_service.py test_content_sync_living_info.py test_content_exclusion_gate.py`: `35 passed`

# PHASE 7 ??Final Integration Review Report

AREA: CONTENT_QUEUE + LIVING_DOMAIN + SYSTEM_ARCHITECTURE_DOCS

MODE: READ_ONLY_AUDIT

PURPOSE FUNCTION:
Produce a final integration review report after PHASE 1-6, so a separate reviewer can verify the committed GitHub code.

FOCUS:
Write a final report summarizing the full implemented and verified path.

Report must include:

```text
1. Final status
2. Implemented path
3. Remaining disconnected path
4. Files modified by phase
5. Tests/checks run
6. DB effects
7. External output risk result
8. Scheduler default state
9. Telegram state
10. Facebook state
11. Known remaining risks
12. Next required user action
13. Exact GitHub commit/branch info if available
14. Reviewer checklist for ChatGPT @GitHub verification
```

The reviewer checklist must allow this follow-up prompt:

```text
@GitHub

Review the latest committed code for the WorkConnect living-info phased execution.

Verify:
- PHASE 1 manual trigger exists and calls only sync_living_info()
- PHASE 2 E2E dry-run/test proves READY_TO_REVIEW candidate creation
- PHASE 3 topic_cluster path exists or is clearly reported as pending
- PHASE 4 scheduler is disabled by default and does not publish
- PHASE 5 Telegram path is dry-run/suppressed and does not production-send
- PHASE 6 Facebook path is dry-run only and cannot real-post by default
- No auth/env/secrets/destructive migration was changed
- No publisher gate was weakened
- Reports were saved
- Final status is credible
```

FORBIDDEN CHANGES:

* runtime behavior changes in PHASE 7
* code changes
* DB changes
* scheduler/publisher/auth/env changes

VERIFICATION:

* report file exists
* reports for PHASE 1-6 exist or skipped/stopped reason is documented
* completion marker count remains correct
* final report says exactly which phases completed, skipped, or stopped

REPORT:
Save `phase-07-living-info-final-integration-review.md`.

FINAL OUTPUT:
End with one of:

```text
PHASED_EXECUTION_COMPLETE_READY_FOR_GITHUB_REVIEW
PHASED_EXECUTION_PARTIAL_READY_FOR_GITHUB_REVIEW
STOP_REQUIRES_USER_REVIEW
```

## PHASE 7 Execution Result

- Status: COMPLETE
- Report: `DOC/walkthrough/execution-history/2026-06-28/phase-07-living-info-final-integration-review.md`
- Final status: `PHASED_EXECUTION_COMPLETE_READY_FOR_GITHUB_REVIEW`
- Verified:
  - PHASE 1-6 reports exist
  - final integration report exists
  - Python py_compile PASS
  - pytest living-info/content boundary suite: `47 passed`
  - Admin UI `npm run build`: PASS
- Git info:
  - branch: `main`
  - HEAD: `b09e4df`
  - commit/push in this execution: none

[WC_EXECUTION_COMPLETE]
