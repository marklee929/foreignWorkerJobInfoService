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

AREA: LIVING_DOMAIN + CONTENT_CARD_GENERATION + CONTENT_QUEUE + DASHBOARD_STATUS
MODE: READ_ONLY_AUDIT
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
생활정보 콘텐츠가 검토/카드 생성/게시 후보로 올라오지 않는 원인을 read-only로 파악하고, 운영자가 UI에서 문제를 진단할 수 있도록 로그 분석 화면 개선 후보를 분리한다.

이번 작업은 원인 감사와 개선 후보 작성만 수행한다.
코드 수정, DB 수정, 게시, 스케줄러 변경, 외부 API 호출은 하지 않는다.

보고 언어:
- 작업 보고서, 중간 보고, 최종 보고는 한국어로 작성한다.
- 단, 파일명, 함수명, class명, DB table/column, API endpoint, enum/status code, AREA, MODE, PURPOSE FUNCTION, Git branch, commit hash, error code, raw log message는 원문 유지한다.

먼저 읽을 문서:
1. `DOC/architecture/00_PRODUCT_NORTH_STAR.md`
2. `DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md`
3. `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
4. `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
5. `DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`
6. `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
7. `DOC/architecture/06_WORK_AREA_REGISTRY.md`
8. `DOC/correction-loop/README.md`
9. `DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md`

현재 관측:
- Telegram에는 `News auto publish completed`가 계속 올라오고 있다.
- Business Insider 여행위험국가 기사, NYTimes 한국 술/섬 이야기 같은 뉴스성 콘텐츠가 올라왔다.
- Admin UI의 실시간 운영 로그는 보이지만 창이 작고, 최근 로그 위주라 원인 분석이 어렵다.
- 시스템 설정 화면에는 코드 가이드가 보이고, 로그 분석 화면이 별도 하위 메뉴로 분리되어 있지 않다.
- 생활정보 콘텐츠 검토/카드 생성이 더 이상 올라오지 않는 것으로 보인다.

검토할 가설:

1. 생활정보 데이터가 아직 수집되지 않았음
- 현재 들어오는 데이터가 뉴스성 데이터 위주인지 확인
- living/lifestyle/domain source가 실제로 collection되고 있는지 확인
- 생활정보 source item, candidate, content candidate가 생성되는지 확인

2. 생활정보 데이터는 있지만 카드 생성 라인에서 오류가 있음
- `CONTENT_CARD_GENERATION` 관련 파일과 로그 확인
- generated card output path, card payload, language validation, source/date/link validation 오류 가능성 확인
- card 생성 실패가 operation log 또는 admin UI에 표시되는지 확인

3. 생활정보 콘텐츠 카드화 파이프라인이 애초에 연결되어 있지 않음
- living/lifestyle source → content candidate → card payload → generated image → review/Telegram/Admin UI 흐름이 구현되어 있는지 확인
- social news pipeline과 lifestyle pipeline이 같은 content candidate 경로를 쓰는지 확인
- content card generation이 social news 전용인지, living domain에도 연결되어 있는지 확인

추가 가능성이 있으면 별도 후보로 기록:
- status filter mismatch
- scheduler/bot disabled
- Telegram review dedupe/suppression
- content candidate sync 누락
- admin UI가 생활정보 후보를 숨기고 있음
- Python pipeline과 Java pipeline ownership 혼선
- log API가 필요한 정보를 노출하지 않음

검토 대상 영역:

문서:
- `DOC/architecture/00` through `06`
- `DOC/correction-loop/`

Admin UI:
- dashboard / system settings / log display 관련 Vue 파일
- sidebar/menu/router 관련 파일
- status code guide 화면 관련 파일
- operation log 표시 컴포넌트
- API client의 log/status endpoint

Backend/API:
- operation log API
- dashboard log API
- bot status API
- lifestyle/living status API
- content card generation API
- content candidate API
- Telegram review/reporting API

Pipeline:
- living/lifestyle/domain collectors
- lifestyle guide candidate generation
- content candidate sync
- card payload generation
- generated card output
- Telegram review/reporting
- Facebook publishing boundary는 read-only로만 확인

DB:
- 필요하면 read-only query 후보만 작성한다.
- 실제 DB query 실행은 명시적으로 안전할 때만 read-only로 제한한다.
- mutation 금지.

금지 변경:
- 소스코드 수정 금지
- DB 수정 금지
- migration 금지
- scheduler 변경 금지
- Facebook publisher 변경 금지
- Telegram runtime behavior 변경 금지
- content publisher 변경 금지
- auth/env/config 변경 금지
- 외부 API 호출 금지
- 실제 게시 금지
- 수집/카드생성/스케줄러 수동 실행 금지
- commit/push 금지

확인 질문:

## A. 로그 UI 진단
1. 현재 실시간 운영 로그는 어떤 API/DB/source에서 가져오는가?
2. 몇 개까지 표시하는가?
3. 페이징 또는 infinite scroll이 가능한 구조인가?
4. 상태별 필터가 가능한가?
5. 로그 내용 검색이 가능한가?
6. 날짜/시간 범위 검색이 가능한가?
7. 로그 원본에 `module`, `level`, `message`, `created_at`, `job/cycle`, `candidate_id`, `source`, `status` 같은 필드가 있는가?
8. UI에서 로그가 작게 보여 운영자가 원인 분석하기 어려운 구조인가?
9. 시스템 설정 화면에서 코드 가이드와 로그 분석을 하위 메뉴로 분리할 수 있는 구조인가?

## B. 생활정보 콘텐츠 미생성 원인
1. 생활정보/lifestyle collector가 실제로 실행되고 있는가?
2. 생활정보 source item이 최근 생성되었는가?
3. 생활정보 domain candidate 또는 content candidate가 생성되었는가?
4. 생활정보 candidate가 `READY_TO_REVIEW`, `READY_TO_PUBLISH`, `GENERATED`, `POSTED`, `SKIPPED`, `FAILED` 중 어디에 머무는가?
5. 생활정보가 card payload generation까지 도달하는가?
6. card payload generation에서 실패한다면 어떤 error/status가 남는가?
7. generated card file이 생성되는가?
8. Telegram review/reporting으로 생활정보가 전송되는가?
9. Facebook public publishing까지 연결되어 있는가?
10. 뉴스성 콘텐츠와 생활정보 콘텐츠가 같은 pipeline을 공유하는가, 분리되어 있는가?
11. content card generation이 social news 전용으로 묶여 있는가?
12. architecture 문서상 의도와 실제 구현이 일치하는가?

## C. 운영자 UI 개선 요구 정리
다음 요구사항을 구현 후보로 정리한다. 실제 구현은 하지 않는다.

1. 시스템 설정 하위 메뉴 분리
- `시스템 설정 > 코드 가이드`
- `시스템 설정 > 운영 로그`
또는
- `시스템 설정` 아래 하위 route/menu 2개 분리

2. 운영 로그 화면 추가/개선
- 로그 목록을 독립 화면으로 제공
- 최대 50개 단위 페이징
- 또는 infinite scroll / load more
- 상단 검색 영역 추가

검색 필드:
- 상태: select
  - 예: ALL / INFO / WARN / ERROR / FAILED / SKIPPED 등 실제 status 기준
- 검색어: input
  - 로그 내용/message/module/source 검색
- 일자: created_at 기준
  - 시작일/종료일 또는 단일 날짜
- 선택 가능하면 module/source 필터도 후보로 기록

3. 운영자가 원인 파악 가능한 컬럼
- 시간
- 모듈
- level/status
- message
- source/candidate title
- cycle/job id
- candidate id 또는 ref id
- action/status code
- error detail 일부
- related screen/link 가능성

보고서 형식:

# LIVING_DOMAIN / LOG_UI READ_ONLY_AUDIT 보고서

## 1. 결론 요약
- 생활정보 콘텐츠가 안 올라오는 가장 유력한 원인
- 로그 UI에서 현재 확인 가능한 것
- 로그 UI에서 부족한 것
- 즉시 구현 가능한 개선 후보

## 2. 읽은 architecture 문서
- 문서별 적용한 하네스 원칙 요약

## 3. 확인한 파일
- 파일 경로
- 역할
- 관련 영역

## 4. 현재 운영 로그 구조
- 로그 저장 위치
- 로그 API
- Admin UI 표시 방식
- 표시 개수/정렬/필터/검색 여부
- 문제점

## 5. 생활정보 콘텐츠 흐름 분석
가능하면 아래 흐름으로 정리:

```text
living source
-> living/domain candidate
-> content candidate
-> card payload
-> generated card
-> review/Telegram
-> public delivery

각 단계별로:

구현됨 / 미구현 / 불명확
관련 파일
관련 status
로그 또는 에러 노출 여부
6. 가설별 판정
가설 1. 생활정보 데이터가 아직 수집되지 않음
근거
반증
판정
가설 2. 생활정보 데이터는 있으나 카드 생성 라인에서 오류
근거
반증
판정
가설 3. 생활정보 카드화 파이프라인이 애초에 연결되지 않음
근거
반증
판정
추가 가설
발견 시 작성
7. UI 개선 후보

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

A. 운영 로그 독립 화면 또는 하위 메뉴 추가

AREA 후보: DASHBOARD_STATUS 또는 새 DASHBOARD_LOGS 필요 여부 판단
MODE 후보: LOW_RISK_FIX
시스템 설정에서 코드 가이드와 운영 로그를 하위 메뉴로 분리

B. 운영 로그 페이징/더보기

50개 단위 페이징 또는 infinite scroll
기존 API가 지원하는지 확인
지원하지 않으면 API 후보 분리

C. 운영 로그 검색/필터

상태 select
검색어 input
일자 created_at
필요하면 module/source 필터

D. 생활정보 콘텐츠 카드 생성 경로 보강

원인에 따라 LIVING_DOMAIN, CONTENT_CARD_GENERATION, CONTENT_QUEUE, TELEGRAM_REPORTING 중 적절한 AREA로 분리
8. 위험/보호 영역
publisher 건드릴 필요가 있는지
scheduler 건드릴 필요가 있는지
DB migration 필요 여부
auth/env/config 필요 여부
protected change 여부
9. 추천 다음 단계
바로 가능한 LOW_RISK_FIX
추가 READ_ONLY_AUDIT 필요
GUARDED_FIX 필요
PROTECTED_CHANGE 필요
먼저 architecture/work-area 보강이 필요한지

중단 조건:

원인 분석 중 publisher/scheduler/auth/env/config 변경이 필요하면 중단하고 보고
DB migration이 필요하면 후보만 작성
실제 수집/게시/외부 API 호출이 필요하면 실행하지 말고 보고
Python vs Java ownership 결정을 강제로 해야 하면 중단하고 보고
CONTENT_PUBLISHER나 FACEBOOK_PUBLISHER 수정이 필요하면 후보만 작성

최종 문장:
"LIVING_DOMAIN / LOG_UI READ_ONLY_AUDIT 완료. 수정은 실행하지 않았고, 원인 분석과 다음 작업 후보만 분리했습니다."

AREA: DASHBOARD_LOGS
MODE: LOW_RISK_FIX
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
운영자가 Admin UI에서 수집/분류/카드생성/검토 실패 원인을 직접 추적할 수 있도록 운영 로그 전용 화면을 추가하고, 기존 실시간 로그보다 넓은 로그 조회/검색/페이징 기능을 제공한다.

이번 작업의 목표는 생활정보 콘텐츠 미생성 원인을 바로 수정하는 것이 아니라, 운영자가 UI에서 원인을 찾을 수 있는 로그 분석 화면을 만드는 것이다.

