# Implementation Queue Rule

## Purpose

This document defines how WorkConnect implementation tasks should be queued, executed, verified, rolled back, and closed.

It complements `05_CODEX_HARNESS_GUIDE.md`, `06_WORK_AREA_REGISTRY.md`, and `08_AUTONOMOUS_EXECUTION_POLICY.md`.

## Queue Boundary

Default daily queue:

```text
DOC/walkthrough/YYYY-MM-DD - execute prompt.md
```

The daily queue uses a single machine-readable completion marker. The exact marker must appear only as the boundary line in the execute prompt.

## Mandatory Implementation Precondition

Implementation must not start until:

```text
audit report saved
-> audit report re-read
-> previous same-AREA reports checked
-> implementation plan written
-> protected boundaries confirmed
```

If any step is missing, write a stop or audit report instead of implementing.

## Queue Execution Rule

When the user gives a short next-task command:

```text
1. Read CODEX_BOOTSTRAP.md.
2. Read architecture docs.
3. Read today's execute prompt.
4. Verify marker state.
5. Identify the next pending task.
6. Read same-AREA execution-history.
7. Execute only the allowed scope.
8. Verify.
9. Save report.
10. Update marker boundary.
11. Generate next task.
```

## Six-Phase Long-Running Task Rule

Long-running tasks must be represented as:

```text
PHASE 1: Pipeline/System Audit
PHASE 2: Save Audit Report
PHASE 3: Re-read Audit and Prior History
PHASE 4: Target Architecture / Implementation Plan
PHASE 5: Bounded Implementation
PHASE 6: Verification / Retry / Rollback / Closeout
```

Each phase must save or update a report before the next phase begins.

## Failure Handling

If implementation fails verification:

```text
classify the failure
-> retry within budget if inside AREA/MODE
-> rollback own changes if unsafe or budget exhausted
-> save failed verification report
-> generate the next safer task if possible
```

Do not hide failed verification as success.

## Codex CLI / VS Code Approval Configuration Note

Local Codex approval prompts are tool-runtime prompts. They are not WorkConnect product safety gates.

For long-running local execution, the recommended local Codex configuration is:

```toml
approval_policy = "never"
sandbox_mode = "danger-full-access"
```

Configuration placement:

- Put these keys at the top level of `~/.codex/config.toml`.
- Do not put them inside `[approval]`.
- If using the VS Code Codex extension, configure the extension so it actually uses `~/.codex/config.toml`.
- This document does not modify local config files. It only records the recommended unattended local-runtime setting.

Warning:

Disabling local approval prompts does not authorize WorkConnect protected changes.

The following WorkConnect stop gates remain unchanged:

- auth
- env/secrets/token
- destructive DB
- real external publish
- Telegram production behavior
- Facebook/content publisher
- scheduler/bot state
- external API behavior

Technical edit failures, string replacement failures, and patch application failures are not user-confirmation triggers. Codex must retry with another safe editing method inside the same `AREA` and `MODE` before asking the user or writing a stop report.

## Report Separation Rule

Reports must distinguish:

- audit findings
- design decisions
- implementation changes
- verification results
- rollback/retry results
- remaining risks
- next task

## Marker Verification

After closeout:

- exact marker line count = 1
- marker substring count = 1
- old decorated Korean marker count = 0
- if no pending queue remains, final line is the marker
- if pending queue remains, marker is immediately before the next pending task

Do not place the exact marker in examples. Use:

```text
[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]
```

## Protected Boundaries

Queue execution must not change:

- `ADMIN_AUTH`
- env/secrets/token handling
- destructive DB state
- `FACEBOOK_PUBLISHER`
- `CONTENT_PUBLISHER`
- Telegram production behavior
- scheduler/bot state
- external API behavior

## Commit / Push

Do not commit or push unless explicitly requested or the task explicitly allows it.

## Success Criteria

- Implementation never starts before saved audit/history review.
- Same issue continues from previous findings.
- Verification failures are classified.
- Retry/rollback results are persisted.
- Next task is generated in bounded format.
