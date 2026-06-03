### 타임스탬프 수정내용 ###

뉴스 원문 저장 및 관리자 상세보기 기능을 반드시 구현해줘.

현재 문제:
- 콘텐츠 생성용 기사 원문을 보려고 했지만 PostgreSQL social_news 테이블이 비어 있었다.
- 실제 데이터는 SQLite logs/news.db에 저장되고 있었고, PostgreSQL social_news 스키마에는 저장되지 않았다.
- 관리자 화면에서 기사 상세보기도 구현되어 있지 않아 수집된 기사 원문, 정규화 내용, 점수, 게시 상태를 확인할 수 없다.

수정 목표:
1. SQLite 저장소 사용 로직을 완전히 제거한다.
2. 뉴스 수집 원문은 PostgreSQL social_news.raw_item에 저장한다.
3. 정규화된 뉴스는 PostgreSQL social_news.normalized_item에 저장한다.
4. 게시 후보는 PostgreSQL social_news.candidate에 저장한다.
5. 관리자 화면에서 뉴스 상세보기를 구현한다.
6. 콘텐츠 생성기는 PostgreSQL에 저장된 원문/정규화/후보 데이터를 기준으로 동작하도록 한다.

필수 구현: 뉴스 상세보기

관리자 화면에 아래 기능을 추가한다.

목록:
- 뉴스 후보 목록에서 각 row 클릭 시 상세보기로 이동
- 또는 “상세보기” 버튼 추가

상세보기 화면 표시 항목:
- raw_item id
- normalized_item id
- candidate id
- source
- source_url
- original_url
- title
- original_title
- summary
- content/body/raw_text
- normalized_text
- language
- collected_at
- normalized_at
- score
- score_breakdown_json
- publish_status
- post_expired
- post_expired_reason
- facebook_posted_yn
- facebook_post_id
- facebook_permalink
- posted_at
- skipped_reason
- duplicate_reason
- raw_json 또는 raw_html
- pipeline_cycle_id
- 관련 pipeline_step_log
- 관련 pipeline_error_log
- 관련 publish_log

상세보기 API 예시:
- GET /admin/social-news/candidates
- GET /admin/social-news/candidates/{candidateId}
- GET /admin/social-news/raw-items/{rawItemId}
- GET /admin/social-news/normalized-items/{normalizedItemId}

상세보기에서 필요한 버튼:
- 원문 URL 열기
- Facebook 게시글 열기
- 다시 점수 계산
- READY_TO_PUBLISH로 변경
- POST_EXPIRED 처리
- dry-run 게시 미리보기
- 게시 로그 보기

원문 저장 정책:
- 기사 본문 또는 수집 가능한 텍스트는 반드시 저장한다.
- 원문 전체 저장이 불가능하면 최소한 title, summary/snippet, source_url, collected_at, raw_json/raw_html을 저장한다.
- content/body/raw_text 컬럼이 없다면 migration으로 추가한다.
- raw_html은 너무 크면 별도 컬럼 또는 압축/텍스트 추출 방식으로 저장하되, 최소 텍스트 본문은 DB에서 확인 가능해야 한다.

PostgreSQL 저장 확인:
뉴스 수집 후 아래 테이블에 데이터가 들어가야 한다.
- social_news.raw_item
- social_news.normalized_item
- social_news.candidate
- social_news.pipeline_cycle
- social_news.pipeline_step_log
- social_news.publish_log

SQLite 관련:
- NEWS_BOT_SQLITE_DB 사용 금지
- sqlite/news.db 우선 사용 로직 제거
- logs/news.db는 런타임에서 읽거나 쓰지 않는다.
- 기존 SQLite 데이터는 삭제하지 말고 수동 migration script만 제공한다.

검증 SQL:
작업 완료 후 아래 쿼리로 확인 가능해야 한다.

select id, source_url, title, collected_at
from social_news.raw_item
order by collected_at desc
limit 20;

select id, title, score, publish_status, created_at
from social_news.candidate
order by created_at desc
limit 20;

select *
from social_news.publish_log
order by created_at desc
limit 20;

