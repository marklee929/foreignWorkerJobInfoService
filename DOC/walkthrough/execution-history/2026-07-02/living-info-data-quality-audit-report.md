# Living Information Data Quality Audit

Date: 2026-07-02

## Scope

This audit covers the first `!wc-next` execution block in `DOC/walkthrough/2026-07-02 - execute prompt.md`.

Work areas:
- `LIVING_DOMAIN`
- `SOCIAL_NEWS_COLLECTOR`
- `SOCIAL_NEWS_CANDIDATE`
- `CONTENT_QUEUE`

Protected areas were not modified. Diagnostics used read-only database transactions and code inspection.

## Executive Summary

Living Information cards are not missing because the Admin UI button is disconnected anymore. The current failure is earlier and more structural:

1. `living_info.topic_cluster` has 0 persisted rows.
2. A dry-run preparation over the current 55 normalized living-info rows would create 52 clusters, but every cluster has `public_candidate_ready_yn = N`.
3. `content.sync_living_info()` currently sees 0 ready topic clusters, so it syncs 0 Living Information card candidates.
4. Existing `content.content_candidate` rows for `source_domain = LIVING_INFO` are old direct `social_news.candidate` mappings, not topic-cluster based Living Information cards.
5. The living-info collection input is too small and too generic: the lifestyle bot uses 3 fixed English keywords and `limit = 1` per keyword.

Primary bottleneck classification:
- `PARAMETER_TOO_LOW`
- `SOURCE_TOO_NARROW`
- `QUERY_TOO_GENERIC`
- `LIVING_INFO_MAPPING_GAP`
- `SOURCE_EVIDENCE_INSUFFICIENT`

## Database Evidence

### Table Counts

| Table | Count |
| --- | ---: |
| `social_news.candidate` | 1,143 |
| `living_info.source_item` | 55 |
| `living_info.normalized_item` | 55 |
| `living_info.topic_cluster` | 0 |
| `living_info.topic_cluster_item` | 0 |
| `content.content_candidate` | 762 |
| `content.publish_log` | 1,927 |

### Social News Living-ish Volume

| Metric | Count |
| --- | ---: |
| All social news candidates | 1,143 |
| Category/content-category living-ish | 151 |
| Source keyword living-ish | 180 |
| Settlement score >= 0.65 | 89 |
| Practical score >= 0.65 | 42 |

Recent daily living-ish counts are low:

| Date | Total | Living category | Living keyword |
| --- | ---: | ---: | ---: |
| 2026-07-02 | 23 | 1 | 1 |
| 2026-07-01 | 2 | 2 | 2 |
| 2026-06-30 | 6 | 3 | 5 |
| 2026-06-29 | 4 | 1 | 1 |
| 2026-06-28 | 7 | 5 | 6 |

### Living Source Items

`living_info.source_item` has 55 rows. All are `source_type = SOCIAL_NEWS` and `source_status = COLLECTED`.

Source distribution:
- `koreajoongangdaily`: 10
- blank source name: 9
- `The Korea Herald`: 9
- `The Korea Times`: 7
- `Businesskorea`: 6
- other one-off sources: remaining rows

Trust distribution:
- `TRUSTED_MEDIA`: 28
- `DISCOVERY`: 27
- `PRIMARY`: 0

No rows are missing `source_url`, `publishable_link_url`, or both `raw_body` and `raw_summary`.

Duplicate signals:
- duplicate canonical/source URL groups: 2
- duplicate title groups: 3

### Normalized Items

`living_info.normalized_item` has 55 rows.

Primary category distribution:
- `DAILY_LIFE`: 13
- `SAFETY_SCAM`: 11
- `BANKING_FINANCE`: 9
- `HEALTHCARE`: 8
- `TRANSPORTATION`: 7
- `HOUSING`: 5
- `EDUCATION_LANGUAGE`: 1
- `REGIONAL_SUPPORT`: 1

Quality gates:
- `validation_needed_yn = Y`: 55
- `actionability_score >= 0.7`: 29
- `repeatability_score >= 0.7`: 55
- `reliability_score >= 0.7`: 33

Signal type:
- `info_signal_type = NEWS_EVENT`: 55

Usage:
- `TOPIC_CLUSTER_MATERIAL`: 31
- `SOURCE_EVIDENCE`: 24

Target user:
- `FOREIGN_RESIDENTS_IN_KOREA`: 55

### Topic Cluster Readiness

Current persisted cluster tables are empty:
- `living_info.topic_cluster`: 0
- `living_info.topic_cluster_item`: 0

Dry-run preparation result:
- `seen_count = 55`
- would create 52 clusters
- `written_count = 0`
- all dry-run clusters had `public_candidate_ready_yn = N`

Reason:
- readiness scores are mostly 20-45, below the required 60
- most validation statuses are `PENDING`
- no official/primary source evidence exists in the current source set

`sync_living_info(limit=100)` result:
- `seen_count = 0`
- `synced_count = 0`
- `skipped_count = 0`

This is the immediate reason topic-cluster based Living Information cards are not entering the content queue.

### Content Candidate Queue

`content.content_candidate` rows with `source_domain = LIVING_INFO`:

| Status | Count |
| --- | ---: |
| `POSTED` | 41 |
| `ARCHIVED` | 6 |
| `SCORED` | 6 |
| `READY_TO_PUBLISH` | 1 |
| `READY_TO_REVIEW` | 1 |

All 55 rows use `raw_ref_table = social_news.candidate`, not `living_info.topic_cluster`.

Missing fields:
- missing link: 6
- missing body: 12

Interpretation:
- There is 1 old direct `READY_TO_REVIEW` row, but the new topic-cluster based Living Information path currently produces 0 review-ready candidates.

### Publish Log

