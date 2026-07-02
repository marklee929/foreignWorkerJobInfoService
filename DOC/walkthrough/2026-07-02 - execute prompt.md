!wc-next

PURPOSE FUNCTION:
Audit the real collected Living Information data quality before modifying collectors or expanding sources.

AREA:
LIVING_DOMAIN + SOCIAL_NEWS_COLLECTOR + SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE

MODE:
AUTONOMOUS_6_PHASE_EXECUTION

FOCUS:
Use DB/read-only diagnostics first to determine whether current collected living-info data is useful, sufficient, and mappable to Living Information cards. Only after the data-quality audit, implement safe source/collector/API parameter fixes that do not touch protected areas.

TIMEBOX:
Continue until all safe audit and implementation tasks are complete or only protected work remains.

PHASE 1 — DB Data Quality Audit:
Run read-only DB diagnostics for current Living Information-related data.

Inspect counts and samples from:
- social_news.candidate
- living_info.source_item
- living_info.normalized_item
- living_info.topic_cluster
- living_info.topic_cluster_item
- content.content_candidate
- content.publish_log

Check:
- total collected count by day
- living-info related count by day
- source_name distribution
- category distribution
- status / publish_status distribution
- missing source_url / canonical_url / link_url count
- missing body / short summary count
- duplicate URL/title/hash count
- Korea relevance
- foreign resident relevance
- actionability
- card-readiness
- Telegram review eligibility
- why READY_TO_REVIEW count is 0

PHASE 2 — Quality Mapping:
Classify current data into:

- usable living-info card source
- weak but salvageable signal
- community/user-need signal only
- irrelevant generic news
- non-Korea/global reference
- missing URL/body
- duplicate noise
- official/trusted source candidate

For each group, report:
- count
- examples
- reason
- recommended action

PHASE 3 — Source Expansion Audit:
Based on DB evidence, decide whether source expansion is required.

Evaluate expansion candidates:
- official agencies
- local government foreign resident support centers
- Seoul Global Center
- Gyeonggi foreign resident support sources
- NHIS / National Pension / banking / telecom / housing guides
- university international office living guides
- trusted English Korea media
- Reddit
- X / Threads
- other public community signals

Rules:
- official/agency sources may support public guide candidates
- trusted media may support explainers
- community sources are signal-first only
- do not quote personal stories directly
- do not collect private, closed, paywalled, or access-controlled content
- validate factual/legal/visa/labor/medical/financial claims against primary or trusted sources

PHASE 4 — Pipeline Gap Analysis:
Determine which layer needs changes:

- collector keyword/source list
- collector limit
- dry_run flag
- parser/body extraction
- URL normalization
- duplicate classification
- living_info ingestion
- normalized_item creation
- topic_cluster creation
- content_candidate sync
- review eligibility
- Admin UI visibility

Do not guess. Use DB evidence and code inspection.

PHASE 5 — Implement Safe Fixes:
After saving and re-reading the audit report, immediately implement safe fixes if they are inside AREA/MODE and do not touch protected areas.

Allowed safe fixes may include:
- adding read-only diagnostic endpoint or admin display for collection quality
- adding source/collector quality log fields if non-destructive
- increasing manual collector limit if not scheduler frequency
- improving keyword/source list for manual collection
- adding source candidates as configuration/list only
- improving skip reason reporting
- improving URL/body missing classification
- adding tests for mapping and source-quality classification

Do not implement:
- scheduler frequency changes
- Telegram production send
- Facebook/content publisher changes
- auth/env/secrets/token changes
- destructive DB changes
- external API behavior requiring production credentials
- private/community scraping without explicit policy

PHASE 6 — Verify / Rollback / Report:
Run targeted tests and static checks.

Save:
- audit report
- implementation report
- verification result
- next CODE_TASK_CANDIDATE

SUCCESS CRITERIA:
- DB evidence shows where current living-info data is failing.
- Current data quality and card mapping rate are measured.
- READY_TO_REVIEW=0 reason is classified.
- Source expansion necessity is proven or rejected with evidence.
- Reddit/X/Threads/community expansion is classified as signal-first or rejected.
- Safe collector/source/API parameter fixes are implemented if available.
- No external output occurs.
- No protected boundary is touched.

