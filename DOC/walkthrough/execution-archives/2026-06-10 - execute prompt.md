### 타임스탬프 수정내용 ###

작업명:
Facebook token/publish error normalization

작업 목적:
오늘 Facebook 자동 게시 중 40분 간격으로 2건 정상 게시 후, 다음 게시에서 “FACEBOOK_PAGE_ACCESS_TOKEN이 유효하지 않습니다”라는 실패 알림이 발생했다.

현재 문제는 실제 Meta API 원본 에러인지, 내부 validation/fallback 메시지인지 구분이 안 된다.

이번 작업은 Facebook 토큰을 재발급하거나 게시 정책을 바꾸는 것이 아니다.
Facebook 게시 실패 원인을 정확히 분류하고, 원본 Meta error를 저장/표시하도록 에러 정규화만 수행한다.

작업 모드:
GUARDED_FIX

작업 영역:
FACEBOOK_STATUS
FACEBOOK_PUBLISH_ERROR_NORMALIZATION
CONTENT_PUBLISH_LOG
TELEGRAM_PUBLISH_NOTIFICATION

보호 영역:
아래는 수정 금지 또는 최소 수정만 허용한다.

- admin auth
- device approval
- scheduler interval
- bot ON/OFF state transition
- content candidate selection logic
- news candidate scoring
- Facebook token refresh/reissue 자동화
- 실제 token 값 저장
- .env 파일
- publish frequency/cooldown 정책 변경

이번 작업에서 허용되는 것:
- Facebook publish 실패 응답 파싱
- token validation 결과 분류
- publish_log error fields 보강
- Telegram 실패 알림 메시지 개선
- 내부 error_code/error_category 정규화
- raw token이 아닌 token fingerprint/status 저장
- dry-run 또는 unit-level validation 추가

이번 작업에서 금지되는 것:
- Facebook 자동 게시 정책 변경
- 40분 주기 변경
- content publisher 전환/비활성화
- token 자동 갱신 로직 추가
- token 값을 DB/로그/문서에 출력
- 실패 시 bot 전체 OFF 처리
- 후보 선택 로직 수정

1. Quick Pre-Review 먼저 수행

코드 수정 전에 10~15분 선검토를 수행해라.

확인할 파일 후보:
- Facebook publisher 관련 파일
- Facebook status/token validation 관련 파일
- content publisher 관련 publish 함수
- social news direct publish 함수가 남아 있다면 해당 파일
- Telegram notification formatter
- publish_log repository/model
- admin API의 facebook/status endpoint
- 오늘 실패 알림을 만드는 코드

찾을 키워드:
- FACEBOOK_PAGE_ACCESS_TOKEN
- pages_manage_posts
- debug_token
- is_valid
- expires_at
- OAuthException
- fbtrace_id
- FAILED_RETRYABLE
- FAILED_PERMISSION
- token
- publish_log
- telegram
- Facebook Publish Failed
- 유효하지 않습니다
- invalid

선검토 결과를 먼저 정리해라.

선검토 결과는 아래 셋 중 하나여야 한다.

- SAFE_TO_PROCEED
- PROCEED_WITH_LIMITS
- STOP_REQUIRES_USER_REVIEW

STOP 조건:
- token refresh/reissue 로직을 건드려야만 해결 가능할 때
- scheduler나 bot state를 바꿔야만 해결 가능할 때
- auth/device approval 영역을 건드려야 할 때
- 실제 token 값을 로그/DB에 저장해야 할 것 같을 때
- Meta 원본 응답 위치를 찾지 못했는데 추측으로 고쳐야 할 때

STOP이면 코드 수정하지 말고:
DOC/walkthrough/YYYY-MM-DD-stop-report-facebook-token-error.md
를 작성해라.

2. 현재 에러 메시지 출처 확인

오늘 Telegram에 표시된:

“FACEBOOK_PAGE_ACCESS_TOKEN이 유효하지 않습니다”

이 문구가 어디서 만들어지는지 확인해라.

구분:
A. Meta API 원본 error.message
B. 내부 env validation 메시지
C. token debug validation 메시지
D. exception fallback 메시지
E. Telegram formatter에서 만든 고정 메시지

