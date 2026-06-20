# Content Dedupe Policy Audit

Report date: 2026-06-16 KST
Last updated: 2026-06-16 KST after Telegram Review dedupe guarded fix.

Current implementation note:

- `DOC/walkthrough/2026-06-16-telegram-review-dedupe.md` records a later guarded fix for Python Telegram Review dedupe.
- Current Python Telegram Review delivery now builds `telegram_review_key` and `semantic_review_key` before sending.
- Those keys are stored in `content.publish_log.request_payload` JSON for new review logs.
- This suppresses repeated Telegram Review delivery for equivalent review messages, but the keys are not first-class indexed columns on `content.content_candidate`.
- The first low-value `LIVING_INFO` review candidate can still enter the review target list when it has not been reviewed before.

## Harness Scope

AREA:

- CONTENT_QUEUE
- SOCIAL_NEWS_CANDIDATE
- DATA_SOURCE_QUALITY

MODE:

- READ_ONLY_AUDIT

FOCUS:

- Analyze repeated duplicate content in Content Review and Telegram Content Review.
- Separate duplicate policy for news-style content from notice, living, immigration, occupation, and job information.

Decision:

- PROCEED_WITH_LIMITS

Limits:

- No runtime code change.
- No DB change.
- No migration execution.
- No Telegram notifier change.
- No Facebook publisher change.
- No scheduler or bot state change.
- No content publisher selection change.
- No raw token or environment change.

Note:

- `DATA_SOURCE_QUALITY` is used by the task as a focus area. It is not an explicit area name in `DOC/architecture/06_WORK_AREA_REGISTRY.md`; this audit treats it as a read-only cross-cutting focus covered by `SOCIAL_NEWS_CANDIDATE`, `CONTENT_QUEUE`, and `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`.
- `DOC/database/11_TO_BE_CONTENT_FLOW.md` was not present. This audit used `DOC/database/TO_BE_DB_ARCHITECTURE.md`, which contains the To-Be Content Flow section.

## Files Inspected

- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
- `DOC/architecture/06_WORK_AREA_REGISTRY.md`
- `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
- `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
- `DOC/database/03_CONTENT_CURRENT.md`
- `DOC/database/TO_BE_DB_ARCHITECTURE.md`
- `DOC/flowchart/flowchart-flow-audit.md`
- `DOC/walkthrough/2026-06-16 - execute prompt.md`
- `DOC/walkthrough/2026-06-16-telegram-review-dedupe.md`
- `SRC/foreign_worker_life_info_collector/content/repository.py`
- `SRC/foreign_worker_life_info_collector/content/service.py`
- `SRC/foreign_worker_life_info_collector/api/admin_server.py`
- `SRC/foreign_worker_life_info_collector/social/news/pipeline.py`
- `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py`
- `SRC/foreign_worker_life_info_collector/social/news/duplicate_guard/duplicate_detector.py`
- `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_07_content_candidate.sql`
- `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_06_immigration_info.sql`
- `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_03_occupation_info.sql`
- `SRC/foreign_worker_life_info_collector/storage/db/migrations/admin_postgres_schema.sql`
- `SRC/ForeignWorkerJobInfoService/src/main/resources/db/migration/2026_06_14_content_approval_workflow.sql`
- `SRC/ForeignWorkerJobInfoService/src/main/java/fwj/aniss/api/content/collector/CollectionRunService.java`
- `SRC/ForeignWorkerJobInfoService/src/main/java/fwj/aniss/api/content/repository/SourceItemRepository.java`
- `SRC/ForeignWorkerJobInfoService/src/main/java/fwj/aniss/api/content/repository/GeneratedContentRepository.java`
- `SRC/ForeignWorkerJobInfoService/src/main/java/fwj/aniss/api/content/repository/ReviewLogRepository.java`
- `SRC/ForeignWorkerJobInfoService/src/main/java/fwj/aniss/api/content/service/ContentApprovalWorkflowService.java`
- `SRC/ForeignWorkerJobInfoService/src/main/java/fwj/aniss/api/content/telegram/TelegramReviewMessageBuilder.java`
- `SRC/ForeignWorkerJobInfoService/src/main/java/fwj/aniss/api/content/telegram/TelegramReviewSender.java`
- `SRC/ForeignWorkerJobInfoService/src/main/java/fwj/aniss/api/content/telegram/TelegramReviewUpdateService.java`
- `SRC/ForeignWorkerJobInfoService/src/main/java/fwj/aniss/api/content/controller/TelegramReviewCallbackController.java`

