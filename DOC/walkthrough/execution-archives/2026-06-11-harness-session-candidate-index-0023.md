# Harness Session: TO_BE_DOCS / CODEX_HARNESS_DOCS

Timebox:

```text
Session start: 2026-06-11 00:23:00 KST
Planned stop: 2026-06-11 01:23:00 KST
Long-run stop: 2026-06-11 06:00:00 KST
```

## Quick Pre-Review

AREA:

- TO_BE_DOCS
- CODEX_HARNESS_DOCS

MODE:

- DOC_ONLY

FOCUS:

- Consolidate discovered `CODE_TASK_CANDIDATE` items.
- Classify candidates by AREA, MODE, risk, and approval requirement.
- Prepare for future one-hour implementation/audit prompts.

Decision:

```text
PROCEED_WITH_LIMITS
```

Limits:

- No code edits.
- No DB changes.
- No external API calls.
- No scheduler, Facebook, auth, env, server, or bot-state changes.
- Do not approve protected candidates from this session.

## Documents Reviewed

- `DOC/walkthrough/2026-06-11-harness-session-codex-harness-docs-0014.md`
- `DOC/walkthrough/2026-06-11-harness-session-db-architecture-docs-0017.md`
- `DOC/walkthrough/2026-06-11-harness-session-design-archive-docs-0019.md`
- `DOC/walkthrough/2026-06-11-harness-session-product-source-quality-0021.md`

## Documents Updated

- `DOC/to-be/CODE_TASK_CANDIDATE_INDEX.md`
  - Added consolidated candidate table.
  - Added recommended execution phases.
  - Added protected area notes.
  - Linked source walkthroughs.

## Structure Improvements

- Future code work is now centralized instead of being scattered only through session reports.
- Protected implementation candidates are separated from read-only audits.
- The recommended next prompts are narrow enough to start future one-hour harness sessions.

## Candidate Counts

```text
Total candidates indexed: 17
Read-only audit or audit-first candidates: 13
Protected implementation candidates: 4
```

Primary protected clusters:

- content-only publishing path and direct social-news publish retirement
- publish rotation across occupation/living/immigration/community-derived content
- Facebook publisher / scheduler / token / publish selection behavior

## Code Task Candidate Highlight

Highest-priority safe next step:

```text
CODE_TASK_CANDIDATE
AREA: DB_ARCHITECTURE_DOCS
MODE: READ_ONLY_AUDIT
FOCUS: Run read-only DB inventory for social_news/content boundaries and write a report.
WHY: Many later protected changes depend on knowing actual source/content/publish-log ownership.
RISK: LOW-MEDIUM
PROTECTED AREA: NO, read-only SQL only.
RECOMMENDED NEXT PROMPT: AREA: DB_ARCHITECTURE_DOCS / MODE: READ_ONLY_AUDIT / FOCUS: Run read-only DB inventory for social_news/content boundaries and write a report.
```

Highest-risk protected step:

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_PUBLISHER
MODE: PROTECTED_CHANGE
FOCUS: Move final automatic publish selection fully to content.content_candidate and retire/gate direct social-news publishing.
WHY: This affects public Facebook output and scheduler behavior.
RISK: HIGH
PROTECTED AREA: YES - CONTENT_PUBLISHER, FACEBOOK_PUBLISHER, SCHEDULER_BOT_STATE.
RECOMMENDED NEXT PROMPT: Do not start until read-only DB/content audits are complete and user explicitly approves protected implementation.
```

## Next Session Recommendation

AREA:

- CODEX_HARNESS_DOCS
- PRODUCT_DOCS

MODE:

- DOC_ONLY

FOCUS:

- Prepare a six-hour compressed report template.
- Check all updated DOC files for Markdown structure.
- Decide whether any additional doc-only cleanup is safe before the 06:00 KST shutdown window.

## Verification

- Markdown structure check: PASS.
  - `CODE_TASK_CANDIDATE_INDEX.md`: even code fence count.
  - This walkthrough: even code fence count.
- Candidate index count check: PASS.
  - 17 candidate rows found.
- Git status check: DONE.
  - Candidate index and walkthrough are new DOC files.
  - Existing prior non-DOC code changes remain in the worktree and were not touched in this session.
- Telegram: NOT RUN, external API calls are forbidden in this DOC_ONLY long-run.
- Commit/push decision: DO NOT COMMIT YET because worktree contains mixed DOC and prior code changes.
