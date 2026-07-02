!wc-fix

PURPOSE FUNCTION:
Upgrade the WorkConnect harness so Codex can continue long-running audit, design, implementation, verification, rollback, and next-task generation without repeatedly asking the user for clarification.

AREA:
CODEX_HARNESS_DOCS + TO_BE_DOCS

MODE:
DOC_ONLY

FOCUS:
Create an autonomous long-term coding pipeline policy for WorkConnect.

TIMEBOX:
120m

READ FIRST:
- DOC/architecture/00_PRODUCT_NORTH_STAR.md
- DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/03_SYSTEM_ARCHITECTURE.md
- DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md

CREATE / UPDATE:
- DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md
- DOC/to-be/09_LONG_TERM_CODING_PIPELINE.md
- DOC/to-be/10_PIPELINE_REAUDIT_PLAN.md
- DOC/to-be/11_SOURCE_COLLECTION_AUDIT_PLAN.md
- DOC/to-be/12_IMPLEMENTATION_QUEUE_RULE.md

REQUIRED CONTENT:
1. User may be absent for long periods.
2. Codex must not stop just because a choice is ambiguous.
3. Codex must inspect architecture, code, tests, and prior reports before deciding.
4. Codex must create a decision log when selecting among alternatives.
5. Codex must implement only inside allowed areas.
6. Codex must test after changes.
7. Codex must rollback or attempt another safe branch when tests fail.
8. Codex must use a retry budget.
9. Codex must stop only for protected areas, destructive risk, external publish risk, or unresolved safety conflict.
10. Codex must generate the next task after each completed task.

FORBIDDEN:
- No runtime code changes
- No DB changes
- No scheduler changes
- No Facebook publisher changes
- No Telegram production behavior changes
- No auth/env/secrets changes
- No external API calls
- No destructive commands

SUCCESS CRITERIA:
- New autonomous execution policy exists.
- Long-term coding pipeline exists.
- Pipeline re-audit plan exists.
- Source collection audit plan exists.
- Implementation queue rule exists.
- Existing protected boundaries are preserved.
- The new policy reduces unnecessary user confirmation requests.
- Reports are written in Korean.
- Technical identifiers remain unchanged.

STOP CONDITIONS:
- If this requires runtime code, stop.
- If this weakens protected boundaries, stop.
- If existing architecture documents conflict, preserve ambiguity and document it.

## Execution Result

- Status: COMPLETE
- AREA: `CODEX_HARNESS_DOCS + TO_BE_DOCS`
- MODE: `DOC_ONLY`
- Report: `DOC/walkthrough/execution-history/2026-07-01/autonomous-execution-policy-doc-only-report.md`
- Created:
  - `DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md`
  - `DOC/to-be/09_LONG_TERM_CODING_PIPELINE.md`
  - `DOC/to-be/10_PIPELINE_REAUDIT_PLAN.md`
  - `DOC/to-be/11_SOURCE_COLLECTION_AUDIT_PLAN.md`
  - `DOC/to-be/12_IMPLEMENTATION_QUEUE_RULE.md`
- Verification:
  - target document creation: PASS
  - runtime code changes: NONE
  - DB/migration changes: NONE
  - scheduler/publisher/auth/env/external API changes: NONE
- Restart / reload:
  - Backend restart: NO
  - Frontend dev server restart: NO
  - Browser hard refresh: NO
  - DB restart: NO
  - Scheduler/Bot restart: NO
  - External service restart: NO

!wc-fix

PURPOSE FUNCTION:
Update the WorkConnect autonomous coding pipeline documents so long-running Codex work must follow the 6-phase cycle: audit, save history, re-read history, design, implement, verify/rollback, closeout, and next-task generation.

AREA:
CODEX_HARNESS_DOCS + TO_BE_DOCS

MODE:
DOC_ONLY

FOCUS:
Rename the long-term pipeline files from 00~03 to 09~12 if needed, then update the documents so implementation cannot begin until the audit report is saved and re-read from execution-history.

TIMEBOX:
120m

READ FIRST:
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md
- DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md
- DOC/to-be/09_LONG_TERM_CODING_PIPELINE.md
- DOC/to-be/10_PIPELINE_REAUDIT_PLAN.md
- DOC/to-be/11_SOURCE_COLLECTION_AUDIT_PLAN.md
- DOC/to-be/12_IMPLEMENTATION_QUEUE_RULE.md

CREATE / UPDATE / RENAME:
- Normalize current long-term pipeline docs to `DOC/to-be/09_LONG_TERM_CODING_PIPELINE.md`
- Normalize current re-audit plan to `DOC/to-be/10_PIPELINE_REAUDIT_PLAN.md`
- Normalize current source collection audit plan to `DOC/to-be/11_SOURCE_COLLECTION_AUDIT_PLAN.md`
- Normalize current implementation queue rule to `DOC/to-be/12_IMPLEMENTATION_QUEUE_RULE.md`
- Update references to old filenames if found.

