# Codex Harness Guide

## Purpose

This document defines how Codex or any automated coding agent should work inside the WorkConnect project.

The goal is not to make Codex work longer.

The goal is to make Codex work safely, within clearly defined boundaries, and stop when the task becomes risky.

Codex must not treat task completion as higher priority than preserving existing system boundaries.

## Core Principle

Every automated task must follow this flow:

```text
work area selection
→ quick pre-review
→ risk classification
→ proceed or stop
→ limited execution
→ verification
→ report

Codex should not start by editing code.

Codex must first understand:

what area it is working on
what files it may touch
what files it must not touch
whether the task crosses protected boundaries
how the result can be verified
Required Input Format

A harness task should be started with a short structured instruction.

Example:

AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
FOCUS: Check whether content candidates have enough subscription value.
TIMEBOX: 60m

Required fields:

AREA
MODE
FOCUS
TIMEBOX

Optional fields:

ALLOWED FILES
FORBIDDEN FILES
SUCCESS CRITERIA
STOP CONDITIONS
REPORT TARGET
Work Modes
READ_ONLY_AUDIT

Allowed:

read code
read documents
inspect DB queries if safe
write analysis report

Not allowed:

modify code
modify DB
change config
change scheduler
publish externally
DOC_ONLY

Allowed:

create or update documentation
update walkthrough
update architecture notes

Not allowed:

modify runtime code
modify DB
modify env/config secrets
LOW_RISK_FIX

Allowed:

UI labels
formatting
display-only changes
summary/count query improvement
pagination
polling cleanup
non-destructive validation
documentation updates

Not allowed:

auth
Facebook publisher
scheduler
bot ON/OFF state transition
destructive DB migration
publish selection logic
GUARDED_FIX

Allowed:

repository query adjustment
validation logic
structured error handling
content quality gate
non-destructive DB column/index addition if approved by task
tests

Requires:

pre-review
limited scope
verification
report
PROTECTED_CHANGE

Protected changes require explicit user approval before editing.

Examples:

admin auth
device approval
Facebook token validation
Facebook publisher
content publisher
scheduler
bot control state
destructive migration
env/secret handling

Codex must not perform PROTECTED_CHANGE from an unattended harness run.

Quick Pre-Review Gate

Before modifying code, Codex must perform quick pre-review.

The pre-review must answer:

What is the requested AREA?
What is the requested MODE?
What is the FOCUS?
Which documents are relevant?
Which files are likely involved?
Which files are forbidden?
Are protected areas involved?
Can the task be completed without crossing boundaries?
What tests or checks can verify the change?

Codex must classify the task as one of:

SAFE_TO_PROCEED
PROCEED_WITH_LIMITS
STOP_REQUIRES_USER_REVIEW
SAFE_TO_PROCEED

The task can be completed inside the requested area without touching protected areas.

PROCEED_WITH_LIMITS

The task can proceed, but Codex must explicitly list what it will not touch.

STOP_REQUIRES_USER_REVIEW

The task is unsafe for unattended automation.

Codex must stop and write a stop report.

Automatic Stop Rule

Codex must stop instead of continuing when:

the task requires protected-area changes
the task requires modifying unrelated modules
the task conflicts with architecture documents
the task cannot be verified
the backend cannot restart
the frontend cannot connect to backend
an error points outside the current work area
the fix requires guessing
the fix would modify auth, Facebook publisher, scheduler, bot state, or destructive migration without approval
the requested change would undo or overwrite a previous completed task
the task scope expands beyond the original AREA

A stopped task is not a failure.

A stopped task with a clear report is better than a completed task that damages the system.

Stop Report

When Codex stops, it must write a stop report instead of patching blindly.

Recommended path:

DOC/walkthrough/YYYY-MM-DD-stop-report-[area].md

Stop report format:

# Stop Report: [AREA]

## Requested Task

## Pre-Review Result

Status:

```text
STOP_REQUIRES_USER_REVIEW
Why Codex Stopped
Files Inspected
Files That Would Need Changes
Protected Areas Involved
Risk
Recommended Next Step
User Decision Needed

Choose one:

approve protected change
narrow task scope
switch to read-only audit
postpone

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

Example:

If `admin_server.py` contains dashboard routes and Facebook routes, a dashboard task must not modify Facebook token logic.

If `Dashboard.vue` contains summary cards and bot controls, a status-card task must not change bot control behavior.

## Reporting Policy

Codex must not run silently for long periods.

### Pre-Review Report

Within the first 10–15 minutes, before code modification.

Format:

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
Checkpoint Report

Every 45–60 minutes during active work.

Keep it short.

Format:

HARNESS CHECKPOINT

Elapsed:
Current status:
Files modified:
Tests run:
Problems found:
Boundary risk:
Next 30–60min plan:
Phase Report

Every 3 hours or when a meaningful work unit is completed.

Format:

HARNESS PHASE REPORT

Completed:
Changed files:
Validation:
Open risks:
Need user decision:
Continue / Stop / Switch mode:
Six-Hour Control Point

Every 6 hours, Codex must stop and produce a compressed report.

Codex should not start a new major phase after the six-hour control point without user review.

Format:

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
Telegram Summary Policy

For long automation runs, Codex or the backend automation reporter should send compressed Telegram summaries every 6 hours.

Telegram report should be short and operational.

Recommended format:

🧭 WorkConnect Harness 6H Summary

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

Telegram summary must not include:

raw tokens
secrets
full stack traces
large diffs
noisy logs
private credentials

Detailed reports should remain in:

DOC/walkthrough/

Telegram should only notify what the user needs to check.

Completion Report

At the end of every task, Codex must report:

AREA
MODE
FOCUS
pre-review result
files inspected
files modified
tests run
backend verification result
frontend verification result
UI visual verification result if applicable
protected areas touched or not touched
stop conditions encountered
remaining risks
next recommended task
Commit Rule

Codex should not commit blindly after unsafe or partially verified work.

Commit is allowed when:

task stayed within area
verification passed or limitations are clearly documented
no protected area was changed without approval
walkthrough or relevant doc was updated
git status is understood

If verification failed or protected boundaries were crossed, do not commit unless the user explicitly approves.

Human Review Rule

User review is required when:

protected area change is needed
Facebook publishing behavior changes
scheduler behavior changes
admin auth changes
destructive migration is proposed
automation cannot verify server/frontend health
task scope expands beyond original area