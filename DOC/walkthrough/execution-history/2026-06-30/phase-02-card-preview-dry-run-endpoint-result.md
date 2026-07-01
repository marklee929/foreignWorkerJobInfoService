# PHASE 2 - Single Candidate Card Preview Dry-Run Endpoint

## 1. 결론

- Status: COMPLETE
- Endpoint added: `POST /api/admin/content/candidates/{id}/card-preview-dry-run`
- External send: NONE
- DB schema change: NONE

## 2. 수정 파일

- `SRC/foreign_worker_life_info_collector/api/admin_server.py`
- `SRC/foreign_worker_life_info_collector/content/service.py`
- `SRC/foreign_worker_life_info_collector/content/repository.py`

## 3. 구현 내용

- `ContentService.generate_card_preview_dry_run(candidate_id)`
  - candidate를 로드합니다.
  - 기존 `telegram_review_card_preview(candidate)`를 재사용합니다.
  - `send_content_review_to_telegram()`은 호출하지 않습니다.
  - Telegram API 함수는 호출하지 않습니다.
  - Facebook publisher는 호출하지 않습니다.
- `ContentRepository.record_content_card_preview(...)`
  - existing `content.publish_log`에 기록합니다.
  - `channel = 'content_card_preview'`
  - success status: `CARD_PREVIEW_DRY_RUN`
  - failure status: `CARD_PREVIEW_FAILED`
  - `dry_run = TRUE`
  - `request_payload.content_card_preview`와 `response_payload`에 preview result를 저장합니다.

## 4. 응답 형태

- Success:
  - `ok: true`
  - `status: CARD_PREVIEW_DRY_RUN`
  - `content_card_preview.status: CARD_PREVIEW_GENERATED`
- Failure:
  - `ok: true`
  - `status: CARD_PREVIEW_FAILED`
  - `content_card_preview.status`와 `reason` 유지
- Missing candidate:
  - HTTP 404
  - `status: NOT_FOUND`

## 5. 검증 상태

- Code path review: PASS
- Compile/test: PHASE 5에서 통합 수행 예정

## 6. 보호영역 확인

- DB/migration: not modified
- Facebook publisher: not modified
- Scheduler: not modified
- Telegram runtime send/callback: not modified
- Auth/env/config: not modified
- External API behavior: not modified

## 7. 재시작 / 재로딩 필요 여부

- Backend restart: YES
  - Reason: `admin_server.py`, `content/service.py`, `content/repository.py` changed.
- Frontend dev server restart: NO
- Browser hard refresh: NO
- DB restart: NO
- Scheduler/Bot restart: NO or included in backend restart if running in the same process.
- Ollama restart: NO

## 8. 다음 PHASE 진행 여부

- Proceed: YES
- Next: PHASE 3 bulk LIVING_INFO card preview dry-run
