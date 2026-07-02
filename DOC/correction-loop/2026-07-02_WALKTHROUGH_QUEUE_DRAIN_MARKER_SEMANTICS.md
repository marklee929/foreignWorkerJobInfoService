# Walkthrough Queue Drain Marker Semantics

Date: 2026-07-02

## Failure

Codex handled the first `!wc-next` block in the daily execute prompt as if it were the whole requested unit of work and inserted `[WC_EXECUTION_COMPLETE]` before later pending `!wc-next` blocks.

The user clarified that:

- `!wc-next` blocks inside one execute prompt are checkpoints.
- A single user request should continue through the last prompt in the file.
- `[WC_EXECUTION_COMPLETE]` belongs only after the final prompt has completed.

## Failed Layer

Harness closeout semantics.

The active rules still described "execute only the next queued task below the marker" and allowed a one-task-per-turn interpretation. That conflicted with the intended queue-drain behavior for WorkConnect walkthrough execution.

## Correction

Updated active harness documents:

- `CODEX_BOOTSTRAP.md`
- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
- `DOC/walkthrough/README.md`

New rule:

- Default WorkConnect walkthrough behavior is queue-drain execution.
- A `!wc-next` block is a checkpoint/task boundary, not a user-turn stop point.
- Intermediate completed blocks must use `[WC_CHECKPOINT]` or normal result headings.
- `[WC_EXECUTION_COMPLETE]` must be written only after the final executable prompt in the active queue has completed.
- If Codex stops before the final prompt, it must record a stop/checkpoint report and avoid writing the exact completion marker.

## Active Prompt Repair

The misplaced intermediate marker in `DOC/walkthrough/2026-07-02 - execute prompt.md` was changed from `[WC_EXECUTION_COMPLETE]` to `[WC_CHECKPOINT]`.

## Future Verification

For every walkthrough closeout, verify:

- exact `[WC_EXECUTION_COMPLETE]` count is 0 when pending prompts remain
- exact `[WC_EXECUTION_COMPLETE]` count is 1 only after the last executable prompt completes
- intermediate results use `[WC_CHECKPOINT]` or normal report headings
- later `!wc-next` blocks are not silently skipped
