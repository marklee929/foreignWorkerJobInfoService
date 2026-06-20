# Correction Loop

## Purpose

`DOC/correction-loop` stores correction-loop findings, harness improvement candidates, recurring failure patterns, and escalation notes.

This folder is for problems discovered during architecture review, audits, implementation work, or operation review before they become direct code changes or active architecture changes.

It is not:

- a bug-fix folder
- an implementation task folder
- an approval queue for automatic code changes
- a replacement for `DOC/architecture`

It is:

- a backlog for reusable harness improvements
- a place to classify recurring failures
- a place to preserve ambiguity before making product or implementation decisions
- a review space for human approval before promotion

## Difference from Direct Fixes

Direct fix:

```text
This line is wrong. Fix it.
```

Correction loop:

```text
This failure shows the harness missed a reusable rule.
Identify the failed layer, strengthen the harness, then decide whether code should change.
```

The correction loop should prevent the same class of failure from recurring across the project.

## Correction Loop Stages

Use this process:

```text
observe
-> classify failed layer
-> identify missing harness rule
-> define reusable improvement
-> review with human
-> promote to architecture/work-area/code task
-> verify recurrence prevention
```

Do not jump from observation directly to patching unless the task has an approved work area, mode, and verification plan.

## Failed Layer Categories

Classify each finding into one or more failed layers:

- product purpose
- source discovery
- raw collection
- normalization
- duplicate classification
- domain classification
- user value evaluation
- review eligibility
- public delivery
- operation notification
- runtime boundary
- work-area boundary
- multi-responsibility file boundary
- verification/reporting

If the failed layer is unclear, keep the finding as a read-only audit candidate.

## Promotion Rules

A finding may be promoted only after review.

Promote into active architecture only when the finding affects:

- product purpose
- repeated cross-area behavior
- trigger cards
- execution cards
- protected boundary clarity
- verification/reporting rules
- recurring failure prevention

Promote to an architecture update when:

- the product purpose or governance rule needs clarification
- multiple work areas would benefit from the same rule
- the active architecture set has a gap or ambiguity

Promote to a work-area registry update when:

- a specific module needs clearer allowed/forbidden boundaries
- a new work area is needed
- risk level or required checks are unclear

Promote to a trigger card when:

- Codex or the system needs to stop, downgrade, review, or escalate under a recognizable condition
- the condition can be checked during pre-review or validation

Promote to an execution card when:

- the same operational sequence is likely to repeat
- the steps, forbidden areas, and verification are known
- the rule should be compact enough to execute under time pressure

Promote to a read-only audit when:

- ownership is ambiguous
- current behavior is unknown
- implementation inspection is needed before choosing a fix
- code path mapping is required
- DB flow inspection is required
- publisher, scheduler, auth, or external API boundaries must be confirmed

Promote to a guarded code fix when:

- the failed layer is known
- the change is inside one allowed work area
- verification is possible
- no protected behavior is changed
- human approval has promoted the finding from backlog to task

Promote to a protected change request when:

- the finding touches auth, device approval, Facebook publisher, content publisher, scheduler, bot state, destructive migration, env/secrets, or external API behavior
- real public delivery or external operation behavior could change
- human approval is required before implementation

Correction-loop findings that target runtime, publisher, scheduler, auth, DB, env/config, external APIs, Telegram, Facebook, or content publisher must include a preliminary verification checklist before promotion.

Verification checklist may include:

- backend health
- frontend build/load
- target API response
- UI visual check
- dry-run/mock mode
- read-only DB diagnostics
- no external output sent
- no protected area touched
- no raw token/secret leakage

## Non-Execution Rule

Documents in this folder are review material only.

They do not execute changes, approve implementation, or override active architecture rules.

Active rules remain in `DOC/architecture/00` through `DOC/architecture/06` until a human-approved task promotes a finding.

## Harness Closeout Failure Rule

A chat-only report is an incomplete execution for walkthrough-driven Codex work.

Record a correction-loop item when Codex:

- finishes a task but fails to save the report under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
- fails to update the relevant daily execute prompt when the task requires it
- leaves multiple completion markers
- uses the legacy decorated Korean marker
- leaves a loose completion marker variant
- writes the completion marker only in chat instead of the execute prompt
- fails to verify marker count and final-line placement
- stops on a new daily execute prompt only because the first-run marker is absent, even though the file contains one clear pending task

Classify these as:

- verification/reporting
- walkthrough closeout
- harness trigger failure

The correction-loop item should state the missed closeout step, the repaired files, protected areas not touched, and the prevention rule that should be promoted if the failure repeats.
