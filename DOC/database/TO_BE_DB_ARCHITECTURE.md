# DB To-Be Architecture

## 1. Purpose

This document defines the target direction for the WorkConnect database.

It is intentionally concise.

Detailed implementation decisions should be added after each Codex or developer task updates the DB, pipeline, or admin UI.

## 2. Product Context

WorkConnect provides practical, source-backed information for foreigners who want to work, live, and settle in Korea.

The database must support:

- trusted source collection
- normalized domain data
- publishable content generation
- Facebook/social publishing
- future GPT answer integration
- admin operations and auditability

## 3. Core Principle

WorkConnect DB separates:

```text
collected source/domain data
```

from:

```text
publishable content
```

and from:

```text
operation/control data
```

## 4. Target Schema Responsibilities

### admin / ops

Responsible for:

* admin access
* module configuration
* runtime configuration
* environment readiness
* bot status
* scheduler state
* operation logs
* dashboard status

### social_news

Responsible for:

* news collection
* raw news data
* normalized news data
* candidate scoring
* duplicate detection
* source-level news status

Not responsible for:

* final Facebook publishing ownership

### content

Responsible for:

* final publishable content candidates
* source reference mapping
* final title/summary/why-it-matters
* link validation status
* publish eligibility
* Facebook/social publish logs
* publish performance snapshots

### occupation

Responsible for:

* Employment24 job/occupation dictionary
* keyword mapping
* enrichment seeds
* future occupation guide source data

Not responsible for:

* active hiring/job posting unless a separate employment source is added

### immigration_info

Responsible for:

* official immigration/visa/stay notices
* source-backed government announcements
* future visa guide source data

### living_info

Responsible for:

* settlement/life information
* housing, banking, healthcare, transport, insurance, language, community data

## 5. Target Data Lifecycle

The target lifecycle is:

```text
external source
→ raw source record
→ normalized source record
→ domain candidate
→ content candidate
→ publish log
→ performance/audit data
```

No source/domain table should publish directly to Facebook.

## 6. Authoritative Publishing Owner

The authoritative publishing object is:

```text
content.content_candidate
```

The authoritative publishing log is:

```text
content.publish_log
```

Existing publish logs in source schemas should be treated as:

```text
legacy
transition-state
source-level audit
```

until migration confirms otherwise.

## 7. Content Candidate Contract

Every publishable item should have:

```text
source_domain
content_type
category
title
summary_en
why_it_matters_en
link_url
source_name
source_trust_level
raw_ref_table
raw_ref_id
status
publish_score
created_at
updated_at
published_at
facebook_post_url or external_post_id
```

## 8. Duplicate Data Policy

Duplicate source data must not be deleted automatically.

Duplicate data may represent:

* same URL repeat noise
* same title same source
* syndicated copy
* same topic from different source
* issue spread signal

Only representative or sufficiently distinct items should become content candidates.

## 9. Status Policy

To-be status values should be grouped by meaning.

### Source processing status

```text
COLLECTED
NORMALIZED
SUMMARIZED
EVALUATED
DUPLICATE
SKIPPED
FAILED
```

### Content status

```text
DRAFT
READY_TO_REVIEW
READY_TO_PUBLISH
POSTED
FAILED
ARCHIVED
REVIEW_REQUIRED
REVIEW_REQUIRED_SENSITIVE
CONTENT_INVALID
```

### Operation status

```text
IDLE
RUNNING
WAITING_COOLDOWN
FAILED_RETRYABLE
FAILED_BLOCKED
DISABLED
```

Do not mix these into one ambiguous status column.

## 10. Date Policy

Date fields should have clear meaning.

Required concepts:

```text
original_published_at
collected_at
normalized_at
content_created_at
content_updated_at
published_at
last_checked_at
```

UI must not display `updated_at` as if it were original publish date.

## 11. Dashboard Query Policy

Dashboard must use:

* summary APIs
* count queries
* recent logs with limit
* lightweight status tables/views

Dashboard must not:

* load all candidates
* load all content rows
* load all logs
* count in frontend
* trigger full collection accidentally

