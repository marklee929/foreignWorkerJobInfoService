# READ_ONLY_AUDIT REPORT: WorkConnect Duplicate Review/Publish Pipeline

## 1. Pre-Review

* AREA: `SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE + TELEGRAM_REPORTING + CONTENT_PUBLISHER`
* MODE: `READ_ONLY_AUDIT`
* Risk: `MEDIUM`
  * 중복 억제 자체는 이미 일부 존재하지만, Telegram review와 Facebook publish가 서로 다른 identity 기준을 사용한다.
  * Facebook publish path에는 원자적 `READY -> PUBLISHING` claim이 보이지 않아 race-condition 가능성이 있다.
  * 출입국/공지형 attachment notice는 URL 기준으로는 중복이 아니지만 운영자 관점에서는 semantic/attachment duplicate처럼 보일 수 있다.
* Protected areas touched: 없음
  * 코드 수정 없음
  * DB write 없음
  * migration 없음
  * scheduler 변경 없음
  * Facebook publisher 변경 없음
  * Telegram runtime/callback 변경 없음
  * auth/env/config 변경 없음
  * 외부 API 호출 없음
  * 실제 Telegram/Facebook 발송 없음
* Files inspected:
  * `CODEX_BOOTSTRAP.md`
  * `DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md`
  * `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
  * `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
  * `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  * `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  * `DOC/correction-loop/2026-06-20_WALKTHROUGH_CLOSEOUT_MARKER_FAILURE.md`
  * `DOC/correction-loop/2026-06-20_LIVING_INFO_TOPIC_CARD_AUDIT.md`
  * `DOC/walkthrough/2026-06-21 - execute prompt.md`
  * `SRC/foreign_worker_life_info_collector/content/repository.py`
  * `SRC/foreign_worker_life_info_collector/content/service.py`
  * `SRC/foreign_worker_life_info_collector/api/admin_server.py`
  * `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py`
  * `SRC/foreign_worker_life_info_collector/social/news/pipeline.py`
  * `SRC/foreign_worker_life_info_collector/social/news/normalizer/news_normalizer.py`
  * `SRC/foreign_worker_life_info_collector/social/news/duplicate_guard/duplicate_detector.py`
  * `SRC/foreign_worker_life_info_collector/social/news/publisher/facebook_publisher.py`
  * `SRC/foreign_worker_life_info_collector/immigration/repository.py`
  * `SRC/foreign_worker_life_info_collector/immigration/normalizer.py`
  * `SRC/foreign_worker_life_info_collector/immigration/collectors.py`
  * `SRC/foreign_worker_life_info_collector/storage/db/migrations/admin_postgres_schema.sql`
  * `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_06_immigration_info.sql`
  * `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_07_content_candidate.sql`

## 2. Duplicate Cases Observed

### Case A: ChosunBiz article Facebook duplicate

관찰: 동일 title/source/link/category/score로 보이는 ChosunBiz article이 서로 다른 Facebook post ID로 두 번 게시됨.

분류:

* `Facebook duplicate`
* `same source URL duplicate` 가능성
* `race-condition candidate` 가능성
* `same candidate published twice` 또는 `same URL represented by multiple candidate_id` 둘 다 가능

현재 코드상 가능한 원인:

* `social_news.candidate`는 `published_at IS NULL`, `facebook_post_url = ''`, `is_representative = TRUE` 조건으로 publish 후보를 조회한다.
* publish 직전 candidate를 `PUBLISHING` 같은 점유 상태로 원자적으로 전환하는 코드가 보이지 않는다.
* `auto_publish()`는 `last_publish_attempt_at`, `publish_attempt_count`를 먼저 업데이트하지만, 다른 프로세스/루프가 같은 READY 후보를 읽지 못하게 막지는 않는다.
* `social_news.publish_log`에는 같은 `news_candidate_id`, `external_post_id`, URL, message fingerprint에 대한 unique/idempotency constraint가 없다.

### Case B: MOEL attachment notice Telegram duplicate

