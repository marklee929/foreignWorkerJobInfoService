# GUARDED_FIX REPORT: LIVING_INFO Card Generation Guardrail

## 1. Pre-Review

- AREA: `LIVING_DOMAIN + CONTENT_CARD_GENERATION`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM
- Protected areas touched: NO
- Files inspected:
  - `CODEX_BOOTSTRAP.md`
  - `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  - `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
  - `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
  - `DOC/walkthrough/2026-06-20 - execute prompt.md`
  - `DOC/walkthrough/execution-history/2026-06-20/living-info-topic-card-read-only-audit-report.md`
  - `DOC/correction-loop/2026-06-20_LIVING_INFO_TOPIC_CARD_AUDIT.md`
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_content_card_generator.py`
- Files modified:
  - `SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_content_card_generator.py`
  - `DOC/walkthrough/2026-06-20 - execute prompt.md`
  - `DOC/walkthrough/execution-history/2026-06-20/living-info-card-generation-guardrail-report.md`

## 2. Current Cause

`ContentService.social_news_payload()` assigns living-classified social/news candidates as:

```text
source_domain = LIVING_INFO
content_type = LIVING_GUIDE
```

`build_content_card_preview()` then treated `LIVING_INFO / LIVING_GUIDE` as information-domain card targets. This allowed a single `social_news.candidate` item to become a card preview when no topic cluster or fact-point evidence existed.

`build_content_card_payload()` also built bullets from `summary_en`, `body_en`, or `why_it_matters_en` without rejecting title echo, source echo, URL echo, duplicate points, or insufficient point count.

The footer used a default Facebook profile URL, which could appear inside the image.

## 3. Changes Made

`SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py`

- Added `MIN_VALID_BULLETS = 3`.
- Added text-review-only failure codes so invalid card points block image generation without blocking text review metadata.
- Added `is_single_living_source_without_topic_evidence()`.
- Added `has_topic_or_fact_evidence()`.
- Added deterministic card point validation:
  - `invalid_card_point_reason()`
  - `normalized_card_point()`
  - `mostly_repeats_title()`
  - `contains_url()`
- Changed `card_bullets()` to require 3 validated points.
- Changed footer generation to `WORK CONNECT KOREA` instead of URL fallback.
- Added footer URL validation.

`SRC/foreign_worker_life_info_collector/tests/test_content_card_generator.py`

- Added tests for single `social_news.candidate` living card block.
- Added test that topic evidence allows rendering.
- Added tests for title echo, source echo, URL echo, one valid bullet, and footer URL removal.

## 4. Collection Coverage

Collection coverage was not reduced.

No collector, source pipeline, scheduler, repository collection query, raw source storage, normalization, or `ContentService.social_news_payload()` source sync behavior was changed.

News/article/blog/community items can still be collected and stored as source evidence. The change only blocks premature card preview generation.

## 5. Validation Rules Added

Reject a card point when:

- it is too short
- it equals the title
- it mostly repeats the title
- it combines title and source
- it is source attribution only
- it contains a URL
- it contains a Facebook URL
- it contains internal/system/error text
- it is a generic label
- it duplicates another point after normalization

For 3-slot card templates, fewer than 3 validated points now returns `INSUFFICIENT_VALID_CARD_POINTS`.

## 6. LIVING_INFO Single Article Public-Card Guardrail

For `LIVING_INFO / LIVING_GUIDE`, if the candidate comes from `social_news.*` and has no topic/fact evidence, card preview generation returns:

```text
status = CARD_NOT_READY
reason = single_news_public_card_not_ready
card_required = false
```

This keeps source evidence available while preventing premature public-style card image generation.

Topic/fact evidence can allow rendering when at least one of the following is present:

- `topic_key`
- `topic_cluster_id`
- `fact_point_id`
- `card_point_id`
- `source_spread_count >= 2`
- `related_source_count >= 2`
- `group_item_count >= 2`
- `usable_point_count >= 3`
- `fact_point_count >= 3`
- `card_point_count >= 3`

## 7. Footer URL Fix

Card image footer now defaults to:

```text
WORK CONNECT KOREA
```

Candidate-provided footer text is only accepted if it has no URL, no forbidden system text, and no non-English public text.

Full `source_url`, `canonical_url`, `publishable_link_url`, and Facebook page/profile URLs are not used inside the card image footer.

Source links remain available outside the image through existing Telegram review message or metadata paths.

## 8. Verification

Commands run:

```text
python -m py_compile SRC\foreign_worker_life_info_collector\utils\content_card_renderer.py
python -m unittest foreign_worker_life_info_collector.tests.test_content_card_generator
```

Results:

```text
py_compile: PASS
unittest: PASS
Ran 14 tests in 14.614s
OK
```

Verified cases:

- title-only/article-like bullet does not become valid card point
- bullet equal to title is rejected
- source-only bullet is rejected
- URL bullet is rejected
- only 1 valid bullet blocks card generation
- 3 valid bullets render
- single `social_news.candidate` `LIVING_INFO` item without topic evidence is `CARD_NOT_READY`
- topic evidence allows rendering
- footer does not contain Facebook profile URL or long URL
- collection path was not modified
- no external API calls were made

## 9. Protected Areas

- Facebook publisher not touched
- scheduler not touched
- Telegram callback not touched
- auth/env/config not touched
- DB/migration not touched
- external API not called
- no real publish/notification sent

## 10. Remaining Risks

- This change blocks premature card preview generation, but it does not add persistent `topic_key`, `fact_point`, or `card_point` schema.
- Existing admin screens may show `CARD_NOT_READY` reason only where card preview status/reason is already surfaced.
- Broader ownership between `social_news.candidate` and `content.content_candidate` still needs a separate DB/domain audit.

## 11. Next CODE_TASK_CANDIDATE

```text
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY + CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Design topic_key / fact_point / card_point ownership before adding persistent topic-based living card generation.
FOCUS:
Map whether topic clustering and usable card points belong in social_news, content, or a living-domain layer.
RISK: MEDIUM
ALLOWED FILES:
DOC only
FORBIDDEN:
DB mutation, migration, scheduler, publisher, Telegram callback, auth/env/config, external API
VERIFICATION:
ownership matrix, proposed fields, migration impact, example topic cluster SELECT
STOP CONDITIONS:
Ownership requires product decision or protected runtime change.
```

## 12. Closeout

- report saved: YES
- execute prompt updated: YES
- correction-loop updated if needed: NO new recurring harness miss found
- `[WC_EXECUTION_COMPLETE]` marker verification passed: YES
