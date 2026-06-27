!wc-audit

PURPOSE FUNCTION:
WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.

AREA:
LIVING_DOMAIN + DATA_SOURCE_QUALITY + SOCIAL_NEWS_COLLECTOR + SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE

MODE:
READ_ONLY_AUDIT

FOCUS:
Research and audit how to expand the LIVING_INFO / LIVING_GUIDE source spectrum.

Current issue:
The system keeps collecting data, but useful living-information outputs are not appearing often enough.
We need to identify better source categories and candidate sources for practical foreigner settlement information in Korea.

This is research-only and read-only.
Do not modify code.
Do not run collectors.
Do not write DB data.
Do not create migrations.
Do not publish or send external notifications.

TIMEBOX:
90m to 120m

READ FIRST:

* CODEX_BOOTSTRAP.md or AGENTS.md if present
* DOC/architecture/00_PRODUCT_NORTH_STAR.md
* DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
* DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
* DOC/architecture/03_SYSTEM_ARCHITECTURE.md
* DOC/architecture/05_CODEX_HARNESS_GUIDE.md
* DOC/architecture/06_WORK_AREA_REGISTRY.md
* DOC/walkthrough/YYYY-MM-DD - execute prompt.md
* Recent reports related to LIVING_INFO card generation, attachment review, duplicate review/publish pipeline, and individual-request default review if present

BACKGROUND:
Recent guardrails changed the system so single news articles and attachment-only official notices should not immediately become public content.
That is correct for quality, but now LIVING_INFO needs a wider and better source base.

The desired future flow is:

```text
broad source discovery
-> raw/source evidence
-> normalized signal
-> category/topic_key/target_user/action_type tagging
-> fact/card point extraction later
-> topic-cluster based living guide/card candidate
-> Telegram review
-> manual approval
```

The goal of this audit is to find where practical living-information signals can come from.

RESEARCH TARGET:
Find source candidates for practical foreigner living/settlement information in Korea.

Include both international and domestic sources.

Research source types:

1. International / foreigner communities

* Reddit communities related to Korea, living in Korea, expats, students, workers, visas, housing, banking, phones, healthcare, insurance, transportation
* Quora or other Q&A communities if useful
* Facebook public pages/groups only if publicly accessible and legally usable
* YouTube channels/comments only as discovery signal, not authoritative fact
* TikTok public creator posts only as trend signal, not authoritative fact
* Blogs/forums used by foreign residents in Korea
* Country/language-specific communities:

  * English
  * Tagalog / Filipino
  * Vietnamese
  * Thai
  * Indonesian
  * Uzbek / Russian
  * Mongolian
  * Nepali
  * Cambodian
  * Chinese
  * Japanese
  * Arabic / African worker communities if discoverable

2. Korean domestic sources with foreigner-relevant living info

* Multicultural family support centers
* local government foreign resident pages
* immigration support centers
* labor counseling centers
* migrant worker support NGOs
* foreign worker welfare centers
* community centers
* local Facebook/Naver/Kakao communities if publicly visible
* Naver Cafe/Blog/Post if public and accessible
* Daum Cafe only if public and accessible
* Korean-language posts discussing foreign resident issues:

  * housing
  * employment/labor
  * wage disputes
  * health insurance
  * telecom
  * banking
  * transportation
  * childcare/school
  * marriage migrant life
  * regional support programs
  * legal aid
  * scams/fraud prevention
  * emergency/safety
  * language education

3. Official / semi-official living sources

* HiKorea practical stay information
* Ministry / local government foreign resident support pages
* Korea Support Center for Foreign Workers
* Danuri / multicultural family portal
* Seoul Global Center and regional global centers
* labor rights portals
* public health insurance guidance
* banks/telecom official foreigner guides
* housing/lease official guides
* legal aid/public counseling resources

4. Existing WorkConnect local sources

* Check current collector/source list if available
* Identify which living categories are under-covered
* Identify which sources collect data but fail content readiness
* Identify if the current source pool is too news-heavy

RESEARCH RULES:
Respect source ethics and legal boundaries.

Do not:

* scrape private, closed, login-only, paywalled, or access-controlled communities
* collect personal identifiers
* quote personal stories directly for public content
* treat community posts as factual authority
* use community content as legal/visa/medical/financial fact without official validation
* create runtime collectors
* run actual large scraping jobs

Allowed:

* public source discovery
* source inventory creation
* keyword strategy design
* API/robots/TOS feasibility notes
* risk classification
* recommendation of future collector candidates
* design of small manual/test-run queries
* propose future CODE_TASK_CANDIDATE items