관찰: `IMMIGRATION_INFO / IMMIGRATION_NOTICE` 후보가 Telegram review로 반복 전송됨. 링크는 `bbs_seq=19542`, `bbs_seq=19543`처럼 다르고 preview text는 거의 동일한 attachment-only text로 보임.

분류:

* `semantic preview duplicate`
* `same official notice with multiple attachments` 가능성
* `attachment duplicate`
* URL 기준으로는 `exact duplicate`가 아님

현재 코드상 가능한 원인:

* `immigration_info.official_notice`는 `UNIQUE (canonical_url)`만 가진다.
* `canonical_url()`은 fragment 제거 외에 board parameter grouping을 하지 않는다.
* `bbs_seq`가 다르면 각각 다른 `canonical_url`이므로 다른 official notice row가 된다.
* `content.content_candidate`는 `raw_ref_table/raw_ref_id` 기준으로만 unique라서 서로 다른 notice row는 서로 다른 content candidate가 된다.
* Telegram `semantic_review_key`는 URL이 있으면 URL을 우선 사용한다. 따라서 `bbs_seq`가 다르면 semantic key도 달라져 suppression을 우회한다.

## 3. Current Pipeline Duplicate Map

### collector/raw source

현재 키/체크:

* `social_news.raw_item.hash_key`
  * 실제 저장 시 `occurrence_hash = stable_hash(f"{source_hash}:{collected_at}:{runtime_cycle_id}:{source_type}")`
  * occurrence 단위라서 같은 기사라도 collection time/cycle이 달라지면 raw row는 계속 생성된다.
* `social_news.raw_item.source_hash`
  * 같은 `candidate.hash_key` 기반 중복 여부를 `is_duplicate`, `duplicate_reason = SOURCE_HASH_DUPLICATE`로 표시한다.
* `immigration_info.official_notice.canonical_url`
  * `UNIQUE (canonical_url)`로 같은 official URL exact duplicate는 upsert 처리된다.

부족한 점:

* raw source layer에는 source-specific semantic key가 없다.
* MOEL/Hikorea/MOJ board article의 `bbs_seq`, `artclSeq`, attachment list, attachment filenames/sizes를 grouping하는 별도 key가 없다.
* 같은 board notice의 attachment-only preview를 대표 notice 하나로 묶는 정책이 없다.

### normalized candidate

현재 키/체크:

* `social_news.normalized_item.hash_key`
  * `ux_news_normalized_hash` unique index.
  * `normalize_news_item()`에서 `hash_key = stable_hash(source_url or google_news_url or similarity_key)`.
* `social_news.candidate.normalized_item_id`
  * 같은 normalized item에 대해 대표 candidate가 있으면 기존 대표를 재사용하고 duplicate counters만 갱신한다.
* `social_news.candidate.duplicate_group_id`
* `social_news.candidate.related_source_count`
* `social_news.candidate.duplicate_count`
* `social_news.candidate.group_item_count`
* `social_news.candidate.last_seen_at`
* `social_news.candidate.is_representative`
* `duplicate_detector.check_duplicate()`
  * same `source_url`
  * same `hash_key`
  * title similarity
  * title + body similarity
  * same-day keyword event

부족한 점:

* `duplicate_detector.check_duplicate()`는 pipeline processing 보조 로직이고 DB-level unique/idempotency는 아니다.
* `hash_key`가 `source_url` 우선이므로 같은 기사라도 resolved URL/canonical URL이 달라지면 다른 normalized item이 될 수 있다.
* `social_news.candidate`에는 `canonical_url` 컬럼과 index는 있지만 canonical URL unique constraint는 없다.
* `title_hash`는 schema에 있으나 현재 저장 로직에서 `candidate.hash_key`와 같게 들어가는 구조가 보여 title-only duplicate key로 분리되어 있지 않다.

### content queue

현재 키/체크:

* `content.content_candidate`
  * `CONSTRAINT ux_content_candidate_raw_ref UNIQUE(raw_ref_table, raw_ref_id)`
