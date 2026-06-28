# Telegram Review Dedupe

Report date: 2026-06-16 KST

## 변경 이유

Content Review Telegram 알림이 같은 후보, 같은 링크, 같은 상태, 같은 점수대에서 반복 발송될 수 있었다.

기존 억제는 같은 `content_candidate_id`의 최근 6시간 `SENT` 또는 `DRY_RUN` 로그에만 의존했다. 따라서 같은 URL/본문이 다른 content id로 생성되면 다시 Telegram Review 대상이 될 수 있었다.

## 변경 범위

수정:

- `SRC/foreign_worker_life_info_collector/content/service.py`
- `SRC/foreign_worker_life_info_collector/content/repository.py`
- `SRC/foreign_worker_life_info_collector/api/admin_server.py`
- `SRC/foreign_worker_life_info_collector/tests/test_content_review_dedupe.py`

추가:

- `DOC/walkthrough/2026-06-16-telegram-review-dedupe.md`

DB migration:

- 없음

## Dedupe Key

저장 위치:

- `content.publish_log.request_payload` JSON

Primary key:

```text
telegram_review_key =
content_candidate_id + status + score_bucket + message_hash
```

Semantic key:

```text
semantic_review_key =
source_domain + content_type + canonical_url_or_title + status + score_bucket + message_hash
```

Score bucket:

```text
0-39
40-59
60-79
80-100
```

`message_hash`는 후보 id와 source_name을 제외하고 아래 기준으로 계산한다.

- title
- summary_en
- why_it_matters_en
- body_en
- review_reason
- normalized review URL
- duplicate signal bucket

의도:

- 같은 candidate/status/score/content는 suppress
- 같은 URL이 다른 content id로 들어와도 suppress
- source_name만 다른 같은 URL 반복은 suppress
- status, score bucket, content/review reason이 바뀌면 새 판단으로 간주

## 발송 조건

발송 가능:

- 기존 `telegram_review_key` 또는 `semantic_review_key`가 없음
- status가 바뀜
- score bucket이 바뀜
- title/summary/body/review_reason/review URL이 바뀜
- duplicate signal bucket이 바뀜
- 기존 전송이 `FAILED`였음

## Suppress 조건

Suppress:

- 같은 `telegram_review_key`가 이미 `SENT` 또는 `DRY_RUN`
- 같은 `semantic_review_key`가 이미 `SENT` 또는 `DRY_RUN`
- 같은 key가 이미 `REVIEW_SUPPRESSED_DUPLICATE`
- 같은 key가 이미 `REVIEW_SUPPRESSED_LOW_VALUE`
- migration 이전 로그 호환용으로 같은 `content_candidate_id + message_preview`가 최근 6시간 내 존재

Suppress status:

- `REVIEW_SUPPRESSED_DUPLICATE`
- `REVIEW_SUPPRESSED_LOW_VALUE`

Suppress 시:

- Telegram API 호출 안 함
- `content.publish_log`에 suppress metadata 저장
- 이미 suppress log가 있으면 추가 log를 반복 생성하지 않고 기존 log id 반환

## 구현 내용

`content.service`:

- `build_telegram_review_metadata()`
- `score_bucket()`
- `normalize_review_url()`
- `review_message_hash()`
- `duplicate_signal_bucket()`
- `telegram_review_metadata()` service method

`content.repository`:

- `find_duplicate_telegram_review()`
- `record_telegram_review(..., metadata=...)`

`api.admin_server`:

- `send_content_review_to_telegram()`에서 Telegram API 호출 전 dedupe check 수행
- suppress 결과는 `REVIEW_SUPPRESSED_*`로 반환
- content generation cycle 결과에 `telegram.suppressed` count 추가

## 테스트 결과

실행:

```text
python -m py_compile SRC/foreign_worker_life_info_collector/content/service.py SRC/foreign_worker_life_info_collector/content/repository.py SRC/foreign_worker_life_info_collector/api/admin_server.py SRC/foreign_worker_life_info_collector/tests/test_content_review_dedupe.py
```

결과:

```text
OK
```

실행:

```text
python -m unittest foreign_worker_life_info_collector.tests.test_content_review_dedupe
```

결과:

```text
Ran 7 tests in 0.001s
OK
```

검증한 케이스:

- same candidate + same state -> same review key
- same candidate + status changed -> different review key
- score bucket changed -> different review key
- same URL + different candidate/source_name -> same semantic key
- content body changed -> different semantic key
- tracking query/fragment URL normalization

## 보호 영역 미수정 확인

수정하지 않음:

- FacebookPublisher
- Facebook token validation
- scheduler interval/cooldown/daily cap
- admin auth
- raw token/env
- destructive migration
- content publish selection

## 남은 TODO

- 실제 PostgreSQL 데이터로 최근 `content.publish_log` key 분포 확인
- 운영 화면에서 `REVIEW_SUPPRESSED_*` count 표시 개선
- 필요 시 non-destructive migration으로 `last_review_key`, `review_sent_at`, `last_suppressed_at` 컬럼 승격
- duplicate signal source count를 first-class column으로 승격 후 threshold 변경 알림 정교화

## Commit/Push

수행하지 않음.

이유:

- 현재 working tree에는 이전 작업으로 생긴 runtime 변경이 같은 파일들에 이미 포함되어 있다.
- 이번 task 변경만 안전하게 분리 stage하기 어렵기 때문에 unrelated/pre-existing 변경까지 같이 commit하지 않기 위해 보류했다.
