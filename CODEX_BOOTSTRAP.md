# WorkConnect Codex Bootstrap

This file is the short startup rule for Codex in this repository.

## Repository Binding

Primary WorkConnect GitHub repository:

* Repository full name: `marklee929/foreignWorkerJobInfoService`
* Repository URL: `https://github.com/marklee929/foreignWorkerJobInfoService`

When a WorkConnect task uses GitHub, Codex must treat this repository as the default target unless the user explicitly names another repository.

If multiple repositories are available through the GitHub app, Codex must not guess or switch repositories silently.

If the requested task appears to concern WorkConnect but the active GitHub target is not `marklee929/foreignWorkerJobInfoService`, Codex must stop and ask for confirmation or report the mismatch before inspecting or changing anything.

Repository binding is an execution context only. It does not redefine the product purpose, architecture, module ownership, protected areas, or implementation permission.

## Command Routing

When the user says a short task command such as `다음 작업`, `다음 테스크`, `이어서 진행`, `계속 진행`, `다음 큐 진행`, `오늘 작업 진행`, or `!wc-next`, Codex must treat it as `WALKTHROUGH_QUEUE_EXECUTION` unless the user explicitly says not to use walkthrough.

Individual issue-specific requests default to review-only behavior unless the user gives an explicit implementation command. Treat questions like "check this", "why is this happening", duplicate/relevance/category concerns, screenshots, and official notice ZIP/PDF relevance checks as `READ_ONLY_AUDIT`: inspect, explain, and produce `CODE_TASK_CANDIDATE` items instead of editing runtime code.

Implementation may proceed only when the user gives a clear bounded fix command such as `!wc-fix`, "implement", "patch", "fix it", "apply the fix", "make the change", or an explicit AREA/MODE/FOCUS implementation prompt.

## Required Bootstrap Sequence

1. Confirm the GitHub repository target is `marklee929/foreignWorkerJobInfoService` when GitHub is used.
2. Read `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`.
3. Read `DOC/architecture/06_WORK_AREA_REGISTRY.md`.
4. Read today KST `DOC/walkthrough/YYYY-MM-DD - execute prompt.md`.
5. Find the single exact WorkConnect completion marker, or apply the first-run fallback when the execute prompt has no marker yet.
6. Execute only the next queued task below the marker. If the first-run fallback applies, treat the whole execute prompt as the first pending task.
7. Do not touch protected areas unless the task explicitly approves them.
8. Save the final report under `DOC/walkthrough/execution-history/YYYY-MM-DD/`.
9. Update today execute prompt with the result.
10. Move or rewrite the WorkConnect completion marker so the final execute prompt has exactly one marker at the final boundary.
11. If a recurring miss, chat-only report, closeout failure, repository mismatch, or protected-boundary confusion occurred, create or update a correction-loop entry.

## Command Lexicon

* `!wc-next`: execute the next walkthrough task.
* `!wc-audit`: perform read-only audit only.
* `!wc-fix`: implement an approved bounded fix.
* `!wc-close`: close the current task, persist the report, and update the marker.
* `!wc-report`: save or repair a missing report only.

Symbol-only commands such as `!@#$` are discouraged. If used, they must be mapped here to a named command before Codex acts on them.

## GitHub Usage Rule

When the user invokes `@GitHub` for WorkConnect without naming a repository, Codex must use:

```text
marklee929/foreignWorkerJobInfoService
```

Allowed GitHub behavior without explicit implementation approval:

* search files
* inspect repository structure
* inspect commits, issues, or pull requests
* read source code for audit
* produce review reports
* produce `CODE_TASK_CANDIDATE` items

Forbidden GitHub behavior without explicit implementation approval:

* changing files
* committing
* pushing
* opening or merging pull requests
* changing protected areas
* modifying scheduler, publisher, auth, env/secrets, DB migrations, or external API behavior

GitHub repository access does not override `AREA`, `MODE`, protected-area rules, walkthrough rules, or runtime safety rules.

## Completion Marker Rule

The WorkConnect completion marker is `[WC_EXECUTION_COMPLETE]`.

It belongs in execute prompt files only as the boundary marker, on its own line.

Use `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]` in examples.

## First-Run Fallback

* If today execute prompt exists, has no exact marker, and appears to contain one clear pending task starting with `!wc-next`, `!wc-audit`, `!wc-fix`, `PURPOSE FUNCTION:`, `AREA:`, or `MODE:`, Codex should treat the whole file as the first pending task.
* After finishing that first task, Codex must append the execution result and put the exact marker as the final line.
* If the marker is missing but the file contains completed reports, multiple unrelated tasks, or ambiguous history, Codex must stop and report.

## Stop Conditions

Codex must stop and report when:

* the GitHub target repository is unclear or mismatched
* today execute prompt cannot be found when walkthrough execution is required
* the completion marker state is ambiguous
* the task requires protected-area changes without explicit approval
* the task requires guessing `AREA`, `MODE`, or `PURPOSE FUNCTION`
* implementation would silently decide unresolved ownership
* verification cannot be performed
* runtime, scheduler, publisher, auth, env/secrets, DB migration, or external API behavior would be affected without approval
