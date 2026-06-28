# Content Card Template Preview

Date: 2026-06-16
Mode: GUARDED_FIX
Area: CONTENT_QUEUE / TELEGRAM_REPORTING / DATA_SOURCE_QUALITY

## Summary

Implemented WorkConnect 1080x1080 PNG preview generation for information-style content candidates before Telegram Content Review delivery.

Article/news link content keeps the existing OG/link preview path. Facebook publishing payload and publisher logic were not changed.

## Template Mapping

- VISA_IMMIGRATION: `visa immigration template.png`
- WORK_LABOR_RIGHTS: `work labor right template.png`
- LIVING_IN_KOREA: `livin in korea template.png`
- CHECKLIST_HOWTO: `checklist howto template.png`
- ALERT_REVIEW: `alert review template.png`

Template files and coordinate config are under:

`SRC/foreign_worker_life_info_collector/assets/templates/content_cards/`

## Payload

```json
{
  "template_type": "LIVING_IN_KOREA",
  "title": "...",
  "subtitle": "...",
  "bullets": ["...", "...", "..."],
  "source": "...",
  "date": "YYYY-MM-DD",
  "footer_url": "https://www.facebook.com/profile.php?id=61581518066485"
}
```

`footer_url` can be overridden with `WORKCONNECT_CONTENT_CARD_FOOTER_URL`.

## Validation

- English-only public text enforced.
- Korean/CJK/Japanese card text fails with `CARD_TEXT_INVALID_LANGUAGE`.
- Forbidden system/operation wording fails with `CARD_TEXT_FORBIDDEN_SYSTEM_TEXT`.
- Text overflow fails with `CARD_TEXT_OVERFLOW`; text is not silently truncated.
- Score 0 candidates are skipped with `CARD_BLOCKED_ZERO_SCORE`.
- Blocked quality gate codes are skipped before rendering.
- Valid-link `NEWS_ARTICLE` candidates skip cards with `NEWS_ARTICLE_LINK_PREVIEW_USES_OG`.

## Telegram Review Change

`send_content_review_to_telegram` now:

- builds a card preview before review metadata creation;
- includes sanitized card preview metadata in review logs;
- sends `sendPhoto` with a 1080x1080 PNG when a card preview is generated;
- falls back to `sendMessage` for link/news/non-card candidates;
- records card generation failures without sending Telegram spam.

Duplicate review suppression still runs before actual Telegram delivery.

## Sample

Sample generation script:

`python foreign_worker_life_info_collector/scripts/generate_content_card_sample.py`

Generated sample:

`SRC/foreign_worker_life_info_collector/storage/cache/content_cards/workconnect-card-checklist_howto-c18abcf9001c.png`

The cache directory is ignored by git.

## Tests

Commands run:

```powershell
python -m py_compile SRC\foreign_worker_life_info_collector\content\card_generator.py SRC\foreign_worker_life_info_collector\content\service.py SRC\foreign_worker_life_info_collector\api\admin_server.py SRC\foreign_worker_life_info_collector\tests\test_content_card_generator.py SRC\foreign_worker_life_info_collector\scripts\generate_content_card_sample.py
python -m unittest foreign_worker_life_info_collector.tests.test_content_card_generator foreign_worker_life_info_collector.tests.test_content_exclusion_gate foreign_worker_life_info_collector.tests.test_content_review_dedupe
python foreign_worker_life_info_collector\scripts\generate_content_card_sample.py
```

Result:

- `py_compile`: OK
- Unit tests: 21 tests OK
- Sample PNG generation: OK

## Protected Areas

Not modified:

- FacebookPublisher
- Facebook token validation
- scheduler interval/cooldown
- admin auth
- DB migration
- raw token/env values

## TODO

- Verify actual Telegram `sendPhoto` against a configured dev bot/chat.
- Add UI preview link for generated card image if Admin Review needs local display.
- Add curated English title generation before card rendering for Korean official titles.
