# Living Information Parameter and Source Bottleneck Audit

Date: 2026-07-02

## Scope

This report covers the second `!wc-next` block in `DOC/walkthrough/2026-07-02 - execute prompt.md`.

Purpose:
- continue from the saved Living Information data-quality audit
- identify whether low collection volume is caused by parameters, collector behavior, source/API/RSS coverage, parser/body extraction, duplicate filtering, or mapping
- implement safe fixes when available

## Inputs Read

- `DOC/walkthrough/execution-history/2026-07-02/living-info-data-quality-audit-report.md`
- `DOC/walkthrough/execution-history/2026-07-02/living-info-collector-input-expansion-implementation-report.md`
- `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
- `DOC/to-be/11_SOURCE_COLLECTION_AUDIT_PLAN.md`
- `SRC/foreign_worker_life_info_collector/api/admin_server.py`
- `SRC/foreign_worker_life_info_collector/social/news/collector/google_news_collector.py`
- `SRC/foreign_worker_life_info_collector/social/news/collector/naver_news_collector.py`
- `SRC/foreign_worker_life_info_collector/social/news/collector/rss_news_collector.py`

## Parameter Audit

| Parameter | Current / observed state | Classification |
| --- | --- | --- |
| `dry_run` for lifestyle bot | Fixed `dry_run=True` | Safe; prevents external Facebook/Telegram publish |
| lifestyle keyword count before fix | 3 broad fixed queries | Too restrictive |
| lifestyle keyword count after fix | 13 default keywords, default 8 executed | Improved manual breadth |
| lifestyle per-keyword limit before fix | fixed `limit=1` | Too restrictive |
| lifestyle per-keyword limit after fix | default 3, env override capped at 10 | Improved manual volume |
| collector run frequency | not changed | Protected/scheduler boundary avoided |
| Google News source | RSS search per keyword | Discovery/trusted-media path, not official-source path |
| Naver source | OpenAPI, returns 0 when credentials are absent | Credential-dependent; not safe to change unattended |
| parser/body extraction | RSS resolver attempts source URL and article metadata; body can still be empty | Secondary issue |
| duplicate filtering | duplicate counts were low in DB audit | Not primary bottleneck |
| living-info mapping | topic clusters have 0 public-ready rows | Immediate content-sync blocker |

## Source / API / RSS Audit

### Google News

- Path: `GoogleNewsCollector -> RSSNewsCollector`
- Expected role: discovery and trusted-media signal collection
- Expected volume: depends on keyword breadth and RSS result availability
- Actual DB evidence: living-ish volume is low; `living_info.source_item` has only 55 rows total
- Body availability: RSS path tries article extraction, but body can be empty
- URL quality: RSS collector keeps Google News URL separate and tries to resolve a source URL
- Card mapping potential: medium for media explainers, low for official public-guide cards unless paired with primary evidence

### Naver News

- Path: `NaverNewsCollector`
- Expected role: Korean news search when `NAVER_CLIENT_ID` and `NAVER_CLIENT_SECRET` exist
- Actual behavior: returns `[]` when credentials are absent
- Body availability: attempts article metadata extraction from original link
- Card mapping potential: medium for trusted media, low for official guide evidence
- Constraint: credentials/env are protected and were not touched

### Official / Public Sources

- Current dedicated source path: none found for Living Information official/public guide collection
- Current workaround: official-source-oriented search keywords were added to the manual lifestyle bot
- Card mapping potential: high when real official source pages are collected and preserved
- Remaining gap: needs a dedicated read-only official/public source collector or source registry in a future guarded task

### RSS / API Coverage

- Current RSS implementation is generic and search-driven.
- It is useful for discovery but does not guarantee primary evidence.
- No dedicated NHIS/NPS/MOEL/HiKorea/Seoul Global Center RSS/API connector was found.

### Community Sources

- No live Reddit/X/Threads/community collection path was found in the current Living Information collector.
- Per architecture, community data must remain signal-first only and must not become public content without official/trusted validation.

## Bottleneck Classification

Confirmed:

- `PARAMETER_TOO_LOW`: lifestyle bot used fixed `limit=1`; safe fix raised default to 3.
- `SOURCE_TOO_NARROW`: lifestyle bot used 3 broad queries; safe fix expanded source-oriented keyword list.
- `QUERY_TOO_GENERIC`: original queries were broad and attracted travel/politics/economy/noise.
- `RSS_OR_API_LOW_SIGNAL`: Google RSS is discovery/media-oriented; Naver requires credentials and is not an official-source path.
- `LIVING_INFO_MAPPING_GAP`: sync path sees 0 public-ready topic clusters.
- `REVIEW_ELIGIBILITY_GAP`: no topic-cluster based ready candidates reach review.

Secondary:

- `BODY_MISSING`: some old direct content candidates have missing body, but source_item rows were not missing both body and summary.
- `PARSER_FAILURE`: possible secondary issue, not proven as primary by current DB evidence.

Not primary:

- `DRY_RUN_ONLY`: dry-run blocks external publish, not DB candidate saving/evaluation.
- `DUPLICATE_OVERFILTER`: duplicate groups were low.
- `URL_INVALID`: source_item URL fields were mostly present.

## Safe Implementation Completed

Already implemented in the previous checkpoint:

- expanded `LIFESTYLE_BOT_KEYWORDS`
- added official/public-source-oriented queries
- changed default max keywords from 3 to 8
- changed fixed `limit=1` to configurable default per-keyword limit 3
- kept `dry_run=True`
- exposed `keyword_count`, `per_keyword_limit`, and per-keyword `limit` in the lifestyle bot result payload
- added contract tests

No additional runtime code change was required for this block because the safe parameter/source fix was already complete.

## Verification

Previously run and still applicable:

```powershell
python -m pytest SRC\foreign_worker_life_info_collector\tests\test_living_info_manual_sync_endpoint_contract.py
python -m py_compile SRC\foreign_worker_life_info_collector\api\admin_server.py
```

Result:
- 6 tests passed.
- `admin_server.py` compiled successfully.
- No external collection or publishing was run.
- Protected boundaries were not touched.

## Next CODE_TASK_CANDIDATE

AREA:
`LIVING_DOMAIN + SOCIAL_NEWS_COLLECTOR + SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE`

MODE:
`LOW_RISK_FIX`

PURPOSE FUNCTION:
Add a read-only Living Information readiness diagnostic endpoint/panel.

FOCUS:
Expose source count, primary evidence count, secondary/trusted evidence count, would-be topic clusters, public-ready count, and top skip reasons after a prep-cycle dry run.

WHY:
The operator currently sees that cards are not created, but not why readiness failed.

ALLOWED:
- read-only endpoint
- admin display of dry-run diagnostics
- tests for response contract

FORBIDDEN:
- production Telegram send
- Facebook publisher behavior
- scheduler frequency/state
- auth/env/secrets/token
- destructive DB writes
- external live collection

VERIFICATION:
- endpoint contract test
- dry-run service test
- no external output

STOP CONDITIONS:
- diagnostic requires protected credentials or live external collection
- implementation would mutate DB outside existing dry-run behavior
