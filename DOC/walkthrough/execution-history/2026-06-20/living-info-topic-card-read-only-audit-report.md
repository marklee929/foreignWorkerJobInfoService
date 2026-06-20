# READ_ONLY_AUDIT REPORT: LIVING_INFO Topic-Based Card Generation

## 1. Pre-Review

- AREA: `LIVING_DOMAIN + SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE + CONTENT_CARD_GENERATION`
- MODE: `READ_ONLY_AUDIT`
- Risk: MEDIUM
- Protected areas touched: NO
- Files inspected:
  - `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  - `DOC/walkthrough/2026-06-20 - execute prompt.md`
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/content/repository.py`
  - `SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py`
  - `SRC/foreign_worker_life_info_collector/api/admin_server.py`
  - `SRC/foreign_worker_life_info_collector/social/news/category_rotation.py`
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_07_content_candidate.sql`
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/admin_postgres_schema.sql`

## 2. Current Pipeline Summary

현재 흐름은 아래처럼 연결된다.

```text
social_news.raw_item
-> social_news.normalized_item
-> social_news.candidate
-> ContentService.sync_social_news()
-> content.content_candidate
-> Telegram Review
-> card preview generation
-> manual score / approve
-> publish candidate
```

현재 구조는 `LIVING_INFO / LIVING_GUIDE`를 만들 수는 있지만, 아직 "뉴스 기사 1건 -> 카드 콘텐츠 1건"으로 흐를 수 있는 구조다.

사용자가 요구한 방향인 "뉴스/블로그/커뮤니티 원문은 source_signal, 생활정보 public content는 topic_key 기반 조합 카드" 구조는 아직 완성되어 있지 않다.

## 3. Current Data Model

현재 있는 것:

- `source_url`
- `canonical_url` 일부
- `source_name`
- `source_domain`
- `content_type`
- `category`
- `priority_group`
- `quality_score`
- `practical_value_score`
- `hash_key`
- `title_hash`
- `similarity_key`
- `duplicate_group_id`
- `publish_log`

현재 부족한 것:

- `topic_key`
- `target_user`
- `action_type`
- `trust_level`
- `actionability_score`
- `fact_point`
- `card_point`
- `usable_for_card`
- `content_fingerprint`
- `card_point_hash`
- `topic_cluster_id`
- `source_spread_count`
- `template_type + topic_key` 기준 최근 게시 중복 방지

따라서 현재는 "생활정보 주제 카드"라기보다 "생활정보로 분류된 기사 카드"에 가깝다.

## 4. Where News Becomes Content

주요 변환 지점은 `ContentService.social_news_payload()`다.

현재 `social_news.candidate`가 `housing`, `banking`, `healthcare`, `transportation`, `insurance`, `settlement_life` 등으로 분류되면 아래처럼 변환된다.

```text
source_domain = LIVING_INFO
content_type = LIVING_GUIDE
```

문제는 `is_living_content()` 범위가 넓다는 점이다.

현재 `travel`, `lifestyle`, `culture`, `local_events`, `safety`, `SECONDARY`, `TERTIARY`까지 생활정보로 들어올 수 있다. 그래서 단일 뉴스 기사도 `LIVING_GUIDE`가 되고, 이후 카드 생성 대상이 될 수 있다.

`ContentRepository.list_review_targets()`는 `LIVING_INFO`, `IMMIGRATION_INFO`를 Telegram Review 대상으로 조회한다.

`ContentService.requires_telegram_review()`는 `content_quality_gate(candidate).review_eligible`를 추가 확인한다.

`send_content_review_to_telegram()`은 카드 preview 대상이면 `telegram_review_card_preview()`를 통해 image path를 만들고, image가 있으면 Telegram `sendPhoto` 경로로 보낼 수 있다.

## 5. Card Generation Input Mapping

현재 `build_content_card_payload()`는 다음 값을 사용한다.

```text
title <- card_title / title / original_title
subtitle <- card_subtitle / why_it_matters_en / summary_en
bullets <- card_bullets 또는 summary_en/body_en/why_it_matters_en 문장
source <- source_name / original_source_name
date <- original_published_at / original_collected_at / created_at / updated_at
footer_url <- footer_url / WORKCONNECT_CONTENT_CARD_FOOTER_URL / DEFAULT_FOOTER_URL
```

발생 가능한 문제:

- 제목이 카드 내용으로 반복될 수 있음
- 출처명이 bullet 안에 섞일 수 있음
- URL 또는 운영 문구가 들어올 위험이 있음
- runtime renderer는 bullet 1개만 있어도 카드 생성 가능
- 3-slot 템플릿인데 1개 포인트만 채워질 수 있음
- runtime renderer 기본 footer가 Facebook profile URL임

로컬 LLaMA util은 bullet 개수 검증이 더 엄격하지만, 실제 runtime renderer는 아직 느슨하다.

## 6. Duplicate / Idempotency Review

