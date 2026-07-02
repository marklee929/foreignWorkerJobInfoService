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

## Confirmation and Approval Policy

Codex must separate reasoning confirmation from platform/tool approval.

### Chat-Level Confirmation

Chat-level confirmation means Codex asks the user in conversation:

- "진행할까요?"
- "적용할까요?"
- "예를 눌러주세요."
- "계속할까요?"

This is not allowed when the user has already issued an execution command, including:

- `다음 요청 진행`
- `다음 테스크`
- `계속 진행`
- `쭉 진행`
- `!wc-next`
- an execute prompt with declared `PURPOSE FUNCTION`, `AREA`, and `MODE`

Required behavior:

- proceed without chat-level confirmation when the task is inside the declared `AREA` and `MODE`
- choose the smallest safe implementation path
- record assumptions in the report instead of waiting
- stop only at a protected boundary or unsafe ambiguity

Forbidden behavior:

- waiting all day for user confirmation when a safe path exists
- restating a tool approval prompt in chat
- telling the user which approval option to click
- using "I need confirmation" as a substitute for bounded execution

### Platform or Tool Approval

Platform or tool approval means the Codex app, shell sandbox, filesystem sandbox, or external connector asks for permission before executing an operation.

Codex does not control that prompt. Codex must not convert it into another chat question.

If a platform/tool approval is rejected or unavailable:

```text
classify as TOOL_APPROVAL_REJECTED or TOOL_WRITE_REJECTED
record the attempted change
continue any remaining read-only or already-authorized verification/reporting work
write a stop/partial report only when no safe authorized work remains
do not ask the user to click approval in chat
```

### Required Security Approval

The following still require explicit approval or a stop report:

- external network or dependency installation
- destructive filesystem operation
- writes outside the workspace
- auth/env/secrets/token handling
- production Telegram send
- Facebook publishing
- scheduler/bot state changes
- destructive DB operation or migration

This policy prevents Codex from becoming idle during unattended WorkConnect work while preserving protected boundaries.

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

## Walkthrough Execution Rule

Use this rule when a task asks Codex to execute work from `DOC/walkthrough/` or a daily execute prompt.

This rule controls queue reading, phase execution, completion marker movement, and execution report storage. It does not approve implementation by itself. The declared `PURPOSE FUNCTION`, `AREA`, `MODE`, allowed files, forbidden files, stop conditions, and protected-area rules still apply.

### Root Bootstrap Rule

Codex must read `CODEX_BOOTSTRAP.md` when a user gives a short task command, a walkthrough command, or an explicit WorkConnect command trigger.

Short commands are not casual chat when they match a WorkConnect trigger. They must activate the walkthrough harness unless the user explicitly says not to use walkthrough.

### TRIGGER CARD: WALKTHROUGH_QUEUE_COMMAND

Trigger phrases:

- `다음 작업`
- `다음 테스크`
- `이어서 진행`
- `계속 진행`
- `다음 큐 진행`
- `오늘 작업 진행`
- `!wc-next`

Required behavior:

- treat the request as `WALKTHROUGH_QUEUE_EXECUTION` unless the user explicitly says not to use walkthrough
- read `CODEX_BOOTSTRAP.md`
- read `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
- read today KST `DOC/walkthrough/YYYY-MM-DD - execute prompt.md`
- find the single exact WorkConnect completion marker, or apply `First-Run Execute Prompt Fallback` when the file has no marker yet
- execute only the next queued task below the marker; if first-run fallback applies, execute the whole file as the first pending task
- do not modify protected areas unless explicitly approved
- save the final report to `DOC/walkthrough/execution-history/YYYY-MM-DD/`
- update today execute prompt with the execution result
- move or rewrite the completion marker so the final document has exactly one exact marker at the final boundary
- create or update a correction-loop entry when a recurring miss, harness violation, chat-only report, or closeout failure occurred
- end with the exact completion marker in the execute prompt, not only in chat

Queue-drain override:

- default behavior is one queued task per user turn
- if the user explicitly says to continue until the whole queue/task set is complete, Codex may execute queued tasks sequentially in the same turn
- queue-drain mode does not override task-level `Stop after report` when the next task requires explicit approval, protected areas, destructive DB work, scheduler/publisher/auth/env changes, or unresolved ownership decisions
- after each completed queued task, Codex must save a report and update the execute prompt before proceeding
- if Codex stops on a protected/precondition gate, the marker must remain immediately before the blocked pending task, and the stop reason must be recorded in the report
- queue-drain mode must not mark later pending tasks as complete unless they were actually executed and verified

### TRIGGER CARD: INDIVIDUAL_REQUEST_DEFAULT_REVIEW

Condition:

The user gives an individual issue-specific follow-up, anomaly report, "check this", "is this right", "why is this happening", duplicate/relevance/category question, screenshot-based concern, or similar request, and the user does not explicitly request implementation.

Required behavior:

- treat the request as `READ_ONLY_AUDIT` by default
- inspect and report only
- do not modify runtime code
- do not modify DB objects or run migrations
- do not change scheduler, publisher, Telegram runtime/callback, auth, env/config, or external API behavior
- do not publish or send real external notifications
- if a fix is needed, produce a `CODE_TASK_CANDIDATE` instead of implementing it
- wait for explicit implementation approval before editing runtime behavior

Explicit implementation triggers:

- `!wc-fix`
- "implement"
- "patch"
- "fix it"
- "apply the fix"
- "make the change"
- any clearly bounded implementation prompt with `AREA`, `MODE`, and `FOCUS`

Rules:

- `!wc-audit` always means `READ_ONLY_AUDIT`
- `!wc-fix` permits implementation only inside the declared `AREA` and `MODE`, after pre-review
- ambiguous requests default to `READ_ONLY_AUDIT`, not `GUARDED_FIX`
- if Codex is unsure whether the user wants code changes, stop and ask or produce a review report only

### TRIGGER CARD: OFFICIAL_NOTICE_ATTACHMENT_REVIEW_REQUIRED

Condition:

- a collected official notice contains a ZIP attachment
- the source or menu label implies immigration, foreign employment, or foreign-worker relevance
- generated review content only says generic attachment text such as `attachment exists`
- the system cannot confirm the actual file contents inside the ZIP
- the notice is classified as `IMMIGRATION_INFO / IMMIGRATION_NOTICE` only because of source, menu, or category label

Required behavior:

- do not treat ZIP attachment existence as publishable content
- do not classify the notice as immigration or foreign-worker content only from menu/source label
- do not generate public content from generic attachment-exists text
- do not send or promote the ZIP as a public content artifact before its contents are inspected
- keep the original source notice and ZIP metadata as source evidence
- mark the item as `ATTACHMENT_REVIEW_REQUIRED`, `EVIDENCE_ONLY`, or the closest existing non-public review state
- inspect ZIP metadata first: attachment filename, file size, file extension, source notice title, original notice URL, `bbs_seq`, `bbs_id`, and attachment count when available
- if ZIP contains PDF/HWP/HWPX/DOC/DOCX/XLS/XLSX, inspect or extract text from the actual document before domain classification
- classify based on document content, not source menu alone
- if the document is not about foreign hiring, foreign worker rights, visa, stay status, immigration, employment permit system, or settlement-relevant labor rights, do not promote it as WorkConnect public content

Specific classification guidance:

- K-New Deal Academy or youth training notices are not `IMMIGRATION_INFO` and not `FOREIGN_WORKER_HIRING`; likely `EMPLOYMENT_INFO / TRAINING_PROGRAM`, publishable only if eligibility for foreign residents, international students, or visa holders is confirmed
- small business labor-management, AI labor law consultation, and fake 3.3 contract notices are not `IMMIGRATION_INFO`; they may be `LABOR_RIGHTS` only if they provide practical worker-rights guidance relevant to foreign workers
- generic MOEL press releases must not become public WorkConnect content unless they pass target-user and actionability gates

Attachment review rule:

- ZIP attachments must not be sent repeatedly to Telegram as independent review items if they belong to the same official notice group
- multiple `bbs_seq` items with nearly identical title/source/preview should be audited for attachment-group duplication
- future grouping keys may include `official_notice_key`, `attachment_group_key`, `notice_title_hash`, and `source_name + notice_date + normalized_title`
- until grouping exists, keep such items as review-only or evidence-only and do not publicize them

### TRIGGER CARD: EXECUTION_CLOSEOUT_REQUIRED

Condition:

Codex has completed any `READ_ONLY_AUDIT`, `DOC_ONLY`, `LOW_RISK_FIX`, `GUARDED_FIX`, or approved `PROTECTED_CHANGE` task.

Required closeout:

- the report must not exist only in chat
- save a report file under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
- update today execute prompt when the task is walkthrough-driven or when the user asks to use the daily queue
- verify exact WorkConnect completion marker count is 1 in the execute prompt
- verify legacy decorated completion marker count is 0 in the execute prompt
- verify loose completion marker count is 0 in the execute prompt
- if the execute prompt has remaining pending queue, verify the marker is the boundary immediately before that pending queue
- if the execute prompt has no remaining pending queue, verify the final line is the exact WorkConnect completion marker
- if loose marker count is not 0, repair the execute prompt marker state or record a harness closeout failure
- add a correction-loop entry if any recurring failure or harness miss happened
- state protected areas touched or not touched
- state verification performed

Stop if:

- the report cannot be saved
- the execute prompt cannot be found and the task requires it
- the completion marker state is ambiguous
- closing the task would require guessing

### Command Lexicon

Recommended WorkConnect command triggers:

- `!wc-next`: execute the next walkthrough task
- `!wc-audit`: read-only audit only
- `!wc-fix`: implement an approved bounded fix
- `!wc-close`: close the current task, persist the report, and update the marker
- `!wc-report`: save or repair a missing report only

Symbol-only commands such as `!@#$` are discouraged because they are hard to search, hard to audit, and semantically unclear. If symbol-only commands are used, they must map to a named command in `CODEX_BOOTSTRAP.md` before Codex acts on them.