* `ContentRepository.upsert_candidate()`
  * same `raw_ref_table/raw_ref_id`면 같은 content candidate 업데이트.
* `ContentService.sync_social_news()`
  * `COALESCE(is_representative, TRUE) = TRUE`
  * `ARCHIVED`, `DUPLICATE_SKIPPED`, `DUPLICATE`, `SKIPPED`, `TEXT_INVALID` 제외.
* `ContentRepository.archive_non_representative_social_news()`
  * non-representative social news는 content queue에서 archive 가능.

부족한 점:

* content queue에는 `source_url`, `link_url`, `title`, `source_name`, content fingerprint 기반 unique key가 없다.
* 같은 URL/제목이 다른 raw row에서 오면 `raw_ref_table/raw_ref_id`가 달라져 새 `content_candidate_id`를 받을 수 있다.
* content queue는 `raw_payload.duplicate_group_id`를 보존하지만, Telegram/Facebook selection의 강한 gate로 쓰지는 않는다.

### Telegram review

현재 키/체크:

* `TELEGRAM_REVIEW_SOURCE_DOMAINS = {"LIVING_INFO", "IMMIGRATION_INFO"}`
* `ContentService.requires_telegram_review()`
  * source domain이 review 대상이고 `content_quality_gate().review_eligible`이어야 함.
* `ContentRepository.list_review_targets()`
  * `status IN ('SCORED','READY_TO_REVIEW','READY_TO_PUBLISH','FAILED_RETRYABLE')`
  * `source_domain IN ('LIVING_INFO','IMMIGRATION_INFO')`
  * 같은 `content_candidate_id`의 `SENT`/`DRY_RUN` log가 최근 6시간 있으면 제외.
* `build_telegram_review_metadata()`
  * `telegram_review_key = content_candidate_id|status|score_bucket|message_hash`
  * `semantic_review_key = source_domain|content_type|canonical_url_or_title|status|score_bucket|message_hash`
* `ContentRepository.find_duplicate_telegram_review()`
  * same `telegram_review_key`
  * same `semantic_review_key`
  * same `content_candidate_id + message_preview` within 6 hours

부족한 점:

* suppression window가 6시간으로 제한되어 있어 같은 notice가 오전/오후에 다시 올라올 수 있다.
* semantic key가 URL 우선이라 `bbs_seq`가 다른 attachment-only official notice는 서로 다른 semantic key가 된다.
* `message_hash`에 `review_url`이 포함된다. URL만 다르고 preview/title/body가 같은 경우도 다른 hash가 될 수 있다.
* `review_sent_at`, `last_review_key`, `review_sent_count`, `last_suppressed_at` 같은 candidate-level persistent review state는 없다.
* attachment filename/size/content signature는 key에 포함되지 않는다.

### Facebook publish

현재 키/체크:

* `social_news.repository.list_publish_candidates_*()`
  * `publish_status`/`status`
  * `published_at IS NULL`
  * `facebook_post_url = ''`
  * `is_representative = TRUE`
  * excluded statuses
* `SocialNewsPipeline.auto_publish()`
  * `last_publish_attempt_at`, `publish_attempt_count` 업데이트
  * `FacebookPublisher.publish()`
  * 이후 성공 시 `status = POSTED` 또는 `DRY_RUN_PUBLISHED`
* `FacebookPublisher.facebook_link_url()`
  * publish link validation.
* `content.ContentService.publish()`
  * content candidate publish path는 quality gate와 link/message validation 후 publish.

부족한 점:

* publish 직전 same `source_url`/`canonical_url`/`title+source`/content fingerprint already-published check가 보이지 않는다.
* `READY_TO_PUBLISH -> PUBLISHING` 원자적 claim이 보이지 않는다.
* `social_news.publish_log`와 `content.publish_log`에 idempotency unique key가 없다.
* 같은 candidate가 두 프로세스에서 동시에 선택되면 둘 다 Facebook API를 호출할 수 있는 구조다.

## 4. Where Duplicate Identity Is Lost

