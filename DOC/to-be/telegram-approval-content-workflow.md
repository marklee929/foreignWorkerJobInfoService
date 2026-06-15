# Work Connect Korea Telegram Approval Content Workflow

Report date: 2026-06-14 KST

Mode: DOC_ONLY

Code changes: NONE

## 1. Existing Document Summary

Reviewed documents:

- `DOC/architecture/00_PRODUCT_NORTH_STAR.md`
- `DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md`
- `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
- `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
- `DOC/design/content_publishing_hub.md`
- `DOC/flowchart/flowchart-definition.md`
- `DOC/flowchart/flowchart-flow-audit.md`
- `DOC/to-be/content-creation.md`
- `DOC/to-be/topic-search.md`
- `DOC/archives/social-news-automation.md`
- PPT files under `DOC/archives/` for foreign worker job subscription service planning and presentation material.

Core direction from existing planning:

- Work Connect Korea is an information platform for foreigners who want to work, live, study, or settle in Korea.
- The product is not a random news repost bot. It should provide practical, source-backed information.
- The first market is Korea, but the system should avoid becoming Korea-only in its core model.
- Main content domains are work, visa, immigration, housing, healthcare, banking, insurance, transportation, language, local support, public services, rights, and daily life.
- PPT planning emphasizes multilingual job information, visa/labor guidance, public/private data collection, translation caching, subscription plans, newsletters, messenger delivery, and expert consultation.
- The architecture documents already separate raw/source data from final publishable content.
- The newer flowchart direction says `content.content_candidate` should become the final publishing boundary.
- Community data is useful as a user-need signal, not as an authoritative source.
- Direct community quotes, private content, login-protected content, and personal stories must not be republished directly.

Important conflict to resolve:

- Older automation docs describe direct automatic Facebook publishing and Telegram as an operation notification channel.
- The new operating direction is stricter: initial automation must stop at Telegram review, and Facebook/site publishing must happen only after approval.
- This document treats the older direct publish path as transitional and defines the approval-first replacement flow.

## 2. Connection Between Existing Plan And Additional Work

Existing plan already covers:

- Subscription platform concept.
- Multilingual foreigner-facing job and settlement information.
- Public/private source collection.
- Translation, curation, and caching.
- Admin console and delivery channels.
- Content publishing hub direction.

Additional work in this document fills the missing operational contract:

- Add Telegram review as the first public-output guard.
- Prohibit initial automatic publishing.
- Standardize content states from collection to approval to publishing.
- Define source risk levels, especially community and social sources.
- Define final Facebook/site content format before publishing.
- Define minimum DB/API/menu structures for a content approval queue.
- Separate normal written content from premium PDF assets.

Target flow:

```text
Source collection
-> normalization
-> AI content draft
-> quality/risk validation
-> GENERATED
-> send review card to Telegram
-> SENT_TO_TELEGRAM
-> human approve/reject
-> APPROVED or REJECTED
-> approved-only publish to Facebook/site
-> PUBLISHED
```

## 3. Data Source List

### Employment

| Source | Method | Use | Risk |
| --- | --- | --- | --- |
| 고용24 / Work24 job and occupation APIs | Official API | job dictionary, occupation guide, job content seed | Low |
| WorkNet / KEIS | Official API or public feed | job and employment policy reference | Low |
| Seoul job portal / local government job pages | API, RSS, crawler | regional job support | Low-Medium |
| public ATS pages such as Greenhouse, Lever, Workable, Ashby | API/public endpoint | company jobs where terms allow | Medium |
| private job boards such as Saramin, JobKorea, JobPlanet | API or approved crawling only | market signal and job listing metadata | Medium-High |

### Visa / Immigration

| Source | Method | Use | Risk |
| --- | --- | --- | --- |
| HiKorea | crawler/API if available | visa, stay, immigration notices | Low-Medium |
| Ministry of Justice | official notice crawler/RSS | immigration policy source | Low |
| Korea.net / government portals | RSS/API/crawler | public policy explainers | Low |
| local government foreign resident support pages | crawler | programs and local notices | Low-Medium |

### Living Information

| Category | Source examples | Method | Risk |
| --- | --- | --- | --- |
| housing | public housing support pages, city portals | crawler/API | Low-Medium |
| finance | banks' foreign customer pages, FSS notices | crawler/API | Medium |
| telecom | major carrier foreigner pages, public guide pages | crawler | Medium |
| healthcare | NHIS, hospitals' international pages, public health centers | crawler/API | Medium |
| education | language schools, public education support, KIIP notices | crawler/API | Low-Medium |
| experts | labor attorneys, immigration admin offices, legal aid, NGOs | curated registry/manual approval | Medium |

