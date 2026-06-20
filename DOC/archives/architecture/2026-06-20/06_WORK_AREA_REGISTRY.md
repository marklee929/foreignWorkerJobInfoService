# Work Area Registry

## Purpose

This document defines WorkConnect work areas for Codex harness tasks.

Each work area defines:

- purpose
- allowed files
- forbidden files
- allowed changes
- forbidden changes
- risk level
- required checks
- stop conditions

Codex must use this document before starting any automated task.

## Risk Levels

### LOW

Safe for unattended or semi-attended harness runs.

Examples:

- documentation
- UI label changes
- read-only reports
- pagination
- summary query optimization

### MEDIUM

Allowed with guarded fix mode and verification.

Examples:

- repository query logic
- validation logic
- content queue status mapping
- non-destructive migration

### HIGH

Requires user approval.

Examples:

- auth
- Facebook publisher
- scheduler
- bot state
- destructive migration
- external publishing behavior

## AREA: PRODUCT_DOCS

Purpose: Product direction and architecture documentation.

Allowed files:

```text
DOC/architecture/00_PRODUCT_NORTH_STAR.md
DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
DOC/architecture/03_SYSTEM_ARCHITECTURE.md
```

Allowed changes:

- documentation only
- clarify product purpose
- clarify system flow
- clarify data quality rules

Forbidden changes:

- runtime code
- DB migration
- env/config
- scheduler
- publisher

Risk level: LOW

## AREA: DB_ARCHITECTURE_DOCS

Purpose: Database reference and to-be architecture documentation.

Allowed files:

```text
DOC/database/
```

Allowed changes:

- DB documentation
- ERD reference
- current/to-be notes
- migration roadmap notes

Forbidden changes:

- actual migration execution
- DB deletion
- schema modification
- code changes unless explicitly requested

Risk level: LOW

## AREA: SYSTEM_ARCHITECTURE_DOCS

Purpose: System architecture, runtime boundary, data-flow, and component responsibility documentation.

Allowed files:

```text
DOC/architecture/03_SYSTEM_ARCHITECTURE.md
DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
DOC/walkthrough/
```

Allowed changes:

- clarify component ownership
- document runtime boundaries
- document source-to-content-to-publishing flow
- record architecture conflicts and future code candidates

Forbidden changes:

- runtime code
- DB migration
- server process changes
- scheduler changes
- Facebook publisher changes
- admin auth changes

Risk level: LOW

## AREA: CODEX_HARNESS_DOCS

Purpose: Codex harness operation rules, session cycle, stop gates, reporting format, and automation-preparation workflow.

Allowed files:

```text
DOC/architecture/05_CODEX_HARNESS_GUIDE.md
DOC/architecture/06_WORK_AREA_REGISTRY.md
DOC/walkthrough/
```

Allowed changes:

- clarify quick pre-review rules
- clarify stop report rules
- clarify code task candidate format
- clarify session and six-hour reporting rules
- document protected areas and required approvals

Forbidden changes:

- runtime code
- DB changes
- environment or secret files
- external API calls
- scheduler changes
- commit/push automation code

Risk level: LOW

## AREA: TO_BE_DOCS

Purpose: Future-state plans and implementation candidates that are not yet approved for code work.

Allowed files:

```text
DOC/to-be/
DOC/walkthrough/
```

Allowed changes:

- add TODO notes
- add deprecation notes
- classify future work candidates
- align future plans with current architecture and DB boundaries

Forbidden changes:

- implementing the future plan
- changing source code
- changing DB schema
- running migrations
- changing scheduler or publisher behavior

Risk level: LOW

## AREA: DESIGN_ARCHIVE_DOCS

Purpose: Legacy design review, archive/deprecated notes, and reference asset classification.

Allowed files:

```text
DOC/design/
DOC/archives/
DOC/walkthrough/
```

Allowed changes:

- mark old design docs as superseded or deprecated
- record which current document absorbs each design
- keep images, zip files, videos, and deck assets as reference assets

Forbidden changes:

- deleting reference assets without explicit instruction
- changing runtime code
- changing DB schema
- changing publish or scheduler behavior

Risk level: LOW

## AREA: DASHBOARD_STATUS

Purpose: Dashboard summary/status display and lightweight status APIs.

Allowed files:

```text
SRC/foreign_worker_life_info_collector/api/*dashboard*
SRC/foreign_worker_life_info_collector/admin_ui/src/*Dashboard*
SRC/foreign_worker_life_info_collector/admin_ui/src/stores/*dashboard*
SRC/foreign_worker_life_info_collector/admin_ui/src/components/*Status*
```

Allowed changes:

- summary count query
- dashboard cache TTL
- status card label
- recent status display
- polling cleanup related to dashboard summary

Forbidden changes:

- admin auth
- Facebook publisher
- token validation
- scheduler
- bot state transition
- content selection logic
- full list loading in dashboard

Risk level: LOW-MEDIUM

Required checks:

- backend health
- dashboard summary API
- admin UI load
- no heavy list API on dashboard load
- polling interval cleanup

## AREA: DASHBOARD_LOGS

Purpose: Recent logs displayed in dashboard/admin UI.

Allowed changes:

- recent log limit
- log display formatting
- log level labels
- log pagination
- operation log read-only queries

Forbidden changes:

- pipeline execution logic
- scheduler logic
- bot state transition
- auth
- publisher

