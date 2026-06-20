# Data Quality and Classification Worldview

## Purpose

This document defines how WorkConnect evaluates source data before it becomes reviewable or public content.

It separates two different decisions:

```text
validation = whether data is usable
classification = what the data means inside WorkConnect
```

A valid article may still be irrelevant.

## Source Evidence Rule

The first collected record must preserve source evidence:

- source name
- source URL
- original URL if different
- canonical URL if known
- publishable link URL if known
- original title
- original summary or body when available
- published date when available
- collected date
- source type
- language
- country
- raw payload when available

Raw source fields must not contain generated summaries, internal errors, or fallback messages as if they were source facts.

## Source Trust Levels

### Primary Sources

Official or authoritative sources such as immigration agencies, labor ministries, employment agencies, public service portals, official visa pages, local governments, and official job or occupation APIs.

Primary sources can support high-confidence guides and policy explainers, but sensitive claims may still require review.

### Trusted Media Sources

Reliable media sources that explain policy changes, public issues, or current events directly relevant to target users.

Media is useful signal, not official policy.

### Secondary Sources

Support centers, NGOs, universities, public-service partners, banks, insurers, hospitals, housing guides, and community organizations.

Secondary sources may support practical content when source-backed and checked against user need.

### Discovery Sources

Search snippets, Google News RSS, aggregators, community search results, forums, and Q&A pages.

Discovery sources identify topics. They must not become final publish links unless the original usable source page is resolved.

### Community and Forum Sources

Community sources are user-need signals, not authoritative facts.

Rules:

- respect platform terms, robots rules, API policies, and access restrictions
- do not collect private, closed, paywalled, or access-controlled content without explicit approval
- do not store personal identifiers without a clear policy and anonymization rule
- do not quote personal stories directly in public content
- validate factual, legal, visa, labor, medical, financial, or safety claims against primary or trusted sources before publication

## URL and Link Boundary

The system must distinguish:

- discovery URL
- source URL
- canonical URL
- publishable link URL

Block or review when:

- URL is empty
- URL is only a search result
- URL is a Google News RSS URL
- URL is only a publisher root URL
- URL is an unresolved redirect
- URL cannot be tied to a real article, notice, guide, or data page

## Content Availability Gate

A usable item needs enough content to summarize, classify, or cite.

Acceptable:

- full body
- official notice body
- structured API data
- sufficient article summary
- reliable metadata plus source link when the source type supports it

Not acceptable as user-facing content:

- saved article body is missing
- RSS/search result HTML access is restricted
- No article body was saved
- Content unavailable
- Failed to fetch article
- Parser error
- Access denied
- internal status, queue, threshold, or publish instructions

These may appear only in diagnostics, logs, admin-only notes, or stop reports.

## Duplicate Policy

Duplicate data should be classified, not blindly deleted.

Duplicate types:

- same URL repeat
- same canonical URL
- same title same source
- same title different source
- syndicated copy
- same topic different article
- same practical issue across multiple sources

Rule:

```text
same URL repeat = usually noise
same topic from multiple reliable sources = possible signal
```

Only representative or meaningfully distinct items should become content candidates.

## Classification Principle

Classification is a product-worldview problem.

An item belongs in WorkConnect only if it helps the target user make a practical decision, reduce uncertainty, access support, or understand a source-backed rule in the target country.

Generic country-related content is not enough.

Usually block or downgrade:

- generic international news
- travel rankings
- domestic politics without settlement impact
- economy or stock-market news without user actionability
- crypto news
- generic lifestyle or tourism content
- social media trends without source-backed practical value
- weak-source claims about legal, visa, labor, medical, financial, or safety issues

Potentially relevant:

- visa or stay-status update
- labor rights notice
- housing contract guide
- health insurance explanation
- banking or telecom setup guide
- local public service or support guide
- official policy explainer
- safety information tied to living, working, or settling in the target country

## Quality Trigger Cards

### Trigger: Invalid Link

Condition: final link is missing, RSS/search-only, root-only, or unresolved.

Action: block or review; do not publish.

### Trigger: Missing Body

Condition: source body or reliable structured content is missing.

Action: mark content missing; do not create public summary from diagnostic text.

### Trigger: System Text Contamination

Condition: internal status, queue, threshold, error, or publish-operation text appears in user-facing fields.

Action: block candidate and fix earliest contamination layer.

### Trigger: Generic Low-Value Topic