### Today Execute Prompt Rule

Before executing walkthrough-based work, Codex must locate and read the current KST date execute prompt.

Default filename pattern:

```text
DOC/walkthrough/YYYY-MM-DD - execute prompt.md
```

If the exact filename is not present, search `DOC/walkthrough/` for a file that contains both the current KST date and `execute prompt`.

Rules:

- if the user specifies an execute prompt file, use that file first
- if no matching execute prompt file is found, do not execute phases; write a stop report if a writable report path is allowed
- do not begin phase work before reading the execute prompt file
- do not treat older execute prompt files as today’s queue unless the user explicitly requested one

### Completion Marker Rule

The WorkConnect completion marker is `[WC_EXECUTION_COMPLETE]`.

Rules:

- the execute prompt file must contain exactly one exact WorkConnect completion marker
- the exact marker must appear on its own line
- content before the marker is completed history or same-day record
- content after the marker is the pending execution queue
- if there is no marker, stop and report
- if there is more than one marker, stop and report
- if there is no executable content after the marker, report that the queue is empty
- do not place the exact marker inside examples, comments, archived sections, or code blocks
- use `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]` for examples
- migrate the legacy decorated Korean marker to the WorkConnect marker
- if both legacy and WorkConnect markers exist, preserve only one WorkConnect marker at the execution boundary and archive or rename the legacy marker so it cannot be matched
- verification must include WorkConnect marker count 1, legacy marker count 0, loose marker count 0, and boundary placement
- final-line verification applies only when no pending queue remains
- if pending tasks remain below the completed task, the marker must stay between the last completed task/result and the first pending task
- do not move the marker to the end of the whole queue after completing only one task; that falsely marks pending tasks as completed

### First-Run Execute Prompt Fallback

Use this only for a new daily execute prompt that has not been closed out before.

Condition:

- today's execute prompt exists
- exact WorkConnect completion marker count is 0
- legacy decorated marker count is 0
- loose completion marker count is 0
- the file starts with one clear pending task, such as `!wc-next`, `!wc-audit`, `!wc-fix`, `PURPOSE FUNCTION:`, `AREA:`, or `MODE:`
- the file does not contain completed execution reports, previous closeout sections, or multiple unrelated task prompts

Required behavior:

- treat the whole file as the first pending task
- do not require the user to add an initial marker before the first run
- after task completion, append the execution result to the same execute prompt
- add the exact WorkConnect completion marker after the first completed task/result; use final line only if no pending queue remains
- save the report to `DOC/walkthrough/execution-history/YYYY-MM-DD/`

Stop if:

- the marker is missing and the file has mixed history plus pending work
- the file contains multiple unrelated tasks and no boundary
- the first pending task cannot be identified confidently
### Pending Queue Execution Rule

Codex reads the pending queue from top to bottom.

Rules:

- run `PHASE 1`, `PHASE 2`, `PHASE 3`, and later phases sequentially
- treat each phase as an independent harness task
- before each phase, confirm `PURPOSE FUNCTION`, `AREA`, `MODE`, allowed changes, forbidden changes, verification, and stop conditions
- proceed to the next phase only when the previous phase meets its success criteria
- stop immediately if protected areas are required without explicit approval
- stop if a phase would require deciding unresolved ownership such as Python vs Java workflow ownership or `social_news.candidate` vs `content.content_candidate` ownership
- do not execute unclear phases; report the ambiguity instead

### Completion Marker Move Rule

After all executable phases are completed or safely stopped, update the execute prompt file only when the task allows that file to be modified.

Required final structure:

```text
today's plan / execution / report history

[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]

remaining pending queue
```

If there is no remaining queue, the completion marker must be the final line of the file.

If remaining queue exists, the completion marker must not be the final line. It must be placed immediately after the last completed task/result and immediately before the first pending task.

Rules:

- remove the old completion marker from its previous location
- keep the executed phase prompts and result summaries in the completed history area
- append the completion marker at the boundary between completed history and remaining pending queue
- leave all remaining pending tasks below the marker so the next short command can identify the next task
- do not move the marker during a `DOC_ONLY` harness-rule update unless that task explicitly asks to update the execute prompt file

### Execution History Rule

`DOC/walkthrough/execution-history/` stores actual execution results.

Default daily folder:

```text
DOC/walkthrough/execution-history/YYYY-MM-DD/
```

Example files:

```text
DOC/walkthrough/execution-history/YYYY-MM-DD/PHASED_EXECUTION_REPORT.md
DOC/walkthrough/execution-history/YYYY-MM-DD/phase-01-result.md
DOC/walkthrough/execution-history/YYYY-MM-DD/phase-02-result.md
DOC/walkthrough/execution-history/YYYY-MM-DD/phase-03-result.md
```

Authority boundaries:

- execute prompt files are queue and same-day working record
- `execution-history` is an execution result archive
- `correction-loop` is recurring failure analysis and improvement candidate storage
- `DOC/architecture` is the active rule set
- archive folders are historical snapshots

Codex must not interpret `execution-history` as active permission to implement work.

### Phase Report Storage Rule

After each completed phase, write a phase report when the task allows writing to `DOC/walkthrough/execution-history/`.

File naming:

```text
DOC/walkthrough/execution-history/YYYY-MM-DD/phase-XX-[short-name]-result.md
```

Minimum phase report structure:

```text
# PHASE XX Result

## 1. 결론 요약
## 2. AREA / MODE / PURPOSE FUNCTION
## 3. 수정한 파일
## 4. 검증 결과
## 5. 보호영역 touched 여부
## 6. 재시작 / 재로딩 필요 여부
## 7. 남은 위험
## 8. 다음 CODE_TASK_CANDIDATE
```

### Restart / Reload Report Rule

Every phase report and every `PHASED_EXECUTION` report must include:

```text
## 재시작 / 재로딩 필요 여부

- Backend restart:
  - YES / NO / MAYBE
  - 이유:

- Frontend dev server restart:
  - YES / NO / MAYBE
  - 이유:

- Browser hard refresh:
  - YES / NO / MAYBE
  - 이유:

- DB restart:
  - YES / NO
  - 이유:

- Scheduler/Bot restart:
  - YES / NO / MAYBE
  - 이유:

- External service restart:
  - YES / NO
  - 대상:
  - 이유:

- 사용자가 직접 해야 할 작업:
  1.
  2.
  3.
```

Report language follows the Report Language Rule below. Technical identifiers must remain in their original form.

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
