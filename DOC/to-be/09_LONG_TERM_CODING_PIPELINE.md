# Long-Term Coding Pipeline

## Purpose

This document defines the long-running WorkConnect coding pipeline for audit, history save, history re-read, design, implementation, verification, rollback, closeout, and next-task generation.

It is a `to-be` execution model. It is not runtime implementation approval by itself.

## Mandatory 6-Phase Cycle

Long-running Codex work must follow this cycle:

```text
PHASE 1: Pipeline/System Audit
PHASE 2: Save Audit Report to DOC/walkthrough/execution-history/YYYY-MM-DD/
PHASE 3: Re-read the saved audit report and prior reports for the same AREA
PHASE 4: Build Target Architecture / Implementation Plan from audit findings
PHASE 5: Implement bounded changes from the plan
PHASE 6: Verify, rollback or retry if needed, save closeout report, update marker, generate next task
```

Implementation must not start until the audit report has been saved and re-read.

## Phase 1 - Pipeline/System Audit

Purpose:

- inspect architecture
- inspect current code
- inspect tests
- inspect prior execution reports
- identify the earliest failing lifecycle stage
- identify protected areas
- produce at least one bounded `CODE_TASK_CANDIDATE`, unless no safe next task exists

Audit output must distinguish:

- current behavior
- evidence
- failure layer
- protected boundary risk
- candidate implementation scope
- verification plan

No runtime implementation should happen in PHASE 1.

## Phase 2 - Save Audit Report

The audit must be saved under:

```text
DOC/walkthrough/execution-history/YYYY-MM-DD/
```

The report must include:

- AREA
- MODE
- PURPOSE FUNCTION
- files inspected
- findings
- decision log
- protected areas
- restart/reload needs
- next `CODE_TASK_CANDIDATE`

Chat-only audit is not enough.

## Phase 3 - Re-Read Execution History

Before implementation, Codex must read:

- today's saved audit report
- latest execution-history for the same `AREA`
- related previous reports if they exist
- current execute prompt
- active architecture docs

If a previous audit already identified the same issue, continue from previous findings instead of restarting investigation.

If prior reports conflict, preserve the ambiguity and use the stronger safety rule.

## Phase 4 - Build Target Architecture / Implementation Plan

The plan must be derived from audit findings.

It must state:

- target behavior
- allowed files
- forbidden files
- protected areas avoided
- data ownership assumptions
- API/UI/DB impact
- verification plan
- rollback plan

If implementation would require unresolved ownership decisions, stop and report.

## Phase 5 - Implement Bounded Changes

Implementation may begin only after:

- audit report exists
- audit report has been re-read
- prior reports for the same AREA have been checked
- target implementation plan exists
- protected boundaries are clear

Implementation rules:

- edit only declared `AREA`
- preserve existing architecture
- prefer preview/dry-run over external output
- prefer existing schema/log fields before migration
- do not weaken content quality gates
- do not publish externally unless explicitly approved

## Phase 6 - Verify / Retry / Rollback / Closeout

If verification passes:

- save closeout report
- update execute prompt result
- move completion marker to the correct boundary
- generate the next task

If verification fails:

```text
classify failure
-> retry within budget if inside AREA/MODE
-> rollback own changes if unsafe or budget exhausted
-> save failed verification report
-> generate next safer task if possible
```

Rollback must affect only Codex-owned changes from the current task. Do not revert user changes.

## Stop Gates

Stop and report when:

- protected area change is required
- destructive DB work is required
- external publish or production notification behavior is required
- scheduler/bot state change is required
- auth/env/secrets change is required
- implementation ownership is unresolved
- verification cannot be performed after retry budget

## Success Criteria

- Audit is saved before implementation.
- Saved audit is re-read before implementation.
- Implementation follows a written plan.
- Verification result is persisted.
- Rollback/retry result is persisted when needed.
- The next task is generated in bounded `CODE_TASK_CANDIDATE` format.
