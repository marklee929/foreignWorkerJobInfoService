# Admin DB Schema Design

이 문서는 Vue admin UI를 실제 실행 데이터와 연결하기 전에 필요한 PostgreSQL 테이블 설계를 정리한다.

대상 DB는 로컬 PostgreSQL이며, 기본 database 이름은 `foreign_worker_job_info`이다. database 안에는 `admin`, `social_news` schema를 분리해서 사용한다. 실제 토큰, 비밀번호, `.env`, DB 파일은 저장하지 않는다.

## 기준 코드

확인한 backend 위치:

- `SRC/foreign_worker_life_info_collector/social/news/pipeline.py`
- `SRC/foreign_worker_life_info_collector/social/news/models.py`
- `SRC/foreign_worker_life_info_collector/social/news/repository/news_repository.py`
- `SRC/foreign_worker_life_info_collector/crew_team/social/news_bot.py`
- `SRC/foreign_worker_life_info_collector/storage/db/migrations/schema.sql`
- `SRC/foreign_worker_life_info_collector/storage/db/sqlite_client.py`

확인한 UI 위치:

- `SRC/foreign_worker_life_info_collector/admin_ui/src/App.vue`
- `SRC/foreign_worker_life_info_collector/admin_ui/src/data/defaultAdminState.js`
- `SRC/foreign_worker_life_info_collector/admin_ui/src/components/*`

현재 상태:

- Python news pipeline은 SQLite repository를 통해 `news_candidate`, `facebook_publish_log`, `telegram_notify_log`를 사용한다.
- Vue admin UI는 PostgreSQL seed와 맞춘 기본 운영 상태를 사용하며, 아직 API/DB 직접 조회는 하지 않는다.
- 이번 작업은 PostgreSQL schema 설계와 초기 seed 구조까지다.
- pipeline 코드를 PostgreSQL로 교체하지는 않는다.

## 적용 파일

- PostgreSQL DDL: `SRC/foreign_worker_life_info_collector/storage/db/migrations/admin_postgres_schema.sql`
- Seed SQL: `SRC/foreign_worker_life_info_collector/storage/db/migrations/seed_admin_config.sql`
- 초기화 스크립트: `SRC/foreign_worker_life_info_collector/scripts/init_admin_db.py`

실행 예:

```powershell
$env:POSTGRES_DSN="postgresql://postgres@localhost:5432/foreign_worker_job_info"
python SRC\foreign_worker_life_info_collector\scripts\init_admin_db.py
```

비밀번호가 필요한 경우:

```powershell
$env:PGHOST="localhost"
$env:PGPORT="5432"
$env:PGDATABASE="foreign_worker_job_info"
$env:PGUSER="postgres"
$env:PGPASSWORD="사용자 로컬 비밀번호"
python SRC\foreign_worker_life_info_collector\scripts\init_admin_db.py
```

`psycopg` 또는 `psycopg2`가 없으면 스크립트는 `psql` CLI를 fallback으로 사용한다.

## Backend 강제 규칙

DB에 저장된 module config는 UI 표시용만이 아니라 backend 실행 제어에도 사용해야 한다.

- `collector.naver=false`이면 `NaverNewsCollector.collect()`를 호출하지 않는다.
- `collector.google=false`이면 `GoogleNewsCollector.collect()`를 호출하지 않는다.
- `collector.rss=false`이면 RSS collector를 호출하지 않는다.
- `step.llama_check=false`이면 `LlamaDuplicateChecker.check()`를 호출하지 않는다.
- `publish.facebook=false`이면 `FacebookPublisher.publish()`를 호출하지 않는다.
- `notify.telegram=false`이면 Telegram notifier를 호출하지 않는다.
- `dry_run=true`이면 외부 API 호출은 simulation만 수행한다.
- real mode라도 필수 환경변수가 없으면 API 호출 전에 실패 처리한다.

## ER 흐름

