# PHASE 6 Living Info Facebook Dry-Run Boundary Result

## 1. 결론
- PHASE 6 `Facebook Publish Boundary / Dry-Run Validation` 완료.
- `LIVING_INFO` candidate의 protected Facebook dry-run path를 테스트로 고정했다.
- 실제 Facebook API post는 실행하지 않았고, 테스트에서도 `FacebookPageClient`가 호출되면 실패하도록 차단했다.

## 2. 수정 파일
- `SRC/foreign_worker_life_info_collector/content/service.py`
- `SRC/foreign_worker_life_info_collector/tests/test_living_info_facebook_dry_run_boundary.py`

## 3. 구현 내용
- `ContentService.publish`
  - protected dry-run 여부를 link/message validation 전에 계산하도록 조정.
  - dry-run publish validation 중 link/message가 실패하면 `update_publish_result(..., dry_run=True)`로 기록되도록 수정.
  - 안전 약화 없음: real publish enable 조건, token selection, Facebook client 호출 조건은 그대로 유지.

## 4. 검증 내용
- Eligible `LIVING_INFO` candidate:
  - `ContentService.publish(candidate_id, dry_run=True)` -> `DRY_RUN`
  - request payload에 `access_token`, `token_masked`, `token_fingerprint` 없음
  - real Facebook client 호출 없음

- Invalid Facebook link:
  - `/path/A` legacy redirect URL -> `FACEBOOK_LINK_INVALID`
  - dry-run validation failure로 기록

- Invalid Facebook message:
  - Korean text 포함 -> `FACEBOOK_MESSAGE_INVALID`
  - dry-run validation failure로 기록

- Quality gate failure:
  - source link missing / score 0 -> `BLOCKED_SOURCE_INVALID`
  - `mark_candidate_quality_blocked` path로 reason 기록
  - publish update 없음

## 5. 테스트 결과
- py_compile 성공:
  - `foreign_worker_life_info_collector\content\service.py`
  - `foreign_worker_life_info_collector\tests\test_living_info_facebook_dry_run_boundary.py`

- pytest 성공:
  - command: `python -m pytest foreign_worker_life_info_collector\tests\test_living_info_facebook_dry_run_boundary.py foreign_worker_life_info_collector\tests\test_living_info_telegram_review_flow.py foreign_worker_life_info_collector\tests\test_living_info_content_prep_scheduler_contract.py foreign_worker_life_info_collector\tests\test_living_info_service.py foreign_worker_life_info_collector\tests\test_content_sync_living_info.py foreign_worker_life_info_collector\tests\test_content_exclusion_gate.py -q`
  - result: `35 passed in 0.11s`

## 6. 보호영역 확인
- real Facebook post: 실행 없음
- token refresh automation: 변경 없음
- publish frequency: 변경 없음
- real publish enabled by default: 변경 없음
- env/secrets: 변경 없음
- scheduler enabling: 변경 없음
- quality gate bypass: 없음

## 7. 다음 PHASE 진행 판단
- PHASE 6 성공 기준 충족.
- PHASE 7 final integration review report 작성 가능.
