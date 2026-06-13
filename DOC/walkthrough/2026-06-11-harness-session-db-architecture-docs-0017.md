# Harness Session: DB_ARCHITECTURE_DOCS / TO_BE_DOCS

Timebox:

```text
Session start: 2026-06-11 00:17:00 KST
Planned stop: 2026-06-11 01:17:00 KST
Long-run stop: 2026-06-11 06:00:00 KST
```

## Quick Pre-Review

AREA:

- DB_ARCHITECTURE_DOCS
- TO_BE_DOCS

MODE:

- DOC_ONLY

FOCUS:

- Review current DB reference docs and to-be content pipeline plan.
- Clarify source data / content candidate / publishing log / admin ops boundaries.
- Record future code work candidates without implementation.

Decision:

```text
PROCEED_WITH_LIMITS
```

Limits:

- No DB metadata queries.
- No migrations.
- No code edits.
- No scheduler, Facebook publisher, auth, env, or server runtime changes.
- Existing mixed worktree changes are not part of this session.

## Documents Reviewed

- `DOC/database/00_DB_ARCHITECTURE_INDEX.md`
- `DOC/database/01_CURRENT_DB_MAP.md`
- `DOC/database/02_SOCIAL_NEWS_CURRENT.md`
- `DOC/database/03_CONTENT_CURRENT.md`
- `DOC/database/TO_BE_DB_ARCHITECTURE.md`
- `DOC/to-be/CONTENT_PIPELINE_REFACTOR.md`

## Documents Updated

- `DOC/database/01_CURRENT_DB_MAP.md`
  - Fixed ERD reference path from non-existing `DOC/database/snapshots/Foreign_Worker_Job_Info_DB.png` to existing `DOC/database/Foreign_Worker_Job_Info_DB.png`.

- `DOC/database/02_SOCIAL_NEWS_CURRENT.md`
  - Removed pasted Markdown wrapper.
  - Fixed code fence closing.
  - Kept the source-news boundary warning intact.

- `DOC/database/03_CONTENT_CURRENT.md`
  - Removed pasted Markdown wrapper.
  - Fixed code fence closing.
  - Kept the authoritative content-publishing role intact.

- `DOC/database/TO_BE_DB_ARCHITECTURE.md`
  - Fixed code fence closings in core principle, content-flow, and migration principle sections.

- `DOC/to-be/CONTENT_PIPELINE_REFACTOR.md`
  - Added Harness Status section.
  - Marked final publishing path, scheduler behavior, automatic selection, retry/cooldown, and bulk migration as protected/high-risk implementation topics.

## Structure Conflicts Found

1. `01_CURRENT_DB_MAP.md` referenced a `snapshots` subfolder that is not present in the current DOC/database tree.

2. `02_SOCIAL_NEWS_CURRENT.md` and `03_CONTENT_CURRENT.md` were wrapped as pasted Markdown documents, which made their top-level headings and code fences harder to trust.

3. The current DB direction is clear: source schemas own source/domain data, while `content` owns final publishable candidates and final publish logs. However, to-be and historical docs still acknowledge direct social-news publishing as a transition path.

4. `CONTENT_PIPELINE_REFACTOR.md` is aligned with the architecture target, but implementation would cross protected areas if it changes scheduler behavior, Facebook publish path, or automatic selection.

## Boundary Summary

Current intended boundary:

```text
source/domain tables
-> content.content_candidate
-> content.publish_log
-> external publishing channel
```

Current source schemas:

- `social_news`: source news collection, normalization, scoring, duplicate handling, source candidate state.
- `occupation`: Employment24 reference/dictionary data, not active job postings.
- `immigration_info`: official notices and policy source data, sensitive by default.
- `living_info`: future settlement/life source data.

Current final publishing schema:

- `content.content_candidate`: final publishable object.
- `content.publish_log`: target authoritative publish log.

Admin/ops boundary:

- runtime settings, bot status, scheduler state, auth/device/session, environment readiness, dashboard status, and operation logs belong to admin/ops responsibility and must not be casually mixed with content lifecycle state.

## Code Task Candidates