```text
admin.module_config
admin.runtime_config
admin.env_status

social_news.pipeline_cycle
-> social_news.pipeline_step_log
-> social_news.pipeline_error_log
-> social_news.raw_item
-> social_news.normalized_item
-> social_news.candidate
-> social_news.publish_log
-> social_news.telegram_notify_log
```

## 테이블 설계

### admin.module_config

목적:

- UI on/off toggle과 backend 실행 제어의 기준 테이블
- collector, step, publish, notify 모듈의 활성화 상태 저장

주요 컬럼:

| 컬럼 | 타입 | Null | 기본값 | 설명 |
|---|---|---:|---|---|
| id | BIGINT IDENTITY | N | | PK |
| module_key | VARCHAR(120) | N | | `collector.naver` 같은 고유 키 |
| module_group | VARCHAR(60) | N | | collector, step, publish, notify |
| module_name | VARCHAR(120) | N | | UI 표시명 |
| description | TEXT | Y | | 설명 |
| is_enabled | BOOLEAN | N | false | 실행 가능 여부 |
| is_required | BOOLEAN | N | false | 필수 단계 여부 |
| run_order | INTEGER | N | 100 | 실행 순서 |
| config_json | JSONB | N | `{}` | adapter 이름 등 확장 설정 |
| created_at | TIMESTAMPTZ | N | now | 생성일 |
| updated_at | TIMESTAMPTZ | N | now | 수정일 |

PK:

- `id`

Unique:

- `module_key`

Index:

- `(module_group, is_enabled, run_order)`

UI 매핑:

- Sidebar 모듈 상태
- BotMonitorCard 활성 모듈 수
- 모듈 on/off toggle 영역

Backend 매핑:

- `NewsPipeline` collector/step 선택
- 향후 `/api/admin/modules`
- 향후 `/api/social/news/cycles` 실행 전 validation

### admin.runtime_config

목적:

- 기본 keyword, limit, dry-run 기본값, UI refresh interval 등 운영 설정 저장
- 민감값은 저장하지 않고 `is_sensitive=true`일 경우 존재 여부만 관리한다.

주요 컬럼:

| 컬럼 | 타입 | Null | 기본값 | 설명 |
|---|---|---:|---|---|
| id | BIGINT IDENTITY | N | | PK |
| config_key | VARCHAR(120) | N | | 설정 키 |
| config_value | TEXT | Y | | 설정값 |
| value_type | VARCHAR(30) | N | string | string, integer, boolean 등 |
| is_sensitive | BOOLEAN | N | false | 민감값 여부 |
| description | TEXT | Y | | 설명 |
| updated_by | VARCHAR(120) | Y | | 수정자 |
| created_at | TIMESTAMPTZ | N | now | 생성일 |
| updated_at | TIMESTAMPTZ | N | now | 수정일 |

PK:

- `id`

Unique:

- `config_key`

UI 매핑:

- Header 검색 기본값
- dry-run 기본 toggle
- dashboard polling interval

Backend 매핑:

- `news_bot.py` 기본 keyword/limit 대체 후보
- API adapter의 runtime config 조회

### admin.env_status

목적:

- 외부 연동에 필요한 환경변수의 존재 여부와 상태 저장
- 실제 token 값은 절대 저장하지 않는다.

주요 컬럼:

| 컬럼 | 타입 | Null | 기본값 | 설명 |
|---|---|---:|---|---|
| id | BIGINT IDENTITY | N | | PK |
| env_key | VARCHAR(120) | N | | 환경변수명 |
| module_key | VARCHAR(120) | Y | | 연결 모듈 |
| is_required | BOOLEAN | N | false | 필수 여부 |
| is_configured | BOOLEAN | N | false | 존재 여부 |
| status | VARCHAR(40) | N | UNKNOWN | READY, MISSING, UNKNOWN |
| checked_at | TIMESTAMPTZ | Y | | 확인 시각 |
| message | TEXT | Y | | UI 표시 메시지 |

FK:

- `module_key -> admin.module_config(module_key)`

Index:

- `(module_key, status)`

UI 매핑:

- Header LLaMA 상태
- BotMonitorCard Facebook/Telegram readiness
- StatusCard 실패/대기 항목

