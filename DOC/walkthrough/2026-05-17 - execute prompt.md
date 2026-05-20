### 타임스탬프 수정내용 ###

작업 대상:
C:\WORK\foreign_worker_job_info\SRC\foreign_worker_life_info_collector

GitHub:
marklee929/foreignWorkerJobInfoService

목표:
현재 foreign_worker_life_info_collector의 폴더 하이어라키를 기능/도메인/저장소/외부채널 기준으로 재정리한다.
이번 작업은 “뉴스 자동화 파이프라인 구현 전 구조 정리”가 목적이다.

중요:
- Spring Boot 프로젝트인 SRC/ForeignWorkerJobInfoService는 건드리지 않는다.
- 작업 대상은 SRC/foreign_worker_life_info_collector 내부만이다.
- 민감정보, 토큰, API 키, .env 파일은 절대 커밋하지 않는다.
- 기존 파일은 바로 삭제하지 말고 이동/래핑 방식으로 정리한다.
- import 경로가 깨지지 않도록 수정한다.
- 가능한 경우 기존 기능이 동작하도록 backward compatibility wrapper를 둔다.
- 작업 후 git status를 확인하고, 변경 내용을 commit/push까지 수행한다.

현재 문제:
최상위에 config, crawler, crew_team, logs, normalizer, parser, quality, storage 등이 평면적으로 놓여 있다.
이 상태에서는 “기능 레이어”와 “데이터 정체성/도메인”이 섞일 가능성이 크다.

정리 원칙:
1. config는 프로젝트 운영 설정 담당
2. crew_team은 각 작업을 수행하는 봇/오케스트레이터 계층
3. research는 데이터 수집·검증·정규화 기능 계층
4. crawler는 research 아래로 이동
5. parser는 research 아래로 이동
6. 비즈니스 데이터 normalizer는 research 아래로 이동
7. 공통 문자열/URL/hash/date normalizer는 utils 아래로 이동
8. social은 Facebook, Telegram, Naver 등 외부 채널 배포/연동 계층
9. 뉴스는 Facebook Page 운영에 종속된 social 콘텐츠이므로 social/news 아래로 둔다
10. Telegram은 현재 게시 결과 알림/운영 알림 담당이므로 social/telegram 아래로 둔다
11. domains는 데이터의 실제 정체성/카테고리 계층
12. storage는 DB, JSON cache, runtime state, raw data 담당
13. logs는 서버/작업 실행 로그만 담당
14. quality는 최상위 폴더로 두지 말고 research/quality 또는 social/news/quality로 분리한다

목표 하이어라키:

SRC/foreign_worker_life_info_collector/
  config/
    __init__.py
    settings.py
    keywords.py
    sources.py
    social_channels.py

  crew_team/
    __init__.py
    social/
      __init__.py
      news_bot.py
      facebook_publish_bot.py
      telegram_notify_bot.py
    research/
      __init__.py
      collector_bot.py
      verifier_bot.py
      normalizer_bot.py
    lifestyle/
      __init__.py
      immigration_bot.py
      labor_bot.py
      hospital_bot.py
      housing_bot.py

  social/
    __init__.py
    facebook/
      __init__.py
      page_client.py
      post_builder.py
      publish_log.py
    telegram/
      __init__.py
      bot_client.py
      notifier.py
    news/
      __init__.py
      models.py
      pipeline.py
      collector/
        __init__.py
        naver_news_collector.py
        google_news_collector.py
        rss_news_collector.py
      normalizer/
        __init__.py
        news_normalizer.py
      duplicate_guard/
        __init__.py
        duplicate_detector.py
      quality/
        __init__.py
        news_quality_score.py
      repository/
        __init__.py
        news_repository.py

  research/
    __init__.py
    pipeline.py
    crawler/
      __init__.py
      naver_search_collector.py
      google_search_collector.py
      local_site_collector.py
    parser/
      __init__.py
      business_info_parser.py
      contact_parser.py
      address_parser.py
      language_parser.py
    normalizer/
      __init__.py
      business_normalizer.py
      region_normalizer.py
      duplicate_detector.py
    quality/
      __init__.py
      quality_score_calculator.py
      stale_data_detector.py
      source_reliability_checker.py
    repository/
      __init__.py
      research_repository.py

  domains/
    __init__.py
    immigration/
      __init__.py
    labor/
      __init__.py
    hospital/
      __init__.py
    housing/
      __init__.py
    translation/
      __init__.py
    local_support/
      __init__.py

  storage/
    __init__.py
    db/
      __init__.py
      sqlite_client.py
      migrations/
      schema.sql
    cache/
    state/
    raw/

  utils/
    __init__.py
    text_normalizer.py
    url_normalizer.py
    hash_utils.py
    date_utils.py
    logging_utils.py

  logs/

  tests/

