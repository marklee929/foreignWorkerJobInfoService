# Codex Harness Guide

## Purpose

This document defines how Codex or any automated coding agent should work inside the WorkConnect project.

The goal is not to make Codex work longer.

The goal is to make Codex work safely, within clearly defined boundaries, and stop when the task becomes risky.

Codex must not treat task completion as higher priority than preserving existing system boundaries.

## Core Workflow

Every automated task must follow this flow:

```text
work area selection
-> quick pre-review
-> risk classification
-> proceed or stop
-> limited execution
-> verification
-> report
```

Codex should not start by editing code.

Before execution, Codex must understand:

- what area it is working on
- what files it may touch
- what files it must not touch
- whether the task crosses protected boundaries
- how the result can be verified

## Required Input Format

A harness task should be started with a short structured instruction.

```text
AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
FOCUS: Check whether content candidates have enough subscription value.
TIMEBOX: 60m
```

Required fields:

- AREA
- MODE
- FOCUS
- TIMEBOX

Optional fields:

- ALLOWED FILES
- FORBIDDEN FILES
- SUCCESS CRITERIA
- STOP CONDITIONS
- REPORT TARGET

## Work Modes

### READ_ONLY_AUDIT

Allowed:

- read code
- read documents
- inspect DB queries if safe
- write analysis report

Not allowed:

- modify code
- modify DB
- change config
- change scheduler
- publish externally

### DOC_ONLY

Allowed:

- create or update documentation
- update walkthrough
- update architecture notes

Not allowed:

- modify runtime code
- modify DB
- modify env/config secrets

### LOW_RISK_FIX

Allowed:

- UI labels
- formatting
- display-only changes
- summary/count query improvement
- pagination
- polling cleanup
- non-destructive validation
- documentation updates

Not allowed:

- auth
- Facebook publisher
- scheduler
- bot ON/OFF state transition
- destructive DB migration
- publish selection logic

### GUARDED_FIX

Allowed:

- repository query adjustment
- validation logic
- structured error handling
- content quality gate
- non-destructive DB column/index addition if approved by task
- tests

Requires:

- pre-review
- limited scope
- verification
- report

### PROTECTED_CHANGE

Protected changes require explicit user approval before editing.

Examples:

- admin auth
- device approval
- Facebook token validation
- Facebook publisher
- content publisher
- scheduler
- bot control state
- destructive migration
- env/secret handling

Codex must not perform PROTECTED_CHANGE from an unattended harness run.

## Quick Pre-Review Gate

Before modifying code, Codex must perform quick pre-review.

The pre-review must answer:

- What is the requested AREA?
- What is the requested MODE?
- What is the FOCUS?
- Which documents are relevant?
- Which files are likely involved?
- Which files are forbidden?
- Are protected areas involved?
- Can the task be completed without crossing boundaries?
- What tests or checks can verify the change?

Codex must classify the task as one of:

- SAFE_TO_PROCEED
- PROCEED_WITH_LIMITS
- STOP_REQUIRES_USER_REVIEW

### SAFE_TO_PROCEED

The task can be completed inside the requested area without touching protected areas.

### PROCEED_WITH_LIMITS

The task can proceed, but Codex must explicitly list what it will not touch.

### STOP_REQUIRES_USER_REVIEW

The task is unsafe for unattended automation.

Codex must stop and write a stop report.

## One-Hour Session Cycle

For long-running automation, Codex should work in fixed one-hour sessions.

The purpose of the one-hour session is to prevent uncontrolled long-running changes and make progress easy for the user to inspect.

```text
00:00-00:10  Quick pre-review
00:10-00:40  Development work
00:40-00:50  Development verification
00:50-01:00  Final check, walkthrough update, conditional commit/push, and Telegram summary
```

### 00:00-00:10 Quick Pre-Review

Codex must not edit code during this period.

Codex must inspect:

- requested AREA
- requested MODE
- requested FOCUS
- related architecture documents
- likely files to touch
- forbidden files or protected areas
- possible verification method
- possible stop conditions

