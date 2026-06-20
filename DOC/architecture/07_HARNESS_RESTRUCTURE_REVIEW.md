# Harness Restructure Review

Status:

This is a review reference document. Active architecture rules are maintained in `DOC/architecture/00` through `DOC/architecture/06`. Use this document as restructure rationale, not as the primary execution rule set.

## Purpose

This review evaluates how the current `DOC/architecture` set should evolve into a practical harness system for WorkConnect.

This document does not rewrite existing architecture documents. It identifies how the existing documents can be lightly reorganized or supplemented so they become executable control structures for a coding agent and human operator.

Reference material from the Brain Pump notes is used only as conceptual background. The reusable concepts are:

- harness is not a long instruction document
- harness controls the reasoning path of an AI coding agent
- purpose function comes before data schema
- validation is a rule problem, classification is a worldview problem
- central governance manages philosophy
- module harnesses execute
- trigger cards define when intervention happens
- execution cards compress operational rules
- correction loop comes before one-to-one patching

## 1. Current Architecture Summary

### `00_PRODUCT_NORTH_STAR.md`

Current control role:

- Defines product identity, mission, first market, target users, content philosophy, automation philosophy, and success criteria.

Document type:

- Product direction
- Product governance
- Purpose definition

What it currently controls:

- WorkConnect is a work-and-settlement information platform, not a random news repost bot.
- Korea is the first market but not the whole product identity.
- Automation should support trust, not replace judgment.
- Public content must be practical, source-aware, and user-useful.

### `01_SYSTEM_GROWTH_WORKFLOW.md`

Current control role:

- Defines how raw information becomes reusable knowledge and public or reviewable content.

Document type:

- Workflow
- Product lifecycle
- Growth loop

What it currently controls:

- User need precedes source discovery.
- Collection is not the final goal.
- Lifecycle stages run from source discovery through feedback and knowledge improvement.
- News is a signal source, not the product itself.

### `02_DATA_SOURCE_AND_QUALITY.md`

Current control role:

- Defines source trust, source lifecycle, quality gates, duplicate handling, source normalization, LLM validation policy, and public-content contamination rules.

Document type:

- Quality gate
- Classification rule set
- Content safety policy

What it currently controls:

- Source evidence must be preserved.
- Discovery URL, source URL, canonical URL, and publishable link URL must be distinct.
- Duplicate noise and duplicate signal must be classified differently.
- Generic country-related news is not automatically WorkConnect-relevant.
- System messages must not leak into public content.

### `03_SYSTEM_ARCHITECTURE.md`

Current control role:

- Defines the high-level component structure and information flow.

Document type:

- System architecture
- Component responsibility
- Runtime topology

What it currently controls:

- Facebook is a delivery channel, not the product.
- Admin UI is the operator cockpit.
- Backend owns validation, normalization, workflow control, and publishing protection.
- Local LLM is optional and advisory.
- Source data and publishable content must remain separated.

### `04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`

Current control role:

- Defines local runtime safety rules while the local PC is both development and operations environment.

Document type:

- Runtime rule
- Safety checklist
- Verification guide

What it currently controls:

- Local changes can affect real Facebook posting and Telegram notifications.
- Backend/frontend health, UI visual checks, API communication, DB safety, scheduler safety, and protected-area boundaries must be verified.
- Runtime errors must be classified before fixing.
- Protected areas must stop instead of being patched blindly.

### `05_CODEX_HARNESS_GUIDE.md`

Current control role:

- Defines how Codex should work inside the project: area, mode, pre-review, risk classification, stop gates, verification, reporting, and candidate formatting.

Document type:

- Codex harness rule
- Session control
- Stop-gate policy

What it currently controls:

- Codex must not start by editing code.
- Every task must declare area, mode, focus, and timebox.
- The agent must classify risk as `SAFE_TO_PROCEED`, `PROCEED_WITH_LIMITS`, or `STOP_REQUIRES_USER_REVIEW`.
- Protected areas cannot be changed in unattended runs.
- DOC_ONLY sessions can identify future code candidates but must not implement them.