각 폴더 역할:

config:
- 환경변수명, 검색 키워드, 수집 소스, 소셜 채널 설정을 관리한다.
- 실제 토큰/API 키는 저장하지 않는다.

crew_team:
- 직접 수집/게시/저장 로직을 구현하지 않는다.
- research, social, storage 모듈을 호출하는 오케스트레이터 역할만 한다.
- 예: news_bot은 수집→정규화→중복검사→게시→알림 흐름을 호출한다.

social:
- 외부 채널 연동 담당.
- Facebook Page 게시, Telegram 알림, 추후 Naver Blog/카페/WhatsApp 등 확장 가능.
- 뉴스 자동화는 social/news에 둔다.

research:
- 생활정보 원천 데이터를 수집·검증·정규화하는 기능 모듈.
- crawler, parser, normalizer, quality, repository를 포함한다.
- research/news 구조는 만들지 않는다.
- research는 데이터 카테고리가 아니라 수집 기능이다.

domains:
- 데이터의 실제 정체성을 표현한다.
- immigration: 행정사, 이민변호사, 비자 상담
- labor: 노무사, 임금체불, 산재
- hospital: 외국인 진료 가능 병원
- housing: 주거, 기숙사, 부동산
- translation: 통역/번역 기관
- local_support: 외국인 지원센터, 다문화가족지원센터

storage:
- SQLite DB, JSON cache, raw data, runtime state 저장 담당.
- schema.sql은 storage/db/migrations 또는 storage/db 아래로 이동한다.
- DB 파일, cache, raw data는 gitignore 처리한다.

utils:
- 공통 문자열 정규화, URL 정규화, hash 생성, 날짜 처리, logging helper 담당.
- 비즈니스 의미가 강한 정규화는 research/normalizer에 둔다.

quality:
- 최상위 폴더로 두지 않는다.
- 생활정보 품질 평가는 research/quality.
- 뉴스 품질 평가는 social/news/quality 또는 duplicate_guard와 가까운 곳에 둔다.

logs:
- 실행 로그만 저장한다.
- git에 실제 로그 파일은 올리지 않는다.

이번 작업의 범위:
1. 현재 파일 구조를 분석한다.
2. 위 목표 구조에 맞게 폴더를 생성한다.
3. 기존 crawler/parser/normalizer/quality/schema.sql 파일을 적절한 위치로 이동한다.
4. import 경로를 수정한다.
5. 기존 실행 진입점이 깨지지 않도록 __main__.py 또는 compatibility wrapper를 수정한다.
6. README.md에 새 하이어라키 설명을 반영한다.
7. schema.sql 위치 변경 시 README 실행 예시도 수정한다.
8. tests가 있으면 import 경로를 수정한다.
9. dry-run 수준의 최소 실행 확인을 한다.
10. git status로 민감정보/DB/log 파일이 포함되지 않았는지 확인한다.
11. 변경 내용을 commit/push한다.

금지:
- SRC/ForeignWorkerJobInfoService 수정 금지
- PyQLE-project 수정 금지
- C:\WORK 전체 탐색 금지
- 민감정보 커밋 금지
- 실제 Facebook/Telegram API 호출 금지
- 기존 파일을 무작정 삭제 금지

완료 기준:
- 폴더 구조가 위 하이어라키에 맞게 정리된다.
- `python -m foreign_worker_life_info_collector` 실행이 최소한 깨지지 않는다.
- 기존 README의 설명이 새 구조와 일치한다.
- schema.sql 위치가 README와 일치한다.
- git status에 .env, *.db, logs, raw/cache 파일이 포함되지 않는다.
- commit/push가 완료된다.

