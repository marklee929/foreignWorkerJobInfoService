AREA: CODEX_HARNESS_DOCS + PRODUCT_DOCS + SYSTEM_ARCHITECTURE_DOCS
MODE: DOC_ONLY
PURPOSE FUNCTION:
Create a review document that evaluates how /DOC/architecture should evolve into a practical harness system.

FOCUS:
Do not modify existing architecture documents yet.
First, create a new review document under DOC/architecture/ that analyzes how the current architecture documents should be reorganized or supplemented using the Brain Pump harness concepts.

REFERENCE MATERIAL:
Use the attached Brain Pump learning notes only as conceptual background.
Do not copy or summarize them as diary content.
Extract only reusable architecture concepts:

- Harness is not Hades.
- Harness is not a long instruction document.
- Harness is a cognitive architecture that controls the reasoning path of an AI coding agent.
- Purpose Function comes before Data Schema.
- Validation is a rule problem, but Classification is a worldview problem.
- Good harness prevents loss of purpose as complexity increases.
- Central Governance manages philosophy.
- Module Harnesses execute.
- Trigger cards define when the harness intervenes.
- Execution cards compress operational rules.
- Correction loop comes before 1:1 patching.
- Documents should become executable control structures, not essays.

TARGET FILES TO REVIEW:
- DOC/architecture/00_PRODUCT_NORTH_STAR.md
- DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/03_SYSTEM_ARCHITECTURE.md
- DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md

CREATE NEW FILE:
DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md

ALLOWED CHANGES:
- Create only the new review document.
- Documentation only.
- No edits to existing architecture documents.
- No runtime code changes.
- No DB changes.
- No scheduler changes.
- No Facebook publisher changes.
- No auth changes.
- No config/env changes.

REVIEW DOCUMENT MUST INCLUDE:

1. Current Architecture Summary
- What each existing architecture document currently controls.
- Whether each document is product direction, workflow, quality gate, runtime rule, Codex rule, or work-area registry.

2. Harness Interpretation
- Define what “harness” means for this project.
- Explain how Purpose Function, Governance, Trigger, Execution Loop, Module Harness, Correction Loop, and Execution Card should map into the current document set.

3. Gap Analysis
For each architecture document, explain:
- What is already strong.
- What is missing.
- What should be added.
- What should not be changed.
- Whether the document should be lightly edited, structurally reorganized, or left mostly unchanged.

4. Proposed Restructure Plan
- Recommended changes for each of 00~06.
- Prioritize minimal edits over full rewrite.
- Identify any document that may need a new section such as:
  - Purpose Function
  - Governance Layer
  - Trigger Cards
  - Execution Card
  - Classification Principle
  - Correction Loop

5. Risk Analysis
- Risks of over-expanding documents.
- Risks of making documents too philosophical.
- Risks of changing existing working rules.
- Risks of confusing product purpose with social posting automation.

6. Recommended Next Codex Task
Write a second-stage prompt that can be used later to actually update 00~06, but do not execute it yet.

SUCCESS CRITERIA:
- The new document helps a human reviewer decide how to update 00~06.
- It does not rewrite existing docs.
- It converts Brain Pump concepts into operational architecture language.
- It preserves WorkConnect’s product identity.
- It helps prevent wrong public posts, such as generic international news being treated as Korea settlement content.
- It keeps the architecture executable, not merely more verbose.

STOP CONDITIONS:
- If existing documents appear contradictory, record the contradiction instead of silently resolving it.
- If the task requires code changes, stop.
- If the task requires DB/schema changes, stop.
- If publisher, scheduler, auth, or env/config are involved, stop.
- If the review becomes a Brain Pump diary summary instead of an architecture review, stop and rewrite as architecture review.

REPORT REQUIRED:
After creating the document, report:
1. File created
2. Files inspected
3. Main findings
4. Suggested next step
5. Any uncertainty

MODE: READ_ONLY_AUDIT
REASONING: HIGH
SPEED: STANDARD

REPOSITORY:
marklee929/foreignWorkerJobInfoService

PURPOSE FUNCTION:
Rebuild Codex's understanding of this repository after local Codex history/context was reset.
The goal is to understand the project structure, architecture documents, harness rules, current implementation state, and safe working boundaries before making any code or document changes.

IMPORTANT:
Do not modify any files.
Do not create files.
Do not run migrations.
Do not start or stop services.
Do not change runtime code.
Do not commit or push.
This task is read-only project review only.

PRIMARY RULE:
Before reviewing source code, always inspect the architecture documents first.

You must review the following files first, in this order:

1. DOC/architecture/00_PRODUCT_NORTH_STAR.md
2. DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
3. DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
4. DOC/architecture/03_SYSTEM_ARCHITECTURE.md
5. DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
6. DOC/architecture/05_CODEX_HARNESS_GUIDE.md
7. DOC/architecture/06_WORK_AREA_REGISTRY.md

SPECIAL FOCUS:
Pay special attention to the harness-related architecture:

- The project uses a harness approach.
- Harness is not a long instruction document.
- Harness is a cognitive architecture that controls how Codex should reason before editing.
- Purpose Function must come before Data Schema or implementation.
- Validation is a rule problem.
- Classification is a product-worldview problem.
- Good harness prevents loss of purpose as complexity increases.
- Central Governance manages philosophy and boundaries.
- Module Harnesses execute within defined areas.
- Trigger Cards define when Codex should intervene, stop, or escalate.
- Execution Cards compress operational rules for actual work.
- Correction Loop must come before 1:1 patching.
- Codex must not treat task completion as more important than preserving system boundaries.

PROJECT IDENTITY:
WorkConnect is not a random news repost bot.
WorkConnect is a source-backed work-and-settlement information platform for foreigners who work, live, study, immigrate, or settle abroad.
The first market is Korea, but the architecture should not become Korea-only.

PUBLIC CONTENT RULE:
A topic is not WorkConnect-relevant just because it mentions Korea, foreigners, travel, international affairs, or news.
A content item is WorkConnect-relevant only if it helps a foreign resident, worker, student, migrant, or mover make a practical decision or reduce uncertainty.

Examples:
- visa update: relevant
- labor rights notice: relevant
- housing contract guide: relevant
- health insurance explanation: relevant
- banking/telecom/local support guide: relevant
- generic politics: usually not relevant
- generic economy news: usually not relevant
- international danger/travel ranking: usually not relevant unless directly tied to Korea settlement/work/living safety
- social media trend: signal only unless source-backed and user-actionable

REVIEW TARGETS AFTER ARCHITECTURE:
After reading /DOC/architecture, inspect the repository structure and identify major areas:

- backend/API structure
- collectors
- content candidate pipeline
- lifestyle information pipeline
- immigration information pipeline
- social/news pipeline
- admin UI
- status code system
- Telegram review/reporting
- Facebook publishing boundary
- scheduler/bot state
- storage/generated or card generation related files
- DB migration and schema directories
- DOC/walkthrough and DOC/to-be if relevant

DO NOT DEEP-DIVE EVERYTHING.
This is a project orientation pass, not a full code audit.
Focus on understanding boundaries, responsibilities, and risk areas.

