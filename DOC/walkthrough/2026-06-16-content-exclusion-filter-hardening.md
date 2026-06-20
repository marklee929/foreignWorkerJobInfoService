# Content Exclusion Filter Hardening

Report date: 2026-06-16 KST

## Harness Scope

AREA:

- SOCIAL_NEWS_CANDIDATE
- CONTENT_QUEUE
- DATA_SOURCE_QUALITY

MODE:

- GUARDED_FIX

Decision:

- PROCEED_WITH_LIMITS

Limits:

- No FacebookPublisher change.
- No Facebook token validation change.
- No scheduler interval change.
- No bot ON/OFF state change.
- No admin auth change.
- No DB migration.
- No raw token/env change.
- No external API call.
- No Facebook publish payload change.

## Pre-Review Summary

Current flow checked:

```text
social_news.candidate
-> social_news_payload()
-> content.content_candidate
-> review_targets()
-> requires_telegram_review()
-> send_content_review_to_telegram()
```

Findings:

- `social_news_payload()` promoted high-score rows to `READY_TO_PUBLISH` or `READY_TO_REVIEW` mostly by score and sensitivity.
- `LIVING_INFO` was broad because categories such as `travel`, `lifestyle`, `culture`, `local_events`, and `safety` counted as living.
- `list_review_targets()` included `SCORED`, `READY_TO_REVIEW`, `READY_TO_PUBLISH`, and `FAILED_RETRYABLE` for `LIVING_INFO` and `IMMIGRATION_INFO`.
- Existing Telegram dedupe suppressed repeat alerts but did not block the first low-value alert.
- Link-missing and system-text cases were partly caught later by Facebook/link validation, not consistently before review eligibility.

## Filters Added

Added deterministic content quality gate in `content.service`:

- `content_quality_gate()`
- `apply_content_quality_gate()`
- `valid_content_link()`
- category/domain helper checks for travel, crypto, politics, economy, watch topics, system text, and missing content

The gate is applied at:

- source-to-content payload creation for social news
- source-to-content payload creation for immigration notices
- Telegram Review eligibility
- content publish entry point before Facebook publishing can be attempted

## Hard Block Criteria

Hard blocked:

- missing or invalid link
- Google News final link
- system/queue/parser/internal text in public fields
- non-Korea global reference only
- title-only or missing content for non-official items
- target country mismatch for non-official items

Blocking result:

- no Telegram Review
- no auto publish
- candidate downgraded to `SCORED` when needed
- gate metadata stored in `raw_payload`

Gate codes:

- `BLOCKED_SOURCE_INVALID`
- `BLOCKED_SYSTEM_TEXT`
- `BLOCKED_GLOBAL_REFERENCE_ONLY`
- `BLOCKED_CONTENT_MISSING`
- `BLOCKED_TARGET_COUNTRY_MISMATCH`

## Penalty / Exclusion Criteria

Excluded from review/publish:

- generic travel/tourism/destination safety
- generic crypto/investment
- domestic politics/election/governance without visa/labor/foreigner action
- generic stock market/macro economy without foreign-resident action
- ceremony/MOU/campaign/meeting/PR style items without user actionability
- zero-score candidates
- score below 40 without official utility or strong practical action

Gate codes:

- `BLOCKED_GENERIC_TRAVEL`
- `BLOCKED_GENERIC_CRYPTO`
- `BLOCKED_DOMESTIC_POLITICS`
- `BLOCKED_GENERIC_ECONOMY`
- `BLOCKED_LOW_USER_NEED`

## Watch Topic Criteria

Watch-only items are retained as data but excluded from immediate review/publish.

Implemented watch topics:

- `MINIMUM_WAGE_2026`
- `GLOBAL_MIGRATION_POLICY_REFERENCE`

Gate code:

- `WATCH_TOPIC_ONLY`

## Review Eligibility

Telegram Review now requires:

- valid source link
- no system/internal text contamination
- Korea relevance or official Korea source
- user need/actionability for living items
- non-zero score
- no generic travel/crypto/politics/economy block
- no watch-only classification

Allowed examples:

- actual foreign worker rights notice
- HiKorea visa/manual/lookup utility
- official medical institution lookup
- immigration agency lookup

## Validation Samples

Unit-level sample results:

| Sample | Result |
| --- | --- |
| Japan foreigner policy, link missing | `BLOCKED_SOURCE_INVALID`, no review, no publish |
| Bali travel safety story | `BLOCKED_GENERIC_TRAVEL`, no review |
| Crypto in South Korea generic guide | `BLOCKED_GENERIC_CRYPTO`, no review |
| Korean local election/governance article | `BLOCKED_DOMESTIC_POLITICS`, no review |
| Minimum wage committee meeting announcement | `WATCH_TOPIC_ONLY`, no immediate review |
| Actual foreign worker rights notice | `REVIEW_ELIGIBLE` |
| HiKorea official lookup/manual | `REVIEW_ELIGIBLE` |
| System text / missing body | `BLOCKED_SYSTEM_TEXT`, downgraded to `SCORED` |

## Modified Files

- `SRC/foreign_worker_life_info_collector/content/service.py`
- `SRC/foreign_worker_life_info_collector/content/repository.py`
- `SRC/foreign_worker_life_info_collector/tests/test_content_exclusion_gate.py`
- `DOC/walkthrough/2026-06-16-content-exclusion-filter-hardening.md`

## Verification

Executed:

```text
python -m py_compile SRC\foreign_worker_life_info_collector\content\service.py SRC\foreign_worker_life_info_collector\content\repository.py SRC\foreign_worker_life_info_collector\tests\test_content_exclusion_gate.py SRC\foreign_worker_life_info_collector\tests\test_content_review_dedupe.py
```

Result:

```text
OK
```

Executed from `SRC`:

```text
python -m unittest foreign_worker_life_info_collector.tests.test_content_exclusion_gate foreign_worker_life_info_collector.tests.test_content_review_dedupe
```

Result:

```text
Ran 15 tests in 0.002s
OK
```

## Protected Areas

Not modified:

- FacebookPublisher
- Facebook token validation
- scheduler interval
- bot ON/OFF state
- admin auth
- DB migrations
- raw token/env
- external API integration
- Facebook publish payload

## Remaining TODO

- Add DB/indexed first-class fields for `content_quality_gate_code`, `review_eligible_yn`, and `auto_publish_eligible_yn` if filtering needs to scale beyond JSON payload.
- Add Admin UI display for content gate reason after backend fields stabilize.
- Sample real recent DB rows to tune false positives for politics/economy/travel.
- Decide whether `WATCH_TOPIC_ONLY` needs a dedicated watch-topic table.

## Commit/Push

Not performed.

Reason:

- The working tree already contains pre-existing runtime and UI changes from earlier tasks.
- Some files modified by this task were already dirty before this task, so committing safely would require separating previous work first.