REQUIRED UPDATES:
1. Add the mandatory 6-phase long-running execution cycle:
   - PHASE 1: Pipeline/System Audit
   - PHASE 2: Save Audit Report to `DOC/walkthrough/execution-history/YYYY-MM-DD/`
   - PHASE 3: Re-read the saved execution-history report and prior reports for the same AREA
   - PHASE 4: Build Target Architecture / Implementation Plan from the audit findings
   - PHASE 5: Implement bounded changes from the plan
   - PHASE 6: Verify, rollback or retry if needed, save closeout report, update marker, generate next task

2. Add a rule:
   Implementation must not start until the audit report has been saved and re-read.

3. Add a rule:
   Before implementation, Codex must read:
   - today’s audit report
   - latest execution-history for the same AREA
   - related previous reports if they exist

4. Add a rule:
   If previous audit already identified the same issue, continue from previous findings instead of restarting investigation.

5. Add a rule:
   Every audit must produce at least one bounded `CODE_TASK_CANDIDATE`, unless the audit finds no safe next task.

6. Add a rule:
   Reports must distinguish:
   - audit findings
   - design decisions
   - implementation changes
   - verification results
   - rollback/retry results
   - remaining risks
   - next task

7. Add a rule:
   If implementation fails verification, Codex must:
   - classify the failure
   - retry within budget if inside AREA/MODE
   - rollback own changes if unsafe or exhausted
   - save the failed verification report
   - generate the next safer task if possible

8. Keep protected boundaries unchanged:
   - no auth changes
   - no env/secrets/token changes
   - no destructive DB work
   - no Facebook/content publisher changes
   - no Telegram production behavior changes
   - no scheduler/bot state changes
   - no external API behavior changes

FORBIDDEN:
- No runtime code changes
- No DB changes
- No scheduler changes
- No Facebook publisher changes
- No Telegram production behavior changes
- No auth/env/secrets changes
- No external API calls
- No destructive commands
- Do not weaken existing stop gates

SUCCESS CRITERIA:
- Files are renamed to 09~12.
- Old filename references are updated or explicitly reported if intentionally preserved.
- 6-phase cycle is documented.
- Audit-save-reread-before-implementation rule is documented.
- Execution-history continuity rule is documented.
- Implementation queue rule requires prior audit/history review.
- Existing protected boundaries remain protected.
- A Korean completion report is saved under execution-history.
- Today’s execute prompt marker remains valid.

STOP CONDITIONS:
- If renaming would break unresolved references that cannot be safely updated, stop and report.
- If any required update conflicts with 05/06/08 protected boundaries, preserve the stronger safety rule and report the ambiguity.
- If runtime code changes are required, stop.

## Execution Result

- Status: COMPLETE
- AREA: `CODEX_HARNESS_DOCS + TO_BE_DOCS`
- MODE: `DOC_ONLY`
- Report: `DOC/walkthrough/execution-history/2026-07-01/autonomous-pipeline-six-phase-update-report.md`
- Updated:
  - `DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md`
  - `DOC/to-be/09_LONG_TERM_CODING_PIPELINE.md`
  - `DOC/to-be/10_PIPELINE_REAUDIT_PLAN.md`
  - `DOC/to-be/11_SOURCE_COLLECTION_AUDIT_PLAN.md`
  - `DOC/to-be/12_IMPLEMENTATION_QUEUE_RULE.md`
- Normalized:
  - misplaced `DOC/architecture/09~12` pipeline docs moved to `DOC/to-be/09~12`
- Verification:
  - target document existence: PASS
  - old filename references: NONE
  - runtime code changes: NONE
  - DB/migration changes: NONE
  - scheduler/publisher/auth/env/external API changes: NONE
- Restart / reload:
  - Backend restart: NO
  - Frontend dev server restart: NO
  - Browser hard refresh: NO
  - DB restart: NO
  - Scheduler/Bot restart: NO
  - External service restart: NO

!wc-next

PURPOSE FUNCTION:
Execute the first complete autonomous WorkConnect development cycle.

The goal is NOT to stop after audit.
The goal is to investigate, design, implement, verify, and continue until all safe implementation tasks are completed.

AREA:
LIVING_DOMAIN
+ SOCIAL_NEWS_COLLECTOR
+ SOCIAL_NEWS_CANDIDATE
+ CONTENT_QUEUE

MODE:
AUTONOMOUS_6_PHASE_EXECUTION

FOCUS:
Find why the Living Information pipeline is not producing enough data and why Telegram Living Information review cards have never reached the operator.

TIMEBOX:
Unlimited until all executable tasks are completed or a protected boundary is reached.