At the end of this step, Codex must decide:

- SAFE_TO_PROCEED
- PROCEED_WITH_LIMITS
- STOP_REQUIRES_USER_REVIEW

If the result is STOP_REQUIRES_USER_REVIEW, Codex must stop and write a stop report.

### 00:10-00:40 Development Work

Codex may work only inside the approved AREA and MODE.

During this period, Codex must not expand the task scope.

Codex must not modify protected areas unless the task was explicitly approved as PROTECTED_CHANGE.

If Codex discovers that the task requires another area, it must stop instead of continuing.

### 00:40-00:50 Development Verification

Codex must verify the work before reporting completion.

Depending on the task, verification may include:

- backend server start check
- frontend build or dev server check
- API response check
- unit or smoke test
- UI visual check
- DB read-only validation
- lint or compile check
- log inspection

If verification cannot be performed, Codex must say so clearly in the report.

A task is not complete only because files were edited.

### 00:50-01:00 Final Check and Summary

Codex must prepare a short final summary for the user.

If Telegram reporting is enabled, the backend automation reporter should send the summary to Telegram.

The summary must be compressed and operational.

## Automatic Stop Rule

Codex must stop instead of continuing when:

- the task requires protected-area changes
- the task requires modifying unrelated modules
- the task conflicts with architecture documents
- the task cannot be verified
- the backend cannot restart
- the frontend cannot connect to backend
- an error points outside the current work area
- the fix requires guessing
- the fix would modify auth, Facebook publisher, scheduler, bot state, or destructive migration without approval
- the requested change would undo or overwrite a previous completed task
- the task scope expands beyond the original AREA

A stopped task is not a failure.

A stopped task with a clear report is better than a completed task that damages the system.

## Error Gate

If an error occurs during work, Codex must classify it before fixing.

### Current Area Error

The error is inside the current work area.

Allowed:

- fix inside allowed files
- verify
- continue

### Boundary Error

The error points to another work area.

Required:

- stop
- write report
- do not patch unrelated modules

### Protected Area Error

The error involves:

- admin auth
- Facebook publisher
- token validation
- scheduler
- bot state
- destructive DB migration
- env secrets

Required:

- stop
- write stop report
- wait for user approval

## Boundary Rule

Same file does not mean same responsibility.

If a file contains multiple responsibilities, Codex must only modify the section related to the current work area.

Examples:

- If `admin_server.py` contains dashboard routes and Facebook routes, a dashboard task must not modify Facebook token logic.
- If `Dashboard.vue` contains summary cards and bot controls, a status-card task must not change bot control behavior.

## Stop Report

When Codex stops, it must write a stop report instead of patching blindly.

Recommended path:

```text
DOC/walkthrough/YYYY-MM-DD-stop-report-[area].md
```

Stop report format:

```text
# Stop Report: [AREA]

## Requested Task

## Pre-Review Result

Status: STOP_REQUIRES_USER_REVIEW

## Why Codex Stopped

## Files Inspected

## Files That Would Need Changes

## Protected Areas Involved

## Risk

## Recommended Next Step

## User Decision Needed

Choose one:

- approve protected change
- narrow task scope
- switch to read-only audit
- postpone
```

## Reporting Policy

Codex must not run silently for long periods.

### Pre-Review Report

Within the first 10-15 minutes, before code modification.

```text
HARNESS PRE-REVIEW

AREA:
MODE:
FOCUS:
Risk:
Decision: SAFE_TO_PROCEED / PROCEED_WITH_LIMITS / STOP_REQUIRES_USER_REVIEW

Files inspected:
Files planned to touch:
Forbidden areas:
Protected areas involved:
Test plan:
```

### Checkpoint Report

Every 45-60 minutes during active work.

```text
HARNESS CHECKPOINT

Elapsed:
Current status:
Files modified:
Tests run:
Problems found:
Boundary risk:
Next 30-60min plan:
```

### Phase Report

