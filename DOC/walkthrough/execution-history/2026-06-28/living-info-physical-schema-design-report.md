# READ_ONLY_AUDIT REPORT: LIVING_INFO Physical Schema Design

## 1. Pre-Review

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY + CONTENT_QUEUE + SYSTEM_ARCHITECTURE_DOCS`
- MODE: `READ_ONLY_AUDIT`
- Risk: MEDIUM
- Protected areas touched: NO
- Files inspected:
  - `CODEX_BOOTSTRAP.md`
  - `DOC/architecture/00_PRODUCT_NORTH_STAR.md`
  - `DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md`
  - `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
  - `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
  - `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  - `DOC/database/00_DB_ARCHITECTURE_INDEX.md`
  - `DOC/database/01_CURRENT_DB_MAP.md`
  - `DOC/database/02_SOCIAL_NEWS_CURRENT.md`
  - `DOC/database/03_CONTENT_CURRENT.md`
  - `DOC/database/06_DOMAIN_DATA_CURRENT.md`
  - `DOC/database/TO_BE_DB_ARCHITECTURE.md`
  - `DOC/to-be/생활정보_개선점.md`
  - `DOC/walkthrough/2026-06-28 - execute prompt.md`
  - `DOC/walkthrough/execution-history/2026-06-27/living-info-source-spectrum-expansion-research-report.md`
  - `DOC/walkthrough/execution-history/2026-06-20/living-info-topic-card-read-only-audit-report.md`
  - `DOC/walkthrough/execution-history/2026-06-20/living-info-card-generation-guardrail-report.md`
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/content/repository.py`
  - `SRC/foreign_worker_life_info_collector/storage/db/postgres.py`
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/admin_postgres_schema.sql`
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_07_content_candidate.sql`
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_06_immigration_info.sql`
- DB read-only queries run: YES
  - `information_schema.tables`
  - `pg_namespace`
  - `content.content_candidate` aggregate/sample SELECT
- Runtime/code changes: NO

## 2. Current State

`living_info` physical schema does not currently exist in the local PostgreSQL database.

Read-only metadata result:

```text
domain_schemas=
domain_tables_count=0
```

The following expected schemas/tables were not found:

- `living_info`
- `living_info.source_item`
- `living_info.raw_item`
- `living_info.normalized_item`
- `living_info.source_signal`
- `living_info.fact_point`
- `living_info.card_point`
- `living_info.topic_cluster`
- `housing_info`
- `healthcare_info`
- `banking_info`
- `transportation_info`

Current `LIVING_INFO` data exists only as content labels in:

```text
content.content_candidate
```

Observed current source reference:

```text
raw_ref_table = social_news.candidate
raw_ref_id = social_news.candidate.id
source_domain = LIVING_INFO
content_type = LIVING_GUIDE
```

The current code path is:

```text
social_news.candidate
-> ContentService.social_news_payload()
-> content.content_candidate
```

`ContentService.social_news_payload()` maps living-classified social/news rows to:

```text
source_domain = "LIVING_INFO"
content_type = "LIVING_GUIDE"
```

This confirms the current problem statement: living information exists as a content label, not as a durable living-domain data layer.

## 3. Current LIVING_INFO Data Count

Read-only query was run against local PostgreSQL:

```sql
SELECT source_domain, content_type, category, COUNT(*)
FROM content.content_candidate
GROUP BY source_domain, content_type, category
ORDER BY COUNT(*) DESC;
```

Relevant result:

```text
LIVING_INFO / LIVING_GUIDE / settlement_life: 11
LIVING_INFO / LIVING_GUIDE / safety: 10
LIVING_INFO / LIVING_GUIDE / transportation: 7
LIVING_INFO / LIVING_GUIDE / banking: 6
LIVING_INFO / LIVING_GUIDE / housing: 6
LIVING_INFO / LIVING_GUIDE / insurance: 5
LIVING_INFO / LIVING_GUIDE / healthcare: 4
LIVING_INFO / LIVING_GUIDE / travel: 2
LIVING_INFO / LIVING_GUIDE / culture: 1
LIVING_INFO / LIVING_GUIDE / local_events: 1
LIVING_INFO / LIVING_GUIDE / local_community: 1
```

Total observed `LIVING_INFO` rows:

```text
54
```

Status distribution:

```text
POSTED: 40
ARCHIVED: 6
SCORED: 6
READY_TO_PUBLISH: 1
READY_TO_REVIEW: 1
```

Raw reference distribution:

```text
social_news.candidate: 54
```

Duplicate URL groups observed:

```text
- : 6
https://www.koreaherald.com/article/10685398 : 2
https://www.travelandtourworld.com/news/article/travel-confidence-tested-as-bali-authorities-counter-south-korea-warning-with-strong-safety-push-and-crime-drop-data : 2
```

Interpretation:

- Current `LIVING_INFO` rows are small enough for manual/dry-run backfill preview.
- They include low-value/noise examples such as travel, culture, local events, stock/economy, non-Korea or generic travel safety items.
- Six rows have no usable URL in the effective URL grouping.
- Existing data should not be bulk migrated blindly.

## 4. Schema Design Recommendation

### Option A: minimal 3-table schema

Tables:

- `living_info.source_item`
- `living_info.normalized_item`
- `living_info.topic_cluster`

Strengths:

- Small initial surface.
- Preserves source/domain vs content boundary.
- Gives living data its own durable layer.
- Avoids premature extraction of fact/card points.

Weakness:

- Community signal handling is awkward if stored only as `source_item`.
- Topic cluster membership needs a join table or JSON payload later.

### Option B: include `fact_point` / `card_point` now

Strengths:

- Directly supports card generation.
- Matches existing renderer guardrail expectations: `fact_point_id`, `card_point_id`, `usable_point_count`.

Weakness:

- Too early. The system has not yet decided extraction ownership, validation rules, point confidence, or review lifecycle.
- It can create false confidence: a short point may look ready even when source validation is weak.
- It increases migration risk before `topic_key` and `source_signal` are stable.

### Option C: separate `source_signal` table

Tables:

- `living_info.source_item`
- `living_info.normalized_item`
- `living_info.source_signal`
- `living_info.topic_cluster`
- `living_info.topic_cluster_item`

Strengths:

- Cleanly separates authoritative source evidence from community/trend demand signals.
- Matches architecture rule: community sources are user-need signals, not facts.
- Supports source spread and demand scoring without storing personal stories as source facts.

Weakness:

- Slightly larger first schema.
- Needs strict PII/TOS rules before any community ingestion.

### Recommendation

Start with a restrained version of Option C:

```text
living_info.source_item
living_info.normalized_item
living_info.source_signal
living_info.topic_cluster
living_info.topic_cluster_item
```

Do not create `living_info.fact_point` or `living_info.card_point` in the first migration.

Reason:

- `source_item` is needed for official, secondary, trusted media, blog, and current social/news evidence.
- `source_signal` is needed because community/trend data must not be stored as authoritative fact rows.
- `topic_cluster` is needed to move from single article labels to topic-based living guides.
- `topic_cluster_item` is needed to avoid hiding many-to-many membership in JSON.
- `fact_point/card_point` should come only after source validation, topic clustering, and manual preview rules are proven.

## 5. Proposed Tables

### 5.1 `living_info.source_item`

Purpose:

Store source evidence for living-domain items from official, secondary, trusted media, blog, and source-backed discovery sources.

Columns:

```text
id BIGINT PRIMARY KEY
source_url TEXT NOT NULL
canonical_url TEXT NOT NULL DEFAULT ''
publishable_link_url TEXT NOT NULL DEFAULT ''
source_name VARCHAR(200) NOT NULL DEFAULT ''
source_type VARCHAR(60) NOT NULL
source_access_policy VARCHAR(60) NOT NULL DEFAULT 'PUBLIC_PAGE'
language VARCHAR(20) NOT NULL DEFAULT 'en'
country VARCHAR(80) NOT NULL DEFAULT 'Korea'
region_in_korea VARCHAR(120) NOT NULL DEFAULT ''
raw_title TEXT NOT NULL DEFAULT ''
raw_summary TEXT NOT NULL DEFAULT ''
raw_body TEXT NOT NULL DEFAULT ''
published_at TIMESTAMPTZ
collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
last_checked_at TIMESTAMPTZ
source_trust_level VARCHAR(40) NOT NULL DEFAULT 'DISCOVERY'
privacy_risk_level VARCHAR(40) NOT NULL DEFAULT 'LOW'
duplicate_key VARCHAR(160) NOT NULL
content_hash VARCHAR(160) NOT NULL DEFAULT ''
source_status VARCHAR(40) NOT NULL DEFAULT 'COLLECTED'
active_yn CHAR(1) NOT NULL DEFAULT 'Y'
raw_ref_table VARCHAR(120) NOT NULL DEFAULT ''
raw_ref_id BIGINT
raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```

