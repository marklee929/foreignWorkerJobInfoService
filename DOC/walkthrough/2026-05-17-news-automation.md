# 2026-05-17 Social News Automation

## 목표

- Issue #1 기준으로 `social/news` 기반 뉴스 자동화 파이프라인의 1차 dry-run 흐름을 구현한다.
- 실제 Facebook/Telegram API 호출 없이 DB 저장, 중복 제거, 게시 후보 선별, 게시/알림 로그 저장까지 검증한다.

## 확인한 문서와 이슈

- `DOC/architecture/workflow-guide.md`
- `DOC/architecture/collector-hierarchy.md`
- `DOC/walkthrough/2026-05-16-workflow-setup.md`
- `DOC/walkthrough/2026-05-16 - execute prompt.md`
- GitHub Issue #1: Social 뉴스 자동화 파이프라인

## 변경 파일 목록

- `README.md`
- `DOC/walkthrough/2026-05-17-news-automation.md`
- `SRC/foreign_worker_life_info_collector/social/news/models.py`
- `SRC/foreign_worker_life_info_collector/social/news/pipeline.py`
- `SRC/foreign_worker_life_info_collector/social/news/normalizer/news_normalizer.py`
- `SRC/foreign_worker_life_info_collector/social/news/duplicate_guard/duplicate_detector.py`
- `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py`
- `SRC/foreign_worker_life_info_collector/storage/db/migrations/schema.sql`
- `SRC/foreign_worker_life_info_collector/tests/test_social_news_pipeline.py`

## 완료한 내용

- `NewsItem`, `NewsCandidate` 모델을 확장했다.
- 뉴스 제목, URL, hash, similarity key 정규화 흐름을 추가했다.
- canonical URL/hash/title similarity 기준 중복 판정 helper를 추가했다.
- SQLite 기반 `NewsRepository`를 구현해 뉴스 후보 저장, 중복 상태 분리, 게시 후보 선별, Facebook/Telegram dry-run 로그 저장을 처리한다.
- `schema.sql`에 `news_candidate`, `facebook_publish_log`, `telegram_notify_log`, `news_performance_snapshot` 테이블과 주요 인덱스를 추가했다.
- `python -m foreign_worker_life_info_collector.social.news.pipeline --db <db_path> --dry-run` 실행 진입점을 구현했다.
- collector가 아직 실제 외부 수집을 하지 못하는 상태에서도 dry-run 검증이 가능하도록 deterministic seed 후보 2건을 사용한다.
- README의 walkthrough 링크를 오늘 작업 기록으로 갱신했다.

## 실행/검증 결과

```powershell
$env:PYTHONPATH='C:\WORK\foreign_worker_job_info\SRC'
python -m unittest discover -s SRC\foreign_worker_life_info_collector\tests
```

결과: `Ran 2 tests in 0.101s`, `OK`

```powershell
$env:PYTHONPATH='C:\WORK\foreign_worker_job_info\SRC'
python -m foreign_worker_life_info_collector.social.news.pipeline --db $env:TEMP\workconnect-news-dryrun.db --dry-run --keyword '외국인 취업 비자'
```

결과:

- dry-run 후보 2건 생성
- 1건은 `CANDIDATE`에서 `PUBLISHED`로 전환
- 동일 URL/제목 1건은 `DUPLICATE`로 분리
- `facebook_publish_log`와 `telegram_notify_log`에 `DRY_RUN` 로그 저장

## 실패/수정한 내용

- 최초 테스트에서 `social.news.pipeline`의 상대 import가 잘못되어 `foreign_worker_life_info_collector.facebook`를 찾는 오류가 발생했다. `social.facebook`, `social.telegram` 경로로 수정했다.
- SQLite 연결이 명시적으로 닫히지 않아 Windows 임시 DB 삭제가 실패했다. `NewsRepository`의 연결 사용부를 `finally: conn.close()` 패턴으로 수정했다.
- `gh` CLI가 설치되어 있지 않아 Issue 확인은 GitHub REST API로 수행했다.

## 다음 작업 시작점

- `social/news/collector`의 Naver/Google/RSS collector를 실제 수집 구현으로 교체한다.
- 실제 Facebook 게시 client와 Telegram notifier는 환경변수 기반으로만 활성화하고, dry-run 기본 동작은 유지한다.
- `news_candidate.status` 전이 규칙을 `FAILED`, `SKIPPED`까지 확장하고 재시도 정책을 정한다.
- 뉴스 품질 점수(`social/news/quality/news_quality_score.py`)를 게시 후보 선별에 연결한다.
- 운영 DB 경로는 `.env` 또는 로컬 실행 인자로만 주입하고 DB 파일은 계속 커밋하지 않는다.

## 2026-05-17 collector 구현 후속 작업

### 변경 파일 목록