## Current Duplicate Generation And Notification Flow

### Python content queue path

Current source-to-content sync uses `content.content_candidate` as the unified candidate table.

Observed flow:

```text
social_news.candidate
-> ContentService.sync_social_news()
-> content.content_candidate
-> ContentRepository.list_review_targets()
-> send_content_review_to_telegram()
-> content.publish_log(channel = 'telegram_review')
```

Immigration notices flow similarly:

```text
immigration_info.official_notice
-> ContentService.sync_immigration()
-> content.content_candidate
-> ContentRepository.list_review_targets()
-> send_content_review_to_telegram()
-> content.publish_log(channel = 'telegram_review')
```

Important current constraints:

- `content.content_candidate` uniqueness is `UNIQUE(raw_ref_table, raw_ref_id)`.
- This prevents duplicate content candidates for the same source row.
- It does not prevent duplicate content candidates when the source system creates different raw ids for the same URL, same title, or same semantic content.
- `ContentRepository.list_review_targets()` currently filters review targets to `source_domain IN ('LIVING_INFO', 'IMMIGRATION_INFO')`.
- Review target selection still excludes only the same `content_candidate_id` with `channel = 'telegram_review'`, status `SENT` or `DRY_RUN`, within 6 hours.
- Pre-send Telegram Review dedupe now runs in `send_content_review_to_telegram()` before the Telegram API call.
- `ContentService.telegram_review_metadata()` builds:
  - `telegram_review_key = content_candidate_id | status | score_bucket | message_hash`
  - `semantic_review_key = source_domain | content_type | canonical_url_or_title | status | score_bucket | message_hash`
- `ContentRepository.find_duplicate_telegram_review()` checks `content.publish_log.request_payload` JSON for either key and also keeps a 6-hour `content_candidate_id + message_preview` fallback for older logs.
- Suppressed sends are recorded as `REVIEW_SUPPRESSED_DUPLICATE` or `REVIEW_SUPPRESSED_LOW_VALUE`.
- There is no content-level `seen_count`, `last_seen_at`, `candidate_key`, `canonical_url`, or `content_hash` on `content.content_candidate`.
- There is no first-class indexed `telegram_review_key`, `semantic_review_key`, `review_sent_at`, or `last_suppressed_at` column on `content.content_candidate`.
- Social news duplicate fields are copied only partly into `raw_payload` (`duplicate_group_id`, `representative_candidate_id`, `is_representative`), not promoted to first-class review selection fields.
- `list_review_targets()` has no minimum score, generic category blocklist, or practical-use quality gate for first-time `LIVING_INFO` review candidates.

Result:

- The same `content_candidate.id` is protected from review spam for 6 hours at query time.
- Equivalent review messages can now be suppressed before Telegram delivery if they match the stored review key metadata.
- A first-time low-value `LIVING_INFO` candidate can still be sent once if it passes the review target query.
- A semantically identical candidate created before the dedupe metadata existed may still rely on fallback matching rather than durable indexed keys.

### Social news candidate path

The social news layer already has duplicate machinery before content sync.

Observed fields and behavior:

- `social_news.raw_item.source_hash`
- `social_news.normalized_item.hash_key`
- `social_news.normalized_item.similarity_key`
- `social_news.candidate.duplicate_group_id`
- `social_news.candidate.related_source_count`
- `social_news.candidate.duplicate_count`
- `social_news.candidate.group_item_count`
- `social_news.candidate.last_seen_at`
- `social_news.candidate.is_representative`