Keys:

- `PRIMARY KEY(id)`

Unique constraints:

- `UNIQUE(duplicate_key)`
- Consider later: `UNIQUE(raw_ref_table, raw_ref_id)` where `raw_ref_table <> ''`

Indexes:

- `(source_type, collected_at DESC)`
- `(source_trust_level, collected_at DESC)`
- `(source_status, collected_at DESC)`
- `(canonical_url)`
- `(content_hash)`
- `(raw_ref_table, raw_ref_id)`

Status lifecycle:

```text
COLLECTED
NORMALIZED
DUPLICATE
LOW_VALUE_ARCHIVED
VALIDATION_REQUIRED
READY_FOR_CLUSTERING
FAILED
```

Ownership:

- Owned by `LIVING_DOMAIN`.
- Not publishable by itself.

Relation to `content.content_candidate`:

- Future content candidate should reference source/cluster through:

```text
raw_ref_table = living_info.topic_cluster
raw_ref_id = living_info.topic_cluster.id
```

or for single official utility pages:

```text
raw_ref_table = living_info.normalized_item
raw_ref_id = living_info.normalized_item.id
```

### 5.2 `living_info.normalized_item`

Purpose:

Store normalized classification and intended use for a `source_item`.

Columns:

```text
id BIGINT PRIMARY KEY
source_item_id BIGINT NOT NULL REFERENCES living_info.source_item(id)
normalized_primary_category VARCHAR(60) NOT NULL
normalized_secondary_category VARCHAR(120) NOT NULL DEFAULT ''
source_usage VARCHAR(60) NOT NULL
info_signal_type VARCHAR(60) NOT NULL
target_user VARCHAR(120) NOT NULL DEFAULT ''
action_type VARCHAR(120) NOT NULL DEFAULT ''
topic_key_candidate VARCHAR(180) NOT NULL DEFAULT ''
validation_needed_yn CHAR(1) NOT NULL DEFAULT 'Y'
validation_source_type VARCHAR(60) NOT NULL DEFAULT ''
actionability_score NUMERIC(8,4) NOT NULL DEFAULT 0
repeatability_score NUMERIC(8,4) NOT NULL DEFAULT 0
source_reliability_score NUMERIC(8,4) NOT NULL DEFAULT 0
normalization_confidence NUMERIC(8,4) NOT NULL DEFAULT 0
normalization_reason TEXT NOT NULL DEFAULT ''
status VARCHAR(40) NOT NULL DEFAULT 'NORMALIZED'
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```

Keys:

- `PRIMARY KEY(id)`
- `FOREIGN KEY(source_item_id)`

Unique constraints:

- `UNIQUE(source_item_id)`

Indexes:

- `(normalized_primary_category, normalized_secondary_category)`
- `(topic_key_candidate)`
- `(source_usage, status)`
- `(info_signal_type, status)`
- `(actionability_score DESC, repeatability_score DESC)`

Status lifecycle:

```text
NORMALIZED
REQUIRES_VALIDATION
CLUSTER_READY
DUPLICATE_SKIPPED
LOW_VALUE_ARCHIVED
MANUAL_REVIEW_REQUIRED
```

Ownership:

- Owned by `LIVING_DOMAIN`.
- Represents domain meaning, not final content text.

Relation to `content.content_candidate`:

- Should not create content automatically unless source usage and review gates pass.

### 5.3 `living_info.source_signal`

Purpose:

Store community/trend/discovery demand signals without treating them as facts.

Columns:

```text
id BIGINT PRIMARY KEY
signal_source_name VARCHAR(200) NOT NULL DEFAULT ''
signal_source_url TEXT NOT NULL DEFAULT ''
signal_platform VARCHAR(80) NOT NULL DEFAULT ''
signal_type VARCHAR(60) NOT NULL
language VARCHAR(20) NOT NULL DEFAULT ''
country VARCHAR(80) NOT NULL DEFAULT 'Korea'
region_in_korea VARCHAR(120) NOT NULL DEFAULT ''
primary_category VARCHAR(60) NOT NULL
topic_key_candidate VARCHAR(180) NOT NULL DEFAULT ''
target_user VARCHAR(120) NOT NULL DEFAULT ''
pain_point_summary TEXT NOT NULL DEFAULT ''
signal_count INTEGER NOT NULL DEFAULT 1
privacy_risk_level VARCHAR(40) NOT NULL DEFAULT 'MEDIUM'
source_access_policy VARCHAR(60) NOT NULL DEFAULT 'PUBLIC_METADATA_ONLY'
validation_needed_yn CHAR(1) NOT NULL DEFAULT 'Y'
status VARCHAR(40) NOT NULL DEFAULT 'SIGNAL_COLLECTED'
observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb
```

Keys:

- `PRIMARY KEY(id)`

Unique constraints:

- `UNIQUE(signal_platform, topic_key_candidate, language, region_in_korea, observed_at)` is too strict and not recommended first.
- Recommended first unique key: none, use duplicate grouping in dry-run logic.

Indexes:

- `(topic_key_candidate, observed_at DESC)`
- `(primary_category, observed_at DESC)`
- `(signal_type, status)`
- `(privacy_risk_level)`

Status lifecycle:

```text
SIGNAL_COLLECTED
SIGNAL_NORMALIZED
VALIDATION_NEEDED
CLUSTER_ATTACHED
IGNORED_PRIVATE_OR_UNSAFE
LOW_VALUE_NOISE
```

Ownership:

- Owned by `LIVING_DOMAIN + DATA_SOURCE_QUALITY`.
- Must not be used as public fact.

Relation to `content.content_candidate`:

- No direct relation.
- Can affect `topic_cluster.community_signal_count` only.

### 5.4 `living_info.topic_cluster`

Purpose:

Group source/normalized items and signals into potential living guide topics.

Columns:

```text
id BIGINT PRIMARY KEY
topic_key VARCHAR(180) NOT NULL
primary_category VARCHAR(60) NOT NULL
secondary_category VARCHAR(120) NOT NULL DEFAULT ''
target_user VARCHAR(120) NOT NULL DEFAULT ''
action_type VARCHAR(120) NOT NULL DEFAULT ''
source_count INTEGER NOT NULL DEFAULT 0
evidence_count INTEGER NOT NULL DEFAULT 0
community_signal_count INTEGER NOT NULL DEFAULT 0
official_source_count INTEGER NOT NULL DEFAULT 0
secondary_source_count INTEGER NOT NULL DEFAULT 0
source_spread_count INTEGER NOT NULL DEFAULT 0
readiness_score NUMERIC(8,4) NOT NULL DEFAULT 0
public_candidate_ready_yn CHAR(1) NOT NULL DEFAULT 'N'
validation_status VARCHAR(40) NOT NULL DEFAULT 'PENDING'
cluster_status VARCHAR(40) NOT NULL DEFAULT 'OPEN'
last_signal_at TIMESTAMPTZ
last_evidence_at TIMESTAMPTZ
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```

Keys:

- `PRIMARY KEY(id)`

Unique constraints:

- `UNIQUE(topic_key, primary_category, target_user, action_type)`

Indexes:

- `(primary_category, readiness_score DESC)`
- `(public_candidate_ready_yn, readiness_score DESC)`
- `(validation_status, cluster_status)`
- `(last_signal_at DESC NULLS LAST)`
- `(last_evidence_at DESC NULLS LAST)`

Status lifecycle:

```text
OPEN
WATCH_TOPIC
READY_FOR_REVIEW
CONTENT_CANDIDATE_CREATED
LOW_VALUE_ARCHIVED
MERGED
```

Ownership:

- Owned by `LIVING_DOMAIN`.
- This is the first object that may become a content candidate.

Relation to `content.content_candidate`:

Future source-to-content mapping:

```text
raw_ref_table = living_info.topic_cluster
raw_ref_id = topic_cluster.id
source_domain = LIVING_INFO
content_type = LIVING_GUIDE
```

### 5.5 `living_info.topic_cluster_item`

Purpose:

Represent many-to-many membership between topic clusters and evidence/signal rows.

Columns:

```text
id BIGINT PRIMARY KEY
topic_cluster_id BIGINT NOT NULL REFERENCES living_info.topic_cluster(id)
normalized_item_id BIGINT REFERENCES living_info.normalized_item(id)
source_signal_id BIGINT REFERENCES living_info.source_signal(id)
item_role VARCHAR(60) NOT NULL
weight_score NUMERIC(8,4) NOT NULL DEFAULT 1
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```

