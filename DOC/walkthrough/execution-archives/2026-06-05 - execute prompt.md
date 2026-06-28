### 타임스탬프 수정내용 ###

Facebook 자동 게시가 다시 실패했다.

실패 로그:
Reason: FACEBOOK_PAGE_ACCESS_TOKEN이 유효하지 않습니다.
Status: FAILED_RETRYABLE

확인할 것:
1. 수동 게시/관리자 재게시/FacebookPublisher.auto_publish가 모두 같은 FACEBOOK_PAGE_ACCESS_TOKEN을 쓰는지 확인
2. FACEBOOK_USER_ACCESS_TOKEN 또는 예전 token을 게시에 사용하지 않는지 확인
3. 앱 시작 시 읽은 FACEBOOK_PAGE_ACCESS_TOKEN 마스킹값과 게시 직전 token 마스킹값을 로그로 남김
4. 게시 직전 debug_token 결과를 저장
   - is_valid
   - type
   - profile_id
   - scopes
   - expires_at
5. profile_id가 FACEBOOK_PAGE_ID와 일치하지 않으면 게시 중단
6. token invalid 시 후보는 FAILED_RETRYABLE 유지
7. 토큰 갱신 후 FAILED_RETRYABLE 후보를 repost 가능하게 유지
8. 관리자 화면에 현재 런타임이 읽는 token fingerprint 표시
   - raw token 절대 노출 금지
   - sha256 앞 8자리 또는 앞6/뒤4만 표시

중요:
방금 1시간 텀 뒤 실패한 것은 cooldown 문제가 아니라 token invalid 문제다.
수동으로 확인한 page token과 실제 봇 런타임 token이 같은지 비교할 수 있어야 한다.