────────────────────────────────────

READ FIRST

- CODEX_BOOTSTRAP.md
- DOC/architecture/*
- DOC/to-be/*
- Today's execute prompt
- Related execution-history
- Related correction-loop

────────────────────────────────────

PHASE 1 — Structure Audit

Perform a complete READ_ONLY_AUDIT.

Inspect:

- source collection
- collectors
- scheduler
- bot runtime
- dry_run
- limit values
- DB flow
- normalized flow
- topic clusters
- content candidates
- Telegram review
- Facebook boundary
- Admin UI

Trace the complete pipeline.

Do NOT guess.

────────────────────────────────────

PHASE 2 — Findings

Identify:

- disconnected pipeline
- dead code
- duplicated flow
- disabled features
- dry-run only logic
- missing scheduler
- missing UI
- bad source
- missing parser
- missing promotion
- missing review

Find the EARLIEST failing lifecycle layer.

────────────────────────────────────

PHASE 3 — Persist Audit

Create execution-history report.

Report:

- pipeline
- findings
- evidence
- inspected files
- failing lifecycle
- CODE_TASK_CANDIDATE

────────────────────────────────────

PHASE 4 — History Review

Read again:

- newly created execution-history
- previous reports
- correction-loop
- previous implementation

Do NOT repeat already completed investigation.

Continue from previous findings.

────────────────────────────────────

PHASE 5 — Target Design

Create or update implementation plan.

Generate implementation priority.

Example:

Priority 1

Reconnect living pipeline

↓

Priority 2

Increase collection sources

↓

Priority 3

Improve pipeline visibility

↓

Priority 4

Improve Telegram review

Only create tasks that are actually required.

────────────────────────────────────

PHASE 6 — IMPLEMENT

THIS PHASE IS MANDATORY.

Do NOT stop after planning.

Immediately implement every executable task that:

- is inside declared AREA
- is LOW_RISK_FIX or GUARDED_FIX
- does not touch protected areas
- can be verified

Implementation loop:

investigate

↓

implement

↓

test

↓

verify

↓

if failed

retry

↓

rollback if necessary

↓

retry another safe solution

↓

verify again

↓

report

↓

continue next task

Continue until:

- every executable task is completed

OR

- only protected tasks remain.

────────────────────────────────────

RETRY POLICY

Use retry budget.

Never stop after first failed implementation.

Retry.

Rollback.

Retry another solution.

────────────────────────────────────

STOP ONLY WHEN

- auth
- env
- secrets
- token
- destructive DB
- scheduler ownership
- Facebook publisher
- Telegram production behavior
- external API behavior
- protected area

Everything else must continue autonomously.

────────────────────────────────────

REPORT

Every completed implementation must generate:

Execution Report

↓

execution-history

↓

next task

↓

continue automatically

────────────────────────────────────

FINAL GOAL

The session is NOT complete after the audit.

The session is complete only when:

✓ Structure understood

✓ Problems identified

✓ Target architecture updated

✓ Runtime implementation executed

✓ Tests completed

✓ Verification completed

✓ Rollback performed if necessary

✓ Reports saved

✓ Next task generated

If executable tasks remain,
continue implementation automatically.

Do not stop after planning.
Do not stop after generating tasks.
Continue until only protected work remains.
## Execution Result

- Status: COMPLETE
- AREA: `LIVING_DOMAIN + CONTENT_QUEUE`
- MODE: `LOW_RISK_FIX`
- Report: `DOC/walkthrough/execution-history/2026-07-01/living-info-admin-prep-cycle-ui-implementation-report.md`
- Implemented:
  - Admin UI `Living info prepare` now calls `POST /api/admin/content/living-info/prep-cycle` through `runLivingInfoPrepCycle({ limit: 100, dryRun: false })`.
  - Result display now shows `prepare` and `sync` counts from the prep-cycle response.
  - Contract test now prevents the UI action from silently falling back to `/living-info/sync` only.
- Verification:
  - `python -m pytest foreign_worker_life_info_collector\tests\test_living_info_manual_sync_endpoint_contract.py foreign_worker_life_info_collector\tests\test_living_info_content_prep_scheduler_contract.py foreign_worker_life_info_collector\tests\test_content_card_preview_dry_run.py -q`: PASS, 15 passed
  - `npm run build`: PASS
- Protected areas:
  - production Telegram send: not modified
  - Facebook publisher: not modified
  - scheduler/bot state: not modified
  - auth/env/secrets/token: not modified
  - DB migration/destructive DB work: not modified
- Restart / reload:
  - Backend restart: NO
  - Frontend dev server restart: YES or Vite hot reload
  - Browser hard refresh: YES
  - DB restart: NO
  - Scheduler/Bot restart: NO
  - External service restart: NO
[WC_EXECUTION_COMPLETE]
