# Admin UI Improvement Plan

## Goal

Make the admin UI an operational console that is fast to open, clear about data ownership, and safe around publishing/destructive actions.

## Dashboard

Current role:

- Show operational status, counts, recent logs, bot state, Facebook/LLaMA readiness, and recent candidates.

Problems:

- Polling was too frequent for a multi-endpoint screen.
- The screen can look like a source-data browser even though it should be an overview.
- Some labels are encoding-damaged.

Applied:

- Silent refresh TTL changed to 30 seconds.
- Polling pauses while the browser tab is hidden.
- Existing paged log loading is preserved.

Next:

- Keep dashboard responses summary-only.
- Limit recent logs to 10-20 rows.
- Move detailed candidate browsing to Social News and Content Management.
- Add clear labels for "source news", "final content", and "posted".

## Social News Screen

Current role:

- Manage source articles, duplicate groups, article body/link cleanup, scoring, and source-to-content linkage.

Problems:

- It is easy to confuse source-news state with final publishing state.
- Facebook links may appear in source-news rows even when the final content row should be the main publishing record.

Next:

- Show `content_candidate_id`, content status, and content Facebook URL as linkage metadata.
- Keep duplicate/non-representative rows visible only when requested.
- Add filters for representative, duplicate group, publish status, sensitive/review-required, and content linked/unlinked.

## Content Management

Current role:

- Manage final Facebook publishable content from social news, immigration, and future sources.

Problems:

- Date columns need stronger separation.
- Publish validation needs to be visible before a user clicks publish.

Applied:

- Content publishing now validates message language/admin text and article link-card URL before posting.

Next:

- Display separate columns:
  - original published at
  - original collected at
  - content created at
  - content updated at
  - posted at
- Show validation state: ready, needs review, invalid link, non-English message, sensitive review required.
- Prefer content Facebook URL on this screen.

## Occupation/Job Info

Current role:

- Code dictionary and job/occupation reference data.

Problems:

- Code/name lists are not enough for content or search workflows.

Next:

- Add enrichment fields:
  - `occupation_name_en`
  - `search_keywords_en`
  - `visa_tags`
  - `industry_tags`
  - `foreign_worker_fit`
  - `content_potential_score`
  - `content_ready_yn`
- Show enrichment readiness clearly.

## Immigration Notices

Current role:

- Collect official notices and prepare them for review/publishing.

Next:

- Distinguish official notice source fields from generated content fields.
- Route publishable notices through `content.content_candidate`.
- Keep manual approval for high-impact or unclear notices.

## LLaMA Controls

Current role:

- Show local/external LLaMA endpoint state and allow reconnect/start/stop.

Next:

- Separate labels for:
  - auto-use on/off
  - model unload
  - Ollama server stop
  - external endpoint disabled
  - local endpoint connected/disconnected
- Avoid ambiguous "LLaMA off" wording.

## Query Performance

Rules:

- No full-table list load on screen entry.
- Use SQL `COUNT`, `GROUP BY`, pagination, and `LIMIT`.
- Recent logs: 20 rows by default.
- Details load only after row click.
- Dashboard uses store/API cache TTL.
- Polling must be cleaned up on unmount and paused when the document is hidden.

## Automatic Article Repair

Applied:

- Admin API starts a background article cleanup scheduler.
- It periodically repairs recoverable source-news rows with missing URLs, empty/short body text, failed content fetch state, zero score, or `TEXT_INVALID` status.
- It does not auto-process duplicate, archived, posted, or already-published rows.
- It uses a retry interval so the same failed row is not hammered every cycle.

Runtime settings:

- `NEWS_ARTICLE_AUTO_CLEANUP=true`
- `NEWS_ARTICLE_AUTO_CLEANUP_INTERVAL_MINUTES=15`
- `NEWS_ARTICLE_AUTO_CLEANUP_LIMIT=20`
- `NEWS_ARTICLE_AUTO_CLEANUP_RETRY_MINUTES=30`

Recommended indexes:

- `social_news.candidate(status)`
- `social_news.candidate(publish_status)`
- `social_news.candidate(cycle_id)`
- `social_news.candidate(collected_at)`
- `social_news.candidate(duplicate_group_id)`
- `content.content_candidate(status)`
- `content.content_candidate(content_type)`
- `content.content_candidate(category)`
- `content.content_candidate(created_at)`
- `content.content_candidate(raw_ref_table, raw_ref_id)`
- `social_news.pipeline_log(created_at)`

## Safety

- Destructive actions require confirm dialogs.
- Publishing buttons must show dry-run vs real mode.
- Real publish should be disabled when validation fails.
- Sensitive content should become `REVIEW_REQUIRED_SENSITIVE` and require manual approval.

## Estimated Sequence

1. Text/label cleanup pass for encoding-damaged strings.
2. Dashboard endpoint and store-cache cleanup.
3. Content Management validation labels and date columns.
4. Social News linkage filters.
5. Index migration.
6. Occupation enrichment UI.
7. LLaMA wording and action separation.
