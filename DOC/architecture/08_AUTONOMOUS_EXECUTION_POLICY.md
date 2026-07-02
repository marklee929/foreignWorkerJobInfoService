# Autonomous Execution Policy

## Purpose

This document defines how Codex may continue WorkConnect work when the user is absent for long periods.

The goal is not unrestricted autonomy. The goal is bounded autonomy:

```text
preserve purpose
-> inspect before deciding
-> choose safe defaults when possible
-> implement only inside allowed areas
-> verify
-> report
-> generate the next task
-> stop only at protected or unsafe boundaries
```

This document extends `05_CODEX_HARNESS_GUIDE.md`. It does not override protected areas, product purpose, runtime safety, or work-area boundaries.

## Authority

Active governance order:

```text
00_PRODUCT_NORTH_STAR.md
-> 01_SYSTEM_GROWTH_WORKFLOW.md
-> 02_DATA_SOURCE_AND_QUALITY.md
-> 03_SYSTEM_ARCHITECTURE.md
-> 04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
-> 05_CODEX_HARNESS_GUIDE.md
-> 06_WORK_AREA_REGISTRY.md
-> 08_AUTONOMOUS_EXECUTION_POLICY.md
```

`08_AUTONOMOUS_EXECUTION_POLICY.md` controls continuation behavior, decision logging, retry budgets, rollback behavior, and next-task generation.

It must not be used to approve:

- protected area changes
- destructive DB changes
- external publishing behavior
- scheduler/bot state changes
- auth/env/secrets changes
- weakening quality gates

## Autonomy Principle

Codex must not stop merely because a choice is mildly ambiguous.

Codex must inspect architecture, code, tests, prior reports, and current diff before deciding. If a safe default exists inside the declared `AREA` and `MODE`, Codex should proceed and record the decision.

When the user delegates work and may be absent, Codex must optimize for non-idling execution:

- do not ask chat-level confirmation after an execution command has been given
- do not wait for the user when a safe, bounded implementation path exists
- do not turn a platform/tool approval prompt into a chat question
- continue through audit, report, implementation, verification, and closeout until only protected or unsafe work remains
- if a tool approval is rejected, record `TOOL_APPROVAL_REJECTED` or `TOOL_WRITE_REJECTED`, complete any remaining safe verification/reporting, and leave the next executable task clearly queued

Codex must stop when ambiguity affects:

- protected area ownership
- destructive or irreversible operations
- external publishing or notification behavior
- auth/session/security behavior
- DB migration or mass data mutation
- unresolved product purpose conflict
- source legality, privacy, or terms-of-use risk
- implementation ownership such as Python vs Java when a runtime decision would be made silently

## Mandatory Long-Running Cycle

For long-running WorkConnect work, Codex must use this 6-phase cycle:

```text
PHASE 1: Pipeline/System Audit
PHASE 2: Save Audit Report to DOC/walkthrough/execution-history/YYYY-MM-DD/
PHASE 3: Re-read the saved audit report and prior reports for the same AREA
PHASE 4: Build Target Architecture / Implementation Plan from audit findings
PHASE 5: Implement bounded changes from the plan
PHASE 6: Verify, rollback or retry if needed, save closeout report, update marker, generate next task
```

Implementation must not start until:

```text
audit report saved
-> audit report re-read
-> previous same-AREA reports checked
-> implementation plan written
-> protected boundaries confirmed
```

If a previous audit already identified the same issue, Codex must continue from previous findings instead of restarting investigation.

Every audit must produce at least one bounded `CODE_TASK_CANDIDATE`, unless the audit finds no safe next task.

## Decision Ladder

Use this order before asking the user:

```text
1. Read active architecture docs.
2. Read today's execute prompt.
3. Read relevant prior execution reports.
4. Inspect source code and tests for current behavior.
5. Identify protected areas and forbidden files.
6. Choose the smallest safe implementation inside the declared area.
7. Record the decision log.
8. Implement.
9. Verify.
10. If verification fails, retry inside budget or rollback.
11. Report and generate next task.
```

Do not ask the user when:

- the task is `DOC_ONLY`
- the task has declared `AREA`, `MODE`, and `PURPOSE FUNCTION`
- the safe path is already specified by architecture
- failure can be handled by retry, rollback, or stop report
- the user used an execution command such as `다음 요청 진행`, `다음 테스크`, `계속 진행`, `쭉 진행`, or `!wc-next`
- the only uncertainty is a routine implementation choice inside the declared area

Ask or stop only when:

- no safe path exists
- required fields are missing and cannot be inferred from the execute prompt structure
- the task crosses a protected boundary
- execution would publish externally or mutate real data destructively

If Codex would otherwise ask "진행할까요?", it must instead:

```text
inspect current state
choose the smallest safe path
implement inside the declared boundary
verify
write the report
update the marker when walkthrough-driven
```

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

## Decision Log

For every non-trivial choice, write a short decision log in the phase report or final report:

```text
Decision:
Alternatives considered:
Selected option:
Why safe:
Why other options were rejected:
Protected areas avoided:
Verification:
```

Decision logs are required when choosing among:

- multiple implementation files
- Python vs Java ownership
- read-only audit vs guarded fix
- direct code patch vs documentation-only task
- retry vs rollback
- bulk operation vs per-item operation
- new field/table vs existing JSON/log field

## Retry Budget

Default retry budget:

```text
analysis retries: 2
implementation retries: 2
test-fix retries: 3
build retries: 2
report/marker closeout retries: 2
```

Retry rules:

- retry only inside the declared `AREA` and `MODE`
- do not use retries to expand scope
- do not retry external publishing, real Telegram sends, scheduler starts, or destructive DB work
- after budget is exhausted, rollback own changes if safe or write a stop report

## Rollback Policy

If tests fail after a change:

```text
classify failure
-> fix if inside area and retry budget remains
-> rollback own change if failure is outside area or unsafe
-> preserve unrelated user changes
-> write report
```

Allowed rollback:

- revert only Codex-created changes from the current task
- remove generated docs or code from the current task if they are invalid
- restore previous safe behavior inside touched files

Forbidden rollback:

- `git reset --hard`
- reverting user changes
- deleting collected data
- destructive DB cleanup
- stopping bots/schedulers unless explicitly approved

## Verification Policy

Verification must match the task.

For `DOC_ONLY`:

- target documents exist
- required sections exist
- protected boundaries are preserved
- no runtime files changed
- execute prompt marker is valid when walkthrough-driven

For `LOW_RISK_FIX`:

- static checks
- targeted UI/API contract checks
- frontend build if UI changed
- no protected areas touched

For `GUARDED_FIX`:

- compile or syntax check
- targeted tests
- relevant backend/frontend build checks
- no external output
- no destructive DB mutation

If a verification step cannot run, the report must say why and what risk remains.

## Stop Gates

Codex must stop and write a stop report when:

- protected area change is required
- destructive DB operation is required
- real external API call is required for verification
- Facebook publisher or content publisher behavior must change without explicit approval
- Telegram production behavior must change without explicit approval
- scheduler/bot state must change without explicit approval
- auth/env/secrets are involved
- architecture docs conflict in a way that changes product meaning
- unresolved ownership would be decided silently
- tests fail and retry budget is exhausted

## Next Task Generation

After every completed task, Codex must generate the next safe task.

The next task must include:

```text
CODE_TASK_CANDIDATE
AREA:
MODE:
PURPOSE FUNCTION:
FOCUS:
WHY:
ALLOWED:
FORBIDDEN:
VERIFICATION:
STOP CONDITIONS:
```

If the next task is protected, mark it as blocked until explicit approval.

## Completion Rule

When walkthrough-driven:

- save report under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
- update today's execute prompt
- keep exactly one `[WC_EXECUTION_COMPLETE]` marker
- if no pending task remains, marker must be the final line
- if pending tasks remain, marker must be immediately before the next pending task

The report must include restart/reload needs even for documentation-only work.

## Success Criteria

This policy is working when:

- Codex continues safe tasks without repeated confirmation
- protected areas remain protected
- choices are recorded as decision logs
- failed verification leads to retry or rollback, not silent success
- reports are persisted, not only written in chat
- next tasks are generated in executable harness format
- WorkConnect remains a source-backed settlement information platform, not a social posting automation script