IMPORTANT CLASSIFICATION PRINCIPLE:
Community sources are user-need signals, not authoritative sources.

They may support:

* recurring pain point detection
* topic demand discovery
* language/community-specific concerns
* practical question clustering
* content idea generation

They must not directly become public facts.

Public WorkConnect content still needs source-backed validation from:

* official sources
* trusted media
* practical secondary sources
* verified institutional guides

RESEARCH QUESTIONS:
Answer these in detail.

1. What living-information categories are currently too narrow or under-supplied?
   Consider:

* housing / rent / deposit / lease
* healthcare / insurance / hospitals
* banking / remittance / account opening
* telecom / SIM / phone contracts
* transportation / driver license / public transport
* public services / local offices
* labor rights / wage / contract / fake freelancer issues
* visa-adjacent daily life issues
* childcare / school / family support
* Korean language classes
* legal aid / counseling
* scam/fraud prevention
* emergency/safety
* regional support programs
* community integration
* daily life how-to

2. Which public international communities can reveal real foreigner pain points in Korea?

For each candidate source:

* source name
* URL or search keyword if known
* language
* target user type
* likely useful categories
* source type:

  * community signal
  * official source
  * trusted media
  * secondary support source
  * discovery source
* authority level
* access method:

  * official API
  * RSS
  * search result only
  * public page
  * manual review only
  * not recommended
* risks:

  * privacy
  * TOS
  * noisy/low quality
  * misinformation
  * hate/sensitive content
  * duplicate spam
  * language quality
* recommended use:

  * collect
  * monitor only
  * manual research only
  * do not use

3. Which Korean domestic sources contain foreigner-relevant living information?

For each:

* source name
* source owner/institution if known
* public accessibility
* likely categories
* whether it can validate community signals
* whether it can become source-backed content
* risks and limitations

4. What keywords should be used for source discovery and test runs?

Create keyword sets by language.

English examples:

* "foreigner in Korea rent deposit"
* "Korea foreign resident health insurance"
* "Korea ARC bank account"
* "Korea phone plan foreigner"
* "Korea labor contract foreign worker"
* "Korea wage unpaid foreign worker"
* "living in Korea foreigner problems"

Korean examples:

* "외국인 근로자 월세 보증금"
* "외국인 건강보험 가입"
* "외국인 통장 개설"
* "외국인 휴대폰 개통"
* "외국인 임금체불"
* "외국인 노동상담"
* "외국인 주민 지원센터"
* "다문화가족 지원"
* "외국인 전입신고"
* "외국인 운전면허"

Add other language keyword candidates if possible.

5. What should be the source-to-content policy?

Define how each source type should flow:

```text
official source
-> source-backed content candidate possible

trusted media
-> signal + explainable content possible with caution

secondary support source
-> practical guide candidate possible

community source
-> user-need signal only
-> requires official/secondary validation before content

social media trend
-> discovery signal only
-> never direct public fact
```

6. What should be the first safe test-run design?

Create a test-run plan without implementing it.

The test-run should answer:

* which sources to test first
* which keywords to use
* how many results to fetch manually or via safe query
* what fields to record
* how to classify topic demand
* how to avoid collecting personal info
* how to score actionability
* how to decide whether a topic becomes a future guide candidate

Suggested fields:

* source_name
* source_url
* source_type
* language
* country/community
* category
* topic_candidate
* target_user
* user_need_signal
* validation_source_needed
* trust_level
* privacy_risk
* actionability_score
* repeatability_score
* freshness
* recommendation

7. What new data fields may be needed later?

Consider:

* topic_key
* source_signal_type
* target_user
* action_type
* pain_point
* validation_needed
* validation_source_url
* fact_point
* usable_for_card
* community_signal_count
* source_spread_count
* language_group
* region_in_korea
* official_validation_status

Do not implement schema changes.
Just recommend.

8. What should not be collected or should be avoided?

Identify:

* private groups
* closed communities
* individual immigration/legal stories with PII
* hate/racist content unless for safety trend detection only
* legal/visa claims without validation
* medical claims without official validation
* financial advice/scam claims without validation
* copyrighted article text beyond metadata/summary
* direct quotes from users without policy

9. What is the recommended priority list?

Create a prioritized source expansion roadmap:

Phase 1:
Manual/read-only source discovery and keyword test list.

Phase 2:
Official/semi-official living support source inventory.

Phase 3:
Community signal monitoring design.

Phase 4:
Small test collector candidates, no public output.

