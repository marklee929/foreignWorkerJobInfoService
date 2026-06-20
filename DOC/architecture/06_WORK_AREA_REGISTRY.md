# Work Area Registry and Module Harness Map

## Purpose

This document defines WorkConnect work areas for Codex harness tasks.

Each work area is a module harness. It inherits product governance from `00`, workflow rules from `01`, quality/classification rules from `02`, system boundaries from `03`, runtime safety from `04`, and agent operation rules from `05`.

## Risk Levels

### LOW

Safe for documentation, read-only reports, display-only UI text, small status presentation improvements, and low-risk non-runtime clarification.

### LOW-MEDIUM

Usually safe with focused scope and verification. Examples: dashboard status display, Telegram summary formatting, content card preview rules.

### MEDIUM

Requires guarded scope and verification. Examples: repository query logic, validation logic, content queue status mapping, candidate quality gates.

### MEDIUM-HIGH

Requires extra review and narrow execution. Examples: Facebook status/error classification, immigration review flows, sensitive domain rules.

### HIGH

Requires explicit user approval. Examples: auth, device approval, Facebook publisher, content publisher, scheduler, bot state, destructive migration, env/secrets, external publishing behavior.

## Governance Inheritance Rule

No work area may override the product constitution.

If a module finds content that is valid but not aligned with WorkConnect purpose, it must downgrade, review, archive, or preserve it as a reference signal instead of promoting it to public content.

## Module Harness Rule

Before work begins, select:

```text
PURPOSE FUNCTION
AREA
MODE
FOCUS
TIMEBOX
```

Then check:

- allowed files
- forbidden files
- protected areas
- verification plan
- stop conditions

## Individual Request Default Rule

When a user gives an individual issue-specific follow-up without an explicit implementation trigger, Codex must treat the task as `READ_ONLY_AUDIT` by default.

Review-only default applies to questions such as:

- whether a displayed candidate is relevant
- why a duplicate or near-duplicate appeared
- whether a category/status/source mapping is correct
- whether a screenshot or Telegram review item looks wrong
- whether an official notice ZIP/PDF should be public content

Implementation requires an explicit bounded trigger such as `!wc-fix`, "implement", "patch", "fix it", "apply the fix", or a prompt with declared `AREA`, `MODE`, and `FOCUS`.

Without that trigger, Codex should inspect, report, and propose `CODE_TASK_CANDIDATE` items instead of editing runtime code.

## Multi-Responsibility File Rule

Same file does not mean same work area.

Codex may modify only the selected responsibility inside a multi-responsibility file.

Large files such as Python admin servers or broad UI views may contain auth, bot controls, Telegram callbacks, LLaMA control, content sync, publishing, cleanup, and dashboards. A task may touch only the declared responsibility.

## Work Modes Reference

- `READ_ONLY_AUDIT`: inspect and report only
- `DOC_ONLY`: documentation changes only
- `LOW_RISK_FIX`: narrow low-risk implementation or display fix
- `GUARDED_FIX`: guarded implementation with verification
- `PROTECTED_CHANGE`: explicit approval required before editing

Reporting language follows `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`. Work reports should be written in Korean, while technical identifiers remain in their original form.

## Protected Areas

Protected areas must not be changed without explicit user approval:

- admin auth
- device approval
- Facebook publisher
- Facebook token handling
- scheduler
- bot state transitions
- content publisher
- destructive DB migration
- env/secrets
- external API behavior
- automatic publishing selection

## Work Areas

### AREA: PRODUCT_DOCS

Purpose: product purpose, constitution, classification worldview.

Allowed files:

```text
DOC/architecture/00_PRODUCT_NORTH_STAR.md
DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
```

Allowed: documentation-only clarification.

Forbidden: runtime code, DB changes, scheduler, publisher, auth, env/config.

Risk: LOW.

### AREA: SYSTEM_ARCHITECTURE_DOCS

Purpose: component ownership, runtime boundary, data flow, governance map.

Allowed files:

```text
DOC/architecture/03_SYSTEM_ARCHITECTURE.md
DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
```

Allowed: documentation-only boundary clarification.

Forbidden: runtime code, DB changes, server process changes, scheduler, Facebook publisher, admin auth.

Risk: LOW.

### AREA: CODEX_HARNESS_DOCS

Purpose: Codex operating harness, stop gates, reporting, work-area registry.

Allowed files:

```text
CODEX_BOOTSTRAP.md
DOC/architecture/05_CODEX_HARNESS_GUIDE.md
DOC/architecture/06_WORK_AREA_REGISTRY.md
DOC/walkthrough/README.md
DOC/walkthrough/execution-history/
DOC/correction-loop/README.md
DOC/correction-loop/
```

Allowed: documentation-only harness rule clarification.

Forbidden: runtime code, DB changes, env/secrets, external API calls, scheduler, commit/push automation behavior.

Risk: LOW.

### AREA: TO_BE_DOCS

Purpose: future plans and implementation candidates that are not approval to implement.

Allowed files:

```text
DOC/to-be/
DOC/walkthrough/ when explicitly allowed
```