Backend 매핑:

- real publish 전 env validation
- `/api/llama/health`
- `/api/admin/env-status`

### social_news.pipeline_cycle

목적:

- 한 번의 뉴스 자동화 실행 단위를 저장한다.
- UI compact report, 상태 카드, 최근 실행 결과의 기준이다.

주요 컬럼:

| 컬럼 | 타입 | Null | 기본값 | 설명 |
|---|---|---:|---|---|
| id | BIGINT IDENTITY | N | | PK |
| cycle_key | VARCHAR(80) | N | | 실행 고유 키 |
| keyword | VARCHAR(300) | N | | 검색 keyword |
| dry_run | BOOLEAN | N | true | dry-run 여부 |
| requested_by | VARCHAR(120) | Y | | CLI, admin user 등 |
| trigger_source | VARCHAR(60) | N | CLI | CLI, UI, SCHEDULER |
| status | VARCHAR(40) | N | PENDING | RUNNING, COMPLETED, FAILED |
| enabled_modules | JSONB | N | `{}` | 실행 당시 모듈 활성화 snapshot |
| collected_count | INTEGER | N | 0 | 수집 수 |
| saved_count | INTEGER | N | 0 | 저장 수 |
| duplicate_count | INTEGER | N | 0 | 중복 수 |
| skipped_count | INTEGER | N | 0 | 제외 수 |
| selected_count | INTEGER | N | 0 | 선택 수 |
| started_at | TIMESTAMPTZ | N | now | 시작 |
| ended_at | TIMESTAMPTZ | Y | | 종료 |
| compact_report | TEXT | Y | | CLI/report 텍스트 |
| error_message | TEXT | Y | | 실패 요약 |

Index:

- `started_at DESC`
- `(status, dry_run)`

UI 매핑:

- StatusCard: 수집 뉴스, 중복 제외, 실패 작업
- BotMonitorCard: pipeline metrics
- LogPanel: cycle 단위 실행 로그

Backend 매핑:

- `NewsPipeline.run()` 시작/종료 기록
- 향후 `POST /api/social/news/cycles`

### social_news.pipeline_step_log

목적:

- 각 cycle 안의 단계별 실행 결과 저장
- 비활성화된 모듈은 `SKIPPED`로 기록하거나 기록하지 않을 수 있으나, 운영 추적을 위해 기록을 권장한다.

주요 컬럼:

| 컬럼 | 타입 | Null | 기본값 | 설명 |
|---|---|---:|---|---|
| id | BIGINT IDENTITY | N | | PK |
| cycle_id | BIGINT | N | | 실행 cycle |
| module_key | VARCHAR(120) | N | | 실행 모듈 |
| step_name | VARCHAR(120) | N | | 단계명 |
| status | VARCHAR(40) | N | PENDING | RUNNING, SUCCESS, SKIPPED, FAILED |
| input_count | INTEGER | N | 0 | 입력 수 |
| output_count | INTEGER | N | 0 | 출력 수 |
| skipped_reason | TEXT | Y | | 비활성화/조건 미충족 사유 |
| started_at | TIMESTAMPTZ | N | now | 시작 |
| ended_at | TIMESTAMPTZ | Y | | 종료 |
| duration_ms | INTEGER | Y | | 수행 시간 |
| detail_json | JSONB | N | `{}` | 상세 payload |

FK:

- `cycle_id -> social_news.pipeline_cycle(id)`
- `module_key -> admin.module_config(module_key)`

Index:

- `(cycle_id, started_at)`
- `(module_key, status)`

UI 매핑:

- Bot table의 status, count, success, fail
- LogPanel의 단계별 기록

Backend 매핑:

- `collect`, `normalize`, `summarize`, `duplicate_check`, `candidate_evaluation`, `publish`, `notify`

### social_news.pipeline_error_log

목적:

- 예외와 실패 사유를 별도로 저장한다.
- 운영자는 raw traceback 대신 summary를 먼저 본다.

주요 컬럼:

| 컬럼 | 타입 | Null | 기본값 | 설명 |
|---|---|---:|---|---|
| id | BIGINT IDENTITY | N | | PK |
| cycle_id | BIGINT | Y | | cycle |
| step_log_id | BIGINT | Y | | step |
| module_key | VARCHAR(120) | Y | | 모듈 |
| severity | VARCHAR(30) | N | ERROR | WARN, ERROR |
| error_code | VARCHAR(80) | Y | | 코드 |
| error_message | TEXT | N | | 메시지 |
| stack_trace | TEXT | Y | | 개발자용 trace |
| context_json | JSONB | N | `{}` | context |
| occurred_at | TIMESTAMPTZ | N | now | 발생 시각 |

FK:

- `cycle_id -> social_news.pipeline_cycle(id)`
- `step_log_id -> social_news.pipeline_step_log(id)`
- `module_key -> admin.module_config(module_key)`

Index:

- `(cycle_id, occurred_at DESC)`

UI 매핑:

- LogPanel error row
- StatusCard 실패 작업

Backend 매핑:

- pipeline exception handling
- env validation 실패
- external API 실패

### social_news.raw_item

목적:

- collector가 가져온 원본 뉴스 후보 저장
- 수집기별 결과와 원문 payload 추적

주요 컬럼:

| 컬럼 | 타입 | Null | 기본값 | 설명 |
|---|---|---:|---|---|
| id | BIGINT IDENTITY | N | | PK |
| cycle_id | BIGINT | Y | | cycle |
| collector_module_key | VARCHAR(120) | N | | collector.naver 등 |
| source_type | VARCHAR(80) | N | | naver, google, rss |
| source_url | TEXT | Y | | URL |
| source_name | VARCHAR(200) | Y | | KBS 뉴스 등 |
| search_keyword | VARCHAR(300) | N | | 검색어 |
| raw_title | TEXT | N | | 원본 title |
| raw_summary | TEXT | Y | | 원본 summary |
| raw_content | TEXT | Y | | 원본 content |
| language | VARCHAR(20) | N | ko | 언어 |
| category | VARCHAR(120) | Y | | 카테고리 |
| collected_at | TIMESTAMPTZ | N | now | 수집 시각 |
| hash_key | VARCHAR(128) | N | | 원본 중복 key |
| raw_payload | JSONB | N | `{}` | 원본 JSON |

FK:

- `cycle_id -> social_news.pipeline_cycle(id)`
- `collector_module_key -> admin.module_config(module_key)`

Unique/Index:

- unique `hash_key`
- `(cycle_id, collector_module_key)`

UI 매핑:

- 상세 분석 Raw Text
- 수집 뉴스 count

Backend 매핑:

- `NaverNewsCollector`, `GoogleNewsCollector`, `RssNewsCollector`

### social_news.normalized_item

목적:

- HTML 제거, canonical URL, source name, hash, similarity key 생성 후 저장

주요 컬럼:

| 컬럼 | 타입 | Null | 기본값 | 설명 |
|---|---|---:|---|---|
| id | BIGINT IDENTITY | N | | PK |
| raw_item_id | BIGINT | Y | | 원본 |
| cycle_id | BIGINT | Y | | cycle |
| source_type | VARCHAR(80) | N | | source |
| source_url | TEXT | Y | | 원본 URL |
| canonical_url | TEXT | Y | | 정규 URL |
| source_name | VARCHAR(200) | Y | | source name |
| title | TEXT | N | | 정규 title |
| summary | TEXT | Y | | plain summary |
| content | TEXT | Y | | plain content |
| language | VARCHAR(20) | N | ko | 언어 |
| category | VARCHAR(120) | Y | | 카테고리 |
| keyword | VARCHAR(300) | Y | | keyword |
| hash_key | VARCHAR(128) | N | | hash |
| title_hash | VARCHAR(128) | Y | | title hash |
| similarity_key | VARCHAR(300) | Y | | 유사도 key |
| normalized_at | TIMESTAMPTZ | N | now | 정규화 시각 |