### `06_WORK_AREA_REGISTRY.md`

Current control role:

- Defines work areas, allowed files, forbidden files, allowed changes, forbidden changes, risk levels, checks, and stop conditions.

Document type:

- Work-area registry
- Module harness inventory
- Permission boundary map

What it currently controls:

- Maps project work into named areas such as `PRODUCT_DOCS`, `SYSTEM_ARCHITECTURE_DOCS`, `CONTENT_QUEUE`, `SOCIAL_NEWS_CANDIDATE`, `LIVING_DOMAIN`, `IMMIGRATION_DOMAIN`, `FACEBOOK_PUBLISHER`, and `SCHEDULER_BOT_STATE`.
- Separates low-risk documentation work from guarded fixes and high-risk protected changes.
- Prevents unrelated tasks from crossing into auth, publisher, scheduler, bot state, or destructive DB changes.

## 2. Harness Interpretation

For this project, a harness is a cognitive and operational control structure that determines how an AI coding agent should reason, classify, stop, execute, and report inside WorkConnect.

It is not:

- a long instruction document
- a general philosophy essay
- a replacement for implementation
- a hidden autopilot
- a tool for forcing completion at any cost

It is:

- a purpose-preserving architecture
- a routing layer for agent decisions
- a set of intervention triggers
- a compressed execution rule system
- a correction loop before patching
- a boundary system that protects product trust

### Mapping Harness Concepts to the Current Document Set

#### Purpose Function

Project mapping:

- The purpose function should live primarily in `00_PRODUCT_NORTH_STAR.md`.
- It should be stated as the first decision rule for all downstream classification:

```text
WorkConnect helps foreigners work, live, study, immigrate, or settle in the target country through practical, source-backed information.
```

Operational implication:

- Content that is merely country-related is not enough.
- A Korea article must help a foreign resident make a practical decision or reduce uncertainty.
- This prevents generic international news, travel stories, stock market news, and domestic politics from becoming Korea settlement content.

#### Governance Layer

Project mapping:

- Central governance should be distributed across:
  - `00_PRODUCT_NORTH_STAR.md`
  - `01_SYSTEM_GROWTH_WORKFLOW.md`
  - `02_DATA_SOURCE_AND_QUALITY.md`

Operational implication:

- Governance defines the worldview and product constraints.
- Module harnesses should not redefine the product purpose.
- If a module wants to publish something, it must inherit the product purpose first.

#### Trigger Cards

Project mapping:

- Trigger cards should be added mostly to `05_CODEX_HARNESS_GUIDE.md` and referenced by `06_WORK_AREA_REGISTRY.md`.

Examples:

- missing valid link
- source body missing
- same URL duplicate
- low WorkConnect relevance
- generic politics/economy/travel/crypto
- Facebook publisher touched
- scheduler interval touched
- auth touched
- DB destructive operation requested
- Telegram review spam detected

Operational implication:

- Trigger cards define when the harness intervenes.
- They should be short enough to execute during pre-review.

#### Execution Loop

Project mapping:

- The current execution loop already exists in `05_CODEX_HARNESS_GUIDE.md`.
- It should remain there, but should be tied more directly to trigger cards and work-area registry entries.

Current loop:

```text
work area selection
-> quick pre-review
-> risk classification
-> proceed or stop
-> limited execution
-> verification
-> report
```

Recommended interpretation:

- This is the Codex session-level harness.
- It should not be duplicated across every document.

#### Module Harness

Project mapping:

- `06_WORK_AREA_REGISTRY.md` is already the module harness registry.
- Each work area is a module harness.

Examples:

- `SOCIAL_NEWS_CANDIDATE` controls classification/scoring behavior.
- `CONTENT_QUEUE` controls candidate state and review workflow.
- `LIVING_DOMAIN` controls living information category rules.
- `IMMIGRATION_DOMAIN` controls official immigration review sensitivity.
- `FACEBOOK_PUBLISHER` is protected and cannot be changed casually.

