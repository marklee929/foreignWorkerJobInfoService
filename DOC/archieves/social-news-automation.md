# Social News Automation Architecture

## Purpose

This document defines the fully automated news publishing flow for WorkConnect Facebook Page.

The previous flow required Telegram approval from the user. That approval step is removed.

The new flow is:

```text
Search Naver for foreigner work news in English/Korean
→ Collect candidate news
→ Summarize and evaluate candidates
→ Check duplicates using DB and optional local LLaMA
→ Select best candidate automatically
→ Publish to Facebook automatically
→ Send publish result to Telegram for user check only
→ Save all candidate/publish data to DB
→ Continue next cycle
```

## Core Principle

Telegram is no longer an approval interface.

Telegram is only an operation notification channel.

```text
Old:
Candidate → Telegram approve/reject/keep → Publish

New:
Candidate → Auto select → Auto publish → Telegram result notification
```

## Module Location

All news automation modules must live under:

```text
SRC/foreign_worker_life_info_collector/social/news/
```

Expected structure:

```text
social/news/
  pipeline.py
  models.py
  collector/
    naver_news_collector.py
  normalizer/
    news_normalizer.py
  summarizer/
    news_summarizer.py
  evaluator/
    candidate_evaluator.py
  duplicate_guard/
    duplicate_detector.py
    llama_duplicate_checker.py
  publisher/
    facebook_publisher.py
  notifier/
    telegram_notifier.py
  repository/
    news_repository.py
```

Shared channel clients may live under:

```text
social/facebook/
social/telegram/
```

The `crew_team` layer should orchestrate the workflow but should not contain low-level crawler, DB, Facebook, or Telegram implementation details.

## Pipeline Steps

### 1. Search and Collect

Collect news from Naver search first.

Initial keyword examples:

```text
foreigner work Korea
foreign worker Korea
Korea visa foreign worker
E9 visa Korea
E7 visa Korea
immigration Korea worker
foreign worker employment Korea
외국인 근로자 취업
외국인 노동자 비자
외국인 고용 한국
```

Collector output must include:

- source_type
- source_url
- original_url if available
- title
- description/summary
- published_at if available
- collected_at
- keyword
- language

### 2. Normalize

Normalize all candidate fields.

Required normalization:

- strip HTML tags
- decode entities
- canonicalize URL
- normalize title spacing
- create hash_key
- create similarity_key
- infer language
- infer rough category

### 3. Save Candidate Before Publishing

Every collected candidate must be saved before publishing.

This allows duplicate detection, audit, and future analysis.

No candidate should be published before DB insertion.

### 4. Summarize

Summarize candidate news before evaluation.

Initial summarizer may be rule-based.

Optional local LLaMA integration can be added behind an interface.

Summarizer output:

- short_summary
- key_points
- reason_for_foreign_worker_relevance
- risk_notes

### 5. Evaluate Candidate

The evaluator selects the best candidate automatically.

Suggested scoring factors:

- foreign_worker_relevance_score
- freshness_score
- source_reliability_score
- duplicate_risk_score
- content_clarity_score
- facebook_post_suitability_score

The highest valid candidate becomes `READY_TO_PUBLISH`.

Low-quality candidates become `SKIPPED`.

Duplicates become `DUPLICATE`.

### 6. Duplicate Check

Duplicate check must happen before publish.

Minimum duplicate checks:

- same canonical URL
- same hash_key
- similar title
- same keyword and same event within recent time window
- already published source URL

Optional local LLaMA duplicate check:

- Compare new candidate summary/title against recent published candidates.
- Ask local LLaMA whether they describe the same real-world news event.
- Local LLaMA result is advisory, not the only source of truth.
- If LLaMA is unavailable, fallback to deterministic duplicate rules.

The system must not fail just because local LLaMA is unavailable.

### 7. Auto Publish

After duplicate check and evaluation, publish automatically to Facebook.

No Telegram approval step is allowed.

Facebook post should include:

- concise headline
- short summary
- why it matters to foreign workers
- source link
- optional hashtags

### 8. Telegram Result Notification

After publishing, send result notification to Telegram.

Telegram message should include:

- published/skipped/duplicate/failed status
- selected title
- source URL
- Facebook post ID if published
- duplicate reason if skipped as duplicate
- error message if failed

Telegram is for user check only, not approval.

### 9. Save Publish Result

Save publish result to DB.

Required logs:

- facebook_publish_log
- telegram_notify_log
- candidate status update

### 10. Continue

After each cycle:

- continue with next keyword or next candidate
- respect API limits
- avoid repeated posting in short intervals
- write cycle summary to logs

## State Machine

```text
COLLECTED
→ NORMALIZED
→ SAVED
→ SUMMARIZED
→ EVALUATED
→ DUPLICATE | SKIPPED | READY_TO_PUBLISH
→ PUBLISHED | FAILED
→ NOTIFIED
```

The DB may keep simplified statuses:

```text
CANDIDATE
DUPLICATE
SKIPPED
READY_TO_PUBLISH
PUBLISHED
FAILED
NOTIFIED
```

## Database Requirements

News automation requires at least:

- news_candidate
- facebook_publish_log
- telegram_notify_log
- news_performance_snapshot later

The DB should store all candidate and publish metadata needed to avoid duplicate posts.

## Local LLaMA Role

Local LLaMA may be used in three places:

1. Candidate relevance check
2. Summary generation
3. Semantic duplicate check

Rules:

- It must be optional.
- It must have timeout handling.
- It must have deterministic fallback.
- Its output must be logged with confidence and reason.
- It must not directly publish anything.

## Dry-run Requirement

Dry-run mode must exist before real publish.

Dry-run should:

- collect or use sample candidates
- save to DB
- run normalization
- run summarization
- run duplicate check
- select candidate
- simulate Facebook publish
- simulate Telegram notification
- update DB statuses accordingly or mark dry_run

Dry-run must not call real Facebook or Telegram APIs.

## Environment Variables

Never hardcode secrets.

Required for real mode:

```text
NAVER_CLIENT_ID
NAVER_CLIENT_SECRET
FACEBOOK_PAGE_ID
FACEBOOK_PAGE_ACCESS_TOKEN
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Optional:

```text
LOCAL_LLAMA_ENDPOINT
LOCAL_LLAMA_MODEL
```

## Completion Criteria

- Approval/reject/keep flow is removed.
- Pipeline can run without user approval.
- Candidate is stored before publish.
- Duplicate detection uses DB history.
- Local LLaMA duplicate/relevance check is optional and non-blocking.
- Facebook publish is automatic in real mode.
- Telegram only receives result notifications.
- Dry-run mode is available.
- Walkthrough is updated after implementation.
