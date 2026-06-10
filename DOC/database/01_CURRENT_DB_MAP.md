# 01_CURRENT_DB_MAP.md

```md
# Current DB Map

## 1. Purpose

This document describes the current WorkConnect database at schema level.

It does not define the final target architecture.  
It records the current DB map so future changes can be made safely.

## 2. Current DB Role

The current DB supports several different responsibilities at once:

```text
admin operation
news automation
content publishing
occupation dictionary
immigration/living/domain expansion
logging and runtime status
````

Because these responsibilities are mixed in one physical database, schema-level separation is required to understand the current system.

## 3. Current Schema Groups

### 3.1 admin / ops group

Purpose:

* admin UI support
* bot/module control
* runtime settings
* environment status
* dashboard state
* operational logs
* auth/device approval if present

Expected table types:

* module config
* runtime config
* env status
* bot status
* admin auth/session/device
* dashboard/log tables

Risk level:

```text
HIGH
```

Reason:

Admin/auth/runtime tables can break login, bot control, scheduler, and dashboard status.

### 3.2 social_news group

Purpose:

* collect news
* normalize news
* create/evaluate candidate
* track duplicate/skipped/ready/posted states
* keep news pipeline cycle logs

Expected table types:

* pipeline cycle
* pipeline step log
* pipeline error log
* raw item
* normalized item
* candidate
* publish log
* telegram notify log

Risk level:

```text
MEDIUM-HIGH
```

Reason:

This schema affects news collection and candidate generation.
If direct Facebook publishing still exists here, publisher-related changes become HIGH risk.

### 3.3 content group

Purpose:

* hold final publishable content candidates
* connect content candidate back to source rows
* store publishing result
* operate integrated publishing queue

Expected table types:

* content_candidate
* publish_log

Risk level:

```text
HIGH
```

Reason:

This schema is becoming the final publishing hub.
Changes here can affect automatic Facebook posting.

### 3.4 occupation group

Purpose:

* store Employment24 job and occupation dictionary data
* store keyword mappings
* store raw API response and collect logs

Expected table types:

* job_info
* occupation_info
* keyword_mapping
* collect_log
* raw_api_response

Risk level:

```text
LOW-MEDIUM
```

Reason:

This is mostly reference/dictionary data.
It should not directly publish content without enrichment.

### 3.5 domain data group

Purpose:

* store immigration/living/visa/employment/public information
* support future content generation
* preserve official notices and life information

Expected schema examples:

* immigration_info
* living_info
* visa_info
* employment_info

Risk level:

```text
MEDIUM
```

Reason:

Some domain data may later feed content publishing.
Official notices can be legally sensitive and should not be auto-published without validation.

## 4. Current Physical ERD

The full current ERD is stored as a snapshot image.

```text
DOC/database/snapshots/Foreign_Worker_Job_Info_DB.png
```

The full ERD should be used to verify physical structure only.

For implementation planning, use domain-specific current documents.

## 5. Current Logical Data Flow

The intended current logical flow appears to be:

```text
external source
→ raw source row
→ normalized row
→ domain candidate
→ content candidate
→ publish log
```

For social news:

```text
news collector
→ social_news.raw_item
→ social_news.normalized_item
→ social_news.candidate
→ content.content_candidate
→ content.publish_log
```

For occupation:

```text
Employment24 API
→ occupation.raw_api_response
→ occupation.job_info / occupation.occupation_info
→ occupation.keyword_mapping
→ future enrichment
→ future content.content_candidate
```

For immigration:

```text
official source
→ immigration_info.official_notice
→ content.content_candidate
```

## 6. Current Relationship Types

The DB has two kinds of relationships.

### Physical FK

Actual DB-level foreign keys.

These are safe to infer from the ERD or DDL.

### Logical Relation

Relations based on columns such as:

* `raw_ref_table`
* `raw_ref_id`
* `source_domain`
* `content_type`
* `candidate_id`
* `normalized_item_id`
* `cycle_id`

Logical relations must be documented separately because they may not be enforced by DB FK constraints.

## 7. Current Architecture Problems to Verify

The following problems must be verified from actual DB metadata and row counts.

### 7.1 Source vs Content Boundary

Check whether `content.content_candidate` is a final publishing object or only a copied news row.

### 7.2 Duplicate Candidate Growth

Check whether `social_news.candidate` contains many duplicate rows without proper grouping.

### 7.3 Raw / Normalized / Candidate Count Mismatch

Check whether raw and normalized rows are fewer than candidate rows.

### 7.4 Publish Log Ownership

Check whether publish logs exist in both:

```text
social_news.publish_log
content.publish_log
```

If both exist, define which one is authoritative.

### 7.5 Date Meaning Confusion

Check whether the UI displays `updated_at` as if it were source publication or collection time.

Required date meanings:

* original published date
* collected date
* content created date
* content updated date
* published date

### 7.6 Status Value Fragmentation

Check whether `status`, `publish_status`, `content_status`, and bot status values overlap or conflict.

### 7.7 Dashboard Query Risk

Check whether dashboard APIs query full source tables instead of summary/count queries.

## 8. Current DB Documentation Rule

This document should not include target design decisions except where marked as “to be verified.”

Target architecture belongs to:

```text
10_TO_BE_DB_ARCHITECTURE.md
11_TO_BE_CONTENT_FLOW.md
12_MIGRATION_ROADMAP.md
```