Observed behavior:

- `social_news.normalized_item` upserts on `hash_key`.
- Existing representative candidates are updated with group counts and `last_seen_at`.
- Duplicate detector checks same source URL, same hash key, high title similarity, title/body similarity, and same-day keyword event similarity.
- `ContentService.sync_social_news()` imports only rows where `COALESCE(is_representative, TRUE) = TRUE` and skips duplicate/skipped/archived statuses.
- `archive_non_representative_social_news()` archives content candidates linked to non-representative or duplicate social news rows.

Gap:

- The news layer preserves duplicate signal, but `content.content_candidate` does not yet have first-class fields such as `source_spread_count`, `duplicate_signal`, or `topic_key`.
- Telegram Review dedupe keys now exist in `content.publish_log.request_payload`, but not as indexed candidate fields.
- News/living split currently happens by category in `social_news_payload()`, so living-like rows sourced from news/blog feeds can still enter `LIVING_INFO` review when they pass the current status/domain query.
- Categories currently treated as living include practical categories such as `housing`, `banking`, `healthcare`, and `education`, but also broader categories such as `travel`, `lifestyle`, `culture`, `local_events`, and `safety`.

### Java approval workflow path

The Java MVP has a newer source/generation/review structure:

```text
content.source_item
-> content.generated_content
-> content.review_log
```

Observed constraints:

- `content.source_item` has `canonical_url`, `source_url`, `publishable_link_url`, and `last_seen_at`.
- `content.source_item` has a unique expression index:

```text
source_domain + md5(canonical_url or source_url)
```

- `CollectionRunService.collect()` checks existing source item by domain and URL hash; if found, it updates `last_seen_at` instead of inserting a new source row.
- `content.generated_content` has a unique partial index on `source_item_id`.
- `content.review_log` records `generated_content_id`, `review_channel`, `telegram_message_id`, and action.
- Telegram callback data is `CALLBACK_PREFIX:ACTION:contentId`.

Gap:

- This Java path suppresses same-domain same-URL source duplicates better than the Python content candidate path.
- It still lacks first-class fields for `content_hash`, `title_hash`, `topic_key`, `candidate_key`, `telegram_review_key`, `review_sent_at`, `last_review_sent_at`, and `review_suppressed_reason`.
- It does not define separate domain-level duplicate policies for news, official notice, living guide, occupation info, and job info.

## Duplicate Type Definitions

### 1. exact duplicate

Definition:

- Same `source_domain`.
- Same `canonical_url` or same normalized `source_url`.
- Same normalized `source_name`.
- Same normalized title.
- Same content hash or unchanged source body.

Meaning:

- It is the same source item, not a new content opportunity.
- It should not create a new review candidate.
- It should not create a new Telegram review.

Action:

- Update `seen_count` and `last_seen_at`.
- Keep first candidate as representative.
- Keep raw/source-level occurrence if needed for audit.

### 2. silent duplicate

Definition:

- Same candidate key already exists.
- No meaningful change in status, score, title, body, URL, source updated timestamp, or content hash.

Meaning:

- It is operational noise.
- The system has learned nothing new.

Action:

- Do not create a new content candidate.
- Do not resend Telegram review.
- Update `seen_count`, `last_seen_at`, and optionally `last_suppressed_at`.

### 3. duplicate signal

Definition:

- Same or very similar topic.
- Different `source_name` or different canonical URL.
- Different source trust path or publisher.

Meaning:

- This can indicate topic spread, importance, or user demand.
- It is not automatically a separate content candidate.

Action:

- Preserve as source spread signal.
- Attach to representative content candidate as `source_spread_count`, `related_source_count`, or `duplicate_signal`.
- Only representative candidate should proceed to content review or publishing.
- Do not resend duplicate Telegram review unless the representative candidate meaningfully changes.