FK:

- `raw_item_id -> social_news.raw_item(id)`
- `cycle_id -> social_news.pipeline_cycle(id)`

Unique/Index:

- unique `hash_key`
- `similarity_key`

UI 매핑:

- 후보 테이블의 title/source/region/category
- 상세 분석의 정제 텍스트

Backend 매핑:

- `normalizer/news_normalizer.py`

### social_news.candidate

목적:

- 평가, 중복검사, 자동 선택, 게시 상태의 중심 테이블
- 기존 SQLite `news_candidate`를 PostgreSQL 운영 모델로 확장한 구조

주요 컬럼:

| 컬럼 | 타입 | Null | 기본값 | 설명 |
|---|---|---:|---|---|
| id | BIGINT IDENTITY | N | | PK |
| normalized_item_id | BIGINT | Y | | normalized item |
| cycle_id | BIGINT | Y | | cycle |
| source_type | VARCHAR(80) | N | | source |
| source_url | TEXT | Y | | URL |
| canonical_url | TEXT | Y | | canonical URL |
| source_name | VARCHAR(200) | Y | | source name |
| title | TEXT | N | | title |
| summary | TEXT | Y | | summary |
| content | TEXT | Y | | content |
| language | VARCHAR(20) | N | ko | language |
| category | VARCHAR(120) | Y | | category |
| keyword | VARCHAR(300) | Y | | keyword |
| hash_key | VARCHAR(128) | Y | | URL/content hash |
| title_hash | VARCHAR(128) | Y | | title hash |
| similarity_key | VARCHAR(300) | Y | | duplicate key |
| short_summary | TEXT | Y | | 요약 |
| key_points | TEXT | Y | | 핵심 포인트 |
| relevance_reason | TEXT | Y | | 관련성 이유 |
| risk_notes | TEXT | Y | | 위험/중복 note |
| evaluation_score | NUMERIC(6,4) | N | 0 | 총점 |
| duplicate_risk_score | NUMERIC(6,4) | N | 0 | 중복 위험 |
| foreign_worker_relevance_score | NUMERIC(6,4) | N | 0 | 외국인 노동자 관련성 |
| korea_relevance_score | NUMERIC(6,4) | N | 0 | 한국 관련성 |
| visa_or_labor_policy_score | NUMERIC(6,4) | N | 0 | 비자/노동정책 관련성 |
| freshness_score | NUMERIC(6,4) | N | 0 | 최신성 |
| source_reliability_score | NUMERIC(6,4) | N | 0 | 출처 신뢰도 |
| content_clarity_score | NUMERIC(6,4) | N | 0 | 내용 명확도 |
| facebook_post_suitability_score | NUMERIC(6,4) | N | 0 | Facebook 적합도 |
| selection_reason | TEXT | Y | | 선택 이유 |
| skip_reason | TEXT | Y | | 제외 이유 |
| duplicate_group_id | BIGINT | Y | | 중복 그룹 |
| status | VARCHAR(40) | N | CANDIDATE | 상태 |
| collected_at | TIMESTAMPTZ | N | now | 수집 시각 |
| published_at | TIMESTAMPTZ | Y | | 게시 시각 |
| created_at | TIMESTAMPTZ | N | now | 생성 |
| updated_at | TIMESTAMPTZ | N | now | 수정 |

FK:

- `normalized_item_id -> social_news.normalized_item(id)`
- `cycle_id -> social_news.pipeline_cycle(id)`
- `duplicate_group_id -> news_candidate(id)`

Index:

- `(cycle_id, status)`
- `evaluation_score DESC`
- `hash_key`
- `similarity_key`

UI 매핑:

- DataTable 후보 row
- Detail inspector
- StatusCard 중복/스킵/게시 수
- Category Mix

Backend 매핑:

- `models.NewsCandidate`
- `NewsRepository.save/update_candidate/list_candidates`
- `CandidateEvaluator`
- `DuplicateDetector`

### social_news.publish_log

목적:

- Facebook 등 외부 social publish 결과 저장
- 기존 `facebook_publish_log`를 channel 확장형으로 일반화

주요 컬럼:

| 컬럼 | 타입 | Null | 기본값 | 설명 |
|---|---|---:|---|---|
| id | BIGINT IDENTITY | N | | PK |
| cycle_id | BIGINT | Y | | cycle |
| news_candidate_id | BIGINT | N | | 후보 |
| channel | VARCHAR(60) | N | facebook | publish channel |
| page_id | VARCHAR(200) | Y | | page id reference |
| external_post_id | VARCHAR(200) | Y | | Facebook post id 등 |
| dry_run | BOOLEAN | N | true | dry-run 여부 |
| status | VARCHAR(40) | N | | DRY_RUN, PUBLISHED, FAILED |
| request_payload | JSONB | N | `{}` | 민감정보 제외 request |
| response_payload | JSONB | N | `{}` | response |
| error_code | VARCHAR(80) | Y | | error code |
| error_message | TEXT | Y | | error |
| published_at | TIMESTAMPTZ | N | now | 시각 |

FK:

- `cycle_id -> social_news.pipeline_cycle(id)`
- `news_candidate_id -> news_candidate(id)`

Index:

- `(news_candidate_id, published_at DESC)`
- `(channel, status, dry_run)`

UI 매핑:

- 게시 결과 확인 버튼
- BotMonitorCard publish status
- LogPanel publish error

Backend 매핑:

- `publisher/facebook_publisher.py`
- 기존 `insert_facebook_log`의 PostgreSQL 대체 대상

### social_news.telegram_notify_log

목적:

- Telegram 결과 알림 저장
- 승인 UI가 아니라 운영 알림 로그만 저장한다.

주요 컬럼:

| 컬럼 | 타입 | Null | 기본값 | 설명 |
|---|---|---:|---|---|
| id | BIGINT IDENTITY | N | | PK |
| cycle_id | BIGINT | Y | | cycle |
| news_candidate_id | BIGINT | Y | | 후보 |
| chat_id_ref | VARCHAR(120) | Y | | chat id reference, 실제 값 저장 금지 권장 |
| dry_run | BOOLEAN | N | true | dry-run 여부 |
| message | TEXT | N | | 알림 메시지 |
| status | VARCHAR(40) | N | | DRY_RUN, NOTIFIED, FAILED |
| error_message | TEXT | Y | | 실패 이유 |
| sent_at | TIMESTAMPTZ | N | now | 전송 시각 |

FK:

- `cycle_id -> social_news.pipeline_cycle(id)`
- `news_candidate_id -> news_candidate(id)`

Index:

- `(news_candidate_id, sent_at DESC)`
- `(status, dry_run)`

UI 매핑:

- LogPanel
- BotMonitorCard Telegram status

Backend 매핑:

- `notifier/telegram_notifier.py`
- 기존 `insert_telegram_log`의 PostgreSQL 대체 대상

## Seed Data

초기 seed는 `seed_admin_config.sql`에 있다.

포함 모듈:

- `collector.naver`
- `collector.google`
- `collector.rss`
- `step.normalize`
- `step.summarize`
- `step.duplicate_check`
- `step.llama_check`
- `step.candidate_evaluation`
- `publish.facebook`
- `notify.telegram`

초기 정책:

- Naver/Google collector는 enabled
- RSS collector는 disabled
- normalize, duplicate_check, candidate_evaluation은 enabled + required
- summarize는 enabled
- LLaMA check는 disabled
- Facebook publish는 disabled
- Telegram notify는 disabled
- dry-run 기본값은 true

## 다음 작업

1. PostgreSQL repository adapter를 추가한다.
2. `NewsPipeline`이 `enabledModules`를 인자로 받도록 변경한다.
3. `admin.module_config`를 읽어 disabled module을 호출하지 않게 한다.
4. API adapter를 추가한다.
5. Vue 기본 운영 상태를 API fallback 구조로 전환한다.
6. 비활성화된 모듈이 호출되지 않는 테스트를 작성한다.