1. `social_news.raw_item` 저장 시
   * `occurrence_hash`가 collection occurrence 기준이다.
   * raw row 반복 저장은 의도된 동작일 수 있으나, 이후 대표 후보로 수렴해야 한다.

2. `normalize_news_item()`에서 URL 변동 시
   * `hash_key = stable_hash(source_url or google_news_url or similarity_key)` 구조다.
   * source URL resolver 결과가 달라지거나 canonical URL이 다르면 동일 기사도 다른 normalized item이 될 수 있다.

3. `content.content_candidate` 생성 시
   * unique 기준이 `raw_ref_table/raw_ref_id`뿐이다.
   * 같은 source URL 또는 canonical URL duplicate를 content queue 레벨에서 막지 않는다.

4. Telegram semantic review key 생성 시
   * URL이 있으면 title보다 URL을 우선한다.
   * `bbs_seq`처럼 board item id가 다르면 preview/title/body가 같아도 semantic key가 달라진다.

5. Facebook publish selection 시
   * publish 후보 조회 후 publish API 호출 전까지 동일 후보를 점유하는 상태가 없다.
   * 이미 publish된 같은 URL/title/source를 다시 확인하는 pre-publish idempotency guard가 없다.

## 5. Telegram Review Duplicate Audit

`telegram_review_key`는 candidate-specific key다.

```text
content_candidate_id + status + score_bucket + message_hash
```

장점:

* 같은 후보가 같은 상태/점수대/메시지로 반복 전송되는 것은 억제 가능하다.

한계:

* `content_candidate_id`가 달라지면 같은 링크/제목이어도 key가 달라진다.
* status나 score bucket이 바뀌면 재발송 가능하다.

`semantic_review_key`는 source/category/URL-or-title 기반 key다.

```text
source_domain + content_type + canonical_url_or_title + status + score_bucket + message_hash
```

장점:

* candidate_id가 달라도 같은 URL이면 중복 억제가 가능하다.

한계:

* `canonical_url_or_title`에서 URL이 우선된다.
* `bbs_seq=19542`와 `bbs_seq=19543`은 다른 semantic identity가 된다.
* `message_hash`에도 URL이 포함되어 URL만 다른 attachment-only preview가 다른 hash로 처리될 수 있다.
* 최근 6시간 log만 candidate-level initial query에서 제외되고, semantic duplicate query도 log 기반이다. 장기 suppression 정책은 없다.

`content_candidate_id + message_preview` fallback은 동일 candidate에만 작동한다.

따라서 Case B처럼 서로 다른 official notice row, 서로 다른 content candidate, 서로 다른 `bbs_seq`, 유사 preview text인 경우는 반복 Telegram review가 발생할 수 있다.

## 6. Facebook Publish Idempotency Audit

현재 Facebook publish path는 candidate 상태와 publish log를 업데이트하지만, publish API 호출 전 idempotency guard가 부족하다.

확인된 구조:

* `list_publish_candidates_for_cycle()`와 `list_publish_candidates_since()`는 `published_at IS NULL` 및 `facebook_post_url = ''` 조건으로 후보를 가져온다.
* `auto_publish()`는 후보를 받은 뒤 `last_publish_attempt_at`, `publish_attempt_count`를 업데이트한다.
* 그 다음 `facebook_publisher.publish()`를 호출한다.
* 성공 후에야 `mark_status(..., published_at=timestamp, facebook_post_url=..., facebook_post_id=...)`가 실행된다.

위험:

* 두 루프 또는 manual/admin trigger가 같은 READY 후보를 거의 동시에 읽으면 둘 다 API 호출까지 갈 수 있다.
* `publish_attempt_count` 업데이트는 원자적 claim이 아니다.
* 같은 `source_url`/`canonical_url`/`title+source`가 이미 성공 게시되었는지 publish 직전에 재확인하지 않는다.
* `social_news.publish_log`에는 `news_candidate_id`, `external_post_id`, `message_preview`, `request_payload.link`에 대한 unique guard가 없다.

결론:

* Case A는 race condition 또는 identity split 둘 다 가능하다.
* 가장 먼저 필요한 것은 read-only duplicate diagnostics이고, 그 다음은 pre-publish idempotency guard 및 atomic claim이다.

## 7. Attachment Notice Grouping Audit

현재 official notice 수집 구조:

* `OfficialNoticeCollector`는 list page의 `<a>` link/title을 수집한다.
* detail URL pattern은 source별로 `artclView.do`, `BoardNtcDetailR.pt`, `noticeDetail.do`, `view.do`, `bbs_seq=`, `news_seq=`를 사용한다.
* `normalize_notice_item()`은 `canonical_url(item.url)`을 사용한다.
* `canonical_url()`은 fragment 제거만 수행한다.
* `immigration_info.official_notice`는 `UNIQUE (canonical_url)`이다.

따라서:

* 같은 `canonical_url`은 update only다.
* 다른 `bbs_seq`는 다른 notice다.
* attachment filename/size/count, parent board id, source board type, title normalized key로 grouping하지 않는다.
* `downloadAllZip.do` 같은 attachment download URL이 content URL로 들어올 경우, 원문 notice identity와 attachment identity가 섞일 위험이 있다.
* attachment-only preview text가 `첨부파일 있음` 수준이면 public/review value가 낮으므로 대표 official notice에 묶거나 `ATTACHMENT_ONLY_REVIEW_SUPPRESSED` 같은 reason으로 낮추는 정책이 필요하다.

운영 정책 제안:

* official board article 자체는 `official_notice_key`로 대표 candidate 하나만 만든다.
* attachments는 child evidence로 보관한다.
* 여러 ZIP/PDF가 같은 notice에 속하면 Telegram review는 한 번만 보낸다.
* 서로 다른 `bbs_seq`라도 title/source/date/attachment metadata가 사실상 같은 경우 `attachment_group_key`로 묶는다.
* attachment URL 자체는 public `link_url` 우선값이 아니라 source evidence URL로 취급한다.

## 8. Recommended Fix Strategy

### Phase 1. Add read-only duplicate diagnostics/admin visibility

* AREA: `CONTENT_QUEUE + SOCIAL_NEWS_CANDIDATE + TELEGRAM_REPORTING`
* MODE: `GUARDED_FIX`
* Risk: `LOW`
* likely files:
  * `SRC/foreign_worker_life_info_collector/api/admin_server.py`
  * `SRC/foreign_worker_life_info_collector/content/repository.py`
  * `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py`
  * Admin UI duplicate diagnostics page or existing content management detail panel
* protected area involvement:
  * No publisher behavior change
  * No scheduler change
  * Read-only SQL only
* verification plan:
  * 같은 `source_url`, `canonical_url`, `title+source`, `semantic_review_key`, Facebook successful post log를 조회하는 diagnostics endpoint.
  * DB mutation 없음 확인.

### Phase 2. Add representative candidate grouping for attachment notices

* AREA: `DATA_SOURCE_QUALITY + CONTENT_QUEUE + IMMIGRATION_INFO`
* MODE: `GUARDED_FIX`
* Risk: `MEDIUM`
* likely files:
  * `SRC/foreign_worker_life_info_collector/immigration/normalizer.py`
  * `SRC/foreign_worker_life_info_collector/immigration/repository.py`
  * `SRC/foreign_worker_life_info_collector/content/service.py`
* protected area involvement:
  * DB migration may be needed if adding `attachment_group_key`; otherwise use `raw_response` first.
  * No Telegram runtime behavior change unless later phase.
* verification plan:
  * `bbs_seq` different but same title/source/date/attachment summary인 샘플이 하나의 representative group으로 묶이는지 dry-run.

### Phase 3. Strengthen Telegram semantic duplicate suppression

* AREA: `TELEGRAM_REPORTING + CONTENT_QUEUE`
* MODE: `GUARDED_FIX`
* Risk: `MEDIUM`
* likely files:
  * `SRC/foreign_worker_life_info_collector/content/service.py`
  * `SRC/foreign_worker_life_info_collector/content/repository.py`
  * `SRC/foreign_worker_life_info_collector/api/admin_server.py`
