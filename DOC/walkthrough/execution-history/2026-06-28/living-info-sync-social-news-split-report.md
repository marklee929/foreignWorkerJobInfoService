# GUARDED_FIX REPORT: LIVING_INFO `sync_social_news()` Split

## 1. Pre-Review

- AREA: `LIVING_DOMAIN + CONTENT_QUEUE + SOCIAL_NEWS_CANDIDATE`
- MODE: `GUARDED_FIX`
- PURPOSE FUNCTION: WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.
- Risk: MEDIUM
- Decision: `PROCEED_WITH_LIMITS`
- Protected areas touched: NO
- Files inspected:
  - `DOC/walkthrough/2026-06-28 - execute prompt.md`
  - `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/living_info/models.py`
  - `SRC/foreign_worker_life_info_collector/living_info/repository.py`
  - `SRC/foreign_worker_life_info_collector/living_info/service.py`
- Files modified:
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/living_info/__init__.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_living_info_service.py`
  - `SRC/foreign_worker_life_info_collector/tests/test_content_sync_living_split.py`

## 2. 구현 내용

- `ContentService.__init__()`에 선택적 `living_info_service` 의존성을 추가했습니다.
- `ContentService.sync_social_news()`의 DB 조회는 유지하고, row 처리만 `_sync_social_news_rows()`로 분리했습니다.
- `social_news_payload(row)` 결과가 `source_domain = "LIVING_INFO"`이면:
  - `LivingInfoService.ingest_from_social_news_candidate(payload)`로 전달합니다.
  - `content.content_candidate`를 직접 생성하지 않습니다.
- `source_domain = "SOCIAL_NEWS"`인 일반 뉴스는 기존처럼 `ContentRepository.upsert_candidate(payload)` 경로를 유지합니다.
- 결과 payload에 아래 세부 카운트를 추가했습니다.
  - `content_candidate_synced_count`
  - `living_info_ingested_count`
  - `living_info_skipped_count`
  - `skipped_no_title_count`
- 기존 호환성을 위해 `synced_count`는 유지했습니다.

## 3. 보존한 경계

- non-living social news:
  - 기존 `SOCIAL_NEWS / NEWS_ARTICLE -> content.content_candidate` 경로 유지
- living-classified social news:
  - `living_info.source_item`
  - `living_info.normalized_item`
  - `content.content_candidate` 직접 생성 차단
- `content.content_candidate`는 여전히 최종 review/publish owner입니다.
- `living_info`는 직접 publish하지 않습니다.

## 4. 테스트 / 검증

- `python -m py_compile foreign_worker_life_info_collector\content\service.py foreign_worker_life_info_collector\living_info\service.py foreign_worker_life_info_collector\living_info\__init__.py foreign_worker_life_info_collector\tests\test_living_info_service.py foreign_worker_life_info_collector\tests\test_content_sync_living_split.py`
  - Result: PASS
- `python -m pytest foreign_worker_life_info_collector\tests\test_living_info_service.py foreign_worker_life_info_collector\tests\test_content_sync_living_split.py -q`
  - Result: `8 passed in 0.09s`
- `python -m pytest foreign_worker_life_info_collector\tests\test_content_exclusion_gate.py foreign_worker_life_info_collector\tests\test_content_review_dedupe.py -q`
  - Result: `17 passed in 0.09s`

## 5. 검증 시나리오

- non-living `content_category = "foreign_jobs"`, `priority_group = "PRIMARY"`
  - `content.content_candidate` path: YES
  - `living_info` ingestion: NO
- living `content_category = "healthcare"`, `priority_group = "SECONDARY"`
  - `living_info` ingestion: YES
  - `content.content_candidate` direct creation: NO
- living row with invalid source URL
  - `living_info_skipped_count`: 증가
  - `content.content_candidate` direct creation: NO

## 6. 재시작 / 재로딩 필요 여부

- Backend restart: YES
  - 이유: `SRC/foreign_worker_life_info_collector/content/service.py` runtime sync boundary가 수정되어 backend 재시작이 필요합니다.
- Frontend dev server restart: NO
  - 이유: Admin UI 파일은 수정하지 않았습니다.
- Browser hard refresh: NO
  - 이유: UI 변경이 없습니다.
- DB restart: NO
  - 이유: DB schema/migration 변경이 없습니다.
- Scheduler/Bot restart: MAYBE
  - 이유: scheduler가 backend 프로세스 내부에서 `ContentService.sync_social_news()`를 호출하면 backend restart에 포함됩니다. 별도 프로세스라면 해당 프로세스 재시작이 필요합니다.
- External service restart: NO
  - 대상: Telegram/Facebook/Ollama
  - 이유: Telegram runtime, Facebook publisher, Ollama 관련 코드를 수정하지 않았습니다.
- 사용자가 직접 해야 할 작업:
  1. backend 재시작
  2. 다음 수집/동기화 실행 후 `LIVING_INFO` row가 `content.content_candidate`가 아니라 `living_info.source_item` / `living_info.normalized_item`에 적재되는지 확인
  3. 기존 뉴스 후보가 계속 `content.content_candidate`로 들어가는지 확인

## 7. 보호영역 확인

- DB/migration: NOT MODIFIED
- publisher/FacebookPublisher: NOT MODIFIED
- scheduler: NOT MODIFIED
- Telegram runtime behavior: NOT MODIFIED
- auth/env/config: NOT MODIFIED
- external API behavior: NOT MODIFIED
- existing content rows delete/update: NOT PERFORMED
- public content creation from living rows: BLOCKED in `sync_social_news()`

## 8. 남은 위험

- `living_info` 적재는 아직 topic clustering까지 자동 연결되지 않습니다.
- 기존에 이미 생성된 `content.content_candidate.source_domain = 'LIVING_INFO'` row는 삭제하거나 변경하지 않았습니다.
- `sync_living_info()`는 아직 구현되지 않았습니다.
- living row가 `living_info`로 들어간 뒤 public 후보가 되는 기준은 TASK 7 audit에서 확정해야 합니다.

## 9. Next CODE_TASK_CANDIDATE

`TASK 7: Audit sync_living_info() Content Candidate Path`를 진행해 `living_info.topic_cluster -> content.content_candidate` 승격 조건을 먼저 확정하는 것이 안전합니다.
