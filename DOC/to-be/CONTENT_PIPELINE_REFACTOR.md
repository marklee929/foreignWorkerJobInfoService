# Content Pipeline Refactor Plan

## Objective

Separate source collection pipelines from the final Facebook publishing pipeline.

## Harness Status

Status: future implementation candidate.

This plan is aligned with the current database architecture direction, but implementation must not be started from a DOC_ONLY session.

The following parts are protected or high-risk:

- changing the final Facebook publish path
- changing scheduler behavior
- changing automatic publish selection
- changing retry/cooldown behavior
- bulk backfill, archive, or migration of content candidates

Recommended first step is a read-only audit of actual source-to-content sync behavior and publish-log ownership.

## Target Model

```text
source domain rows
  -> source-specific cleanup and scoring
  -> content.content_candidate
  -> publish scheduler
  -> content.publish_log
  -> source row publish fields updated through raw_ref_table/raw_ref_id
```

## Source Pipelines

Source pipelines collect and normalize data only:

- social news articles
- immigration notices
- occupation/job dictionaries
- living information
- visa and stay information

They should not directly decide final Facebook publishing except for creating/updating a content candidate.

## Publishing Pipeline

The publishing pipeline selects from `content.content_candidate`.

Rules:

- Source duplicate rows are not active content.
- `raw_ref_table` and `raw_ref_id` are required for traceability.
- Only representative, validated, publishable rows become `READY_TO_PUBLISH`.
- Sensitive rows become `REVIEW_REQUIRED_SENSITIVE` or `READY_TO_REVIEW`.
- Posted rows update both content and source publish metadata.

## Scheduling Rules

Recommended:

- 30-minute publish cadence.
- Daily max 48 posts.
- No failure cooldown that hides available candidates; show "no candidate" separately from "cooldown active".
- Rotation by priority group/category to prevent one source from dominating.

## Facebook Validation

Message rules:

- English-only automated posts.
- No operational/admin text in the final Facebook body.
- Do not include pipeline status, score thresholds, queue state, skip reasons, or internal log text.
- Build message from article/content fields only: title, summary, why-it-matters, and hashtags.

Link rules:

- Use Facebook Graph API `link` parameter.
- Do not paste long article URLs into `message`.
- Reject Google News URLs as final link-card URLs.
- Reject publisher root URLs.
- Reject legacy `/path/A...` redirect URLs.
- Prefer canonical article URLs.

Applied:

- `social.news.publisher.facebook_publisher` now exposes shared message/link validation.
- `content.service` uses that validation before dry-run or real publish.

## Sensitive Content

Sensitive content should not auto-publish.

Examples:

- accidents
- deaths
- crime
- discrimination or hate incidents
- political conflict
- labor dispute content with unclear facts
- articles that may overexpose personal damage or victims

Handling:

- Mark as `REVIEW_REQUIRED_SENSITIVE`.
- Preserve data for review.
- Allow manual publishing only after admin approval.

## Direct News Publishing

Current risk:

- The existing social news pipeline can still publish directly while the content hub also has a publish path.

Target:

- Add or enforce `NEWS_DIRECT_FACEBOOK_PUBLISH=false`.
- Scheduler should publish via `content.content_candidate`.
- Social News screen should remain a source management screen.

Do not remove direct publishing in one large change. First add observability and feature flags, then migrate scheduler behavior, then retire the direct path.

## Integration Direction

- Immigration notices: sync important official notices into content candidates.
- Occupation/job info: enrich first, then create content only when `content_ready_yn = true`.
- Living info: build source-specific collectors and content generators before publishing.

## TODO

- Add index migration for content/source lookup and status/date filters.
- Add content publish scheduler with 30-minute cadence.
- Add daily publish cap.
- Add category/priority rotation.
- Add validation status fields or derived API response for UI.
- Backfill/archive duplicate content candidates after review.
- Clean existing mojibake labels and error messages.
