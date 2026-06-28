# READ_ONLY_AUDIT REPORT: LIVING_INFO Server Integration and Social News Split Design

## 1. Pre-Review

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY + CONTENT_QUEUE + SOCIAL_NEWS_CANDIDATE + SYSTEM_ARCHITECTURE_DOCS`
- MODE: `READ_ONLY_AUDIT`
- Risk: MEDIUM
- Protected areas touched: NO
- Files inspected:
  - `CODEX_BOOTSTRAP.md`
  - `DOC/architecture/00_PRODUCT_NORTH_STAR.md`
  - `DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md`
  - `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
  - `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
  - `DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`
  - `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  - `DOC/database/01_CURRENT_DB_MAP.md`
  - `DOC/database/02_SOCIAL_NEWS_CURRENT.md`
  - `DOC/database/03_CONTENT_CURRENT.md`
  - `DOC/database/06_DOMAIN_DATA_CURRENT.md`
  - `DOC/database/TO_BE_DB_ARCHITECTURE.md`
  - `DOC/walkthrough/2026-06-28 - execute prompt.md`
  - `DOC/walkthrough/execution-history/2026-06-28/living-info-physical-schema-design-report.md`
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/content/repository.py`
  - `SRC/foreign_worker_life_info_collector/social/news/pipeline.py`
  - `SRC/foreign_worker_life_info_collector/social/news/category_rotation.py`
  - `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py`
  - `SRC/foreign_worker_life_info_collector/storage/db/postgres.py`
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/admin_postgres_schema.sql`
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_06_immigration_info.sql`
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_07_content_candidate.sql`
- DB read-only queries run: YES
  - `information_schema.tables` count for `living_info`
  - `content.content_candidate` counts for current `LIVING_INFO`
- Runtime/code changes: NO

DB read-only result:

```text
living_info_table_count=0
living_ref=LIVING_INFO social_news.candidate 54
```

## 2. Current Code Path

Current content sync entry point:

```text
ContentService.sync_all()
-> ContentService.sync_social_news()
-> ContentService.sync_immigration()
```

Admin API entry point:

```text
POST /api/admin/content/sync
-> content_service().sync_all(limit=...)
```

Current social news sync flow:

```text
ContentService.sync_social_news()
-> SELECT representative rows from social_news.candidate
-> social_news_payload(row)
-> ContentRepository.upsert_candidate(payload)
-> content.content_candidate
```

The current SQL in `sync_social_news()` filters:

```sql
WHERE COALESCE(is_representative, TRUE) = TRUE
  AND COALESCE(publish_status, status, '') NOT IN (
      'ARCHIVED', 'DUPLICATE_SKIPPED', 'DUPLICATE', 'SKIPPED', 'TEXT_INVALID'
  )
```

The current `LIVING_INFO` assignment happens in `social_news_payload(row)`:

```python
living = is_living_content(content_category or category or "", content_priority_group or "")
payload = {
    "source_domain": "LIVING_INFO" if living else "SOCIAL_NEWS",
    "content_type": "LIVING_GUIDE" if living else "NEWS_ARTICLE",
    "raw_ref_table": "social_news.candidate",
    "raw_ref_id": row_id,
}
```

Current `is_living_content()` includes:

```text
housing
banking
healthcare
transportation
insurance
korean_language
cost_of_living
local_community
education
settlement_life
travel
lifestyle
culture
local_events
safety
SECONDARY
TERTIARY
```

Current content uniqueness is:

```sql
CONSTRAINT ux_content_candidate_raw_ref UNIQUE(raw_ref_table, raw_ref_id)
```

Implication:

- A `social_news.candidate` row can become exactly one `content.content_candidate` row.
- If the row is later reclassified, `upsert_candidate()` updates the existing content row because the conflict key is still `raw_ref_table='social_news.candidate'`, `raw_ref_id=<id>`.
- Future `living_info.topic_cluster` content candidates cannot use the same raw reference identity. They need a new `raw_ref_table`.

## 3. Target Architecture

Target path:

```text
social_news.candidate
-> living_info.source_item
-> living_info.normalized_item
-> living_info.topic_cluster_item
-> living_info.topic_cluster
-> content.content_candidate
-> content.publish_log
```

