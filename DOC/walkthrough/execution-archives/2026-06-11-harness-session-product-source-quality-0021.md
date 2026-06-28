# Harness Session: PRODUCT_DOCS / TO_BE_DOCS

Timebox:

```text
Session start: 2026-06-11 00:21:00 KST
Planned stop: 2026-06-11 01:21:00 KST
Long-run stop: 2026-06-11 06:00:00 KST
```

## Quick Pre-Review

AREA:

- PRODUCT_DOCS
- TO_BE_DOCS
- LIVING_DOMAIN

MODE:

- DOC_ONLY

FOCUS:

- Compare future GPT/community topic discovery ideas against product direction and data quality gates.
- Add source-policy guardrails where future plans mention community, comments, GPT, or broad search.
- Record code work candidates without implementation.

Decision:

```text
PROCEED_WITH_LIMITS
```

Limits:

- No external API calls.
- No community scraping.
- No code changes.
- No DB schema changes.
- No publishing, scheduler, auth, env, or server changes.

## Documents Reviewed

- `DOC/architecture/00_PRODUCT_NORTH_STAR.md`
- `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
- `DOC/to-be/gpt-connect.md`
- `DOC/to-be/topic-search.md`

## Documents Updated

- `DOC/architecture/00_PRODUCT_NORTH_STAR.md`
  - Fixed a Markdown code fence closing.

- `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
  - Added community/forum discovery sources.
  - Added rules for terms, access restrictions, privacy, anonymization, and source-backed validation.

- `DOC/to-be/gpt-connect.md`
  - Added Harness Status as future architecture concept.
  - Added guardrails for source domains, blocked questions, citations, PII, stale data, and audit logging.

- `DOC/to-be/topic-search.md`
  - Added Harness Status as future discovery concept requiring source-policy review.
  - Added allowed/blocked platform, terms, privacy, retention, and validation prerequisites.

## Structure Conflicts Found

1. Product North Star says WorkConnect must be source-backed and practical, while `topic-search.md` could be misread as broad community scraping unless guardrails are explicit.

2. `gpt-connect.md` describes future GPT access, but did not yet state that GPT must not become an unrestricted DB reader or unsourced advice engine.

3. Community posts/comments are useful as user-need signals, but they are not authoritative evidence for visa/labor/legal claims.

4. Raw comments and personal stories create privacy and terms-of-service risks if collected or quoted without a clear policy.

## Code Task Candidates

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN
MODE: READ_ONLY_AUDIT
FOCUS: Draft a safe community-source policy for topic discovery before implementing any collector.
WHY: Future topic-search plans mention Reddit, Quora, forums, blogs, and Facebook groups, but source legality, access restrictions, and privacy rules must be defined first.
RISK: MEDIUM-HIGH
PROTECTED AREA: NO for policy audit. Future collection may require approval depending on platform/API terms.
RECOMMENDED NEXT PROMPT: AREA: LIVING_DOMAIN / MODE: READ_ONLY_AUDIT / FOCUS: Produce allowed/blocked community-source policy and retention rules.
```

```text
CODE_TASK_CANDIDATE
AREA: LLAMA_STATUS
MODE: READ_ONLY_AUDIT
FOCUS: Define Local LLM usage boundaries for community-signal classification and GPT future answers.
WHY: LLM may classify user concerns and summarize patterns, but must not decide legal meaning, publish directly, or replace source validation.
RISK: MEDIUM
PROTECTED AREA: NO
RECOMMENDED NEXT PROMPT: AREA: LLAMA_STATUS / MODE: READ_ONLY_AUDIT / FOCUS: Document LLM allowed/blocked uses for topic discovery and GPT answer preparation.
```

```text
CODE_TASK_CANDIDATE
AREA: DB_ARCHITECTURE_DOCS
MODE: READ_ONLY_AUDIT
FOCUS: Design a future data model for community topic signals without storing unnecessary PII.
WHY: Topic discovery may need URL, platform, title, snippet, aggregate signals, and anonymized metadata, but raw comment storage may be risky.
RISK: MEDIUM
PROTECTED AREA: NO for design audit. Schema change would require later guarded migration planning.
RECOMMENDED NEXT PROMPT: AREA: DB_ARCHITECTURE_DOCS / MODE: READ_ONLY_AUDIT / FOCUS: Draft privacy-preserving topic signal data model without migration.
```

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
FOCUS: Define how community topic signals can become source-backed content candidates.
WHY: Community signals should not bypass official/trusted source validation or become final publishable content by themselves.
RISK: MEDIUM
PROTECTED AREA: NO
RECOMMENDED NEXT PROMPT: AREA: CONTENT_QUEUE / MODE: READ_ONLY_AUDIT / FOCUS: Propose signal-to-source-backed-content workflow and review gates.
```

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_PUBLISHER
MODE: PROTECTED_CHANGE
FOCUS: Add GPT/community-derived content to publishing only after source-backed validation and review gates exist.
WHY: Publishing content derived from community signals risks privacy issues, weak sourcing, and overclaiming unless guarded.
RISK: HIGH
PROTECTED AREA: YES - CONTENT_PUBLISHER, FACEBOOK_PUBLISHER, SCHEDULER_BOT_STATE.
RECOMMENDED NEXT PROMPT: AREA: CONTENT_PUBLISHER / MODE: PROTECTED_CHANGE / FOCUS: Implement publishing only after source policy and content validation are approved.
```

## Protected Change Candidates

- Collecting private, logged-in, closed-group, or access-controlled community content.
- Storing personal identifiers or raw personal stories.
- Publishing community-derived claims without primary/trusted source validation.
- Giving GPT direct unrestricted database access.
- Allowing GPT output to publish without admin/content review.

## Next Session Recommendation

AREA:

- CODEX_HARNESS_DOCS
- TO_BE_DOCS

MODE:

- DOC_ONLY

FOCUS:

- Consolidate discovered `CODE_TASK_CANDIDATE` entries into a task-candidate index or section.
- Classify candidates by AREA, MODE, risk, protected area, and recommended next prompt.
- Prepare for the first 6H compressed report structure.

## Verification

- Markdown structure check: PASS.
  - `00_PRODUCT_NORTH_STAR.md`: even code fence count.
  - `02_DATA_SOURCE_AND_QUALITY.md`: even code fence count.
  - `gpt-connect.md`: no code fences.
  - `topic-search.md`: even code fence count.
  - This walkthrough: even code fence count.
- Guardrail marker scan: PASS.
  - Community/forum source rule found.
  - GPT future architecture status found.
  - Topic-search future discovery status found.
- Git status check: DONE.
  - Product/to-be docs changed.
  - Existing prior non-DOC code changes remain in the worktree and were not touched in this session.
- Telegram: NOT RUN, external API calls are forbidden in this DOC_ONLY long-run.
- Commit/push decision: DO NOT COMMIT YET because worktree contains mixed DOC and prior code changes.