확인 결과를 walkthrough에 기록해라.

3. Meta API 원본 error 보존

Facebook publish 실패 시 Meta 응답 원문에서 아래 필드를 가능한 한 보존해라.

- error.message
- error.type
- error.code
- error.error_subcode
- error.fbtrace_id
- raw response status code
- request endpoint
- request link_url
- request mode: dry_run / real
- candidate/content id

주의:
request payload에는 token을 저장하지 마라.
Authorization header나 access_token 값은 절대 저장하지 마라.

4. Error Category 정규화

Facebook publish 실패를 아래 category로 분류해라.

권장 enum:

- TOKEN_INVALID
- TOKEN_EXPIRED
- TOKEN_EXPIRING_SOON
- TOKEN_PERMISSION_MISSING
- TOKEN_WRONG_TYPE
- TOKEN_PAGE_MISMATCH
- FACEBOOK_RATE_LIMIT
- FACEBOOK_POLICY_BLOCK
- FACEBOOK_LINK_INVALID
- FACEBOOK_LINK_BLOCKED
- FACEBOOK_PAYLOAD_INVALID
- FACEBOOK_API_TEMPORARY
- FACEBOOK_UNKNOWN_ERROR
- INTERNAL_ENV_MISSING
- INTERNAL_VALIDATION_FAILED
- INTERNAL_EXCEPTION

분류 기준:

Meta error code 190:
- OAuth/token 문제
- message에 expired/session 포함 시 TOKEN_EXPIRED
- validating access token 포함 시 TOKEN_INVALID

Meta error code 200:
- 권한 문제
- TOKEN_PERMISSION_MISSING 또는 PERMISSION_ERROR 계열

Meta error code 4, 17, 32, 613:
- rate limit 가능성
- FACEBOOK_RATE_LIMIT

Meta error code 368:
- policy/spam/action block 가능성
- FACEBOOK_POLICY_BLOCK

Meta error code 100:
- parameter/payload/link 문제 가능성
- FACEBOOK_PAYLOAD_INVALID 또는 FACEBOOK_LINK_INVALID

Meta error에 fbtrace_id가 있으면 반드시 저장.

Meta 원본 error가 없고 내부 validation 실패라면 INTERNAL_* 로 분류.

중요:
모든 실패를 “FACEBOOK_PAGE_ACCESS_TOKEN invalid”로 뭉개지 마라.

5. Token validation 결과 분리

Facebook token 상태 검증 결과와 게시 실패 결과를 분리해라.

Token status는 아래처럼 표현:

- token_type: PAGE / USER / APP / UNKNOWN
- is_valid: true / false / unknown
- page_id_match: true / false / unknown
- required_scopes_present: true / false / unknown
- expires_at
- expires_in_seconds
- token_fingerprint
- validation_checked_at

주의:
token_fingerprint는 token 원문 저장이 아니라 sha256 앞 8~12자리 정도만 사용.
토큰 원문 출력 금지.

정책:
- is_valid=false → TOKEN_INVALID
- type이 PAGE가 아니면 TOKEN_WRONG_TYPE
- page_id가 FACEBOOK_PAGE_ID와 다르면 TOKEN_PAGE_MISMATCH
- pages_manage_posts 누락이면 TOKEN_PERMISSION_MISSING
- expires_at이 가까워도 is_valid=true이면 TOKEN_EXPIRING_SOON 경고이지 게시 차단 사유가 아니다.
- expiring soon을 invalid로 처리하지 마라.

6. Publish log 저장 보강

content.publish_log 또는 현재 실제 사용 중인 publish log에 가능한 범위로 아래 필드를 저장하거나 response_payload/error payload에 포함해라.

필드가 이미 있으면 활용:
- error_category
- error_code
- error_subcode
- error_message
- error_type
- fbtrace_id
- http_status
- link_url
- token_status_snapshot
- retryable_yn
- failed_at

만약 migration이 필요하면 destructive migration 금지.
새 컬럼 추가가 부담되면 우선 response_payload JSON에 구조화해서 저장해라.

권장 JSON:

{
  "error_category": "TOKEN_EXPIRED",
  "meta_error": {
    "message": "...",
    "type": "OAuthException",
    "code": 190,
    "error_subcode": 463,
    "fbtrace_id": "..."
  },
  "http_status": 400,
  "link_url": "...",
  "token_status": {
    "token_type": "PAGE",
    "is_valid": false,
    "page_id_match": true,
    "required_scopes_present": true,
    "expires_at": "...",
    "expires_in_seconds": 0,
    "token_fingerprint": "abcd1234"
  }
}

7. Telegram 실패 알림 개선

현재 Telegram 실패 알림이 너무 뭉뚱그려져 있다.

실패 시 아래 형식으로 보내라.

예시:

⚠️ Facebook Publish Failed

Content ID: 123
Title: ...
Internal Status: FAILED_RETRYABLE
Error Category: TOKEN_EXPIRED

Meta Error:
- type: OAuthException
- code: 190
- subcode: 463
- message: Error validating access token...
- fbtrace_id: ...

Token Status:
- type: PAGE
- valid: false
- page match: true
- scopes: ok
- expires_at: ...
- fingerprint: abcd1234

Link:
- https://...

Next Action:
- Recheck Page Access Token in Meta Debugger.
- Do not assume this is a posting frequency issue until Meta code is confirmed.

만약 Meta 원본 error가 없으면:

Meta Error:
- not available

Internal Reason:
- ...

이렇게 표시해라.

8. Retryable 판단 정리

retryable_yn은 다음 기준으로 설정해라.

Retryable true:
- FACEBOOK_API_TEMPORARY
- FACEBOOK_RATE_LIMIT
- temporary network error
- timeout

Retryable false:
- TOKEN_INVALID
- TOKEN_EXPIRED
- TOKEN_PERMISSION_MISSING
- TOKEN_WRONG_TYPE
- TOKEN_PAGE_MISMATCH
- FACEBOOK_LINK_BLOCKED
- INTERNAL_ENV_MISSING

주의:
TOKEN_EXPIRED는 자동 재시도해도 성공 가능성이 낮으므로 retryable=false가 맞다.
단 bot 전체 OFF 처리하지 말고 publish candidate만 FAILED_BLOCKED 또는 FAILED_TOKEN으로 처리해라.

9. 테스트 또는 검증

가능하면 실제 Facebook 호출 없이 테스트 가능한 함수로 분리해라.

테스트 케이스:
- Meta code 190 expired → TOKEN_EXPIRED
- Meta code 190 invalid → TOKEN_INVALID
- Meta code 200 → TOKEN_PERMISSION_MISSING
- Meta code 613 → FACEBOOK_RATE_LIMIT
- Meta code 368 → FACEBOOK_POLICY_BLOCK
- Meta code 100 with link message → FACEBOOK_LINK_INVALID
- internal missing env → INTERNAL_ENV_MISSING
- expiring soon but is_valid true → TOKEN_EXPIRING_SOON warning, not failure

실제 Facebook API 호출은 하지 않아도 된다.
dry-run 또는 mock response로 검증해라.

10. Walkthrough 작성

작업 후 아래 문서를 작성 또는 업데이트해라.

DOC/walkthrough/YYYY-MM-DD-facebook-token-error-normalization.md

포함 내용:
- 오늘 발생한 문제 요약
- 기존에는 실패 원인을 어떻게 표시했는지
- 실제 에러 메시지 출처
- 새 error_category 목록
- Meta 원본 error 저장 방식
- token status snapshot 저장 방식
- Telegram 알림 개선 내용
- 테스트 결과
- 남은 문제

11. 완료 보고

완료 후 아래 형식으로 보고해라.

1. Pre-review result
2. 수정한 파일
3. 에러 메시지 출처
4. 추가/정리한 error category
5. publish_log 저장 변경
6. Telegram 알림 변경
7. 테스트 결과
8. 건드리지 않은 보호 영역
9. 사용자가 확인해야 할 것

중요:
이번 작업은 “토큰 문제 해결”이 아니라 “토큰/게시 실패 원인 정규화” 작업이다.
토큰 재발급, scheduler 변경, publish frequency 변경은 하지 마라.