```text
CODE_TASK_CANDIDATE
AREA: DB_ARCHITECTURE_DOCS
MODE: READ_ONLY_AUDIT
FOCUS: Inspect actual DB table and status distributions for social_news and content schemas.
WHY: Current docs list source/content boundary risks, but row counts, status distributions, duplicate counts, and publish-log ownership must be verified from actual DB before implementation.
RISK: LOW-MEDIUM
PROTECTED AREA: NO, if read-only SQL only.
RECOMMENDED NEXT PROMPT: AREA: DB_ARCHITECTURE_DOCS / MODE: READ_ONLY_AUDIT / FOCUS: Run read-only DB inventory for social_news/content boundaries and write a report.
```

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
FOCUS: Verify whether content.content_candidate is a final publishing object or a copy of social_news.candidate.
WHY: The content hub loses value if it simply mirrors source rows without final content fields, validation state, and source references.
RISK: MEDIUM
PROTECTED AREA: NO, if read-only.
RECOMMENDED NEXT PROMPT: AREA: CONTENT_QUEUE / MODE: READ_ONLY_AUDIT / FOCUS: Compare content candidates with source candidates and report duplication/traceability gaps.
```

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_PUBLISHER
MODE: PROTECTED_CHANGE
FOCUS: Retire or gate direct social_news Facebook publishing after content pipeline ownership is verified.
WHY: DB and architecture docs define content as the authoritative final publishing owner, but direct social-news publishing may still exist as transition behavior.
RISK: HIGH
PROTECTED AREA: YES - CONTENT_PUBLISHER, FACEBOOK_PUBLISHER, SCHEDULER_BOT_STATE.
RECOMMENDED NEXT PROMPT: AREA: CONTENT_PUBLISHER / MODE: PROTECTED_CHANGE / FOCUS: After read-only audit, migrate final publish selection to content-only path with explicit approval.
```

```text
CODE_TASK_CANDIDATE
AREA: DASHBOARD_STATUS
MODE: READ_ONLY_AUDIT
FOCUS: Verify dashboard APIs use summary/count queries rather than loading full source/content tables.
WHY: Current DB map marks dashboard query risk as a current architecture problem to verify.
RISK: LOW-MEDIUM
PROTECTED AREA: NO
RECOMMENDED NEXT PROMPT: AREA: DASHBOARD_STATUS / MODE: READ_ONLY_AUDIT / FOCUS: Inspect dashboard API query patterns and report heavy-load risks.
```

## Protected Change Candidates

- Moving final publish selection from direct social-news path to content-only path.
- Changing scheduler intervals, cooldown, daily cap, or bot state transitions.
- Bulk backfill/archive/migration of content candidates.
- Changing Facebook publish path, retry behavior, payload, or token usage.

## Next Session Recommendation

AREA:

- TO_BE_DOCS
- DESIGN_ARCHIVE_DOCS

MODE:

- DOC_ONLY

FOCUS:

- Review older design docs and to-be docs for direct Facebook publishing, approval-flow, token assumptions, and admin UI assumptions.
- Mark absorbed/superseded design notes without deleting assets.
- Produce candidates for future read-only audits.

## Verification

- Markdown structure check: PASS.
  - `01_CURRENT_DB_MAP.md`: even code fence count.
  - `02_SOCIAL_NEWS_CURRENT.md`: even code fence count.
  - `03_CONTENT_CURRENT.md`: even code fence count.
  - `TO_BE_DB_ARCHITECTURE.md`: even code fence count.
  - `CONTENT_PIPELINE_REFACTOR.md`: even code fence count.
  - This walkthrough: even code fence count.
- Stale reference scan: PASS for checked DB/to-be scope.
- Git status check: DONE.
  - DB/to-be docs changed.
  - `TO_BE_DB_ARCHITECTURE.md` is currently untracked because of prior file movement/rename state.
  - Existing prior non-DOC code changes remain in the worktree and were not touched in this session.
- Telegram: NOT RUN, external API calls are forbidden in this DOC_ONLY long-run.
- Commit/push decision: DO NOT COMMIT YET because worktree contains mixed DOC and prior code changes.