Operational implication:

- Module harnesses execute.
- Central governance defines the philosophy.
- A module harness should not decide that generic travel content is useful if central governance says practical settlement value is required.

#### Correction Loop

Project mapping:

- Correction loop should be explicit in `01_SYSTEM_GROWTH_WORKFLOW.md`, `02_DATA_SOURCE_AND_QUALITY.md`, and `05_CODEX_HARNESS_GUIDE.md`.

Operational implication:

- When wrong content appears, the system should not immediately patch one URL or one title.
- It should classify the failure:
  - source problem
  - normalization problem
  - duplicate problem
  - classification problem
  - user-need scoring problem
  - review eligibility problem
  - publisher boundary problem

Then the patch should target the earliest failing layer.

#### Execution Card

Project mapping:

- Execution cards should be short operational blocks inside `05_CODEX_HARNESS_GUIDE.md` and `06_WORK_AREA_REGISTRY.md`.

Examples:

```text
EXECUTION CARD: Content Review Duplicate Suppression
Trigger: same candidate/link/status/score bucket repeats
Action: suppress Telegram review, log reason
Do not touch: Facebook publisher, scheduler, auth
Verify: same item second send is suppressed
```

Operational implication:

- Execution cards compress rules for repeated work.
- They keep the architecture executable rather than verbose.

## 3. Gap Analysis

### `00_PRODUCT_NORTH_STAR.md`

Already strong:

- Clear mission and product identity.
- Clear distinction between global product model and Korea first market.
- Good statement that WorkConnect is not a random news repost bot.
- Good automation philosophy.

Missing:

- A compact Purpose Function section that can be used as the first classification rule.
- A clear "Current Channel Scope" rule for WorkConnect Korea.
- A statement that product purpose has priority over source availability or social reach.

Should be added:

- `Purpose Function`
- `Current Target Country Rule`
- `Classification Principle`

Should not be changed:

- Do not make the product Korea-only.
- Do not remove the long-term global product direction.
- Do not turn the North Star into implementation detail.

Recommended change level:

- Light edit.

### `01_SYSTEM_GROWTH_WORKFLOW.md`

Already strong:

- Source-to-knowledge lifecycle is clear.
- User need precedes data collection.
- The document already says a country-related article is not automatically relevant.
- Feedback and knowledge improvement are included.

Missing:

- Explicit correction loop before patching.
- Trigger points where the workflow should stop, suppress, review, or archive.
- Clear separation between public delivery and operation notification.

Should be added:

- `Correction Loop`
- `Workflow Trigger Points`
- `Representative Candidate Rule`

Should not be changed:

- Do not turn this into a low-level implementation guide.
- Do not duplicate every quality gate already in `02_DATA_SOURCE_AND_QUALITY.md`.

Recommended change level:

- Light structural supplement.

### `02_DATA_SOURCE_AND_QUALITY.md`

Already strong:

- Strongest existing quality gate document.
- Good source evidence requirements.
- Good duplicate distinction between noise and signal.
- Good system-message contamination policy.
- Good low-relevance examples.

Missing:

- The classification worldview is implied but not named.
- Quality gates are strong, but trigger cards are not compressed.
- Domain-specific duplicate policy could be better separated from generic validation.

Should be added:

- `Classification Principle`
- `Trigger Cards`
- `Domain Duplicate Policy`
- `Review Eligibility Execution Card`

Should not be changed:

- Do not weaken URL/content/system-message gates.
- Do not let LLM validation override deterministic validation.
- Do not make all domains share the same duplicate policy.

Recommended change level:

- Structural supplement, not rewrite.

### `03_SYSTEM_ARCHITECTURE.md`

Already strong:

- Good component ownership.
- Facebook is correctly defined as a channel, not the product.
- Backend ownership of validation and workflow control is clear.
- Local LLM optional/advisory rule is clear.

Missing:

- Central governance versus module harness execution is not explicit.
- Architecture layers do not yet identify which documents control each layer.
- The relationship between content candidate, Telegram review, and Facebook publishing could be clearer as separate control paths.

Should be added:

- `Governance Layer`
- `Module Harness Map`
- `Public Delivery vs Operation Notification Boundary`

Should not be changed:

- Do not collapse Facebook into the product architecture.
- Do not make Local LLM required.
- Do not blur source data and publishable content.

Recommended change level:

- Light structural supplement.

### `04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`

Already strong:

- Strong runtime safety rules.
- Clear local-production risk.
- Good protected-area stop rules.
- Good DB, scheduler, UI, timestamp, and error handling rules.

Missing:

- Trigger cards could make the stop points easier to execute.
- It should explicitly point to `05` and `06` instead of repeating all harness logic.
- Some rules are long enough that they may be hard to apply during a fast pre-review.

Should be added:

- `Runtime Trigger Cards`
- `Runtime Execution Card`

Should not be changed:

- Do not remove existing safety checks.
- Do not weaken Facebook/Telegram external-impact warnings.
- Do not turn runtime guide into product philosophy.

Recommended change level:

- Mostly unchanged, with compressed trigger cards added.

### `05_CODEX_HARNESS_GUIDE.md`

Already strong:

- Clear area/mode/timebox format.
- Clear pre-review and stop classification.
- Good protected change policy.
- Good reporting and candidate format.

Missing:

- It describes the harness process, but not yet the harness concept: control reasoning path, not just task process.
- It lacks named trigger card and execution card sections.
- It could better state that correction loop comes before direct patching.

Should be added:

- `Harness Definition`
- `Trigger Card Format`
- `Execution Card Format`
- `Correction Loop Rule`

Should not be changed:

- Do not expand into a huge instruction book.
- Do not duplicate every work-area rule from `06`.
- Do not make Codex work longer by default.

Recommended change level:

- Moderate structural supplement.

### `06_WORK_AREA_REGISTRY.md`

Already strong:

- Practical work-area map.
- Clear protected areas.
- Useful area-specific allowed/forbidden boundaries.

Missing:

- Each area could benefit from a compact execution card.
- Some areas have risk level but not explicit trigger-to-stop behavior.
- Product governance inheritance is not explicit.

Should be added:

- `Module Harness Rule`
- Optional `Execution Card` block per high-use area.
- `Governance Inheritance Rule`

Should not be changed:

- Do not loosen protected areas.
- Do not mix product docs and runtime code permissions.
- Do not make every area equally complex.

Recommended change level:

- Incremental restructuring, not full rewrite.

## 4. Proposed Restructure Plan

### Recommended Changes for `00_PRODUCT_NORTH_STAR.md`

Add:

- `Purpose Function`
- `Current WorkConnect Korea Scope`
- `Classification Principle`

Minimal content target:

```text
Purpose Function:
WorkConnect helps foreigners work, live, study, immigrate, or settle in the target country through practical, source-backed information.

Classification Principle:
A topic is WorkConnect-relevant only when it helps the target user make a practical decision, reduce uncertainty, access support, or understand a source-backed rule in the target country.
```

### Recommended Changes for `01_SYSTEM_GROWTH_WORKFLOW.md`

Add:

- `Correction Loop Before Patching`
- `Workflow Trigger Points`

Minimal content target:

```text
When wrong content appears, classify which lifecycle stage failed before patching:
source -> normalization -> duplicate -> domain classification -> user value -> review eligibility -> public delivery.
```

### Recommended Changes for `02_DATA_SOURCE_AND_QUALITY.md`

Add:

- `Classification Principle`
- `Trigger Cards`
- `Domain Duplicate Policy`

Candidate trigger cards:

- invalid link
- content missing
- system text present
- same URL repeat
- same topic different source
- non-Korea global reference
- generic travel/crypto/politics/economy
- official notice updated

### Recommended Changes for `03_SYSTEM_ARCHITECTURE.md`

Add:

- `Governance Layer`
- `Module Harness Map`
- `Public Delivery Boundary`

Minimal content target:

```text
Central governance documents define purpose and classification.
Module harness documents execute area-specific rules.
Facebook publishing is public delivery.
Telegram review is operation control.
They must not be treated as the same pipeline stage.
```

### Recommended Changes for `04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`

Add:

- `Runtime Trigger Cards`
- `Runtime Execution Card`

Keep most existing content unchanged.

### Recommended Changes for `05_CODEX_HARNESS_GUIDE.md`

Add:

- `Harness Definition`
- `Trigger Card Format`
- `Execution Card Format`
- `Correction Loop Rule`

Keep existing modes, pre-review, session cycle, stop report, and code task candidate rules.

### Recommended Changes for `06_WORK_AREA_REGISTRY.md`

Add:

- `Module Harness Rule`
- `Governance Inheritance Rule`
- Small execution cards only for high-frequency areas:
  - `SOCIAL_NEWS_CANDIDATE`
  - `CONTENT_QUEUE`
  - `DATA_SOURCE_QUALITY` if added as a registry area
  - `LIVING_DOMAIN`
  - `IMMIGRATION_DOMAIN`
  - `TELEGRAM_REPORTING`

Avoid adding heavy execution cards to every area.

## 5. Risk Analysis

### Risk: Over-expanding Documents

If every document becomes a full harness essay, Codex will have too much text to apply under time pressure.

Mitigation:

- Keep central governance short.
- Use trigger cards and execution cards for repeated operational rules.
- Put detailed diagnostics in walkthrough reports, not architecture documents.

### Risk: Making Documents Too Philosophical

Harness concepts are useful only if they change execution behavior.

Bad outcome:

- Documents describe purpose beautifully but do not stop wrong public posts.

Mitigation:

- Every philosophical principle should map to at least one gate, trigger, stop condition, or execution card.

### Risk: Changing Existing Working Rules

The current docs already protect key boundaries. A restructure could accidentally weaken them.

High-risk examples:

- loosening Facebook publisher protection
- making Local LLM required
- treating Telegram review as Facebook publishing
- weakening source URL/content gates
- allowing generic Korea-related news because it may create reach

Mitigation:

- Use minimal edits.
- Preserve protected-area wording.
- Add cross-references rather than rewriting working sections.

### Risk: Confusing Product Purpose With Social Posting Automation

WorkConnect is a structured information platform. Facebook is only a delivery channel.

If social posting becomes the implicit product purpose, the system will optimize for fresh posts instead of useful settlement information.

Mitigation:

- Keep Purpose Function in `00`.
- Keep content classification in `02`.
- Keep Facebook publisher protected in `06`.
- Keep public delivery and operation notification separated in `03`.

### Risk: Korea Scope Confusion

The product is global in direction but Korea is the current channel.

Risk:

- Non-Korea global reference content enters WorkConnect Korea review/public posting.

Mitigation:

- Add a current target country rule.
- Keep global references as future expansion signals, not current Korea public content.

### Risk: Correction Loop Skipped

When a bad item appears, a direct one-off patch may hide the real failure.

Example:

- Blocking one Travel And Tour World URL does not fix generic travel classification.

Mitigation:

- Add correction loop rule:
  - classify failure layer first
  - patch earliest failing layer
  - add test/sample if possible

## 6. Contradictions or Ambiguities to Preserve for Human Review

### Automatic Publishing Boundary

`01_SYSTEM_GROWTH_WORKFLOW.md` and `03_SYSTEM_ARCHITECTURE.md` mention automatic publishing for safe high-confidence content.

`05_CODEX_HARNESS_GUIDE.md` and `06_WORK_AREA_REGISTRY.md` treat content publisher and Facebook publisher behavior as protected.

