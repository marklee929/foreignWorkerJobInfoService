# Growth Workflow and Correction Loop

## Purpose

This document defines how WorkConnect grows from user need and source discovery into practical content, reusable knowledge, and safer future automation.

It controls workflow shape. It does not define every quality gate; detailed validation and classification rules live in `02_DATA_SOURCE_AND_QUALITY.md`.

## Core Lifecycle

WorkConnect follows this lifecycle:

```text
user need
-> source discovery
-> raw collection
-> normalization
-> duplicate classification
-> domain classification
-> user value evaluation
-> content candidate
-> review eligibility
-> public delivery or operation notification
-> feedback
-> knowledge improvement
```

Collection is not the goal. The goal is practical, repeatable guidance for people working, living, studying, immigrating, or settling abroad.

## User Need Before Source Collection

Before adding or promoting a source, ask:

- Which target user does this help?
- What practical uncertainty does it reduce?
- What decision or next check does it support?
- Is it relevant to the current target country and channel?
- Is the source evidence strong enough for its intended use?

If these questions cannot be answered, the source may remain a discovery signal but should not become public content.

## Workflow Stages

### 1. Source Discovery

Find possible information sources such as official agencies, employment services, visa pages, public notices, trusted media, support organizations, and practical living guides.

Output: `source candidate`.

### 2. Raw Collection

Collect source evidence without losing original context.

Output: `raw item`.

Raw data is evidence and must not be overwritten by generated summaries.

### 3. Normalization

Normalize URL, title, body, language, country, source type, trust level, hash keys, and similarity keys.

Output: `normalized item`.

### 4. Duplicate Classification

Classify repeated or similar data before promotion.

Same URL repeat is usually noise. Same topic from multiple reliable sources may be signal.

Output: `duplicate_noise`, `duplicate_signal`, or representative candidate.

### 5. Domain Classification

Place information into a WorkConnect domain such as work, visa, immigration, labor rights, occupation, housing, healthcare, banking, insurance, transportation, language, local support, public services, safety, or daily life.

Output: `domain candidate`.

### 6. User Value Evaluation

Evaluate actionability, repeatability, target-user relevance, source reliability, freshness, sensitivity risk, and current country/channel fit.

Output: `evaluated candidate`.

### 7. Content Candidate Creation

Create a reviewable or publishable object with title, summary, why it matters, target user, source link, category, status, quality score, and source reference.

Output: `content candidate`.

### 8. Review Eligibility

Decide whether the item should be reviewed, blocked, archived, or prepared for safe publishing.

Sensitive, legal, visa, weak-source, missing-body, or unclear-actionability items should default to review or block.

### 9. Public Delivery or Operation Notification

Public delivery and operation notification are separate.

Facebook is public delivery. Telegram review/reporting is operation control. Admin UI is operator visibility.

### 10. Feedback and Knowledge Improvement

Use performance, review decisions, repeated topics, and operator feedback to improve future source selection, classification, guides, alerts, search, APIs, and GPT-assisted answers.

## Correction Loop Before Patching

When wrong content appears, do not start with one-to-one patching.

First classify the failed lifecycle stage:

```text
source discovery
-> raw collection
-> normalization
-> duplicate classification
-> domain classification
-> user value evaluation
-> review eligibility
-> public delivery
```

Patch the earliest failing layer.

Examples:

- If a Google News RSS URL became a final link, fix URL validation/normalization before publisher behavior.
- If generic politics entered review, fix domain classification or user value evaluation before one article title.
- If internal status text appeared in a post, fix contamination gates before formatting.
- If the same item repeatedly enters Telegram review, fix duplicate identity or review eligibility before message wording.

## Workflow Trigger Points

Stop, downgrade, review, or archive when:

- source evidence is missing
- source body is missing or only diagnostic text
- URL is a search/RSS/root/redirect instead of a usable source page
- the topic is generic international news, travel ranking, politics, economy, crypto, or lifestyle without direct user actionability
- source trust is weak for legal, visa, labor, medical, financial, or safety claims
- duplicate type is unclear
- current target country/channel fit is unclear
- public delivery would cross a protected boundary

## Representative Candidate Rule

Duplicate data should not be blindly deleted.

The system should select or preserve a representative candidate when:

- multiple sources report the same practical update
- one official source confirms a media signal
- multiple user-signal sources point to the same unmet need

Representative selection must preserve source references and duplicate context.

## Feedback and Knowledge Improvement

The growth loop should gradually produce:

- source quality improvements
- topic clusters
- country-specific guides
- visa/work/life knowledge base
- settlement checklists
- occupation and domain readiness hints
- recurring update topics
- safer review and publishing rules

News may create reach, but repeatable practical guidance creates long-term value.

## Success Criteria

The workflow is healthy when:

- collected data becomes reusable knowledge
- content remains useful beyond one-time news reading
- admins can see where an item is in the lifecycle
- automation stops before damaging trust
- public delivery is separated from operation notification
- bad outputs lead to lifecycle-level corrections, not only one-off patches
