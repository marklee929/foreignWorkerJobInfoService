# Facebook Token/Publish Error Normalization

Date: 2026-06-10

## Pre-review result

Result: PROCEED_WITH_LIMITS

The failure text `FACEBOOK_PAGE_ACCESS_TOKEN is invalid` was not confirmed as a raw Meta API message. In the current code path it was produced by internal token debug validation in `social/news/publisher/facebook_publisher.py` when `debug_token` reported `is_valid=false`.

No token refresh, token reissue, scheduler interval, bot ON/OFF state transition, candidate selection, scoring, cooldown, or publish frequency change was required.

## Existing failure display

Before this change:

- Meta HTTP errors were parsed in `social/facebook/page_client.py`, but only a simplified `error_code` and `error_message` were returned.
- Internal validation errors in `facebook_publisher.py` reused broad codes such as `FACEBOOK_TOKEN_INVALID`.
- Telegram notifications showed only `Reason`, `Status`, and `Source`, so internal validation and Meta raw errors were hard to distinguish.

## Error message source

Observed text:

`FACEBOOK_PAGE_ACCESS_TOKEN is invalid`

Classification:

- Source: internal token debug validation message
- Not confirmed as: raw Meta `error.message`
- Code path: `FacebookPublisher.publish()` after `debug_token()` result with `is_valid=false`

## Error categories

Added normalized categories:

- TOKEN_INVALID
- TOKEN_EXPIRED
- TOKEN_EXPIRING_SOON
- TOKEN_PERMISSION_MISSING
- TOKEN_WRONG_TYPE
- TOKEN_PAGE_MISMATCH
- FACEBOOK_RATE_LIMIT
- FACEBOOK_POLICY_BLOCK
- FACEBOOK_LINK_INVALID
- FACEBOOK_LINK_BLOCKED
- FACEBOOK_PAYLOAD_INVALID
- FACEBOOK_API_TEMPORARY
- FACEBOOK_UNKNOWN_ERROR
- INTERNAL_ENV_MISSING
- INTERNAL_VALIDATION_FAILED
- INTERNAL_EXCEPTION

## Meta raw error preservation

For Meta HTTP failures, the client now preserves:

- error.message
- error.type
- error.code
- error.error_subcode
- error.fbtrace_id
- HTTP status

These are included in `error_context.meta_error` and in publish log response payload JSON.

Tokens are not stored. Request payloads only include token mask/fingerprint/status metadata.

## Token status snapshot

Publish failures now include a token status snapshot:

- token_type
- is_valid
- page_id_match
- required_scopes_present
- expires_at
- expires_in_seconds
- token_fingerprint
- validation_checked_at

`TOKEN_EXPIRING_SOON` is treated as a warning category, not as an invalid-token failure when `is_valid=true`.

## Publish log storage

`social_news.publish_log.response_payload` now receives structured JSON containing:

- error_category
- error_context
- meta_error
- token_status
- retryable_yn
- facebook_link_url
- link validation fields

No destructive migration was added. Existing JSON payload storage is used.

## Telegram notification

Failure notifications now include:

- Content ID
- Internal Status
- Error Category
- Meta Error block, or `not available`
- Internal Reason when no Meta error exists
- Token Status block
- Link
- Next Action guidance

This avoids collapsing every failure into a generic invalid token message.

## Retryable decision

Retryable true:

- FACEBOOK_API_TEMPORARY
- FACEBOOK_RATE_LIMIT

Retryable false:

- TOKEN_INVALID
- TOKEN_EXPIRED
- TOKEN_PERMISSION_MISSING
- TOKEN_WRONG_TYPE
- TOKEN_PAGE_MISMATCH
- FACEBOOK_LINK_BLOCKED
- INTERNAL_ENV_MISSING

Token and permission failures block only the candidate as `FAILED_PERMISSION`. They do not turn the bot off.

## Tests

Executed:

- `python -m py_compile ...`
- `python -m unittest foreign_worker_life_info_collector.tests.test_social_news_pipeline foreign_worker_life_info_collector.tests.test_facebook_error_normalizer foreign_worker_life_info_collector.tests.test_social_news_collectors`
- `npm run build`

Result:

- 19 Python tests passed.
- Admin UI build passed.

## Remaining issues

This change normalizes and preserves error causes. It does not refresh or replace Facebook tokens. If Meta returns token categories such as `TOKEN_EXPIRED` or `TOKEN_INVALID`, the operator still needs to verify the Page Access Token in Meta tooling.