Community/trend path:

```text
community/trend/discovery source
-> living_info.source_signal
-> living_info.topic_cluster_item
-> living_info.topic_cluster
```

Rules:

- `social_news.candidate` remains source/news candidate storage.
- `living_info.source_item` stores source-backed evidence for living-domain input.
- `living_info.source_signal` stores community/trend demand signals only.
- `living_info.topic_cluster` is the first living-domain object that can become a content candidate.
- `content.content_candidate` remains final review/publish owner.
- `living_info.source_item` must not publish directly.
- Community/trend signals must not directly create `content.content_candidate`.

Recommended future content references:

```text
raw_ref_table = 'living_info.topic_cluster'
raw_ref_id = living_info.topic_cluster.id
source_domain = 'LIVING_INFO'
content_type = 'LIVING_GUIDE'
```

For single official utility pages:

```text
raw_ref_table = 'living_info.normalized_item'
raw_ref_id = living_info.normalized_item.id
source_domain = 'LIVING_INFO'
content_type = 'LIVING_GUIDE'
```

## 4. Proposed Server Module Design

Recommended package:

```text
SRC/foreign_worker_life_info_collector/living_info/
```

Recommended first files:

```text
living_info/__init__.py
living_info/models.py
living_info/repository.py
living_info/normalizer.py
living_info/service.py
living_info/topic_clusterer.py
living_info/backfill_preview.py
```

### `living_info.models`

Purpose:

- Define lightweight dataclasses or typed payload structures.
- Keep DB enum/status strings centralized.

Suggested model names:

```text
LivingSourceItem
LivingNormalizedItem
LivingSourceSignal
LivingTopicCluster
LivingTopicClusterItem
LivingBackfillPreviewRow
```

### `living_info.repository`

Purpose:

- Own `living_info.*` DB access.
- Use `storage.db.postgres.connect()` directly, consistent with `ContentRepository`.
- Keep read and write methods separate.

First read methods:

```text
schema_exists()
find_source_item_by_duplicate_key(duplicate_key)
find_source_item_by_raw_ref(raw_ref_table, raw_ref_id)
list_cluster_candidates(limit)
list_backfill_preview_rows(limit)
```

First write methods after migration approval:

```text
upsert_source_item_from_social_news(row)
upsert_normalized_item(source_item_id, normalization_payload)
upsert_source_signal(signal_payload)
upsert_topic_cluster(cluster_payload)
attach_normalized_item_to_cluster(topic_cluster_id, normalized_item_id, item_role)
attach_source_signal_to_cluster(topic_cluster_id, source_signal_id, item_role)
```

### `living_info.normalizer`

Purpose:

- Convert `social_news.candidate` or official/support source rows into normalized living-domain categories.
- Keep classification separate from content message formatting.

Suggested functions:

```text
normalize_social_news_living_candidate(row) -> dict
normalize_source_usage(...)
normalize_primary_category(...)
build_topic_key_candidate(...)
build_duplicate_key(...)
```

### `living_info.topic_clusterer`

Purpose:

- Build or update topic clusters from normalized living-domain items and source signals.
- Do not create content candidates directly in first version.

Suggested functions:

```text
cluster_key(normalized_item)
candidate_cluster_payload(normalized_item)
compute_readiness_score(cluster)
is_public_candidate_ready(cluster)
```

### `living_info.service`

Purpose:

- Orchestrate repository + normalizer + clusterer.
- Provide explicit methods for current transition stages.

Suggested methods:

```text
ingest_from_social_news_candidate(row, dry_run=False)
ingest_existing_content_candidate(candidate_row, dry_run=True)
preview_backfill_from_content_candidates(limit=500)
sync_topic_clusters(limit=200)
list_ready_topic_clusters(limit=50)
```

### `living_info.backfill_preview`

Purpose:

- CLI/dev-only read-only preview.
- Output JSON/CSV.
- No inserts/updates.

Suggested CLI:

```text
python -m foreign_worker_life_info_collector.living_info.backfill_preview --limit 500 --output storage/generated/living_info/backfill_preview.json
```