## 12. Migration Rule

All migration toward this architecture must be:

```text
non-destructive first
```

Preferred sequence:

```text
add new columns/tables
→ backfill
→ verify
→ switch UI/API
→ deprecate old fields
→ remove only after explicit approval
```

## 13. Open Questions

These must be answered gradually:

* Should duplicate groups become a separate table?
* Should source status and publish status be fully separated?
* Which publish log becomes authoritative after migration?
* How should content_candidate uniqueness be enforced?
* Which domain schemas are active vs planned?
* Should dashboard summary be a view, materialized view, or API aggregation?

# To-Be Content Flow

## 1. Purpose

This document defines the intended source-to-content flow.

It is a living guide.  
Codex or developers should update it after each implementation step.

## 2. Core Flow

The target flow is:

```text
external source
→ source raw table
→ source normalized table
→ domain candidate
→ content.content_candidate
→ content.publish_log
```

Only `content.content_candidate` can become a public Facebook/social post.

## 3. Source Domains

### Social News

```text
news collector
→ social_news.raw_item
→ social_news.normalized_item
→ social_news.candidate
→ content.content_candidate
```

Mapping:

```text
source_domain = SOCIAL_NEWS
content_type = NEWS_ARTICLE
raw_ref_table = social_news.candidate
raw_ref_id = social_news.candidate.id
```

Rules:

* duplicate rows should not all become content candidates
* Google RSS discovery-only rows should not become publishable unless canonical article URL and content are resolved
* sensitive news should become `REVIEW_REQUIRED_SENSITIVE`
* final posting text must be generated from article/content data, not operation logs

### Immigration

```text
official source
→ immigration_info.official_notice
→ content.content_candidate
```

Mapping:

```text
source_domain = IMMIGRATION_INFO
content_type = IMMIGRATION_NOTICE or GOVERNMENT_NOTICE
raw_ref_table = immigration_info.official_notice
raw_ref_id = immigration_info.official_notice.id
```

Rules:

* official notices should usually start as `READY_TO_REVIEW`
* legal/visa content must preserve official source URL
* generated summaries must not overstate legal certainty

### Occupation

```text
Employment24 API
→ occupation.raw_api_response
→ occupation.job_info / occupation.occupation_info
→ enrichment
→ content.content_candidate
```

Mapping after enrichment:

```text
source_domain = OCCUPATION_INFO
content_type = OCCUPATION_GUIDE
raw_ref_table = occupation.occupation_info
raw_ref_id = occupation.occupation_info.id
```

Rules:

* occupation data is dictionary data, not job posting data
* must be enriched before publishing
* possible visa tags are hints, not legal guarantees

### Living Info

```text
official/semi-official source
→ living_info.item
→ content.content_candidate
```

Mapping:

```text
source_domain = LIVING_INFO
content_type = LIVING_GUIDE
raw_ref_table = living_info.item
raw_ref_id = living_info.item.id
```

Rules:

* content must be practical and source-backed
* avoid generic travel/lifestyle content unless it helps settlement

## 4. Content Candidate Eligibility

A source item can become a content candidate only if it has:

```text
valid source URL
source name
clear title
usable summary or content
source trust level
category
foreign user relevance
language handling
```

A content candidate can become publishable only if it has:

```text
summary_en
why_it_matters_en
valid link_url
safe language
no operation log contamination
no unresolved sensitive content
publish score above threshold
```

## 5. Publishing Validation

Before publishing, validate:

```text
message language
link URL
source trust level
sensitive content
duplicate publish history
cooldown
daily max limit
required environment status
```

Block publishing if:

* message contains Korean in English post
* message contains operation words such as admin/repost/threshold/candidate/queue
* link is Google RSS
* link is publisher root only
* source is not directly relevant enough
* sensitive article is not reviewed
* Facebook token/env is invalid

## 6. Publish Output

Facebook publishing should separate:

```text
message
```

and:

```text
link
```

The message should contain:

* headline
* concise summary
* why it matters
* hashtags

The link should contain:

* canonical article/detail URL

## 7. Telegram Role

Telegram is an operation notification channel.