[WC_CHECKPOINT]
completed_at: 2026-07-02
result:
- Saved audit report: `DOC/walkthrough/execution-history/2026-07-02/living-info-data-quality-audit-report.md`
- Saved implementation report: `DOC/walkthrough/execution-history/2026-07-02/living-info-collector-input-expansion-implementation-report.md`
- Root cause classified: current topic-cluster based Living Information path has 0 public-ready clusters; current source evidence is social-news-only, validation-needed, and has 0 primary/official evidence rows.
- Immediate queue reason: `sync_living_info(limit=100)` sees 0 ready topic clusters, so it syncs 0 card candidates.
- Safe fix implemented: expanded manual lifestyle bot collection inputs from 3 broad keywords / fixed `limit=1` to 13 default keywords, default 8 executed, default per-keyword limit 3, while keeping `dry_run=True`.
- Verification: `python -m pytest SRC\foreign_worker_life_info_collector\tests\test_living_info_manual_sync_endpoint_contract.py` passed 6 tests; `python -m py_compile SRC\foreign_worker_life_info_collector\api\admin_server.py` passed.
next_CODE_TASK_CANDIDATE:
- Add a read-only Living Information readiness diagnostic endpoint/panel that shows source count, primary evidence count, would-be topic clusters, public-ready count, and top skip reasons after a prep-cycle dry run.

!wc-next

PURPOSE FUNCTION:
Continue from the existing Living Information data-quality audit and determine whether the low collection volume is caused by pipeline parameters, collector behavior, or weak source/API/RSS coverage.

AREA:
LIVING_DOMAIN + SOCIAL_NEWS_COLLECTOR + SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE

MODE:
AUTONOMOUS_6_PHASE_EXECUTION

FOCUS:
Use the existing data-quality findings first. Then inspect collector parameters, keyword lists, limits, dry_run settings, API/RSS behavior, parser results, duplicate filtering, and source coverage to identify the earliest collection-volume bottleneck. Implement safe fixes if they are inside the declared AREA and do not touch protected areas.

READ FIRST:
- latest Living Information data-quality audit report
- latest execution-history reports for LIVING_DOMAIN / SOCIAL_NEWS_COLLECTOR / CONTENT_QUEUE
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/to-be/11_SOURCE_COLLECTION_AUDIT_PLAN.md
- current collector code
- current admin_server bot/prep-cycle code
- current tests related to living-info collection and sync

PHASE 1 — Parameter Audit:
Inspect:
- dry_run defaults
- limit values
- keyword count
- per-keyword limit
- collector run frequency assumptions
- source filters
- category mapping
- duplicate thresholds
- missing URL/body gates
- parser fallback behavior

Report whether each parameter is:
- safe
- too restrictive
- test-only
- production-blocking
- unknown

PHASE 2 — Source/API/RSS Audit:
Inspect each current source path:
- Google News
- Naver News
- official/public sources if present
- RSS/API connectors
- trusted media paths
- community signal paths if present

For each source, report:
- expected volume
- actual saved volume
- body availability
- URL quality
- duplicate rate
- parser failure rate
- WorkConnect relevance
- card mapping potential

PHASE 3 — Bottleneck Classification:
Classify the low-volume cause as one or more:

- `PARAMETER_TOO_LOW`
- `DRY_RUN_ONLY`
- `SOURCE_TOO_NARROW`
- `QUERY_TOO_GENERIC`
- `QUERY_TOO_RESTRICTIVE`
- `RSS_OR_API_LOW_SIGNAL`
- `PARSER_FAILURE`
- `BODY_MISSING`
- `URL_INVALID`
- `DUPLICATE_OVERFILTER`
- `QUALITY_GATE_TOO_STRICT`
- `LIVING_INFO_MAPPING_GAP`
- `REVIEW_ELIGIBILITY_GAP`

PHASE 4 — Safe Implementation:
After saving and re-reading the audit report, implement safe fixes immediately when possible.

Allowed safe fixes:
- increase manual collection limit
- expand keyword list for manual living-info collection
- separate Korean/English living-info keyword groups
- add source-specific diagnostics
- improve skipped reason logging
- expose collector result counts in Admin UI/logs
- add read-only diagnostic endpoint
- add source candidates as config/list only
- add tests for parameter and source-quality classification

Forbidden:
- scheduler frequency changes
- production Telegram send
- Facebook/content publisher behavior
- auth/env/secrets/token changes
- destructive DB changes
- live external publishing
- private/closed community scraping
- external API behavior requiring new credentials

PHASE 5 — Verification:
Run targeted tests and static checks.

Verify:
- no external output
- no protected areas touched
- new parameter/source diagnostics are visible
- tests cover changed behavior
- low-volume cause is explicitly classified

PHASE 6 — Report and Next Task:
Save:
- parameter/source audit report
- implementation report if changes were made
- verification result
- next CODE_TASK_CANDIDATE

