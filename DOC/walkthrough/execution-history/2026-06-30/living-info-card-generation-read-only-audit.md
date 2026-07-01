# Living Info Card Generation Read-Only Audit

## 1. 결론

생활정보 카드 생성 기능은 구현되어 있지만 `LIVING_INFO` 후보 생성, `topic_cluster` 준비, `sync_living_info()`, `READY_TO_REVIEW` 상태 변경만으로는 자동 실행되지 않습니다. 실제 카드 생성은 `send_content_review_to_telegram()` 안에서 `ContentService.telegram_review_card_preview()`가 호출될 때 발생합니다. 따라서 뉴스 수집/게시 루프가 계속 돌아도 생활정보 카드 보고가 안 보이는 핵심 원인은 뉴스 루프와 카드 생성 루프가 분리되어 있고, 생활정보 준비 파이프라인은 Telegram review 호출 전까지 카드 PNG를 만들거나 `publish_log`에 `content_card_preview`를 남기지 않기 때문입니다.

최종 판정: `CARD_GENERATION_MANUAL_ONLY`

## 2. Current card generation path

현재 실제 코드 흐름:

```text
content.content_candidate
-> ContentService.review_targets()
-> send_content_review_to_telegram(candidate, dry_run=...)
-> ContentService.telegram_review_card_preview(candidate)
-> build_content_card_preview(candidate)
-> card_generation_target(candidate)
-> build_content_card_payload(candidate, template_type)
-> render_content_card(payload)
-> storage/cache/content_cards/workconnect-card-*.png
-> content.publish_log request_payload.content_card_preview
-> Admin UI ContentManagementPage.vue detail publish_logs card preview block
```

확인한 코드:

- `SRC/foreign_worker_life_info_collector/content/service.py`
  - `review_targets()`
  - `telegram_review_card_preview()`
  - `telegram_review_message()`

- `SRC/foreign_worker_life_info_collector/api/admin_server.py`
  - `send_content_review_to_telegram()`
  - `telegram_card_preview_metadata()`
  - `run_content_generation_cycle()`

- `SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py`
  - `build_content_card_preview()`
  - `card_generation_target()`
  - `build_content_card_payload()`
  - `render_content_card()`

- `SRC/foreign_worker_life_info_collector/content/repository.py`
  - `publish_log_row()`
  - `extract_content_card_preview()`

- `SRC/foreign_worker_life_info_collector/admin_ui/src/views/ContentManagementPage.vue`
  - detail `publishLogs`
  - `log.content_card_preview` display

## 3. Trigger gap

카드 생성이 자동으로 호출되지 않는 지점:

- `ContentService.sync_living_info()`
  - `living_info.topic_cluster`를 `content.content_candidate`로 upsert할 뿐 카드 preview를 생성하지 않음.

- `LivingInfoService.prepare_topic_clusters()`
  - `living_info.normalized_item`을 `topic_cluster` / `topic_cluster_item`로 준비할 뿐 카드 preview를 생성하지 않음.

- `run_living_info_content_prep_cycle()`
  - `prepare_living_info_topic_clusters()`와 조건부 `sync_living_info()`만 실행.
  - 결과 payload에 `telegram: "NOT_SENT"`가 명시되어 있음.

- `POST /api/admin/content/living-info/sync`
  - 후보 생성만 수행.
  - Telegram review나 card preview 생성 없음.

카드 생성이 호출되는 지점:

- `POST /api/admin/content/candidates/{id}/send-telegram-review`
- `run_content_generation_cycle()`가 review target을 잡아 `send_content_review_to_telegram()`를 호출하는 경우

즉, `LIVING_INFO READY_TO_REVIEW` 후보가 존재해도 Telegram review 경로를 타지 않으면 카드 PNG와 card report는 생성되지 않습니다.

## 4. Eligibility / failure conditions

`LIVING_INFO` 후보가 카드 생성 대상에서 제외될 수 있는 조건:

- `final_publish_score <= 0`
  - reason: `CARD_BLOCKED_ZERO_SCORE`

- `content_quality_gate_code`가 bypass block code인 경우
  - 예: `BLOCKED_SOURCE_INVALID`, `BLOCKED_LOW_USER_NEED`, `BLOCKED_SYSTEM_TEXT`, `WATCH_TOPIC_ONLY`

- `content_type == NEWS_ARTICLE`이고 valid link가 있는 경우
  - reason: `NEWS_ARTICLE_LINK_PREVIEW_USES_OG`

- 단일 `social_news.candidate` 기반 living candidate인데 topic/fact evidence가 없는 경우
  - status: `CARD_NOT_READY`
  - reason: `single_news_public_card_not_ready`

- 카드 bullet이 3개 미만이거나 usable point가 부족한 경우
  - status: `INSUFFICIENT_VALID_CARD_POINTS`