### 4. update duplicate

Definition:

- Same canonical URL or same official/job/occupation id.
- Title, body, source updated timestamp, deadline, status, employer, or content hash changed.

Meaning:

- The item is the same object, but the source has changed.

Action:

- Update the existing source/candidate row.
- Mark `review_required_updated` or equivalent if the change affects user guidance, risk, deadline, legal meaning, employer/job availability, or publication status.
- Resend Telegram review only when the update is meaningful for the operator.

## Domain-Specific Duplicate Policy

| Domain | Duplicate key | Silent suppress | Duplicate signal | Update duplicate |
| --- | --- | --- | --- | --- |
| NEWS_ARTICLE | canonical URL, source URL, hash key, title/content similarity | Same URL/hash/title from same source should not create another review or publish candidate. | Same topic from different credible outlets should increase source spread and representative score. | Same canonical URL with changed title/body can refresh the representative candidate. |
| IMMIGRATION_NOTICE / GOVERNMENT_NOTICE | official notice id when available, canonical URL, source name, title hash, content hash | Same official notice URL/title from the same agency should be suppressed. | Same topic from different official agencies is a signal and should be attached to the representative official content candidate. | Changed body, notice date, attachment, visa type, deadline, or legal meaning should require updated review. |
| LIVING_GUIDE | canonical URL, source URL, source name, normalized title, content hash | Same URL duplicate should be suppressed. | Same practical topic from multiple trusted sources should improve confidence. | Changed guide body, eligibility, phone/address, fee, checklist, or official link should require updated review. |
| OCCUPATION_INFO | source + occupation_code | Same occupation code should update only. | Related occupations can become enrichment context, not duplicate Telegram reviews. | Changed title, description, job family, keyword mapping, or enrichment readiness updates the row. |
| EMPLOYMENT_JOB | source_job_id, source + job id, canonical URL | Same job id/URL should update only. | Similar jobs from different employers are not exact duplicates; they may be market signal. | Deadline, employer, status, salary, location, visa/eligibility, or posting availability changes can notify. |

## Recommended Domain Decisions

### NEWS_ARTICLE

- Keep some duplicate source rows for audit and topic spread.
- Promote only one representative candidate per duplicate/topic group.
- Do not send Telegram duplicate review for news.
- News can continue its own publication path if the current product policy allows direct news posting.
- Different sources on the same topic should increase `source_spread_count`, not multiply content candidates.

### IMMIGRATION_NOTICE / GOVERNMENT_NOTICE

- Same URL or same official notice exact duplicate should be silent-suppressed.
- Same topic across official agencies should be duplicate signal.
- Telegram review should resend only on meaningful update.
- Legal/visa-sensitive changes should default to updated review, not automatic publish.

### LIVING_GUIDE

- Same URL duplicate should be suppressed.
- Generic travel, crypto, stock, lifestyle, and low-settlement relevance should be excluded from Telegram review candidates.
- Same practical topic from trusted sources should become signal.
- Blog/community items should not be treated as authoritative guide content unless supported by a trusted or official source.

### OCCUPATION_INFO

- Same `occupation_code` should update existing occupation data only.
- Before enrichment, it should not become publish candidate.
- Duplicate Telegram review should be forbidden.
- Enrichment status can decide when it becomes a future content guide.

### EMPLOYMENT_JOB

- Same `source_job_id` or canonical URL should update only.
- Deadline, employer, job status, availability, salary, location, or work eligibility changes are meaningful updates.
- Non-meaningful re-collection should only touch `last_seen_at`.

## Current Code/DB Missing Fields

Note:

- `telegram_review_key` and `semantic_review_key` now exist as JSON metadata in new `content.publish_log` rows for the Python Telegram Review path.
- In the lists below, "missing" means missing as a first-class candidate/generated-content column or indexed lookup field.

### Missing or not first-class in `content.content_candidate`