REQUIRED OUTPUT:
Create a project review report in your response only.
Do not write it to a file yet.

The report must include:

1. Architecture First Review
- Summarize the role of each DOC/architecture file.
- Explain how the harness rules should control future Codex tasks.
- Identify which document should be checked before different types of work.

2. Project Structure Map
- List major directories.
- Explain what each major area appears to do.
- Identify backend, frontend, data, automation, and documentation boundaries.

3. Current Product Understanding
- Explain what WorkConnect is.
- Explain what it is not.
- Explain how content should flow from source data to public output.

4. Harness Operating Rule for Future Tasks
Define a default rule Codex should follow before any future task:

Architecture review
→ work area selection
→ purpose function confirmation
→ risk classification
→ allowed/forbidden file check
→ execution or stop
→ verification
→ report

5. Protected Areas
List areas that must not be changed without explicit user approval:
- admin auth
- device approval
- Facebook publisher
- Facebook token handling
- scheduler
- bot state transitions
- content publisher
- destructive DB migration
- env/secrets
- external API behavior
- automatic publishing selection

6. Suggested Work Area Registry Usage
Explain how to select AREA and MODE before future tasks.
Use examples:
- DOC_ONLY
- READ_ONLY_AUDIT
- LOW_RISK_FIX
- GUARDED_FIX
- PROTECTED_CHANGE

7. Immediate Risks or Confusions
List any architecture conflicts, unclear boundaries, missing docs, or places where future Codex work may accidentally cross protected boundaries.

8. Recommended Next Step
Suggest the next safe task.
Do not execute it.

STOP CONDITIONS:
Stop and report instead of continuing if:
- architecture documents conflict with each other
- source code suggests behavior that violates architecture docs
- protected areas appear necessary to inspect deeply
- the task would require code changes
- the repository structure is too large to review safely in one pass
- the review starts becoming implementation work

FINAL LINE:
End the report with:

"Project context rebuilt. Future work must start from /DOC/architecture and declared AREA/MODE/PURPOSE FUNCTION."

AREA: CODEX_HARNESS_DOCS + PRODUCT_DOCS + SYSTEM_ARCHITECTURE_DOCS
MODE: DOC_ONLY
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
Archive the current DOC/architecture/00~06 documents, then recreate DOC/architecture/00~06 as a clean practical WorkConnect harness architecture set.

The goal is to remove confusion between old architecture notes and the new harness operating structure.

This task must preserve the old documents in DOC/archives and leave only the newly rewritten 00~06 architecture files in DOC/architecture.

PRIMARY RULE:
Architecture comes before source code.

Do not inspect or modify runtime source code for this task.
Do not implement any runtime behavior.
This is a documentation-only architecture restructuring task.

READ FIRST:
1. DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md
2. DOC/architecture/05_CODEX_HARNESS_GUIDE.md
3. DOC/architecture/06_WORK_AREA_REGISTRY.md
4. DOC/architecture/00_PRODUCT_NORTH_STAR.md
5. DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
6. DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
7. DOC/architecture/03_SYSTEM_ARCHITECTURE.md
8. DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md

ARCHIVE REQUIREMENT:
Before rewriting the architecture documents, preserve the current versions.

Move or copy the existing files:

- DOC/architecture/00_PRODUCT_NORTH_STAR.md
- DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/03_SYSTEM_ARCHITECTURE.md
- DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md

into:

DOC/archives/architecture/YYYY-MM-DD/

Use the current date for YYYY-MM-DD.

Recommended archived filenames:

- 00_PRODUCT_NORTH_STAR.md
- 01_SYSTEM_GROWTH_WORKFLOW.md
- 02_DATA_SOURCE_AND_QUALITY.md
- 03_SYSTEM_ARCHITECTURE.md
- 04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
- 05_CODEX_HARNESS_GUIDE.md
- 06_WORK_AREA_REGISTRY.md

After archiving, recreate new files with the same original names under DOC/architecture/.

Do not delete historical content without preserving it in the archive.

Keep DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md in place as the restructure review reference unless a direct conflict requires reporting.

PROJECT CONTEXT TO PRESERVE:
WorkConnect is a practical, source-backed work-and-settlement information platform for foreigners who work, live, study, immigrate, or settle abroad.

Korea is the first active market and current public channel target, but WorkConnect must not become Korea-only.

WorkConnect is not:

- a random news repost bot
- a generic Korea news feed
- a travel blog
- a sensational issue feed
- an unverified visa/legal advice site
- a social-posting automation project

A topic is not WorkConnect-relevant only because it mentions Korea, foreigners, travel, international affairs, or news.

A topic becomes WorkConnect-relevant only when it helps a foreign worker, resident, student, migrant, or mover:

- make a practical decision
- reduce uncertainty
- understand what to check next
- access source-backed work, visa, housing, healthcare, banking, labor, public service, safety, or daily-life guidance

HARNESS CONCEPT TO APPLY:
Use the harness concepts already distilled in DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md.

Do not copy Brain Pump diary language into the documents.
Do not summarize the PDF notes.
Convert the concepts into operational architecture rules.

Required harness concepts:

- Harness is not a long instruction document.
- Harness controls Codex's reasoning path before editing.
- Purpose Function comes before Data Schema and implementation.
- Validation is a rule problem.
- Classification is a product-worldview problem.
- Central Governance manages product philosophy and boundaries.
- Module Harnesses execute within declared work areas.
- Trigger Cards define when Codex must intervene, stop, downgrade, review, or escalate.
- Execution Cards compress repeated operational rules.
- Correction Loop comes before one-to-one patching.
- A good harness prevents the project from losing purpose as complexity increases.

ADDITIONAL CONTEXT FROM PROJECT REBUILD REVIEW:
Codex has already rebuilt project context and found:

1. /DOC/architecture must be treated as governance, not background reading.
2. Future work must start from architecture review and declared AREA/MODE/PURPOSE FUNCTION.
3. There is an architecture tension between social_news.candidate and content.content_candidate.
   - content.content_candidate appears intended to be the final publishable object.
   - social/news direct publishing paths may still exist.
   - Do not resolve this tension in this DOC_ONLY task.
   - Preserve it as a future READ_ONLY_AUDIT target.
4. Python admin_server.py contains many responsibilities in one file:
   - auth
   - bot controls
   - Telegram callbacks
   - LLaMA control
   - content sync
   - publishing
   - cleanup
   - dashboards

   Same file does not mean same work area.
   Strengthen the rule that Codex may modify only the selected responsibility inside a multi-responsibility file.

5. Java Spring Boot and Python pipelines both contain content approval / collection / Telegram / migration-related flows.
   Future implementation tasks must clarify ownership before editing either path.
6. Existing untracked walkthrough/archive files must not be touched unless explicitly requested.

ALLOWED CHANGES:
Allowed paths:

- DOC/architecture/00_PRODUCT_NORTH_STAR.md
- DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/03_SYSTEM_ARCHITECTURE.md
- DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md
- DOC/archives/architecture/YYYY-MM-DD/

Documentation only.
Archive old 00~06 first.
Then write clean new 00~06 files.

