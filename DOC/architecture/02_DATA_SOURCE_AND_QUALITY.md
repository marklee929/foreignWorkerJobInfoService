# Data Source and Quality

## Purpose

This document defines how WorkConnect evaluates source data before it becomes content.

WorkConnect collects information from many source types, but not every collected item is useful, safe, or publishable.

The goal is to reduce low-quality data early, preserve reliable source evidence, and prevent broken system messages from becoming user-facing content.

## Core Principle

Data collection is not the final goal.

A collected item becomes valuable only when it can help someone work, live, study, or settle in another country.

Every item should pass through these checks:

```text
source validity
→ content availability
→ duplicate normalization
→ domain relevance
→ user need relevance
→ quality gate
→ content candidate
```

## Supported Source Domains

WorkConnect currently handles or plans to handle these source domains:

- news
- living information
- immigration information
- occupation information
- employment/job information

Each source domain may have different collectors and tables, but all should follow the same quality flow.

## Source Lifecycle

### 1. Source Discovery

The system may discover potential sources from:

- official websites
- public agency pages
- trusted media
- RSS feeds
- search APIs
- domain APIs
- public datasets
- manually added sources

Discovery does not mean the item is valid content.

### 2. Raw Source Collection

The first collected record must preserve source evidence.

Required source evidence:

- source name
- source URL
- original URL if different
- original title
- original summary if available
- original body if available
- published date if available
- collected date
- source type
- language
- raw payload if available

Raw source fields should not contain generated summaries, internal errors, or system fallback messages.

### 3. Source Normalization

After collection, the system should normalize:

- canonical URL
- resolved article/detail URL
- source domain
- title
- body text
- language
- country
- category
- hash key
- similarity key
- source trust level

The system should distinguish:

- discovery URL
- source URL
- canonical URL
- publishable link URL

These should not be treated as the same thing.

## Source Trust Levels

### Primary Sources

Official or authoritative sources.

Examples:

- immigration agencies
- labor ministries
- employment agencies
- public service portals
- official local government pages
- official visa or resident support pages
- official job/occupation APIs

Primary sources can support high-confidence guides and policy explainers.

### Trusted Media Sources

Reliable media sources that explain current events or policy changes.

Examples:

- established local English-language media
- national news agencies
- reputable international media when directly related to the target country

Media sources are useful, but they are not official policy sources.

### Secondary Sources

Useful but requiring validation.

Examples:

- support centers
- NGOs
- universities
- public-service partners
- bank, insurance, hospital, or housing guides
- community organizations

Secondary sources may become content if they are practical and source-backed.

### Discovery Sources

Sources used to find topics, not to publish directly.

Examples:

- Google News RSS
- search result snippets
- aggregator pages
- public community search result pages
- public forum or Q&A URLs

Discovery sources should not become final publish links unless the real original article/detail URL and usable content are resolved.

Discovery sources may identify user questions or emerging topics, but they do not automatically become publishable source evidence.

### Community and Forum Sources

Community, forum, social, and Q&A sources may be useful for discovering user concerns.

Examples:

- Reddit posts or comments
- Quora questions
- public forum threads
- public blog comments
- public Facebook group links when access and terms allow

Rules:

- Treat these as user-need signals, not authoritative facts.
- Respect platform terms, robots rules, API policies, and login/access restrictions.
- Do not collect private, closed-group, paywalled, or access-controlled content without explicit approval.
- Do not store personal identifiers unless there is a clear policy and anonymization rule.
- Do not quote personal stories directly in public content.
- Convert findings into anonymized topic patterns, FAQs, or content ideas.
- Validate any factual, legal, visa, labor, medical, financial, or safety claim against primary or trusted sources before publishing.

Community sources should usually flow through:

```text
discovery signal
-> topic candidate
-> source-backed validation
-> content candidate
```

They should not bypass source trust and quality gates.

## Data Quality Gates

### Gate 1 - Source URL Validity

The item must have a usable source URL.

Block or review if:

- URL is empty
- URL is only a search result
- URL is a Google News RSS URL
- URL is only a publisher root URL
- URL is an unresolved redirect
- URL cannot be tied to a real article, notice, or data page

### Gate 2 - Content Availability

The item must have enough content to summarize.

Acceptable:

- full body
- official notice body
- structured API data
- sufficient article summary
- reliable metadata plus source link

Not acceptable as user-facing content:

- 저장된 기사 본문이 없습니다.
- 일부 RSS/검색 결과는 원문 HTML 접근이 제한될 수 있습니다.
- No article body was saved.
- Content unavailable.
- Failed to fetch article.
- Parser error.
- Access denied.

These are system or collector messages.

They may be stored in diagnostic fields, but they must never be copied into:

- summary
- content body
- Facebook message
- why-it-matters
- user-facing guide text

### Gate 3 - Duplicate and Source Normalization

The system should identify duplicate or near-duplicate data before content creation.

Duplicate types:

- same URL repeat
- same canonical URL
- same title same source
- same title different source
- syndicated copy
- same topic different article

Duplicate data should not be deleted automatically.

It should be classified.

Important rule:

- same URL repeat = noise
- same topic from multiple sources = signal

Only representative or meaningfully distinct items should become content candidates.

### Gate 4 - Domain Relevance

The item must belong to at least one WorkConnect domain.

Primary domains:

- work
- visa
- immigration
- labor rights
- occupation
- employment
- housing
- healthcare
- banking
- insurance
- transportation
- language
- local support
- public services
- daily life

A country-related article is not automatically WorkConnect-relevant.

For example:

- local election strategy article: usually not relevant
- stock market milestone article: low relevance / economy context only
- visa eligibility update: relevant
- foreign worker labor rights notice: relevant
- housing contract guide: relevant

### Gate 5 - User Need Relevance

The item should help answer a real user question.

Examples:

- Can I work there?
- What visa or permit do I need?
- What should I prepare?
- What rights or risks should I know?
- Where can I get help?
- How do I handle daily life after arrival?

If it does not help answer one of these, it should not become high-priority content.

### Gate 6 - Actionability and Repeatability

WorkConnect should prioritize repeatable practical guidance over one-time news.

High-value examples:

- visa checklist
- employment document guide
- housing contract warning
- health insurance explanation
- labor rights steps
- occupation guide
- official policy explainer

Lower-value examples:

- general politics
- generic economy news
- stock market movement
- celebrity/lifestyle news
- one-time human interest story without practical guidance

News can create reach.

Repeatable practical guidance creates subscription value.

## Minimal LLM Validation Policy

LLM validation should be used carefully.

The system should not call an LLM for every item if deterministic rules can reject or classify the item first.

### Preferred Validation Order

```text
rule-based validation
-> metadata validation
-> duplicate/hash validation
-> source/domain scoring
-> local LLM validation only if needed
-> external or larger LLM only if explicitly allowed
```

### Use Local LLM For

Local LLM can be used for limited advisory checks:

- unclear domain classification
- semantic duplicate check
- user need relevance check
- sensitive topic detection
- summary quality check
- whether article can become a checklist/guide

### Do Not Use Local LLM For

- validating secrets
- deciding final legal meaning
- overriding official source text
- publishing directly
- replacing deterministic URL/content validation
- processing every low-value item

### Local LLM Failure Rule

If local LLM is unavailable:

- fallback to deterministic rules

The pipeline must not fail only because local LLM is unavailable.

## System Message Contamination Policy

Internal messages must never appear in user-facing fields.

Forbidden user-facing text examples:

- 저장된 기사 본문이 없습니다.
- 일부 RSS/검색 결과는 원문 HTML 접근이 제한될 수 있습니다.
- 관리자 재게시 요청으로 즉시 Facebook 게시를 시도했습니다.
- 게시 기준 40점 이상을 충족했습니다.
- 현재 점수:
- READY_TO_PUBLISH
- candidate
- queue
- threshold
- publish_status
- Facebook 게시를 시도

These messages belong only in:

- diagnostic fields
- error logs
- admin-only notes
- pipeline logs

They must not appear in:

- Facebook posts
- content summaries
- why-it-matters text
- public guides
- generated content fields

## Content Candidate Readiness

A source item can become a content candidate only when it has:

- valid source reference
- valid link URL
- meaningful title
- usable content or structured data
- domain category
- user relevance
- source trust level
- duplicate classification
- language status
- safety status

A content candidate should include:

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

## Domain-Specific Quality Notes

### News

News should be treated as a signal source.

News items should not be published only because they are fresh.

They should be evaluated for:

- foreign resident relevance
- work/settlement impact
- user actionability
- repeated future value
- sensitivity risk

### Living Information

Living information should be practical and reusable.

Examples:

- housing
- banking
- healthcare
- insurance
- transportation
- local support
- language support

A living item should explain what the user can do or check.

### Immigration Information

Immigration information should prefer official sources.

Because visa and stay status information can be sensitive, unclear items should default to review-required.

Generated text should not overstate legal certainty.

### Occupation Information

Occupation data is reference/dictionary data.

It should not be treated as job posting data.

Before becoming content, it may need:

- English name
- keyword enrichment
- possible visa relevance
- industry tags
- foreign worker fit
- content readiness flag

### Employment / Job Information

Employment data should distinguish:

- job posting
- job category
- occupation dictionary
- employment policy
- labor market article

Job posting data must include clear source, employer or listing source, date, and availability status.

## Content Management Goal

All validated source/domain items should flow into the content management layer when appropriate.

The content management layer should allow:

- automatic publishing for safe high-confidence items
- manual review for sensitive or uncertain items
- admin editing
- additional publishing
- re-publishing with improved message
- archiving
- rejection
- performance tracking

The first goal is automated operation.

The second goal is admin-controlled improvement.

## Quality Status

Recommended quality statuses:

- RAW_COLLECTED
- NORMALIZED
- SOURCE_INVALID
- CONTENT_MISSING
- DUPLICATE_NOISE
- DUPLICATE_SIGNAL
- LOW_RELEVANCE
- LOW_USER_NEED
- REVIEW_REQUIRED
- READY_FOR_CONTENT
- CONTENT_CANDIDATE_CREATED
- CONTENT_INVALID
- READY_TO_PUBLISH
- PUBLISHED
- ARCHIVED

Status names may differ by implementation, but the meaning should remain separated.

Do not mix:

- source collection status
- content readiness status
- publishing status
- operation error status

## Admin Visibility

The admin UI should show why an item was blocked or promoted.

Examples:

- Blocked: Google RSS link only
- Blocked: no usable body
- Blocked: domestic politics, no settlement relevance
- Review: official immigration notice
- Promoted: high actionability visa checklist candidate
- Promoted: living guide with official source

Admins should not have to infer quality reasons from raw logs.

## Success Criteria

This quality system is working when:

- broken article body messages do not appear in public content
- Google RSS links are not used as final publish links
- duplicate rows are classified rather than blindly deleted
- political/economy/general news is filtered unless user-relevant
- official immigration content is handled carefully
- occupation data is not mistaken for job postings
- local LLM is used only when useful
- content management receives useful publishable candidates
- admin can see why an item was accepted, blocked, or reviewed