- `canonical_url`
- `publishable_link_url`
- `content_hash`
- `title_hash`
- `topic_key`
- `similarity_key`
- `candidate_key`
- `duplicate_type`
- `duplicate_group_id` as a direct column
- `representative_candidate_id` as a direct column
- `source_spread_count`
- `related_source_count`
- `seen_count`
- `first_seen_at`
- `last_seen_at`
- `last_meaningful_update_at`
- `meaningful_update_yn`
- `review_sent_at`
- `last_review_sent_at`
- `telegram_review_key`
- `review_suppressed_reason`
- `review_policy_version`

### Missing or incomplete in `content.generated_content`

- `content_hash`
- `title_hash`
- `candidate_key`
- `telegram_review_key`
- `review_sent_at`
- `last_review_sent_at`
- `review_suppressed_reason`
- `meaningful_update_yn`
- `source_spread_count`
- `duplicate_signal_json`

### Existing fields that partially help

- Python content: `raw_ref_table`, `raw_ref_id`, `source_url`, `link_url`, `raw_payload`.
- Python Telegram Review log metadata: `telegram_review_key`, `semantic_review_key`, `score_bucket`, `message_hash`, `review_identity_url`, and `duplicate_signal_bucket` in `content.publish_log.request_payload` JSON for new logs.
- Social news: `hash_key`, `similarity_key`, `duplicate_group_id`, `duplicate_count`, `related_source_count`, `last_seen_at`, `is_representative`.
- Immigration current table: `canonical_url UNIQUE`, `duplicate_group_id`.
- Occupation current table: `UNIQUE(source, occupation_code)` and `UNIQUE(source, job_code)`.
- Java source item: `canonical_url`, `publishable_link_url`, `last_seen_at`, unique domain URL hash.
- Java generated content: unique `source_item_id`, `telegram_message_id`.
- Review logs: per-candidate review history.

## Candidate Key Proposal

### source_exact_key

Purpose:

- Block exact source duplicates.

Suggested input:

```text
source_domain
content_type or source type
normalized source_name
canonical_url or source_url
normalized title
content_hash when body exists
```

Suggested hash:

```text
sha256(source_domain | content_type | source_name_norm | canonical_url_norm | title_norm | content_hash)
```

### source_url_key

Purpose:

- Suppress same-URL repeats even when title/body are missing or unstable.

Suggested input:

```text
source_domain
canonical_url or source_url
```

Suggested hash:

```text
sha256(source_domain | canonical_url_norm)
```

### topic_signal_key

Purpose:

- Preserve duplicate signal across different sources.

Suggested input:

```text
source_domain
content_type
topic_key or similarity_key
date bucket for news only
target country
category
```

Suggested hash:

```text
sha256(source_domain | content_type | topic_key | date_bucket | country | category)
```

News should use a short date bucket because news topics decay quickly.

Official notice, living guide, occupation, and job information should avoid short date buckets unless the source object itself is time-bound.

### candidate_key

Purpose:

- Decide whether a source item should create a content candidate or update an existing representative.

Suggested policy:

- NEWS_ARTICLE: representative `topic_signal_key`, with exact duplicate children suppressed.
- IMMIGRATION_NOTICE / GOVERNMENT_NOTICE: `source_url_key`, falling back to official notice id/title hash.
- LIVING_GUIDE: `source_url_key`, falling back to trusted source + normalized title.
- OCCUPATION_INFO: `source + occupation_code`.
- EMPLOYMENT_JOB: `source_job_id` or source + canonical URL.

### telegram_review_key

Current implemented Python key:

```text
telegram_review_key =
content_candidate_id + status + score_bucket + message_hash

semantic_review_key =
source_domain + content_type + canonical_url_or_title + status + score_bucket + message_hash
```

Current storage:

```text
content.publish_log.request_payload JSON
```

Future first-class key proposal:

Purpose:

- Prevent repeated Telegram review for equivalent content across candidate ids.

Suggested input:

```text
review_policy_version
source_domain
content_type
candidate_key
content_hash or update_version
review_reason class
```

Suggested hash:

```text
sha256(review_policy_version | source_domain | content_type | candidate_key | content_hash_or_update_version | review_reason_class)
```

Review resend rule:

- Same `telegram_review_key`: suppress.
- Same candidate key but changed content hash/update version: allow review only if meaningful update policy says yes.
- Duplicate signal only: suppress Telegram review and update representative signal fields.

## Suppressible Telegram Repeat Cases

The following repeated cases should be suppressible by policy:

- Same official labor notice id, same link, same title sent in morning and afternoon with no content change.
- Same official immigration or justice notice URL collected again with unchanged title/body.
- Same Travel And Tour World link appearing under multiple content ids.
- Same living guide/blog URL re-collected with unchanged title/body/score.
- Same source URL in `LIVING_INFO` imported from social news because category mapping changed but link did not.
- Same occupation code re-collected without enrichment changes.
- Same job posting id or canonical URL re-collected without deadline/status/employer changes.

## Low-Score Review Exclusion Criteria

Current cause of low-score or generic `LIVING_INFO` review candidates:

- `social_news_payload()` can map news/blog/feed rows into `LIVING_INFO` when the category looks living-related.
- `is_living_content()` currently includes both practical settlement categories and broad categories such as `travel`, `lifestyle`, `culture`, `local_events`, and `safety`.
- `ContentRepository.list_review_targets()` selects `LIVING_INFO` and `IMMIGRATION_INFO` candidates by status, but does not apply a score floor, category exclusion, source trust rule, or actionability rule.
- Telegram Review dedupe now suppresses repeated equivalent alerts, but does not block the first alert for a low-value candidate.

Recommended exclusion before Telegram Review selection:

- Exclude `LIVING_INFO` from Telegram Review when `final_publish_score < 40` and no legal, safety, housing, healthcare, finance, immigration, or official-source review reason exists.
- Exclude generic categories unless they are clearly practical for foreign residents: `travel`, `tourism`, `lifestyle`, `culture`, `local_events`, `entertainment`, `crypto`, `stock_market`, and generic market/news trend.
- Exclude rows with missing or unusable `link_url`/`source_url`.
- Exclude rows whose summary/body is missing, fallback text, parser error text, or source diagnostic text.
- Exclude travel aggregators, generic lifestyle feeds, and market/crypto sources unless explicitly whitelisted as practical settlement sources.
- Keep `IMMIGRATION_INFO` official notices reviewable even at lower scores when the source is official and the item affects visa, stay, work permission, enforcement, deadline, institution, or required action.
- Keep low-ish `LIVING_INFO` reviewable only when it is highly actionable: address/location, public service, application path, fee, deadline, phone, eligibility, healthcare, housing, banking, telecom, education, or safety.

Suggested statuses or log reasons:

- `REVIEW_SUPPRESSED_LOW_VALUE`
- `LOW_RELEVANCE`
- `DUPLICATE_SILENT`
- `DUPLICATE_SIGNAL_UPDATED`

Policy distinction:

- Repeat suppression belongs in Telegram Review dedupe.
- First-time low-value prevention belongs in the content review target quality gate.

## Risk Summary

Main current risk:

- Repeat Telegram Review is now suppressed at send time by review keys, but low-value first-time `LIVING_INFO` candidates can still enter the review target list.

Secondary risk:

- Semantic review keys are stored in `content.publish_log.request_payload` JSON, not first-class indexed candidate fields.
- News-like rows can be reclassified into living categories and enter Telegram Review unless living guide policy checks source quality and practical relevance before target selection.

Design risk:

- A single duplicate policy for all content types will either over-suppress useful news spread or under-suppress official/living repeat noise.

Protected implementation risk:

- Any change to scheduler, Telegram notifier, Facebook publisher, auto publish selection, or DB migration must be handled as a separate approved task.

## CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: CONTENT_QUEUE / SOCIAL_NEWS_CANDIDATE
MODE: READ_ONLY_AUDIT
FOCUS: Quantify recent duplicate content candidates by source URL, canonical URL, title, raw_ref_table/raw_ref_id, and Telegram review logs.
WHY: Current audit found the likely duplicate path, but row-level counts are needed before changing policy or schema.
RISK: LOW-MEDIUM
PROTECTED AREA: NO, if read-only DB queries only.
FILES LIKELY INVOLVED: `DOC/walkthrough/`, read-only SQL/query snippets, `SRC/foreign_worker_life_info_collector/content/repository.py`, `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py`
RECOMMENDED NEXT PROMPT: AREA: CONTENT_QUEUE / SOCIAL_NEWS_CANDIDATE / MODE: READ_ONLY_AUDIT / FOCUS: Run read-only SQL samples that group recent content candidates by normalized URL/title/source and compare them to telegram_review logs.

## CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: CONTENT_QUEUE
MODE: GUARDED_FIX
FOCUS: Add non-destructive duplicate tracking fields for candidate key, content hash, seen count, last seen time, review sent time, and Telegram review key.
WHY: Current Telegram Review keys are stored in publish log JSON, but candidate-level indexing and lifecycle fields are still missing for durable dedupe, reporting, and review target selection.
RISK: MEDIUM-HIGH
PROTECTED AREA: YES - DB migration approval required before schema change.
FILES LIKELY INVOLVED: `SRC/foreign_worker_life_info_collector/storage/db/migrations/`, `SRC/foreign_worker_life_info_collector/content/repository.py`, `SRC/foreign_worker_life_info_collector/content/service.py`, `SRC/ForeignWorkerJobInfoService/src/main/resources/db/migration/`
RECOMMENDED NEXT PROMPT: AREA: CONTENT_QUEUE / MODE: GUARDED_FIX / FOCUS: Implement a non-destructive migration and repository mapping for content duplicate metadata. Do not change publisher, scheduler, or Telegram sender behavior.

## CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: CONTENT_QUEUE / LIVING_DOMAIN
MODE: GUARDED_FIX
FOCUS: Add a low-score and generic-category quality gate before `LIVING_INFO` Telegram Review target selection.
WHY: Telegram Review dedupe suppresses repeated alerts, but first-time generic travel/lifestyle/market rows can still enter review because `list_review_targets()` has no score/category/actionability gate.
RISK: MEDIUM
PROTECTED AREA: NO, if limited to review target eligibility and does not change Facebook publisher, scheduler, callback actions, or content publish selection.
FILES LIKELY INVOLVED: `SRC/foreign_worker_life_info_collector/content/repository.py`, `SRC/foreign_worker_life_info_collector/content/service.py`, `SRC/foreign_worker_life_info_collector/api/admin_server.py`, `SRC/foreign_worker_life_info_collector/tests/`
RECOMMENDED NEXT PROMPT: AREA: CONTENT_QUEUE / LIVING_DOMAIN / MODE: GUARDED_FIX / FOCUS: Exclude low-score and generic living/news/blog candidates from Telegram Review target selection while preserving official immigration and actionable living items. Do not modify Facebook publisher or scheduler.

## CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: SOCIAL_NEWS_CANDIDATE
MODE: GUARDED_FIX
FOCUS: Promote representative duplicate signal into content sync fields such as source spread count and duplicate signal summary.
WHY: News duplicates from different sources are useful as topic-spread signal, but should not create multiple content/review candidates.
RISK: MEDIUM
PROTECTED AREA: NO, if limited to candidate normalization and content sync metadata.
FILES LIKELY INVOLVED: `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py`, `SRC/foreign_worker_life_info_collector/content/service.py`, `SRC/foreign_worker_life_info_collector/content/repository.py`
RECOMMENDED NEXT PROMPT: AREA: SOCIAL_NEWS_CANDIDATE / MODE: GUARDED_FIX / FOCUS: Export social news source spread metadata to content candidates without changing Facebook publisher or scheduler behavior.

## CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: CONTENT_QUEUE / LIVING_DOMAIN / IMMIGRATION_DOMAIN
MODE: READ_ONLY_AUDIT
FOCUS: Sample living and immigration review candidates and classify exact duplicates, low-relevance generic lifestyle/news, and official update duplicates.
WHY: Living and immigration should be reviewed, but generic news/travel/lifestyle rows should not flood Telegram.
RISK: LOW-MEDIUM
PROTECTED AREA: NO, if read-only.
FILES LIKELY INVOLVED: `DOC/walkthrough/`, `SRC/foreign_worker_life_info_collector/content/service.py`, `SRC/foreign_worker_life_info_collector/api/admin_server.py`, relevant read-only SQL
RECOMMENDED NEXT PROMPT: AREA: CONTENT_QUEUE / LIVING_DOMAIN / IMMIGRATION_DOMAIN / MODE: READ_ONLY_AUDIT / FOCUS: Classify recent Telegram review candidates into official notice, practical living guide, generic news, blog/community signal, and duplicate suppress buckets.

## CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: CONTENT_QUEUE
MODE: GUARDED_FIX
FOCUS: Add domain-specific duplicate policy selection before candidate creation or review delivery.
WHY: NEWS_ARTICLE, official notices, living guides, occupation info, and job postings need different duplicate behavior.
RISK: MEDIUM-HIGH
PROTECTED AREA: YES - may require DB migration and review flow behavior change.
FILES LIKELY INVOLVED: `SRC/foreign_worker_life_info_collector/content/service.py`, `SRC/foreign_worker_life_info_collector/content/repository.py`, `SRC/ForeignWorkerJobInfoService/src/main/java/fwj/aniss/api/content/collector/CollectionRunService.java`, `SRC/ForeignWorkerJobInfoService/src/main/java/fwj/aniss/api/content/service/ContentApprovalWorkflowService.java`
RECOMMENDED NEXT PROMPT: AREA: CONTENT_QUEUE / MODE: GUARDED_FIX / FOCUS: Add domain-specific duplicate policy for content candidate creation and Telegram review suppression. Keep Facebook publishing and scheduler unchanged.

## CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: DASHBOARD_STATUS / CONTENT_QUEUE
MODE: LOW_RISK_FIX
FOCUS: Show duplicate status, representative candidate, source spread count, and review suppression reason in Admin UI after backend fields exist.
WHY: Operators need to know whether an item was blocked as noise or absorbed as useful duplicate signal.
RISK: LOW-MEDIUM
PROTECTED AREA: NO, if display-only and after backend fields are available.
FILES LIKELY INVOLVED: `SRC/foreign_worker_life_info_collector/admin_ui/src/views/ContentManagementPage.vue`, `SRC/foreign_worker_life_info_collector/admin_ui/src/views/LifestyleInfoPage.vue`, `SRC/foreign_worker_life_info_collector/admin_ui/src/views/ImmigrationNoticePage.vue`, `SRC/foreign_worker_life_info_collector/admin_ui/src/components/`
RECOMMENDED NEXT PROMPT: AREA: DASHBOARD_STATUS / CONTENT_QUEUE / MODE: LOW_RISK_FIX / FOCUS: Display duplicate policy fields and review suppression reasons in candidate lists without changing backend selection logic.

## Validation

Performed:

- Required architecture/database/flow documents reviewed.
- Current duplicate and review flow inspected in code and migrations.
- `git status --short` checked before writing this walkthrough.
- No runtime code, DB, migration, Telegram notifier, Facebook publisher, scheduler, or token/env file was intentionally modified by this audit.

Known working tree note:

- The repository already contained modified and untracked runtime files before this report was written.
- This audit only adds this walkthrough file.

Commit/push:

- Not performed, because the working tree contains pre-existing runtime changes outside this read-only audit.