작업 완료 후 알려줄 것:
1. SQLite를 사용하던 코드 위치
2. 제거/수정한 파일 목록
3. PostgreSQL 저장 흐름
4. 추가한 상세보기 API
5. 추가한 관리자 화면 경로
6. 원문 확인 SQL
7. 콘텐츠 생성기가 어떤 테이블을 기준으로 원문을 읽는지

### 타임스탬프 수정내용 ###

뉴스 게시 봇 로직이 아직 의도대로 동작하지 않는다.

현재 문제:
- Telegram 로그에 “오늘 READY_TO_PUBLISH 후보가 없습니다”가 반복된다.
- 그런데 의도는 후보가 없으면 점수 기준을 유동적으로 낮춰서 오늘 수집된 뉴스 중 최소 안전조건을 통과한 최고 점수 1건을 READY_TO_PUBLISH로 승격하고 게시하는 것이다.
- 또한 Facebook 토큰 만료로 1건 게시 실패가 발생했는데, 실패 이후에도 다음 사이클에서 후보 복구/재시도 흐름이 보이지 않는다.

수정 목표:
게시기는 단순히 READY_TO_PUBLISH만 조회하고 끝나면 안 된다.
매시간 실행 시 아래 순서로 동작해야 한다.

1. 오늘 READY_TO_PUBLISH 후보 조회
2. 없으면 오늘 수집된 COLLECTED / SCORED / NORMALIZED / SKIPPED_LOW_SCORE 후보까지 확장 조회
3. 필수 안전조건 통과 후보를 찾음
4. minimum_safe_score를 동적으로 낮춤
   - 기본 50
   - 후보 없음이면 45
   - 그래도 없으면 40
   - 단 40 미만은 절대 게시 금지
5. 가장 높은 점수 1건을 READY_TO_PUBLISH로 승격
6. Facebook 토큰이 유효하면 게시 시도
7. 게시 성공 시 POSTED
8. 게시 실패 시 READY_TO_PUBLISH 또는 FAILED_RETRYABLE로 유지
9. 후보가 정말 없을 때만 “게시 후보 없음” 알림 발송

중요:
- “READY_TO_PUBLISH가 없음”은 게시 종료 사유가 아니다.
- 그것은 “후보 확장 평가를 시작해야 한다”는 의미다.
- 게시 성공 후에만 1시간 cooldown을 적용한다.
- 게시 실패나 후보 없음은 cooldown이 아니다.
- 토큰 만료 실패는 FACEBOOK_TOKEN_EXPIRED로 기록하고, 해당 뉴스는 다음 토큰 갱신 후 재시도 가능하게 남긴다.

Telegram 알림도 수정:
- 후보 없음 알림은 최종적으로 모든 fallback까지 실패했을 때만 보낸다.
- 중간 상태인 READY_TO_PUBLISH 없음은 WARN 로그만 남기고 텔레그램 알림으로 보내지 않는다.
- 토큰 만료는 별도 긴급 알림으로 보낸다.

dry-run에 반드시 표시:
- ready_count
- expanded_candidate_count
- minimum_safe_score
- selected_candidate
- promoted_to_ready 여부
- publish_attempted 여부
- no_publish_reason

Facebook 게시 실패 #200 원인을 확인해줘.

중요:
내가 브라우저에서 FACEBOOK_PAGE_ACCESS_TOKEN으로 feed 조회는 성공했다.
그런데 앱 게시에서는 #200 권한 오류가 난다.
따라서 앱 런타임이 실제로 어떤 토큰을 쓰는지 확인해야 한다.

수정/확인 요구:
1. FacebookPublisher.publish()에서 사용하는 토큰 env key를 확인해라.
2. 반드시 FACEBOOK_PAGE_ACCESS_TOKEN만 사용하게 해라.
3. FACEBOOK_USER_ACCESS_TOKEN을 게시에 쓰면 안 된다.
4. 게시 직전 token debug_token을 호출해서 다음 값을 로그로 남겨라.
   - token type
   - is_valid
   - profile_id
   - scopes
   - expires_at
   - 단 token 원문은 마스킹
