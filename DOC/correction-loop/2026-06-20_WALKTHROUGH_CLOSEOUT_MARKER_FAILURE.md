# Correction Loop: Walkthrough Closeout Marker Failure

## Purpose

This correction-loop entry records a recurring harness closeout failure:

- report output can be left only in chat
- daily execute prompt can retain old or duplicate completion markers
- completion marker closeout can be skipped after a task appears complete

This file is correction-loop material only. It does not approve code changes, DB changes, scheduler changes, publisher changes, Telegram runtime changes, auth changes, env/config changes, external API behavior changes, actual collection, or actual publishing.

## Failed Layer

- verification/reporting
- walkthrough closeout
- harness trigger failure

## Observed Failure Pattern

Codex may correctly analyze or implement a task but miss the harness closeout sequence when the user gives a short command or when the task output is delivered in chat.

The failure becomes visible when:

- no report file is saved under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
- today execute prompt is not updated
- the completion marker is not moved to the final boundary
- legacy decorated marker lines remain in the active execute prompt
- multiple marker-like lines remain matchable by scanners

## Reusable Improvement

Promote explicit closeout trigger cards into the active harness:

- `TRIGGER CARD: WALKTHROUGH_QUEUE_COMMAND`
- `TRIGGER CARD: EXECUTION_CLOSEOUT_REQUIRED`

The active bootstrap must also define short commands:

- `!wc-next`
- `!wc-audit`
- `!wc-fix`
- `!wc-close`
- `!wc-report`

## Marker Rule

The legacy decorated Korean marker must no longer be used as the active execution boundary.

The active execute prompt boundary is the WorkConnect marker.

Examples must use `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]`, not the exact active marker.

## Verification Checklist

For walkthrough-driven work, closeout verification must include:

- report file saved
- today execute prompt updated
- exact WorkConnect marker count is 1
- legacy decorated marker count is 0
- loose marker count is 0
- final line is the WorkConnect marker when the queue is empty
- protected areas touched/not touched stated

## Protected Areas Not Touched

- DB/migration
- Facebook publisher
- content publisher
- scheduler
- Telegram runtime/callback behavior
- auth/env/config
- external API
- actual collection
- actual publishing

## Promotion Status

Promoted into:

- `CODEX_BOOTSTRAP.md`
- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
- `DOC/walkthrough/README.md`
- `DOC/correction-loop/README.md`

No runtime behavior was changed.
