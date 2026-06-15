Work Connect Korea 프로젝트의 자동화 워크플로우를 설계/정리해줘.

중요:
작업 시작 전에 반드시 업로드된 기존 기획서, PPT, 발표자료, 문서를 먼저 읽고 현재 기획 방향을 파악하라.
기존 문서의 핵심 방향인 “외국인 대상 한국 취업·비자·생활정보 구독형 플랫폼”과 충돌하지 않게 확장 설계하라.
문서에 이미 있는 내용은 중복 작성하지 말고, 부족한 부분을 보완하는 방식으로 정리하라.

목표:
외국인 대상 한국 취업·비자·생활정보·커뮤니티 콘텐츠를 수집하고, AI로 정리한 뒤, 바로 게시하지 않고 Telegram 검수 후 승인된 콘텐츠만 Facebook/사이트에 게시하는 구조를 만든다.

작업 순서:

1. API/크롤링/RSS 데이터 소스 정리
2. UI 개선: 화면명 변경 및 메뉴 구조 정리
3. 콘텐츠 생성 결과물 보정: Facebook 업로드 전 최종 포맷 정리
4. 생성 콘텐츠를 Telegram으로 전송하되 자동 게시 금지
5. 검수 패턴이 안정화되면 승인 기반 게시 자동화로 확장

카테고리:

* 취업
* 비자/출입국
* 생활정보

  * 주거
  * 금융
  * 통신
  * 의료
  * 교육
  * 전문가
* 커뮤니티

필수 산출물:

1. 기존 문서 요약
2. 기존 기획과 추가 작업의 연결점
3. 데이터 소스 목록
4. 수집 주기
5. DB 테이블 초안
6. API 명세 초안
7. 메뉴 구조
8. 관리자 화면 구조
9. 콘텐츠 상태값 설계
10. Telegram 검수 플로우
11. Facebook 게시 포맷
12. PDF vs Written Content + Image 비교 후 추천안

콘텐츠 상태값:

* COLLECTED
* GENERATED
* SENT_TO_TELEGRAM
* APPROVED
* REJECTED
* PUBLISHED

기본 게시 포맷:
PDF가 아니라 Written Content + 대표 이미지 형식으로 설계한다.
PDF는 주간/월간 리포트, 비자 가이드북 같은 프리미엄 콘텐츠용으로만 분리한다.

주의사항:

* 초기에는 절대 자동 게시하지 않는다.
* Telegram 전송까지만 자동화한다.
* 승인 이후에만 Facebook/사이트 게시가 가능하게 설계한다.
* 출처, 번역 여부, 원문 링크, 생성일, 검수자, 승인일을 반드시 추적한다.
* 네이버 블로그, Reddit, Facebook Group 등 커뮤니티성 데이터는 저작권/약관/출처표기 리스크를 별도로 표시하라.

# Implementation Phase Start

IMPORTANT

지금까지 생성한 문서와 기존 프로젝트 문서를 모두 검토하라.

특히 아래 문서를 구현 기준(To-Be Spec)으로 사용하라.