- bullet이 title/source/url을 반복하는 경우
  - `CARD_POINT_TITLE_ECHO`
  - `CARD_POINT_SOURCE_ECHO`
  - `CARD_POINT_URL_ECHO`

- 카드 텍스트가 너무 길어 템플릿에 맞지 않는 경우
  - `CARD_TEXT_OVERFLOW`

- public text에 한글/일본어/중국어 문자가 포함된 경우
  - `CARD_TEXT_INVALID_LANGUAGE`

- 운영/시스템 문구가 카드 payload에 포함된 경우
  - `CARD_TEXT_FORBIDDEN_SYSTEM_TEXT`

테스트 확인:

- `test_content_card_generator.py`
  - living card PNG 생성 가능
  - `NEWS_ARTICLE`은 OG preview 사용
  - single social-news living source는 `CARD_NOT_READY`
  - topic evidence가 있으면 render 가능
  - invalid bullet/text/language/overflow 차단

## 5. Reporting gap

카드가 생성되면 보고되는 위치:

- `send_content_review_to_telegram()`이 `review_metadata["content_card_preview"]`에 metadata를 넣음.
- `record_telegram_review()`가 `content.publish_log.request_payload`에 metadata를 저장.
- `ContentRepository.extract_content_card_preview()`가 `publish_log`에서 preview를 추출.
- `ContentManagementPage.vue`가 detail panel의 `publishLogs`에서 `log.content_card_preview`를 표시.

보고가 안 보이는 경우:

- `send_content_review_to_telegram()`이 호출되지 않은 경우
- review target에 잡히지 않은 경우
- 이미 6시간 내 `SENT`/`DRY_RUN` log가 있어 `list_review_targets()`에서 제외된 경우
- card generation 결과가 `CARD_NOT_REQUIRED` / `CARD_NOT_READY`인데 Telegram review log까지 가지 않은 경우
- `sync_living_info()` 또는 content prep cycle만 실행하고 Telegram review를 실행하지 않은 경우

파일 상태 확인:

- `SRC/foreign_worker_life_info_collector/storage/cache/content_cards`
  - `workconnect-card-*.png` 5개 확인
  - 최신 cache card: `2026-06-20 22:26:04`

- `SRC/foreign_worker_life_info_collector/storage/generated/content_cards`
  - CLI/sample generator output 56개 확인
  - 최신 generated card: `2026-06-17 21:56:07`

- `SRC/foreign_worker_life_info_collector/storage/generated/living_info`
  - `manual_sync_dry_run.json` 등 living-info dry-run output은 있음
  - 이 경로는 card image output이 아니라 living-info sync dry-run output임

판단:

- 카드 생성 기능은 존재하고 과거 output도 있음.
- 현재 생활정보 준비/동기화 단계만 실행하면 카드가 새로 생성되거나 report에 나타나지 않는 구조.
- 카드 report는 Telegram review log 기반이므로 `publish_log`가 없으면 Admin UI에도 표시되지 않음.

## 6. News loop comparison

뉴스 루프:

- `sync_all()`은 `sync_social_news()`와 `sync_immigration()`만 호출.
- 일반 뉴스는 기존 social/news publish 흐름 또는 content publish 흐름을 타며, card image generation과 직접 연결되지 않음.
- `NEWS_ARTICLE` + valid link는 card renderer에서 의도적으로 `NEWS_ARTICLE_LINK_PREVIEW_USES_OG`로 제외됨.
- 뉴스는 OG/link preview 기반으로 게시되거나 처리될 수 있음.

생활정보 카드 루프:

- `LIVING_INFO`는 `sync_all()`에 포함되지 않음.
- 별도 manual path:
  - `prepare_living_info_topic_clusters()`
  - `sync_living_info()`
  - `READY_TO_REVIEW`
- 카드 생성은 이 단계가 아니라 Telegram review 단계에서만 실행.
- `run_living_info_content_prep_cycle()`도 `telegram: "NOT_SENT"`를 명시함.

결론:

뉴스 posting이 된다고 해서 생활정보 card generation이 같이 실행되는 구조가 아닙니다. 뉴스는 링크/OG 중심이고, 생활정보 카드는 Telegram review preview 중심입니다.

## 7. CODE_TASK_CANDIDATE

### CODE_TASK_CANDIDATE 1

AREA: `CONTENT_CARD_GENERATION + CONTENT_QUEUE`

MODE: `LOW_RISK_FIX`

PURPOSE FUNCTION:
Add read-only/admin-visible card generation audit status so operators can see whether a `LIVING_INFO` candidate is card-eligible before Telegram review.

ALLOWED:
- Add preview status calculation endpoint or detail-only diagnostic field.
- Add Admin UI display for `card_generation_target()` result.
- Add tests for status display.

FORBIDDEN:
- No real Telegram send.
- No Facebook publisher changes.
- No scheduler changes.
- No DB migration.
- No auth/env/secrets changes.