FORBIDDEN CHANGES:
- No runtime code changes
- No DB changes
- No migrations
- No scheduler changes
- No Facebook publisher changes
- No Telegram runtime behavior changes
- No content publisher behavior changes
- No auth changes
- No env/config changes
- No service start/stop
- No changes outside DOC/architecture/00~06 and DOC/archives/architecture/YYYY-MM-DD/
- No deletion of old architecture content before archiving
- No touching DOC/walkthrough or unrelated archive files
- No resolving social_news.candidate vs content.content_candidate ownership in this task
- No deciding Python vs Java pipeline ownership in this task

NEW DOCUMENT SET DESIGN:
After archiving, rewrite DOC/architecture/00~06 with clear responsibilities.

The new document roles must be:

```text
00 = Product Constitution / Purpose Function
01 = Growth Workflow / Correction Loop
02 = Data Quality / Classification Worldview
03 = System Boundary / Governance Map
04 = Local Runtime Safety / Runtime Triggers
05 = Codex Harness Engine / Agent Operating Rules
06 = Work Area Registry / Module Harness Map

CROSS-DOCUMENT CONSISTENCY RULES:

00 defines product purpose and classification worldview.
01 defines growth loop and correction loop.
02 defines quality gates and classification triggers.
03 defines component boundaries and governance map.
04 defines local runtime safety.
05 defines Codex operating harness.
06 defines module/work-area harness boundaries.

Do not make every document explain everything.
Avoid duplicated long explanations.
Use compact executable sections.

REQUIRED DESIGN BY FILE:

DOC/architecture/00_PRODUCT_NORTH_STAR.md

Rewrite as the product constitution.

Must include:

Core Mission
Purpose Function
Current WorkConnect Korea Scope
Global Product Direction
Target Users
Classification Principle
Product Identity
What WorkConnect Must Not Become
Success Criteria

Must clearly state:

WorkConnect global direction remains intact.
WorkConnect Korea is the current active channel/market.
Generic global or non-Korea content may be stored as future/global reference signals, but must not enter WorkConnect Korea public review by default.
Source availability or social reach must not override product purpose.
A topic is WorkConnect-relevant only when it helps the target user make a practical decision or reduce uncertainty.

Do not include implementation details.

DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md

Rewrite as the growth workflow and correction-loop document.

Must include:

Purpose
Core Lifecycle
Workflow Stages
User Need Before Source Collection
Correction Loop Before Patching
Workflow Trigger Points
Representative Candidate Rule
Feedback and Knowledge Improvement
Success Criteria

Correction Loop must require classifying the failed lifecycle stage first:

source discovery
→ raw collection
→ normalization
→ duplicate classification
→ domain classification
→ user value evaluation
→ review eligibility
→ public delivery

Patch the earliest failing layer.

Do not duplicate all quality gates from 02.

DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md

Rewrite as the data quality and classification worldview document.

Must include:

Purpose
Source Evidence Rule
Source Trust Levels
URL and Link Boundary
Content Availability Gate
Duplicate Policy
Classification Principle
Quality Trigger Cards
Domain Duplicate Policy
Review Eligibility Execution Card
System Message Contamination Policy
LLM Validation Policy
Content Candidate Readiness

Must clearly distinguish:

Validation = whether data is usable
Classification = what the data means inside WorkConnect

A valid article may still be irrelevant.

Must include handling for:

generic international news
travel ranking
politics
economy
crypto
generic lifestyle
weak source
missing source body
system text contamination

Do not weaken existing rules for:

URL validity
content availability
system-message contamination
deterministic validation before LLM
source evidence preservation
DOC/architecture/03_SYSTEM_ARCHITECTURE.md

Rewrite as the system boundary and governance map document.

Must include:

Purpose
High-Level Architecture
Governance Layer
Document-to-Layer Control Map
Module Harness Map
Main Components
Public Delivery vs Operation Notification Boundary
Backend Responsibility
Admin UI Responsibility
Local LLM Advisory Rule
Source Data vs Publishable Content Boundary
Facebook as Channel, Not Product
Target Architecture Direction

Must clearly state:

Facebook publishing is public delivery.
Telegram review/reporting is operation control.
They must not be treated as the same pipeline stage.
Backend validates and controls workflow, but protected publishing behavior cannot be changed casually.
Local LLM remains optional and advisory.

Do not collapse Facebook into the product.

DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md

Rewrite as the local runtime safety document.

Must include:

Purpose
Current Runtime Assumption
Core Runtime Rule
Local Server Safety
Frontend-Backend Communication Rule
Admin UI Visual Check Rule
Runtime Trigger Cards
Runtime Execution Card
External Output Risk Trigger
Runtime Boundary Error Trigger
DB Safety Rule
Migration Rule
Scheduler and Polling Rule
Facebook and Telegram External Impact Rule
Local LLaMA/Ollama Rule
Completion Report Requirement
Stop Rule

This document should point to 05 and 06 for harness operation instead of duplicating all harness logic.

Keep practical runtime safety rules strong.

DOC/architecture/05_CODEX_HARNESS_GUIDE.md

Rewrite as the Codex harness engine document.

Must include:

Purpose
Mandatory Architecture-First Rule
Harness Definition
Required Input Format with PURPOSE FUNCTION
Work Modes
Quick Pre-Review Gate
Risk Decision
Trigger Card Format
Execution Card Format
Correction Loop Rule
Multi-Responsibility File Boundary Rule
One-Hour Session Cycle
Stop Report
Reporting Policy
Telegram Summary Policy
Conditional Commit/Push Rule
Completion Report

The Required Input Format must include:

PURPOSE FUNCTION:
AREA:
MODE:
FOCUS:
TIMEBOX:
SUCCESS CRITERIA:
STOP CONDITIONS:

Must clearly state:

Future Codex work must start from /DOC/architecture and declared PURPOSE FUNCTION / AREA / MODE.
Codex must not start from source code unless the architecture boundary is already known.
Same file does not mean same responsibility.
Codex may modify only the selected responsibility inside a multi-responsibility file.

Do not remove useful existing work modes, stop rules, session cycle, reporting rules, or protected-change policy.

DOC/architecture/06_WORK_AREA_REGISTRY.md

Rewrite as the module harness registry.

Must include:

Purpose
Risk Levels
Governance Inheritance Rule
Module Harness Rule
Multi-Responsibility File Rule
Work Modes Reference
Protected Areas
Work Areas
Future Audit Targets
Required Checks
Stop Conditions

Must include or preserve areas for:

PRODUCT_DOCS
SYSTEM_ARCHITECTURE_DOCS
CODEX_HARNESS_DOCS
TO_BE_DOCS
DASHBOARD_STATUS
ADMIN_AUTH
FACEBOOK_STATUS
FACEBOOK_PUBLISHER
SOCIAL_NEWS_COLLECTOR
SOCIAL_NEWS_CANDIDATE
CONTENT_QUEUE
CONTENT_PUBLISHER
OCCUPATION_DICTIONARY
IMMIGRATION_DOMAIN
LIVING_DOMAIN
CONTENT_CARD_GENERATION
LLAMA_STATUS
SCHEDULER_BOT_STATE
TELEGRAM_REPORTING

CONTENT_CARD_GENERATION must cover:

Allowed:

card template config
card text validation
generated image output path
source/date/link display
language validation
preview-only generation

Forbidden:

publishing cards automatically
changing Facebook publisher payload
bypassing content candidate approval
generating public cards directly from raw source
using internal diagnostic/status text on public cards

Future Audit Targets must include:

AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Verify whether content.content_candidate is acting as the final publishable content object or merely duplicating social_news.candidate.
TIMEBOX: 60m

Also preserve the Python vs Java workflow ownership ambiguity as a future implementation audit target.

Do not add heavy execution cards to every area.
Keep the registry usable.

SUCCESS CRITERIA:

Existing architecture files 00~06 are archived under DOC/archives/architecture/YYYY-MM-DD/.
New architecture files 00~06 exist under DOC/architecture/.
DOC/architecture contains the clean new active architecture set.
Existing working rules are preserved in rewritten form.
Protected areas remain protected.
Documents become easier for Codex to execute, not merely longer.
Every future Codex task is clearly required to start from /DOC/architecture.
PURPOSE FUNCTION / AREA / MODE becomes the default task entry point.
Generic international news, travel ranking, domestic politics, low-value economy, crypto, or generic lifestyle content cannot become WorkConnect Korea public content unless it passes user-need/actionability gates.
social_news.candidate vs content.content_candidate ownership question is preserved as a future audit target.
admin_server.py and similar large files are treated as multi-responsibility files with section-level boundaries.
Python vs Java workflow ownership ambiguity is preserved for future implementation tasks, not silently resolved.

STOP CONDITIONS:
Stop and report instead of editing if:

old 00~06 cannot be archived safely
a proposed rewrite weakens protected boundaries
runtime code must be changed
DB/schema changes are needed
publisher, scheduler, auth, bot state, env/config, or external API behavior would be affected
contradictions cannot be resolved without product decision
documents become significantly longer without improving execution clarity
the task requires resolving social_news.candidate vs content.content_candidate ownership
the task requires deciding Python vs Java pipeline ownership
the task requires touching files outside DOC/architecture/00~06 and DOC/archives/architecture/YYYY-MM-DD/

REPORT AFTER COMPLETION:
Report:

Files inspected
Files archived
Archive path used
Files recreated
Summary of new role per file
Existing sections intentionally preserved in rewritten form
Ambiguities preserved
Remaining risks
Suggested next CODE_TASK_CANDIDATE items

Suggested next CODE_TASK_CANDIDATE should include, but not execute:

AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Verify whether content.content_candidate is acting as the final publishable content object or merely duplicating social_news.candidate.
TIMEBOX: 60m

FINAL LINE:
End the report with:

"Architecture harness reset completed. Future work must start from /DOC/architecture and declared PURPOSE FUNCTION / AREA / MODE."

AREA: CODEX_HARNESS_DOCS + PRODUCT_DOCS
MODE: DOC_ONLY
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
Create a correction-loop documentation area that captures harness improvement opportunities discovered during architecture review, without modifying runtime code or active architecture documents.

The goal is not to directly fix individual errors.
The goal is to convert discovered issues into reusable harness improvements that can prevent similar failures across the project.

PRIMARY RULE:
Do not modify source code.
Do not modify DB.
Do not modify runtime behavior.
Do not modify DOC/architecture/00~06 in this task.
Create documentation only.

READ FIRST:
1. DOC/architecture/00_PRODUCT_NORTH_STAR.md
2. DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
3. DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
4. DOC/architecture/03_SYSTEM_ARCHITECTURE.md
5. DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
6. DOC/architecture/05_CODEX_HARNESS_GUIDE.md
7. DOC/architecture/06_WORK_AREA_REGISTRY.md
8. DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md

CREATE FOLDER:
DOC/correction-loop/

CREATE FILES:
1. DOC/correction-loop/README.md
2. DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md

DOCUMENT PURPOSE:
This folder stores discovered problems, architecture gaps, harness weaknesses, and improvement candidates before they become direct code or architecture changes.

This is not a bug-fix folder.
This is not an implementation task folder.
This is a correction-loop and harness-improvement folder.

The correction-loop process is:

```text
issue observed
-> identify failed layer
-> check whether harness missed a rule
-> define reusable improvement
-> review with human
-> promote to architecture/work-area/code task only after approval

