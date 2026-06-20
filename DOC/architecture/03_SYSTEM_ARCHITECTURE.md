# System Boundary and Governance Map

## Purpose

This document defines WorkConnect's high-level system boundaries, governance layers, and component responsibilities.

It protects the product from becoming only a social-posting automation system.

## High-Level Architecture

WorkConnect is organized as:

```text
external sources
-> collectors and backend workflow
-> database and content management
-> admin UI and operation controls
-> public delivery channels
-> feedback and knowledge layer
```

Current runtime is local before production deployment.

Current active public channel is Facebook Page: WorkConnect Korea.

Current operator channel is the local admin web UI.

## Governance Layer

Central governance defines product purpose and boundaries.

Module harnesses execute within those boundaries.

```text
product constitution
-> growth workflow
-> data quality and classification
-> system boundary
-> runtime safety
-> Codex harness
-> work area registry
```

Module code or module documentation must not redefine the product purpose.

## Document-to-Layer Control Map

- `00_PRODUCT_NORTH_STAR.md`: product purpose and classification worldview
- `01_SYSTEM_GROWTH_WORKFLOW.md`: lifecycle, growth loop, correction loop
- `02_DATA_SOURCE_AND_QUALITY.md`: validation gates and classification triggers
- `03_SYSTEM_ARCHITECTURE.md`: component ownership and governance map
- `04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`: local runtime safety and runtime triggers
- `05_CODEX_HARNESS_GUIDE.md`: Codex operating harness
- `06_WORK_AREA_REGISTRY.md`: module harness boundaries

## Document Authority Map

- `DOC/architecture/00` through `DOC/architecture/06`: active governance and active harness rules
- `DOC/architecture/07`: review reference and restructure rationale, not the primary execution rule set
- `DOC/correction-loop`: backlog and promotion candidates, not active implementation permission
- `DOC/to-be`: future plans, not approval to implement
- `DOC/walkthrough`: task history and reports
- `DOC/archives`: historical snapshots, not active rules
- `DOC/database`: DB reference and planning docs; implementation still requires task approval

Codex must not treat backlog, to-be, walkthrough, archive, database-reference, or review-reference documents as permission to implement.

## Module Harness Map

Work areas in `06_WORK_AREA_REGISTRY.md` are module harnesses.

Examples:

- `SOCIAL_NEWS_COLLECTOR`: collects and preserves source evidence
- `SOCIAL_NEWS_CANDIDATE`: normalizes, deduplicates, scores, and classifies news candidates
- `CONTENT_QUEUE`: manages reviewable/publishable content candidates
- `IMMIGRATION_DOMAIN`: handles official immigration/visa information with review sensitivity
- `LIVING_DOMAIN`: handles practical settlement/lifestyle information
- `FACEBOOK_PUBLISHER`: protected public delivery behavior
- `TELEGRAM_REPORTING`: operation notification and review reporting
- `SCHEDULER_BOT_STATE`: protected recurring automation and bot state

## Main Components

### External Sources

External sources include official agencies, public portals, employment APIs, occupation dictionaries, immigration pages, trusted media, RSS/search sources, support organizations, and practical living guides.

Sources are not trusted as-is. They must pass validation, normalization, classification, and quality gates.

### Backend

Backend responsibilities:

- expose admin APIs
- run collection pipelines
- normalize sources
- validate data quality
- classify source/domain data
- manage content candidates
- store logs and status
- preserve source evidence
- protect publishing and scheduler boundaries
- call Local LLM only as optional advisory support
- send operation summaries if enabled

The backend validates and controls workflow, but protected publishing behavior cannot be changed casually.

### Database and Content Management

The database should preserve lifecycle boundaries:

```text
raw/source data
-> normalized/domain data
-> content candidates
-> review/publish state
-> publish logs
-> feedback/performance data
```

Source/domain data and publishable content must not be collapsed into the same responsibility.

### Admin UI

Admin UI is the operator cockpit.

It should show:

- what was collected
- what was normalized
- what became content
- what was blocked or skipped
- what needs review
- what was published
- what failed
- bot, scheduler, Facebook, Telegram, and Local LLM status

Admin UI should expose workflow health, not hide it behind raw table dumps.

### Local LLM

Local LLM is optional and advisory.

It may support semantic duplicate checks, relevance checks, summary quality checks, sensitive topic detection, and drafting support.

It must not be required for the system to run and must not control final publishing by itself.

### Public Delivery Channels

Facebook is public delivery.

Future public channels may include website, email, PDF guide, API, GPT interface, and personalized alerts.

## Public Delivery vs Operation Notification Boundary

Facebook publishing and Telegram review/reporting are different pipeline stages.

```text
Facebook = public delivery
Telegram = operation control / review / reporting
Admin UI = operator visibility and manual control
```

Telegram approval or reporting must not be treated as public publishing.

Public publishing must not happen only because an operation notification succeeded.

## Source Data vs Publishable Content Boundary

Source schemas collect, preserve, normalize, and classify evidence.

Content management owns final reviewable or publishable content objects, including final message, final link, validation state, approval state, and publish state.

Target architecture:

- content management should own the final public message
- content management should own the final publishable link
- source/domain tables should preserve and classify evidence
- publisher modules should publish only final approved or reviewable content objects

Known ambiguity to preserve for future audit:

```text
social_news.candidate
vs
content.content_candidate
```

The intended direction is that `content.content_candidate` acts as the final publishable content object, but this document does not resolve current implementation ownership.

Do not change publisher behavior based only on this target boundary. First run the future ownership audit.

## Facebook as Channel, Not Product

Facebook is the first public delivery channel for WorkConnect Korea.

It is not the product.

The product is the structured, source-backed information system behind it.

Facebook token, page, payload, frequency, retry, and selection behavior are protected areas.

## Target Architecture Direction

WorkConnect should evolve toward:

```text
country-specific sources
-> normalized domain data
-> content management
-> review and public delivery
-> feedback/performance
-> reusable knowledge base
-> future GPT/API/subscription layer
```

The architecture must remain expandable beyond Korea and keep country-specific rules separate from global purpose.

## Success Criteria

The system boundary is healthy when:

- Facebook remains a channel, not the product
- Telegram remains operation control, not public delivery
- backend validation prevents unsafe automation
- source data and publishable content remain separated
- Local LLM remains optional
- protected publishing, scheduler, auth, and bot-state areas cannot be changed casually
- Python and Java workflow ownership questions are handled by explicit future audits, not silent assumptions
