# Harness Improvement Review

## Context

This review follows the architecture harness reset and review of `DOC/architecture/00` through `DOC/architecture/06`.

The purpose is to capture harness improvement opportunities before they become direct architecture, work-area, or code changes.

This document is a correction-loop backlog. It is not an implementation plan and does not modify active architecture rules.

Promotion Status:

Selected candidates were promoted in a later DOC_ONLY architecture task. Historical `Do not execute now` notes are preserved as the original review state; active rules now live in the promoted target documents.

Correction-loop process:

```text
issue observed
-> identify failed layer
-> check whether harness missed a rule
-> define reusable improvement
-> review with human
-> promote to architecture/work-area/code task only after approval
```

## Immediate Small Improvements

### A. Strengthen Required Input Rule in 05

Issue:

Current wording may allow Codex to infer missing required fields too freely.

Improvement:

If `PURPOSE FUNCTION`, `AREA`, or `MODE` is missing, Codex must not edit files. It may only run `READ_ONLY_AUDIT` or ask for clarification.

Target:

`DOC/architecture/05_CODEX_HARNESS_GUIDE.md`

Type:

Architecture update candidate

Do not execute now:

Yes

### B. Add Target Country Mismatch Trigger in 02

Issue:

Global or non-Korea content may still enter WorkConnect Korea review/publishing if target-country fit is not explicit.

Improvement:

Add a quality trigger card for Target Country Mismatch.

Target:

`DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`

Type:

Trigger card candidate

Do not execute now:

Yes

### C. Add Local Test Touches Real External Output Trigger in 04

Issue:

Local tests may accidentally send real Facebook posts, Telegram messages, or external API calls.

Improvement:

Add runtime trigger requiring dry-run, mock mode, or explicit approval before any real external output.

Target:

`DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`

Type:

Runtime trigger candidate

Do not execute now:

Yes

### D. Clarify Final Public Message/Link Ownership in 03

Issue:

`social_news.candidate` vs `content.content_candidate` ownership is still a known ambiguity.

Improvement:

State that final public message and final publishable link should be owned by content management, while preserving implementation ambiguity for future audit.

Target:

`DOC/architecture/03_SYSTEM_ARCHITECTURE.md`

Type:

Architecture clarification candidate

Do not execute now:

Yes

### E. Mark 07 as Review Reference

Issue:

`07_HARNESS_RESTRUCTURE_REVIEW.md` may be mistaken for active rules.

Improvement:

Add status note: "Review reference. Active architecture rules are in 00~06."

Target:

`DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md`

Type:

Documentation status candidate

Do not execute now:

Yes

## General Improvement Extraction

## Candidate: Required Field Stop Gate

Observed issue:

The active harness says missing required fields may be inferred conservatively. For file-editing tasks, this can still allow Codex to proceed before the core task identity is explicit.

Failed layer:

work-area boundary

Missing harness rule:

Required fields need a hard stop rule for write operations.

Reusable improvement:

Add a rule that any write operation requires explicit `PURPOSE FUNCTION`, `AREA`, and `MODE`. Without them, Codex may only read architecture documents, perform a read-only audit, or ask for clarification.

Suggested target:

`DOC/architecture/05_CODEX_HARNESS_GUIDE.md`

Promotion type:

- architecture update
- trigger card

Risk:

LOW

Do not execute now:

Yes

## Candidate: Target Country Mismatch Trigger

Observed issue:

The active product constitution says non-Korea content should not enter WorkConnect Korea public review by default, but the quality trigger list does not yet name target-country mismatch as a specific trigger card.

Failed layer:

domain classification

Missing harness rule:

Target-country mismatch should trigger downgrade, reference-only storage, review, or stop before public review/publishing.

Reusable improvement:

Add a `Target Country Mismatch` trigger card to data quality rules.

Suggested target:

`DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`

Promotion type:

- trigger card
- architecture update

Risk:

LOW

Do not execute now:

Yes

## Candidate: Real External Output During Local Testing

Observed issue:

The runtime guide identifies Facebook and Telegram as external-impact paths, but it does not yet state a compact test-specific trigger for local testing that could send real external output.

Failed layer:

runtime boundary

Missing harness rule:

Any local test or verification that could send Facebook posts, Telegram messages, or external API calls must require dry-run, mock mode, or explicit approval.

Reusable improvement:

Add a runtime trigger card: `Local Test Touches Real External Output`.

Suggested target:

`DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`

Promotion type:

- trigger card
- runtime trigger candidate

Risk:

MEDIUM

Do not execute now:

Yes

## Candidate: Final Public Message and Link Ownership

Observed issue:

The active system architecture preserves ambiguity between `social_news.candidate` and `content.content_candidate`, but future work may still change publishers before confirming which layer owns final public message/link state.

Failed layer:

public delivery

Missing harness rule:

Final public message and final publishable link ownership should be stated as a target boundary while implementation ownership remains an audit question.

Reusable improvement:

Clarify that content management should own final public message and final publishable link, and that current implementation must be audited before changing publisher behavior.

Suggested target:

`DOC/architecture/03_SYSTEM_ARCHITECTURE.md`

Promotion type:

- architecture update
- read-only audit

Risk:

MEDIUM

Do not execute now:

Yes

## Candidate: Review Reference Status for 07

Observed issue:

`07_HARNESS_RESTRUCTURE_REVIEW.md` remains in the architecture folder and may be read as an active architecture rule document.

Failed layer:

verification/reporting

Missing harness rule:

Reference documents should clearly declare whether they are active rules or review material.

Reusable improvement:

Add a status note to `07_HARNESS_RESTRUCTURE_REVIEW.md` that active architecture rules are in `00` through `06`.

Suggested target:

`DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md`

Promotion type:

- architecture update
- documentation status candidate

Risk:

LOW

Do not execute now:

Yes

## Candidate: Correction-Loop Promotion Rule for Architecture Changes

Observed issue:

The active architecture documents define correction loops, but there is no active rule explaining when a correction-loop finding should graduate into an architecture edit versus a work-area audit or code task.

Failed layer:

verification/reporting

Missing harness rule:

Correction-loop findings need explicit promotion criteria before active rule documents are changed.

Reusable improvement:

Promote findings to architecture only when they affect product purpose, repeated cross-area behavior, trigger cards, execution cards, or protected boundary clarity.

Suggested target:

`DOC/correction-loop/README.md` first; after human review, possibly `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`.

Promotion type:

- execution card
- architecture update

Risk:

LOW

Do not execute now:

Yes

## Candidate: Active Rule vs Backlog Document Boundary

Observed issue:

The project now has architecture docs, archive docs, to-be docs, walkthroughs, and correction-loop docs. Future Codex tasks may treat backlog candidates as already approved rules.

Failed layer:

work-area boundary

Missing harness rule:

Documents should be classified by authority: active rule, reference, backlog, walkthrough, or archive.

Reusable improvement:

Add a lightweight document authority map so Codex knows which documents control execution and which only preserve history or candidates.

Suggested target:

`DOC/architecture/03_SYSTEM_ARCHITECTURE.md` or `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`

Promotion type:

- architecture update
- work-area registry update

Risk:

LOW

Do not execute now:

Yes

## Candidate: Operation Notification Recurrence Suppression

Observed issue:

Architecture separates public delivery from operation notification, but repeated Telegram review/reporting of the same candidate can still become an operational failure pattern if duplicate identity is unclear.

Failed layer:

operation notification

Missing harness rule:

Operation notification needs its own duplicate and recurrence suppression trigger, separate from public content duplicate rules.

Reusable improvement:

Add a trigger or execution card for repeated Telegram review/reporting suppression based on stable review identity.

Suggested target:

`DOC/architecture/06_WORK_AREA_REGISTRY.md` under `TELEGRAM_REPORTING`, or `DOC/architecture/05_CODEX_HARNESS_GUIDE.md` as a generic execution card pattern.

Promotion type:

- execution card
- work-area registry update
- read-only audit

Risk:

MEDIUM

Do not execute now:

Yes

## Candidate: Source Signal vs Publishable Source Boundary

Observed issue:

Discovery sources and community/forum sources are defined as signals, but future code tasks may accidentally promote signal-only data into content candidates without source-backed validation.

Failed layer:

source discovery

Missing harness rule:

Signal-only sources should have a named promotion barrier before content candidate creation.

Reusable improvement:

Add an execution card for `Signal to Source-Backed Content` requiring validation against primary, trusted, or practical secondary sources before review or publishing.

Suggested target:

`DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md` or `DOC/architecture/06_WORK_AREA_REGISTRY.md`

Promotion type:

- execution card
- trigger card
- read-only audit

Risk:

MEDIUM

Do not execute now:

Yes

## Candidate: Verification Plan Required for Runtime-Adjacent Docs

Observed issue:

Work areas can be documentation-only, but some doc changes create future runtime expectations. If verification requirements are not captured when the candidate is written, future implementation tasks may start with unclear checks.

Failed layer:

verification/reporting

Missing harness rule:

Runtime-adjacent correction-loop candidates should include expected verification checks before promotion.

Reusable improvement:

Require candidate entries that target runtime, publisher, scheduler, auth, DB, or external APIs to include a preliminary verification checklist.

Suggested target:

`DOC/correction-loop/README.md`, then possibly `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`

Promotion type:

- execution card
- architecture update

Risk:

LOW

Do not execute now:

Yes

## Candidate: Multi-Responsibility File Section Map

Observed issue:

The architecture now says same file does not mean same responsibility, but large files may still need a section-level ownership map before safe implementation.

Failed layer:

multi-responsibility file boundary

Missing harness rule:

High-risk multi-responsibility files should be mapped before guarded fixes if the target section is unclear.

Reusable improvement:

Create a read-only audit pattern for section maps: identify responsibilities, protected sections, allowed sections for the task, and verification needed.

Suggested target:

`DOC/architecture/05_CODEX_HARNESS_GUIDE.md` or `DOC/architecture/06_WORK_AREA_REGISTRY.md`

Promotion type:

- execution card
- read-only audit

Risk:

MEDIUM

Do not execute now:

Yes

## Do Not Implement

This document is a backlog and review document only.

No architecture change is executed in this task.

No source code, database, migration, scheduler, Facebook publisher, Telegram runtime behavior, content publisher, auth, env/config, or external API behavior is changed in this task.

No ownership decision is made for `social_news.candidate` vs `content.content_candidate`.

No Python vs Java workflow ownership decision is made.

## Recommended Next Task

Suggested next safe task:

```text
AREA: CODEX_HARNESS_DOCS + PRODUCT_DOCS
MODE: DOC_ONLY
PURPOSE FUNCTION:
Review DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md with the human, then promote approved candidates into DOC/architecture updates.
TIMEBOX: 60m
```

Do not execute this promotion task until the human has selected which candidates to promote.