Living Information publish log summary:
- Telegram review `SENT`: 29
- Telegram review `CARD_TEXT_OVERFLOW`: 23
- Facebook `PUBLISHED`: 11
- Facebook `FAILED_RETRYABLE`: 3
- Facebook `DRY_RUN`: 2
- Telegram duplicate suppressed: 1

Card preview evidence:
- `SENT`: request had card in 1 case, response had card in 0 cases, total 29
- `CARD_TEXT_OVERFLOW`: request had card in 23 cases, response had card in 23 cases
- duplicate suppressed: request and response had card in 1 case

Notable samples include generic or weak living-info candidates such as Bali travel safety, KOSPI, local elections, property investment, crypto, generic politics/economy/travel noise, and one repeated card-text-overflow candidate.

## Quality Mapping

| Group | Approx count | Examples / signals | Reason | Recommended action |
| --- | ---: | --- | --- | --- |
| Usable living-info card source | 0 topic clusters ready | none in current topic-cluster path | No persisted public-ready topic cluster | Require official/trusted evidence and readiness >= 60 |
| Weak but salvageable signal | 24-31 | `SOURCE_EVIDENCE` / `TOPIC_CLUSTER_MATERIAL` rows | Some relevance, but still single-news and validation-needed | Keep as cluster material only |
| Community/user-need signal only | 0 collected in current DB path | none | Current collector is Google/Naver news only | Future community sources must be signal-first only |
| Irrelevant generic news | present in samples | travel, markets, elections, generic economy | Topic may match keywords but not practical living guidance | Tighten keywords and classification |
| Non-Korea/global reference | present in samples | Bali/travel/global examples | Not suitable as Korea living card evidence | Archive or low-value classify |
| Missing URL/body | 6 missing link, 12 missing body in content candidates | direct social-news mappings | Weak card generation input | Improve classification/reporting |
| Duplicate noise | 2 URL groups, 3 title groups | repeated titles/URLs | Low duplicate volume, not primary bottleneck | Keep current duplicate gates |
| Official/trusted source candidate | trusted media 28, primary 0 | Korea Times/Herald/JoongAng | Trusted media exists but no primary sources | Expand official/public source queries |

## Source Expansion Audit

Source expansion is required.

Recommended source roles:
- Official agencies: public guide candidate evidence, required for factual/legal/medical/financial claims.
- Local government foreign resident support centers: practical regional guide evidence.
- Seoul Global Center and city/global-center sources: high-value living guide evidence.
- Gyeonggi and other foreign resident support sources: regional support evidence.
- NHIS / National Pension / banking / telecom / housing guides: primary or near-primary evidence for category-specific cards.
- University international office guides: supplemental living guide evidence, especially housing/banking/healthcare setup.
- Trusted English Korea media: useful explainer/background evidence, not enough alone for official claims.
- Reddit / X / Threads / public community sources: signal-first only; do not quote personal stories directly, and validate claims against official/trusted sources before card creation.

Do not collect private, closed, paywalled, or access-controlled content.

## Pipeline Gap Analysis

| Layer | Finding | Classification |
| --- | --- | --- |
| Collector keyword/source list | Lifestyle bot has only 3 broad English queries | `SOURCE_TOO_NARROW`, `QUERY_TOO_GENERIC` |
| Collector limit | Lifestyle bot passes `limit = 1`; effective collection is very small | `PARAMETER_TOO_LOW` |
| Dry-run flag | `dry_run=True` prevents external Facebook/Telegram publishing but still saves/evaluates candidates | Safe, not the card blocker |
| Parser/body extraction | No source_item rows missing both body and summary; some content candidates missing body | Secondary issue |
| URL normalization | No source_item rows missing publishable URL; small duplicate groups | Not primary blocker |
| Duplicate classification | Duplicate counts are low | Not primary blocker |
| Living info ingestion | 55 source and normalized rows exist | Working, but source quality is weak |
| Normalized item creation | All rows are `NEWS_EVENT` and validation-needed | Evidence quality bottleneck |
| Topic cluster creation | No persisted clusters; dry-run clusters are not public-ready | Immediate sync blocker |
| Content candidate sync | Sees 0 topic clusters | Immediate card queue blocker |
| Review eligibility | No topic-cluster based ready rows; one old direct row exists | Not enough ready source material |
| Admin UI visibility | Button path was fixed earlier, but readiness failure is not obvious to operator | Improve diagnostics later |

## Safe Fix Candidate

Implement a narrow manual-collection parameter/source fix in `admin_server.py`:

1. Move lifestyle bot default keywords into named constants.
2. Expand the default keyword list beyond 3 broad queries.
3. Include official/public-source-oriented queries for foreign resident living support, healthcare, pension, labor, housing, banking, transport, and regional support.
4. Increase the manual default max keyword count from 3 to 8.
5. Increase per-keyword manual pipeline limit from fixed 1 to configurable default 3.
6. Keep `dry_run=True`.
7. Do not change scheduler frequency, production Telegram send, Facebook publisher behavior, credentials, destructive DB behavior, or private/community scraping.

This is safe because it changes only manual one-shot collection input breadth and observability, not publishing or protected runtime boundaries.

## Verification Plan

Targeted verification:
- Add tests for lifestyle bot default keyword breadth and per-keyword limit configuration.
- Verify `dry_run=True` remains fixed for lifestyle bot runs.
- Run the targeted tests.
- Re-run static code inspection for protected-boundary changes.

## Next CODE_TASK_CANDIDATE

After this safe collector input fix, the next useful task is:

`CODE_TASK_CANDIDATE: Add a read-only Living Information readiness diagnostic endpoint/panel that shows source count, primary evidence count, would-be topic clusters, public-ready count, and top skip reasons after a prep-cycle dry run.`