## 5. DB Connection and Transaction Design

Use existing helper:

```python
from ..storage.db.postgres import connect
```

Connection rule:

- Reuse `connect()` in `LivingInfoRepository`.
- Do not create a separate connection utility.
- Keep each upsert operation in one explicit transaction.
- For multi-step ingestion:

```text
source_item upsert
-> normalized_item upsert
-> cluster upsert
-> cluster_item attach
-> commit
```

Transaction boundaries:

- `ingest_from_social_news_candidate()` should be atomic for source/normalized/cluster attach.
- `sync_living_info()` should not share a transaction with Facebook/Telegram/publisher work.
- `ContentRepository.upsert_candidate()` should stay responsible only for `content.content_candidate`.

Read/write separation:

- Preview utilities must call only read methods.
- Write methods should be impossible to call from dry-run preview unless explicitly enabled.
- Add a `dry_run` or separate class/module only if implementation later needs it.

Schema readiness:

- `LivingInfoRepository` should not auto-run migrations.
- It may expose:

```text
schema_ready() -> bool
```

If schema is missing, service should return a structured status such as:

```text
{"ok": false, "reason": "LIVING_INFO_SCHEMA_MISSING"}
```

Do not silently fall back to writing `LIVING_INFO` rows to `content.content_candidate`.

## 6. Migration Process Design

Migration file should be a new additive PostgreSQL file:

```text
SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql
```

If created later on a different date, use that actual date.

Migration should include:

- `CREATE SCHEMA IF NOT EXISTS living_info`
- table creation:
  - `living_info.source_item`
  - `living_info.normalized_item`
  - `living_info.source_signal`
  - `living_info.topic_cluster`
  - `living_info.topic_cluster_item`
- indexes
- FK constraints
- conservative check constraints only where stable

Recommended constraint strategy:

- Use `CHECK` for stable `active_yn` values:

```text
active_yn IN ('Y', 'N')
```

- Use `VARCHAR` initially for category/status/usage values instead of heavy enum-like `CHECK` constraints.

Reason:

- Category and usage values are still evolving.
- Over-strict `CHECK` constraints can block future source discovery and backfill preview.

Verification SQL:

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

Rollback plan:

- First migration is additive.
- Rollback in local/dev can be `DROP SCHEMA living_info CASCADE` only if no production data exists and user explicitly approves.
- Safer rollback for shared/prod-like data:

```text
disable write path
archive generated preview files
stop using living_info schema
leave tables in place
```

No destructive rollback should be automated.

## 7. Social News Split Strategy

Recommended safer first implementation:

```text
ContentService.sync_social_news()
-> if not living:
      existing social news -> content.content_candidate path
   if living:
      LivingInfoService.ingest_from_social_news_candidate(row)
      do not immediately create content.content_candidate
```

Reason this is safer than modifying `SocialNewsPipeline` first:

- `sync_social_news()` is already the boundary where social/news candidates become content candidates.
- Splitting there preserves existing collection, normalization, scoring, duplicate, and representative logic.
- It avoids touching collector/scheduler behavior.
- It isolates the first runtime change to content sync responsibility.

What should remain unchanged:

- `social_news.raw_item`
- `social_news.normalized_item`
- `social_news.candidate`
- social news duplicate/representative logic
- collector execution
- scheduler
- publisher

What should change later:

- `sync_social_news()` should skip `ContentRepository.upsert_candidate()` for living rows after successfully ingesting them into `living_info`.
- Non-living rows should continue current `SOCIAL_NEWS / NEWS_ARTICLE` content sync.

Handling broad living categories:

```text
travel
culture
local_events
lifestyle
broad safety
```

These should not automatically become active `living_info.topic_cluster` content material.

Recommended mapping:

- `travel`: usually `LOW_VALUE_NOISE` or `TREND_SIGNAL`; block unless practical settlement action exists.
- `culture`: usually `LOW_VALUE_NOISE` or `COMMUNITY_SIGNAL`; block unless public-service/language/community integration value exists.
- `local_events`: `TEXT_REVIEW_ONLY` or `SOURCE_EVIDENCE`; only promote if foreign resident support program.
- `lifestyle`: `TREND_SIGNAL`; not content candidate without validation.
- broad `safety`: only promote if actionable safety/scam/emergency information for foreign residents.

