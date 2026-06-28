# Harness Session: DESIGN_ARCHIVE_DOCS / TO_BE_DOCS

Timebox:

```text
Session start: 2026-06-11 00:19:00 KST
Planned stop: 2026-06-11 01:19:00 KST
Long-run stop: 2026-06-11 06:00:00 KST
```

## Quick Pre-Review

AREA:

- DESIGN_ARCHIVE_DOCS
- TO_BE_DOCS

MODE:

- DOC_ONLY

FOCUS:

- Review older design and to-be documents against current architecture/database direction.
- Mark outdated assumptions without deleting assets.
- Record future code work candidates only.

Decision:

```text
PROCEED_WITH_LIMITS
```

Limits:

- No code edits.
- No DB changes or migrations.
- No archive asset deletion.
- No server, scheduler, Facebook, Telegram, env, auth, or bot-state changes.

## Documents Reviewed

- `DOC/design/admin-ui-process-integration.md`
- `DOC/design/admin_db_schema.md`
- `DOC/design/content_publishing_hub.md`
- `DOC/to-be/ADMIN_UI_IMPROVEMENT.md`
- `DOC/to-be/content-creation.md`

## Documents Updated

- `DOC/design/admin-ui-process-integration.md`
  - Added Harness Status as legacy design reference.
  - Pointed to current architecture/database docs before implementation.
  - Marked SQLite/runtime/UI assumptions as outdated.

- `DOC/design/admin_db_schema.md`
  - Added Harness Status as legacy schema design reference.
  - Pointed to current DB documents as authoritative references.
  - Warned that schema plans may be implemented, renamed, or superseded.

- `DOC/design/content_publishing_hub.md`
  - Added Harness Status as current design reference with protected implementation items.
  - Marked scheduler/Facebook/token/frequency/selection changes as protected.

- `DOC/to-be/content-creation.md`
  - Added Harness Status as future concept requiring decomposition.
  - Split its scope conceptually into smaller future work areas.
  - Marked publishing, scheduler, token, and automatic selection changes as protected.

## Structure Conflicts Found

1. `admin-ui-process-integration.md` still describes the admin UI as disconnected from backend APIs and the runtime repository as SQLite in several places.

2. `admin_db_schema.md` is useful history but cannot be the authoritative DB schema source because current DB docs now split responsibilities by schema and include later content-hub direction.

3. `content_publishing_hub.md` is mostly aligned with current architecture, but its remaining work includes protected implementation areas.

4. `content-creation.md` is too broad for a one-hour harness session because it combines occupation data, community interest collection, LLM analysis, content generation, DB expansion, UI work, and Facebook publishing.

## Archive / Deprecated Decision

- No files moved.
- No image, zip, video, PPT, or other reference asset deleted.
- `admin-ui-process-integration.md` and `admin_db_schema.md` are now marked as legacy design references.
- `content_publishing_hub.md` remains a current design reference, but protected implementation items are flagged.
- `content-creation.md` remains a future concept and must be decomposed before implementation.

## Code Task Candidates

```text
CODE_TASK_CANDIDATE
AREA: DASHBOARD_STATUS
MODE: READ_ONLY_AUDIT
FOCUS: Compare Admin UI Improvement Plan with actual dashboard API/store behavior and identify stale assumptions.
WHY: The to-be plan says dashboard should be summary-only, paginated, and cache-aware; actual behavior should be audited before any UI changes.
RISK: LOW-MEDIUM
PROTECTED AREA: NO
RECOMMENDED NEXT PROMPT: AREA: DASHBOARD_STATUS / MODE: READ_ONLY_AUDIT / FOCUS: Audit dashboard API/store query behavior and report only.
```

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
FOCUS: Verify content management validation labels, date columns, and source link fields against current content API responses.
WHY: `ADMIN_UI_IMPROVEMENT.md` and `content_publishing_hub.md` both require clearer content validation visibility, but implementation should follow actual API fields.
RISK: MEDIUM
PROTECTED AREA: NO
RECOMMENDED NEXT PROMPT: AREA: CONTENT_QUEUE / MODE: READ_ONLY_AUDIT / FOCUS: Inspect content API payloads and UI display gaps without changing code.
```

```text
CODE_TASK_CANDIDATE
AREA: OCCUPATION_DICTIONARY
MODE: READ_ONLY_AUDIT
FOCUS: Decompose occupation-based content creation into data readiness, enrichment, and publishing-independent content draft phases.
WHY: `content-creation.md` is too broad and includes protected publisher/scheduler changes. Occupation data should first be treated as reference/dictionary data.
RISK: LOW-MEDIUM
PROTECTED AREA: NO
RECOMMENDED NEXT PROMPT: AREA: OCCUPATION_DICTIONARY / MODE: READ_ONLY_AUDIT / FOCUS: Produce an occupation content readiness report and task split.
```

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_PUBLISHER
MODE: PROTECTED_CHANGE
FOCUS: Add occupation/living/immigration content into the publish rotation after content readiness and review rules are defined.
WHY: Future content concepts require publishing slots, daily caps, and rotation rules, all of which affect public Facebook output.
RISK: HIGH
PROTECTED AREA: YES - CONTENT_PUBLISHER, FACEBOOK_PUBLISHER, SCHEDULER_BOT_STATE.
RECOMMENDED NEXT PROMPT: AREA: CONTENT_PUBLISHER / MODE: PROTECTED_CHANGE / FOCUS: After readiness audits, implement guarded publish rotation with explicit approval.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN
MODE: READ_ONLY_AUDIT
FOCUS: Review community/topic-search collection ideas for policy, source reliability, privacy, and terms-of-service risks before implementation.
WHY: `content-creation.md` and `topic-search.md` mention Reddit/community/social sources; these need a safe source policy before collection.
RISK: MEDIUM-HIGH
PROTECTED AREA: NO, if audit only. Future collection may require approval depending on source/API terms.
RECOMMENDED NEXT PROMPT: AREA: LIVING_DOMAIN / MODE: READ_ONLY_AUDIT / FOCUS: Draft safe community-source discovery policy and blocked-source rules.
```

## Protected Change Candidates

- Real publishing of occupation/living/immigration generated content.
- Any change to Facebook publish payload, token usage, frequency, retry, or final selection.
- Any scheduler interval/cooldown/daily-cap change.
- Any DB migration for new community-interest or content-generation tables.
- Any external community data collection that may involve API terms, privacy, or PII risk.

## Next Session Recommendation

AREA:

- TO_BE_DOCS
- PRODUCT_DOCS

MODE:

- DOC_ONLY

FOCUS:

- Review `gpt-connect.md`, `topic-search.md`, and product/data-quality docs together.
- Add safe-source and privacy TODOs where community/GPT future plans need guardrails.
- Produce next candidates for `LIVING_DOMAIN`, `LLAMA_STATUS`, and future GPT/data-access work.

## Verification

- Markdown structure check: PASS.
  - `admin-ui-process-integration.md`: even code fence count.
  - `admin_db_schema.md`: even code fence count.
  - `content_publishing_hub.md`: even code fence count.
  - `content-creation.md`: no code fences.
  - This walkthrough: even code fence count.
- Harness status notes: PASS.
  - Legacy/current/future status markers found in reviewed design/to-be docs.
- Git status check: DONE.
  - Design/to-be docs changed.
  - Existing prior non-DOC code changes remain in the worktree and were not touched in this session.
- Telegram: NOT RUN, external API calls are forbidden in this DOC_ONLY long-run.
- Commit/push decision: DO NOT COMMIT YET because worktree contains mixed DOC and prior code changes.
