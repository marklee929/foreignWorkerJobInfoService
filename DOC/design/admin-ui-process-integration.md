# Admin UI Process and Module Integration

## Harness Status

Status: legacy design reference.

This document was written before the current PostgreSQL/admin API/content-hub architecture was fully reflected in `DOC/architecture` and `DOC/database`.

Use the following as current references before implementing any item from this document:

- `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
- `DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`
- `DOC/architecture/06_WORK_AREA_REGISTRY.md`
- `DOC/database/00_DB_ARCHITECTURE_INDEX.md`
- `DOC/database/01_CURRENT_DB_MAP.md`
- `DOC/database/03_CONTENT_CURRENT.md`

Known outdated assumptions:

- SQLite is described as the runtime repository in several places.
- The admin UI is described as not connected to backend APIs.
- Direct social-news publishing appears as a main pipeline path.

Do not implement from this document directly. Convert any actionable item into a `CODE_TASK_CANDIDATE` first.

이 문서는 `SRC/foreign_worker_life_info_collector` 전체 기준으로 Web UI, CrewTeam, social/news 파이프라인, 저장소 모듈이 어떻게 연결되어야 하는지 정리한다.

현재 Vue 관리자 화면은 개발 가능한 프론트엔드 초안이며, 아직 Python 파이프라인이나 DB와 직접 연결되어 있지 않다. UI는 `admin_ui/src/data/defaultAdminState.js`의 기본 운영 상태를 사용하고, 실제 동작은 `run.bat` 또는 Python CLI를 통해 실행된다.

## 현재 실행 구조

### 실제 동작하는 CLI 흐름

```text
run.bat
-> python -m foreign_worker_life_info_collector.crew_team.social.news_bot
-> crew_team/social/news_bot.py
-> social/news/pipeline.py
-> collector / normalizer / summarizer / duplicate_guard / evaluator
-> publisher / notifier / repository
-> SQLite DB
```

기본 실행은 dry-run이다.

```powershell
run.bat
```

실제 Facebook/Telegram API 호출은 환경변수가 준비된 상태에서 명시적으로 real mode를 켰을 때만 허용한다.

```powershell
run.bat --real
```

### 현재 Web UI 흐름

```text
admin_ui/src/main.js
-> admin_ui/src/App.vue
-> components/*
-> data/defaultAdminState.js
```

현재 UI는 다음을 하지 않는다.

- Python 파이프라인 실행
- SQLite DB 조회
- Facebook API 호출
- Telegram API 호출
- local LLaMA health check
- scheduler 시작/중지
- 실시간 로그 tailing

즉, 현재 UI는 "운영 화면 디자인과 컴포넌트 구조"만 준비된 상태다.

## 모듈별 책임

### admin_ui

위치: `SRC/foreign_worker_life_info_collector/admin_ui`

역할:

- Vue 3 + Vite + Tailwind 기반 관리자 화면
- 운영자가 뉴스 파이프라인 상태, 후보, 로그, 봇 상태를 확인할 화면
- 추후 API 연동을 위한 컴포넌트 구조 제공

현재 상태:

- PostgreSQL seed와 맞춘 기본 운영 상태 렌더링
- API client 없음
- 버튼은 실제 backend action에 연결되지 않음

### crew_team/social

위치: `SRC/foreign_worker_life_info_collector/crew_team/social`

역할:

- 사용자가 실행하는 entrypoint
- CLI argument 처리
- social/news 파이프라인 호출
- compact report 또는 JSON 출력

중요 원칙:

- 직접 수집, 게시, 저장 로직을 길게 구현하지 않는다.
- 실제 기능은 `social/news`, `social/facebook`, `social/telegram`, `storage` 계층에 둔다.

### social/news

위치: `SRC/foreign_worker_life_info_collector/social/news`

역할:

- 뉴스 후보 수집
- 정규화
- 요약
- 중복 검사
- 후보 평가
- 자동 후보 선택
- dry-run 또는 real publish
- Telegram 결과 알림
- DB 저장

현재 파이프라인:

```text
collect
-> save_normalized
-> summarize
-> duplicate check
-> evaluate
-> auto_select
-> auto_publish
-> notify_publish_result
-> save publish/notify logs
```

주요 파일:

- `pipeline.py`: 전체 실행 흐름
- `models.py`: `NewsItem`, `NewsCandidate`, 평가/중복 결과 모델
- `collector/*`: Naver, Google, RSS 뉴스 수집기
- `normalizer/news_normalizer.py`: HTML 제거, source name 분리, hash/similarity key 생성
- `summarizer/news_summarizer.py`: rule-based summary, optional local LLaMA summary
- `duplicate_guard/duplicate_detector.py`: URL/hash/similarity/date-keyword 중복 검사
- `duplicate_guard/llama_duplicate_checker.py`: optional local LLaMA semantic duplicate advisory
- `evaluator/candidate_evaluator.py`: 한국 관련성, 외국인 노동자 관련성, 비자/노동정책 점수 계산
- `publisher/facebook_publisher.py`: Facebook 게시 또는 dry-run simulation
- `notifier/telegram_notifier.py`: 게시 결과 알림 또는 dry-run simulation
- `repository/news_repository.py`: SQLite 저장, 상태 업데이트, publish/notify log 저장

### social/facebook

역할:

- Facebook Page API client
- post message builder
- publish log 보조

현재 주의점:

- dry-run에서는 실제 API를 호출하지 않는다.
- real mode에서는 `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_ACCESS_TOKEN`이 필요하다.

### social/telegram

역할:

- Telegram Bot API client
- 운영 알림 전송

현재 원칙:

- Telegram은 승인 UI가 아니다.
- approve/reject/keep 흐름을 되살리지 않는다.
- 게시 결과, 실패 사유, 중복 스킵 결과만 알린다.

### research

위치: `SRC/foreign_worker_life_info_collector/research`

역할:

- 생활정보 원천 데이터 수집, 파싱, 정규화, 품질 평가

현재 UI 연결 상태:

- admin UI와 직접 연결되어 있지 않다.
- `python -m foreign_worker_life_info_collector` 기본 실행과 연관될 수 있으나, social/news 자동 게시 파이프라인과는 별도 흐름이다.

## UI와 모듈 연결 상태

| UI 영역 | 현재 상태 | 연결 대상 | 현재 동작 |
|---|---|---|---|
| Sidebar | 기본 navigation | future router/module filter | 화면 표시만 함 |
| Header search | 기본 keyword | future search/filter API | 실행 없음 |
| KPI status cards | 기본 운영 상태 | `/api/dashboard/summary` | DB 조회 없음 |
| Bot monitor | 기본 모듈 상태 | `/api/bots/status` | 실제 bot 상태 조회 없음 |
| LLaMA status | 기본 비활성 상태 | `/api/llama/health` | endpoint 확인 없음 |
| News pipeline metrics | 기본 준비 상태 | `/api/social/news/cycles/latest` | 최근 실행 결과 조회 없음 |
| DataTable | seed 기반 모듈 rows | `/api/social/news/candidates` | DB row 조회 없음 |
| LogPanel | 기본 준비 로그 | `/api/logs/recent` | 실제 로그 tailing 없음 |
| Detail panel | 빈 후보 상태 | `/api/social/news/candidates/{id}` | 선택 row 연동 없음 |
| 실행 버튼 | no-op | `POST /api/social/news/cycles` | 파이프라인 실행 안 함 |
| export 버튼 | no-op | future export API | 파일 생성 안 함 |

## 활성화 기반 실행 원칙

사용자가 요청한 핵심 규칙은 다음이다.

```text
UI에서 활성화한 모듈만 실행한다.
UI에서 비활성화한 모듈은 backend에서도 절대 실행하지 않는다.
```

이 규칙은 frontend 표시만으로 보장하면 안 된다. backend 파이프라인에서도 같은 설정을 검증해야 한다.

### 권장 실행 설정 모델

```json
{
  "dryRun": true,
  "keyword": "외국인 취업 비자",
  "enabledModules": {
    "collectors": {
      "naver": true,
      "google": true,
      "rss": false
    },
    "steps": {
      "normalize": true,
      "summarize": true,
      "duplicateCheck": true,
      "llamaCheck": false,
      "candidateEvaluation": true,
      "facebookPublish": false,
      "telegramNotify": false
    }
  }
}
```

### backend 강제 규칙

- `facebookPublish=false`이면 `FacebookPublisher.publish()`를 호출하지 않는다.
- `telegramNotify=false`이면 `NewsTelegramNotifier.notify_publish_result()`를 호출하지 않는다.
- `llamaCheck=false`이면 `LlamaDuplicateChecker.check()`를 호출하지 않는다.
- `collectors.naver=false`이면 `NaverNewsCollector.collect()`를 호출하지 않는다.
- `collectors.google=false`이면 `GoogleNewsCollector.collect()`를 호출하지 않는다.
- `dryRun=true`이면 외부 API 호출은 모두 simulation으로 처리한다.
- `dryRun=false`라도 필수 환경변수가 없으면 API 호출 전에 실패 처리한다.
- UI 버튼이 비활성화되어 있어도 backend endpoint는 별도로 권한과 module flag를 검증한다.

### 상태값 기준

현재 social/news 파이프라인에서 사용하는 상태값:

```text
CANDIDATE
NORMALIZED
SUMMARIZED
DUPLICATE
SKIPPED
READY_TO_PUBLISH
DRY_RUN_PUBLISHED
PUBLISHED
FAILED
DRY_RUN_NOTIFIED
NOTIFIED
```

UI 표시 기준:

- `READY_TO_PUBLISH`: 게시 직전 후보
- `DRY_RUN_PUBLISHED`: dry-run Facebook simulation 완료
- `DRY_RUN_NOTIFIED`: dry-run Telegram simulation 완료
- `PUBLISHED`: 실제 Facebook 게시 완료
- `NOTIFIED`: 실제 Telegram 결과 알림 완료
- `DUPLICATE`: 중복으로 제외
- `SKIPPED`: 점수 또는 관련성이 낮아 제외
- `FAILED`: 환경변수 누락, API 실패, 예외 발생

## 권장 API 경계

현재는 API layer가 없다. Vue UI와 Python 모듈을 연결하려면 얇은 HTTP adapter가 필요하다.

권장 위치:

```text
SRC/foreign_worker_life_info_collector/api/
  app.py
  routes/
    dashboard.py
    news.py
    bots.py
    logs.py
    modules.py
```

권장 endpoint:

```http
GET /api/admin/modules
PATCH /api/admin/modules/{module_id}
GET /api/dashboard/summary
GET /api/social/news/cycles/latest
POST /api/social/news/cycles
GET /api/social/news/candidates
GET /api/social/news/candidates/{id}
GET /api/logs/recent
GET /api/llama/health
```

### `POST /api/social/news/cycles`

요청 예시:

```json
{
  "keyword": "외국인 취업 비자",
  "dryRun": true,
  "limit": 1,
  "enabledModules": {
    "collectors": {
      "naver": true,
      "google": true,
      "rss": false
    },
    "steps": {
      "summarize": true,
      "duplicateCheck": true,
      "llamaCheck": false,
      "facebookPublish": false,
      "telegramNotify": false
    }
  }
}
```

응답 예시:

```json
{
  "dryRun": true,
  "collectedCount": 10,
  "savedCount": 10,
  "duplicateCount": 0,
  "skippedCount": 9,
  "selectedCount": 1,
  "selectedCandidate": {
    "id": 12,
    "title": "외국인 취업비자 개편",
    "sourceName": "KBS 뉴스",
    "score": 0.91,
    "status": "DRY_RUN_NOTIFIED",
    "selectionReason": "한국 내 외국인 취업비자 제도 개편과 직접 관련"
  }
}
```

## 아직 연결 안 된 부분

현재 기준으로 명확히 미연결인 부분:

- Vue UI에서 Python 파이프라인 실행
- Vue UI에서 SQLite DB 조회
- Vue UI에서 최근 실행 결과 표시
- Vue UI에서 후보 row 선택 후 상세 정보 표시
- Vue UI에서 로그 tailing
- Vue UI에서 LLaMA endpoint health check
- Vue UI에서 Facebook/Telegram env readiness 표시
- UI module toggle 값이 `NewsPipeline` 실행 옵션으로 전달되는 구조
- `NewsPipeline` 내부에서 collector/step별 활성화 flag를 받아 selective execution하는 구조
- scheduler 또는 continuous cycle runner
- admin 권한/인증
- 실패한 cycle 재시도 버튼

## 지금 바로 동작하는 것

### CLI

```powershell
run.bat
```

동작:

- social news dry-run 실행
- 후보 수집 또는 fallback sample 처리
- DB 저장
- normalize
- summarize
- duplicate check
- candidate evaluation
- dry-run Facebook publish simulation
- dry-run Telegram notify simulation
- compact report 출력

### Vue UI

```powershell
cd SRC\foreign_worker_life_info_collector\admin_ui
npm install
npm run dev
```

동작:

- Vite dev server 실행
- Stitch 디자인 기반 dashboard 렌더링
- 기본 운영 상태 표시

동작하지 않는 것:

- 실제 뉴스 파이프라인 실행
- 실제 DB 조회
- 실제 API 호출
- 실제 bot 상태 제어

## 다음 구현 순서

1. Python API adapter를 추가한다.
2. `GET /api/dashboard/summary`를 DB read-only로 구현한다.
3. `POST /api/social/news/cycles`를 dry-run 전용으로 먼저 구현한다.
4. `NewsPipeline`에 `enabledModules` 옵션을 추가한다.
5. 비활성화된 collector/step이 호출되지 않는 테스트를 작성한다.
6. Vue에 `src/services/apiClient.js`를 추가한다.
7. `defaultAdminState.js` 기본 상태를 API response fallback 구조로 전환한다.
8. 실행 버튼은 기본 dry-run만 연결한다.
9. real publish toggle은 별도 admin-only control로 분리한다.
10. Facebook/Telegram real mode는 env validation과 이중 확인 후에만 허용한다.

## 커밋 제외 대상

다음은 커밋하지 않는다.

- `.env`
- `*.db`
- `logs/*`
- `node_modules/`
- `dist/`
- `storage/cache/*`
- `storage/raw/*`
- `storage/state/*`

커밋 가능한 대상:

- Vue source
- `package.json`
- `package-lock.json`
- Tailwind/Vite config
- Python API adapter source
- architecture/design 문서