Phase 5:
Topic cluster candidate generation.

Phase 6:
Source-backed living guide/card generation.

OUTPUT REPORT IN KOREAN.
Technical identifiers, source names, URLs, command names, file paths, table names, and code identifiers must remain in original form.

REPORT FORMAT:

# READ_ONLY_AUDIT REPORT: LIVING_INFO Source Spectrum Expansion Research

## 1. Pre-Review

* AREA:
* MODE:
* Risk:
* Protected areas touched:
* Files inspected:
* Research method:
* External research performed:
* Runtime/code changes: NO

## 2. Current Problem Definition

Explain why LIVING_INFO is collecting but not producing enough useful content.

## 3. Existing Source Coverage Summary

Summarize current known WorkConnect source coverage and what seems under-covered.

## 4. Living Information Category Map

Define the target category spectrum for LIVING_INFO / LIVING_GUIDE.

Include:

* category
* user problem
* likely source type
* whether community signal is useful
* whether official validation is required
* content/card potential

## 5. International / Foreigner Community Source Candidates

List candidate sources.
For each source:

* name
* URL/search query if available
* language
* target user
* category coverage
* source type
* access method
* risks
* recommended use
* priority

## 6. Korean Domestic Source Candidates

List candidate sources.
For each:

* name
* institution/type
* URL/search query if available
* category coverage
* validation value
* access method
* risks
* recommended use
* priority

## 7. Keyword Strategy

Create keyword sets by language and category.

Include at least:

* English
* Korean
* Tagalog/Filipino if possible
* Vietnamese if possible
* Thai/Indonesian/Nepali/Uzbek/Russian/Mongolian if possible

## 8. Community Signal Policy

Define how Reddit, foreigner forums, Facebook public pages, YouTube/TikTok, blogs, and domestic communities should be used safely.

Include:

* allowed use
* forbidden use
* validation requirement
* privacy/PII rule
* quote/publication rule

## 9. Source-to-Content Promotion Rules

Define when a source can become:

* source_signal only
* evidence only
* review candidate
* topic cluster candidate
* source-backed guide/card candidate
* public content

## 10. Safe Test-Run Plan

Design a test run but do not execute it.

Include:

* source set
* keyword set
* result limit
* fields to record
* scoring rules
* expected output
* stop conditions
* verification plan

## 11. Data Model Gaps

List future fields/tables needed for source-signal and topic-cluster generation.
Do not propose immediate migration unless clearly necessary.

## 12. Risk Analysis

Include:

* privacy risk
* TOS/API risk
* misinformation risk
* over-collection risk
* duplicate/noise risk
* classification risk
* public content trust risk

## 13. Recommended Roadmap

Give phased next steps:

* READ_ONLY_AUDIT tasks
* DOC_ONLY policy tasks
* GUARDED_FIX candidates
* future collector candidates

## 14. CODE_TASK_CANDIDATE

Suggest next tasks in Codex format.

At minimum include:

1. LIVING_INFO source inventory documentation
2. Community signal policy doc
3. Safe test-run query design
4. Official/semi-official living source collector audit
5. topic_key / source_signal schema read-only design
6. small manual import/test-run prototype if later approved

## 15. Stop Conditions Encountered

Record anything that requires user approval before implementation.

## 16. Final Recommendation

State the safest next action to expand LIVING_INFO source spectrum without weakening WorkConnect quality.

## Execution Result - 2026-06-27

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY + SOCIAL_NEWS_COLLECTOR + SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE`
- MODE: `READ_ONLY_AUDIT`
- Result: COMPLETED
- Report:
  - `DOC/walkthrough/execution-history/2026-06-27/living-info-source-spectrum-expansion-research-report.md`
- Runtime/code changes: NO
- DB/migration changes: NO
- Collector execution: NO
- External notification/publish: NO
- Protected areas touched: NO
- Main finding:
  - `LIVING_INFO / LIVING_GUIDE` needs a broader source spectrum, but community/blog/forum/social sources must remain `source_signal` only.
  - Official and semi-official sources such as HiKorea, Danuri, Seoul Global Center, NHIS, NPS, MOEL/EPS, legal aid, local government foreign resident pages, and support centers should validate practical guide/card candidates.
  - Current code can classify social/news candidates into `LIVING_INFO`, but card generation correctly blocks single-news public cards without topic/fact evidence.
  - Next safe action is `DOC_ONLY` source policy and a small manual/read-only source discovery test before any collector or schema change.

[WC_EXECUTION_COMPLETE]