커밋 메시지:
Refactor life info collector hierarchy for social and research modules

## 2026-05-16 문서 운영 구조 정리

### 현재 상태

- `DOC/architecture/workflow-guide.md`가 생성되어 ChatGPT 대화, GitHub 문서, Codex 작업을 연결하는 기본 운영 패턴을 정의한다.
- 앞으로 Codex 작업은 먼저 `git pull`을 수행하고, `DOC/architecture/workflow-guide.md`, 최신 `DOC/walkthrough` 문서, 관련 GitHub Issue를 확인한 뒤 시작한다.
- README는 프로젝트 소개와 상세 문서 링크만 담는 입구 문서로 유지한다.
- 상세 설계, 작업 로그, Codex 작업 결과, 시행착오 기록은 README가 아니라 `DOC` 아래에 남긴다.

### 확인한 문서와 이슈

- `DOC/architecture/workflow-guide.md`
- `DOC/walkthrough/2026-05-16.md`
- GitHub Issue #1: Social 뉴스 자동화 파이프라인
- GitHub Issue #2: README 최소화 및 DOC/walkthrough 일자별 기록 분리

### 완료된 것

- 최신 `main`을 pull 받았다.
- `DOC/architecture`, `DOC/walkthrough`, `DOC/database` 기준 구조를 확인했다.
- 루트 README를 간결한 프로젝트 소개와 DOC 링크 중심으로 정리한다.
- `DOC/database`에는 DB 설계 문서를 둘 위치를 만든다.

### 다음 작업

- 다음 구현 작업은 `social/news` 기반 뉴스 자동화 파이프라인이다.
- 뉴스 자동화 작업 시작 전 Issue #1과 `DOC/architecture/workflow-guide.md`를 다시 확인한다.
- 실제 Facebook/Telegram API 호출 없이 dry-run 가능한 DB 저장, 중복 제거, 게시 후보 선별 흐름부터 구현한다.

### 타임스탬프 수정내용 ###

이제 시작하자.

작업 대상:
C:\WORK\foreign_worker_job_info

먼저 git pull로 최신 main을 받아라.

그 다음 아래 문서를 순서대로 확인해라.
1. DOC/architecture/workflow-guide.md
2. DOC/architecture/collector-hierarchy.md
3. DOC/walkthrough 최신 날짜 문서
4. 관련 GitHub Issue

이번 작업은 문서에 적힌 “다음 작업”을 기준으로 진행한다.

원칙:
- README는 비대하게 만들지 않는다.
- 상세 작업 기록은 DOC/walkthrough에 남긴다.
- 코드 구조 원칙은 DOC/architecture를 따른다.
- 민감정보, 토큰, .env, DB 파일, logs 파일은 커밋하지 않는다.
- 작업 범위 밖 폴더는 수정하지 않는다.

작업 완료 후:
- 변경 파일 목록
- 실행/검증 결과
- 실패한 내용
- 다음 작업 시작점

을 DOC/walkthrough 최신 날짜 문서에 업데이트하고 commit/push까지 해라.

### 타임스탬프 수정내용 ###

작업 대상:
C:\WORK\foreign_worker_job_info\SRC\foreign_worker_life_info_collector

먼저 git pull 후 아래 문서를 확인해라.
- DOC/architecture/workflow-guide.md
- DOC/architecture/collector-hierarchy.md
- DOC/architecture/social-news-automation.md
- DOC/walkthrough 최신 문서

현재 문제:
run.bat 실행 결과가 뉴스 운영 UI가 아니라 research/raw DB dump처럼 출력된다.
뉴스 자동화 흐름은 일부 동작하지만, 출력/요약/후보선정/상태값이 운영용으로 부적합하다.

