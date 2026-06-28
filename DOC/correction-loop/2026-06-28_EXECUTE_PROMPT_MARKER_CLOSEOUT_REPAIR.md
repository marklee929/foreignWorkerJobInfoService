# Execute Prompt Marker Closeout Repair

## 1. Observation

`DOC/walkthrough/2026-06-28 - execute prompt.md` had queued work below the existing WorkConnect marker and did not end with the exact marker line.

Initial verification showed:

```text
exact_marker_count=1
old_marker_count=0
loose_completion_marker_count=1
final_line=Stop after report.
```

The loose marker came from an inline mention of the exact marker inside the queue instruction.

## 2. Failed Layer

- verification/reporting
- walkthrough closeout
- harness trigger failure

## 3. Repair Performed

- Removed the old marker from the middle of the execute prompt.
- Replaced the inline exact-marker mention with a non-matching instruction phrase.
- Added the exact marker as the final line of the execute prompt.
- Saved the task report under `DOC/walkthrough/execution-history/2026-06-28/`.

Final verification showed:

```text
exact_marker_count=1
old_marker_count=0
loose_completion_marker_count=0
final_line=[WC_EXECUTION_COMPLETE]
```

## 4. Protected Areas

Not touched:

- DB/migration
- publisher
- scheduler
- Telegram runtime behavior
- auth/env/config
- external API behavior
- actual publish/collection execution

## 5. Prevention Rule

When updating a daily execute prompt, do not include the exact WorkConnect marker in prose, examples, comments, or task instructions. Use a non-matching phrase or `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]` for examples.

Closeout verification must check:

- exact marker count = 1
- old marker count = 0
- loose marker count = 0
- boundary placement is correct

Final-line verification applies only when no pending queue remains.

If pending tasks remain, the exact marker must be placed immediately after the last completed task/result and immediately before the first pending task.

## 6. Follow-up Repair

After `TASK 1` completion, the marker was incorrectly moved to the end of the whole queued task list. That made `TASK 2` through later tasks appear completed even though they were still pending.

Repair:

- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md` was updated so final-line marker verification applies only when no pending queue remains.
- `DOC/walkthrough/2026-06-28 - execute prompt.md` was updated so `[WC_EXECUTION_COMPLETE]` sits after `TASK 1` execution result and before `TASK 2`.

Correct interpretation:

```text
completed task and execution result
[WC_EXECUTION_COMPLETE]
pending next task
pending later task
```