### 타임스탬프 수정내용 ###

작업명:
WorkConnect DOC Architecture Review and Harness Preparation

작업 대상:
C:\WORK\foreign_worker_job_info

작업 모드:
DOC_ONLY

작업 영역:
PRODUCT_DOCS
DB_ARCHITECTURE_DOCS
SYSTEM_ARCHITECTURE_DOCS
CODEX_HARNESS_DOCS

작업 목적:
오늘까지 작성된 DOC 문서들을 검토하고, WorkConnect의 제품 방향성 / 데이터 품질 / 시스템 아키텍처 / 로컬 개발 안전수칙 / 하네스 운영 규칙 / 작업 영역 레지스트리가 서로 충돌하지 않게 정리한다.

이번 작업은 코드 수정이 아니다.
이번 작업은 운영 서버, 백엔드, 프론트엔드, DB, Facebook 게시, 스케줄러, 봇 상태를 변경하지 않는다.

코드 수정 금지.
DB 변경 금지.
migration 실행 금지.
.env 수정 금지.
scheduler 변경 금지.
Facebook publish 관련 코드 수정 금지.
admin auth 수정 금지.

현재 DOC 구조를 먼저 확인해라.

현재 확인된 구조 참고:

DOC/
- architecture/
  - 00_PRODUCTION_NORTH_STAR.md
  - 01_SYSTEM_GROWTH_WORKFLOW.md
  - 02_DATA_SOURCE_AND_QUALITY copy.md
  - 03_SYSTEM_ARCHITECTURE.md
  - 04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
  - 05_CODEX_HARNESS_GUIDE.md
  - 06_Harness_Session_Cycle.md
  - 07_WORK_AREA_REGISTRY.md

- database/
  - 00_DB_ARCHITECTURE_INDEX.md
  - 01_CURRENT_DB_MAP.md
  - 02_SOCIAL_NEWS_CURRENT.md
  - 03_CONTENT_CURRENT.md
  - 04_OCCUPATION_CURRENT.md
  - 05_ADMIN_OPS_CURRENT.md
  - 06_DOMAIN_DATA_CURRENT.md
  - Foreign_Worker_Job_Info_DB.png
  - mermaid-diagram.png
  - social_news.png
  - social_news_candidate.png

- design/
  - admin-ui-process-integration.md
  - admin_db_schema.md
  - content_publishing_hub.md
  - stitch_korea_life_admin_hub.zip

- to-be/
- walkthrough/
- archives or archieves folder may exist

중요:
문서를 무작정 많이 만들지 말고, 현재 문서의 역할과 중복을 정리해라.
기존 문서 내용을 대량 삭제하지 말고, 필요한 경우 archive/deprecated 처리만 해라.

1. Quick Pre-Review 먼저 수행

첫 10분 동안은 수정하지 말고 아래를 검토해라.

- DOC/architecture 문서 목록
- DOC/database 문서 목록
- DOC/design 문서가 최신 architecture/database로 흡수됐는지
- DOC/to-be 문서 역할
- DOC/walkthrough 최신 문서
- 파일명 오타/중복/번호 꼬임
- 05_CODEX_HARNESS_GUIDE와 06_Harness_Session_Cycle의 역할 중복
- 07_WORK_AREA_REGISTRY의 위치/번호
- database to-be 문서 누락 여부

Pre-review 결과를 walkthrough에 짧게 남겨라.

Pre-review decision은 아래 중 하나여야 한다.

- SAFE_TO_PROCEED
- PROCEED_WITH_LIMITS
- STOP_REQUIRES_USER_REVIEW

이번 작업은 DOC_ONLY이므로, 코드/DB/서버 수정이 필요해지면 STOP_REQUIRES_USER_REVIEW로 중단해라.

2. 문서 파일명 정리 검토

아래 파일명은 의도와 다를 가능성이 크다.

확인하고, 실제 내용이 맞다면 rename 또는 정리해라.

- 00_PRODUCTION_NORTH_STAR.md
  - 목표 파일명: 00_PRODUCT_NORTH_STAR.md

- 02_DATA_SOURCE_AND_QUALITY copy.md
  - 목표 파일명: 02_DATA_SOURCE_AND_QUALITY.md