* protected area involvement:
  * Telegram actual send path must remain dry-run/testable.
  * Callback behavior should not change.
* verification plan:
  * same candidate/status/message second send suppressed.
  * different candidate but same semantic title/source/attachment_group suppressed.
  * meaningful update changes review key and allows review.

### Phase 4. Add pre-publish idempotency check by source/canonical/title/content fingerprint

* AREA: `SOCIAL_NEWS_CANDIDATE + CONTENT_PUBLISHER`
* MODE: `GUARDED_FIX`
* Risk: `HIGH`
* likely files:
  * `SRC/foreign_worker_life_info_collector/social/news/pipeline.py`
  * `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py`
  * possible content publisher repository if unified publish path is active
* protected area involvement:
  * Facebook publisher API payload should not change.
  * Selection/publisher behavior changes require dry-run verification.
* verification plan:
  * same `source_url` already successful published -> skip with reason.
  * same `canonical_url` already successful published -> skip with reason.
  * same `title+source` within freshness window -> skip or manual review.

### Phase 5. Add atomic READY -> PUBLISHING claim if missing

* AREA: `SOCIAL_NEWS_CANDIDATE + CONTENT_PUBLISHER`
* MODE: `GUARDED_FIX`
* Risk: `HIGH`
* likely files:
  * `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py`
  * `SRC/foreign_worker_life_info_collector/social/news/pipeline.py`
* protected area involvement:
  * Scheduler interval unchanged.
  * FacebookPublisher unchanged.
  * DB migration may be needed if status enum constraints exist elsewhere.
* verification plan:
  * concurrent claim simulation.
  * second claim returns no row.
  * failed publish releases/marks retryable safely.

### Phase 6. Add duplicate reason logging

* AREA: `DATA_SOURCE_QUALITY + CONTENT_QUEUE + TELEGRAM_REPORTING`
* MODE: `GUARDED_FIX`
* Risk: `LOW`
* likely files:
  * `content.publish_log`
  * `social_news.pipeline_step_log`
  * `social_news.publish_log`
* protected area involvement:
  * No external API.
  * No scheduler change.
* verification plan:
  * `DUPLICATE_SILENT`, `DUPLICATE_SIGNAL_UPDATED`, `REVIEW_SUPPRESSED_DUPLICATE`, `PUBLISH_SUPPRESSED_DUPLICATE` reasons visible in admin logs.

## 9. CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: `TELEGRAM_REPORTING + CONTENT_QUEUE`
MODE: `GUARDED_FIX`
FOCUS: Strengthen Telegram duplicate suppression for different `content_candidate_id` but same semantic official/living content.
WHY: Current `semantic_review_key` is URL-first, so different `bbs_seq` or attachment URL can bypass suppression even when preview/title/source are effectively the same.
RISK: `MEDIUM`
PROTECTED AREA: Telegram callback/runtime behavior, scheduler, Facebook publisher, DB destructive migration.
FILES LIKELY INVOLVED: `content/service.py`, `content/repository.py`, `api/admin_server.py`, tests under `SRC/foreign_worker_life_info_collector/tests/`.
RECOMMENDED NEXT PROMPT: Add a guarded Telegram review duplicate suppression fix that introduces an attachment/title/source semantic key and verifies same semantic notice is suppressed without changing Telegram callback behavior.

CODE_TASK_CANDIDATE
AREA: `DATA_SOURCE_QUALITY + CONTENT_QUEUE + IMMIGRATION_INFO`
MODE: `READ_ONLY_AUDIT`
FOCUS: Audit MOEL/MOJ/HiKorea attachment notice identity and define `official_notice_key` / `attachment_group_key`.
WHY: Different `bbs_seq` values may represent attachment-only or closely related official notices that should be grouped before content review.
RISK: `LOW`
PROTECTED AREA: DB mutation, migration, scheduler, Telegram/Facebook runtime.
FILES LIKELY INVOLVED: `immigration/collectors.py`, `immigration/normalizer.py`, `immigration/repository.py`, `content/service.py`.
RECOMMENDED NEXT PROMPT: Read-only audit official notice attachment identity and recommend grouping keys for board URL, title/source/date, and attachment metadata.