ALLOWED CHANGES:

Create DOC/correction-loop/
Create README.md
Create 2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md
Documentation only

FORBIDDEN CHANGES:

No runtime code
No DB changes
No migrations
No scheduler changes
No Facebook publisher changes
No Telegram runtime behavior changes
No content publisher changes
No auth changes
No env/config changes
No source code inspection beyond what is necessary to understand documentation boundaries
No modification to DOC/architecture/00~06
No implementation of improvement candidates

README.md MUST INCLUDE:

Purpose
Explain that DOC/correction-loop stores correction-loop findings, harness improvement candidates, recurring failure patterns, and escalation notes.
Difference from Direct Fixes
Explain:
Direct fix:
"This line is wrong. Fix it."

Correction loop:
"This failure shows the harness missed a reusable rule. Identify the failed layer, strengthen the harness, then decide whether code should change."
Correction Loop Stages
Include:
observe
-> classify failed layer
-> identify missing harness rule
-> define reusable improvement
-> review with human
-> promote to architecture/work-area/code task
-> verify recurrence prevention
Failed Layer Categories
Include:
product purpose
source discovery
raw collection
normalization
duplicate classification
domain classification
user value evaluation
review eligibility
public delivery
operation notification
runtime boundary
work-area boundary
multi-responsibility file boundary
verification/reporting
Promotion Rules
Explain when a finding should become:
architecture update
work-area registry update
trigger card
execution card
read-only audit
guarded code fix
protected change request

2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md MUST INCLUDE:

Context
This review follows the architecture harness reset and review of DOC/architecture/00~06.
Immediate Small Improvements
Include these five known improvement candidates:

A. Strengthen Required Input Rule in 05
Issue:
Current wording may allow Codex to infer missing required fields too freely.

Improvement:
If PURPOSE FUNCTION, AREA, or MODE is missing, Codex must not edit files. It may only run READ_ONLY_AUDIT or ask for clarification.

Target:
DOC/architecture/05_CODEX_HARNESS_GUIDE.md

Type:
Architecture update candidate

B. Add Target Country Mismatch Trigger in 02
Issue:
Global or non-Korea content may still enter WorkConnect Korea review/publishing if target-country fit is not explicit.

Improvement:
Add a quality trigger card for Target Country Mismatch.

Target:
DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md

Type:
Trigger card candidate

C. Add Local Test Touches Real External Output Trigger in 04
Issue:
Local tests may accidentally send real Facebook posts, Telegram messages, or external API calls.

Improvement:
Add runtime trigger requiring dry-run, mock mode, or explicit approval before any real external output.

Target:
DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md

Type:
Runtime trigger candidate

D. Clarify Final Public Message/Link Ownership in 03
Issue:
social_news.candidate vs content.content_candidate ownership is still a known ambiguity.

Improvement:
State that final public message and final publishable link should be owned by content management, while preserving implementation ambiguity for future audit.

Target:
DOC/architecture/03_SYSTEM_ARCHITECTURE.md