Condition: generic politics, economy, crypto, travel, international ranking, or lifestyle item lacks direct user need/actionability.

Action: downgrade, skip, or store only as reference signal.

### Trigger: Target Country Mismatch

Condition: item is global, non-Korea, generic international, future-market-only, or not directly tied to the current target country/channel.

Action: do not send to WorkConnect Korea public review or publishing by default. Store as future/global reference signal, downgrade, archive, or require explicit review depending on source value. Make target country/channel fit visible in the candidate or review reason.

Do not promote to Korea public content only because it mentions foreigners, travel, international affairs, or general safety.

### Trigger: Sensitive Domain

Condition: visa, immigration, labor rights, medical, financial, safety, or legal meaning is unclear.

Action: require review and prefer primary sources.

### Trigger: Weak Source

Condition: source is community, aggregator, snippet, or unclear authority for factual claims.

Action: use as discovery signal only until validated.

## Domain Duplicate Policy

Duplicate rules may differ by domain:

- News: duplicate article noise should be suppressed; same topic across trusted sources may increase signal.
- Immigration: official duplicate or revised notices should preserve official source lineage and default to review.
- Living information: repeated user questions may indicate guide demand, but public content still needs source-backed validation.
- Occupation: dictionary rows are reference data, not job postings; duplicates should preserve code/source identity.
- Jobs: listings require source, employer/listing source, date, and availability status.

## Review Eligibility Execution Card

Trigger: item passes validation but public suitability is uncertain.

Action:

```text
check source trust
-> check target country/channel fit
-> check user need and actionability
-> check sensitivity
-> check duplicate state
-> send to review, block, or archive
```

Do not touch:

- Facebook publisher payload
- scheduler frequency
- auth/device approval
- destructive DB state

Verify:

- review reason is visible
- source reference is preserved
- public fields contain no diagnostic text

## Signal to Source-Backed Content Execution Card

Use when data comes from a discovery source, community signal, forum, search result, aggregator, RSS snippet, or trend signal.

Steps:

```text
classify as signal first
-> identify primary, trusted media, or practical secondary source validation
-> preserve anonymized topic/user-need signal when useful
-> create public content candidate only after source-backed validation exists
```

Do not:

- treat signal-only data as authoritative fact
- quote personal or community content directly in public content
- promote signal-only data to public review or publishing

Verify:

- source-backed validation is recorded or the item remains a signal
- public fields do not imply authority that the source does not have

## System Message Contamination Policy

Internal messages must never appear in:

- Facebook posts
- public summaries
- why-it-matters text
- guide content
- generated card text
- user-facing content candidate body

Internal messages may appear only in:

- diagnostic fields
- error logs
- admin-only notes
- pipeline logs
- stop reports

## LLM Validation Policy

Use deterministic validation before LLM validation.

Preferred order:

```text
rule-based validation
-> metadata validation
-> duplicate/hash validation
-> source/domain scoring
-> local LLM advisory check only if needed
-> external/larger LLM only if explicitly allowed
```

Local LLM may assist with:

- unclear domain classification
- semantic duplicate checking
- user-need relevance
- sensitive topic detection
- summary quality checks
- guide/checklist potential

Local LLM must not:

- validate secrets
- decide final legal meaning
- override official source text
- replace deterministic URL/body validation
- process every low-value item
- publish directly

If Local LLM is unavailable, use deterministic fallback. The pipeline must not fail only because Local LLM is unavailable.

## Content Candidate Readiness

A source item can become a content candidate only when it has:

- valid source reference
- valid link URL
- meaningful title
- usable content or structured data
- domain category
- target country/channel fit
- target user relevance
- source trust level
- duplicate classification
- language status
- safety status
- review or publish readiness status

Recommended candidate fields:

- source_domain
- source_type
- content_type
- target_country
- target_user
- category
- title
- summary
- why_it_matters
- source_url
- link_url
- source_name
- quality_score
- user_need_score
- repeatability_score
- actionability_score
- subscription_value_score
- status
- raw_ref_table
- raw_ref_id

## Success Criteria

The quality system is working when:

- broken body messages never become public content
- Google RSS/search links are not final publish links
- duplicate rows are classified as noise or signal
- generic politics, economy, travel, crypto, and lifestyle content are filtered unless user-relevant and actionable
- official immigration and labor content is handled carefully
- occupation data is not mistaken for job postings
- Local LLM is optional and advisory
- admins can see why an item was accepted, blocked, or sent to review