보고 언어:
- 작업 보고서, 중간 보고, 최종 보고는 한국어로 작성한다.
- 단, 파일명, 함수명, class명, DB table/column, API endpoint, enum/status code, AREA, MODE, PURPOSE FUNCTION, raw log message는 원문 유지한다.

먼저 읽을 문서:
1. DOC/architecture/03_SYSTEM_ARCHITECTURE.md
2. DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
3. DOC/architecture/05_CODEX_HARNESS_GUIDE.md
4. DOC/architecture/06_WORK_AREA_REGISTRY.md
5. DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md

이전 READ_ONLY_AUDIT 결론:
- 현재 운영 로그는 `social_news.pipeline_step_log` 중심이다.
- API는 `GET /api/logs/recent`를 사용한다.
- UI는 `Dashboard.vue` + `LogPanel.vue` 중심이다.
- 현재 로그 UI는 창이 작고 원인 분석이 어렵다.
- 상태 필터, 검색어 필터, 날짜 범위 필터, module/source 필터가 없다.
- `candidate_id`는 API 원천에 있으나 UI 노출이 약하다.
- `content.publish_log`의 Telegram review/card preview 로그는 대시보드 로그에 바로 보이지 않는다.
- 이번 작업에서는 content.publish_log 통합은 구현하지 말고 후속 후보로 남긴다.

작업 목표:
1. 시스템 설정 하위 메뉴를 분리한다.
   - `시스템 설정 > 코드 가이드`
   - `시스템 설정 > 운영 로그`

2. 운영 로그 독립 화면을 추가한다.
   - 기존 대시보드의 작은 로그 패널보다 넓게 확인 가능해야 한다.
   - 기존 dashboard 로그 기능은 깨지지 않아야 한다.

3. 운영 로그 목록 조회를 개선한다.
   - 50개 단위 조회
   - `limit/offset` 기반 페이징 또는 더보기 버튼
   - 가능하면 기존 `/api/logs/recent` 구조를 유지한다.

4. 상단 검색 영역을 추가한다.
   - 상태: select
     - ALL / INFO / WARN / ERROR 등 실제 level/status 기준
   - 검색어: input
     - message / module / source / title 검색 후보
   - 일자: created_at 기준
     - 시작일/종료일 또는 날짜 필터
   - module/source 필터가 기존 데이터로 가능하면 추가 후보로 검토

5. 로그 컬럼을 운영자가 원인 파악하기 쉽게 구성한다.
   - 시간
   - module 또는 bot
   - level/status
   - message
   - step/action
   - source/candidate title 가능 시
   - candidate_id 가능 시
   - error detail 일부 가능 시

허용 변경:
- Admin UI route/menu/sidebar 수정
- 운영 로그 화면 Vue 파일 신규 생성 또는 기존 SectionPage/LogPanel 확장
- `apiClient.js`에 로그 조회 함수 추가/확장
- `admin_server.py`의 `/api/logs/recent` read-only query 파라미터 확장
- 기존 dashboard 로그 표시가 깨지지 않는 범위의 `LogPanel.vue` 개선
- read-only API만 허용

금지 변경:
- DB mutation 금지
- migration 금지
- publisher 변경 금지
- scheduler 변경 금지
- Telegram runtime behavior 변경 금지
- Facebook publisher 변경 금지
- auth/env/config 변경 금지
- 실제 수집 실행 금지
- 실제 게시 금지
- 외부 API 호출 금지
- content.publish_log 통합 구현 금지
- 생활정보 카드 생성 로직 수정 금지
- commit/push 금지

구현 범위 제한:
이번 작업은 `social_news.pipeline_step_log` 기반 운영 로그 화면 개선까지만 한다.

다음 항목은 구현하지 말고 CODE_TASK_CANDIDATE로 남긴다.
- `content.publish_log`와 운영 로그 통합
- card preview status/reason/image_path 노출
- 생활정보 카드 생성 실패 사유 상세 노출
- living 후보 DB 집계
- Business Insider/NYTimes 분류 조건 수정
- publisher/scheduler 관련 변경

검증:
가능하면 아래를 확인한다.

Backend:
- `/api/logs/recent` 기존 호출이 계속 동작하는지
- `limit`, `offset`이 기존 방식과 호환되는지
- 추가 필터 파라미터가 없을 때 기존 결과와 호환되는지
- read-only query인지 확인

Frontend:
- 시스템 설정 하위 메뉴가 보이는지
- `코드 가이드` 화면이 기존처럼 열리는지
- `운영 로그` 화면이 열리는지
- 로그 50개 조회가 가능한지
- 더보기 또는 페이징 동작이 가능한지
- 상태 필터 / 검색어 / 일자 필터 UI가 동작하는지
- 빈 결과 / 로딩 / 오류 상태가 깨지지 않는지
- 기존 dashboard 로그 패널이 깨지지 않는지

테스트:
- 가능하면 frontend build 또는 관련 lint/test 실행
- backend route는 mock 또는 local read-only로 확인
- DB 변경 없이 수행

중단 조건:
- DB schema 변경이 필요하면 중단하고 후보로 보고
- publisher/scheduler/auth/env/config 변경이 필요하면 중단
- content.publish_log 통합이 필요하면 이번 작업에서 하지 말고 후보로 보고
- 생활정보 카드 생성 로직 수정이 필요하면 하지 말고 후보로 보고
- 기존 dashboard가 깨질 위험이 크면 중단하고 보고
- API 응답 구조를 크게 바꿔야 하면 중단하고 보고

보고서 형식:

# DASHBOARD_LOGS LOW_RISK_FIX 보고서

## 1. 결론 요약
- 무엇을 구현했는지
- 기존 dashboard 로그에 영향이 있는지
- 운영자가 무엇을 새로 확인할 수 있는지

## 2. 읽은 architecture 문서
- 적용한 하네스 원칙 요약

## 3. 수정한 파일
- 파일 경로
- 변경 내용
- 기존 동작
- 변경 후 동작

## 4. API 변경
- endpoint
- query parameter
- response shape 변화 여부
- 기존 호환성 여부

## 5. UI 변경
- 추가된 메뉴
- 추가된 화면
- 검색/필터/페이징 기능
- empty/loading/error 처리

## 6. 검증 결과
- 실행한 테스트/build
- backend 확인
- frontend 확인
- UI visual check 여부
- 실패 또는 미확인 항목

## 7. 수정하지 않은 것
아래 항목이 수정되지 않았는지 명시:
- DB schema/migration
- publisher
- scheduler
- Telegram runtime behavior
- Facebook publisher
- auth/env/config
- content card generation logic
- living pipeline logic

## 8. 남은 위험
- `content.publish_log`가 아직 운영 로그 화면에 통합되지 않음
- card preview 실패 사유는 후속 작업 필요
- 생활정보 후보가 실제 어디서 멈추는지는 DB read-only audit 필요

## 9. 다음 작업 후보

반드시 포함:

CODE_TASK_CANDIDATE:
AREA: CONTENT_CARD_GENERATION + CONTENT_QUEUE + TELEGRAM_REPORTING
MODE: GUARDED_FIX
PURPOSE FUNCTION:
생활정보 카드 생성 실패 사유를 운영 로그/API/UI에서 확인할 수 있게 한다.
Target files:
`admin_server.py`, `content/repository.py`, `ContentManagementPage.vue`
Expected change:
`content_card_preview.status/reason/image_path/template_type` 표시
Forbidden areas:
Telegram runtime behavior 변경, Facebook publisher, scheduler, auth/env/config
Verification:
dry-run review log 또는 mock payload에서 `CARD_PREVIEW_GENERATED` / 실패 코드 확인
Risk:
MEDIUM

CODE_TASK_CANDIDATE:
AREA: LIVING_DOMAIN + SOCIAL_NEWS_CANDIDATE
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Business Insider/NYTimes 등 일반 뉴스가 생활정보 후보로 들어오는 분류 조건을 확인한다.
Target files:
`category_rotation.py`, `candidate_evaluator.py`, `content/service.py`, DB read-only query 후보
Expected change:
없음. 원인 매핑만.
Forbidden areas:
publisher, scheduler, DB mutation
Verification:
read-only count/query report
Risk:
LOW

최종 문장:
"DASHBOARD_LOGS LOW_RISK_FIX 완료. 운영 로그 분석 화면을 추가했고, 생활정보 카드 생성 원인 수정은 후속 후보로 분리했습니다."

AREA: CONTENT_CARD_GENERATION + CONTENT_QUEUE + TELEGRAM_REPORTING
MODE: GUARDED_FIX
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
생활정보 콘텐츠의 카드 생성 결과와 실패 사유를 운영자가 Admin UI에서 확인할 수 있도록 한다.

목표는 생활정보 카드 생성이 실패했는지, 성공했는지, 생성된 이미지 경로가 무엇인지, 왜 Telegram review로 올라오지 않았는지 운영자가 추적할 수 있게 만드는 것이다.

이번 작업은 card preview / content candidate / review log 가시성 개선 작업이다.
Telegram runtime behavior, Facebook publisher, scheduler, auth, env/config는 수정하지 않는다.

보고 언어:
- 작업 보고서, 중간 보고, 최종 보고는 한국어로 작성한다.
- 단, 파일명, 함수명, class명, DB table/column, API endpoint, enum/status code, AREA, MODE, PURPOSE FUNCTION, raw log message는 원문 유지한다.

먼저 읽을 문서:
1. DOC/architecture/00_PRODUCT_NORTH_STAR.md
2. DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
3. DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
4. DOC/architecture/03_SYSTEM_ARCHITECTURE.md
5. DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
6. DOC/architecture/05_CODEX_HARNESS_GUIDE.md
7. DOC/architecture/06_WORK_AREA_REGISTRY.md
8. DOC/correction-loop/README.md
9. DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md

PHASE 진입 조건:
- PHASE 1 `DASHBOARD_LOGS LOW_RISK_FIX`가 완료되어야 한다.
- 운영 로그 화면 또는 로그 조회 개선이 최소한 동작해야 한다.
- PHASE 1에서 dashboard/log API가 깨지지 않았다는 보고가 있어야 한다.

이전 READ_ONLY_AUDIT 결론:
- 생활정보 카드 생성은 생활정보 수집 시점이 아니라 `content.content_candidate` 동기화 후 Telegram review 직전에 실행된다.
- 생활정보 흐름은 대략 다음과 같다.