Type:
Architecture clarification candidate

E. Mark 07 as Review Reference
Issue:
07_HARNESS_RESTRUCTURE_REVIEW.md may be mistaken for active rules.

Improvement:
Add status note: "Review reference. Active architecture rules are in 00~06."

Target:
DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md

Type:
Documentation status candidate

General Improvement Extraction
Review the active architecture documents and extract additional improvement candidates.

For each candidate, use this format:

## Candidate: [short name]

Observed issue:
...

Failed layer:
...

Missing harness rule:
...

Reusable improvement:
...

Suggested target:
...

Promotion type:
- architecture update
- work-area registry update
- trigger card
- execution card
- read-only audit
- guarded fix
- protected change request

Risk:
LOW / MEDIUM / HIGH

Do not execute now:
Yes
Do Not Implement Section
Clearly state that this document is a backlog/review document only.
No architecture or source change is executed in this task.
Recommended Next Task
Suggest the next safe task, but do not execute it.

Suggested next task:

AREA: CODEX_HARNESS_DOCS + PRODUCT_DOCS
MODE: DOC_ONLY
PURPOSE FUNCTION:
Review DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md with the human, then promote approved candidates into DOC/architecture updates.
TIMEBOX: 60m

SUCCESS CRITERIA:

DOC/correction-loop/ exists.
README.md explains the correction-loop concept clearly.
2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md captures the five known improvement candidates.
Additional improvement candidates are extracted without implementing them.
No active architecture file is modified.
No runtime code is touched.
The document supports future human review before promotion.

STOP CONDITIONS:
Stop and report if:

the task requires modifying DOC/architecture/00~06
the task requires source code changes
the task requires deciding social_news.candidate vs content.content_candidate ownership
the task requires changing publisher, scheduler, auth, DB, env/config, or external API behavior
the review starts becoming implementation work

REPORT AFTER COMPLETION:
Report:

Files created
Files inspected
Improvement candidates captured
Additional candidates found
What was intentionally not changed
Recommended next task

FINAL LINE:
End the report with:

"Correction-loop review created. No fixes were executed; candidates require human review before promotion."

AREA: CODEX_HARNESS_DOCS + PRODUCT_DOCS + SYSTEM_ARCHITECTURE_DOCS
MODE: DOC_ONLY
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
Promote approved correction-loop findings from DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md into active DOC/architecture rules.

The goal is not to add more documentation volume.
The goal is to strengthen the active harness so future Codex tasks prevent recurring failures before they become direct code fixes.

PRIMARY RULE:
Architecture comes before source code.

Do not inspect or modify runtime source code.
Do not modify DB.
Do not change scheduler, publisher, auth, env/config, external API behavior, or runtime behavior.
This is a documentation-only architecture promotion task.

READ FIRST:
1. DOC/correction-loop/README.md
2. DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md
3. DOC/architecture/00_PRODUCT_NORTH_STAR.md
4. DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
5. DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
6. DOC/architecture/03_SYSTEM_ARCHITECTURE.md
7. DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
8. DOC/architecture/05_CODEX_HARNESS_GUIDE.md
9. DOC/architecture/06_WORK_AREA_REGISTRY.md
10. DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md

ALLOWED CHANGES:
Edit only:

- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/03_SYSTEM_ARCHITECTURE.md
- DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md
- DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md
- DOC/correction-loop/README.md
- DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md only if adding a short promoted-status note is useful

Documentation only.
Keep edits compact.
Promote approved correction-loop findings into active architecture rules.

FORBIDDEN CHANGES:
- No runtime code
- No DB changes
- No migration
- No scheduler changes
- No Facebook publisher changes
- No Telegram runtime behavior changes
- No content publisher behavior changes
- No auth changes
- No env/config changes
- No service start/stop
- No external API calls
- No source code edits
- No resolving social_news.candidate vs content.content_candidate implementation ownership
- No deciding Python vs Java workflow ownership
- No broad rewrite of architecture documents
- No changing archived documents

APPROVED PROMOTION TARGETS:

1. Strengthen Required Input Rule in 05

Target:
DOC/architecture/05_CODEX_HARNESS_GUIDE.md

Promote this rule:

If PURPOSE FUNCTION, AREA, or MODE is missing, Codex must not edit files.

Allowed behavior when required fields are missing:
- read DOC/architecture
- perform READ_ONLY_AUDIT
- ask for clarification
- produce a stop/pre-review report

Forbidden:
- modifying files
- running migrations
- changing runtime behavior
- guessing the task identity and proceeding with edits

This should replace or override any wording that allows Codex to infer required fields too freely.

2. Add Target Country Mismatch Trigger in 02

Target:
DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md

Add a Quality Trigger Card:

TRIGGER: Target Country Mismatch

Condition:
- Item is not directly tied to the current target country/channel.
- Item is global, non-Korea, generic international, or future-market-only.
- Item does not directly affect WorkConnect Korea users' work, settlement, visa, public service, safety, support, or daily-life decisions.

Action:
- Do not send to WorkConnect Korea public review or publishing by default.
- Store as future/global reference signal, downgrade, archive, or require explicit review depending on source value.
- Require target_country/channel fit to be visible in candidate or review reason.

Do not:
- Promote to Korea public content only because it mentions foreigners, travel, international affairs, or general safety.

3. Add Local Test Touches Real External Output Trigger in 04

Target:
DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md

Add a runtime trigger:

TRIGGER: Local Test Touches Real External Output

Condition:
A local test, smoke test, verification step, or manual run could send:
- real Facebook post
- real Telegram message
- real external API request
- real publish/review notification
- real scheduler-triggered external output

Action:
- Require dry-run, mock mode, sandbox channel, preview-only mode, or explicit user approval before execution.
- If dry-run/mock mode is unavailable, stop and report.

Do not:
- verify by sending real external output unless explicitly approved.
- treat a local environment as safe merely because the server is local.

4. Clarify Final Public Message/Link Ownership in 03

Target:
DOC/architecture/03_SYSTEM_ARCHITECTURE.md

Add or strengthen this boundary:

Target architecture:
- Content management should own the final public message.
- Content management should own the final publishable link.
- Source/domain tables should preserve and classify evidence.
- Publisher modules should publish only final approved/reviewable content objects.

Preserve ambiguity:
- Current implementation ownership between social_news.candidate and content.content_candidate remains a future audit target.
- Do not resolve implementation ownership in architecture docs.
- Do not change publisher behavior based on this clarification.

5. Mark 07 as Review Reference

Target:
DOC/architecture/07_HARNESS_RESTRUCTURE_REVIEW.md

Add a short status note near the top:

Status:
This is a review reference document.
Active architecture rules are maintained in DOC/architecture/00 through DOC/architecture/06.
Use this document as restructure rationale, not as the primary execution rule set.

6. Add Correction-Loop Promotion Rule

Target:
DOC/correction-loop/README.md
Secondary target if needed:
DOC/architecture/05_CODEX_HARNESS_GUIDE.md

Add a compact promotion rule:

A correction-loop finding may be promoted into active architecture only when it affects:
- product purpose
- repeated cross-area behavior
- trigger cards
- execution cards
- protected boundary clarity
- verification/reporting rules
- recurring failure prevention