Risk level: LOW

## AREA: ADMIN_AUTH

Purpose: Admin login, device approval, session, auth headers.

Allowed changes: only with explicit user approval.

Forbidden in unattended harness:

- changing auth middleware
- changing device approval logic
- changing localStorage/session keys
- changing admin secret headers
- changing CORS auth behavior

Risk level: HIGH

Stop condition: any unrelated task requiring ADMIN_AUTH changes must stop.

## AREA: FACEBOOK_STATUS

Purpose: Facebook token/page status display and error classification.

Allowed changes:

- token status display
- token fingerprint display
- error category mapping
- Meta error logging
- Telegram failure summary formatting
- status endpoint read-only validation

Forbidden changes:

- token refresh automation
- changing actual publish payload
- changing publish frequency
- changing scheduler
- storing raw access token
- changing content selection

Risk level: MEDIUM-HIGH

Required checks:

- no raw token in logs
- token type/status shown
- Meta code/subcode/fbtrace_id preserved if available
- failed publish is not collapsed into generic invalid token

## AREA: FACEBOOK_PUBLISHER

Purpose: Actual Facebook publishing behavior.

Allowed changes: only with explicit user approval.

Includes:

- publish payload
- link/message behavior
- retry behavior
- publish frequency
- Page API call
- token usage during publish

Risk level: HIGH

Stop condition: any unattended task requiring FACEBOOK_PUBLISHER changes must stop.

## AREA: SOCIAL_NEWS_COLLECTOR

Purpose: News source collection.

Allowed changes:

- source collection bug fix
- URL normalization before raw save
- collector error classification
- source metadata preservation
- discovery source handling

Forbidden changes:

- content publishing
- Facebook publisher
- scheduler
- admin auth
- content selection beyond source handoff

Risk level: MEDIUM

## AREA: SOCIAL_NEWS_CANDIDATE

Purpose: News candidate normalization, duplicate classification, scoring.

Allowed changes:

- duplicate type classification
- quality gate
- source relevance scoring
- user need scoring
- system-message contamination blocking
- candidate status mapping

Forbidden changes:

- direct Facebook publishing
- content publisher execution
- scheduler
- auth

Risk level: MEDIUM

Required checks:

- broken body messages do not become content
- political/economy low relevance items are skipped or lowered
- Google RSS final links are blocked

## AREA: CONTENT_QUEUE

Purpose: Content candidate management and listing.

Allowed changes:

- content candidate sync validation
- status display
- source reference mapping
- content readiness checks
- admin list columns
- manual review state

Forbidden changes:

- automatic publisher execution
- Facebook publisher payload
- scheduler frequency
- auth
- destructive content deletion

Risk level: MEDIUM

## AREA: CONTENT_PUBLISHER

Purpose: Automatic or manual content publishing.

Allowed changes: only with explicit user approval unless task is read-only audit.

Includes:

- auto publish selection
- cooldown
- daily max
- Facebook publish trigger
- publish retry
- final message generation

Risk level: HIGH

Stop condition: unattended harness must not change CONTENT_PUBLISHER behavior.

## AREA: OCCUPATION_DICTIONARY

Purpose: Employment24 occupation/job dictionary collection and display.

Allowed changes:

- read-only UI improvements
- pagination
- keyword mapping
- enrichment draft fields
- collect log display

Forbidden changes:

- treating occupation as job posting
- auto publishing occupation guides without enrichment
- visa eligibility guarantees
- destructive data rewrite

Risk level: LOW-MEDIUM

## AREA: IMMIGRATION_DOMAIN

Purpose: Immigration/visa official information.

Allowed changes:

- source inventory
- official notice display
- collect log display
- review-required status
- source metadata

Forbidden changes:

- legal certainty generation
- auto publishing official notices without review
- destructive migration

Risk level: MEDIUM-HIGH

## AREA: LIVING_DOMAIN

Purpose: Living/settlement information.

Allowed changes:

- category definitions
- source mapping
- guide candidate rules
- admin display

Forbidden changes:

- publishing unsourced lifestyle content
- treating generic travel content as settlement guide

Risk level: MEDIUM

## AREA: LLAMA_STATUS

Purpose: Local LLM/Ollama status and optional helper use.

Allowed changes:

- status display
- fallback status
- timeout display
- manual off display

Forbidden changes:

- killing server process
- starting/stopping Ollama without explicit task
- making Local LLM required
- publishing directly from LLM output

Risk level: MEDIUM

## AREA: SCHEDULER_BOT_STATE

Purpose: Schedulers, bot ON/OFF, cooldown, recurring jobs.

Allowed changes: only with explicit user approval unless read-only audit.

Forbidden in unattended harness:

- changing intervals
- changing cooldown
- changing bot ON/OFF transition
- starting new loops
- disabling bots after retryable failure
- overlapping same job without lock

Risk level: HIGH

## AREA: TELEGRAM_REPORTING

Purpose: Operation summaries and harness reports sent to Telegram.

Allowed changes:

- 6-hour compressed summary format
- publish failure summary
- stop report notification
- operational status notification

Forbidden changes:

- approval/reject publishing flow
- leaking secrets
- sending full stack traces
- sending raw tokens
- spammy high-frequency reporting

Risk level: LOW-MEDIUM

Recommended report frequency:

- checkpoint: local/walkthrough
- telegram compressed summary: every 6 hours
- urgent stop report: immediately
