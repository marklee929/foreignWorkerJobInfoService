# WorkConnect DB Architecture Index

## 1. Purpose

This document is the entry point for understanding the current WorkConnect database architecture.

The WorkConnect database supports:

- foreign worker news collection
- content publishing queue
- Facebook publishing logs
- admin dashboard operations
- bot/module runtime control
- occupation dictionary collection
- immigration/living/domain data expansion

The database is already larger than a single news automation database.  
Therefore, the DB should not be understood from one full ERD image alone.

Instead, the DB is documented by domain/schema responsibility.

## 2. Current ERD Snapshot

The current ERD was exported from DBeaver.

Recommended path:

```text
DOC/database/Foreign_Worker_Job_Info_DB.png
```

Because the full ERD is too large, it should be treated as a physical snapshot, not as an implementation guide.

The actual implementation guide is split into schema/domain documents.

## 3. How to Read the DB

The DB should be read in the following order:

```text
admin / ops
→ social_news
→ content
→ occupation
→ domain data
```

The most important architectural boundary is:

```text
source/domain data
→ content candidate
→ external publishing
```

Source/domain tables store collected or normalized data.
The `content` schema stores publishable content candidates and external publishing results.

## 4. Current Reference Documents

| Document                    | Purpose                                                        |
| --------------------------- | -------------------------------------------------------------- |
| `01_CURRENT_DB_MAP.md`      | Whole DB map by schema and responsibility                      |
| `02_SOCIAL_NEWS_CURRENT.md` | Current social news collection and candidate structure         |
| `03_CONTENT_CURRENT.md`     | Current integrated content publishing queue                    |
| `04_OCCUPATION_CURRENT.md`  | Current Employment24 occupation/job dictionary structure       |
| `05_ADMIN_OPS_CURRENT.md`   | Current admin, bot, runtime, auth, and operations DB structure |

## 5. To-Be Reference

| Document                      | Purpose                                           |
| ----------------------------- | ------------------------------------------------- |
| `TO_BE_DB_ARCHITECTURE.md`    | Target DB architecture, content flow, and safe migration roadmap |

## 6. DB Architecture Core Statement

WorkConnect DB separates collected source/domain data from publishable content.

Collected data belongs to domain schemas such as:

* `social_news`
* `occupation`
* `immigration_info`
* `living_info`

Publishable content belongs to:

* `content.content_candidate`
* `content.publish_log`

Operational control belongs to:

* `admin`
* ops/log related tables

Dashboard screens must read summary/status APIs or summary views, not full source tables.

## 7. Current High-Level Schema Groups

### Admin / Ops

Responsible for:

* admin access
* module configuration
* runtime config
* bot state
* environment readiness
* dashboard status
* operation logs

### Social News

Responsible for:

* news source collection
* raw item storage
* normalized news item
* news candidate evaluation
* duplicate detection
* news-specific status tracking

### Content

Responsible for:

* integrated publishable candidates
* source reference mapping
* final message/link data
* Facebook publishing result
* content publishing logs

### Occupation

Responsible for:

* Employment24 job/occupation dictionary
* occupation keyword mapping
* occupation collection logs
* raw API response preservation

### Domain Data

Responsible for future or partial domain-specific data:

* immigration notices
* visa information
* living information
* employment information
* public agency data

## 8. Current Main Concern

The biggest current DB architecture concern is the boundary between:

```text
social_news.candidate
```

and

```text
content.content_candidate
```

The intended direction is:

```text
social_news.candidate = source news candidate
content.content_candidate = final publishable content candidate
```

If `content.content_candidate` becomes only a duplicated copy of `social_news.candidate`, the content hub loses its role.

## 9. Documentation Rule

Current DB documents must describe the database as it exists now.

To-be ideas must be written in separate to-be documents.

Do not mix:

* current behavior
* desired architecture
* migration plan

in the same section.