CODE_TASK_CANDIDATE
AREA: `SOCIAL_NEWS_CANDIDATE + CONTENT_PUBLISHER`
MODE: `READ_ONLY_AUDIT`
FOCUS: Trace duplicate Facebook publish case using publish logs, source_url/canonical_url/title/source, and candidate state transitions.
WHY: Case A may be caused by same candidate concurrent publish or same article split into multiple candidates.
RISK: `LOW`
PROTECTED AREA: Facebook publisher, scheduler, DB writes, external API.
FILES LIKELY INVOLVED: `social/news/repository/news_repository.py`, `social/news/pipeline.py`, `social/news/publisher/facebook_publisher.py`, `api/admin_server.py`.
RECOMMENDED NEXT PROMPT: Add read-only duplicate diagnostics to identify whether ChosunBiz duplicate was same candidate, same URL across candidates, or publish race.

CODE_TASK_CANDIDATE
AREA: `SOCIAL_NEWS_CANDIDATE + CONTENT_PUBLISHER`
MODE: `GUARDED_FIX`
FOCUS: Add pre-publish idempotency check by `source_url`, `canonical_url`, normalized `title+source`, and message/link fingerprint.
WHY: Publish path currently relies on candidate state after publish and lacks a final already-published guard before calling Facebook.
RISK: `HIGH`
PROTECTED AREA: Facebook API payload, scheduler interval, auth/env/config.
FILES LIKELY INVOLVED: `social/news/repository/news_repository.py`, `social/news/pipeline.py`, tests.
RECOMMENDED NEXT PROMPT: Implement a guarded pre-publish duplicate check in dry-run first; do not change `FacebookPublisher` payload or scheduler.

CODE_TASK_CANDIDATE
AREA: `SOCIAL_NEWS_CANDIDATE + CONTENT_PUBLISHER`
MODE: `GUARDED_FIX`
FOCUS: Add atomic `READY_TO_PUBLISH -> PUBLISHING` claim before Facebook publish.
WHY: Without atomic claim, concurrent loops/manual triggers can publish the same candidate before `published_at` is written.
RISK: `HIGH`
PROTECTED AREA: Scheduler interval, FacebookPublisher, auth/env/config, destructive migration.
FILES LIKELY INVOLVED: `social/news/repository/news_repository.py`, `social/news/pipeline.py`, possible migration if status constraint requires it.
RECOMMENDED NEXT PROMPT: Implement repository-level atomic claim with `UPDATE ... WHERE status/publish_status READY ... RETURNING id`, then publish only claimed candidates, with tests.

## 10. Stop Conditions Encountered

No stop condition was triggered.

Implementation was intentionally not performed because the requested mode is `READ_ONLY_AUDIT`.

The following changes would require a guarded follow-up task:

* changing Telegram suppression behavior
* changing Facebook publish selection or idempotency behavior
* adding `PUBLISHING` status or DB constraints
* adding attachment grouping columns or migrations
* changing scheduler/manual publish coordination

## 11. Final Recommendation

가장 안전한 다음 구현 작업은 `READ_ONLY` diagnostics endpoint/UI를 먼저 추가하는 것이다.

이유:

* Case A가 same candidate race인지, same URL multi-candidate인지 먼저 구분해야 한다.
* Case B가 true multi-notice인지, attachment-only semantic duplicate인지 먼저 보이게 해야 한다.
* diagnostics는 publisher, scheduler, Telegram runtime을 건드리지 않고 운영자가 중복 원인을 확인할 수 있다.

그 다음 순서는 다음이 적절하다.

1. Telegram semantic suppression 강화
2. official attachment notice grouping
3. Facebook pre-publish idempotency guard
4. atomic `READY_TO_PUBLISH -> PUBLISHING` claim

