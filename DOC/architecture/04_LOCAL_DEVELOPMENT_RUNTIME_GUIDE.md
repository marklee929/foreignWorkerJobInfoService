# Local Runtime Safety

## Purpose

This document defines runtime safety rules while WorkConnect is operated from a local PC before production deployment.

The local environment is both a development environment and an operations environment. Local changes can affect real data, Telegram notifications, and Facebook public output.

For Codex harness operation, use `05_CODEX_HARNESS_GUIDE.md` and `06_WORK_AREA_REGISTRY.md`. This document controls runtime safety triggers and verification expectations.

## Current Runtime Assumption

Current runtime:

```text
local PC
-> local backend server
-> local admin web UI
-> local PostgreSQL
-> local automation bots/schedulers
-> optional local LLaMA/Ollama
-> external Facebook and Telegram APIs
```

Even when the web/admin system is local, public delivery and operation notifications may be external.

## Core Runtime Rule

A runtime change is not complete because syntax is valid.

A runtime change is complete only when the relevant runtime path is verified and protected areas were not touched unintentionally.

## Local Server Safety

Backend checks should confirm:

- server starts without import or configuration errors
- health/status endpoint responds
- first request does not crash the server
- dashboard load does not crash the server
- unexpected 500 errors are not introduced
- CORS/preflight behavior still works when relevant
- optional endpoint failure is not misclassified as full server failure

Frontend checks should confirm:

- dev server or build works when relevant
- admin page loads
- frontend can call backend APIs
- loading, empty, and error states are reasonable
- polling does not create duplicate loops or heavy repeated calls

## Frontend-Backend Communication Rule

Any change to routes, API client behavior, CORS, headers, auth, response status, or response shape must be verified from both sides.

Check:

- request URL
- HTTP method
- response status
- JSON shape
- CORS headers
- auth/device headers
- frontend error handling
- loading/empty/failure states

`204 No Content` must not be treated as full server disconnection unless that endpoint explicitly means server failure.

## Admin UI Visual Check Rule

Admin UI changes require visual inspection when possible.

Check:

- target screen loads
- layout is not broken
- tables do not overflow unexpectedly
- long text wraps or truncates safely
- buttons and status badges are readable
- Korean labels render correctly
- timestamps are unambiguous
- unrelated screens were not damaged

If visual verification cannot be performed, the task report must say so.

## Runtime Trigger Cards

### Trigger: Backend Crash

Action: stop feature work, identify crash source, classify area, fix only if inside allowed area, restart, verify health.

### Trigger: Frontend Cannot Connect

Action: verify backend health, API URL, CORS, auth/device headers, and endpoint response shape before changing unrelated UI.

### Trigger: Protected Area Appears

Condition: auth, device approval, Facebook publisher, token validation, scheduler, bot state, destructive DB migration, content publisher, env/secrets.

Action: stop and report unless explicitly approved.

### Trigger: External Output Risk

Condition: change could alter Facebook posting, Telegram notification, publish selection, retry, frequency, or public message text.

Action: stop or switch to approved guarded/protected mode.

### Trigger: Local Test Touches Real External Output

Condition: a local test, smoke test, verification step, or manual run could send a real Facebook post, Telegram message, external API request, publish/review notification, or scheduler-triggered external output.

Action: require dry-run, mock mode, sandbox channel, preview-only mode, or explicit user approval before execution. If dry-run/mock mode is unavailable, stop and report.

Do not verify by sending real external output unless explicitly approved. A local server is not automatically safe.

### Trigger: Boundary Error

Condition: error points outside declared AREA or requires another module.

Action: stop and report; do not patch unrelated code.

### Trigger: Silent Degradation

Condition: proposed fix hides failures by returning fake success or empty data.

Action: reject; report explicit degraded status instead.

## Runtime Execution Card

Before runtime code changes:

```text
identify AREA and MODE
-> identify affected screen/API/job/table
-> check protected areas
-> define verification
-> edit only allowed responsibility
-> verify target path
-> report checks and risks
```

If any step is unclear, stop before editing.

## External Output Risk Trigger

Facebook and Telegram integrations may affect real external users.

Do not change without guarded review or explicit protected approval:

- publish frequency
- token validation
- publish payload
- content selection
- retry policy
- Telegram notification structure
- Facebook link/message behavior

Publishing failures must preserve source error details such as Meta error type, code, subcode, message, and `fbtrace_id` when available. Do not collapse all failures into a generic token error.

## Runtime Boundary Error Trigger

Same file does not mean same responsibility.

If a file contains multiple responsibilities, modify only the section related to the declared work area.

Examples:

- a dashboard task must not change Facebook token logic in the same server file
- a status-card task must not change bot control behavior in the same UI file
- a content queue task must not alter scheduler or publisher behavior

## DB Safety Rule

PostgreSQL may contain real collected data and publish history.

Forbidden without explicit approval:

- `DROP TABLE`
- `TRUNCATE`
- bulk `DELETE`
- destructive `ALTER`
- mass status rewrite
- removing publish logs
- removing candidates
- clearing content queues

Preferred first:

- read-only diagnostics
- backup
- nullable additions
- indexes
- archive status
- dry-run backfill
- verification SQL

## Migration Rule

Migrations must be non-destructive first.

Preferred sequence:

```text
add new column/table
-> backfill safely
-> verify counts
-> update UI/API
-> mark old field deprecated
-> remove only after approval
```

Migration reports must include affected tables, before/after row counts when available, rollback plan, and verification SQL.

## Scheduler and Polling Rule

Polling changes must:

- prevent duplicate intervals
- clean up on route leave/unmount
- pause or reduce work when document is hidden when appropriate
- avoid polling heavy list APIs
- use summary endpoints for dashboard
- not treat one optional poll failure as full server failure

Scheduler changes are protected unless explicitly approved.

Do not casually change intervals, cooldowns, bot on/off transitions, loop starts, overlap behavior, or retry failure state.

## Facebook and Telegram External Impact Rule

Facebook is public output.

Telegram is operation control and review/reporting.

Both can affect real operations and must be treated as external-impact paths.

Telegram summaries must not leak secrets, raw tokens, full stack traces, private credentials, or noisy logs.

## Local LLaMA/Ollama Rule

Local LLaMA/Ollama is optional.

The system must distinguish:

- automatic use off
- model unloaded
- Ollama server stopped
- endpoint disconnected
- timeout
- fallback used

Do not start, stop, kill, or require Local LLM unless the task explicitly allows it.

## Completion Report Requirement

Runtime tasks must report:

- task area
- files inspected
- files modified
- backend verification result
- frontend verification result
- API verification result
- UI visual verification result if applicable
- protected areas touched or not touched
- tests/builds run
- remaining risks
- next recommended action

## Stop Rule

Stop and report instead of continuing when:

- backend cannot restart
- frontend cannot connect to backend
- auth is affected unexpectedly
- Facebook/token/scheduler logic must be changed
- DB migration becomes destructive
- UI breaks outside target screen
- error source is outside current work area
- verification cannot be performed
- fixing requires guessing
- protected areas are required without approval

A stopped task with a clear report is better than a completed task that breaks local operations.
