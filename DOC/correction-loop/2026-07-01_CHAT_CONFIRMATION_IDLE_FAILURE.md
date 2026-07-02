# Correction Loop: Chat Confirmation Idle Failure

## Purpose

Record a recurring harness failure where Codex stopped unattended WorkConnect execution by asking chat-level confirmation after the user had already delegated the task.

## Failed Layer

- execution control
- approval classification
- unattended continuation
- closeout discipline

## Failure Pattern

Codex confused three different approval types:

1. Chat-level confirmation
   - Codex asks "진행할까요?", "적용할까요?", or "예를 눌러주세요."
   - This must not happen after the user has already issued an execution command.

2. Platform/tool approval
   - The Codex app, shell sandbox, or filesystem sandbox asks for permission.
   - Codex must not restate this as a chat question.

3. Required security approval
   - Protected operations such as secrets, destructive DB work, production Telegram send, Facebook publish, scheduler/bot state changes, or writes outside workspace.
   - Codex must stop/report or request the required platform approval.

## Correction

Architecture updated:

- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - Added `Confirmation and Approval Policy`

- `DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md`
  - Added non-idling unattended execution rule
  - Added explicit "do not ask" cases for execution commands

## Required Future Behavior

When the user says:

- `다음 요청 진행`
- `다음 테스크`
- `계속 진행`
- `쭉 진행`
- `!wc-next`

Codex must:

```text
inspect
choose safe bounded path
implement when allowed
verify
write report
update marker when walkthrough-driven
stop only at protected or unsafe boundary
```

Codex must not:

- ask chat-level confirmation
- tell the user which approval option to click
- wait indefinitely when safe authorized work remains

## Recovery Rule

If a platform/tool approval is rejected or unavailable:

```text
record TOOL_APPROVAL_REJECTED or TOOL_WRITE_REJECTED
continue read-only verification/reporting if possible
leave the next executable task clearly queued
do not ask the user to approve in chat
```