SUCCESS CRITERIA:
- It is clear whether the bottleneck is parameters, source/API/RSS quality, parser/body extraction, duplicate filtering, or mapping.
- At least one safe implementation is completed if available.
- If source expansion is required, produce a concrete source expansion task with source list and rules.
- No protected boundary is touched.

[WC_CHECKPOINT]
completed_at: 2026-07-02
result:
- Saved parameter/source bottleneck audit: `DOC/walkthrough/execution-history/2026-07-02/living-info-parameter-source-bottleneck-audit.md`
- Confirmed bottlenecks: `PARAMETER_TOO_LOW`, `SOURCE_TOO_NARROW`, `QUERY_TOO_GENERIC`, `RSS_OR_API_LOW_SIGNAL`, `LIVING_INFO_MAPPING_GAP`, `REVIEW_ELIGIBILITY_GAP`.
- Confirmed non-primary causes: `DRY_RUN_ONLY`, `DUPLICATE_OVERFILTER`, and `URL_INVALID`.
- Safe implementation was already completed in the previous checkpoint: expanded manual lifestyle bot keywords and configurable per-keyword limit while keeping `dry_run=True`.
- Verification remains: 6 targeted contract tests passed and `admin_server.py` compiled successfully.
next_CODE_TASK_CANDIDATE:
- Add a read-only Living Information readiness diagnostic endpoint/panel showing source evidence, topic-cluster dry-run readiness, public-ready count, and skip reasons.

!wc-next

PURPOSE FUNCTION:
Create the implementation design goals from the completed Living Information audit before runtime implementation begins.

AREA:
LIVING_DOMAIN
+ SOCIAL_NEWS_COLLECTOR
+ SOCIAL_NEWS_CANDIDATE
+ CONTENT_QUEUE
+ TO_BE_DOCS

MODE:
DOC_ONLY

FOCUS:
Convert the completed audit findings into a concrete implementation architecture and development roadmap.

The audit has already been completed.

Do NOT repeat the investigation.

Continue only from the saved execution-history and audit reports.

TIMEBOX:
120m

READ FIRST:

- Latest execution-history
- Latest audit reports
- Latest correction-loop
- DOC/architecture/*
- DOC/to-be/*
- Current implementation reports

────────────────────────────

PHASE 1

Read all audit findings.

Summarize only the confirmed findings.

Ignore already solved items.

────────────────────────────

PHASE 2

Group findings into implementation themes.

Examples:

Source Collection

Pipeline

Parser

Normalization

Topic Cluster

Candidate Mapping

Telegram Review

Admin UI

Monitoring

Testing

Do not create implementation yet.

────────────────────────────

PHASE 3

For every finding create:

Current State

↓

Problem

↓

Target State

↓

Implementation Goal

↓

Expected Verification

Example

Current

Living collector produces
1 raw/day

↓

Target

30~50 raw/day

↓

Verification

Daily raw count
>=30

────────────────────────────

PHASE 4

Build the implementation roadmap.

Prioritize.

Priority 1

Critical

↓

Priority 2

High

↓

Priority 3

Medium

↓

Priority 4

Future

Every task must include

WHY

EXPECTED EFFECT

RISK

VERIFICATION

────────────────────────────

PHASE 5

Create Target Architecture.

Include:

Current pipeline

↓

Target pipeline

↓

New collectors

↓

New source categories

↓

New diagnostics

↓

New monitoring

↓

New Admin UI

↓

Expected Living Card Flow

────────────────────────────

PHASE 6

Create executable implementation queue.

Break every implementation into

LOW_RISK_FIX

GUARDED_FIX

PROTECTED_CHANGE

Each task must be independently executable.

Each task must contain

AREA

MODE

PURPOSE FUNCTION

SUCCESS CRITERIA

STOP CONDITIONS

VERIFICATION

────────────────────────────

DO NOT

Implement runtime code.

Do not modify DB.

Do not touch Scheduler.

Do not touch Telegram production.

Do not touch Facebook.

This task ends with

Implementation Design

NOT implementation.

────────────────────────────

OUTPUT

Generate

Implementation Design Report

Development Roadmap

Target Architecture

Implementation Queue

Next executable task list

────────────────────────────

SUCCESS CRITERIA

The completed audit has been fully converted into:

✓ Development goals

✓ Architecture goals

✓ Implementation roadmap

✓ Prioritized queue

✓ Executable LOW_RISK_FIX tasks

✓ Executable GUARDED_FIX tasks

No runtime code should be changed in this task.

[WC_CHECKPOINT]
completed_at: 2026-07-02
result:
- Saved implementation design and roadmap: `DOC/walkthrough/execution-history/2026-07-02/living-info-implementation-design-roadmap.md`
- Converted audit findings into implementation themes: source collection, diagnostics, normalization/evidence classification, topic readiness, candidate mapping, and testing.
- Produced prioritized roadmap and executable queue.
- Selected next highest-priority safe task: read-only Living Information readiness diagnostic endpoint/panel foundation.
- No runtime code, DB object, scheduler, Telegram production, or Facebook behavior was changed in this DOC_ONLY block.

!wc-next

PURPOSE FUNCTION:
Implement the completed Living Information development design and roadmap.

AREA:
LIVING_DOMAIN + SOCIAL_NEWS_COLLECTOR + SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE

MODE:
AUTONOMOUS_6_PHASE_EXECUTION

FOCUS:
Use the completed design report and implementation queue to start development. Do not stop on ambiguity. Investigate, choose the safest bounded path, implement, verify, retry or rollback if needed, then write the final report.

TIMEBOX:
Continue until all safe executable tasks from the design are completed or only protected tasks remain.

READ FIRST:
- Latest Living Information implementation design report
- Latest development roadmap
- Latest target architecture
- Latest implementation queue
- Latest audit reports
- Latest execution-history for same AREA
- DOC/architecture/*
- DOC/to-be/*

PHASE 1 — Design Review:
Read the completed design and queue.
Do not repeat the audit unless the design is missing evidence.

PHASE 2 — Select Implementation Task:
Pick the highest-priority task that is:
- inside declared AREA
- LOW_RISK_FIX or GUARDED_FIX
- independently verifiable
- not protected

PHASE 3 — Implement:
Modify only the required files.
If ambiguity appears:
- inspect code
- inspect tests
- inspect prior reports
- choose the smallest safe path
- record decision log
- continue

Do not ask the user.

PHASE 4 — Verify:
Run targeted checks:
- py_compile / pytest for Python
- npm run build if Admin UI changed
- static contract checks
- no external output
- no protected boundary touched

PHASE 5 — Failure Handling:
If implementation fails:
- classify the failure
- retry inside budget
- rollback own change if unsafe
- try another safe solution
- continue

Do not stop at first failure.

PHASE 6 — Report / Continue:
Save implementation report under:

DOC/walkthrough/execution-history/YYYY-MM-DD/

Report must include:
- implemented task
- files changed
- decision log
- verification result
- failed attempts
- retry/rollback result
- protected areas untouched
- remaining risks
- next task

Then continue to the next safe implementation task.

STOP ONLY WHEN:
- auth/env/secrets/token is required
- destructive DB change is required
- scheduler/bot state change is required
- Telegram production behavior is required
- Facebook/content publisher behavior is required
- external API behavior requiring credentials is required
- all remaining tasks are protected
- retry budget is exhausted and rollback cannot produce a safe state

FORBIDDEN:
- No production Telegram send
- No Facebook publish
- No scheduler frequency change
- No auth/env/secrets/token changes
- No destructive DB mutation
- No private/closed community scraping
- No broad refactor outside declared AREA

SUCCESS CRITERIA:
- At least the highest-priority safe implementation task is completed.
- More safe tasks are completed automatically if available.
- Tests/checks pass or failed attempts are rolled back.
- Final report is saved.
- Next executable task is generated.
- Codex does not stop merely because implementation details are ambiguous.

final_result:
- Saved final implementation report: `DOC/walkthrough/execution-history/2026-07-02/living-info-readiness-diagnostics-and-source-registry-implementation-report.md`
- Implemented read-only endpoint: `/api/admin/content/living-info/readiness-diagnostics`
- Added readiness skip reason aggregation: `missing_primary_evidence`, `readiness_score_below_threshold`, `validation_status_not_ready`, `missing_trusted_evidence`, `missing_source_evidence`
- Added Admin UI readiness display and API client call.
- Added official/public Living Information source registry as list/config only.
- Verified current DB readiness diagnostic: `seen_count=58`, `cluster_count=55`, `public_ready_count=0`, top reasons `missing_primary_evidence=55`, `readiness_score_below_threshold=55`.
- Verification passed: targeted pytest 9 passed, combined targeted pytest 20 passed, Python compile checks passed, Admin UI `npm run build` passed.
- Stopped before official/public collector dry-run preview because it introduces guarded external HTTP collection behavior.
next_CODE_TASK_CANDIDATE:
- `GUARDED_FIX`: Implement an official/public Living Information collector dry-run preview from the source registry with mocked collector tests and no credentials, scheduler changes, Telegram/Facebook output, or private/closed scraping.

[WC_EXECUTION_COMPLETE]