현재 관찰된 문제:
1. saved 후보 전체가 JSON으로 길게 출력된다.
2. short_summary, key_points, telegram message에 HTML anchor tag가 그대로 들어간다.
3. evaluator 점수가 대부분 동일해서 실제 best candidate 선정 근거가 약하다.
4. WorkConnect의 핵심 대상은 “한국에서 일하는 외국인/외국인 노동자/비자/정착”인데, H-1B 같은 미국 취업비자 뉴스가 최상위로 선택된다.
5. ready_to_publish 후보의 status가 NOTIFIED로 표시되어 상태 흐름이 혼동된다.
6. 운영자가 봐야 하는 출력은 전체 raw row가 아니라 요약된 execution report여야 한다.

이번 작업 목표:
뉴스 자동화 파이프라인의 CLI/run.bat 출력, 요약 정제, 후보 평가 기준, 상태 흐름을 정리한다.
실제 Facebook/Telegram API 호출은 dry-run에서는 하지 않는다.

필수 변경 사항:

1. CLI 출력 모드 분리
기본 실행 출력은 compact report로 바꾼다.

예시:

[WorkConnect News Automation - DRY RUN]
Collected: 10
Saved: 10
Duplicates: 0
Skipped: 9
Selected: 1

Selected Candidate:
- Title: [단독] 일 잘하면 혜택도 더 많이…외국인 취업비자 개편 - KBS 뉴스
- Source: KBS 뉴스
- Keyword: 외국인 취업 비자
- Score: 0.91
- Reason: 한국 내 외국인 취업비자 제도 개편과 직접 관련
- URL: ...

Publish:
- Facebook: DRY_RUN
- Telegram: DRY_RUN
- DB status: PUBLISHED_DRY_RUN or DRY_RUN_NOTIFIED

Full JSON dump는 기본 출력하지 않는다.
필요하면 --json 또는 --verbose 옵션에서만 출력한다.

2. HTML 제거
summary, short_summary, key_points, telegram message, facebook message에서 HTML tag를 제거한다.
Google News RSS summary의 <a>, <font> 태그를 strip하고 깨끗한 plain text로 변환한다.

필요한 유틸 위치:
utils/text_normalizer.py
또는 social/news/normalizer/news_normalizer.py

3. source name 추출
title 끝의 "- KBS 뉴스", "- 뉴시스" 등 source를 별도 필드 source_name으로 분리한다.
본문 메시지에는 source_name을 깔끔하게 표시한다.

4. 한국 관련성 가중치 추가
candidate_evaluator에 korea_relevance_score를 추가한다.

강하게 가산:
- 한국
- Korea
- 국내
- 법무부
- 고용노동부
- 출입국
- E-9
- E-7
- 고용허가제
- 지역특화형 비자
- 외국인 노동자
- 외국인 근로자
- 외국인 취업비자
- 정주
- 산업현장
- 중소기업

감점:
- H-1B
- 미국
- US
- Canada
- Australia
- 해외 취업
- 한국과 직접 관련 없는 외국 비자 뉴스

5. 평가 점수 다양화
모든 후보가 같은 score를 받지 않도록 scoring을 조정한다.

권장 점수:
- foreign_worker_relevance_score
- korea_relevance_score
- visa_or_labor_policy_score
- freshness_score
- source_reliability_score
- duplicate_risk_penalty
- facebook_post_suitability_score

6. best candidate 선정 근거 저장
선택된 후보에는 selection_reason 필드를 저장한다.
스킵된 후보에는 skip_reason을 저장한다.

예:
- selected because it directly discusses Korea foreign worker visa reform
- skipped because a higher scoring Korea-specific visa article was selected
- skipped because it is related to US H-1B, not Korea foreign worker support

7. 상태값 정리
dry-run과 실제 publish 상태를 분리한다.

권장 상태:
- CANDIDATE
- NORMALIZED
- SUMMARIZED
- DUPLICATE
- SKIPPED
- READY_TO_PUBLISH
- DRY_RUN_PUBLISHED
- PUBLISHED
- FAILED
- DRY_RUN_NOTIFIED
- NOTIFIED

ready_to_publish 배열에는 READY_TO_PUBLISH 또는 DRY_RUN_PUBLISHED 직전 상태만 넣고,
최종 notified 결과는 publish_results에만 표시하거나 상태 흐름을 명확히 한다.