- `SRC/foreign_worker_life_info_collector/social/news/collector/rss_news_collector.py`
- `SRC/foreign_worker_life_info_collector/social/news/collector/google_news_collector.py`
- `SRC/foreign_worker_life_info_collector/social/news/collector/naver_news_collector.py`
- `SRC/foreign_worker_life_info_collector/tests/test_social_news_collectors.py`
- `DOC/walkthrough/2026-05-17-news-automation.md`

### 완료한 내용

- RSS collector를 `urllib`와 `xml.etree.ElementTree` 기반으로 구현했다.
- Google News collector를 Google News RSS search URL 생성 후 RSS collector로 파싱하도록 구현했다.
- Naver News collector를 `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` 환경변수가 있을 때만 OpenAPI를 호출하도록 구현했다.
- Naver/Google/RSS collector 모두 테스트에서는 외부 네트워크 호출 없이 주입된 fetch 함수로 검증 가능하게 했다.
- 네트워크 오류, XML/JSON 파싱 오류, Naver 환경변수 누락 시 빈 결과를 반환해 기존 dry-run seed 흐름이 깨지지 않게 했다.

### 실행/검증 결과

```powershell
$env:PYTHONPATH='C:\WORK\foreign_worker_job_info\SRC'
python -m unittest discover -s SRC\foreign_worker_life_info_collector\tests
```

결과: `Ran 6 tests in 0.100s`, `OK`

```powershell
$db = Join-Path $env:TEMP 'workconnect-news-dryrun-20260517.db'
Remove-Item -LiteralPath $db -ErrorAction SilentlyContinue
$env:PYTHONPATH='C:\WORK\foreign_worker_job_info\SRC'
python -m foreign_worker_life_info_collector.social.news.pipeline --db $db --dry-run --keyword '외국인 취업 비자'
```

결과:

- 기본 실행 환경에서는 Naver credentials가 없고 Google RSS 네트워크 결과가 없어 deterministic dry-run seed 2건으로 검증됐다.
- 1건은 `PUBLISHED`, 1건은 `DUPLICATE`로 처리됐다.
- Facebook/Telegram 실제 API 호출 없이 `DRY_RUN` 로그가 생성됐다.

### 실패한 내용

- 실제 외부 뉴스 수집 결과는 로컬 검증에 포함하지 않았다. 테스트는 네트워크 의존성을 피하기 위해 fetch 함수를 주입해 검증했다.
- Naver OpenAPI는 로컬 환경변수가 없으면 호출하지 않는다.

### 다음 작업 시작점

- `social/news/quality/news_quality_score.py`를 게시 후보 선별 흐름에 연결한다.
- `news_candidate.status` 전이 규칙을 `SKIPPED`, `FAILED`까지 확장하고 실패 로그/재시도 기준을 정한다.
- 실제 Facebook/Telegram client는 환경변수 기반으로만 활성화하고, 기본값은 계속 dry-run으로 둔다.

## 2026-05-17 automated publishing pipeline 구현

### 변경 파일 목록

- `SRC/foreign_worker_life_info_collector/social/news/pipeline.py`
- `SRC/foreign_worker_life_info_collector/social/news/models.py`
- `SRC/foreign_worker_life_info_collector/social/news/normalizer/news_normalizer.py`
- `SRC/foreign_worker_life_info_collector/social/news/duplicate_guard/duplicate_detector.py`
- `SRC/foreign_worker_life_info_collector/social/news/duplicate_guard/llama_duplicate_checker.py`
- `SRC/foreign_worker_life_info_collector/social/news/summarizer/news_summarizer.py`
- `SRC/foreign_worker_life_info_collector/social/news/evaluator/candidate_evaluator.py`
- `SRC/foreign_worker_life_info_collector/social/news/publisher/facebook_publisher.py`
- `SRC/foreign_worker_life_info_collector/social/news/notifier/telegram_notifier.py`
- `SRC/foreign_worker_life_info_collector/social/facebook/page_client.py`
- `SRC/foreign_worker_life_info_collector/social/telegram/bot_client.py`
- `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py`
- `SRC/foreign_worker_life_info_collector/storage/db/migrations/schema.sql`
- `SRC/foreign_worker_life_info_collector/tests/test_social_news_pipeline.py`
- `DOC/walkthrough/2026-05-17-news-automation.md`

### 승인 플로우 제거 여부

- 코드 검색 기준 `approve`, `reject`, `keep`, `waiting_for_approval`, `approval callback`, `send_candidate_to_telegram_for_approval`, `user decision` 기반 승인 플로우는 없다.
- Telegram은 게시 전 승인 UI가 아니라 게시 결과/실패/중복 스킵 결과를 기록하고 알리는 운영 알림 채널로만 사용한다.
- 파이프라인은 `auto_select`, `auto_publish`, `notify_publish_result`, `save_publish_result` 역할을 수행한다.

### 완료한 내용

