# Correction Loop: LIVING_INFO Topic-Based Card Audit Persistence

## Purpose

This correction-loop entry records two findings:

1. The `LIVING_INFO Topic-Based Card Generation` audit found a recurring product/architecture risk.
2. The audit report was initially returned only in chat and was not persisted to the harness storage locations.

This file is correction-loop material only. It does not approve implementation, DB changes, scheduler changes, publisher changes, Telegram runtime changes, auth changes, env/config changes, or external API behavior changes.

## Failed Layer

- verification/reporting
- work-area boundary
- domain classification
- review eligibility
- public delivery

## Missing Harness Behavior

When a walkthrough-based audit is completed, Codex must not stop at chat output.

The result should be persisted to:

- `DOC/walkthrough/execution-history/YYYY-MM-DD/`
- `DOC/walkthrough/YYYY-MM-DD - execute prompt.md` same-day record when the task allows it
- `DOC/correction-loop/` when the result describes recurring failure patterns or reusable harness improvements

## Recurring Product Risk

The current `LIVING_INFO / LIVING_GUIDE` path can still treat a single news article as a card-worthy content candidate.

This risks producing WorkConnect public content that is really just a repackaged article rather than source-backed, topic-based settlement guidance.

## Audit Report Stored

The full audit result was stored in:

```text
DOC/walkthrough/execution-history/2026-06-20/living-info-topic-card-read-only-audit-report.md
```

## Audit Summary

현재 구조는 `LIVING_INFO / LIVING_GUIDE`를 만들 수는 있지만, 아직 "뉴스 기사 1건 -> 카드 콘텐츠 1건"으로 흐를 수 있는 구조다.

사용자가 요구한 방향인:

- 뉴스/블로그/커뮤니티 원문은 `source_signal`
- 생활정보 public content는 `topic_key` 기반으로 여러 근거를 조합
- 카드에는 3개의 검증된 정보 포인트만 표시
- 단일 기사 제목/출처/URL 반복 카드 방지

이 구조는 아직 완성되어 있지 않다.

## Key Findings

1. `ContentService.social_news_payload()`에서 `social_news.candidate`가 living category로 분류되면 `source_domain = LIVING_INFO`, `content_type = LIVING_GUIDE`로 변환된다.
2. `is_living_content()` 범위가 넓어 `travel`, `lifestyle`, `culture`, `local_events`, `safety`, `SECONDARY`, `TERTIARY`가 생활정보로 들어올 수 있다.
3. `build_content_card_payload()`는 `summary_en`, `body_en`, `why_it_matters_en`에서 bullet을 만들지만 title/source/url echo validation이 부족하다.
4. runtime renderer는 bullet 1개만 있어도 카드 생성을 허용한다.
5. Telegram review 중복 억제는 있으나, 단일 기사 기반 생활정보 카드 생성 자체를 막지는 않는다.
6. `topic_key`, `fact_point`, `card_point`, `usable_for_card`, `content_fingerprint`, `card_point_hash`가 없다.

## Recommended Promotion

Promote the following as separate future tasks only after human approval.

```text
AREA: LIVING_DOMAIN + CONTENT_CARD_GENERATION
MODE: GUARDED_FIX
PURPOSE FUNCTION:
Prevent single news articles from becoming public LIVING_INFO card candidates.
FOCUS:
Block one-article LIVING_INFO / LIVING_GUIDE CARD_IMAGE candidate generation unless it is source-backed structured information.
RISK: MEDIUM
```

```text
AREA: CONTENT_CARD_GENERATION
MODE: GUARDED_FIX
PURPOSE FUNCTION:
Make WorkConnect card payloads useful and non-repetitive.
FOCUS:
Add CARD_POINT_TITLE_ECHO, source echo, URL echo, and minimum point count validation.
RISK: LOW
```

```text
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Design topic_key / fact_point / card_point ownership before DB changes.
FOCUS:
Map whether topic and fact extraction belongs in social_news, content, or a new living-domain layer.
RISK: LOW
```

## Protected Areas Not Touched

- DB/migration
- Facebook publisher
- content publisher
- scheduler
- Telegram callback/runtime behavior
- auth/env/config
- external API
- actual collection
- actual publishing

## Correction

The missed persistence step has been corrected by storing the audit report in `execution-history` and recording this reusable failure pattern in `correction-loop`.

Future Codex runs should treat chat-only audit output as incomplete when the execute prompt or harness rule requires persistent report storage.
