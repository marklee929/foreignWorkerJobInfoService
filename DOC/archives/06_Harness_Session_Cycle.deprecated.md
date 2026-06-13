# Deprecated: Harness Session Cycle

Status: deprecated and absorbed into `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`.

Reason: the session cycle, conditional commit/push rule, Telegram summary rule, and six-hour compression rule are operational harness rules. Keeping them in a separate architecture file duplicated the harness guide and created numbering pressure for the work area registry.

Replacement:

```text
DOC/architecture/05_CODEX_HARNESS_GUIDE.md
```

## Original Role

This file defined the one-hour harness session cycle:

```text
00:00-00:10  Quick pre-review
00:10-00:40  Development work
00:40-00:50  Development verification
00:50-01:00  Final check, walkthrough update, conditional commit/push, and Telegram summary
```

It also covered:

- multi-session handling
- six-hour compression reports
- conditional commit/push rules
- Telegram summary constraints

Those rules now live in the harness guide.