5. profile_id가 FACEBOOK_PAGE_ID=810804142117301와 같은지 검증해라.
6. scopes에 pages_read_engagement, pages_manage_posts가 없으면 게시하지 말고 FACEBOOK_PERMISSION_MISSING으로 기록해라.
7. 앱 시작 시 실제 읽은 FACEBOOK_PAGE_ID와 PAGE_TOKEN 마스킹 값을 로그로 남겨라.
8. 서버 재시작 후에도 같은 토큰을 읽는지 확인해라.
9. #200 실패 건은 FAILED_PERMISSION으로 저장하고, 관리자에서 repost 버튼으로 재시도 가능하게 해라.
10. repost 실행 전에도 token debug 결과를 보여줘라.

### 타임스탬프 수정내용 ###

뉴스 게시 봇 로직이 아직 의도대로 동작하지 않는다.

현재 문제:
1. Facebook 게시 실패 후보가 다음 게시 후보군에 다시 포함되지 않는다.
2. READY_TO_PUBLISH 후보가 없으면 점수 기준을 낮춰 후보를 확장해야 하는데, 바로 “뉴스 게시 없음” 텔레그램 알림을 보낸다.
3. “게시 후보 없음” 알림이 너무 자주 오고, 실제로는 fallback 후보를 찾아야 할 상황이다.

수정 목표:
- 게시 실패한 후보는 버리지 말고 재시도 가능한 상태로 유지한다.
- READY_TO_PUBLISH가 없으면 종료하지 말고 후보군을 확장한다.
- 최종적으로 정말 아무 후보도 없을 때만 텔레그램 “게시 없음” 알림을 보낸다.

필수 정책:

1. 실패 후보 재포함
Facebook 게시 실패 시:
- token/permission 오류여도 후보 자체는 삭제하거나 제외하지 않는다.
- publish_status = FAILED_RETRYABLE 또는 READY_TO_PUBLISH 유지
- last_publish_error 저장
- publish_attempt_count 증가
- next_retry_at 설정
- repost 버튼으로 수동 재게시 가능
- 토큰 교체 후 자동/수동으로 다시 게시 가능해야 함

단, 같은 후보 무한 반복 방지:
- publish_attempt_count >= 3 이면 AUTO_RETRY_BLOCKED
- 수동 repost는 가능

2. READY 후보 없음 처리
READY_TO_PUBLISH 후보가 없으면 바로 게시 없음 처리하지 말 것.

대신:
- 오늘 수집된 COLLECTED / NORMALIZED / SCORED / SKIPPED_LOW_SCORE / FAILED_RETRYABLE 후보를 조회
- 필수 안전조건 통과 후보만 추림
- 점수 기준을 동적으로 완화
  - 기본 minimum_safe_score = 50
  - 후보 없으면 45
  - 그래도 없으면 40
  - 40 미만은 게시 금지
- 최고 점수 후보 1건을 READY_TO_PUBLISH로 승격
- 그 후보를 게시 시도

3. “게시 없음” 알림 조건 변경
아래를 모두 실패했을 때만 텔레그램 게시 없음 알림 발송:
- READY_TO_PUBLISH 없음
- FAILED_RETRYABLE 재시도 가능 후보 없음
- 확장 후보 없음
- minimum_safe_score 40 이상 후보 없음

중간 상태인 “READY 후보 없음”은 텔레그램 알림 금지.
운영 로그에만 남겨라.

4. 토큰/권한 실패 처리
Facebook #200, token expired, permission missing 실패는:
- 후보를 버리지 않는다.
- FAILED_RETRYABLE 또는 FAILED_PERMISSION 상태로 보존
- 토큰 교체 후 repost 가능해야 함
- 텔레그램에는 실패 1회만 알림
- 같은 후보 실패 알림 반복 금지

5. 게시 선택 우선순위
매시간 게시기 실행 시:
1. 재시도 가능한 FAILED_RETRYABLE 후보
2. READY_TO_PUBLISH 후보
3. 오늘 평균 이상 SCORED 후보
4. minimum_safe_score까지 낮춘 fallback 후보

이 순서로 최고 점수 1건 선택.

6. 로그
매 실행마다 반드시 남겨라:
- ready_count
- retryable_failed_count
- expanded_candidate_count
- fallback_threshold
- selected_candidate_id
- selected_from_status
- promoted_to_ready
- publish_attempted
- publish_result
- no_publish_reason

핵심:
“READY_TO_PUBLISH 후보 없음”은 종료 사유가 아니라 fallback 후보 확장 시작 조건이다.