Duplicate/injection prevention:

- `living_info.source_item` should use:

```text
duplicate_key = hash(canonical_url or source_url or raw_ref_table/raw_ref_id)
```

- Preserve original source reference:

```text
raw_ref_table = 'social_news.candidate'
raw_ref_id = social_news.candidate.id
```

- Later content candidate should not reference the original `social_news.candidate`; it should reference `living_info.topic_cluster` or `living_info.normalized_item`.

## 8. Existing LIVING_INFO Backfill Strategy

Existing rows are identified by:

```sql
SELECT *
FROM content.content_candidate
WHERE source_domain = 'LIVING_INFO'
  AND raw_ref_table = 'social_news.candidate';
```

Current observed state:

```text
LIVING_INFO rows: 54
raw_ref_table social_news.candidate: 54
```

Backfill should be preview-first:

```text
content.content_candidate
-> join social_news.candidate by raw_ref_id
-> classify preview action
-> export JSON/CSV
-> manual review
-> only later insert into living_info
```

Preview classifications:

```text
MIGRATE_SOURCE_ITEM
MIGRATE_NORMALIZED_ITEM
DUPLICATE_SKIP
LOW_VALUE_ARCHIVE
NEEDS_MANUAL_REVIEW
DO_NOT_MIGRATE
```

Mapping to `living_info.source_item`:

```text
source_url <- source_url / original_source_url / link_url
canonical_url <- social_news.candidate.canonical_url if available
source_name <- source_name / original_source_name
source_type <- from social_news.candidate.source_type or 'SOCIAL_NEWS'
raw_title <- original_title / title
raw_summary <- summary_en
raw_body <- body_en
published_at <- original_published_at
collected_at <- original_collected_at
source_trust_level <- derived from source/domain
duplicate_key <- canonical/source URL or raw ref fallback
content_hash <- normalized title/summary/body hash
raw_ref_table <- content.content_candidate.raw_ref_table
raw_ref_id <- content.content_candidate.raw_ref_id
raw_payload <- source candidate + content gate metadata
```

Mapping to `living_info.normalized_item`:

```text
normalized_primary_category <- mapped from category
normalized_secondary_category <- original category
source_usage <- based on quality gate/backfill action
info_signal_type <- INFORMATIONAL / NEWS_EVENT / LOW_VALUE_NOISE
target_user <- inferred later, empty in preview if unclear
action_type <- inferred later, empty in preview if unclear
topic_key_candidate <- normalized category + core topic phrase
validation_needed_yn <- Y
actionability_score <- practical_value_score or preview score
repeatability_score <- derived from category/source
normalization_confidence <- preview confidence
status <- preview status
```

Already `POSTED` rows:

- Do not automatically promote to future living knowledge.
- They may be backfilled as historical source evidence if they pass quality rules.
- Low-value `POSTED` rows should be flagged `LOW_VALUE_ARCHIVE` or `NEEDS_MANUAL_REVIEW`.

Missing URL rows:

- Do not migrate automatically.
- Mark as `NEEDS_MANUAL_REVIEW` or `DO_NOT_MIGRATE`.

Duplicate URL rows:

- Migrate only representative `source_item`.
- Preserve related rows as duplicate context only if the schema later needs a duplicate relation table.

## 9. Future Content Candidate Creation from LIVING_INFO

Future method:

```text
ContentService.sync_living_info(limit=...)
```

Future query source:

```text
living_info.topic_cluster
WHERE public_candidate_ready_yn = 'Y'
  AND validation_status = 'VALIDATED'
  AND cluster_status IN ('READY_FOR_REVIEW', 'OPEN')
```

Future content payload:

```text
source_domain = 'LIVING_INFO'
content_type = 'LIVING_GUIDE'
raw_ref_table = 'living_info.topic_cluster'
raw_ref_id = topic_cluster.id
category = topic_cluster.primary_category
priority_group = 'LIVING_GUIDE'
status = 'READY_TO_REVIEW'
review_required_yn = TRUE
```