Forbidden: runtime implementation, DB schema changes, migrations, scheduler or publisher behavior.

Risk: LOW.

Execution boundary:

- `DOC/walkthrough/` may contain daily execute prompt files and same-day working records.
- Walkthrough-based execution must follow `DOC/architecture/05_CODEX_HARNESS_GUIDE.md` `Walkthrough Execution Rule`.
- `DOC/walkthrough/execution-history/` is an execution result archive, not an active rule source and not implementation permission.
- `execution-history` reports may be read for context, but they do not override `DOC/architecture` or declared `PURPOSE FUNCTION`, `AREA`, `MODE`, allowed files, forbidden files, or stop conditions.
- Report language follows `DOC/architecture/05_CODEX_HARNESS_GUIDE.md` `Report Language Rule`.

### AREA: DASHBOARD_STATUS

Purpose: dashboard summary/status display and lightweight status APIs.

Allowed:

- summary count query
- dashboard cache TTL
- status card labels
- recent status display
- dashboard-related polling cleanup

Forbidden:

- admin auth
- Facebook publisher
- token validation
- scheduler
- bot state transition
- content selection logic
- full list loading in dashboard

Required checks:

- backend health
- dashboard summary API
- admin UI load
- no heavy list API on dashboard load
- polling interval cleanup

Risk: LOW-MEDIUM.

### AREA: ADMIN_AUTH

Purpose: admin login, device approval, sessions, auth headers.

Allowed: only with explicit user approval.

Forbidden in unattended harness:

- auth middleware changes
- device approval changes
- localStorage/session key changes
- admin secret header changes
- CORS auth behavior changes

Risk: HIGH.

Stop: any unrelated task requiring `ADMIN_AUTH` changes must stop.

### AREA: FACEBOOK_STATUS

Purpose: Facebook token/page status display and error classification.

Allowed:

- token status display
- token fingerprint display
- error category mapping
- Meta error logging
- Telegram failure summary formatting
- status endpoint read-only validation

Forbidden:

- token refresh automation
- publish payload changes
- publish frequency changes
- scheduler changes
- raw token storage/logging
- content selection changes

Required checks:

- no raw token in logs
- token type/status shown
- Meta code/subcode/fbtrace_id preserved when available
- failures are not collapsed into generic invalid-token errors

Risk: MEDIUM-HIGH.

### AREA: FACEBOOK_PUBLISHER

Purpose: actual Facebook publishing behavior.

Includes:

- publish payload
- link/message behavior
- retry behavior
- publish frequency
- Page API call
- token usage during publish

Allowed: only with explicit user approval.

Risk: HIGH.

Stop: unattended tasks requiring this area must stop.

### AREA: SOCIAL_NEWS_COLLECTOR

Purpose: news source collection and source evidence preservation.

Allowed:

- source collection bug fix
- URL normalization before raw save
- collector error classification
- source metadata preservation
- discovery source handling

Forbidden:

- content publishing
- Facebook publisher
- scheduler
- admin auth
- content selection beyond source handoff

Risk: MEDIUM.

### AREA: SOCIAL_NEWS_CANDIDATE

Purpose: news candidate normalization, duplicate classification, quality scoring, and user-value classification.

Allowed:

- duplicate type classification
- quality gate
- source relevance scoring
- user need scoring
- system-message contamination blocking
- candidate status mapping

Forbidden:

- direct Facebook publishing
- content publisher execution
- scheduler
- auth

Required checks:

- broken body messages do not become content
- politics/economy/travel/crypto low-relevance items are skipped or lowered
- Google RSS/search links are blocked as final links

Risk: MEDIUM.

### AREA: CONTENT_QUEUE

Purpose: content candidate management, listing, source reference mapping, and manual review state.

Allowed:

- content candidate sync validation
- status display
- source reference mapping
- content readiness checks
- admin list columns
- manual review state

Forbidden:

- automatic publisher execution
- Facebook publisher payload
- scheduler frequency
- auth
- destructive content deletion

Risk: MEDIUM.

### AREA: CONTENT_PUBLISHER

Purpose: automatic or manual content publishing behavior.

Includes:

- auto publish selection
- cooldown
- daily max
- Facebook publish trigger
- publish retry
- final message generation

Allowed: only with explicit user approval unless task is read-only audit.

Risk: HIGH.

Stop: unattended harness must not change `CONTENT_PUBLISHER` behavior.

### AREA: OCCUPATION_DICTIONARY

Purpose: Employment24 occupation/job dictionary collection and display.

Allowed:

- read-only UI improvements
- pagination
- keyword mapping
- enrichment draft fields
- collect log display

Forbidden:

- treating occupation dictionary as job posting
- auto publishing occupation guides without enrichment
- visa eligibility guarantees
- destructive data rewrite

Risk: LOW-MEDIUM.

### AREA: IMMIGRATION_DOMAIN

Purpose: immigration and visa official information.

Allowed:

- source inventory
- official notice display
- collect log display
- review-required status
- source metadata

Forbidden:

- legal certainty generation
- auto publishing official notices without review
- destructive migration
- treating ZIP attachment existence or generic attachment text as publishable immigration content
- classifying an official notice as `IMMIGRATION_INFO` only from source/menu label when document contents are not inspected