It is not an approval UI.

Telegram should report:

* posted
* skipped
* duplicate
* failed
* cooldown
* no safe candidate

Telegram should not be required for publishing approval.

## 8. Update Rule

Whenever a new source domain is connected to content, update this document with:

* source table
* source_domain value
* content_type value
* raw_ref_table format
* eligibility rule
* publishing risk

# DB Migration Roadmap

## 1. Purpose

This document defines a safe, phased migration path from the current DB structure to the target WorkConnect DB architecture.

It is intentionally high-level.

Each phase should be expanded after actual implementation work.

## 2. Migration Principles

All DB migration must be:

```text
non-destructive first
observable
reversible when possible
documented
tested before publish behavior changes
```

Do not delete data during early migration.

Use:

```text
ARCHIVED
DEPRECATED
LEGACY
DISABLED
```

before physical deletion.

## 3. Phase 0 — Current Inventory

Goal:

Document the current DB state.

Tasks:

* export ERD snapshot
* list schemas/tables
* count rows
* extract status distributions
* list FK/indexes
* identify logical relations
* identify active vs prototype tables

Output:

```text
00_DB_ARCHITECTURE_INDEX.md
01_CURRENT_DB_MAP.md
02_SOCIAL_NEWS_CURRENT.md
03_CONTENT_CURRENT.md
04_OCCUPATION_CURRENT.md
05_ADMIN_OPS_CURRENT.md
06_DOMAIN_DATA_CURRENT.md
```

## 4. Phase 1 — Source vs Content Boundary

Goal:

Clarify and enforce the boundary between source candidates and content candidates.

Tasks:

* confirm `content.content_candidate` contract
* verify `raw_ref_table/raw_ref_id`
* prevent duplicate source rows from creating duplicate content rows
* ensure posted items have content publish records
* mark legacy direct news publish path

No direct publish behavior change without approval.

## 5. Phase 2 — Content Publishing Authority

Goal:

Move final publishing ownership to content schema.

Tasks:

* confirm `content.publish_log` as authoritative
* map existing social news publish logs
* ensure Facebook post URL exists on content side
* keep source publish logs as legacy/audit until migration complete

Requires approval before disabling direct news publish.

## 6. Phase 3 — Status Cleanup

Goal:

Separate source processing status, content status, and operation status.

Tasks:

* inventory current status values
* group by meaning
* add new status fields if needed
* backfill status mapping
* update UI labels
* avoid destructive rename at first

## 7. Phase 4 — Dashboard Performance

Goal:

Make dashboard lightweight and stable.

Tasks:

* implement summary/count queries
* limit recent logs
* avoid full table reads
* add indexes if needed
* add frontend cache TTL
* prevent duplicate polling intervals

This phase is low-risk if auth/publisher/scheduler are untouched.

## 8. Phase 5 — Duplicate Signal Model

Goal:

Turn duplicate data from noise into useful topic spread signal.

Tasks:

* classify duplicate type
* consider duplicate_group table
* calculate source diversity
* select representative candidate
* prevent all duplicate rows from becoming content candidates

No candidate deletion.

## 9. Phase 6 — Domain Expansion

Goal:

Connect official and practical domain data to content.

Order:

```text
immigration_info
→ living_info
→ occupation enrichment
→ visa_info
→ employment_info
```

Rules:

* official/legal data starts as review-required
* occupation data needs enrichment
* living data must be practical/source-backed

## 10. Phase 7 — Legacy Deprecation

Goal:

Remove or freeze old paths only after stable replacement.

Tasks:

* mark old columns/tables as deprecated
* remove UI dependency
* remove API dependency
* archive old docs
* delete only after explicit approval

## 11. Phase Report Format

After each phase, update this document with:

```text
date
implemented files
migration files
backfill SQL
verification SQL
row counts before/after
rollback method
open issues
```

## 12. Current Next Step

The next safe step is:

```text
Phase 0 completion
```

Meaning:

* current DB inventory
* actual row counts
* actual status distributions
* actual FK/index list
* current relationship verification

No code behavior changes are required for Phase 0.