Single official utility page exception:

```text
raw_ref_table = 'living_info.normalized_item'
raw_ref_id = normalized_item.id
```

Only allow this when:

- source is official or trusted secondary
- link is valid
- topic is evergreen utility
- no community-only fact
- review gate passes

No direct publish rule:

- `living_info.source_item` never calls publisher.
- `living_info.topic_cluster` never calls publisher.
- Only `content.content_candidate` can enter Telegram review or Facebook publishing paths.

## 10. Compatibility with Telegram/Card/Facebook

Telegram:

- No Telegram runtime change is required while `living_info` only stores source/domain data.
- Existing Telegram review continues to read from `content.content_candidate`.
- Future living content reaches Telegram only after `ContentService.sync_living_info()` creates a `content.content_candidate`.

Card generation:

- Current card guardrail already expects topic/fact evidence such as:

```text
topic_key
topic_cluster_id
source_spread_count
usable_point_count
```

- Future `sync_living_info()` should include these in `raw_payload`.
- Until then, single-source living rows should remain blocked from public-style card generation.

Facebook:

- Facebook publisher remains unchanged.
- `living_info` does not publish.
- Existing `content.content_candidate` publish rules remain protected.
- Future living content must pass the same content review/publish gates.

Protected behavior unchanged:

- Facebook publisher payload
- Facebook token validation
- Telegram send/callback runtime
- scheduler interval
- bot ON/OFF state
- admin auth/env/config

## 11. Phased Implementation Plan

### Phase 0: Documentation/design only

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY + SYSTEM_ARCHITECTURE_DOCS`
- MODE: `READ_ONLY_AUDIT` or `DOC_ONLY`
- Risk: LOW
- Files likely involved:
  - `DOC/database/06_DOMAIN_DATA_CURRENT.md`
  - `DOC/database/TO_BE_DB_ARCHITECTURE.md`
  - `DOC/walkthrough/execution-history/`
- Protected areas: none
- Verification:
  - document diff only
  - no runtime code diff
- Stop conditions:
  - user requests runtime behavior change without approved mode

### Phase 1: Add migration SQL draft only, no execution

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM
- Files likely involved:
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql`
  - optional verification SQL under scripts/generated path
- Protected areas:
  - migration execution
  - destructive DB changes
- Verification:
  - SQL syntax review
  - `rg` confirms no scheduler/publisher/auth files touched
  - no DB execution
- Stop conditions:
  - destructive DDL needed
  - enum/check constraints block uncertain values

### Phase 2: Create read-only backfill preview utility

- AREA: `LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM
- Files likely involved:
  - `SRC/foreign_worker_life_info_collector/living_info/backfill_preview.py`
  - `SRC/foreign_worker_life_info_collector/living_info/__init__.py`
- Protected areas:
  - DB mutation
  - migration execution
  - publisher/scheduler/Telegram runtime
- Verification:
  - py_compile
  - run preview with output file only
  - confirm no INSERT/UPDATE/DELETE in utility
- Stop conditions:
  - utility requires writing DB
  - utility needs collector execution

### Phase 3: Execute additive migration after approval

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM-HIGH
- Files likely involved:
  - migration file
  - migration verification script
- Protected areas:
  - DB schema change
- Verification:
  - before/after table counts
  - `information_schema.tables`
  - `pg_indexes`
  - FK/constraint query
- Stop conditions:
  - destructive migration
  - production-like DB without backup/approval

### Phase 4: Create `living_info.repository` with table-level methods but no scheduler/runtime write path

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM
- Files likely involved:
  - `SRC/foreign_worker_life_info_collector/living_info/repository.py`
  - `SRC/foreign_worker_life_info_collector/living_info/models.py`
  - tests
- Protected areas:
  - scheduler
  - publisher
  - auth/env/config
- Verification:
  - py_compile
  - repository unit tests with dry-run/mocked DB if available
  - no runtime call sites changed
- Stop conditions:
  - repository auto-runs migration
  - repository changes content publisher

### Phase 5: Add manual/dev-only ingestion from existing `content.content_candidate` LIVING_INFO rows

- AREA: `LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM
- Files likely involved:
  - `living_info/service.py`
  - `living_info/backfill_preview.py`
  - optional dev-only tool