8. Telegram 메시지 정리
Telegram dry-run 메시지는 아래처럼 plain text만 사용한다.

[WorkConnect News Published - DRY RUN]
Status: DRY_RUN_PUBLISHED
Title: ...
Source: ...
Why selected: ...
Summary: ...
URL: ...

승인/거절/보류 문구는 넣지 않는다.

9. run.bat 역할 정리
run.bat 기본 실행은 dry-run compact report를 보여준다.
full JSON은 별도 옵션으로만 가능하게 한다.

10. DB 저장 유지
후보/news_candidate 저장, 중복 방지용 hash/similarity_key 저장, publish log 저장 구조는 유지한다.
단, dry-run DB 파일/log 파일이 git에 올라가지 않게 확인한다.

주의:
- Spring 프로젝트 SRC/ForeignWorkerJobInfoService는 수정하지 않는다.
- PyQLE-project는 수정하지 않는다.
- 실제 토큰/API 키는 코드나 문서에 쓰지 않는다.
- dry-run에서는 실제 Facebook/Telegram 호출하지 않는다.
- 승인/거절/보류 플로우를 되살리지 않는다.

완료 후:
1. run.bat 실행 결과를 확인한다.
2. 출력이 compact report인지 확인한다.
3. HTML tag가 제거되었는지 확인한다.
4. H-1B 같은 비한국 뉴스가 한국 관련 뉴스보다 우선 선택되지 않는지 확인한다.
5. DOC/walkthrough 최신 날짜 문서에 변경 파일, 검증 결과, 남은 문제, 다음 작업을 기록한다.
6. git status 확인 후 민감정보, DB, logs 파일이 포함되지 않았는지 확인한다.
7. commit/push한다.

커밋 메시지:
Refine social news automation reporting and candidate 

### 타임스탬프 수정내용 ###

첨부한 stitch_korea_life_admin_hub.zip 안의 code.html, DESIGN.md, screen.png를 기준으로 현재 정적 HTML UI를 Vue 3 + Vite + Tailwind 프로젝트로 재구성해줘.

요구사항:
1. 기존 화면 디자인과 레이아웃은 최대한 유지한다.
2. code.html의 단일 HTML 구조를 Vue 컴포넌트로 분리한다.
3. 최소 컴포넌트 구조:
   - App.vue
   - components/Sidebar.vue
   - components/Header.vue
   - components/StatusCard.vue
   - components/DataTable.vue
   - components/BotMonitorCard.vue
   - components/LogPanel.vue
4. DESIGN.md의 색상, 타이포그래피, spacing, border-radius 기준을 Tailwind config에 반영한다.
5. CDN 방식은 제거하고 npm 기반 Tailwind 설정으로 바꾼다.
6. 화면 데이터는 우선 mock data로 구성한다.
7. 추후 API 연동이 쉽도록 데이터 배열과 UI 렌더링을 분리한다.
8. Composition API와 `<script setup>` 문법을 사용한다.
9. 기존 HTML 안에 반복되는 UI는 재사용 가능한 컴포넌트로 정리한다.
10. 결과물은 바로 `npm install && npm run dev`로 실행 가능해야 한다.

목표:
스티치에서 생성된 정적 관리자 대시보드를 실제 개발 가능한 Vue 프론트엔드 프로젝트 초안으로 전환하는 것. // 참조 material은 DOC/design에 ziip 파일로 있으니까 확인해주고 

### 타임스탬프 수정내용 ###

현재 Vue admin UI를 실제 실행 데이터와 연결하기 전에, 먼저 backend 코드 구조에 맞는 DB 테이블 설계를 진행해줘.

참고 자료:
- DOC/design 폴더 안의 stitch_korea_life_admin_hub.zip
- Admin UI Process and Module Integration 문서
- 현재 SRC/foreign_worker_life_info_collector 전체 코드

작업 목표:
현재 Python news/social pipeline, repository, CLI 실행 구조, Vue admin UI mock data를 모두 확인한 뒤, UI 운영에 필요한 기초 테이블과 실행/수집/게시/로그 테이블을 설계한다.