```text
생활정보 봇
-> NewsPipeline dry-run
-> social_news.candidate
-> content_service.sync_social_news()
-> content.content_candidate
-> review_targets()
-> telegram_review_card_preview()
-> build_content_card_preview()
-> Telegram sendPhoto 또는 sendMessage
카드 생성 실패는 CARD_TEXT_OVERFLOW, CARD_TEXT_INVALID_LANGUAGE, CARD_BLOCKED_ZERO_SCORE, CARD_NOT_REQUIRED 등으로 발생할 수 있다.
하지만 현재 운영 로그 UI는 social_news.pipeline_step_log 중심이라 카드 생성 실패 사유와 content.publish_log.request_payload.content_card_preview를 직접 보기 어렵다.

작업 목표:

content candidate 상세 또는 content management 화면에서 card preview 상태를 확인할 수 있게 한다.
표시 후보:
content_card_preview.status
content_card_preview.reason
content_card_preview.image_path
content_card_preview.template_type
content_card_preview.source
content_card_preview.generated_at 또는 생성 시각이 있으면 표시
card preview가 실패한 경우 운영자가 실패 이유를 볼 수 있게 한다.
예:
CARD_TEXT_OVERFLOW
CARD_TEXT_INVALID_LANGUAGE
CARD_BLOCKED_ZERO_SCORE
CARD_NOT_REQUIRED
CARD_RENDER_FAILURE
LLAMA_UNAVAILABLE
기타 실제 코드상 status/reason
content.publish_log 또는 기존 저장 구조에 card preview 정보가 있다면 read-only로 조회해서 UI에 노출한다.
기존 Telegram review 전송 동작 자체는 바꾸지 않는다.
즉, Telegram으로 보내는 payload나 approve/reject callback 로직은 변경하지 않는다.
기존 Facebook publisher와 자동 게시 로직은 절대 변경하지 않는다.

검토 및 수정 대상 후보:

SRC/foreign_worker_life_info_collector/content/service.py
SRC/foreign_worker_life_info_collector/content/repository.py
SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py
SRC/foreign_worker_life_info_collector/utils/content_card_payload_generator.py
SRC/foreign_worker_life_info_collector/social/news/notifier/telegram_notifier.py
SRC/foreign_worker_life_info_collector/api/admin_server.py
SRC/foreign_worker_life_info_collector/admin_ui/src/views/ContentManagementPage.vue
SRC/foreign_worker_life_info_collector/admin_ui/src/services/apiClient.js
관련 test file

허용 변경:

content candidate 상세 API에 card preview 관련 read-only 필드 추가
content management UI에서 card preview status/reason/image_path 표시
publish log request_payload 안의 card preview 정보를 read-only로 파싱/노출
card preview 실패 사유 표시용 UI badge/text 추가
필요한 경우 기존 status badge 사용
mock 기반 테스트 추가 또는 보완
기존 동작을 깨지 않는 read-only 조회 보강

금지 변경:

Telegram sendPhoto/sendMessage 실제 전송 로직 변경 금지
Telegram approve/reject callback 변경 금지
Facebook publisher 변경 금지
content publisher 자동 게시 조건 변경 금지
scheduler 변경 금지
auth/env/config 변경 금지
DB schema/migration 변경 금지
실제 수집/게시/외부 API 호출 금지
raw token/secret 노출 금지
card generation 실행을 강제로 트리거하지 말 것
social_news.candidate vs content.content_candidate ownership을 이번 작업에서 결정하지 말 것

주의:
이번 작업은 card preview 결과의 “가시성 개선”이다.
card 생성 알고리즘 자체를 고치거나, Telegram 전송 정책을 바꾸는 작업이 아니다.

구현 우선순위:

기존 저장된 card preview 정보가 있는지 확인
있으면 API에서 read-only로 노출
UI에서 content candidate 상세 또는 list detail에 표시
실패 코드가 있으면 사람이 읽을 수 있게 표시
없으면 “card preview 정보 없음”으로 표시하고 후속 후보 작성

검증:
Backend:

관련 content candidate/detail API가 정상 응답하는지 확인
기존 응답과 호환되는지 확인
없는 card preview 정보에 대해 500이 아니라 null/empty state로 처리되는지 확인

Frontend:

Content Management 화면이 정상 로드되는지 확인
candidate 상세 또는 side panel에서 card preview status/reason 확인 가능한지 확인
image_path가 있으면 링크 또는 경로가 표시되는지 확인
실패/없음/성공 상태가 구분되는지 확인
기존 content list가 깨지지 않는지 확인

Test:

가능하면 mock data로 card preview success/failure/none 케이스 테스트
실제 Telegram/Facebook 호출 금지
실제 card generation 강제 실행 금지

중단 조건:

DB migration이 필요하면 중단하고 후보로 보고
Telegram runtime behavior 변경이 필요하면 중단
Facebook publisher 변경이 필요하면 중단
scheduler/auth/env/config 변경이 필요하면 중단
content publisher 조건 변경이 필요하면 중단
card generation 알고리즘 수정이 필요하면 이번 작업에서 하지 말고 후보로 보고
social_news.candidate vs content.content_candidate ownership 결정이 필요하면 중단하고 보고
Python vs Java ownership 결정이 필요하면 중단하고 보고

보고서 형식:

CONTENT_CARD_GENERATION / CONTENT_QUEUE GUARDED_FIX 보고서
1. 결론 요약
무엇을 구현했는지
운영자가 새로 확인할 수 있는 card preview 정보
Telegram/Facebook/publisher 동작 변경 여부
2. 읽은 architecture 문서
적용한 하네스 원칙 요약
3. 수정한 파일
파일 경로
변경 내용
기존 동작
변경 후 동작
4. card preview 데이터 흐름

아래 흐름으로 실제 확인된 경로 작성:

content candidate
-> review target
-> card preview build
-> publish_log/request_payload
-> admin API
-> admin UI

각 단계별:

구현됨 / 미구현 / 불명확
관련 파일
표시되는 status/reason
5. API 변경
endpoint
추가 필드
response shape 변화
기존 호환성
6. UI 변경
표시 위치
표시 필드
success/failure/none 상태 처리
empty/loading/error 처리
7. 검증 결과
실행한 테스트/build
backend 확인
frontend 확인
UI visual check 여부
실패 또는 미확인 항목
8. 수정하지 않은 것

아래 항목이 수정되지 않았는지 명시:

Telegram runtime behavior
Telegram approve/reject callback
Facebook publisher
content publisher 자동 게시 조건
scheduler
auth/env/config
DB schema/migration
card generation 알고리즘
social_news.candidate vs content.content_candidate ownership
9. 남은 위험
card preview 정보가 저장되지 않는 케이스
content.publish_log 통합 범위
living candidate가 card preview까지 도달하지 않는 원인
DB read-only audit 필요 여부
10. 다음 작업 후보

반드시 포함:

CODE_TASK_CANDIDATE:
AREA: LIVING_DOMAIN + SOCIAL_NEWS_CANDIDATE
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Business Insider/NYTimes 등 일반 뉴스가 생활정보 후보로 들어오는 분류 조건을 확인한다.
Target files:
category_rotation.py, candidate_evaluator.py, content/service.py, DB read-only query 후보
Expected change:
없음. 원인 매핑만.
Forbidden areas:
publisher, scheduler, DB mutation
Verification:
read-only count/query report
Risk:
LOW

CODE_TASK_CANDIDATE:
AREA: CONTENT_CARD_GENERATION + CONTENT_QUEUE
MODE: GUARDED_FIX
PURPOSE FUNCTION:
card preview 정보가 저장되지 않는 경우, 저장 지점과 실패 사유 기록을 보강한다.
Target files:
실제 감사 결과 기준 작성
Expected change:
card preview result persistence 보강
Forbidden areas:
Telegram runtime behavior, Facebook publisher, scheduler, auth/env/config
Verification:
mock card preview success/failure
Risk:
MEDIUM

최종 문장:
"CONTENT_CARD_GENERATION / CONTENT_QUEUE GUARDED_FIX 완료. card preview 가시성을 보강했고, 게시/전송 동작은 변경하지 않았습니다."

# PHASE 3 프롬프트
## LIVING_DOMAIN / SOCIAL_NEWS_CANDIDATE READ_ONLY_AUDIT

```text
AREA: LIVING_DOMAIN + SOCIAL_NEWS_CANDIDATE
MODE: READ_ONLY_AUDIT
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
Business Insider, NYTimes 등 일반 뉴스가 생활정보 또는 WorkConnect Korea 콘텐츠 후보로 들어오는 분류 조건을 확인하고, 생활정보 후보가 수집/분류/동기화/card preview/review 중 어느 단계에서 멈추는지 read-only로 파악한다.

이번 작업은 원인 감사만 수행한다.
코드 수정, DB 수정, 게시, 스케줄러 변경, 외부 API 호출은 하지 않는다.

보고 언어:
- 작업 보고서, 중간 보고, 최종 보고는 한국어로 작성한다.
- 단, 파일명, 함수명, class명, DB table/column, API endpoint, enum/status code, AREA, MODE, PURPOSE FUNCTION, raw log message는 원문 유지한다.

먼저 읽을 문서:
1. DOC/architecture/00_PRODUCT_NORTH_STAR.md
2. DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
3. DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
4. DOC/architecture/03_SYSTEM_ARCHITECTURE.md
5. DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
6. DOC/architecture/05_CODEX_HARNESS_GUIDE.md
7. DOC/architecture/06_WORK_AREA_REGISTRY.md
8. DOC/correction-loop/README.md
9. DOC/correction-loop/2026-06-20_HARNESS_IMPROVEMENT_REVIEW.md

PHASE 진입 조건:
- PHASE 1 로그 UI 개선 완료 또는 최소한 로그/API 구조 확인 완료
- PHASE 2 card preview 가시성 개선 완료 또는 card preview 저장/노출 경로 확인 완료
- 단, PHASE 2가 보호영역 때문에 중단되었을 경우에도 read-only 감사는 가능

현재 의심:
1. 생활정보 봇이 전용 생활정보 source가 아니라 `NaverNewsCollector`, `GoogleNewsCollector` 같은 뉴스 수집기를 재사용하고 있다.
2. 생활정보 후보가 `social_news.candidate`를 거쳐 들어온다.
3. `is_living_content()` 또는 유사 분류 조건에 따라 `LIVING_INFO` / `LIVING_GUIDE`로 변환된다.
4. 이 과정에서 Business Insider, NYTimes 같은 일반 뉴스가 WorkConnect Korea 후보로 들어올 수 있다.
5. 반대로 진짜 생활정보 후보는 카드 생성/review까지 못 가고 중간에서 `SKIPPED`, `FAILED`, `LOW_SCORE`, `DUPLICATE`, `NOT_REQUIRED` 등으로 빠질 수 있다.

검토 대상 파일 후보:
- SRC/foreign_worker_life_info_collector/social/news/pipeline.py
- SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py
- SRC/foreign_worker_life_info_collector/social/news/category_rotation.py
- SRC/foreign_worker_life_info_collector/social/news/candidate_evaluator.py
- SRC/foreign_worker_life_info_collector/content/service.py
- SRC/foreign_worker_life_info_collector/content/repository.py
- SRC/foreign_worker_life_info_collector/admin_ui/src/views/LifestyleInfoPage.vue
- SRC/foreign_worker_life_info_collector/api/admin_server.py
- living/lifestyle/domain collector 관련 파일
- DB read-only query 후보

확인 질문:

## A. 생활정보 수집/분류 구조
1. 생활정보 봇은 어떤 collector를 사용하는가?
2. 생활정보 전용 source/domain table이 있는가?
3. 생활정보 후보는 `social_news.candidate`를 재사용하는가?
4. `LifestyleInfoPage.vue`는 어떤 API와 어떤 table/view를 보고 있는가?
5. 생활정보 후보의 category/source_domain/content_type은 어디서 결정되는가?
6. `LIVING_INFO`, `LIVING_GUIDE`, `SOCIAL_NEWS` 분기는 어디에서 일어나는가?

## B. 일반 뉴스가 생활정보 후보로 들어오는 조건
1. Business Insider 위험국가 기사 같은 travel/general news가 왜 후보로 남는가?
2. NYTimes 한국 술/섬 기사가 왜 `housing` 또는 생활정보 계열로 분류됐는가?
3. category keyword, source domain, title keyword, score 중 무엇이 영향을 주는가?
4. `target_country/channel fit`이 실제 코드에서 반영되는가?
5. `Generic Low-Value Topic`, `Target Country Mismatch`, `Signal to Source-Backed Content` 규칙이 실제 구현에 반영되어 있는가?
6. score 100.00 같은 높은 점수가 왜 일반 뉴스에 부여되는가?

