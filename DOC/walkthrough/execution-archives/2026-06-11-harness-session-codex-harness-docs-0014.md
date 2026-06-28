# Harness Session: CODEX_HARNESS_DOCS / SYSTEM_ARCHITECTURE_DOCS

Timebox:

```text
Session start: 2026-06-11 00:14:00 KST
Planned stop: 2026-06-11 01:14:00 KST
Long-run stop: 2026-06-11 06:00:00 KST
```

## Quick Pre-Review

AREA:

- CODEX_HARNESS_DOCS
- SYSTEM_ARCHITECTURE_DOCS
- TO_BE_DOCS

MODE:

- DOC_ONLY

FOCUS:

- Prepare future automation sessions by improving harness documentation.
- Identify future code work as candidates only.
- Do not modify code, DB, env, scheduler, Facebook publisher, admin auth, bot state, or server runtime.

Decision:

```text
PROCEED_WITH_LIMITS
```

Limits:

- Existing non-DOC worktree changes are present from a prior Facebook token task.
- This session does not edit those code files.
- Commit/push is unsafe until the mixed worktree is reviewed separately.
- Telegram summary is not sent because this session forbids actual external API calls.

## Documents Reviewed

- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
- `DOC/architecture/06_WORK_AREA_REGISTRY.md`
- `DOC/database/TO_BE_DB_ARCHITECTURE.md`
- `DOC/to-be/ADMIN_UI_IMPROVEMENT.md`
- `DOC/to-be/CONTENT_PIPELINE_REFACTOR.md`
- `DOC/to-be/content-creation.md`
- `DOC/to-be/duplicate-data-distribution.md`
- `DOC/to-be/gpt-connect.md`
- `DOC/to-be/topic-search.md`

## Documents Updated

- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - Added `Code Task Candidate Rule`.
  - Added required `CODE_TASK_CANDIDATE` format for DOC_ONLY discovery sessions.

- `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  - Added `SYSTEM_ARCHITECTURE_DOCS`.
  - Added `CODEX_HARNESS_DOCS`.
  - Added `TO_BE_DOCS`.
  - Added `DESIGN_ARCHIVE_DOCS`.

## Structure Conflicts Found

1. The long-run request uses document-only areas that were not fully represented in the work area registry.
   - `SYSTEM_ARCHITECTURE_DOCS`
   - `CODEX_HARNESS_DOCS`
   - `TO_BE_DOCS`
   - `DESIGN_ARCHIVE_DOCS`

2. Future-code planning existed in `DOC/to-be`, but the harness guide did not define a standard way to capture code work discovered during DOC_ONLY review.

3. `DOC/to-be/content-creation.md` still references direct Facebook Page Access Token assumptions. This may conflict with the newer runtime direction where publishing should be centralized and token handling should be treated as a protected Facebook area.

4. `DOC/to-be/CONTENT_PIPELINE_REFACTOR.md` aligns with DB architecture direction, but it needs future validation against actual source-to-content sync behavior before implementation.

## Code Task Candidates

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
FOCUS: Audit whether social_news rows are synced into content.content_candidate with raw_ref_table/raw_ref_id and without losing source ownership.
WHY: DB to-be docs say content.content_candidate should be the authoritative publishing object, while source schemas remain source/domain data.
RISK: MEDIUM
PROTECTED AREA: NO
RECOMMENDED NEXT PROMPT: AREA: CONTENT_QUEUE / MODE: READ_ONLY_AUDIT / FOCUS: Verify source-to-content sync boundaries and produce a report only.
```

```text
CODE_TASK_CANDIDATE
AREA: FACEBOOK_STATUS
MODE: READ_ONLY_AUDIT
FOCUS: Audit Facebook token status reporting and error category mapping without changing publish behavior.
WHY: Recent token failure analysis showed status/reporting needs to distinguish token invalid, token expired, page mismatch, permission missing, and unknown Meta failures.
RISK: MEDIUM-HIGH
PROTECTED AREA: YES - Facebook token/status reporting only; do not change publisher behavior.
RECOMMENDED NEXT PROMPT: AREA: FACEBOOK_STATUS / MODE: READ_ONLY_AUDIT / FOCUS: Inspect token/error reporting paths and document gaps without code edits.
```

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_PUBLISHER
MODE: PROTECTED_CHANGE
FOCUS: Move final automatic publishing selection fully to content.content_candidate and prevent direct source-schema publishing.
WHY: Architecture and DB docs define content as the authoritative publishing owner, but historical docs still mention direct news publishing paths.
RISK: HIGH
PROTECTED AREA: YES - CONTENT_PUBLISHER and Facebook publishing behavior.
RECOMMENDED NEXT PROMPT: AREA: CONTENT_PUBLISHER / MODE: PROTECTED_CHANGE / FOCUS: Implement content-only publishing after explicit approval and pre-review.
```

```text
CODE_TASK_CANDIDATE
AREA: SOCIAL_NEWS_CANDIDATE
MODE: GUARDED_FIX
FOCUS: Split duplicate status into duplicate_type and representative grouping.
WHY: `DOC/to-be/duplicate-data-distribution.md` says DUPLICATE rows currently collapse useful signal into one state.
RISK: MEDIUM
PROTECTED AREA: NO
RECOMMENDED NEXT PROMPT: AREA: SOCIAL_NEWS_CANDIDATE / MODE: READ_ONLY_AUDIT / FOCUS: Inspect duplicate fields and produce implementation plan before any schema/code change.
```

```text
CODE_TASK_CANDIDATE
AREA: OCCUPATION_DICTIONARY
MODE: READ_ONLY_AUDIT
FOCUS: Audit occupation/job dictionary data flow before generating occupation-based content.
WHY: `DOC/to-be/content-creation.md` proposes occupation content generation, but architecture says occupation data is reference/dictionary data and should not be treated as active job postings.
RISK: LOW-MEDIUM
PROTECTED AREA: NO
RECOMMENDED NEXT PROMPT: AREA: OCCUPATION_DICTIONARY / MODE: READ_ONLY_AUDIT / FOCUS: Verify occupation data readiness for guide content without publishing.
```

## Protected Change Candidates

- `CONTENT_PUBLISHER`: final automatic publishing selection and Facebook publish trigger changes.
- `FACEBOOK_PUBLISHER`: any change to Page API call, publish payload, retry behavior, token usage during publish.
- `SCHEDULER_BOT_STATE`: publish interval/cooldown changes and bot ON/OFF behavior.
- `ADMIN_AUTH`: any admin login, device approval, session, or auth header changes.

## Next Session Recommendation

AREA:

- DB_ARCHITECTURE_DOCS
- TO_BE_DOCS

MODE:

- DOC_ONLY

FOCUS:

- Review `DOC/database/*CURRENT.md` and `DOC/database/TO_BE_DB_ARCHITECTURE.md`.
- Confirm source data / content candidate / publish log / admin ops boundaries.
- Add TODO/deprecation notes to `DOC/to-be` where older plans conflict with the current architecture.

## Verification

- Markdown structure check: PASS.
  - `05_CODEX_HARNESS_GUIDE.md`: even code fence count.
  - `06_WORK_AREA_REGISTRY.md`: even code fence count.
  - This walkthrough: even code fence count.
- Stale reference scan: PASS for the checked architecture/database/to-be/walkthrough scope.
- Git status check: DONE.
  - DOC files changed in this session.
  - Existing prior non-DOC changes remain in the worktree and were not touched in this session.
- Telegram: NOT RUN, external API calls are forbidden in this DOC_ONLY long-run.
- Commit/push decision: DO NOT COMMIT YET because worktree contains mixed DOC and prior code changes.