* DOC/to-be/content-approval-workflow.md
* DOC/to-be/content-creation.md
* DOC/to-be/topic-search.md
* DOC/architecture/*
* DOC/design/*
* 외국인 취업정보 구독 서비스 PPT
* 외국인 취업정보 구독 서비스 발표자료 PPT

중요:

지금부터는 문서 작성이 목적이 아니다.

새로운 설계 문서 생성 금지.
중복 문서 생성 금지.
회의록 생성 금지.
제안서 생성 금지.

기존 문서를 요구사항 명세서(PRD)로 간주하고 실제 구현 작업을 진행하라.

목표:

Telegram 승인 기반 콘텐츠 게시 시스템 구축

Workflow

COLLECTED
→ GENERATED
→ SENT_TO_TELEGRAM
→ APPROVED
→ REJECTED
→ PUBLISHED

현재 단계에서는 Facebook 자동 게시 구현 금지.

우선순위

1순위
DB 설계

* DDL 생성
* ERD 생성
* Migration Script 생성

대상 테이블

* content.source_item
* content.generated_content
* content.review_log
* content.publish_target
* content.community_signal

2순위
Backend 구현

Spring Boot 기준

생성 대상

* Entity
* Repository
* Service
* Controller
* DTO
* Mapper

API

* 수집
* 콘텐츠 생성
* Telegram 전송
* 승인
* 반려
* 조회

3순위
Telegram Workflow

구현 범위

* Telegram Bot 연동
* 승인 버튼
* 반려 버튼
* Callback 처리
* 상태 변경

4순위
Admin UI

Vue3 기준

생성 대상

* Content Review Queue
* Approval Queue
* Source Registry
* Publish Log

5순위
배치

Spring Scheduler

구현

* Source Collection
* Content Generation
* Telegram Delivery

금지사항

* Facebook 자동 게시
* 자동 승인
* 자동 공개 배포

출력 형식

문서 설명 최소화

반드시 아래 형식으로 출력

1. 작업 계획
2. 생성 대상 파일 목록
3. 실제 생성 코드
4. 변경된 디렉토리 구조
5. 다음 작업

설명보다 구현을 우선한다.

If implementation is possible, generate code immediately.
Do not stop at documentation.

# Continue Implementation From Current Report

IMPORTANT

이전 작업 보고서를 기준으로 이어서 진행한다.

먼저 아래 내용을 증빙하라.

## Step 0. Implementation Verification

문서 설명 금지.
실제 결과만 출력.

출력 항목:

1. 생성된 파일 개수

2. 생성된 파일 전체 목록

3. git diff 요약

4. 신규 생성 Entity 목록

5. 신규 생성 Controller 목록

6. 신규 생성 Scheduler 목록

7. ContentWorkflowDto.java 주요 코드

8. ContentWorkflowScheduler.java 주요 코드

9. Telegram Callback 처리 코드

10. mvn -q -DskipTests compile 실행 로그 마지막 부분

만약 구현되지 않은 파일이 있다면
구현 완료 후 결과를 출력한다.

---

## Step 1. DB 검증

현재 생성된 DDL 기준으로

* PK
* FK
* Index
* Unique Key

검토

성능상 문제점 수정

필요 시 Migration 업데이트

---

## Step 2. Telegram Workflow Completion

현재 구현 상태를 검토한다.

확인 항목

* Telegram 메시지 생성
* Approve 버튼
* Reject 버튼
* Callback 처리
* 상태 변경
* Review Log 저장

미완성 부분은 구현한다.

---

## Step 3. Admin UI Completion

ContentApprovalWorkflowPage.vue 기준

다음 기능 구현

* GENERATED 목록 조회
* SENT_TO_TELEGRAM 목록 조회
* APPROVED 목록 조회
* REJECTED 목록 조회

상세보기

* 원문
* 생성 콘텐츠
* 이미지
* 상태

버튼

* Telegram 전송
* 승인
* 반려

---

## Step 4. Source Collection Expansion

현재 시스템에 아래 카테고리 추가

### Employment

* Work24
* WorkNet

### Visa

* HiKorea
* Ministry of Justice

### Living Information

* Housing
* Finance
* Telecom
* Healthcare
* Education

### Community Signals

* Reddit
* Public Community Trend

주의

커뮤니티 원문 재게시 금지

Topic Signal만 저장

---

## Step 5. Content Generation Pipeline

구현

COLLECTED
→ GENERATED
→ SENT_TO_TELEGRAM
→ APPROVED
→ PUBLISHED

현재는

PUBLISHED 호출 차단

APPROVED 까지만 구현

Facebook 자동 게시 금지

---

## Output Rules

새 문서 작성 금지

회의록 작성 금지

설계 보고서 작성 금지

반드시

1. 실제 변경 파일
2. 실제 코드
3. 실제 수정 내역
4. 남은 TODO

위주로 출력

구현 가능한 경우 코드부터 생성한다.

# Continue Without Intermediate Confirmation

IMPORTANT

이전 작업 보고서는 확인했다.

이제부터 중간 보고하지 말고 가능한 구현 작업을 끝까지 진행하라.

컨펌 요청 금지.
문서 추가 생성 금지.
설계 설명 금지.
"다음 작업"만 나열하고 멈추지 말 것.

단, 외부 비밀값/계정/실제 운영 권한이 필요한 작업은 TODO로 남긴다.

현재 상태:

* DB/DDL/Migration/ERD 생성 완료
* Backend Content Approval Workflow 생성 완료
* Telegram 승인/반려 Callback 뼈대 생성 완료
* Admin UI `/content-approval` 생성 완료
* `mvn -q -DskipTests compile` 통과
* Vue build는 npm/pnpm/yarn PATH 문제로 미검증
* 외부 Source collector는 catalog/manual 수준
* Facebook/site publish는 의도적으로 차단 상태

목표:

현재 생성된 뼈대를 기준으로 실제 동작 가능한 MVP까지 이어서 구현한다.

---

## Step 1. Source Collector 실제 구현

아래 source catalog를 단순 목록이 아니라 실제 수집기 구조로 구현하라.

대상:

* Work24
* WorkNet
* HiKorea
* Ministry of Justice
* Housing
* Finance
* Telecom
* Healthcare
* Education
* Reddit
* Public Community Trend

구현 범위:

* SourceCollector interface
* 각 Source별 Collector class
* SourceCollectorRegistry
* CollectionRunService
* SourceItem 저장
* 중복 URL 방지
* source_risk_level 자동 세팅
* usable_for_content_yn 자동 판정

주의:

* 실제 API KEY가 필요한 소스는 mock/dry-run fallback 구현
* 실제 URL 호출이 가능한 공식 페이지는 Jsoup 또는 RestTemplate 기반으로 구현
* 커뮤니티 소스는 원문 저장 금지
* Reddit/Facebook/Naver Blog류는 topic signal만 저장

---

## Step 2. Content Generation 실제 구현

현재 placeholder 수준이면 실제 생성 로직으로 보강하라.

구현 범위:

* SourceItem -> GeneratedContent 변환
* content_type 자동 분류
* title 생성
* written_content 생성
* short_summary 생성
* why_it_matters 생성
* check_next 생성
* hashtags 생성
* image_prompt 생성
* source_disclaimer 생성

AI API 연동이 없다면 deterministic template generator로 구현한다.

즉, 외부 LLM 없이도 MVP가 동작해야 한다.

---

## Step 3. Telegram 실제 메시지 보강

구현 범위:

* Telegram Review Message formatting 완성
* approve/reject callback_data 생성
* content_id/action 파싱 안정화
* Telegram message id 저장
* dry-run=true일 때도 review_log 저장
* dry-run=false일 때 실제 Bot 전송

Bot.java 기존 구조를 확인하고 충돌 없이 연결하라.

---

## Step 4. Admin UI 동작 검증 보강

Vue build가 불가능하면 코드 정적 검증을 수행하라.

구현 범위:

* route 등록 확인
* apiClient 함수 확인
* 상태별 탭/필터 확인
* Telegram 전송 버튼
* 승인 버튼
* 반려 버튼
* 에러 메시지 출력
* loading state
* empty state

npm/pnpm/yarn이 없으면 실행하지 말고 코드 레벨에서 import/path 오류를 최대한 제거하라.

---

## Step 5. DB Migration 적용성 검토

실제 DB에 바로 적용하지 말고 SQL 문법과 호환성을 검토하라.

구현 범위:

* PostgreSQL 기준이면 schema/table/index 문법 확인
* MySQL/MariaDB 기준이면 partial index/md5 expression index 사용 가능 여부 확인
* 현재 프로젝트 DB 종류를 pom/application 설정에서 확인
* DB 종류에 맞게 migration 수정

주의:

MariaDB/MySQL에서 PostgreSQL partial index 문법을 쓰면 안 된다.
현재 프로젝트 DB 설정을 반드시 확인한 뒤 맞춰라.

---

## Step 6. End-to-End Dry Run API 추가

실제 운영 전에 아래 테스트용 API를 추가하라.

```text
POST /api/admin/content/e2e-dry-run
```

동작:

1. mock source item 생성
2. generated_content 생성
3. Telegram dry-run 전송 처리
4. review_log 저장
5. 결과 반환

응답:

* source_item_id
* generated_content_id
* status
* telegram_dry_run_result
* review_log_id

이 API는 local/dev profile에서만 동작하게 제한하라.

---

## Step 7. Compile 재검증

반드시 실행:

```bash
mvn -q -DskipTests compile
```

실패하면 수정 후 재실행.

성공할 때까지 가능한 범위에서 수정.

---

## 최종 출력 규칙

중간 보고하지 말고 마지막에만 출력하라.

최종 출력 항목:

1. 추가/수정 파일 목록
2. 실제 구현된 Collector 목록
3. 실제 구현된 Content Generation 로직
4. Telegram Workflow 동작 요약
5. E2E Dry Run API 사용법
6. DB 호환성 확인 결과
7. Compile 결과
8. 남은 TODO

금지:

* 새 기획서 작성
* 새 설계 문서 작성
* 단순 설명만 하고 종료
* "진행할까요?" 질문
* "다음 단계"만 출력하고 종료

현재 구현된 MVP를 기준으로 로컬 검증용 실행 스크립트와 테스트 데이터를 추가하라.

중간 보고 금지.
문서 생성 금지.
컨펌 요청 금지.

목표:
DB migration 적용 전후, E2E dry-run API, Telegram dry-run, Admin UI API 연결을 한 번에 확인할 수 있는 로컬 검증 패키지를 만든다.

작업:
1. local/dev profile용 sample data SQL 생성
2. e2e-dry-run API 호출용 curl script 생성
3. generated -> sent_to_telegram -> approve/reject 상태전이 테스트용 curl script 생성
4. PostgreSQL migration 적용 확인 SQL 생성
5. Vue UI에서 필요한 API 응답 mock JSON 생성
6. README가 아니라 실행 가능한 scripts 중심으로 작성

생성 위치:
- SRC/ForeignWorkerJobInfoService/src/main/resources/db/sample/
- SRC/ForeignWorkerJobInfoService/scripts/content-workflow/
- SRC/foreign_worker_life_info_collector/admin_ui/src/mocks/

반드시 마지막에만 출력:
1. 생성/수정 파일 목록
2. 실행 순서
3. curl 예시
4. 검증 성공 기준
5. 남은 TODO

프로젝트: Foreign Worker Job Info

현재 상태

* Content Approval Workflow 구현 완료
* Collector 구현 완료

  * Work24
  * WorkNet
  * HiKorea
  * Ministry of Justice
  * Housing
  * Finance
  * Telecom
  * Healthcare
  * Education
  * Reddit
  * Public Community Trend

완료 범위

* SourceCollector
* SourceCollectorRegistry
* CollectionRunService
* 중복 URL 방지
* 위험도 자동 세팅
* 콘텐츠 사용 가능 여부 자동 판정
* Reddit/Public Community Trend는 community_signal만 저장

Content Workflow 상태
COLLECTED
→ GENERATED
→ SENT_TO_TELEGRAM
→ APPROVED
→ PUBLISHED

또는

COLLECTED
→ GENERATED
→ SENT_TO_TELEGRAM
→ REJECTED

추가 구현

* Local Sample Data SQL
* Migration Check SQL
* PowerShell Verification Scripts (00~04)
* Admin UI Mock JSON 11개

검증 성공 기준

* Required Table 5
* PK 5
* FK 3
* Index 21
* Duplicate URL Hash = 0
* E2E Dry Run = SENT_TO_TELEGRAM
* Review Log 저장 확인
* Approve Path = APPROVED
* Reject Path = REJECTED
* Admin API Smoke 성공
* Mock JSON Parse 성공
* Maven Compile 성공

남은 TODO

* PostgreSQL 환경변수 연결
* Admin 인증 Cookie 적용
* Telegram 실전 검증
* Vue Build 환경 복구

다음 작업 요청 시 규칙

1. 이미 구현된 기능을 다시 설계하지 말 것
2. 현재 구조를 최대한 유지할 것
3. 변경 파일 목록을 먼저 제시할 것
4. DB Migration 영향 여부를 먼저 분석할 것
5. API 변경 시 Frontend 영향도 같이 분석할 것
6. 코드 생성 전 구현 계획을 먼저 제시할 것

좋습니다. 그 기준으로 바로 다음 작업을 진행해주세요.

우선 남은 TODO 중에서 `Vue Build 환경 복구`부터 처리합니다.

요구사항:

1. 현재 `admin_ui`의 package manager 상태를 확인해주세요.
2. `node/npm/pnpm/yarn` PATH 문제인지, lock file 기준 package manager 불일치인지 확인해주세요.
3. 수정이 필요한 파일이 있다면 변경 파일 목록을 먼저 제시해주세요.
4. DB Migration 영향 여부는 없음으로 판단 가능한지 명시해주세요.
5. API 변경이 없다면 Frontend 영향도는 build 환경 한정으로 정리해주세요.
6. 실제 수정 전 구현 계획을 먼저 제시해주세요.
7. 이후 Vue build가 통과하도록 필요한 설정/스크립트 수정안을 제시해주세요.

주의:

* 기존 Content Workflow 구현은 재설계하지 마세요.
* 현재 구조를 유지하세요.
* mock JSON 11개는 유지하세요.
* 임의로 package manager를 변경하지 말고, lock file과 package.json 기준으로 판단하세요.