## C. 생활정보 후보가 card/review까지 못 가는 원인
1. 최근 생활정보 후보가 실제로 생성되는가?
2. 생성된다면 어떤 status에서 멈추는가?
3. `content_service.sync_social_news()`가 생활정보 후보를 `content.content_candidate`로 동기화하는가?
4. `review_targets()`가 생활정보 후보를 가져오는가?
5. card preview 대상 조건에 생활정보가 포함되는가?
6. zero score, invalid language, overflow, duplicate, low score 등으로 제외되는가?
7. Telegram review suppress 또는 recurrence suppression이 발생하는가?

## D. DB read-only query 후보
실제 DB query를 실행하지 말고, 필요한 경우 후보만 작성한다.
안전하다고 판단되는 경우에도 read-only SELECT만 작성하고 실행 여부를 보고한다.

확인하고 싶은 count/query 후보:
- 최근 24시간 `social_news.candidate` status/category/source count
- 최근 24시간 생활정보 category 후보 count
- `source_domain = LIVING_INFO`
- `content_type = LIVING_GUIDE`
- `content.content_candidate` status별 count
- card preview 관련 publish_log count
- review target으로 선별된 후보 count
- skipped/failed reason count

금지 변경:
- 소스코드 수정 금지
- DB mutation 금지
- migration 금지
- scheduler 변경 금지
- Facebook publisher 변경 금지
- Telegram runtime behavior 변경 금지
- content publisher 변경 금지
- auth/env/config 변경 금지
- 외부 API 호출 금지
- 실제 수집 실행 금지
- 실제 게시 금지
- score/classification 수정 금지
- category keyword 수정 금지
- commit/push 금지

허용:
- 코드 read-only 확인
- 문서 read-only 확인
- 안전한 read-only DB query 후보 작성
- 실제 DB query는 명시적으로 안전하고 필요할 때만 SELECT로 제한
- 원인 후보와 수정 후보 작성

보고서 형식:

# LIVING_DOMAIN / SOCIAL_NEWS_CANDIDATE READ_ONLY_AUDIT 보고서

## 1. 결론 요약
- 일반 뉴스가 생활정보/WorkConnect 후보로 들어오는 가장 유력한 원인
- 진짜 생활정보 후보가 card/review까지 못 가는 가장 유력한 원인
- 바로 수정 가능한 부분
- 추가 DB 확인이 필요한 부분

## 2. 읽은 architecture 문서
- 적용한 하네스 원칙 요약

## 3. 확인한 파일
- 파일 경로
- 역할
- 관련 흐름

## 4. 생활정보 수집/분류 흐름
아래 흐름으로 실제 구현 정리:

```text
collector
-> social_news.candidate
-> evaluator/classifier
-> content_service.sync_social_news()
-> content.content_candidate
-> review_targets()
-> card preview
-> Telegram review

각 단계별:

구현됨 / 미구현 / 불명확
관련 파일
status/category/source_domain/content_type
5. 일반 뉴스 유입 원인 분석
Business Insider 류 travel/global news
NYTimes 류 human-interest/general Korea news
score/category/source 영향
target country mismatch 처리 여부
low-value topic 처리 여부
6. 생활정보 후보 미노출 원인 분석
수집 없음
후보 생성 후 skip
content sync 누락
review target 미선정
card preview 실패
Telegram review suppress
UI 미노출
각 가능성별 근거/반증/판정
7. 필요한 DB read-only query 후보

실행 여부를 명시하고, 실행하지 않았다면 후보로만 작성.

각 query 후보는 아래 형식:

QUERY_CANDIDATE:
Purpose:
Tables:
SQL:
Risk:
Expected insight:
8. 수정 후보

각 후보는 아래 형식:

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

A. 일반 뉴스 low-value / target country mismatch 분류 보강
AREA 후보: SOCIAL_NEWS_CANDIDATE + LIVING_DOMAIN
MODE 후보: GUARDED_FIX
목표: generic travel/international/human-interest/news가 생활정보 후보로 잘못 승격되지 않게 함

B. 생활정보 후보 content sync/review target 조건 보강
AREA 후보: LIVING_DOMAIN + CONTENT_QUEUE
MODE 후보: GUARDED_FIX
목표: 진짜 생활정보 후보가 content candidate/review/card preview로 이어지게 함

C. DB read-only 집계 작업
AREA 후보: LIVING_DOMAIN + CONTENT_QUEUE
MODE 후보: READ_ONLY_AUDIT
목표: 실제 row count/status/reason으로 병목 확인

9. 위험/보호 영역
publisher 필요 여부
scheduler 필요 여부
DB migration 필요 여부
Telegram runtime behavior 필요 여부
Python vs Java ownership 여부
protected change 여부
10. 추천 다음 단계
바로 가능한 GUARDED_FIX
먼저 DB read-only가 필요한지
architecture 보강이 필요한지
publisher/scheduler/auth 등 보호영역 필요 여부

중단 조건:

publisher/scheduler/auth/env/config 변경이 필요하면 중단
DB mutation/migration이 필요하면 중단
실제 수집/게시/외부 API 호출이 필요하면 중단
Python vs Java ownership을 임의 결정해야 하면 중단
classification 수정이 보호영역과 충돌하면 중단

최종 문장:
"LIVING_DOMAIN / SOCIAL_NEWS_CANDIDATE READ_ONLY_AUDIT 완료. 수정은 실행하지 않았고, 분류/동기화/card review 병목과 다음 작업 후보만 분리했습니다."

# PHASED_EXECUTION 실행 결과 - 2026-06-20

AREA: DASHBOARD_LOGS + CONTENT_CARD_GENERATION + CONTENT_QUEUE + LIVING_DOMAIN + SOCIAL_NEWS_CANDIDATE
MODE: PHASED_EXECUTION
PURPOSE FUNCTION:
완료 구분선 이후 PHASE 1, PHASE 2, PHASE 3 작업을 순차 실행하고, 진행 가능한 범위의 구현/검증/감사를 완료했다.

## PHASE 1 결과

- 실행 여부: 실행 완료
- 수정 범위:
  - `/api/logs/recent` read-only query filter 확장
  - `social_news.pipeline_step_log` 기반 운영 로그 독립 화면 추가
  - `시스템 설정 > 코드 가이드`, `시스템 설정 > 운영 로그` 하위 메뉴 연결
- 검증:
  - `python -m py_compile` 성공
  - `npm run build` 성공
- 보호영역:
  - DB schema/migration, publisher, scheduler, Telegram runtime behavior, Facebook publisher, auth/env/config, content.publish_log 통합 미수정

## PHASE 2 결과

- 실행 여부: 실행 완료
- 수정 범위:
  - `content.publish_log.request_payload.content_card_preview` read-only 추출
  - Content Management 상세 로그에서 `content_card_preview.status/reason/image_path/template_type` 표시
  - raw payload 객체를 JSON 문자열로 표시
- 검증:
  - `python -m py_compile` 성공
  - `npm run build` 성공
- 보호영역:
  - Telegram sendPhoto/sendMessage, approve/reject callback, Facebook publisher, scheduler, auth/env/config, DB schema/migration, card generation algorithm 미수정

## PHASE 3 결과

- 실행 여부: read-only audit 완료
- 코드 확인 결과:
  - 생활정보 봇은 전용 생활정보 source가 아니라 `NaverNewsCollector`, `GoogleNewsCollector`를 `NewsPipeline` dry-run으로 사용한다.
  - 생활정보 화면은 `/api/admin/lifestyle/candidates`를 통해 `social_news.candidate` 중 `content_priority_group = SECONDARY` 기본 필터를 본다.
  - `is_living_content()`는 `SECONDARY`, `TERTIARY`, `travel`, `lifestyle`, `culture`, `local_events`, `safety`까지 `LIVING_INFO/LIVING_GUIDE`로 승격할 수 있다.
  - `content_service.sync_social_news()` 이후 `content.content_candidate`로 sync되고, Telegram review는 `source_domain IN ('LIVING_INFO', 'IMMIGRATION_INFO')`와 `content_quality_gate().review_eligible`를 통과해야 한다.
- DB read-only 확인 결과:
  - 최근 24시간 `social_news.candidate`에는 `SECONDARY settlement_life SKIPPED 8`, `SECONDARY transportation POSTED 5`, `SECONDARY banking/healthcare/insurance SKIPPED 4` 등 생활정보 계열 후보가 존재한다.
  - 최근 7일 `content.content_candidate`에는 `LIVING_INFO/LIVING_GUIDE POSTED 16`, `READY_TO_PUBLISH 1`, `SCORED 3`, `ARCHIVED 3`이 존재한다.
  - 최근 7일 Telegram review card preview는 `CARD_TEXT_MISSING 1606`, `CARD_TEXT_OVERFLOW 23`, `NO_PREVIEW 101`이 확인되어 card preview 병목은 주로 텍스트 부족/오버플로우다.
- 보호영역:
  - 코드 수정 없음
  - DB mutation 없음
  - 실제 수집/게시/외부 API 호출 없음

## 남은 CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + SOCIAL_NEWS_CANDIDATE
MODE: GUARDED_FIX
PURPOSE FUNCTION:
생활정보 후보의 source/category gate를 보강해 일반 뉴스가 `LIVING_INFO/LIVING_GUIDE`로 과승격되지 않게 한다.
WHY:
현재 `SECONDARY/TERTIARY`와 `travel/lifestyle`가 넓게 생활정보로 취급되어 일반 뉴스가 생활정보 후보로 보일 수 있다.
RISK:
MEDIUM
PROTECTED AREA:
publisher, scheduler, Telegram runtime behavior, auth/env/config, DB migration
FILES LIKELY INVOLVED:
`content/service.py`, `social/news/category_rotation.py`, `social/news/evaluator/candidate_evaluator.py`, `LifestyleInfoPage.vue`
RECOMMENDED NEXT PROMPT:
`LIVING_DOMAIN + SOCIAL_NEWS_CANDIDATE GUARDED_FIX`로 생활정보 source/category gate를 좁히고, 뉴스형 일반 기사와 source-backed living guide를 분리하라.

CODE_TASK_CANDIDATE
AREA: CONTENT_CARD_GENERATION + CONTENT_QUEUE
MODE: GUARDED_FIX
PURPOSE FUNCTION:
`CARD_TEXT_MISSING`과 `CARD_TEXT_OVERFLOW`가 반복되는 후보의 card payload 생성/요약 길이/본문 확보 조건을 보강한다.
WHY:
read-only 집계상 Telegram review card preview 실패 대부분이 `CARD_TEXT_MISSING`이다.
RISK:
MEDIUM
PROTECTED AREA:
Telegram runtime behavior, Facebook publisher, scheduler, auth/env/config, DB migration
FILES LIKELY INVOLVED:
`content/card_generator.py`, `utils/content_card_renderer.py`, `content/service.py`, `ContentManagementPage.vue`
RECOMMENDED NEXT PROMPT:
`CONTENT_CARD_GENERATION + CONTENT_QUEUE GUARDED_FIX`로 card payload missing/overflow 원인을 줄이고, 실패 reason별 admin action을 분리하라.

## 10. 재시작 / 재로딩 필요 여부

- Backend restart: YES
  - 이유: `admin_server.py`가 수정되어 API 변경 반영을 위해 backend 재시작이 필요합니다.

- Frontend dev server restart: MAYBE
  - 이유: `router/index.js`, `Sidebar.vue`, 신규 `OperationLogPage.vue`, `ContentManagementPage.vue`가 수정되었습니다. Vite hot reload가 적용될 수 있으나 route/menu 반영을 위해 dev server 재시작 또는 브라우저 hard refresh를 권장합니다.

- Browser hard refresh: YES
  - 이유: 신규 Admin UI route/menu와 로그 화면 반영 확인이 필요합니다.

- DB restart: NO
  - 이유: DB schema/migration 변경이 없습니다.

- Scheduler/Bot restart: NO 또는 BACKEND_RESTART에 포함
  - 이유: scheduler/publisher 동작은 수정하지 않았습니다. 단, backend 프로세스 내부에서 함께 실행 중이면 backend 재시작에 포함됩니다.

- Ollama restart: NO
  - 이유: 이번 PHASED_EXECUTION은 Ollama 관련 코드를 수정하지 않았습니다.

- 사용자가 직접 확인할 것:
  1. backend 재시작
  2. frontend dev server 재시작 또는 브라우저 hard refresh
  3. Admin UI에서 `시스템 설정 > 운영 로그` 메뉴 확인
  4. 운영 로그 검색/필터/더보기 동작 확인
  5. Content Management 상세에서 card preview status/reason 표시 확인

AREA: DASHBOARD_LOGS + CONTENT_CARD_GENERATION + LIVING_DOMAIN
MODE: DOC_ONLY
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
방금 완료된 PHASED_EXECUTION 보고서에 재시작/재로딩 필요 여부를 추가한다.

작업:
`DOC/walkthrough/2026-06-20 - execute prompt.md`의 최신 PHASED_EXECUTION 보고서 하단에 아래 섹션을 추가한다.

추가할 섹션:

## 10. 재시작 / 재로딩 필요 여부

- Backend restart: YES
  - 이유: `admin_server.py`가 수정되어 API 변경 반영을 위해 backend 재시작이 필요합니다.

- Frontend dev server restart: MAYBE
  - 이유: `router/index.js`, `Sidebar.vue`, 신규 `OperationLogPage.vue`, `ContentManagementPage.vue`가 수정되었습니다. Vite hot reload가 적용될 수 있으나 route/menu 반영을 위해 dev server 재시작 또는 브라우저 hard refresh를 권장합니다.

- Browser hard refresh: YES
  - 이유: 신규 Admin UI route/menu와 로그 화면 반영 확인이 필요합니다.

- DB restart: NO
  - 이유: DB schema/migration 변경이 없습니다.

- Scheduler/Bot restart: NO 또는 BACKEND_RESTART에 포함
  - 이유: scheduler/publisher 동작은 수정하지 않았습니다. 단, backend 프로세스 내부에서 함께 실행 중이면 backend 재시작에 포함됩니다.

- Ollama restart: NO
  - 이유: 이번 PHASED_EXECUTION은 Ollama 관련 코드를 수정하지 않았습니다.

- 사용자가 직접 확인할 것:
  1. backend 재시작
  2. frontend dev server 재시작 또는 브라우저 hard refresh
  3. Admin UI에서 `시스템 설정 > 운영 로그` 메뉴 확인
  4. 운영 로그 검색/필터/더보기 동작 확인
  5. Content Management 상세에서 card preview status/reason 표시 확인

금지:
- 소스코드 수정 금지
- DB 수정 금지
- scheduler/publisher/auth/env/config 수정 금지
- 외부 API 호출 금지
- commit/push 금지

보고:
한국어로 작성하고, 파일명/기술 식별자는 원문 유지.

최종 문장:
"재시작 필요 여부 섹션을 PHASED_EXECUTION 보고서에 추가했습니다."

<!-- archived completion marker removed from completed-history copy -->

AREA: CODEX_HARNESS_DOCS + TO_BE_DOCS
MODE: DOC_ONLY
REASONING: HIGH
SPEED: STANDARD

PURPOSE FUNCTION:
Codex가 walkthrough 기반 실행 작업을 할 때, 오늘 날짜의 execute prompt 파일을 먼저 확인하고, 완료 구분선 이후의 작업만 실행하며, 작업 후 PHASE 보고서를 execution-history에 저장하고, 완료 구분선을 문서 맨 마지막으로 이동하도록 하네스 규칙을 보강한다.

이번 작업은 하네스 운영 규칙 보강이다.
실제 PHASE 작업은 실행하지 않는다.

보고 언어:
- 작업 보고서, 중간 보고, 최종 보고는 한국어로 작성한다.
- 단, 파일명, 폴더명, 함수명, class명, API endpoint, AREA, MODE, PURPOSE FUNCTION, status code, raw log message는 원문 유지한다.

먼저 읽을 문서:
1. `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
2. `DOC/architecture/06_WORK_AREA_REGISTRY.md`
3. `DOC/walkthrough/`
4. `DOC/correction-loop/README.md`가 있으면 참고