이미 일부 Telegram 중복 억제는 있다.

`content.publish_log` 기준으로 아래를 확인한다.

- `telegram_review_key`
- `semantic_review_key`
- `content_candidate_id + message_preview`
- 6시간 window

하지만 이것은 Telegram 반복 발송 억제이고, "단일 기사 기반 생활정보 카드 생성 자체"를 막는 구조는 아니다.

현재 부족한 중복 방지:

- same `topic_key`
- same `content_fingerprint`
- same `card_point_hash`
- same `template_type + topic_key` recent published
- source overlap / point overlap 기반 skip
- publish 직전 `READY -> PUBLISHING` 원자 claim 확인은 추가 감사 필요

## 7. Feasibility of Topic Cluster SELECT

현재 DB만으로는 제한적으로 가능하다.

`category`, `similarity_key`, `source_url`, `source_name`, `quality_score`, `practical_value_score`를 이용해 임시 topic cluster를 만들 수는 있다.

개념 SELECT 초안:

```sql
SELECT
    c.category AS topic_key_surrogate,
    COUNT(*) AS candidate_count,
    COUNT(DISTINCT COALESCE(NULLIF(c.original_source_url, ''), c.source_url)) AS source_count,
    AVG(c.quality_score) AS avg_quality_score,
    AVG(c.practical_value_score) AS avg_practical_value_score,
    MAX(c.updated_at) AS last_seen_at
FROM content.content_candidate c
WHERE c.source_domain = 'LIVING_INFO'
  AND c.content_type = 'LIVING_GUIDE'
  AND c.status NOT IN ('ARCHIVED', 'POSTED')
  AND c.created_at >= CURRENT_TIMESTAMP - INTERVAL '90 days'
GROUP BY c.category
HAVING COUNT(DISTINCT COALESCE(NULLIF(c.original_source_url, ''), c.source_url)) >= 2
   AND AVG(c.practical_value_score) >= 40;
```

이 쿼리는 실행하지 않았다. 실제 운영용으로는 `topic_key`, `fact_point`, `usable_for_card`, `content_fingerprint`가 필요하다.

## 8. Gap Analysis

현재 구조에서 부족한 항목:

- `topic_key` 없음
- `fact_point` 없음
- `card_point` 없음
- `usable_for_card` 없음
- `title echo` validation 없음
- `source echo` validation 없음
- `url echo` validation 없음
- runtime renderer의 최소 point count 검증 부족
- source URL과 Facebook page/profile URL 역할 분리 부족
- 생활정보 뉴스 단독 발행 차단 부족
- 과거 발행 fingerprint 부족
- `social_news.candidate`와 `content.content_candidate` ownership 경계가 불명확함

## 9. Recommended Future Implementation Plan

Phase 1:

- AREA: `LIVING_DOMAIN + CONTENT_QUEUE + CONTENT_CARD_GENERATION`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM
- 예상 수정 파일: `content/service.py`, `utils/content_card_renderer.py`
- DB migration 필요 여부: NO
- protected area 포함 여부: NO
- verification plan: 단일 `NEWS_ARTICLE` 기반 `LIVING_INFO` 카드 생성 차단 테스트

Phase 2:

- AREA: `CONTENT_CARD_GENERATION`
- MODE: `GUARDED_FIX`
- Risk: LOW
- 예상 수정 파일: `utils/content_card_renderer.py`
- DB migration 필요 여부: NO
- protected area 포함 여부: NO
- verification plan: title/source/url echo, minimum point count validation 테스트