Keys:

- `PRIMARY KEY(id)`
- `FOREIGN KEY(topic_cluster_id)`
- `FOREIGN KEY(normalized_item_id)`
- `FOREIGN KEY(source_signal_id)`

Unique constraints:

- `UNIQUE(topic_cluster_id, normalized_item_id)` where `normalized_item_id IS NOT NULL`
- `UNIQUE(topic_cluster_id, source_signal_id)` where `source_signal_id IS NOT NULL`

Indexes:

- `(topic_cluster_id, item_role)`
- `(normalized_item_id)`
- `(source_signal_id)`

Status lifecycle:

- No independent lifecycle needed in first version.

Ownership:

- Owned by `LIVING_DOMAIN`.

Relation to `content.content_candidate`:

- Indirect only through `topic_cluster`.

## 6. Source-to-Content Flow

Recommended new flow:

```text
external source
-> living_info.source_item
-> living_info.normalized_item
-> living_info.topic_cluster_item
-> living_info.topic_cluster
-> content.content_candidate
-> content.publish_log
```

Community/trend flow:

```text
community/trend/discovery source
-> living_info.source_signal
-> living_info.topic_cluster_item
-> living_info.topic_cluster
```

Community/trend signal must not directly create:

```text
content.content_candidate
```

Future `fact_point/card_point` position:

```text
living_info.topic_cluster
-> living_info.fact_point
-> living_info.card_point
-> content.content_candidate
```

But `fact_point/card_point` should wait until:

- source inventory policy is approved
- topic clustering is stable
- point validation rules exist
- manual preview/backfill confirms useful output

## 7. Existing Data Backfill Plan

Design only. Do not execute.

### Phase 1: read-only count

```sql
SELECT source_domain, content_type, category, status, COUNT(*)
FROM content.content_candidate
WHERE source_domain = 'LIVING_INFO'
GROUP BY source_domain, content_type, category, status
ORDER BY category, status;
```

### Phase 2: duplicate grouping

```sql
SELECT COALESCE(NULLIF(source_url,''), NULLIF(original_source_url,''), NULLIF(link_url,''), '-') AS effective_url,
       COUNT(*) AS row_count,
       MIN(id) AS representative_content_candidate_id,
       MAX(updated_at) AS last_seen_at
FROM content.content_candidate
WHERE source_domain = 'LIVING_INFO'
GROUP BY effective_url
ORDER BY row_count DESC, last_seen_at DESC;
```

### Phase 3: representative selection

Representative priority:

1. valid URL exists
2. not archived
3. high `final_publish_score`
4. official/secondary source if known
5. more complete title/summary/body
6. latest `original_collected_at`

### Phase 4: source_item preview

Create a dry-run preview table/file, not DB rows:

```text
source_url
canonical_url
source_name
source_type
language
country
region_in_korea
raw_title
raw_summary
raw_body
source_trust_level
privacy_risk_level
duplicate_key
content_hash
raw_ref_table
raw_ref_id
backfill_action
backfill_reason
```

### Phase 5: normalized_item preview

Preview fields:

```text
source_item_preview_id
normalized_primary_category
normalized_secondary_category
source_usage
info_signal_type
target_user
action_type
topic_key_candidate
validation_needed_yn
actionability_score
repeatability_score
normalization_confidence
status
```

### Phase 6: manual review

Manual review required when:

- URL missing
- title/source is generic
- source is news-only
- category is `travel`, `culture`, `local_events`, or broad `safety`
- score conflicts with user value
- item is already `POSTED` but low-value
- non-Korea/global content appears

### Phase 7: migration later

Only after dry-run approval:

- add schema/table migration
- no runtime path switch
- no content candidate creation
- verify counts

### Phase 8: backfill later

Only after backup and approval:

- insert source_item rows
- insert normalized_item rows
- create topic cluster preview
- do not create public content automatically

Backfill classification values:

```text
MIGRATE_SOURCE_ITEM
MIGRATE_NORMALIZED_ITEM
DUPLICATE_SKIP
LOW_VALUE_ARCHIVE
NEEDS_MANUAL_REVIEW
DO_NOT_MIGRATE
```

## 8. Duplicate Handling Before Migration

Same `source_url`:

- If content/body/hash unchanged, migrate only representative row.
- Mark others as `DUPLICATE_SKIP` in preview.

Same `canonical_url`:

- Same as source URL; prefer canonical URL as `duplicate_key`.

Missing URL:

- Do not migrate automatically.
- Mark as `NEEDS_MANUAL_REVIEW` or `DO_NOT_MIGRATE`.

Same title/summary hash:

- If same source and same title/summary, one representative only.
- If different source but same topic, treat as possible `source_spread_count`, not duplicate deletion.

Same `topic_key_candidate`:

- Preserve multiple reliable sources as cluster evidence.
- Do not create multiple content candidates.

Low-value archive:

- Generic travel, generic politics, generic economy, stock market, generic culture/event, non-Korea property/investment, and missing-link items should not be migrated into active living source tables unless preserved as `LOW_VALUE_ARCHIVE`.

Representative item:

- One source representative per exact URL/hash.
- One topic representative per `topic_cluster` for content candidate creation.

## 9. Category/Usage/Info-Type Support

Primary category support:

```text
WORK
VISA_IMMIGRATION
LABOR_RIGHTS
HOUSING
HEALTHCARE
BANKING_FINANCE
TELECOM_DIGITAL_ID
TRANSPORTATION
PUBLIC_SERVICES
LEGAL_AID
EDUCATION_LANGUAGE
FAMILY_CHILDCARE
SAFETY_SCAM
REGIONAL_SUPPORT
DAILY_LIFE
COMMUNITY_SIGNAL
TREND_SIGNAL
LOW_VALUE_NOISE
```

These map to:

```text
living_info.normalized_item.normalized_primary_category
living_info.topic_cluster.primary_category
living_info.source_signal.primary_category
```

Source usage support:

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

These map to:

```text
living_info.normalized_item.source_usage
```

Info/signal type support:

```text
INFORMATIONAL
TREND_SIGNAL
NEWS_EVENT
OFFICIAL_UPDATE
ATTACHMENT_ONLY
LOW_VALUE_NOISE
```

These map to:

```text
living_info.normalized_item.info_signal_type
living_info.source_signal.signal_type
```

`target_user`, `action_type`, `validation_needed`, `topic_key_candidate` are first-class fields in:

```text
living_info.normalized_item
living_info.source_signal
living_info.topic_cluster
```

## 10. Risks

Over-schema risk:

- Too many tables can freeze uncertain ownership too early.
- Mitigation: start with source/signal/cluster only, no `fact_point/card_point`.

Premature `fact_point/card_point` risk:

- Card points look like public-ready knowledge even when validation is incomplete.
- Mitigation: create only after topic cluster preview proves quality.

Duplicate migration risk:

- Current 54 rows include missing URL, repeated URL, generic travel, generic culture, and low-value items.
- Mitigation: dry-run preview and manual review before backfill.

Content queue ownership risk:

- `content.content_candidate` is the publishable object and must remain owner of final public message, final link, review state, and publish state.
- Mitigation: `living_info` should preserve source/domain evidence, not publish directly.

DB migration risk:

- New schema affects future write path and backfill.
- Mitigation: non-destructive migration draft first; no execution in audit.

Rollback requirement:

- First migration must be additive only.
- Backfill should be reversible by source reference and batch id in future implementation.

## 11. Recommended Next Steps

1. `DOC_ONLY` schema policy
   - Update DB/to-be documentation with `living_info` ownership and source/signal separation.

2. Migration SQL draft only
   - Create a non-executed SQL draft for `living_info.source_item`, `normalized_item`, `source_signal`, `topic_cluster`, `topic_cluster_item`.

3. Dry-run backfill preview utility
   - Read from `content.content_candidate WHERE source_domain = 'LIVING_INFO'`.
   - Output JSON/CSV preview only.
   - No insert/update.

4. Manual review of preview
   - Classify each current row as `MIGRATE_SOURCE_ITEM`, `MIGRATE_NORMALIZED_ITEM`, `DUPLICATE_SKIP`, `LOW_VALUE_ARCHIVE`, `NEEDS_MANUAL_REVIEW`, or `DO_NOT_MIGRATE`.

5. Guarded migration after approval
   - Add schema/tables only.
   - No runtime write path switch.

6. Controlled backfill after backup
   - Insert approved rows only.
   - Verify counts.
   - Do not generate content candidates automatically.