- `social/news` 아래에 summarizer, evaluator, publisher, notifier, optional local LLaMA duplicate checker 모듈을 추가했다.
- dry-run 흐름을 `collect → normalize/save → summarize → duplicate check → evaluate/auto select → Facebook publish simulation → Telegram notify simulation → DB result save`로 재구성했다.
- Naver/Google 수집 결과가 없으면 deterministic sample 후보로 dry-run을 계속 검증한다.
- `LOCAL_LLAMA_ENDPOINT`가 있을 때만 semantic duplicate advisory를 시도하고, timeout/error/unparseable 결과는 deterministic rule로 fallback한다.
- 실제 모드에서 Facebook/Telegram 환경변수가 없으면 API 호출 없이 `FAILED` 로그를 DB에 남긴다.
- `news_candidate`에 keyword, summary/evaluation/duplicate risk 관련 컬럼을 추가하고 기존 DB에도 필요한 컬럼을 보강하도록 했다.

### dry-run 결과

```powershell
$env:PYTHONPATH='C:\WORK\foreign_worker_job_info\SRC'
python -m unittest discover -s SRC\foreign_worker_life_info_collector\tests
```

결과: `Ran 7 tests in 0.170s`, `OK`

```powershell
$db = Join-Path $env:TEMP 'workconnect-news-auto-20260517.db'
Remove-Item -LiteralPath $db -ErrorAction SilentlyContinue
$env:PYTHONPATH='C:\WORK\foreign_worker_job_info\SRC'
python -m foreign_worker_life_info_collector.social.news.pipeline --db $db --dry-run --keyword '외국인 취업 비자'
```

결과:

- 후보 2건 수집/저장
- 1건은 자동 선별 후 Facebook `DRY_RUN` publish simulation
- Telegram `DRY_RUN` result notification 저장
- 최종 상태: `NOTIFIED` 1건, `DUPLICATE` 1건

### DB 저장 확인 여부

- `news_candidate`: 2건
- `facebook_publish_log`: 1건
- `telegram_notify_log`: 1건
- 상태 집계: `DUPLICATE` 1건, `NOTIFIED` 1건

### 실패한 내용

- 실제 Facebook/Telegram API 호출은 수행하지 않았다.
- 실제 local LLaMA 호출은 `LOCAL_LLAMA_ENDPOINT`가 없는 환경이므로 수행하지 않았다.
- 최초 구현에서 같은 배치의 뒤 후보가 앞 후보를 역으로 중복 처리하는 문제가 있었고, 중복 비교를 과거 후보 기준으로 제한해 수정했다.

### 다음 작업 시작점

- 실제 운영 cycle runner를 추가해 키워드 목록을 순회하고 API rate limit/backoff를 적용한다.
- `news_performance_snapshot` 수집을 Facebook Graph API 기반으로 연결한다.
- 실제 모드 검증은 로컬 환경변수와 비공개 `.env`를 준비한 뒤 공개 저장소에 값이 남지 않게 수행한다.

## 2026-05-17 legacy top-level wrapper 제거

### 변경 파일 목록

- `DOC/architecture/collector-hierarchy.md`
- `DOC/walkthrough/2026-05-17-news-automation.md`
- `SRC/foreign_worker_life_info_collector/crawler/*` 삭제
- `SRC/foreign_worker_life_info_collector/parser/*` 삭제
- `SRC/foreign_worker_life_info_collector/normalizer/*` 삭제
- `SRC/foreign_worker_life_info_collector/quality/*` 삭제

### 완료한 내용

- 최상위 `crawler`, `parser`, `normalizer`, `quality` 폴더 내부 파일을 확인했다.
- 해당 파일들은 실제 구현이 아니라 `research/*` 구현을 재수출하는 compatibility wrapper임을 확인했다.
- 내부 코드에서 최상위 legacy import 경로를 사용하지 않는 것을 확인했다.
- 최상위 legacy wrapper 폴더 4개를 제거했다.
- `SRC/foreign_worker_life_info_collector` 아래의 `__pycache__` 폴더를 삭제했다.
- `collector-hierarchy.md`에 최종 구조 기준으로 legacy wrapper 폴더를 남기지 않는다는 원칙을 반영했다.

### 실행/검증 결과

```powershell
$env:PYTHONPATH='C:\WORK\foreign_worker_job_info\SRC'
python -m foreign_worker_life_info_collector
```

결과: 정상 실행

```powershell
$env:PYTHONPATH='C:\WORK\foreign_worker_job_info\SRC'
python -m unittest discover -s SRC\foreign_worker_life_info_collector\tests
```

결과: 전체 테스트 통과

### 실패한 내용

- 없음.

### 다음 작업 시작점

- `social/news/quality/news_quality_score.py`를 게시 후보 선별 흐름에 연결한다.
- `news_candidate.status` 전이 규칙을 `SKIPPED`, `FAILED`까지 확장하고 실패 로그/재시도 기준을 정한다.
- 실제 Facebook/Telegram client는 환경변수 기반으로만 활성화하고, 기본값은 계속 dry-run으로 둔다.