### Community

| Source | Method | Allowed use | Risk |
| --- | --- | --- | --- |
| Reddit | official API where permitted | topic signal, question pattern, anonymized trend | Medium-High |
| public forums/Q&A | search discovery, crawler if terms allow | topic discovery only | Medium-High |
| Naver Blog | search/discovery only unless rights are clear | source discovery, not direct content reuse | High |
| Facebook Groups | only public/access-allowed links and terms review | topic signal only | High |

Community rules:

- Do not collect private, closed, login-only, or paywalled content without explicit approval.
- Do not store direct personal identifiers.
- Do not quote personal stories directly in public content.
- Convert community data into anonymized topic patterns.
- Validate factual, visa, labor, medical, financial, and safety claims against official or trusted sources.

## 4. Collection Schedule

| Domain | Suggested schedule | Reason |
| --- | --- | --- |
| official immigration/visa notices | every 1-3 hours during daytime, daily fallback | policy changes are time-sensitive |
| employment/job feeds | every 3-6 hours | frequent enough for updates without excessive crawling |
| occupation/job dictionary | weekly or manual refresh | reference data changes slowly |
| living information official pages | daily | moderate freshness need |
| social/news RSS | every 30-60 minutes but promotion remains strict | useful for timely alerts |
| community discovery | daily or 2-4 times per day | use as trend signal, not breaking news |
| content generation batch | after collection or scheduled 2-4 times per day | keeps review queue manageable |
| Telegram review send | immediate after successful generation, rate-limited | review-first workflow |
| Facebook/site publish | never automatic in phase 1; approval-only | trust and safety |

## 5. DB Table Draft

### `content.source_item`

Purpose: normalized collected source record.

Fields:

- `id`
- `source_domain`: EMPLOYMENT, VISA_IMMIGRATION, LIVING_INFO, COMMUNITY, SOCIAL_NEWS
- `source_platform`
- `source_name`
- `source_url`
- `canonical_url`
- `publishable_link_url`
- `title`
- `body_text`
- `summary_text`
- `language`
- `country_code`
- `category`
- `subcategory`
- `collected_at`
- `last_seen_at`
- `source_published_at`
- `raw_payload`
- `source_risk_level`
- `access_restriction`: PUBLIC, LOGIN_REQUIRED, PAYWALLED, PRIVATE, UNKNOWN
- `copyright_risk_level`
- `pii_checked_yn`
- `usable_for_content_yn`
- `created_at`
- `updated_at`

### `content.generated_content`

Purpose: AI-generated candidate that requires Telegram review.

Fields:

- `id`
- `source_item_id`
- `content_type`: NEWS_EXPLAINER, JOB_GUIDE, VISA_GUIDE, LIVING_TIP, COMMUNITY_FAQ, EXPERT_GUIDE
- `category`
- `subcategory`
- `target_persona`
- `language`
- `title`
- `written_content`
- `short_summary`
- `why_it_matters`
- `check_next`
- `hashtags`
- `image_url`
- `image_prompt`
- `source_disclaimer`
- `translation_yn`
- `translated_from`
- `original_link`
- `generated_at`
- `generation_model`
- `quality_score`
- `risk_score`
- `status`: COLLECTED, GENERATED, SENT_TO_TELEGRAM, APPROVED, REJECTED, PUBLISHED
- `status_reason`
- `created_at`
- `updated_at`

### `content.review_log`

Purpose: Telegram/admin review trace.

Fields:

- `id`
- `generated_content_id`
- `review_channel`: TELEGRAM, ADMIN
- `telegram_message_id`
- `reviewer_id`
- `reviewer_name`
- `action`: SENT, APPROVED, REJECTED, EDIT_REQUESTED
- `comment`
- `reviewed_at`
- `created_at`

### `content.publish_target`

Purpose: publish destination and final result.

Fields:

- `id`
- `generated_content_id`
- `target_channel`: FACEBOOK, SITE
- `publish_status`: PENDING, PUBLISHED, FAILED
- `published_url`
- `external_post_id`
- `published_at`
- `error_category`
- `error_message`
- `request_payload`
- `response_payload`
- `created_at`

### `content.community_signal`

Purpose: anonymized community trend signal.

Fields:

- `id`
- `source_platform`
- `source_url`
- `topic`
- `language`
- `country`
- `category`
- `question_pattern`
- `frequency_score`
- `urgency_score`
- `sample_count`
- `author_hash`
- `raw_retention_policy`
- `pii_checked_yn`
- `usable_for_content_yn`
- `terms_risk_level`
- `created_at`

