# DOC_ONLY REPORT: Codex Walkthrough Command Bootstrap

## 1. Pre-Review

- AREA: `CODEX_HARNESS_DOCS + SYSTEM_ARCHITECTURE_DOCS`
- MODE: `DOC_ONLY`
- Risk: LOW
- Protected areas touched: NO
- Files inspected:
  - `C:\Users\이인결\.codex\attachments\d0330bc6-1917-425b-b5a1-2c25b588cbe2\pasted-text.txt`
  - `CODEX_BOOTSTRAP.md`
  - `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  - `DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`
  - `DOC/walkthrough/README.md`
  - `DOC/walkthrough/2026-06-20 - execute prompt.md`
  - `DOC/correction-loop/README.md`
- Files modified:
  - `CODEX_BOOTSTRAP.md`
  - `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  - `DOC/walkthrough/README.md`
  - `DOC/correction-loop/README.md`
  - `DOC/correction-loop/2026-06-20_WALKTHROUGH_CLOSEOUT_MARKER_FAILURE.md`
  - `DOC/walkthrough/2026-06-20 - execute prompt.md`
  - `DOC/walkthrough/execution-history/2026-06-20/codex-walkthrough-command-bootstrap-doc-only-report.md`

## 2. Changes Made

- `CODEX_BOOTSTRAP.md`
  - Added short bootstrap rules for short commands such as `다음 작업`, `계속 진행`, and `!wc-next`.
  - Added command lexicon for `!wc-next`, `!wc-audit`, `!wc-fix`, `!wc-close`, and `!wc-report`.

- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - Added `Root Bootstrap Rule`.
  - Added `TRIGGER CARD: WALKTHROUGH_QUEUE_COMMAND`.
  - Added `TRIGGER CARD: EXECUTION_CLOSEOUT_REQUIRED`.
  - Added command lexicon.
  - Replaced the legacy completion marker rule with the WorkConnect marker rule.

- `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  - Expanded `CODEX_HARNESS_DOCS` allowed files to include bootstrap, walkthrough README, execution-history, and correction-loop docs.

- `DOC/walkthrough/README.md`
  - Replaced the legacy completion marker with the WorkConnect marker rule.
  - Added short command triggers and command lexicon.
  - Added chat-only closeout warning.

- `DOC/correction-loop/README.md`
  - Added `Harness Closeout Failure Rule`.

- `DOC/correction-loop/2026-06-20_WALKTHROUGH_CLOSEOUT_MARKER_FAILURE.md`
  - Recorded the recurring failure pattern: chat-only report or bad marker closeout is incomplete walkthrough execution.

- `DOC/walkthrough/2026-06-20 - execute prompt.md`
  - Migrated the daily execute prompt boundary to the WorkConnect marker.
  - Archived legacy marker references so scanner rules do not match them.
  - Added this DOC_ONLY execution result.

## 3. Trigger Commands Added

- `!wc-next`
- `!wc-audit`
- `!wc-fix`
- `!wc-close`
- `!wc-report`

Short Korean trigger phrases were also added:

- `다음 작업`
- `다음 테스크`
- `이어서 진행`
- `계속 진행`
- `다음 큐 진행`
- `오늘 작업 진행`

## 4. Closeout Rules Added

Closeout is now explicitly incomplete when the final report exists only in chat.

The harness now requires:

- report persistence under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
- daily execute prompt update when the task is walkthrough-driven
- exact marker verification
- correction-loop entry when a recurring miss, chat-only report, or marker closeout failure occurs
- protected-area touched/not-touched statement
- verification performed statement

## 5. Completion Marker Safety

The legacy decorated Korean marker is no longer the active marker.

The active marker is the WorkConnect marker and must appear only as the execute prompt boundary on its own line.

Safety rule:

- examples must use `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]`
- old decorated markers must be archived or renamed
- loose marker variants must be removed
- the final execute prompt line must be the WorkConnect marker when no queue remains

## 6. Verification

- bootstrap document exists or was updated: PASS
- `05_CODEX_HARNESS_GUIDE.md` contains `WALKTHROUGH_QUEUE_COMMAND`: PASS
- `05_CODEX_HARNESS_GUIDE.md` contains `EXECUTION_CLOSEOUT_REQUIRED`: PASS
- command lexicon exists: PASS
- exact completion marker is not duplicated in execute prompt examples: PASS
- protected areas not touched: PASS
- DB/migration not touched: PASS
- scheduler/publisher/auth/env/config not touched: PASS
- external API, actual publish, actual notification not executed: PASS

Execute prompt marker verification after closeout:

- exact `[WC_EXECUTION_COMPLETE]` line count = 1
- old decorated Korean marker line count = 0
- loose completion marker line count = 0
- final line is `[WC_EXECUTION_COMPLETE]`

## 7. Remaining Risks

- Historical docs and archive files may still mention old marker concepts as history. Active execution must use `CODEX_BOOTSTRAP.md`, `05_CODEX_HARNESS_GUIDE.md`, and today execute prompt.
- Some existing docs contain mojibake from earlier encoding issues. This task did not normalize unrelated historical text.
- `!wc-fix` still requires the target task to declare allowed files, forbidden files, and verification; the command alone is not permission to touch protected areas.

## 8. Final Recommendation

Future `다음 작업`, `다음 테스크`, `계속 진행`, or `!wc-next` requests should now reliably trigger the full walkthrough execution and closeout path:

```text
bootstrap
-> architecture harness
-> today execute prompt
-> next queue item
-> execution-history report
-> execute prompt update
-> correction-loop if needed
-> WorkConnect completion marker closeout
```