허용 변경:
- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
- `DOC/architecture/06_WORK_AREA_REGISTRY.md`
- `DOC/walkthrough/README.md` 생성 또는 수정
- `DOC/walkthrough/execution-history/README.md` 생성 또는 수정
- 문서 수정만 허용

금지 변경:
- 소스코드 수정 금지
- DB 수정 금지
- migration 금지
- scheduler 변경 금지
- publisher 변경 금지
- Telegram runtime behavior 변경 금지
- auth/env/config 변경 금지
- 외부 API 호출 금지
- 실제 PHASE 실행 금지
- commit/push 금지

추가해야 할 핵심 규칙:

## 1. Today Execute Prompt Rule

Codex가 walkthrough 기반 실행 작업을 받을 경우, 반드시 오늘 날짜의 execute prompt 파일을 먼저 확인해야 한다.

파일명 기준 예시:

```text
DOC/walkthrough/YYYY-MM-DD - execute prompt.md

또는 실제 파일명이 약간 다를 경우:

DOC/walkthrough/ 안에서 현재 KST 날짜와 `execute prompt`를 포함하는 파일

규칙:

작업 시작 전 오늘 날짜의 execute prompt 파일을 찾는다.
파일을 찾지 못하면 실행하지 말고 stop report를 작성한다.
사용자가 특정 execute prompt 파일을 지정한 경우, 그 파일을 우선한다.
execute prompt 파일을 읽기 전에는 phase 작업을 시작하지 않는다.
2. Completion Marker Rule

완료 구분선은 아래 문자열을 정확히 사용한다.

<!-- archived completion marker removed from completed-history copy -->

규칙:

execute prompt 파일에서 이 완료 구분선을 찾는다.
완료 구분선 이전 내용은 완료/기록 영역으로 본다.
완료 구분선 이후 내용만 실행 대기 큐로 본다.
완료 구분선 이후에 아무 내용도 없으면 실행할 작업이 없는 것으로 보고 stop/report한다.
완료 구분선이 없으면 실행하지 말고 stop report를 작성한다.
완료 구분선이 여러 개 있으면 실행하지 말고 stop report를 작성한다.
3. Pending Queue Execution Rule

Codex는 완료 구분선 이후의 작업을 위에서 아래로 읽는다.

규칙:

PHASE 1, PHASE 2, PHASE 3 등으로 구분된 경우 순차 실행한다.
각 PHASE는 독립 작업으로 처리한다.
각 PHASE마다 PURPOSE FUNCTION, AREA, MODE, 금지조건, 검증조건을 확인한다.
보호영역이 필요하면 즉시 중단한다.
다음 PHASE는 이전 PHASE의 성공 기준을 만족했을 때만 진행한다.
PHASE 조건이 불명확하면 진행하지 말고 보고한다.
4. Completion Marker Move Rule

모든 진행 가능한 PHASE가 끝나면 execute prompt 파일을 업데이트한다.

수행할 일:

기존 위치의 완료 구분선을 제거한다.
이번에 실행한 PHASE 프롬프트와 결과 요약은 문서에 남긴다.
문서 맨 마지막에 완료 구분선을 다시 추가한다.
완료 구분선 아래에는 아직 실행하지 않은 다음 작업 큐만 남긴다.
남은 작업이 없다면 완료 구분선은 문서의 마지막 줄에 위치한다.

즉 최종 구조는 아래와 같아야 한다.

오늘까지의 계획/실행/보고 기록

<!-- archived completion marker removed from completed-history copy -->

아직 실행하지 않은 다음 작업 큐

남은 큐가 없으면:

오늘까지의 계획/실행/보고 기록

<!-- archived completion marker removed from completed-history copy -->
5. Execution History Rule

PHASED_EXECUTION 보고서는 execute prompt 파일 안에만 두지 않고 별도 execution-history 폴더에도 저장한다.

기본 경로:

DOC/walkthrough/execution-history/YYYY-MM-DD/

생성할 수 있는 파일 예시:

DOC/walkthrough/execution-history/YYYY-MM-DD/PHASED_EXECUTION_REPORT.md
DOC/walkthrough/execution-history/YYYY-MM-DD/phase-01-result.md
DOC/walkthrough/execution-history/YYYY-MM-DD/phase-02-result.md
DOC/walkthrough/execution-history/YYYY-MM-DD/phase-03-result.md

규칙:

execute prompt 파일은 실행 큐와 당일 작업 기록이다.
execution-history는 실제 실행 결과 보관소다.
correction-loop는 문제 패턴과 재발 방지 후보를 저장한다.
architecture는 active rule이다.
archives는 과거 스냅샷이다.
Codex는 execution-history를 active permission으로 해석하면 안 된다.
6. Phase Report Storage Rule

각 PHASE가 끝나면 다음 형식으로 phase report를 작성한다.

DOC/walkthrough/execution-history/YYYY-MM-DD/phase-XX-[short-name]-result.md

보고서에는 최소한 아래 항목을 포함한다.

# PHASE XX Result

## 1. 결론 요약
## 2. AREA / MODE / PURPOSE FUNCTION
## 3. 수정한 파일
## 4. 검증 결과
## 5. 보호영역 touched 여부
## 6. 재시작 / 재로딩 필요 여부
## 7. 남은 위험
## 8. 다음 CODE_TASK_CANDIDATE
7. Restart / Reload Report Rule

모든 PHASE 보고서와 PHASED_EXECUTION 보고서에는 반드시 아래 섹션을 포함한다.

## 재시작 / 재로딩 필요 여부

- Backend restart:
  - YES / NO / MAYBE
  - 이유:

- Frontend dev server restart:
  - YES / NO / MAYBE
  - 이유:

- Browser hard refresh:
  - YES / NO / MAYBE
  - 이유:

- DB restart:
  - YES / NO
  - 이유:

- Scheduler/Bot restart:
  - YES / NO / MAYBE
  - 이유:

- External service restart:
  - YES / NO
  - 대상:
  - 이유:

- 사용자가 직접 해야 할 작업:
  1.
  2.
  3.
8. Report Language Rule Reinforcement

이 규칙이 이미 있으면 중복하지 말고 참조만 추가한다.

보고서는 한국어로 작성한다.
기술 식별자는 원문 유지한다.
파일명, 폴더명, 함수명, class명, DB table/column, API endpoint, enum/status code, AREA, MODE, PURPOSE FUNCTION, raw log message는 번역하지 않는다.

수정 대상별 반영 지침:

DOC/architecture/05_CODEX_HARNESS_GUIDE.md
Today Execute Prompt Rule
Completion Marker Rule
Pending Queue Execution Rule
Completion Marker Move Rule
Execution History Rule
Phase Report Storage Rule
Restart / Reload Report Rule
를 추가한다.
위치는 Reporting Policy, Completion Report, 또는 새 섹션 Walkthrough Execution Rule 근처가 적절하다.
DOC/architecture/06_WORK_AREA_REGISTRY.md
TO_BE_DOCS 또는 관련 문서 영역에 walkthrough/execution-history 규칙 참조를 추가한다.
execution-history는 active rule이 아니라 실행 결과 보관소라고 명시한다.
보고 언어 규칙은 05_CODEX_HARNESS_GUIDE.md를 따른다고 짧게 참조한다.
DOC/walkthrough/README.md
없으면 생성한다.
walkthrough의 역할을 설명한다.
execute prompt 파일, 완료 구분선, pending queue, execution-history 관계를 설명한다.
DOC/walkthrough/execution-history/README.md
없으면 생성한다.
execution-history는 실제 실행 결과 보관소라고 설명한다.
active rule이나 implementation permission이 아니라고 명시한다.
phase report naming rule을 설명한다.

성공 기준:

05_CODEX_HARNESS_GUIDE.md에 walkthrough execution / completion marker / execution-history / restart report 규칙이 추가됨
06_WORK_AREA_REGISTRY.md에 execution-history의 authority boundary가 반영됨
DOC/walkthrough/README.md가 생성 또는 보강됨
DOC/walkthrough/execution-history/README.md가 생성 또는 보강됨
실제 PHASE 작업은 실행하지 않음
소스코드 수정 없음
완료 구분선 자체를 지금 execute prompt에서 이동하는 작업은 하지 않음. 이 작업은 규칙 보강만 수행한다.

중단 조건:

소스코드 수정이 필요하면 중단
DB/migration이 필요하면 중단
publisher/scheduler/auth/env/config 변경이 필요하면 중단
실제 PHASE 실행으로 넘어가려 하면 중단
오늘자 execute prompt를 직접 수정해야 한다고 판단되면 이번 작업에서는 후보로만 남긴다

보고 형식:

WALKTHROUGH HARNESS DOC_ONLY 보고서
1. 결론 요약
2. 읽은 파일
3. 수정한 파일
4. 추가한 규칙
5. 생성한 README
6. 수정하지 않은 것
7. 남은 위험
8. 다음 작업 후보

최종 문장:
"Walkthrough execution harness 보강 완료. 앞으로 Codex는 오늘자 execute prompt, 완료 구분선, execution-history 규칙을 따라야 합니다."

<!-- archived completion marker removed from completed-history copy -->

PURPOSE FUNCTION:
WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.

AREA:
LIVING_DOMAIN + SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE + CONTENT_CARD_GENERATION

MODE:
READ_ONLY_AUDIT

FOCUS:
생활정보(LIVING_INFO / LIVING_GUIDE) 도메인에서 뉴스 기사 단독 발행 흐름을 제거하고,
저장된 source / normalized item / fact point / candidate 데이터를 조합해
topic_key 기반 카드형 콘텐츠 후보를 생성할 수 있는지 현재 구조를 검토한다.

TIMEBOX:
60m

READ FIRST:
- DOC/architecture/00_PRODUCT_NORTH_STAR.md
- DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/03_SYSTEM_ARCHITECTURE.md
- DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md

BACKGROUND:
현재 CARD_IMAGE 생성 테스트에서 다음 문제가 확인됐다.

1. 기사 1개가 바로 카드로 변환됨
2. 본문/핵심포인트 부족 시 title + source fallback이 카드 point로 들어감
3. 3-slot 카드 템플릿에 1개 정보만 들어가 빈 카드처럼 보임
4. 이미지 안에 긴 URL 또는 Facebook profile URL이 들어감
5. 생활정보 도메인에서 뉴스 기사 자체가 public/post 후보가 되는 흐름이 있음
6. 같은 기사/후보가 중복 발행 또는 중복 알림될 가능성이 있음

DESIRED PRODUCT DIRECTION:
생활정보 도메인은 뉴스 기사 자체를 발행하지 않는다.
뉴스/기사/커뮤니티/외부 글은 source signal 또는 evidence로만 저장한다.
public content는 저장된 정보들을 topic_key, category, target_user, action_type, source_trust, freshness, actionability 기준으로 조합한 카드형 guide/candidate 중심으로 생성한다.

TARGET FLOW:
external source
-> raw/source 저장
-> normalization
-> duplicate classification
-> domain/category/topic_key 분류
-> fact point 추출
-> usable_for_card 검증
-> topic cluster candidate SELECT
-> 최소 기준 충족 시 CARD_IMAGE candidate 생성
-> Telegram review
-> 수동 승인 후 public delivery

AUDIT QUESTIONS:
1. 현재 LIVING_INFO 또는 LIVING_GUIDE 데이터가 어떤 테이블/엔티티/DTO를 통해 저장되는가?
2. 현재 뉴스 기사 단독으로 content candidate 또는 Facebook post 후보가 되는 경로는 어디인가?
3. 생활정보 도메인에서 news article을 public candidate로 승격시키는 조건은 무엇인가?
4. 현재 topic_key, category, target_user, action_type, trust_level, quality_score, actionability_score, duplicate_key에 해당하는 필드가 존재하는가?
5. fact point 또는 card point에 해당하는 저장 구조가 존재하는가?
6. 없으면 최소 어떤 테이블/컬럼이 필요해 보이는가?
7. 현재 카드 생성기는 어떤 입력값으로 title, subtitle, point1~pointN, source, date, link를 채우는가?
8. title echo / source echo / url echo를 막는 검증 로직이 있는가?
9. source_url, canonical_url, facebook_url, page_profile_url, publishable_link_url이 분리되어 있는가?
10. 이미 발행된 topic/source/content와 비교하는 fingerprint 또는 duplicate check가 있는가?
11. 최근 30일/90일 기준으로 topic cluster를 SELECT할 수 있는 구조인가?
12. Local LLM이 필요한 지점과 deterministic rule/query로 처리 가능한 지점을 분리할 수 있는가?

PROPOSED FUTURE POLICY TO VALIDATE:
- LIVING_INFO / LIVING_GUIDE 에서는 news article 단독 CARD_IMAGE 생성 금지
- news article은 source_signal 또는 evidence로만 저장
- CARD_IMAGE는 topic_key 기반 조합 후보에서만 생성
- source item 최소 3~5개 또는 usable fact point 최소 5~8개 이상일 때만 생성 후보
- 서로 다른 source 2개 이상 필요
- usable_for_card = true point 3개 이상 필요
- title/source/url echo point는 카드 사용 금지
- 같은 topic_key + template_type 최근 발행 이력 있으면 skip/review
- source overlap 또는 point hash overlap이 높으면 중복 후보로 처리
- 이미지 내부에는 긴 URL을 넣지 않음
- 이미지 footer는 WORK CONNECT KOREA / Source / Date 정도만 표시
- 실제 link는 Telegram review message 또는 Facebook caption에만 포함

CHECK CURRENT IMPLEMENTATION FOR:
- collector
- candidate generation
- content approval workflow
- deterministic content generator
- card image generator
- Telegram review message builder
- Facebook publish trigger
- DB migration / DDL
- repository query
- duplicate check
- scheduler path

FORBIDDEN:
- 파일 수정 금지
- DB write 금지
- migration 실행 금지
- scheduler 변경 금지
- Facebook publisher 변경 금지
- Facebook token/payload/retry/frequency 변경 금지
- Telegram approval/reject callback 변경 금지
- admin auth/device approval 변경 금지
- env/secrets 변경 금지
- 외부 API 호출로 실제 게시/알림 발송 금지

DO NOT TOUCH:
- FACEBOOK_PUBLISHER
- CONTENT_PUBLISHER
- SCHEDULER_BOT_STATE
- ADMIN_AUTH
- env/secrets
- destructive DB migration

OUTPUT REPORT IN KOREAN.
Technical identifiers, file paths, class names, method names, table names, and enum values must remain in original form.

REPORT FORMAT:

# READ_ONLY_AUDIT REPORT: LIVING_INFO Topic-Based Card Generation

## 1. Pre-Review
- AREA:
- MODE:
- Risk:
- Protected areas touched: NO
- Files inspected:

## 2. Current Pipeline Summary
현재 생활정보/뉴스/카드 생성 흐름을 source collection부터 Telegram review/Facebook publish 직전까지 요약한다.

## 3. Current Data Model
관련 table/entity/DTO를 정리한다.
특히 다음 항목의 존재 여부를 표시한다.

- source_url
- canonical_url
- publishable_link_url
- source_name
- source_type
- trust_level
- domain
- category
- topic_key
- target_user
- action_type
- quality_score
- actionability_score
- duplicate_key
- fact_point/card_point
- published history/fingerprint

## 4. Where News Becomes Content
뉴스 기사 1개가 content candidate, card image, Facebook post, Telegram review로 승격되는 정확한 코드 경로를 찾는다.

포함:
- class/file
- method/function
- 조건문
- status transition
- template selection
- publish/review trigger

## 5. Card Generation Input Mapping
현재 카드 이미지의 각 영역이 어떤 필드에서 채워지는지 정리한다.

- title
- subtitle
- point/card slot 1
- point/card slot 2
- point/card slot 3
- source
- date
- footer link
- badge/status

그리고 다음 문제가 왜 발생했는지 추정한다.

- title이 point로 반복됨
- source name이 point에 붙음
- footer에 Facebook profile URL이 들어감
- 3-slot 템플릿인데 1개 point만 들어감

## 6. Duplicate / Idempotency Review
다음 중복 차단이 현재 존재하는지 확인한다.

- same source_url
- same canonical_url
- same title + source
- same topic_key
- same content_fingerprint
- same card point hash
- same template_type + topic_key recent published
- publish 직전 READY -> PUBLISHING 원자적 선점

## 7. Feasibility of Topic Cluster SELECT
현재 DB 구조로 아래 개념의 SELECT가 가능한지 판단한다.

개념:
최근 30일 또는 90일 기준으로
domain/category/topic_key/target_user/action_type 단위로 묶고,
source_count, usable_point_count, trust_score, actionability_score가 높은 후보를 선별한다.

필요하면 예시 SELECT 초안을 작성한다.
단, 실제 DB write나 migration은 하지 않는다.

## 8. Gap Analysis
현재 구조에서 부족한 항목을 정리한다.

예:
- topic_key 없음
- fact_point 없음
- usable_for_card 없음
- title echo validation 없음
- source URL과 Facebook page/profile URL 혼동
- 생활정보 뉴스 단독 발행 차단 없음
- 과거 발행 fingerprint 없음

## 9. Recommended Future Implementation Plan
코드 수정은 하지 말고, 안전한 단계별 구현 후보만 제안한다.

Phase 1:
생활정보 뉴스 단독 CARD_IMAGE/public candidate 차단

Phase 2:
card point validation 추가
- title echo
- source echo
- url echo
- minimum point count

Phase 3:
fact_point 또는 card_point 저장 구조 설계

Phase 4:
topic cluster SELECT 후보 생성

Phase 5:
content_fingerprint / duplicate prevention

Phase 6:
Telegram review-only 카드 후보 전송

각 Phase마다:
- AREA
- MODE
- Risk
- 예상 수정 파일
- DB migration 필요 여부
- protected area 포함 여부
- verification plan

## 10. CODE_TASK_CANDIDATE
다음 작업을 Codex용 task candidate 형태로 제안한다.

각 항목은 아래 형식을 따른다.

```text
AREA:
MODE:
PURPOSE FUNCTION:
FOCUS:
RISK:
ALLOWED FILES:
FORBIDDEN:
VERIFICATION:
STOP CONDITIONS:

최소 후보:

LIVING_INFO news 단독 card/public candidate 차단
CARD_POINT_TITLE_ECHO validation 추가
card footer URL 제거 및 source/date 표시 수정
topic_key/fact_point DB 구조 READ_ONLY 설계
topic cluster SELECT query 초안 작성
duplicate/fingerprint audit
11. Stop Conditions Encountered

검토 중 protected area가 필요하거나 ownership이 불명확한 지점을 기록한다.
수정하지 않는다.

12. Final Recommendation

생활정보 도메인을 “뉴스 기사 발행”에서 “조합형 카드 가이드 생성”으로 전환하는 것이 현재 구조에서 가능한지,
가능하다면 가장 안전한 첫 구현 작업이 무엇인지 결론을 낸다.

# READ_ONLY_AUDIT 실행 결과 - 2026-06-20 LIVING_INFO Topic-Based Card Generation

AREA: LIVING_DOMAIN + SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE + CONTENT_CARD_GENERATION
MODE: READ_ONLY_AUDIT

## 결과 요약

- 생활정보 카드 생성 감사 결과를 chat output에만 남긴 누락을 보정했다.
- 실제 감사 보고서를 `DOC/walkthrough/execution-history/2026-06-20/living-info-topic-card-read-only-audit-report.md`에 저장했다.
- 재발 방지 및 harness correction 기록을 `DOC/correction-loop/2026-06-20_LIVING_INFO_TOPIC_CARD_AUDIT.md`에 저장했다.
- 기존 execute prompt 내부의 중복 completion marker 문자열은 archived marker 주석으로 정리했다.
- 남은 pending queue가 없으므로 완료 구분선을 문서 마지막 줄로 이동했다.