- Protected areas:
  - automatic runtime ingestion
  - scheduler
  - publisher
- Verification:
  - dry-run preview first
  - limited approved row count
  - before/after insert counts if later approved
- Stop conditions:
  - missing URL rows dominate
  - low-value/noise rows cannot be filtered safely

### Phase 6: Modify `sync_social_news()` so living-classified rows go to `living_info`

- AREA: `LIVING_DOMAIN + CONTENT_QUEUE + SOCIAL_NEWS_CANDIDATE`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM-HIGH
- Files likely involved:
  - `content/service.py`
  - `living_info/service.py`
  - tests
- Protected areas:
  - publisher
  - scheduler
  - Telegram runtime
  - auth/env/config
- Verification:
  - non-living social news still creates `SOCIAL_NEWS / NEWS_ARTICLE`
  - living rows create `living_info.source_item` and no direct `content.content_candidate`
  - existing `ContentRepository.upsert_candidate()` behavior preserved for non-living
  - no Facebook/Telegram send triggered
- Stop conditions:
  - content sync endpoint becomes incompatible
  - old LIVING_INFO rows are accidentally archived/deleted

### Phase 7: Add `sync_living_info()` that creates content candidates only from ready topic clusters

- AREA: `LIVING_DOMAIN + CONTENT_QUEUE`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM-HIGH
- Files likely involved:
  - `content/service.py`
  - `content/repository.py`
  - `living_info/repository.py`
  - `living_info/service.py`
  - tests
- Protected areas:
  - publisher
  - scheduler
  - Telegram runtime behavior
- Verification:
  - only `public_candidate_ready_yn='Y'` clusters sync
  - `raw_ref_table='living_info.topic_cluster'`
  - Telegram/card preview can read topic evidence from `raw_payload`
  - no auto-publish
- Stop conditions:
  - topic readiness cannot be computed safely
  - community-only signal would become content

### Phase 8: Future topic clustering and fact/card point generation after validation