필수 작업:
1. 현재 코드에서 실제 저장소 계층을 확인한다.
   - social/news/repository
   - storage 관련 모듈
   - pipeline.py
   - models.py
   - news_bot.py
   - 기존 SQLite 사용 위치

2. 현재 UI에서 필요한 데이터 항목을 확인한다.
   - dashboardData.js
   - App.vue
   - components/*
   - 상태 카드
   - 봇 모니터
   - 후보 테이블
   - 로그 패널
   - 모듈 on/off toggle 영역

3. 코드 기준으로 필요한 테이블을 설계한다.
   최소 포함:
   - admin_module_config
   - admin_runtime_config
   - admin_env_status
   - news_pipeline_cycle
   - news_pipeline_step_log
   - news_pipeline_error_log
   - news_raw_item
   - news_normalized_item
   - news_candidate
   - social_publish_log
   - telegram_notify_log

4. 각 테이블별로 다음을 작성한다.
   - 테이블 목적
   - 컬럼명
   - 타입
   - nullable 여부
   - 기본값
   - primary key
   - foreign key
   - index 필요 여부
   - UI에서 사용되는 위치
   - backend 코드에서 매핑될 위치

5. SQLite 기준 DDL을 먼저 작성한다.
   단, 추후 Oracle/PostgreSQL로 이전 가능하도록 컬럼명과 타입을 너무 SQLite 전용으로 설계하지 않는다.

6. 초기 seed data를 작성한다.
   최소 포함:
   - collector.naver
   - collector.google
   - collector.rss
   - step.normalize
   - step.summarize
   - step.duplicate_check
   - step.llama_check
   - step.candidate_evaluation
   - publish.facebook
   - notify.telegram

7. UI 실행 전 기초 데이터 삽입 흐름을 만든다.
   예:
   - scripts/init_admin_db.py
   - 또는 storage/init_schema.py
   - 또는 기존 repository 구조에 맞는 migration/init 함수

8. backend 강제 규칙을 반영한다.
   - UI에서 비활성화한 모듈은 backend에서도 절대 실행하지 않는다.
   - dry_run=true이면 외부 API 호출은 simulation만 수행한다.
   - facebookPublish=false이면 FacebookPublisher.publish()를 호출하지 않는다.
   - telegramNotify=false이면 Telegram notifier를 호출하지 않는다.
   - llamaCheck=false이면 LLaMA checker를 호출하지 않는다.
   - collector별 enabled=false이면 해당 collector는 collect() 호출하지 않는다.

9. 결과 문서를 생성한다.
   위치:
   - DOC/design/admin_db_schema.md

10. 가능하면 실제 적용 파일도 생성한다.
   권장 위치:
   - SRC/foreign_worker_life_info_collector/storage/schema.sql
   - SRC/foreign_worker_life_info_collector/storage/seed_admin_config.sql
   - SRC/foreign_worker_life_info_collector/scripts/init_admin_db.py

주의사항:
- 기존 코드와 충돌하지 않게 먼저 현재 repository 구조를 읽고 맞춰라.
- 기존 DB 파일이나 운영 데이터는 삭제하지 마라.
- .env, *.db, logs, node_modules, dist는 수정하거나 커밋 대상으로 포함하지 마라.
- UI mock data를 바로 제거하지 말고, API 연결 전까지 fallback으로 유지한다.
- 실제 Facebook/Telegram API 호출은 절대 추가하지 않는다.
- 이번 작업은 테이블 설계와 초기화 구조까지만 진행한다.

완료 기준:
1. admin_db_schema.md에 전체 테이블 설계가 정리되어 있다.
2. SQLite DDL이 작성되어 있다.
3. 초기 seed SQL 또는 init script가 작성되어 있다.
4. 현재 코드 구조 기준으로 어느 UI/API/파이프라인이 어느 테이블을 사용하는지 매핑되어 있다.
5. `python scripts/init_admin_db.py` 또는 이에 준하는 명령으로 기초 테이블 생성과 seed 삽입이 가능하다.
5. `python scripts/init_admin_db.py` 또는 이에 준하는 명령으로 기초 테이블 생성과 seed 삽입이 가능하다.