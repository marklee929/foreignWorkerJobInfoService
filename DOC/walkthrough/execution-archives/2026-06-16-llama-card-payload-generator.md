# LLaMA Card Payload Generator

Date: 2026-06-16
Mode: GUARDED_FIX
Area: CONTENT_QUEUE / DATA_SOURCE_QUALITY / LLAMA_STATUS

## Purpose

Add a local utility that turns source-backed content text into a validated WorkConnect card payload JSON, then renders a 1080x1080 preview PNG with the existing card renderer.

This does not publish to Facebook, send Telegram messages, change scheduler behavior, change auth, or modify DB migrations.

## Input

CLI direct input:

```powershell
python -m foreign_worker_life_info_collector.tools.generate_content_card_from_text `
  --template LIVING_IN_KOREA `
  --text "Foreign residents in Korea should keep their address, health insurance, and banking information updated." `
  --source "WorkConnect Guide" `
  --link "https://www.facebook.com/profile.php?id=61581518066485" `
  --date "2026-06-16"
```

Input JSON mode:

```powershell
python -m foreign_worker_life_info_collector.tools.generate_content_card_from_text --input sample_input.json
```

Required request fields:

- `content_text`
- `source`
- `link`
- `date`
- optional `template_type`
- optional `category`
- optional `source_domain`

## Output

The utility prints:

- `generated_image_path`
- `generated_payload_path`
- `validation_status`
- `template_type`
- `source`
- `date`

Generated files use:

```text
{template_type}_{YYYYMMDD_HHMMSS}_{short_hash}.png
{template_type}_{YYYYMMDD_HHMMSS}_{short_hash}.json
```

Output directory:

```text
SRC/foreign_worker_life_info_collector/storage/generated/content_cards/
```

The generated directory is ignored by git.

## LLaMA Prompt

The prompt builder loads:

```text
assets/templates/content_cards/json_payloads/{template_sample}.json
```

It uses each sample payload and its `llama_rule` as the template-specific example/rule source.

Prompt rules:

- JSON only
- no markdown
- no code fence
- no explanation
- English only
- requested `template_type` must be preserved
- `date` must be `YYYY-MM-DD`
- `source` uses user input
- `footer_url` is `WorkConnect Korea`
- `CHECKLIST_HOWTO` requires exactly 4 bullets
- all other templates require exactly 3 bullets

## Validation

Validation rejects:

- invalid JSON
- missing required fields
- unsupported or mismatched `template_type`
- non-English public text
- forbidden system/operation text
- wrong bullet count
- missing source
- missing source link
- invalid date format

Renderer validation still catches text overflow through `CARD_TEXT_OVERFLOW`.

LLaMA raw response is not copied into public output when invalid.

## Renderer Connection

The generator passes validated payloads into:

```text
content.card_generator.render_content_card
```

The renderer was extended to support templates with 4 bullet positions, so `CHECKLIST_HOWTO` now renders all 4 checklist items.

## Verification

Commands run:

```powershell
python -m py_compile SRC\foreign_worker_life_info_collector\content\card_payload_generator.py SRC\foreign_worker_life_info_collector\content\card_generator.py SRC\foreign_worker_life_info_collector\tools\generate_content_card_from_text.py SRC\foreign_worker_life_info_collector\tests\test_content_card_payload_generator.py
python -m unittest foreign_worker_life_info_collector.tests.test_content_card_payload_generator foreign_worker_life_info_collector.tests.test_content_card_generator foreign_worker_life_info_collector.tests.test_content_exclusion_gate foreign_worker_life_info_collector.tests.test_content_review_dedupe
python -m foreign_worker_life_info_collector.tools.generate_content_card_from_text --template CHECKLIST_HOWTO --text "Health insurance status can affect clinic visits, visa renewals, and unpaid bills. Foreign residents should confirm payment status, keep receipts, and ask NHIS before deadlines." --source NHIS --link https://www.nhis.or.kr --date 2026-06-16 --sample-mode
```

Results:

- `py_compile`: OK
- Unit tests: 26 tests OK
- CHECKLIST_HOWTO sample-mode CLI: OK
- LLaMA disabled path: returns `LLAMA_UNAVAILABLE`

## Protected Areas

Not modified by this task:

- FacebookPublisher
- Facebook token validation
- scheduler
- admin auth
- DB migration
- Telegram actual send path
- automatic publish selection logic
- raw token/env values
- template PNG files

## TODO

- Run a live local LLaMA request when Ollama is intentionally enabled.
- Add curated Korean-to-English operator review flow for Korean official source text.
- Optionally add an Admin UI button for local card preview generation.