A correction-loop finding should become READ_ONLY_AUDIT when it requires:
- ownership investigation
- code path mapping
- DB flow inspection
- publisher/scheduler/auth boundary confirmation

A correction-loop finding should become GUARDED_FIX or PROTECTED_CHANGE only after human approval and after architecture/work-area boundaries are clear.

7. Add Document Authority Map

Target:
DOC/architecture/03_SYSTEM_ARCHITECTURE.md or DOC/architecture/05_CODEX_HARNESS_GUIDE.md

Add a compact document authority map:

- DOC/architecture/00~06 = active governance / active harness rules
- DOC/architecture/07 = review reference
- DOC/correction-loop = backlog and promotion candidates
- DOC/to-be = future plans, not approval to implement
- DOC/walkthrough = task history and reports
- DOC/archives = historical snapshots, not active rules
- DOC/database = DB reference and planning docs; implementation still requires task approval

Rule:
Codex must not treat backlog, to-be, walkthrough, archive, or review-reference documents as active permission to implement.

8. Add Operation Notification Recurrence Suppression Candidate

Target:
DOC/architecture/06_WORK_AREA_REGISTRY.md under TELEGRAM_REPORTING
Optional secondary target:
DOC/architecture/05_CODEX_HARNESS_GUIDE.md as execution card pattern

Add a compact execution card:

EXECUTION CARD: Operation Notification Recurrence Suppression

Use when:
- same candidate, same review identity, same status, or same failure repeatedly enters Telegram reporting/review.

Action:
- suppress or downgrade repeated operation notifications when stable duplicate identity is available.
- log suppression reason.
- preserve first occurrence and latest meaningful state change.

Do not touch:
- Facebook publisher
- content publisher
- scheduler frequency
- auth/device approval
- external API behavior

Verify:
- repeated notification is suppressed or clearly classified.
- meaningful state change still notifies.

Note:
This is an architecture/work-area rule only. Do not implement runtime behavior in this task.

9. Add Source Signal vs Publishable Source Boundary

Target:
DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
Optional secondary target:
DOC/architecture/06_WORK_AREA_REGISTRY.md

Add an execution card or trigger:

EXECUTION CARD: Signal to Source-Backed Content

Use when:
- data comes from discovery source, community signal, forum, search result, aggregator, RSS snippet, or trend signal.

Steps:
- classify as signal first.
- identify whether primary, trusted media, or practical secondary source validation exists.
- do not create public content candidate until source-backed validation exists.
- preserve anonymized topic/user-need signal if useful.

Do not:
- treat signal-only data as authoritative fact.
- quote personal/community content directly in public content.
- promote signal-only data to public review/publishing.

10. Add Verification Plan Requirement for Runtime-Adjacent Candidates

Target:
DOC/correction-loop/README.md
Optional secondary target:
DOC/architecture/05_CODEX_HARNESS_GUIDE.md

Add rule:

Correction-loop candidates that target runtime, publisher, scheduler, auth, DB, env/config, external APIs, Telegram, Facebook, or content publisher must include a preliminary verification checklist before promotion.

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

11. Add Multi-Responsibility File Section Map Pattern

Target:
DOC/architecture/05_CODEX_HARNESS_GUIDE.md
Optional secondary target:
DOC/architecture/06_WORK_AREA_REGISTRY.md

Add an execution card:

EXECUTION CARD: Multi-Responsibility File Section Map

Use when:
- target file contains multiple responsibilities.
- target section is unclear.
- file includes protected and non-protected responsibilities together.

Steps:
- identify responsibilities inside the file.
- mark protected sections.
- mark allowed section for declared AREA.
- mark forbidden adjacent sections.
- define verification for the selected section only.
- stop if section boundaries are unclear.

Do not:
- treat file-level access as permission to edit all responsibilities.
- modify protected sections because they are nearby.

REQUIRED UPDATE TO CORRECTION-LOOP REVIEW:
If modifying DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md, only add a short "Promotion Status" note.

Do not rewrite the whole review.
Do not remove "Do not execute now" history unless adding a clear note that selected items were promoted in a later task.

SUCCESS CRITERIA:
- The five immediate small improvements are promoted into active architecture docs.
- Additional selected correction-loop improvements are promoted compactly.
- No runtime code is touched.
- No active architecture document becomes significantly longer without executable clarity.
- 05 clearly prevents file edits when PURPOSE FUNCTION / AREA / MODE is missing.
- 02 includes Target Country Mismatch and Signal-to-Source-Backed Content rules.
- 04 includes Local Test Touches Real External Output rule.
- 03 clarifies final public message/link target ownership while preserving implementation ambiguity.
- 07 is marked as review reference.
- 06 includes Telegram recurrence suppression as architecture/work-area guidance only.
- DOC/correction-loop continues to function as backlog, not active implementation permission.

STOP CONDITIONS:
Stop and report instead of editing if:
- a proposed change requires source code changes
- a proposed change weakens protected areas
- a proposed change requires deciding social_news.candidate vs content.content_candidate ownership
- a proposed change requires deciding Python vs Java workflow ownership
- a proposed change touches publisher, scheduler, auth, DB, env/config, external API behavior, or runtime behavior
- documents become essay-like instead of operational
- the task would modify files outside the allowed list

REPORT AFTER COMPLETION:
Report:

1. Files inspected
2. Files modified
3. Candidates promoted
4. Candidates intentionally left as backlog
5. Sections added per file
6. What was intentionally not changed
7. Ambiguities preserved
8. Remaining risks
9. Suggested next CODE_TASK_CANDIDATE items

Suggested next CODE_TASK_CANDIDATE should include, but not execute:

```text
AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Verify whether content.content_candidate is acting as the final publishable content object or merely duplicating social_news.candidate.
TIMEBOX: 60m

AREA: CODEX_HARNESS_DOCS
MODE: DOC_ONLY
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
코덱스 작업 보고서의 기본 언어 규칙을 active architecture에 추가한다.
목표는 향후 코덱스 보고서를 한국어로 읽기 쉽게 만들되, 파일명/코드명/상태값 같은 기술 식별자는 원문 그대로 유지하게 하는 것이다.

읽을 문서:
1. DOC/architecture/05_CODEX_HARNESS_GUIDE.md
2. DOC/architecture/06_WORK_AREA_REGISTRY.md

허용 변경:
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md 수정
- DOC/architecture/06_WORK_AREA_REGISTRY.md에 짧은 참조 추가 가능
- 문서 수정만 허용

금지 변경:
- 소스코드 수정 금지
- DB 수정 금지
- migration 금지
- scheduler / publisher / auth / env/config 수정 금지
- 외부 API 호출 금지
- 05/06 외 문서 수정 금지

필수 반영:

1. DOC/architecture/05_CODEX_HARNESS_GUIDE.md

`Reporting Policy` 근처에 Report Language Rule을 추가한다.

내용:

- 코덱스의 작업 보고서, 중간 보고, 중단 보고, 최종 보고는 한국어로 작성한다.
- 단, 기술 식별자는 원문 그대로 유지한다.
- 번역하지 말아야 할 항목:
  - file path
  - folder path
  - code
  - function name
  - class name
  - DB table / column name
  - API endpoint
  - enum / status code
  - AREA
  - MODE
  - PURPOSE FUNCTION
  - Git branch
  - commit hash
  - error code
  - raw log message
  - external service name used as identifier

좋은 예시:
`DOC/architecture/05_CODEX_HARNESS_GUIDE.md`에 Required Input Rule을 보강했습니다.
`PURPOSE FUNCTION`, `AREA`, `MODE`가 없으면 파일 수정 금지 규칙을 추가했습니다.
다음 작업은 `CONTENT_QUEUE` 영역의 `READ_ONLY_AUDIT`가 안전합니다.

나쁜 예시:
`PURPOSE FUNCTION`, `AREA`, `MODE` 같은 식별자를 임의로 한글 번역함.
파일명이나 status code를 한글로 바꿈.
로그 원문을 의역함.

2. DOC/architecture/06_WORK_AREA_REGISTRY.md

필요하면 짧은 참조만 추가한다.

예:
보고 언어 규칙은 `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`를 따른다. 작업 보고서는 한국어로 작성하되, 기술 식별자는 원문 그대로 유지한다.

성공 기준:
- 05에 Report Language Rule이 추가됨
- 06에는 필요 시 짧은 참조만 추가됨
- 보고서는 한국어로 작성됨
- 기술 식별자는 원문 유지됨
- 다른 파일은 수정하지 않음

보고:
다음 항목을 한국어로 보고한다. 단, 파일명/AREA/MODE 등 기술 식별자는 원문 유지.

1. 읽은 파일
2. 수정한 파일
3. 추가한 섹션
4. 일부러 수정하지 않은 것
5. 다음 추천 작업

최종 문장:
"Report Language Rule 반영 완료. 이후 코덱스 보고서는 한국어로 작성하고 기술 식별자는 원문 유지합니다."

AREA: LLAMA_STATUS
MODE: READ_ONLY_AUDIT
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
Local LLM/Ollama가 실제 사용량보다 큰 메모리를 기본 홀딩하는 원인을 검토한다.
목표는 Llama 안정성 보강이 baseline memory usage를 과하게 증가시키지 않았는지 확인하고, 수정 후보를 분리하는 것이다.

기본 원칙:
- 소스코드 수정 금지
- 설정 변경 금지
- Ollama process kill/start 금지
- 모델 실행/강제 로딩 금지
- DB 수정 금지
- scheduler/publisher/auth/env/config 수정 금지
- 보고서는 한국어로 작성
- 파일명/함수명/env 이름/status code는 원문 유지

먼저 읽을 문서:
1. DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
2. DOC/architecture/05_CODEX_HARNESS_GUIDE.md
3. DOC/architecture/06_WORK_AREA_REGISTRY.md
4. DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md

검토 대상:
- Local LLM / Ollama status 관련 코드
- LLaMA 호출부
- dashboard LLaMA status polling
- fallback 처리
- timeout / retry / keep_alive / num_ctx 설정
- 모델 unload 또는 idle 정책
- 최근 변경된 LLaMA 안정성 관련 코드

검토 질문:

1. LLaMA status check가 실제 모델 로딩을 유발하는가?
2. dashboard polling이 반복적으로 LLaMA endpoint를 호출하는가?
3. keep_alive 또는 유사 설정이 너무 길게 잡혀 있는가?
4. num_ctx 또는 기본 context size가 과도하게 큰가?
5. 실패 시 retry loop가 계속 모델을 깨우는가?
6. Local LLM이 unavailable일 때 deterministic fallback으로 빠지는가?
7. 작업 완료 후 모델 unload 또는 idle unload 정책이 있는가?
8. 최근 안정성 보강이 baseline memory usage를 증가시켰는가?
9. Local LLM이 optional helper라는 architecture 원칙과 실제 구현이 일치하는가?

보고서 형식:

# LLAMA_STATUS READ_ONLY_AUDIT 보고서

## 1. 결론 요약
- baseline memory hold 원인 추정
- 가장 의심되는 설정/코드 경로
- 즉시 수정 가능 여부

## 2. 확인한 파일
- 파일 경로
- 역할
- LLaMA/Ollama 관련 부분 요약

## 3. 메모리 홀딩 가능 원인
- keep_alive
- num_ctx
- preload
- polling
- retry loop
- status check model load
- unload 부재
- fallback 미작동

## 4. architecture 원칙과 구현 차이
- Local LLM optional/advisory 원칙과 실제 구현 비교
- runtime safety 위반 가능성

## 5. 수정 후보
수정은 실행하지 말고 후보만 작성.

각 후보는 아래 형식 사용:

CODE_TASK_CANDIDATE:
AREA:
MODE:
PURPOSE FUNCTION:
Target files:
Expected change:
Forbidden areas:
Verification:
Risk:

## 6. 추천 다음 단계
- LOW_RISK_FIX 가능 여부
- GUARDED_FIX 필요 여부
- env/config 변경 승인 필요 여부
- Ollama 직접 설정 변경이 필요한지 여부

중단 조건:
- Ollama process start/kill이 필요하면 중단
- env/config 변경이 필요하면 후보만 작성
- scheduler/publisher/auth 관련 수정이 필요하면 중단
- 실제 모델 실행이 필요하면 실행하지 말고 보고

최종 문장:
"LLAMA_STATUS READ_ONLY_AUDIT 완료. 수정은 실행하지 않았고, 메모리 홀딩 원인 후보와 다음 작업만 분리했습니다."

AREA: LLAMA_STATUS
MODE: LOW_RISK_FIX
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
Local LLM/Ollama의 baseline memory hold를 줄이기 위해 `/api/generate` 호출부의 `keep_alive` 기본 정책을 작업별 low-memory 정책으로 분리한다.

목표는 기본 대기 상태에서는 LLaMA/Ollama 메모리 점유를 낮게 유지하고, 실제 요청 시에만 메모리가 증가하며, 요청 종료 후 짧은 idle 이후 메모리가 감소할 수 있게 하는 것이다.

중요:
이번 작업은 `keep_alive` 정책 분리와 mock 검증만 수행한다.
`run_bot_loop()` 정책 변경, `.env` 직접 수정, Ollama process 제어는 하지 않는다.

보고 언어:
- 작업 보고서, 중간 보고, 최종 보고는 한국어로 작성한다.
- 단, 파일명, 함수명, class명, env 이름, endpoint, status code, log 원문, AREA, MODE, PURPOSE FUNCTION은 원문 유지한다.

먼저 읽을 문서:
1. `DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`
2. `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
3. `DOC/architecture/06_WORK_AREA_REGISTRY.md`
4. `DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md`

이전 감사 결과 요약:
- `.env`의 `OLLAMA_KEEP_ALIVE=10m`가 baseline memory hold의 최상위 원인 후보임.
- `NewsSummarizer`, `LlamaDuplicateChecker`, `content_card_payload_generator`가 `/api/generate` 호출 시 `keep_alive`를 전달함.
- `OLLAMA_NUM_CTX=3072`, `OLLAMA_SUMMARY_NUM_CTX=3072`도 메모리 증가 요인이지만, 이번 작업의 1차 범위는 `keep_alive` 정책 분리임.
- `/api/admin/llama/status`는 `/api/tags` 기반이라 모델 로딩 직접 원인으로 보이지 않음.
- 일반 작업 종료 후 자동 unload는 없고, `keep_alive`가 사실상 메모리 유지 정책으로 작동함.

