# Product System Workflow

## Purpose

This document explains how WorkConnect grows from raw information collection into a reliable work-and-settlement information system.

It is not a low-level implementation guide.

It defines the product workflow that collectors, databases, admin UI, content pipeline, automation, and future GPT interfaces should follow.

## Core Workflow

WorkConnect follows this lifecycle:

```text
user need
→ source discovery
→ source collection
→ normalization
→ domain classification
→ user value evaluation
→ content candidate
→ publishing or review
→ user reaction
→ knowledge improvement
```

The system should not treat collection as the final goal.

The goal is to turn scattered information into useful, repeatable guidance for people working, living, studying, or settling abroad.

## Growth Stages

### Stage 1 — Source Discovery

Goal:

Find information sources that may help people working or settling abroad.

Examples:

* official immigration pages
* employment and labor agencies
* job/occupation dictionaries
* public service notices
* reliable local news
* housing, banking, healthcare, insurance, transportation guides
* local support organizations

Output:

```text
source candidate
```

A source candidate is not yet trusted content.

### Stage 2 — Collection

Goal:

Collect source data without losing evidence.

The system stores:

* original URL
* source name
* original title
* original summary or body
* published date if available
* collected date
* language
* raw payload

Output:

```text
raw item
```

Raw data is evidence and should not be overwritten by generated summaries.

### Stage 3 — Normalization

Goal:

Convert collected data into a consistent internal format.

The system normalizes:

* canonical URL
* clean title
* clean text
* language
* source type
* country
* category
* hash key
* similarity key
* source trust level

Output:

```text
normalized item
```

Normalization makes data comparable across sources and countries.

### Stage 4 — Domain Classification

Goal:

Place normalized data into the correct domain.

Main domains:

* work
* visa
* immigration
* labor rights
* occupation
* housing
* healthcare
* banking
* insurance
* transportation
* language
* local support
* public services
* daily life

Output:

```text
domain candidate
```

A domain candidate belongs to a specific information area.

### Stage 5 — User Value Evaluation

Goal:

Decide whether the information is useful for WorkConnect users.

The system evaluates:

* target user relevance
* work or settlement relevance
* actionability
* repeatability
* subscription value
* source reliability
* freshness
* sensitivity risk
* country relevance

Important principle:

```text
A country-related article is not automatically WorkConnect-relevant.
```

The information must help someone work, live, study, immigrate, settle, or access support in the target country.

Output:

```text
evaluated candidate
```

### Stage 6 — Content Candidate Creation

Goal:

Turn useful domain data into a publishable or reviewable content object.

The system creates:

```text
content candidate
```

A content candidate should contain:

* title
* summary
* why it matters
* target persona
* source link
* category
* publish score
* review status
* source reference

Content candidates are the bridge between internal data and public delivery.

### Stage 7 — Publishing or Review

Goal:

Decide whether content should be published automatically, reviewed manually, or skipped.

Possible outcomes:

```text
publish
review required
sensitive review required
skip
archive
```

Automatic publishing is allowed only when:

* the source is valid
* the link is valid
* the content is useful
* the language is safe
* the topic is not sensitive
* the post does not contain operational text
* the content fits WorkConnect’s product identity

### Stage 8 — Delivery

Goal:

Deliver content through the right channel.

Initial delivery channels:

* Facebook Page
* Telegram operation notifications
* admin UI

Future channels:

* website
* email
* PDF guide
* GPT interface
* API
* personalized alert

Public delivery and operation notification must be separated.

### Stage 9 — Reaction and Feedback

Goal:

Use user reactions to improve content strategy.

Signals:

* views
* clicks
* reactions
* comments
* shares
* saves if available
* subscription conversion
* repeated topic interest

Important lesson:

```text
News can create reach.
Repeatable practical guidance creates subscription value.
```

The system should learn which content types produce real user value, not only views.

### Stage 10 — Knowledge Improvement

Goal:

Turn collected data and user reaction into better future guidance.

The system should gradually build:

* topic clusters
* country-specific guides
* visa/work/life knowledge base
* occupation-to-visa hints
* settlement checklists
* user persona mappings
* recurring update topics

Output:

```text
reusable knowledge
```

## Workflow Shape

WorkConnect is not a single linear pipeline.

It is a growth loop.

```text
collect
→ normalize
→ classify
→ evaluate
→ publish/review
→ observe
→ improve
→ collect better
```

Each loop should improve:

* source quality
* content quality
* user relevance
* publishing safety
* subscription value

## Stage Priority

Early product stages should prioritize:

```text
source reliability
data structure
content usefulness
admin visibility
safe automation
```

Later stages can add:

```text
personalization
paid subscription
country expansion
GPT answers
automated guide generation
multi-language delivery
```

## What This Means for Automation

Automation should not blindly complete the pipeline.

Automation should be allowed to stop when:

* source quality is weak
* relevance is low
* topic is sensitive
* link is invalid
* content is not useful
* protected system areas would be changed
* the task crosses workflow boundaries

A stopped automation with a clear report is better than a completed automation that damages trust.

## What This Means for DB

The DB should preserve lifecycle boundaries.

```text
raw item
→ normalized item
→ domain candidate
→ content candidate
→ publish log
→ feedback/performance data
```

Source data and publishable content should not be mixed.

## What This Means for Admin UI

The admin UI should show where each item is in the workflow.

Examples:

* collected
* normalized
* classified
* evaluated
* ready to review
* ready to publish
* published
* skipped
* archived
* failed

The dashboard should show status and flow health, not raw table dumps.

## What This Means for Content Strategy

Content should move from news-heavy posting toward repeatable practical guidance.

Examples:

* visa checklist
* job/occupation guide
* housing preparation
* banking guide
* healthcare guide
* labor rights guide
* official policy update explainer
* weekly work-and-life abroad digest

News remains useful as a source signal, but it is not the product itself.

## Success Criteria

This workflow is working when:

* collected data becomes reusable knowledge
* content is useful beyond one-time news reading
* users can understand what to do next
* admin can see and control the system safely
* automation can run without crossing protected boundaries
* publishing improves trust rather than creating noise