## 보호영역 확인

- DB/migration: 수정 없음
- Facebook publisher/content publisher: 수정 없음
- scheduler/bot runtime: 수정 없음
- Telegram callback/runtime behavior: 수정 없음
- auth/env/config: 수정 없음
- external API/actual publish/actual collection: 실행 없음

<!-- archived legacy completion marker removed from completed-history copy -->

PURPOSE FUNCTION:
Improve the WorkConnect Codex harness so short user commands reliably trigger walkthrough queue execution, report persistence, correction-loop recording, and completion marker closure.

AREA:
CODEX_HARNESS_DOCS + SYSTEM_ARCHITECTURE_DOCS

MODE:
DOC_ONLY

FOCUS:
Add a bootstrap/trigger system so Codex no longer misses required closeout steps when the user says short commands such as “다음 작업”, “다음 테스크”, “계속 진행”, or command-style triggers like `!wc-next`.

TIMEBOX:
60m

READ FIRST:

* DOC/architecture/05_CODEX_HARNESS_GUIDE.md
* DOC/architecture/06_WORK_AREA_REGISTRY.md
* DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
* DOC/walkthrough/README.md if it exists
* Today’s DOC/walkthrough/YYYY-MM-DD - execute prompt.md if it exists
* DOC/correction-loop/ recent entries if needed

TASK:
Implement documentation-only harness improvements.

Required updates:

1. Create or update a short root bootstrap document:

   * Prefer `CODEX_BOOTSTRAP.md` or `AGENTS.md` at project root.
   * It must be short.
   * It must tell Codex what to do when the user gives short task commands.

2. Add a Trigger Card to `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`:

   TRIGGER CARD: WALKTHROUGH_QUEUE_COMMAND

   Trigger phrases:

   * 다음 작업
   * 다음 테스크
   * 이어서 진행
   * 계속 진행
   * 다음 큐 진행
   * 오늘 작업 진행
   * `!wc-next`

   Required behavior:

   * Treat the request as WALKTHROUGH_QUEUE_EXECUTION unless the user explicitly says not to use walkthrough.
   * Read the root bootstrap document.
   * Read `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`.
   * Read today’s `DOC/walkthrough/YYYY-MM-DD - execute prompt.md`.
   * Find the single exact completion marker.
   * Execute only the next queued task below the marker or the next clearly pending task.
   * Do not modify protected areas unless explicitly approved.
   * Save the final report to `DOC/walkthrough/execution-history/YYYY-MM-DD/`.
   * Update today’s execute prompt with the execution result.
   * Move or rewrite the completion marker so the final document has exactly one exact marker at the final boundary.
   * If a recurring miss, harness violation, chat-only report, or closure failure occurred, create or update a correction-loop entry.
   * End with the exact completion marker in the execute prompt, not only in chat.

3. Add a Trigger Card to `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`:

   TRIGGER CARD: EXECUTION_CLOSEOUT_REQUIRED

   Condition:

   * Codex has completed any READ_ONLY_AUDIT, DOC_ONLY, LOW_RISK_FIX, GUARDED_FIX, or approved PROTECTED_CHANGE task.

   Required closeout:

   * Report must not exist only in chat.
   * Save report file under `DOC/walkthrough/execution-history/YYYY-MM-DD/`.
   * Update today’s execute prompt.
   * Verify exact completion marker count = 1.
   * Verify loose/duplicate completion marker count = 0.
   * Verify the final line is the exact completion marker when the execute prompt format requires it.
   * Add correction-loop entry if any recurring failure or harness miss happened.
   * State protected areas touched or not touched.
   * State verification performed.

   Stop if:

   * The report cannot be saved.
   * The execute prompt cannot be found and the task requires it.
   * The completion marker state is ambiguous.
   * Closing the task would require guessing.

4. Add a command lexicon:

   Recommended command triggers:

   * `!wc-next` = execute next walkthrough task
   * `!wc-audit` = read-only audit only
   * `!wc-fix` = implement approved bounded fix
   * `!wc-close` = close current task, persist report, update marker
   * `!wc-report` = save/repair missing report only

   Rule:

   * Symbol-only commands such as `!@#$` are discouraged because they are hard to search, hard to audit, and semantically unclear.
   * If symbol-only commands are used, they must map to a named command in the bootstrap document.

5. Completion marker safety:

   * Do not place the exact completion marker string inside examples.
   * Use placeholder text such as `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]`.
   * The real execute prompt must contain exactly one exact completion marker.
   * Any duplicate or loose marker must be archived or renamed so it does not match the exact marker scanner.

6. Correction-loop rule:
   Add or promote a rule stating:

   * “A chat-only report is an incomplete execution for walkthrough-driven Codex work.”
   * “If Codex finishes a task but fails to save the report, update the execute prompt, or maintain the completion marker, this must be recorded as a correction-loop item.”

FORBIDDEN:

* No runtime code changes.
* No DB changes.
* No scheduler changes.
* No Facebook publisher changes.
* No Telegram runtime/callback changes.
* No auth/device approval changes.
* No env/secrets changes.
* No external API calls.
* No actual publish or notification.

OUTPUT REPORT IN KOREAN.
Technical identifiers, file paths, command names, and trigger names must remain in original form.

REPORT FORMAT:

# DOC_ONLY REPORT: Codex Walkthrough Command Bootstrap

## 1. Pre-Review

* AREA:
* MODE:
* Risk:
* Protected areas touched:
* Files inspected:
* Files modified:

## 2. Changes Made

List each created/modified document and the section added.

## 3. Trigger Commands Added

List:

* `!wc-next`
* `!wc-audit`
* `!wc-fix`
* `!wc-close`
* `!wc-report`

## 4. Closeout Rules Added

Explain how report persistence, execute prompt update, correction-loop entry, and completion marker verification are now enforced.

## 5. Completion Marker Safety

Explain how exact marker duplication is prevented.

## 6. Verification

Verify:

* bootstrap document exists or was updated
* `05_CODEX_HARNESS_GUIDE.md` contains WALKTHROUGH_QUEUE_COMMAND
* `05_CODEX_HARNESS_GUIDE.md` contains EXECUTION_CLOSEOUT_REQUIRED
* command lexicon exists
* exact completion marker is not duplicated in examples
* protected areas not touched

## 7. Remaining Risks

List any ambiguity that still requires user decision.

## 8. Final Recommendation

State whether future “다음 작업” or `!wc-next` requests should now reliably trigger the full walkthrough execution and closeout path.

7. Replace the legacy completion marker with a machine-readable WorkConnect marker.

New exact completion marker:
`[WC_EXECUTION_COMPLETE_ARCHIVED_REFERENCE]`

Required behavior:

* Stop using the old decorated Korean marker line.
* The execute prompt must contain exactly one exact completion marker.
* The exact marker must appear on its own line.
* The exact marker must be the final line of the execute prompt after closeout.
* Codex must search for `[WC_EXECUTION_COMPLETE_ARCHIVED_REFERENCE]` as the execution boundary.
* Codex must execute only the next queued task below the previous marker position or the next clearly pending task after reading the execute prompt structure.
* After task completion, Codex must move or rewrite `[WC_EXECUTION_COMPLETE_ARCHIVED_REFERENCE]` to the final boundary.
* Do not place the exact marker inside examples, comments, archived sections, or code blocks.
* Use `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]` for examples instead.
* If the old decorated Korean marker exists, migrate it to `[WC_EXECUTION_COMPLETE_ARCHIVED_REFERENCE]`.
* If both old and new markers exist, preserve only one `[WC_EXECUTION_COMPLETE_ARCHIVED_REFERENCE]` at the final boundary and archive/rename the old marker so it cannot be matched.
* Verification must include:

  * exact `[WC_EXECUTION_COMPLETE_ARCHIVED_REFERENCE]` count = 1
  * old decorated Korean marker count = 0
  * loose completion marker count = 0
  * final line is `[WC_EXECUTION_COMPLETE_ARCHIVED_REFERENCE]`

Correction-loop rule:

* If Codex leaves multiple completion markers, uses the old marker, or writes the marker only in chat instead of the execute prompt, record it as a harness closeout failure.

# DOC_ONLY 실행 결과 - 2026-06-20 Codex Walkthrough Command Bootstrap

AREA: CODEX_HARNESS_DOCS + SYSTEM_ARCHITECTURE_DOCS
MODE: DOC_ONLY

## 결과 요약

