# Content Publishing Hub

## Current Decision

News collection and Facebook publishing are being separated.

- `social_news.candidate` remains the source table for the existing Social News board.
- The Social News board UI remains unchanged.
- Publishable items are copied into `content.content_candidate`.
- The `/content` admin page becomes the integrated publishing queue.
- Other refined domains can become Facebook content by writing rows into `content.content_candidate`.

## Added Database Objects

Migration:

- `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_07_content_candidate.sql`

Tables:

- `content.content_candidate`
- `content.publish_log`

Key reference fields:

- `raw_ref_table`
- `raw_ref_id`
- `raw_payload`

These fields connect a content candidate back to the original source row without changing the source board.

## Initial Source Mapping

| Source table | source_domain | content_type | Status mapping |
| --- | --- | --- | --- |
| `social_news.candidate` | `SOCIAL_NEWS` | `NEWS_ARTICLE` | high-scoring unposted rows become `READY_TO_PUBLISH`; posted rows become `POSTED` |
| `immigration_info.official_notice` | `IMMIGRATION_INFO` | `IMMIGRATION_NOTICE` / `GOVERNMENT_NOTICE` | important official notices become `READY_TO_PUBLISH` or `READY_TO_REVIEW` |

Planned sources:

- `LIVING_INFO`
- `VISA_INFO`
- `OCCUPATION_INFO`
- `GOVERNMENT_NOTICE`

Each source should create or update `content.content_candidate` through the same upsert interface.

## Backend API

Added endpoints:

- `GET /api/admin/content/dashboard`
- `GET /api/admin/content/candidates`
- `GET /api/admin/content/candidates/{id}`
- `POST /api/admin/content/sync`
- `POST /api/admin/content/candidates/{id}/publish`

Publishing is guarded by environment variables:

- `CONTENT_AUTO_PUBLISH=true`
- `CONTENT_PUBLISH_TEST_MODE=false`
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_ACCESS_TOKEN`

If these are not enabled, content publishing records a dry-run publish log and does not call Facebook.

## Admin UI

Route:

- `/content`

Purpose:

- Show integrated publishable candidates.
- Keep `/social-news` as the news-specific board.
- Allow manual content sync from existing source tables.
- Show candidate detail, scores, source link, and publish logs.
- Run publish simulation from the content list.

## Message/Link Rule

Facebook publishing should keep message and link separate:

- `message`: title, summary, why-it-matters, hashtags
- `link`: candidate `link_url`

The message should not embed long article URLs.

## Validation Performed

Commands:

```powershell
python -m py_compile SRC\foreign_worker_life_info_collector\content\repository.py SRC\foreign_worker_life_info_collector\content\service.py SRC\foreign_worker_life_info_collector\api\admin_server.py
npm run build
```

Database sync smoke test:

```powershell
cd C:\WORK\foreign_worker_job_info\SRC
python - <<'PY'
from foreign_worker_life_info_collector.content.service import ContentService
service = ContentService()
print(service.sync_all(limit=20))
print(service.repository.dashboard())
PY
```

Result:

- `social_news.candidate`: 20 seen / 20 synced
- `immigration_info.official_notice`: 3 seen / 3 synced
- `content.content_candidate`: 23 total
- `READY_TO_PUBLISH`: 11

## Remaining Work

- Move the automatic scheduler from direct news publishing to the content publisher.
- Add 30-minute content publish cooldown.
- Add daily max 48 post guard.
- Add priority group rotation: `PRIMARY`, `SECONDARY`, `TERTIARY`.
- Add living info, visa info, occupation info content generators.
- Route Telegram publish notifications through content publish results.
- Disable or wrap direct news Facebook publishing with `NEWS_DIRECT_FACEBOOK_PUBLISH=false`.