## 6. API Specification Draft

### Collection

```text
POST /api/admin/sources/collect
```

Request:

```json
{
  "domain": "VISA_IMMIGRATION",
  "category": "visa",
  "limit": 50,
  "dry_run": true
}
```

Response:

```json
{
  "collected": 20,
  "created": 5,
  "updated": 15,
  "blocked": 2
}
```

### Generate Content

```text
POST /api/admin/content/generate
```

Request:

```json
{
  "source_item_ids": [101, 102],
  "content_type": "LIVING_TIP",
  "language": "en",
  "send_to_telegram": false
}
```

### Send To Telegram

```text
POST /api/admin/content/{id}/send-telegram
```

Rules:

- Allowed only when status is `GENERATED`.
- Changes status to `SENT_TO_TELEGRAM`.
- Does not publish to Facebook or site.

### Telegram Approval Webhook

```text
POST /api/admin/telegram/review-callback
```

Request:

```json
{
  "content_id": 123,
  "action": "APPROVE",
  "reviewer_id": "telegram-user-id",
  "comment": "ok"
}
```

Rules:

- `APPROVE` changes status to `APPROVED`.
- `REJECT` changes status to `REJECTED`.
- `EDIT_REQUEST` keeps status as `SENT_TO_TELEGRAM` or moves to `GENERATED` depending on implementation.

### Publish Approved Content

```text
POST /api/admin/content/{id}/publish
```

Rules:

- Allowed only when status is `APPROVED`.
- Target can be `FACEBOOK`, `SITE`, or both.
- On success, status becomes `PUBLISHED`.

### Admin Read APIs

```text
GET /api/admin/content/dashboard
GET /api/admin/content/items?status=GENERATED&category=employment
GET /api/admin/content/items/{id}
GET /api/admin/source-items?domain=COMMUNITY&risk=HIGH
GET /api/admin/review-logs?content_id=123
```

## 7. Menu Structure

Recommended admin menu:

```text
Dashboard
Sources
  - Source Registry
  - Collection Runs
  - Source Risk Review
Content Queue
  - All Content
  - Telegram Review Queue
  - Approved
  - Rejected
  - Published
Domains
  - Employment
  - Visa / Immigration
  - Living Information
    - Housing
    - Finance
    - Telecom
    - Healthcare
    - Education
    - Experts
  - Community Signals
Publishing
  - Facebook
  - Site
  - Publish Logs
Settings
  - Telegram Reviewers
  - Source Policies
  - AI Prompt Templates
  - Risk Rules
```

Screen name changes:

- `소셜 뉴스` -> `소스 뉴스`
- `콘텐츠 관리` -> `콘텐츠 검수 큐`
- `Facebook 게시` -> `승인 콘텐츠 게시`
- `봇 상태` -> `자동화 상태`
- `뉴스 연동` -> `소스 수집`

## 8. Admin Screen Structure

### Dashboard

Shows:

- collected today
- generated today
- sent to Telegram
- waiting approval
- approved
- rejected
- published
- blocked by source risk
- blocked by content quality

### Source Registry

Shows:

- source name
- source domain
- method: API, RSS, crawler, manual
- access rule
- copyright/terms risk
- collection schedule
- enabled/disabled

### Content Review Queue

List columns:

- status
- category / subcategory
- title
- source
- source risk
- quality score
- Telegram sent at
- reviewer
- approval date
- generated date
- original link

Detail panel:

- original source text
- generated written content
- representative image
- translation status
- source/disclaimer block
- AI model/prompt trace
- Telegram message preview
- approve/reject/edit actions

### Community Signals

Shows:

- platform
- topic
- frequency
- urgency
- category mapping
- risk level
- official validation source
- whether content generation is allowed

## 9. Content Status Design

Required status path:

```text
COLLECTED
-> GENERATED
-> SENT_TO_TELEGRAM
-> APPROVED
-> PUBLISHED
```

Reject path:

```text
COLLECTED
-> GENERATED
-> SENT_TO_TELEGRAM
-> REJECTED
```

Status meanings:

| Status | Meaning | Public publish allowed |
| --- | --- | --- |
| COLLECTED | source data collected and normalized | No |
| GENERATED | AI draft created | No |
| SENT_TO_TELEGRAM | sent to reviewer | No |
| APPROVED | reviewer approved | Yes |
| REJECTED | reviewer rejected | No |
| PUBLISHED | published to Facebook/site | Already published |