Phase 3:

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY`
- MODE: `READ_ONLY_AUDIT`
- Risk: LOW
- 예상 수정 파일: 문서 또는 후속 migration 후보
- DB migration 필요 여부: 설계 후 판단
- protected area 포함 여부: NO
- verification plan: `topic_key`, `fact_point`, `card_point` 모델 검토

Phase 4:

- AREA: `CONTENT_QUEUE + DATA_SOURCE_QUALITY`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM
- 예상 수정 파일: repository query, admin read-only API
- DB migration 필요 여부: NO 또는 후속
- protected area 포함 여부: NO
- verification plan: topic cluster SELECT dry-run

Phase 5:

- AREA: `CONTENT_QUEUE`
- MODE: `READ_ONLY_AUDIT` 후 `GUARDED_FIX`
- Risk: MEDIUM
- 예상 수정 파일: repository, quality gate
- DB migration 필요 여부: 가능성 있음
- protected area 포함 여부: publisher 직접 변경 금지
- verification plan: same topic/template duplicate suppression 테스트

Phase 6:

- AREA: `TELEGRAM_REPORTING + CONTENT_CARD_GENERATION`
- MODE: `GUARDED_FIX`
- Risk: MEDIUM
- 예상 수정 파일: Telegram review message builder, card preview path
- DB migration 필요 여부: NO
- protected area 포함 여부: Telegram callback 변경 금지
- verification plan: dry-run image preview only, 실제 발송 금지

## 10. CODE_TASK_CANDIDATE

```text
AREA: LIVING_DOMAIN + CONTENT_CARD_GENERATION
MODE: GUARDED_FIX
PURPOSE FUNCTION:
Prevent single news articles from becoming public LIVING_INFO card candidates.
FOCUS:
Block one-article LIVING_INFO / LIVING_GUIDE CARD_IMAGE candidate generation unless it is source-backed structured information.
RISK: MEDIUM
ALLOWED FILES:
content/service.py
utils/content_card_renderer.py
FORBIDDEN:
FacebookPublisher, scheduler, auth/env/config, DB migration, Telegram callback
VERIFICATION:
single NEWS_ARTICLE living candidate -> no card
source-backed structured living info -> card allowed
STOP CONDITIONS:
Requires content publisher or Facebook publisher changes
```

```text
AREA: CONTENT_CARD_GENERATION
MODE: GUARDED_FIX
PURPOSE FUNCTION:
Make WorkConnect card payloads useful and non-repetitive.
FOCUS:
Add CARD_POINT_TITLE_ECHO, source echo, URL echo, and minimum point count validation.
RISK: LOW
ALLOWED FILES:
utils/content_card_renderer.py
FORBIDDEN:
FacebookPublisher, scheduler, auth/env/config, DB migration
VERIFICATION:
title-only card fails
source-only bullet fails
URL-like bullet fails
3 valid bullets pass
STOP CONDITIONS:
Requires template PNG edits or external image generation
```

```text
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Design topic_key / fact_point / card_point ownership before DB changes.
FOCUS:
Map whether topic and fact extraction belongs in social_news, content, or a new living-domain layer.
RISK: LOW
ALLOWED FILES:
DOC only
FORBIDDEN:
DB mutation, migration, scheduler, publisher, external API
VERIFICATION:
ownership matrix and migration impact analysis
STOP CONDITIONS:
Ownership cannot be decided without human product decision
```

```text
AREA: CONTENT_QUEUE + DATA_SOURCE_QUALITY
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Draft topic cluster SELECT for source-backed living cards.
FOCUS:
Use current DB to identify topic candidates without writing data.
RISK: LOW
ALLOWED FILES:
DOC or read-only SQL sample
FORBIDDEN:
DB write, migration, scheduler, publisher
VERIFICATION:
SELECT is read-only and runnable against PostgreSQL
STOP CONDITIONS:
Requires schema change before useful result
```

```text
AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Define duplicate/fingerprint policy for topic cards.
FOCUS:
Review same topic_key + template_type + recent published suppression.
RISK: MEDIUM
ALLOWED FILES:
DOC only
FORBIDDEN:
Publisher changes, scheduler changes, DB mutation
VERIFICATION:
candidate duplicate scenarios documented
STOP CONDITIONS:
Requires destructive migration or publisher rewrite
```

## 11. Stop Conditions Encountered

- `DOC/walkthrough/2026-06-20 - execute prompt.md`에 completion marker 문자열이 여러 번 있어 PHASED_EXECUTION은 실행하지 않는 것이 맞다.
- `CONTENT_PUBLISHER`와 `FACEBOOK_PUBLISHER` 경로는 보호 영역이므로 수정하지 않았다.
- `social_news.candidate`와 `content.content_candidate` ownership 경계가 불명확해 코드 변경을 하지 않았다.
- `topic_key`, `fact_point`, `content_fingerprint`는 DB schema 영향이 있으므로 이번 감사에서 구현하지 않았다.

## 12. Final Recommendation

현재 구조에서 생활정보 프레임을 "기사 발행형"에서 "구조화된 topic card 생성형"으로 전환하는 것은 가능하다.

가장 안전한 첫 구현은 DB 변경 없이 다음 두 가지다.

1. `LIVING_INFO / LIVING_GUIDE` 단일 뉴스 기사 기반 `CARD_IMAGE/public candidate` 차단
2. runtime card payload validation 강화

그 다음에 `topic_key`, `fact_point`, `card_point`, `content_fingerprint` 저장 구조를 별도 `READ_ONLY_AUDIT`로 설계하는 것이 맞다.

## 13. 재시작 / 재로딩 필요 여부

- Backend restart: NO
  - 이유: 이번 작업은 read-only audit 보고서 저장이며 runtime code를 수정하지 않았다.

- Frontend dev server restart: NO
  - 이유: Admin UI code를 수정하지 않았다.

- Browser hard refresh: NO
  - 이유: UI 반영 대상이 없다.

- DB restart: NO
  - 이유: DB schema/migration 변경이 없다.

- Scheduler/Bot restart: NO
  - 이유: scheduler, publisher, bot runtime behavior를 수정하지 않았다.

- External service restart: NO
  - 이유: 외부 API, Telegram 실제 전송, Facebook 게시를 실행하지 않았다.