## 12. CODE_TASK_CANDIDATE

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY + SYSTEM_ARCHITECTURE_DOCS
MODE: DOC_ONLY
FOCUS:
Document the first `living_info` physical schema policy and source/signal/topic ownership.
WHY:
The audit confirms there is no physical `living_info` schema, and current LIVING_INFO rows are labels copied from `social_news.candidate`.
RISK: LOW
PROTECTED AREA:
DB execution, runtime code, publisher, scheduler, Telegram runtime, auth/env/config
FILES LIKELY INVOLVED:
DOC/database/06_DOMAIN_DATA_CURRENT.md
DOC/database/TO_BE_DB_ARCHITECTURE.md
DOC/walkthrough/YYYY-MM-DD - execute prompt.md
RECOMMENDED NEXT PROMPT:
Convert the READ_ONLY_AUDIT living_info physical schema design into DOC_ONLY DB architecture updates without creating migrations or code.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY
MODE: GUARDED_FIX
FOCUS:
Create a migration SQL draft file for `living_info` schema, but do not execute it.
WHY:
The next implementation step needs a concrete, reviewable migration draft before any DB change.
RISK: MEDIUM
PROTECTED AREA:
Migration execution, destructive DB changes, publisher, scheduler, Telegram runtime, auth/env/config
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/storage/db/migrations/
DOC/walkthrough/execution-history/YYYY-MM-DD/
RECOMMENDED NEXT PROMPT:
Draft a non-executed PostgreSQL migration for `living_info.source_item`, `normalized_item`, `source_signal`, `topic_cluster`, and `topic_cluster_item`, with no runtime path changes.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY
MODE: GUARDED_FIX
FOCUS:
Create a read-only backfill preview utility for existing `content.content_candidate` rows where `source_domain = 'LIVING_INFO'`.
WHY:
Existing LIVING_INFO rows must be classified before migration because they include duplicate, missing-link, and low-value rows.
RISK: MEDIUM
PROTECTED AREA:
DB mutation, migration execution, publisher, scheduler, Telegram runtime, auth/env/config
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/tools/
DOC/walkthrough/execution-history/YYYY-MM-DD/
RECOMMENDED NEXT PROMPT:
Implement a local read-only preview utility that exports proposed `living_info` backfill actions to JSON/CSV without inserting or updating DB rows.
```

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_QUEUE + LIVING_DOMAIN
MODE: READ_ONLY_AUDIT
FOCUS:
Audit impact of switching future LIVING_INFO content candidates from `social_news.candidate` source refs to `living_info.topic_cluster` source refs.
WHY:
The content path must preserve `content.content_candidate` as publishable owner while moving source/domain evidence into `living_info`.
RISK: MEDIUM
PROTECTED AREA:
Publisher, scheduler, Telegram runtime, DB mutation, auth/env/config
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/content/service.py
SRC/foreign_worker_life_info_collector/content/repository.py
DOC/database/03_CONTENT_CURRENT.md
RECOMMENDED NEXT PROMPT:
Read-only audit the content sync path impact if future LIVING_INFO candidates reference `living_info.topic_cluster`.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY
MODE: GUARDED_FIX
FOCUS:
Implement future source-to-`living_info` write path after migration and preview approval.
WHY:
New incoming living data should stop being represented only as `content.content_candidate` labels.
RISK: MEDIUM-HIGH
PROTECTED AREA:
Publisher, scheduler, Telegram runtime, auth/env/config, external API behavior
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/
DOC/walkthrough/execution-history/YYYY-MM-DD/
RECOMMENDED NEXT PROMPT:
After migration approval, add a guarded living_info write path for official/secondary source evidence only, leaving community signals and publishing disabled.
```

## 13. Final Recommendation

The safest first implementation step is:

```text
DOC_ONLY schema policy
-> non-executed migration SQL draft
-> read-only backfill preview utility
-> manual review
-> guarded additive migration after approval
```

Do not start with runtime write-path changes.
Do not create `fact_point/card_point` yet.
Do not backfill current 54 rows automatically.

First physical schema should be:

```text
living_info.source_item
living_info.normalized_item
living_info.source_signal
living_info.topic_cluster
living_info.topic_cluster_item
```

This is the smallest schema that separates source evidence, community signal, and topic clustering while keeping `content.content_candidate` as the final review/publish owner.