Every 3 hours or when a meaningful work unit is completed.

```text
HARNESS PHASE REPORT

Completed:
Changed files:
Validation:
Open risks:
Need user decision:
Continue / Stop / Switch mode:
```

### Six-Hour Control Point

Every 6 hours, Codex must stop and produce a compressed report.

Codex should not start a new major phase after the six-hour control point without user review.

```text
HARNESS 6H CONTROL POINT

Time range:
Area:
Mode:
Focus:

Completed:
Changed files:
Tests/checks:
Protected areas touched:
Open risks:
User decisions needed:
Recommended next slot:
```

## Telegram Summary Policy

For long automation runs, Codex or the backend automation reporter should send compressed Telegram summaries every 6 hours.

Telegram report should be short and operational.

Recommended format:

```text
WorkConnect Harness 6H Summary

Area: [AREA]
Mode: [MODE]
Time: YYYY-MM-DD HH24:MI:SS ~ YYYY-MM-DD HH24:MI:SS KST

Done:
- ...

Changed:
- ...

Checks:
- Backend: OK / FAIL / NOT RUN
- Frontend: OK / FAIL / NOT RUN
- Tests: OK / FAIL / NOT RUN

Risk:
- NONE / LOW / MEDIUM / HIGH

Stopped:
- YES / NO
- Reason: ...

Needs user:
- ...
```

Telegram summary must not include:

- raw tokens
- secrets
- full stack traces
- large diffs
- noisy logs
- private credentials

Detailed reports should remain in:

```text
DOC/walkthrough/
```

Telegram should only notify what the user needs to check.

## Conditional Commit/Push Rule

During the final 10 minutes of each session, Codex should commit and push only when all of the following are true:

- the task stayed within the declared AREA
- no protected area was modified without approval
- backend/frontend/test verification passed, or skipped checks are clearly explained
- no known runtime-breaking error remains
- walkthrough was updated
- git diff was reviewed
- the commit message clearly describes the session result

If verification fails, Codex must not push broken work.

Instead, Codex must:

- write a walkthrough report
- write a stop report if needed
- leave changes uncommitted or commit only documentation if safe
- clearly tell the user what failed

## Completion Report

At the end of every task, Codex must report:

- AREA
- MODE
- FOCUS
- pre-review result
- files inspected
- files modified
- tests run
- backend verification result
- frontend verification result
- UI visual verification result if applicable
- protected areas touched or not touched
- stop conditions encountered
- remaining risks
- next recommended task

## Code Task Candidate Rule

During DOC_ONLY automation-preparation sessions, Codex may inspect documents and identify future code work.

Codex must not implement those code changes during DOC_ONLY mode.

When a document review finds a code change, protected-area change, DB change, scheduler change, Facebook publishing change, auth change, or environment/config change that may be needed later, Codex must record it as a candidate instead of editing runtime files.

Required format:

```text
CODE_TASK_CANDIDATE
AREA:
MODE:
FOCUS:
WHY:
RISK:
PROTECTED AREA:
RECOMMENDED NEXT PROMPT:
```

Candidate rules:

- AREA must map to `06_WORK_AREA_REGISTRY.md`.
- MODE must be one of `READ_ONLY_AUDIT`, `LOW_RISK_FIX`, `GUARDED_FIX`, or `PROTECTED_CHANGE`.
- RISK must be `LOW`, `MEDIUM`, `MEDIUM-HIGH`, or `HIGH`.
- PROTECTED AREA must say `YES` or `NO`, with the protected area named when yes.
- The recommended next prompt must be narrow enough for a one-hour harness session.
- If the candidate requires user approval, Codex must state that clearly.

DOC_ONLY sessions should prefer producing accurate candidates over broad implementation plans.

## Human Review Rule

User review is required when:

- protected area change is needed
- Facebook publishing behavior changes
- scheduler behavior changes
- admin auth changes
- destructive migration is proposed
- automation cannot verify server/frontend health
- task scope expands beyond original area