Risk: MEDIUM-HIGH.

Execution card: Official Notice Attachment Review Required

Use when an official MOEL/MOJ/HiKorea/EPS notice has ZIP/PDF/HWP/HWPX/DOC/DOCX/XLS/XLSX attachments and the extracted public content is only generic attachment text or source/menu label inference.

Action:

- keep original notice URL and attachment metadata as source evidence
- require attachment metadata review before public content classification
- prefer `ATTACHMENT_REVIEW_REQUIRED`, `EVIDENCE_ONLY`, or closest non-public review state until the document content is inspected
- audit repeated `bbs_seq` items with similar title/source/preview for attachment-group duplication

Do not touch:

- Facebook publisher
- content publisher
- scheduler
- Telegram callback/runtime behavior
- auth/env/config
- external API behavior

This is an architecture/work-area rule only. Do not implement runtime behavior from this card without an approved task.

### AREA: LIVING_DOMAIN

Purpose: living and settlement information.

Allowed:

- category definitions
- source mapping
- guide candidate rules
- admin display

Forbidden:

- publishing unsourced lifestyle content
- treating generic travel content as settlement guide

Risk: MEDIUM.

### AREA: CONTENT_CARD_GENERATION

Purpose: preview and generation rules for content card assets.

Allowed:

- card template config
- card text validation
- generated image output path
- source/date/link display
- language validation
- preview-only generation

Forbidden:

- publishing cards automatically
- changing Facebook publisher payload
- bypassing content candidate approval
- generating public cards directly from raw source
- using internal diagnostic/status text on public cards

Required checks:

- generated card has source/date/link where applicable
- public card text has no diagnostic/status contamination
- generation is preview-only unless a protected publishing task is approved

Risk: LOW-MEDIUM.

### AREA: LLAMA_STATUS

Purpose: Local LLM/Ollama status and optional helper use.

Allowed:

- status display
- fallback status
- timeout display
- manual-off display

Forbidden:

- killing server process
- starting/stopping Ollama without explicit task
- making Local LLM required
- publishing directly from LLM output

Risk: MEDIUM.

### AREA: SCHEDULER_BOT_STATE

Purpose: schedulers, bot on/off, cooldown, recurring jobs.

Allowed: only with explicit user approval unless read-only audit.

Forbidden in unattended harness:

- interval changes
- cooldown changes
- bot on/off transition changes
- starting new loops
- disabling bots after retryable failure
- overlapping same job without explicit locking

Risk: HIGH.

### AREA: TELEGRAM_REPORTING

Purpose: operation summaries, review messages, and harness reports sent to Telegram.

Allowed:

- compressed summary format
- publish failure summary
- stop report notification
- operational status notification

Forbidden:

- approval/reject publishing flow changes
- leaking secrets
- sending full stack traces
- sending raw tokens
- spammy high-frequency reporting

Risk: LOW-MEDIUM.

Execution card: Operation Notification Recurrence Suppression

Use when the same candidate, review identity, status, or failure repeatedly enters Telegram reporting/review.

Action:

- suppress or downgrade repeated operation notifications when stable duplicate identity is available
- log suppression reason
- preserve the first occurrence and latest meaningful state change

Do not touch:

- Facebook publisher
- content publisher
- scheduler frequency
- auth/device approval
- external API behavior

Verify:

- repeated notification is suppressed or clearly classified
- meaningful state changes still notify

This is an architecture/work-area rule only. Do not implement runtime behavior from this card without an approved task.

## Future Audit Targets

### CODE_TASK_CANDIDATE

```text
AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Verify whether content.content_candidate is acting as the final publishable content object or merely duplicating social_news.candidate.
TIMEBOX: 60m
```

Risk: MEDIUM.

Protected area: NO for read-only audit; YES if audit recommends publisher changes.

### CODE_TASK_CANDIDATE

```text
AREA: SYSTEM_ARCHITECTURE_DOCS + CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Clarify Python vs Java workflow ownership for collection, content approval, Telegram review, migrations, and publish boundaries before implementation work.
TIMEBOX: 60m
```

Risk: MEDIUM.

Protected area: NO for read-only audit; YES if implementation requires scheduler, publisher, auth, DB migration, or external API changes.

## Required Checks

Choose checks based on AREA and MODE:

- architecture/doc consistency
- no forbidden files touched
- backend health
- frontend build/load
- target API response
- UI visual inspection
- read-only DB diagnostics
- unit/smoke tests
- no raw token/secret leakage
- no protected area touched
- public content contamination check

## Stop Conditions

Stop and report when:

- task requires protected-area changes without approval
- task requires unrelated module changes
- architecture documents conflict
- ownership is ambiguous and implementation would decide it silently
- backend/frontend verification cannot be performed when required
- runtime error points outside the current area
- fix requires guessing
- auth, Facebook publisher, content publisher, scheduler, bot state, destructive migration, env/secrets, or external API behavior would be affected without approval
- task scope expands beyond declared AREA

A stopped task with a clear report is preferred over a completed task that weakens WorkConnect boundaries.
