# Codex Harness Engine

## Purpose

This document defines how Codex or any automated coding agent must operate inside WorkConnect.

The goal is not to make Codex work longer. The goal is to make Codex reason safely, preserve product purpose, stay inside declared boundaries, verify changes, and stop when risk exceeds the task.

## Mandatory Architecture-First Rule

Future Codex work must start from `/DOC/architecture` and declared:

```text
PURPOSE FUNCTION
AREA
MODE
```

Codex must not start from source code unless the architecture boundary is already known.

Architecture documents are governance, not background reading.

## Harness Definition

A harness is not a long instruction document.

A harness is a cognitive and operational architecture that controls Codex's reasoning path before editing.

It provides:

- purpose function before implementation
- work-area routing
- trigger cards for intervention
- execution cards for repeated operations
- correction loop before patching
- protected boundaries
- verification and reporting rules

A good harness prevents WorkConnect from losing purpose as complexity increases.

## Required Input Format

Every harness task should start with:

```text
PURPOSE FUNCTION:
AREA:
MODE:
FOCUS:
TIMEBOX:
SUCCESS CRITERIA:
STOP CONDITIONS:
```

Optional fields:

- ALLOWED FILES
- FORBIDDEN FILES
- VERIFICATION PLAN
- REPORT TARGET

If `PURPOSE FUNCTION`, `AREA`, or `MODE` is missing, Codex must not edit files.

Allowed behavior when required fields are missing:

- read `DOC/architecture`
- perform `READ_ONLY_AUDIT`
- ask for clarification
- produce a stop or pre-review report

Forbidden behavior when required fields are missing:

- modifying files
- running migrations
- changing runtime behavior
- guessing the task identity and proceeding with edits

## Work Modes

### READ_ONLY_AUDIT

Allowed:

- read documents
- read code
- inspect safe read-only queries if explicitly allowed
- write an analysis report

Not allowed:

- modify code
- modify DB
- change config
- change scheduler
- publish externally

### DOC_ONLY

Allowed:

- create or update documentation in allowed paths
- archive or restructure documentation when requested
- record future code candidates

Not allowed:

- modify runtime code
- modify DB
- run migrations
- change env/config/secrets
- start or stop services

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
- content publisher selection
- scheduler
- bot on/off state transition
- destructive DB migration

### GUARDED_FIX

Allowed with pre-review and verification:

- repository query adjustment
- validation logic
- structured error handling
- content quality gate
- non-destructive DB column/index addition when explicitly approved
- tests

### PROTECTED_CHANGE

Requires explicit user approval before editing.

Protected examples:

- admin auth
- device approval
- Facebook token validation
- Facebook publisher
- content publisher
- scheduler
- bot control state
- destructive migration
- env/secret handling
- external API behavior

Codex must not perform `PROTECTED_CHANGE` from an unattended harness run.

## Quick Pre-Review Gate

Before modifying files, Codex must answer:

- What is the purpose function?
- What is the requested AREA?
- What is the requested MODE?
- Which architecture docs control the task?
- Which files may be touched?
- Which files or sections are forbidden?
- Are protected areas involved?
- Is the task current-area, boundary, or protected?
- How can the result be verified?

## Risk Decision

Classify every task as:

- `SAFE_TO_PROCEED`
- `PROCEED_WITH_LIMITS`
- `STOP_REQUIRES_USER_REVIEW`

### SAFE_TO_PROCEED

The task can be completed inside the declared area without touching protected areas.

### PROCEED_WITH_LIMITS

The task can proceed only with explicit limits. Codex must state what it will not touch.

### STOP_REQUIRES_USER_REVIEW

The task is unsafe for unattended automation. Codex must stop and report.

## Trigger Card Format

Use trigger cards to decide when the harness must intervene.

```text
TRIGGER CARD: [Name]
Condition:
Action:
Do not touch:
Verify:
Stop if:
```

Examples:

- invalid final link
- source body missing
- generic politics/economy/travel/crypto topic
- Facebook publisher touched
- scheduler interval touched
- auth/device approval touched
- destructive DB operation requested
- same item repeatedly enters Telegram review

## Execution Card Format

Use execution cards to compress repeated operational rules.

```text
EXECUTION CARD: [Name]
Use when:
Steps:
Allowed files/areas:
Forbidden files/areas:
Verification:
Report:
```

Execution cards should be short enough to apply during pre-review.

## Correction Loop Rule

When an output is wrong, Codex must classify the failed lifecycle stage before patching:

```text
source discovery
-> raw collection
-> normalization
-> duplicate classification
-> domain classification
-> user value evaluation
-> review eligibility
-> public delivery
```

Patch the earliest failing layer.

Do not patch one URL, one title, or one post if the real failure is classification, validation, duplicate identity, review eligibility, or publisher boundary.

## Multi-Responsibility File Boundary Rule

Same file does not mean same responsibility.

Codex may modify only the selected responsibility inside a multi-responsibility file.

Examples:

- If `admin_server.py` contains dashboard routes, auth, bot controls, Telegram callbacks, LLaMA control, content sync, publishing, cleanup, and reposting, a dashboard task must not change publisher or auth sections.
- If a UI file contains status cards and bot controls, a status display task must not change bot state behavior.
- If a Java service includes content generation and scheduler behavior, a content display task must not change scheduled execution.

If section boundaries are unclear, stop or narrow the task.

## Multi-Responsibility File Section Map Execution Card

Use when:

- target file contains multiple responsibilities
- target section is unclear
- protected and non-protected responsibilities are near each other

Steps:

```text
identify responsibilities inside the file
-> mark protected sections
-> mark allowed section for declared AREA
-> mark forbidden adjacent sections
-> define verification for selected section only
-> stop if section boundaries are unclear
```

Do not:

- treat file-level access as permission to edit all responsibilities
- modify protected sections because they are nearby
- use one successful check as proof that unrelated responsibilities are safe

## One-Hour Session Cycle

For long-running automation, use fixed one-hour sessions:

```text
00:00-00:10  Quick pre-review
00:10-00:40  Limited execution
00:40-00:50  Verification
00:50-01:00  Final check, report, conditional commit/push if allowed
```

Do not start a major new phase at the end of a session.

## Stop Report

When Codex stops, it must report instead of patching blindly.

Recommended format:

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
```

Do not create a stop-report file unless the task allows writing that path.

## Reporting Policy

## Report Language Rule

Codex work reports, interim updates, stop reports, and final reports should be written in Korean.

Technical identifiers must remain in their original form.

Do not translate:

- file path
- folder path
- code
- function name
- class name
- DB table / column name
- API endpoint
- enum / status code
- AREA
- MODE
- PURPOSE FUNCTION
- Git branch
- commit hash
- error code
- raw log message
- external service name used as identifier

Good examples:

- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`에 Required Input Rule을 보강했습니다.
- `PURPOSE FUNCTION`, `AREA`, `MODE`가 없으면 파일 수정 금지 규칙을 추가했습니다.
- 다음 작업은 `CONTENT_QUEUE` 영역의 `READ_ONLY_AUDIT`가 안전합니다.

Bad examples:

- Translating identifiers such as `PURPOSE FUNCTION`, `AREA`, or `MODE` into Korean.
- Changing file names or status codes into Korean.
- Paraphrasing raw log messages instead of preserving the original text.

### Pre-Review Report

Before modification, report:

```text
AREA:
MODE:
PURPOSE FUNCTION:
Risk:
Decision:
Files inspected:
Files planned to touch:
Forbidden areas:
Protected areas involved:
Verification plan:
```

### Checkpoint Report

For long active work, report every 45-60 minutes:

```text
Elapsed:
Current status:
Files modified:
Checks run:
Problems found:
Boundary risk:
Next plan:
```

### Completion Report

At the end, report:

- AREA
- MODE
- PURPOSE FUNCTION
- pre-review result
- files inspected
- files modified
- tests/checks run
- backend verification result if applicable
- frontend verification result if applicable
- UI visual verification result if applicable
- protected areas touched or not touched
- stop conditions encountered
- remaining risks
- next recommended task

## Telegram Summary Policy

For long automation runs where Telegram reporting is explicitly enabled, summaries should be short and operational.

Telegram summaries must not include:

- raw tokens
- secrets
- full stack traces
- large diffs
- noisy logs
- private credentials

## Conditional Commit/Push Rule

Commit and push only when explicitly requested or allowed by the task and all are true:

- work stayed inside declared AREA
- no protected area was modified without approval
- verification passed or skipped checks are clearly explained
- diff was reviewed
- commit message describes the actual session result

Do not push broken or unverified protected work.

## Completion Report

Every task must end with a concise report that distinguishes:

- what was inspected
- what was changed
- what was verified
- what was intentionally not touched
- what ambiguity remains
- what next task is safest

Task completion must never be treated as more important than preserving WorkConnect boundaries.