- 06_Harness_Session_Cycle.md
  - 05_CODEX_HARNESS_GUIDE.md 안으로 통합할지 검토
  - 통합이 맞다면 05에 흡수하고 06 파일은 archive 또는 deprecated 처리

- 07_WORK_AREA_REGISTRY.md
  - 06_Harness_Session_Cycle을 통합했다면 06_WORK_AREA_REGISTRY.md로 rename 검토
  - 단, 이미 문서 내부 참조가 많으면 무리하게 rename하지 말고 index에 현재 번호를 명시

- DOC/archieves
  - 오타 가능성 있음
  - 목표 폴더명: DOC/archives
  - 다만 Git rename이 부담되면 이번 세션에서는 문서에 TODO로 남겨도 됨

주의:
rename은 문서 파일에만 한정한다.
코드 import/path에 영향을 주는 파일은 건드리지 않는다.

3. Architecture 문서 역할 정리

architecture 문서의 목표 구조는 다음과 같다.

권장 구조:

- 00_PRODUCT_NORTH_STAR.md
  - 제품의 최상위 방향성
  - 타국에 정착하거나 일하러 간 사람들을 위한 정보 플랫폼
  - 한국은 첫 적용 국가
  - 뉴스는 정보 신호일 뿐, 핵심은 반복 가능한 실용 정보

- 01_SYSTEM_GROWTH_WORKFLOW.md
  - 정보 구조가 성장하는 방향
  - source discovery → collection → normalization → domain classification → user value evaluation → content candidate → publish/review → feedback → knowledge improvement

- 02_DATA_SOURCE_AND_QUALITY.md
  - 출처 신뢰도
  - 좋은 데이터/나쁜 데이터
  - 원문/중복/정규화
  - 시스템 메시지 contamination 방지
  - 최소 LLM 검증 원칙
  - 뉴스/생활정보/출입국/직업정보/채용정보 품질 게이트

- 03_SYSTEM_ARCHITECTURE.md
  - 큰 시스템 구도
  - Facebook WorkConnect Korea
  - Admin frontend
  - Backend + Local LLM
  - external sources: country APIs, Naver, Google, official sources
  - normalization/content management/public publishing flow

- 04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
  - 로컬 PC 운영 전제
  - 서버가 죽지 않게 개발
  - frontend-backend 통신 확인
  - UI 깨짐 확인
  - 문자열은 코드/enum이 아니면 한글 우선
  - timestamp는 YYYY-MM-DD HH24:MI:SS
  - 서버 죽으면 수정 후 재시작/검증

- 05_CODEX_HARNESS_GUIDE.md
  - Codex 자동화 작업 방식
  - quick pre-review
  - risk classification
  - stop report
  - error gate
  - 1시간 세션 사이클
  - 조건부 commit/push
  - Telegram summary
  - 6시간 압축 리포트

- 06_WORK_AREA_REGISTRY.md
  - AREA별 허용/금지 범위
  - PRODUCT_DOCS
  - DB_ARCHITECTURE_DOCS
  - DASHBOARD_STATUS
  - FACEBOOK_STATUS
  - CONTENT_QUEUE
  - CONTENT_PUBLISHER
  - SOCIAL_NEWS_CANDIDATE
  - ADMIN_AUTH
  - SCHEDULER_BOT_STATE 등

4. 05_CODEX_HARNESS_GUIDE 정리

05_CODEX_HARNESS_GUIDE.md에 다음 내용이 반드시 포함되어야 한다.

- 목적:
  Codex가 더 오래 작업하게 만드는 것이 아니라, 안전하게 작업하고 위험하면 멈추게 하는 것

- 핵심 원칙:
  Codex must not treat task completion as higher priority than preserving existing system boundaries.

- 작업 흐름:
  work area selection
  → quick pre-review
  → risk classification
  → proceed or stop
  → limited execution
  → verification
  → report

- 1시간 세션 사이클:

```text
00:00–00:10  Quick pre-review
00:10–00:40  Development work
00:40–00:50  Development verification
00:50–01:00  Final check, walkthrough update, conditional commit/push, and Telegram summary
```