This is not necessarily a contradiction, but it needs clearer wording:

- Product architecture may allow automatic publishing as a future or controlled capability.
- Harness execution must still protect publisher behavior from unattended changes.
- Current WorkConnect Korea sensitive/living/immigration review flows should not be bypassed.

### Global Product vs Korea Current Channel

`00_PRODUCT_NORTH_STAR.md` correctly says WorkConnect is not Korea-only.

`02_DATA_SOURCE_AND_QUALITY.md` correctly filters non-Korea content for the current channel.

This should be made explicit:

- Global product model remains broad.
- Current channel target country is Korea.
- Non-Korea references may be stored as future/global reference signals but must not enter Korea public review by default.

### Harness Process vs Harness Architecture

`05_CODEX_HARNESS_GUIDE.md` is strong as a process guide.

It does not yet fully explain harness as a reasoning-path control architecture.

This should be added without making the document longer than necessary.

## 7. Recommended Next Codex Task

Use this second-stage prompt later to update 00~06. Do not execute it as part of this review.

```text
AREA: CODEX_HARNESS_DOCS + PRODUCT_DOCS + SYSTEM_ARCHITECTURE_DOCS
MODE: DOC_ONLY
PURPOSE FUNCTION:
Update DOC/architecture/00~06 using the findings from DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md.

FOCUS:
Make the architecture documents more executable as a WorkConnect harness system while preserving existing working rules.

READ FIRST:
- DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md
- DOC/architecture/00_PRODUCT_NORTH_STAR.md
- DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/03_SYSTEM_ARCHITECTURE.md
- DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md

ALLOWED CHANGES:
- Edit only DOC/architecture/00~06.
- Documentation only.
- Minimal edits preferred.

FORBIDDEN CHANGES:
- No runtime code.
- No DB changes.
- No scheduler changes.
- No Facebook publisher changes.
- No auth changes.
- No config/env changes.
- No new broad rewrite.

REQUIRED UPDATES:
1. Add a compact Purpose Function to 00.
2. Add Current WorkConnect Korea scope without making the product Korea-only.
3. Add Correction Loop before patching to 01.
4. Add Classification Principle and trigger-card style quality gates to 02.
5. Add Governance Layer / Module Harness mapping to 03.
6. Add compressed runtime trigger cards to 04.
7. Add Harness Definition, Trigger Card Format, Execution Card Format, and Correction Loop Rule to 05.
8. Add Module Harness Rule and Governance Inheritance Rule to 06.

SUCCESS CRITERIA:
- Existing working rules are preserved.
- Protected areas remain protected.
- The docs become easier for Codex to execute, not merely longer.
- WorkConnect remains a practical source-backed settlement information platform.
- Generic international news, travel, crypto, domestic politics, and low-value economy content remain blocked from Korea settlement review unless they meet user-need/actionability gates.

STOP CONDITIONS:
- If a proposed edit would weaken protected boundaries, stop.
- If the change requires runtime code, stop.
- If contradictions cannot be resolved without product decision, record the ambiguity instead of silently resolving it.

REPORT:
- Files edited
- Sections added
- Sections intentionally left unchanged
- Ambiguities preserved
- Suggested next CODE_TASK_CANDIDATE items, if any
```

## 8. Review Conclusion

The current architecture set is already close to a harness system.

The main missing piece is not more documentation volume. The missing piece is a clearer control structure:

```text
Purpose Function
-> Governance Layer
-> Trigger Cards
-> Module Harnesses
-> Execution Cards
-> Correction Loop
-> Verification Report
```

Recommended approach:

- preserve current documents
- add compact executable sections
- avoid full rewrites
- keep product purpose above social posting automation
- make classification decisions traceable to the purpose function

This should help WorkConnect prevent wrong public posts, especially cases where generic international news, travel, economy, politics, or low-value lifestyle content is incorrectly treated as Korea settlement content.