Recommended auxiliary fields:

- `status_reason`
- `blocked_reason`
- `source_risk_level`
- `content_quality_status`
- `telegram_message_id`
- `reviewer_id`
- `approved_at`
- `published_at`

Do not use operational states such as `FAILED_LLM`, `FAILED_FACEBOOK`, or `CONTENT_INVALID` as the six public workflow states. Store them in `status_reason`, `blocked_reason`, or operation logs.

## 10. Telegram Review Flow

### Phase 1: Review-only automation

Automation allowed:

- collect source
- generate draft
- format review card
- send to Telegram

Automation forbidden:

- Facebook publish
- site publish
- auto-approval

### Telegram message format

```text
[WorkConnect Review]

Content ID: 123
Category: 생활정보 > 의료
Status: GENERATED
Risk: LOW
Source: National Health Insurance Service
Translation: EN from KO
Generated: 2026-06-14 10:30 KST

Title:
How foreign residents can check national insurance eligibility

Draft:
...

Why it matters:
...

Original:
https://...

Actions:
[Approve] [Reject] [Edit Needed]
```

### Approval rules

- `Approve`: status becomes `APPROVED`.
- `Reject`: status becomes `REJECTED` with reviewer reason.
- `Edit Needed`: status remains `GENERATED` or `SENT_TO_TELEGRAM`, and admin UI shows edit request.

### Reviewer trace

Track:

- Telegram user ID or internal reviewer ID
- reviewer display name
- action
- comment
- reviewed_at
- approval source

## 11. Facebook Publish Format

Default format is written content plus representative image.

PDF is not the default Facebook post asset.

### Facebook post structure

```text
{short title}

{2-4 sentence explanation}

Why this matters:
{practical relevance for foreign residents / job seekers}

What to check:
- {action 1}
- {action 2}
- {action 3}

Source:
{source name}
{original link}

Note:
Information can change. Check the official source before making visa, job, medical, financial, or legal decisions.

#WorkConnectKorea #WorkInKorea #{CategoryTag}
```

### Required publish checks

- status must be `APPROVED`
- source link exists
- source is not a search result, root URL, login-only page, or unresolved redirect
- generated message has no internal/admin text
- translation status is recorded
- original source is recorded
- generated date is recorded
- reviewer and approval date are recorded
- representative image exists or a safe default category image is used

## 12. PDF vs Written Content + Image

### Written Content + Image

Pros:

- better for Facebook feed readability
- faster to review in Telegram
- easier to edit before approval
- easier to track source and disclaimer
- lower production cost
- better for frequent daily posts

Cons:

- less suitable for long-form guides
- weaker premium value than a structured report

Recommended use:

- daily job/visa/living tips
- source-backed short explainers
- community question answers
- Facebook/site posts
- Telegram review cards

### PDF

Pros:

- good for structured, premium, evergreen content
- useful for weekly/monthly reports
- useful for visa guidebooks and job category guides
- can support paid subscription tiers

Cons:

- slower to generate and review
- harder to read inside Facebook feed
- more risk if legal/visa details become outdated
- requires stronger versioning and disclaimer controls

Recommended use:

- weekly report
- monthly settlement guide
- visa guidebook
- occupation guidebook
- premium subscriber downloads
- B2B/B2G reports

### Recommendation

Use Written Content + Representative Image as the default format.

Use PDF only for premium or periodic long-form content:

- weekly/monthly reports
- visa guidebooks
- occupation guidebooks
- expert-reviewed guides

## Implementation Phases

### Phase 1: Review-first MVP

- collect source data
- generate content
- send to Telegram
- record approval/rejection
- prohibit Facebook/site auto publish

### Phase 2: Approved publishing

- admin/Telegram approval creates `APPROVED`
- manual publish button publishes to Facebook/site
- publish logs and public URLs are stored

### Phase 3: Assisted automation

- safe categories can auto-send to Telegram
- repeat reviewer patterns can suggest approval
- still no public publishing without approval

### Phase 4: Conditional auto-publish

Only after stable review patterns:

- trusted official source
- low risk
- repeated approved format
- no legal/visa interpretation risk
- no community-origin direct claims
- configured category allowlist

Even in phase 4, community-origin content should normally remain approval-required.

## Notes On Protected Areas

This document is a design artifact only.

Do not change without explicit implementation approval:

- Facebook publisher behavior
- scheduler frequency
- Telegram webhook behavior
- bot ON/OFF state
- database migrations
- automatic publish rules
- source scraping of community platforms