수정 대상 파일:
- `SRC/foreign_worker_life_info_collector/social/news/summarizer/news_summarizer.py`
- `SRC/foreign_worker_life_info_collector/social/news/duplicate_guard/llama_duplicate_checker.py`
- `SRC/foreign_worker_life_info_collector/utils/content_card_payload_generator.py`

테스트 파일:
- 기존 관련 test가 있으면 기존 test 파일에 추가
- 없으면 해당 모듈 주변의 기존 테스트 구조를 확인한 뒤 최소 mock test 파일 추가
- 실제 Ollama 호출 금지
- `urlopen` 또는 HTTP 호출은 반드시 mock 처리

허용 변경:
- 위 3개 `/api/generate` 호출부의 `keep_alive` 결정 로직 수정
- 작업별 env 이름 추가
- 낮은 기본값 적용
- mock 기반 테스트 추가
- 필요한 경우 작은 helper 함수 추가

금지 변경:
- `.env` 파일 직접 수정 금지
- `.env.example` 수정은 이번 작업에서 하지 말 것
- `admin_server.py` 수정 금지
- `run_bot_loop()` 수정 금지
- `Dashboard.vue` 수정 금지
- scheduler 변경 금지
- publisher 변경 금지
- auth/env/config 변경 금지
- DB/migration 변경 금지
- Ollama process start/stop/kill 금지
- 실제 `/api/tags` 또는 `/api/generate` 호출 금지
- 모델 강제 로딩 금지
- 외부 API 호출 금지
- commit/push 금지

필수 설계:

1. `OLLAMA_KEEP_ALIVE` 단일 전역값을 `/api/generate` 호출부의 기본 fallback으로 사용하지 않도록 한다.

현재 `.env`에 `OLLAMA_KEEP_ALIVE=10m`가 있으면 모든 작업이 10분간 모델을 hold할 수 있다.
이번 수정 후에는 task-specific env가 없을 때 낮은 기본값을 사용해야 한다.

2. 작업별 env를 도입한다.

추천 env 이름:

```text
OLLAMA_SUMMARY_KEEP_ALIVE
OLLAMA_DUPLICATE_KEEP_ALIVE
OLLAMA_CARD_PAYLOAD_KEEP_ALIVE
낮은 기본값을 적용한다.

추천 기본값:

summary: 30s
duplicate: 30s
card payload: 30s

단, 코드 구조상 더 안전한 값이 있으면 이유를 보고하고 적용한다.

env 우선순위는 아래처럼 한다.
task-specific env
-> code default low-memory value

주의:
이번 작업에서는 OLLAMA_KEEP_ALIVE=10m를 fallback으로 쓰지 말 것.
그 값을 fallback으로 쓰면 baseline memory hold 개선 효과가 사라진다.

/api/generate payload에 들어가는 keep_alive 값을 테스트로 고정한다.

mock test 기준:

summary 호출 payload에 keep_alive가 OLLAMA_SUMMARY_KEEP_ALIVE 또는 기본 30s로 들어가는지 확인
duplicate 호출 payload에 keep_alive가 OLLAMA_DUPLICATE_KEEP_ALIVE 또는 기본 30s로 들어가는지 확인
card payload 호출 payload에 keep_alive가 OLLAMA_CARD_PAYLOAD_KEEP_ALIVE 또는 기본 30s로 들어가는지 확인
기존 OLLAMA_KEEP_ALIVE=10m가 환경에 있어도 task-specific env가 없으면 10m가 payload로 들어가지 않는지 확인
num_ctx는 이번 작업에서 직접 줄이지 않는다.

단, 보고서에 다음 후보로 분리한다:

CODE_TASK_CANDIDATE:
AREA: LLAMA_STATUS
MODE: LOW_RISK_FIX 또는 GUARDED_FIX
PURPOSE FUNCTION:
작업별 `num_ctx` 기본값을 low-memory 정책으로 재검토한다.
run_bot_loop() 정책은 이번 작업에서 수정하지 않는다.

보고서에 다음 후보로 분리한다:

CODE_TASK_CANDIDATE:
AREA: LLAMA_STATUS
MODE: GUARDED_FIX
PURPOSE FUNCTION:
`run_bot_loop()`에서 Local LLM unavailable 시 cycle skip 대신 deterministic fallback으로 계속 진행할지 architecture 기준에 맞게 결정한다.

검증:
가능한 검증만 수행한다.

필수:

관련 unit/mock test 실행
실제 Ollama 호출이 발생하지 않았음을 보고
수정 파일 diff 확인
금지 영역 미수정 확인

권장:

python -m pytest ...로 관련 테스트만 실행
전체 테스트가 무거우면 관련 테스트만 실행하고 이유 보고

중단 조건:

실제 Ollama 호출이 필요하면 중단
.env 수정이 필요하면 중단하고 수동 변경 후보로 보고
admin_server.py 수정이 필요하면 중단
run_bot_loop() 수정이 필요하면 중단
scheduler/publisher/auth/DB/env/config 수정이 필요하면 중단
테스트 구조가 불명확해서 추측이 필요하면 중단하고 보고
변경 범위가 3개 호출부를 넘어가면 중단하고 보고

보고서 형식:

LLAMA_STATUS LOW_RISK_FIX 보고서
1. 결론 요약
무엇을 변경했는지
baseline memory hold에 어떤 효과를 기대하는지
실제 메모리 측정은 수행했는지/하지 않았는지
2. 읽은 architecture 문서
문서별 확인한 원칙 요약
3. 수정한 파일
파일 경로
변경 내용
기존 동작
변경 후 동작
4. keep_alive 정책

아래 표 형식으로 정리:

작업	env	기본값	기존 fallback	변경 후 fallback
5. 테스트/검증
실행한 테스트
mock 처리 여부
실제 Ollama 호출 여부
결과
6. 수정하지 않은 것
.env
num_ctx
admin_server.py
run_bot_loop()
scheduler/publisher/auth/DB/env/config
7. 남은 위험
.env에 OLLAMA_SUMMARY_NUM_CTX=3072가 남아있는 영향
Ollama 자체 keep_alive 정책
실제 메모리 감소는 다음 실행에서 확인 필요
8. 다음 작업 후보

각 후보는 아래 형식 사용:

CODE_TASK_CANDIDATE:
AREA:
MODE:
PURPOSE FUNCTION:
Target files:
Expected change:
Forbidden areas:
Verification:
Risk:

반드시 포함할 후보:

작업별 num_ctx low-memory 정책 검토
run_bot_loop() Local LLM unavailable fallback 정책 검토
필요 시 .env 수동 변경 안내 문서화

최종 문장:
"LLAMA_STATUS LOW_RISK_FIX 완료. 실제 Ollama 호출 없이 keep_alive 정책을 작업별 low-memory 기본값으로 분리했습니다."