---

## DOC Architecture Pre-Review and Harness Cleanup - 2026-06-10

### HARNESS PRE-REVIEW

AREA:

- PRODUCT_DOCS
- DB_ARCHITECTURE_DOCS
- SYSTEM_ARCHITECTURE_DOCS
- CODEX_HARNESS_DOCS

MODE:

- DOC_ONLY

FOCUS:

- Review current DOC structure.
- Resolve architecture numbering and duplicate harness-session roles.
- Keep product direction, DB architecture, system architecture, local runtime safety, harness rules, and work area registry consistent.

Risk:

- LOW, limited to documentation files.
- Existing worktree already contained documentation renames from `archieves` to `archives`, `00_PRODUCT_NORTH_STAR.md`, `02_DATA_SOURCE_AND_QUALITY.md`, and `TO_BE_DB_ARCHITECTURE.md`.

Decision:

```text
PROCEED_WITH_LIMITS
```

Limits:

- Do not modify runtime code.
- Do not modify DB schema or data.
- Do not run migrations.
- Do not modify `.env`.
- Do not change scheduler, Facebook publisher, bot state, or admin auth.

### Files Inspected

- `DOC/architecture/00_PRODUCT_NORTH_STAR.md`
- `DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md`
- `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
- `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
- `DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`
- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
- `DOC/architecture/06_Harness_Session_Cycle.md`
- `DOC/architecture/07_WORK_AREA_REGISTRY.md`
- `DOC/database/00_DB_ARCHITECTURE_INDEX.md`
- `DOC/database/01_CURRENT_DB_MAP.md`
- `DOC/database/TO_BE_DB_ARCHITECTURE.md`
- `DOC/design/`
- `DOC/to-be/`
- `DOC/walkthrough/`

### Pre-Review Findings

- `00_PRODUCT_NORTH_STAR.md` already exists with the target product naming.
- `02_DATA_SOURCE_AND_QUALITY.md` already exists with the target naming.
- `DOC/archives` already exists; the old `DOC/archieves` path appears only in git history/status as a prior rename.
- `05_CODEX_HARNESS_GUIDE.md` and `06_Harness_Session_Cycle.md` duplicated session-cycle rules.
- `07_WORK_AREA_REGISTRY.md` should become `06_WORK_AREA_REGISTRY.md` after the session-cycle document is absorbed into the harness guide.
- `02_DATA_SOURCE_AND_QUALITY.md`, `05_CODEX_HARNESS_GUIDE.md`, and `07_WORK_AREA_REGISTRY.md` had Markdown structure risks from unclosed code blocks or unstructured headings.
- DB to-be documentation is present as `DOC/database/TO_BE_DB_ARCHITECTURE.md`; indexes still referenced planned split files `10_TO_BE_DB_ARCHITECTURE.md`, `11_TO_BE_CONTENT_FLOW.md`, and `12_MIGRATION_ROADMAP.md`.

### Changes Made

- Rebuilt `05_CODEX_HARNESS_GUIDE.md` as the single harness operation document.
- Deprecated `06_Harness_Session_Cycle.md` into `DOC/archives/06_Harness_Session_Cycle.deprecated.md`.
- Renamed/rebuilt `07_WORK_AREA_REGISTRY.md` as `06_WORK_AREA_REGISTRY.md`.
- Fixed `01_SYSTEM_GROWTH_WORKFLOW.md` code fence closing.
- Fixed `02_DATA_SOURCE_AND_QUALITY.md` Markdown section structure and quality-gate lists.
- Updated DB docs to point to the actual `TO_BE_DB_ARCHITECTURE.md` document.

### Verification

- Documentation-only scan performed.
- Markdown code fence count checked across `DOC/architecture`, `DOC/database`, and this walkthrough; all checked files have even fence counts.
- Old architecture/database/design/to-be references to `07_WORK_AREA_REGISTRY.md`, `06_Harness_Session_Cycle.md`, `00_PRODUCTION_NORTH_STAR.md`, `02_DATA_SOURCE_AND_QUALITY copy.md`, and split DB to-be files were not found.
- No runtime code changed.
- No DB changes or migrations performed.
- No server, scheduler, Facebook publisher, bot state, or admin auth changes performed.

