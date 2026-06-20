# WorkConnect Codex Bootstrap

This file is the short startup rule for Codex in this repository.

When the user says a short task command such as `다음 작업`, `다음 테스크`, `이어서 진행`, `계속 진행`, `다음 큐 진행`, `오늘 작업 진행`, or `!wc-next`, Codex must treat it as `WALKTHROUGH_QUEUE_EXECUTION` unless the user explicitly says not to use walkthrough.

Individual issue-specific requests default to review-only behavior unless the user gives an explicit implementation command. Treat questions like "check this", "why is this happening", duplicate/relevance/category concerns, screenshots, and official notice ZIP/PDF relevance checks as `READ_ONLY_AUDIT`: inspect, explain, and produce `CODE_TASK_CANDIDATE` items instead of editing runtime code. Implementation may proceed only when the user gives a clear bounded fix command such as `!wc-fix`, "implement", "patch", "fix it", or an explicit AREA/MODE/FOCUS implementation prompt.

Required bootstrap sequence:

1. Read `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`.
2. Read `DOC/architecture/06_WORK_AREA_REGISTRY.md`.
3. Read today KST `DOC/walkthrough/YYYY-MM-DD - execute prompt.md`.
4. Find the single exact WorkConnect completion marker, or apply the first-run fallback when the execute prompt has no marker yet.
5. Execute only the next queued task below the marker. If the first-run fallback applies, treat the whole execute prompt as the first pending task.
6. Do not touch protected areas unless the task explicitly approves them.
7. Save the final report under `DOC/walkthrough/execution-history/YYYY-MM-DD/`.
8. Update today execute prompt with the result.
9. Move or rewrite the WorkConnect completion marker so the final execute prompt has exactly one marker at the final boundary.
10. If a recurring miss, chat-only report, or closeout failure occurred, create or update a correction-loop entry.

Command lexicon:

- `!wc-next`: execute the next walkthrough task.
- `!wc-audit`: perform read-only audit only.
- `!wc-fix`: implement an approved bounded fix.
- `!wc-close`: close the current task, persist the report, and update the marker.
- `!wc-report`: save or repair a missing report only.

Symbol-only commands such as `!@#$` are discouraged. If used, they must be mapped here to a named command before Codex acts on them.

The WorkConnect completion marker is `[WC_EXECUTION_COMPLETE]`. It belongs in execute prompt files only as the boundary marker, on its own line. Use `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]` in examples.

First-run fallback:

- If today execute prompt exists, has no exact marker, and appears to contain one clear pending task starting with `!wc-next`, `!wc-audit`, `!wc-fix`, `PURPOSE FUNCTION:`, `AREA:`, or `MODE:`, Codex should treat the whole file as the first pending task.
- After finishing that first task, Codex must append the execution result and put the exact marker as the final line.
- If the marker is missing but the file contains completed reports, multiple unrelated tasks, or ambiguous history, Codex must stop and report.