- short command bootstrap 문서 `CODEX_BOOTSTRAP.md`를 생성했다.
- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`에 `WALKTHROUGH_QUEUE_COMMAND`와 `EXECUTION_CLOSEOUT_REQUIRED` trigger card를 추가했다.
- `!wc-next`, `!wc-audit`, `!wc-fix`, `!wc-close`, `!wc-report` command lexicon을 추가했다.
- legacy decorated Korean marker를 WorkConnect machine-readable marker 체계로 교체했다.
- marker examples는 `[COMPLETION_MARKER_EXAMPLE_DO_NOT_COPY]`를 쓰도록 정리했다.
- chat-only report와 marker closeout 실패를 correction-loop 기록 대상으로 명시했다.
- 실행 결과 보고서를 `DOC/walkthrough/execution-history/2026-06-20/codex-walkthrough-command-bootstrap-doc-only-report.md`에 저장했다.
- closeout failure correction-loop 기록을 `DOC/correction-loop/2026-06-20_WALKTHROUGH_CLOSEOUT_MARKER_FAILURE.md`에 저장했다.

## 보호영역 확인

- DB/migration: 수정 없음
- Facebook publisher/content publisher: 수정 없음
- scheduler/bot runtime: 수정 없음
- Telegram callback/runtime behavior: 수정 없음
- auth/env/config: 수정 없음
- external API/actual publish/actual notification: 실행 없음

[WC_EXECUTION_COMPLETE_ARCHIVED_REFERENCE]

!wc-fix

PURPOSE FUNCTION:
WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.

AREA:
LIVING_DOMAIN + CONTENT_CARD_GENERATION

MODE:
GUARDED_FIX

FOCUS:
Keep broad information collection enabled, but prevent premature CARD_IMAGE/public living guide generation from single LIVING_INFO news/article items.

This task must not reduce collection coverage.
It must only improve content/card generation readiness gates.

TIMEBOX:
60m

READ FIRST:

* CODEX_BOOTSTRAP.md or AGENTS.md if present
* DOC/architecture/05_CODEX_HARNESS_GUIDE.md
* DOC/architecture/06_WORK_AREA_REGISTRY.md
* DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
* DOC/architecture/03_SYSTEM_ARCHITECTURE.md
* DOC/walkthrough/YYYY-MM-DD - execute prompt.md
* DOC/walkthrough/execution-history/2026-06-20/living-info-topic-card-read-only-audit-report.md if present
* DOC/correction-loop/2026-06-20_LIVING_INFO_TOPIC_CARD_AUDIT.md if present

BACKGROUND:
A READ_ONLY_AUDIT found the following problems:

1. A single news/article item can become a `LIVING_INFO / LIVING_GUIDE` card.
2. When body/key points are insufficient, `title + source_name` fallback can become a card bullet.
3. A 3-slot card template can be generated with only 1 real point.
4. Long URL or Facebook profile URL can appear inside the card image footer.
5. Telegram duplicate suppression exists, but it does not prevent poor card generation itself.
6. The current structure is closer to “living news article card” than “topic-based living guide card.”

IMPORTANT PRODUCT DECISION:
Do not block collection of news/articles/blog/community items.

News, blogs, media articles, and community posts may still be collected and stored as:

* raw source evidence
* source_signal
* normalized item
* topic clustering material
* future card generation evidence

However, for `LIVING_INFO / LIVING_GUIDE`:

* do not generate `CARD_IMAGE` directly from a single news/article/source item
* do not promote a single news/article/source item directly into public living guide content
* use news/article items only as evidence or signal until enough validated topic-level information exists

TARGET BEHAVIOR:
For `LIVING_INFO / LIVING_GUIDE`:

* Continue collecting LIVING_INFO-related news/articles/blog/community items.
* Store them as raw source, normalized item, source_signal, or evidence.
* Do not delete, skip, suppress, or reduce collection only because the item is news.
* Do not generate `CARD_IMAGE` directly from one news/article/source item.
* Do not promote one news/article/source item directly as public living guide content.
* If card points are insufficient, mark card generation as not ready.
* Keep the item available for future topic clustering.
* Do not allow title/source/url fallback text to become a card point.
* Require at least 3 validated card bullets for 3-slot card templates.
* If fewer than 3 validated bullets exist, block card image generation and keep the candidate as text review / evidence only / card not ready, using the closest existing internal mechanism.
* Do not put long URLs or Facebook profile URLs inside the card image.
* Image footer should use brand/source/date only:

  * `WORK CONNECT KOREA`
  * `Source: <source_name>`
  * `Updated: <date>`
* Actual links must remain in Telegram review message or Facebook caption only, not inside the image.

IMPLEMENTATION SCOPE:
Inspect and modify only the minimum necessary sections in:

* `SRC/foreign_worker_life_info_collector/content/service.py`
* `SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py`
* related tests if they already exist
* small helper function file only if already part of card generation path

Allowed:

* Add deterministic validation for card bullets.
* Add validation reason fields if existing DTO/dict structure can carry them safely.
* Disable card preview generation for invalid living cards.
* Keep source/candidate data available for future topic clustering.
* Add or update unit/smoke tests using local mock data only.
* Improve runtime renderer validation so it matches or exceeds local LLaMA utility validation.

Forbidden:

* Do not change collectors to reduce news/article collection coverage.
* Do not change source collection coverage.
* Do not delete existing source data.
* Do not change Facebook publisher behavior.
* Do not change Facebook payload, token, retry, frequency, or publish API call.
* Do not change Telegram approval/reject callbacks.
* Do not change scheduler behavior.
* Do not change admin auth/device approval.
* Do not change env/secrets/config.
* Do not run DB migrations.
* Do not perform DB writes except local test fixtures if already part of test framework.
* Do not call external APIs.
* Do not send real Telegram messages.
* Do not publish to Facebook.

VALIDATION RULES TO ADD:
Create deterministic card point validation before rendering.

Reject a bullet/card point if:

* it is empty or too short to be meaningful
* it equals the title after normalization
* it mostly repeats the title
* it is `title + source_name`
* it contains only source attribution
* it contains a URL
* it contains `facebook.com/profile.php` or any Facebook page/profile URL
* it contains internal/system/error text such as:

  * `No article body`
  * `Content unavailable`
  * `Failed to fetch article`
  * `Parser error`
  * `Access denied`
  * `threshold`
  * `queue`
  * `publish`
  * `diagnostic`
* it is only a generic source label or category label
* it is duplicated with another bullet after normalization

For 3-slot card templates:

* require at least 3 validated bullets
* render only validated bullets
* if fewer than 3 valid bullets remain, block card rendering

LIVING_INFO SINGLE ARTICLE PUBLIC-CARD RULE:
If `source_domain = LIVING_INFO` or `content_type = LIVING_GUIDE`,
and the candidate appears to be based on a single news/article/source item without topic-cluster or fact-point evidence:

* keep the source item collected and stored
* keep it available as source_signal/evidence
* do not delete or block the raw/normalized source
* do not generate `CARD_IMAGE`
* do not promote it as public living guide content
* mark the card generation result as not ready / text review only / evidence only using the closest existing internal mechanism
* add clear reason when possible:

  * `single_news_public_card_not_ready`
  * `evidence_only`
  * `source_signal_only`
  * `insufficient_topic_evidence`
  * `insufficient_valid_card_points`
  * `card_point_title_echo`
  * `card_point_source_echo`
  * `card_point_url_echo`

If the current model does not have a clean status field for this:

* do not invent a broad new workflow
* keep the candidate reviewable if existing flow requires it
* disable card preview generation
* expose/log a clear non-public reason

FOOTER RULE:
Modify card payload/rendering so image footer never uses:

* full `source_url`
* `canonical_url`
* `publishable_link_url`
* Facebook page/profile URL

Footer should be built from:

* brand: `WORK CONNECT KOREA`
* source name
* updated date / collected date / published date, whichever the current payload safely supports

Do not remove source links from Telegram review messages or normal text metadata unless they are currently leaking into the image.

CHECK CURRENT IMPLEMENTATION:
Before editing, identify:

* where `source_domain = LIVING_INFO` and `content_type = LIVING_GUIDE` are assigned
* where `build_content_card_payload()` fills title/subtitle/bullets/source/footer_url
* where card preview is generated
* where invalid card generation can be blocked without touching publisher/scheduler
* whether tests exist for card rendering or content service

PRE-REVIEW REPORT BEFORE EDITING:
Print a short pre-review in Korean:

* AREA:
* MODE:
* Risk:
* Files inspected:
* Files planned to modify:
* Protected areas involved:
* Decision:
* Verification plan:

STOP CONDITIONS:
Stop and report if:

* the fix would require reducing collection coverage
* the fix would require collector/source suppression changes
* blocking card generation requires Facebook publisher changes
* blocking card generation requires scheduler changes
* status transition ownership is unclear
* DB migration is required
* Telegram callback changes are required
* auth/env/config changes are required
* the current code path cannot distinguish card preview generation from actual publishing
* fixing requires guessing outside the declared area

VERIFICATION:
Run safe local checks only.

Required if possible:

* unit test or small local script proving title-only article does not produce card bullets
* test/mock candidate where bullet equals title -> rejected
* test/mock candidate where bullet contains source name only -> rejected
* test/mock candidate where bullet contains URL -> rejected
* test/mock candidate with only 1 valid bullet -> card generation blocked
* test/mock candidate with 3 valid bullets -> card payload/render remains possible
* confirm footer does not contain Facebook profile URL or long source URL
* confirm collection path was not reduced
* confirm no protected area files changed
* confirm no external API calls were made

CLOSEOUT REQUIRED:
This is walkthrough-driven Codex work.

At completion:

* Save final report under `DOC/walkthrough/execution-history/YYYY-MM-DD/`
* Update today’s `DOC/walkthrough/YYYY-MM-DD - execute prompt.md`
* If a harness miss or recurring issue is found, update `DOC/correction-loop/`
* Verify exact `[WC_EXECUTION_COMPLETE_ARCHIVED_REFERENCE]` count = 1
* Verify old decorated Korean completion marker count = 0
* Verify loose completion marker count = 0
* Verify final line is `[WC_EXECUTION_COMPLETE_ARCHIVED_REFERENCE]`
* State protected areas touched or not touched

OUTPUT REPORT IN KOREAN.
Technical identifiers, file paths, class names, function names, table names, enum/status values, and command names must remain in original form.

REPORT FORMAT:

# GUARDED_FIX REPORT: LIVING_INFO Card Generation Guardrail

## 1. Pre-Review

* AREA:
* MODE:
* Risk:
* Protected areas touched:
* Files inspected:
* Files modified:

## 2. Current Cause

Explain where the single-news living card and title/source/url echo problem occurred.

## 3. Changes Made

List each changed file and exact behavior changed.

## 4. Collection Coverage

Confirm that news/article/blog/community collection was not reduced or suppressed.

## 5. Validation Rules Added

List the deterministic validations added.

## 6. LIVING_INFO Single Article Public-Card Guardrail

Explain how `LIVING_INFO / LIVING_GUIDE` single-news card generation is blocked/downgraded while source evidence remains stored.

## 7. Footer URL Fix

Explain how the image footer now avoids long URLs/Facebook profile URLs.

## 8. Verification

List tests/scripts/checks run and result.

## 9. Protected Areas

Confirm:

* Facebook publisher not touched
* scheduler not touched
* Telegram callback not touched
* auth/env/config not touched
* DB/migration not touched
* external API not called
* no real publish/notification sent

## 10. Remaining Risks

List any remaining ambiguity.

## 11. Next CODE_TASK_CANDIDATE

Suggest the next safest task, likely:

* collected LIVING_INFO data audit after several collection runs
* topic_key temporary generation
* fact_point/card_point DB design READ_ONLY_AUDIT
* topic cluster SELECT prototype

## 12. Closeout

Confirm:

* report saved
* execute prompt updated
* correction-loop updated if needed
* `[WC_EXECUTION_COMPLETE_ARCHIVED_REFERENCE]` marker verification passed

# GUARDED_FIX 실행 결과 - 2026-06-20 LIVING_INFO Card Generation Guardrail

AREA: LIVING_DOMAIN + CONTENT_CARD_GENERATION
MODE: GUARDED_FIX

## 결과 요약

- `LIVING_INFO / LIVING_GUIDE` 단일 `social_news.candidate` 기반 카드 preview 생성을 차단했다.
- 수집/동기화 경로는 변경하지 않아 news/article/blog/community evidence 수집 범위는 유지했다.
- 카드 bullet validation을 추가해 title echo, source echo, URL echo, system text, duplicate, insufficient points를 차단했다.
- 3-slot card template은 3개 validated bullets가 있어야 render 가능하게 했다.
- 카드 이미지 footer는 `WORK CONNECT KOREA` 기본값을 사용하고 Facebook profile URL 또는 긴 URL을 넣지 않게 했다.
- 실행 보고서를 `DOC/walkthrough/execution-history/2026-06-20/living-info-card-generation-guardrail-report.md`에 저장했다.

## 수정 파일

- `SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py`
- `SRC/foreign_worker_life_info_collector/tests/test_content_card_generator.py`
- `DOC/walkthrough/execution-history/2026-06-20/living-info-card-generation-guardrail-report.md`
- `DOC/walkthrough/2026-06-20 - execute prompt.md`

## 검증

- `python -m py_compile SRC\foreign_worker_life_info_collector\utils\content_card_renderer.py`: PASS
- `python -m unittest foreign_worker_life_info_collector.tests.test_content_card_generator`: PASS, 14 tests

## 보호영역 확인

- DB/migration: 수정 없음
- Facebook publisher/content publisher: 수정 없음
- scheduler/bot runtime: 수정 없음
- Telegram callback/runtime behavior: 수정 없음
- auth/env/config: 수정 없음
- external API/actual publish/actual notification: 실행 없음

[WC_EXECUTION_COMPLETE]