이 작업은 단일 1시간 세션으로 끝내지 말고, 2026-06-11 06:00:00 KST까지 1시간 Harness Session Cycle을 반복한다.

각 세션은 다음 순서를 따른다.

00:00–00:10  Quick pre-review  
00:10–00:40  Development work  
00:40–00:50  Development verification  
00:50–01:00  Final check, walkthrough update, conditional commit/push, and Telegram summary

각 세션 종료 후 stop condition이 없으면 다음 1시간 세션을 시작한다.

6개 세션마다 6H compressed report를 작성하고 Telegram summary를 보낸 뒤 사용자 검토가 필요한지 판단한다.

종료 시각:
2026-06-11 06:00:00 KST

종료 시각 30분 전부터는 신규 대형 작업을 시작하지 말고, 진행 중인 세션의 정리, 문서화, 검증, commit/push 여부 판단, 최종 리포트 작성에 집중한다.

전체 목표:
2026-06-11 06:00:00 KST까지 WorkConnect 프로젝트의 DOC 중심 아키텍처와 하네스 운영 기준을 계속 보완하고, 이후 자동화 작업에 필요한 수정 및 개선사항을 찾아 정리한다.

이번 장기 작업의 우선순위:

1. DOC/architecture 정리
- Product North Star
- System Growth Workflow
- Data Source and Quality
- System Architecture
- Local Development Runtime Guide
- Codex Harness Guide
- Work Area Registry

위 문서들이 서로 충돌하지 않는지 검토하고, 문서 간 역할 중복을 줄여라.

2. DOC/database 정리
- current reference 문서
- to-be architecture 문서
- content flow 문서
- migration roadmap 문서

DB 문서가 source data / content candidate / publishing log / admin ops 경계를 명확히 설명하는지 확인해라.

3. DOC/to-be 검토
- 기존 to-be 문서가 최신 architecture 방향과 충돌하는지 확인
- 충돌하면 코드 수정 없이 TODO 또는 deprecation note로 남겨라
- 바로 구현하지 말고, 향후 작업 후보로 정리해라

4. DOC/design / DOC/archives 정리
- 최신 기준 문서로 흡수된 과거 설계 문서는 archive/deprecated 처리한다
- 아직 필요한 내용은 어느 architecture/database/to-be 문서로 흡수할지 기록한다
- 이미지, ppt, zip 같은 참고 자산은 무리하게 삭제하지 않는다

5. Harness 준비
- 앞으로 사용자가 AREA / MODE / FOCUS / TIMEBOX만 던져도 Codex가 작업할 수 있도록 문서 구조를 보강한다
- 05_CODEX_HARNESS_GUIDE.md와 06_WORK_AREA_REGISTRY.md가 실제 자동화에 쓸 수 있을 정도로 명확한지 확인한다
- Quick Pre-Review, Stop Report, Error Gate, 1시간 세션 사이클, 6시간 압축 리포트, Telegram Summary 규칙을 정리한다

6. 개선사항 발굴
각 세션마다 최소 하나 이상 아래 중 하나를 남겨라.

- 문서 구조 개선
- 누락된 기준
- 중복된 문서
- 충돌하는 설명
- 향후 코드 작업 후보
- 위험한 자동화 영역
- 사용자 승인이 필요한 protected change
- 다음 세션에서 집중할 AREA 후보

중요 제한:
이번 장기 작업은 기본적으로 DOC_ONLY이다.

코드 수정 금지.
DB 변경 금지.
migration 실행 금지.
.env 수정 금지.
Facebook publish 코드 수정 금지.
scheduler 변경 금지.
admin auth 변경 금지.
bot ON/OFF 상태 변경 금지.
실제 외부 API 호출 금지.
서버 실행 변경 금지.

단, 문서 파일명 정리, 문서 이동, archive/deprecated 표시, walkthrough 작성은 허용한다.

파일명 또는 폴더명 변경 시 주의:
- 문서 링크가 깨질 수 있으면 링크도 함께 수정한다.
- 링크 추적이 어렵다면 변경하지 말고 TODO로 남긴다.
- 코드에서 참조하는 경로일 가능성이 있으면 변경하지 말고 STOP 또는 TODO로 남긴다.