- AREA: `LIVING_DOMAIN + CONTENT_CARD_GENERATION + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM-HIGH
- Files likely involved:
  - `living_info/topic_clusterer.py`
  - future `fact_point` / `card_point` modules
  - card generator tests
- Protected areas:
  - publisher
  - Telegram runtime
  - scheduler
- Verification:
  - official/secondary validation source exists
  - no community-only fact
  - 3 valid card points minimum
  - card preview remains review-only
- Stop conditions:
  - source validation missing
  - legal/visa/medical/financial claims lack official source

## 12. Stop Conditions

Stop implementation if:

- migration execution is required without explicit approval
- destructive DDL is needed
- DB write/backfill is requested without dry-run preview
- source rows need collector execution
- scheduler changes are required
- Telegram runtime behavior must change
- Facebook publisher/payload/selection must change
- auth/env/config changes are needed
- community/trend signal would directly create `content.content_candidate`
- `living_info.source_item` would publish directly
- existing `content.content_candidate` rows would be deleted or mass-updated
- `fact_point/card_point` becomes necessary before source validation policy is stable

## 13. CODE_TASK_CANDIDATE

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY
MODE: GUARDED_FIX
FOCUS:
Create a non-executed PostgreSQL migration SQL draft for the first `living_info` physical schema.
WHY:
The design audit confirms `living_info` tables do not exist and the next safe implementation artifact is a reviewable migration draft.
RISK: MEDIUM
PROTECTED AREA:
Migration execution, destructive DB changes, publisher, scheduler, Telegram runtime, auth/env/config
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql
DOC/walkthrough/execution-history/2026-06-28/
RECOMMENDED NEXT PROMPT:
Create only the non-executed migration SQL draft for `living_info.source_item`, `normalized_item`, `source_signal`, `topic_cluster`, and `topic_cluster_item`. Do not execute migration and do not modify runtime code.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY
MODE: GUARDED_FIX
FOCUS:
Create a read-only backfill preview utility for current `content.content_candidate` rows with `source_domain = 'LIVING_INFO'`.
WHY:
Existing 54 rows contain duplicates, missing URLs, low-value categories, and already-posted rows; they need preview classification before any migration.
RISK: MEDIUM
PROTECTED AREA:
DB mutation, migration execution, collector execution, publisher, scheduler, Telegram runtime, auth/env/config
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/living_info/backfill_preview.py
SRC/foreign_worker_life_info_collector/living_info/__init__.py
DOC/walkthrough/execution-history/2026-06-28/
RECOMMENDED NEXT PROMPT:
Implement a local read-only backfill preview utility that exports proposed actions to JSON/CSV and performs no INSERT, UPDATE, DELETE, or migration.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY
MODE: GUARDED_FIX
FOCUS:
Create `living_info.repository` and models after migration approval, with table-level methods but no runtime write path.
WHY:
The service needs a DB access layer before `sync_social_news()` can be safely split.
RISK: MEDIUM
PROTECTED AREA:
Scheduler, publisher, Telegram runtime, auth/env/config
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/living_info/models.py
SRC/foreign_worker_life_info_collector/living_info/repository.py
SRC/foreign_worker_life_info_collector/tests/
RECOMMENDED NEXT PROMPT:
After living_info migration is approved/applied, implement repository skeleton and tests without changing content sync or scheduler runtime.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + CONTENT_QUEUE + SOCIAL_NEWS_CANDIDATE
MODE: GUARDED_FIX
FOCUS:
Split `ContentService.sync_social_news()` so living-classified rows enter `living_info` instead of directly becoming `content.content_candidate`.
WHY:
This is the boundary where current LIVING_INFO labels are created, and it is the smallest controlled split point.
RISK: MEDIUM-HIGH
PROTECTED AREA:
Publisher, scheduler, Telegram runtime, auth/env/config, destructive DB updates
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/content/service.py
SRC/foreign_worker_life_info_collector/living_info/service.py
SRC/foreign_worker_life_info_collector/tests/
RECOMMENDED NEXT PROMPT:
Implement the social-news living split after migration/repository are ready, preserving non-living content sync and preventing automatic content candidates for living rows.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
FOCUS:
Audit how `living_info.topic_cluster` should sync into `content.content_candidate` without breaking Telegram/card/Facebook boundaries.
WHY:
Future living content should reference `living_info.topic_cluster`, but final review/publish ownership must remain in content.
RISK: MEDIUM
PROTECTED AREA:
Publisher, scheduler, Telegram runtime, DB mutation, auth/env/config
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/content/service.py
SRC/foreign_worker_life_info_collector/content/repository.py
SRC/foreign_worker_life_info_collector/living_info/
RECOMMENDED NEXT PROMPT:
Read-only audit the future `sync_living_info()` design and payload contract for topic-cluster-based content candidates.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY + CONTENT_CARD_GENERATION
MODE: GUARDED_FIX
FOCUS:
Prototype topic clustering later after source validation and repository/write path are stable.
WHY:
Topic clustering and fact/card points should be built only after source evidence and signal separation are reliable.
RISK: MEDIUM-HIGH
PROTECTED AREA:
Publisher, scheduler, Telegram runtime, auth/env/config
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/living_info/topic_clusterer.py
SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py
SRC/foreign_worker_life_info_collector/tests/
RECOMMENDED NEXT PROMPT:
Prototype topic clustering for living_info with no public publishing and no community-only facts.
```

## 14. Final Recommendation

The safest next implementation step is:

```text
Create only the non-executed migration SQL draft for `living_info`.
```

Recommended immediate sequence:

```text
1. migration SQL draft only
2. read-only backfill preview utility
3. migration execution only after explicit approval
4. repository skeleton after schema exists
5. social_news living split
6. living_info topic_cluster -> content.content_candidate sync
```

Do not start by modifying `sync_social_news()`.

Reason:

- There are no `living_info` tables yet.
- Splitting runtime before schema/repository exists would either fail or silently fall back to the old content-label behavior.
- The first safe executable artifact is a migration draft that can be reviewed without touching DB or runtime behavior.