VERIFICATION:
- `LIVING_INFO READY_TO_REVIEW` detail shows `CARD_ELIGIBLE`, `CARD_NOT_READY`, or failure reason.
- No PNG generation required for status-only audit.
- Admin UI build passes.

STOP CONDITIONS:
- Requires DB schema change.
- Requires publisher/scheduler/auth changes.

### CODE_TASK_CANDIDATE 2

AREA: `CONTENT_CARD_GENERATION + CONTENT_QUEUE + LIVING_DOMAIN`

MODE: `GUARDED_FIX`

PURPOSE FUNCTION:
Generate dry-run card preview metadata for `LIVING_INFO READY_TO_REVIEW` candidates without sending Telegram, so card output is visible before manual review delivery.

ALLOWED:
- Add manual/admin-only dry-run card preview endpoint.
- Generate PNG into `storage/cache/content_cards`.
- Store result in existing `content.publish_log` with a non-send status such as `CARD_PREVIEW_DRY_RUN`.
- Add tests.

FORBIDDEN:
- No real Telegram send.
- No Facebook publish.
- No scheduler enabling.
- No destructive DB migration.
- No auth/env/secrets changes.

VERIFICATION:
- Manual endpoint returns `content_card_preview`.
- PNG path exists when `CARD_PREVIEW_GENERATED`.
- Failure status is logged with reason.
- No external output occurs.

STOP CONDITIONS:
- Requires changing Telegram callback/runtime.
- Requires changing publisher payload.

### CODE_TASK_CANDIDATE 3

AREA: `CONTENT_CARD_GENERATION + TELEGRAM_REPORTING + ADMIN_UI`

MODE: `LOW_RISK_FIX`

PURPOSE FUNCTION:
Show card preview status consistently in Admin UI and Telegram review dry-run reports, including failures such as `CARD_NOT_READY`, `INSUFFICIENT_VALID_CARD_POINTS`, and `CARD_TEXT_OVERFLOW`.

ALLOWED:
- Improve Admin UI detail panel.
- Improve dry-run response payload.
- Add mock JSON or tests.

FORBIDDEN:
- No real Telegram send.
- No Facebook publisher.
- No scheduler.
- No DB migration.
- No auth/env/secrets.

VERIFICATION:
- Admin UI detail displays preview status/reason/image_path when log exists.
- Dry-run Telegram response includes `content_card_preview`.
- UI build passes.

STOP CONDITIONS:
- Requires production Telegram send.
- Requires DB schema change.

## 8. 최종 판정

`CARD_GENERATION_MANUAL_ONLY`

## 9. 재시작 / 재로딩 필요 여부

- Backend restart:
  - NO
  - 이유: 이번 작업은 `READ_ONLY_AUDIT`이며 runtime code를 수정하지 않았습니다.

- Frontend dev server restart:
  - NO
  - 이유: Admin UI code를 수정하지 않았습니다.

- Browser hard refresh:
  - NO
  - 이유: UI 변경이 없습니다.

- DB restart:
  - NO
  - 이유: DB schema/migration/query mutation 변경이 없습니다.

- Scheduler/Bot restart:
  - NO
  - 이유: scheduler, bot state, Telegram runtime, Facebook publisher를 수정하지 않았습니다.

- External service restart:
  - NO
  - 대상: Telegram, Facebook, Ollama
  - 이유: 외부 서비스 호출/설정 변경이 없습니다.

- 사용자가 직접 해야 할 작업:
  1. 없음.
  2. 다음 구현 단계에서 card preview dry-run endpoint를 추가한다면 그때 backend restart가 필요합니다.
  3. Admin UI 표시를 변경한다면 그때 frontend dev server reload 또는 browser hard refresh가 필요합니다.

## 10. 검증

- GitHub repository target:
  - `origin https://github.com/marklee929/foreignWorkerJobInfoService`

- Completion marker pre-check:
  - exact `[WC_EXECUTION_COMPLETE]` count: `0`
  - legacy decorated Korean marker count: `0`
  - loose completion marker count: `0`
  - First-Run Fallback 적용

- Commands:
  - `python -m pytest foreign_worker_life_info_collector\tests\test_content_card_generator.py foreign_worker_life_info_collector\tests\test_living_info_telegram_review_flow.py -q`
  - result: `17 passed in 14.08s`

  - `python -m py_compile foreign_worker_life_info_collector\utils\content_card_renderer.py foreign_worker_life_info_collector\content\service.py foreign_worker_life_info_collector\api\admin_server.py`
  - result: PASS

## 11. 보호영역 확인

- 코드 수정: 없음
- DB/migration: 변경 없음
- Scheduler/Bot state: 변경 없음
- Facebook publisher: 변경 없음
- Telegram runtime/callback: 변경 없음
- auth/env/secrets: 변경 없음
- real Telegram/Facebook output: 없음
