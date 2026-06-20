# Walkthrough Queue

## Purpose

`DOC/walkthrough/` stores daily execution prompts, walkthrough records, and same-day task queues for Codex harness runs.

This folder is not the active architecture rule set. Active operating rules remain in `DOC/architecture/`.

## Execute Prompt Files

Daily execute prompt files should use this pattern when possible:

```text
DOC/walkthrough/YYYY-MM-DD - execute prompt.md
```

If the exact filename varies, Codex should look for a file in `DOC/walkthrough/` that contains the current KST date and `execute prompt`.

When the user explicitly names an execute prompt file, that file takes priority.

## Completion Marker

The WorkConnect completion marker is `[WC_EXECUTION_COMPLETE]`.

Meaning:

- content above the marker is completed plan, execution, or report history
- content below the marker is the pending queue
- if there is no content below the marker, there is no pending work

There must be exactly one completion marker in a daily execute prompt file after closeout. If the marker is missing before the first run, Codex may use the first-run fallback below. If the marker is duplicated, Codex should stop and report instead of executing phases.

Safety rules:

- the marker must appear on its own line
- the marker must be the final line when no queue remains
- do not place the exact marker inside examples, comments, archived sections, or code blocks
- use `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]` in examples
- legacy decorated Korean markers and loose marker variants must be archived or renamed so scanners cannot match them

## First-Run Fallback

If today execute prompt exists and has no completion marker yet, Codex should treat the whole file as the first pending task only when:

- the file starts with one clear task command or header such as `!wc-audit`, `!wc-fix`, `PURPOSE FUNCTION:`, `AREA:`, or `MODE:`
- the file does not contain completed reports or mixed history
- there are no duplicate or legacy markers

After the first task completes, Codex must append the execution result and put the exact marker as the final line.

## Short Command Triggers

The following user commands activate walkthrough queue execution unless the user explicitly says not to use walkthrough:

- `다음 작업`
- `다음 테스크`
- `이어서 진행`
- `계속 진행`
- `다음 큐 진행`
- `오늘 작업 진행`
- `!wc-next`

Codex must read `CODEX_BOOTSTRAP.md`, then `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`, then today execute prompt before acting.

Command lexicon:

- `!wc-next`: execute the next walkthrough task
- `!wc-audit`: read-only audit only
- `!wc-fix`: implement an approved bounded fix
- `!wc-close`: close the current task, persist the report, and update the marker
- `!wc-report`: save or repair a missing report only
## Pending Queue

For walkthrough-based execution, Codex must:

1. read `DOC/architecture/` first
2. read the current execute prompt file
3. find the completion marker, or apply first-run fallback when allowed
4. execute only the content below the marker, or the whole file when first-run fallback applies
5. process phases from top to bottom
6. verify and report after each phase
7. proceed to the next phase only when success criteria are met

Protected areas, stop conditions, and declared `PURPOSE FUNCTION`, `AREA`, and `MODE` still control execution.

## Completion Marker Movement

After all executable phases are complete, and only when the task allows editing the execute prompt file, Codex should:

1. remove the old marker
2. keep executed prompts and result summaries in the completed history area
3. place the marker between completed history and remaining pending queue
4. leave the marker as the final line when no queue remains

Closeout is incomplete if the report exists only in chat.

## Execution History

Detailed phase result reports should be stored under:

```text
DOC/walkthrough/execution-history/YYYY-MM-DD/
```

`execution-history` is a result archive. It is not an active rule source and does not grant implementation permission.

## Related Rule Documents

- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`: active Codex harness execution rules
- `DOC/architecture/06_WORK_AREA_REGISTRY.md`: work-area boundaries
- `DOC/correction-loop/`: recurring failure analysis and improvement candidates
