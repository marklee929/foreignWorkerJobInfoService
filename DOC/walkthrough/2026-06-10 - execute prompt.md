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