다음 조건 중 하나라도 발생하면 반복을 중단한다.

- STOP_REQUIRES_USER_REVIEW
- protected area change required
- verification failed
- backend/frontend communication broken
- commit/push unsafe
- task scope exceeded declared AREA
- 문서 정리만으로 해결할 수 없고 코드 수정이 필요함
- 어떤 문서를 기준 문서로 삼아야 할지 판단 불가
- 기존 내용을 삭제해야만 정리가 가능한 상황
- Git 충돌 또는 push 실패
- 현재 세션에서 복구할 수 없는 Markdown 구조 깨짐

각 1시간 세션 종료 시 반드시 수행:
- DOC/walkthrough/YYYY-MM-DD-harness-session-[area]-HHMM.md 작성
- git status 확인
- 변경 파일 요약
- Markdown 구조 최소 확인
- 조건부 commit/push 판단
- Telegram summary 가능하면 발송
- Telegram 미구현이면 walkthrough에 Telegram: NOT RUN 기록

Commit/push 조건:
다음 조건을 모두 만족할 때만 commit/push 한다.

- 작업이 declared AREA 안에 머물렀다
- 코드/DB/서버/Facebook/scheduler/auth를 건드리지 않았다
- 문서 변경이 확인 가능하다
- Markdown 코드블록이 깨지지 않았다
- walkthrough가 작성됐다
- git diff를 검토했다
- commit message가 세션 결과를 명확히 설명한다

검증 실패 또는 불확실성이 있으면 broken work를 push하지 마라.

최종 종료 리포트:
2026-06-11 06:00:00 KST 도달 시 아래 내용을 정리한다.

- 전체 세션 수
- 완료한 문서 정리
- 변경한 파일
- archive/deprecated 처리한 파일
- 남은 TODO
- 다음에 사용자가 집중할 AREA 후보
- protected change 후보
- commit/push 결과
- Telegram summary 결과

정정합니다.

이번 장기 반복 작업의 기본 모드는 DOC_ONLY가 맞지만, 단순 문서 작성만 하라는 의미는 아닙니다.

목표는 2026-06-11 06:00:00 KST까지 1시간 Harness Session Cycle을 반복하면서:

1. DOC/architecture, DOC/database, DOC/to-be, DOC/walkthrough를 검토하고
2. 문서 구조와 하네스 기준을 정리하며
3. 이후 실제 코드 자동화에 필요한 작업 AREA / 위험도 / 개선 후보를 발굴하고
4. 문서만으로 안전하게 정리 가능한 부분은 반영하고
5. 코드 수정이 필요한 부분은 직접 수정하지 말고 TODO 또는 STOP_REPORT로 남기는 것입니다.

즉, 지금은 코드 수정 세션이 아니라 “자동화 준비 및 개선사항 발굴 세션”입니다.

DOC_ONLY의 의미:
- 문서 수정 가능
- 문서 이동/rename 가능
- archive/deprecated 처리 가능
- walkthrough 작성 가능
- 코드/DB/env/scheduler/Facebook/auth 수정 금지

각 1시간 세션마다 다음을 반드시 남겨주세요.

- 이번 세션에서 검토한 문서
- 정리한 문서/파일명
- 발견한 구조 충돌
- 이후 코드 작업 후보
- 각 후보의 AREA
- 각 후보의 MODE
- 위험도
- 사용자 승인 필요 여부
- 다음 세션 추천 작업

문서 검토 중 코드 수정이 필요하다고 판단되는 항목은 직접 고치지 말고 아래 형식으로 남기세요.

```text
CODE_TASK_CANDIDATE
AREA:
MODE:
FOCUS:
WHY:
RISK:
PROTECTED AREA:
RECOMMENDED NEXT PROMPT:

짧게 말하면 코덱스에게 이렇게 못 박아야 함.

```text
DOC_ONLY = 문서만 쓰라는 뜻이 아니라,
코드 자동화를 하기 위한 기준 정리와 작업 후보 발굴까지 포함한다.
