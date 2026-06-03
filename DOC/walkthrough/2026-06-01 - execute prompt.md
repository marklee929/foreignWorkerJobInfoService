### 타임스탬프 수정내용 ###

고용24/워크넷 채용정보 Open API 수집 로직을 수정해줘.

이번 작업에서는 EMPLOYEE_24_OPEN_API_EMPLOYMENT_KEY만 사용한다.

JOB_KEY, OCCUPATION_KEY, DIPLOMAT_KEY는 이번 채용공고 수집 작업에서 사용하지 않는다.
해당 키들은 직무정보/직업정보/학과정보용 참조 데이터 API로 보이므로, 현재 MVP의 최신 채용공고 수집 범위에서는 제외한다.

목표:
기존 수집에서 비자/외국인/직종/지역/언어 필터를 걸어 데이터가 거의 안 들어온 것으로 추정된다.
이번에는 필터 없이 최신 채용정보를 넓게 수집해서 실제 응답 구조와 데이터 품질을 확인한다.

API 기본값:
- authKey = EMPLOYEE_24_OPEN_API_EMPLOYMENT_KEY
- callTp = L
- returnType = XML
- display = 100
- startPage = 1~10
- sortOrderBy = DESC

이번 작업에서 사용하지 말아야 할 파라미터:
- region
- occupation
- salTp
- minPay
- maxPay
- education
- career
- pref
- subway
- empTp
- coTp
- busino
- workerCnt
- welfare
- regDate
- keyword
- foreignLanguage
- major
- comPreferential
- pfPreferential
- workHrCd
- 기타 필터성 파라미터 전체

즉, 필수 파라미터와 정렬 파라미터만으로 최신 공고를 수집한다.

수집 방식:
- 1회 실행 시 startPage 1부터 10까지 순차 호출한다.
- 각 페이지는 display=100으로 호출한다.
- 페이지 사이에는 500ms~1000ms 대기한다.
- 1시간마다 실행 가능한 scheduler를 추가하거나 기존 scheduler를 수정한다.
- 로컬 테스트용으로 display=10, startPage=1만 호출하는 smoke test도 만든다.

중복 기준:
- wantedAuthNo를 자연키로 사용한다.
- wantedAuthNo가 이미 있으면 update 또는 skip 처리한다.
- 신규/업데이트/스킵 건수를 로그로 남긴다.

저장 필드:
- wantedAuthNo
- company
- busino
- indTpNm
- title
- salTpNm
- sal
- minSal
- maxSal
- region
- holidayTpNm
- minEdubg
- maxEdubg
- career
- regDt
- closeDt
- infoSvc
- wantedInfoUrl
- wantedMobileInfoUrl
- zipCd
- strtnmCd
- basicAddr
- detailAddr
- empTpCd
- jobsCd
- smodifyDtm
- rawXml
- collectedAt

raw XML 저장:
실제 응답 필드 누락이나 문서와 실제 데이터 차이를 확인해야 하므로, 파싱된 데이터와 별도로 원문 XML도 저장한다.

로그:
- 시작 시간
- 종료 시간
- 호출 페이지 수
- 총 수신 건수
- 신규 저장 건수
- 업데이트 건수
- 중복 스킵 건수
- 실패 페이지
- 0건일 경우 authKey를 제외한 최종 요청 파라미터

주의:
- 인증키는 절대 하드코딩하지 않는다.
- 로그에 인증키 전체를 출력하지 않는다.
- 비자/외국인 가능 여부 판단은 이번 작업에서 하지 않는다.
- 외국인 친화 필터는 데이터가 며칠 쌓인 뒤 후속 작업으로 진행한다.

작업 완료 후:
1. 기존 수집 코드에서 어떤 필터가 걸려 있었는지 알려줘.
2. 수정한 파일 목록 알려줘.
3. 로컬 smoke test 실행 방법 알려줘.
4. 수집 결과 확인 SQL 알려줘.

추가 요구사항: 관리자페이지에 채용정보 수집 봇 관리 화면을 추가한다.

메뉴명:
- 채용정보 수집 봇

목적:
고용24/워크넷 채용정보 Open API 수집 상태를 관리자에서 확인하고, 수동 실행/스모크 테스트/스케줄러 ON-OFF를 제어할 수 있게 한다.

관리자 화면 기능:
1. 수집 상태 카드
- 현재 상태: RUNNING / STOPPED / ERROR
- 마지막 실행 시간
- 다음 실행 예정 시간
- 최근 총 수신 건수
- 최근 신규 저장 건수
- 최근 업데이트 건수
- 최근 중복 스킵 건수
- 최근 실패 페이지
- 최근 에러 메시지

2. 수집 설정 표시 및 수정
- display 기본값 100
- startPageFrom 기본값 1
- startPageTo 기본값 10
- sortOrderBy 기본값 DESC
- intervalMinutes 기본값 60
- filterEnabled 기본값 false

3. 버튼
- 즉시 수집 실행
- 스모크 테스트 실행(display=10, startPage=1)
- 스케줄러 시작
- 스케줄러 중지
- 최근 로그 새로고침

4. 수집 로그 목록
- 실행 ID
- 실행 시작 시간
- 실행 종료 시간
- 요청 페이지 범위
- 총 수신 건수
- 신규 저장 건수
- 업데이트 건수
- 스킵 건수
- 실패 건수
- 상태
- 에러 메시지

5. 주의사항
- API 인증키는 화면에 노출하지 않는다.
- 인증키 존재 여부만 표시한다.
- 실제 사용자 서비스 화면과 분리한다.
- 수집된 채용공고를 바로 공개하지 말고, 관리자 검수 또는 후속 필터링 이후 공개 가능하도록 한다.

백엔드 API 예시:
- GET /admin/job-collector/status
- GET /admin/job-collector/logs
- POST /admin/job-collector/run
- POST /admin/job-collector/smoke-test
- POST /admin/job-collector/scheduler/start
- POST /admin/job-collector/scheduler/stop
- PUT /admin/job-collector/settings

### 타임스탬프 수정내용 ###

현재 foreignWorkerJobInfoService 프로젝트의 최신 커밋 기준으로 뉴스 컬렉터/페이스북 자동 게시 로직을 점검하고 수정해줘.

목표:
기존에 수집된 뉴스 중 오래된 미게시 데이터는 더 이상 게시하지 않고, 오늘 이후 수집된 뉴스만 대상으로 Facebook Page에 자동 게시한다.
뉴스 수집량은 많을 수 있으므로 점수 기준을 더 엄격하게 적용하고, 최종 게시는 1시간에 1개만 수행한다.
게시 성공/실패 결과는 관리자 또는 운영자에게 통보할 수 있는 구조를 만든다.

전제:
- Facebook Page ID:
  FACEBOOK_PAGE_ID=810804142117301
- Facebook API 호출에는 Page Access Token을 사용한다.
- 환경변수:
  FACEBOOK_PAGE_ID
  FACEBOOK_USER_ACCESS_TOKEN
  FACEBOOK_APP_TOKEN
  FACEBOOK_PAGE_ACCESS_TOKEN
- 실제 피드 읽기/게시에는 FACEBOOK_PAGE_ACCESS_TOKEN만 사용한다.
- USER_ACCESS_TOKEN은 재발급/관리용이다.
- APP_TOKEN은 debug_token 검증용이다.
- 토큰은 절대 코드에 하드코딩하지 않는다.

1. 기존 뉴스 컬렉터 구조 확인
먼저 프로젝트에서 아래 키워드로 기존 구현을 검색한다.

- news
- collector
- facebook
- page
- feed
- post
- score
- scheduler
- crawl
- publish
- posted

기존에 뉴스 수집, 점수 계산, Facebook 게시, 스케줄러, 관리자 화면, 로그 테이블이 있다면 그 구조를 최대한 재사용한다.

2. 오래된 미게시 데이터 처리
이번 정책부터는 오래된 미게시 뉴스는 게시하지 않는다.

기준:
- created_at 또는 collected_at 또는 published_at 기준으로 오늘 00:00 이전에 수집된 미게시 뉴스는 자동 게시 대상에서 제외한다.
- 가능하면 상태를 EXPIRED 또는 SKIPPED_OLD로 변경한다.
- 삭제하지 말고 상태만 변경한다.
- 단, raw/news archive 용도로는 보존한다.

상태 예시:
- COLLECTED
- CANDIDATE
- POSTED
- FAILED
- SKIPPED_LOW_SCORE
- SKIPPED_OLD
- EXPIRED

3. 게시 대상 기준
게시 후보는 오늘 수집된 뉴스만 대상으로 한다.

조건:
- collected_at >= 오늘 00:00
- status in ('COLLECTED', 'CANDIDATE', 'FAILED_RETRYABLE') 중 프로젝트 기존 상태에 맞게 선택
- facebook_posted_yn = false 또는 posted_at is null
- source_url 중복 제거
- title/message 중복 제거
- 이미 Facebook에 올라간 permalink/source_url은 제외

4. 점수 기준 강화
뉴스가 너무 많이 수집되고 있으므로 기본 점수 기준을 빡세게 잡는다.

점수 요소 예시:
가산점:
- 외국인 근로자 직접 관련: +40
- 비자, 체류, 재고용, EPS, E-9, H-2, F-4 관련: +35
- 한국 취업/채용/노동법/임금/산재/체불 관련: +30
- 정부 정책/고용노동부/출입국/지자체 지원 관련: +25
- 생활 정착에 중요한 정보: 병원, 주거, 교통, 금융, 환전, 한국어 교육: +15
- 실제 행동 가능한 정보: 신청기간, 서류, 지원금, 연락처, 링크 있음: +20
- 영어/한국어 외 다국어 확장 가치가 높음: +10

감점:
- 외국인과 무관한 일반 정치 뉴스: -30
- 자극적이지만 실질 정보 부족: -20
- 중복 주제: -25
- 출처 불명확: -30
- 링크 없음: -20
- 너무 오래된 기사: -40
- 단순 홍보성 글: -20

초기 기본 게시 기준:
- base threshold = 75점 이상

5. 동적 threshold 조정
수집 뉴스가 많으면 기준을 높이고, 적으면 기준을 완화한다.

예시:
- 오늘 후보 뉴스 100개 이상: threshold = 90
- 오늘 후보 뉴스 50개 이상: threshold = 85
- 오늘 후보 뉴스 20개 이상: threshold = 80
- 오늘 후보 뉴스 5~19개: threshold = 75
- 오늘 후보 뉴스 1~4개: threshold = 65
- 후보가 0개면 게시하지 않음

단, threshold를 낮추더라도 최소 안전 기준은 유지한다.
- 외국인/비자/취업/정착 중 하나와 관련이 없는 뉴스는 게시 금지
- 링크 없는 뉴스는 기본적으로 게시 금지
- 점수 60 미만은 게시 금지

6. 게시 주기
Facebook 게시는 1시간에 1개만 수행한다.

규칙:
- 마지막 게시 성공 시간이 1시간 이내면 게시하지 않는다.
- 마지막 게시 실패가 rate limit 또는 token error이면 재시도하지 않고 통보한다.
- 후보가 여러 개면 가장 높은 score 순으로 1개만 게시한다.
- 동점이면 최신 뉴스 우선.
- 게시 성공 후 해당 뉴스 상태를 POSTED로 변경하고 facebook_post_id, facebook_permalink, posted_at을 저장한다.

7. Facebook 게시 메시지 포맷
게시 메시지는 너무 길지 않게 생성한다.

예시:

[Title]

Short summary in English.

Why it matters for foreign workers in Korea:
- point 1
- point 2

Read more:
{source_url}

필요하면 한국어 요약도 함께 포함한다.

조건:
- Facebook message 길이는 과도하게 길지 않게 한다.
- 링크가 있으면 반드시 포함한다.
- 제목/요약에 민감하거나 단정적인 표현은 피한다.
- 법률/비자 정보는 “check official source” 뉘앙스를 유지한다.

8. Facebook API 호출
피드 게시는 Page Access Token을 사용한다.

POST:
https://graph.facebook.com/v25.0/{FACEBOOK_PAGE_ID}/feed

Params 또는 form:
- message
- access_token = FACEBOOK_PAGE_ACCESS_TOKEN

응답에서 id를 받아 facebook_post_id로 저장한다.

게시 후 가능하면:
GET /{facebook_post_id}?fields=id,permalink_url,created_time
로 permalink_url을 조회하여 저장한다.

9. 통보 기능
게시 성공/실패/게시 없음 상태를 운영자에게 통보하는 구조를 만든다.

기존 notification, email, slack, telegram, admin log 중 이미 있는 방식을 우선 재사용한다.
없다면 최소한 DB 로그와 애플리케이션 로그를 남기고, 추후 알림 채널을 연결하기 쉽게 interface를 만든다.

통보 메시지 예시:

성공:
[News Publisher] Facebook posted
- title:
- score:
- source:
- facebook_post_id:
- permalink:
- posted_at:

실패:
[News Publisher] Facebook post failed
- title:
- score:
- reason:
- status_code:
- response_body:
- occurred_at:

게시 없음:
[News Publisher] No post
- reason: no candidate / cooldown / low score
- candidate_count:
- threshold:
- checked_at:

10. 관리자 페이지/관리 API
관리자페이지가 있다면 “뉴스 게시 봇” 관리 화면 또는 API를 추가한다.

필요 기능:
- 현재 상태 조회
- 마지막 게시 시간
- 다음 게시 가능 시간
- 오늘 수집 뉴스 수
- 오늘 후보 뉴스 수
- 현재 threshold
- 최근 게시 성공/실패 로그
- 수동 게시 실행
- dry-run 실행
- 스케줄러 ON/OFF

백엔드 API 예시:
- GET /admin/news-publisher/status
- GET /admin/news-publisher/logs
- POST /admin/news-publisher/run
- POST /admin/news-publisher/dry-run
- POST /admin/news-publisher/scheduler/start
- POST /admin/news-publisher/scheduler/stop

11. dry-run
실제 Facebook에 올리기 전에 반드시 dry-run 가능하게 한다.

dry-run 결과:
- 후보 뉴스 수
- threshold
- top 10 후보
- 각 후보 score
- score breakdown
- 게시 예정 메시지 preview
- 제외된 주요 이유

12. 스케줄러
- 뉴스 수집 scheduler와 뉴스 게시 scheduler를 분리한다.
- 수집은 기존 주기를 유지하거나 프로젝트 설정을 따른다.
- 게시 scheduler는 1시간마다 실행한다.
- 서버 재시작 후에도 마지막 게시 시간을 DB에서 읽어 cooldown을 유지한다.

13. DB/엔티티 보강
기존 테이블이 있으면 최대한 재사용한다.
필요한 필드가 없으면 migration을 추가한다.

필요 필드 예시:
- score
- score_breakdown_json
- publish_status
- facebook_posted_yn
- facebook_post_id
- facebook_permalink
- posted_at
- skipped_reason
- last_publish_attempt_at
- publish_attempt_count

게시 로그 테이블 예시:
news_publish_log
- id
- news_id
- channel
- status
- score
- threshold
- message_preview
- response_code
- response_body
- error_message
- created_at

14. 실패 처리
- token invalid: 즉시 중단, 통보
- permission error: 즉시 중단, 통보
- rate limit: 최소 1시간 이상 재시도 금지
- network error: 해당 건 FAILED_RETRYABLE 처리
- 같은 뉴스는 최대 3회까지만 재시도

15. 환경변수 정리
.env.example에 아래 값을 추가 또는 정리한다.

FACEBOOK_PAGE_ID=
FACEBOOK_USER_ACCESS_TOKEN=
FACEBOOK_APP_TOKEN=
FACEBOOK_PAGE_ACCESS_TOKEN=

주의:
- 실제 키 값은 커밋하지 않는다.
- 로그에 access token 전체를 찍지 않는다.
- 토큰 출력 시 앞 6자리/뒤 4자리만 마스킹한다.

16. 작업 완료 후 알려줄 것
- 기존 뉴스 컬렉터 구조 요약
- 수정한 파일 목록
- 추가/변경한 테이블 목록
- Facebook 게시 테스트 방법
- dry-run 실행 방법
- 실제 게시 scheduler 동작 방식
- 수집은 됐지만 게시 제외된 뉴스 확인 SQL
- 오늘 게시 후보 확인 SQL

### 타임스탬프 수정내용 ###

뉴스 게시 알고리즘을 다시 조정해줘.

핵심 목표:
Facebook 게시 봇은 1시간마다 1개씩 올리되, 단순히 최근 1시간 수집 뉴스만 보지 않는다.
최근 1시간 수집 뉴스와 오늘 00:00 이후 쌓인 READY_TO_PUBLISH 백로그를 함께 평가해서, 현재 시점에서 가장 좋은 후보 1개를 게시해야 한다.

중요 정책:
1. 하루 사이클은 00:00에 시작하고 23:59에 종료한다.
2. 오늘 이전 미게시 뉴스는 다음날로 이월하지 않고 EXPIRED 또는 SKIPPED_DAILY_RESET 처리한다.
3. 오늘 수집된 READY_TO_PUBLISH 후보는 게시되지 않았다고 바로 탈락시키지 않는다.
4. 오늘 안에서는 계속 대기열에 남겨두고, 매시간 다시 평가한다.
5. 게시 성공 후에만 1시간 cooldown을 적용한다.
6. 게시가 없었던 경우는 cooldown으로 보지 않는다.

후보 풀 구성:
- recent_pool: 최근 1시간 이내 수집된 READY_TO_PUBLISH 뉴스
- backlog_pool: 오늘 00:00 이후 수집됐고 아직 게시되지 않은 READY_TO_PUBLISH 뉴스
- candidate_pool = recent_pool + backlog_pool 중복 제거

단, backlog_pool도 전부 후보로 쓰지 말고 현재 품질 평균보다 좋은 기사만 유지한다.

평균 기준:
- today_avg_score = 오늘 READY_TO_PUBLISH 후보 전체의 평균 점수
- backlog 후보는 score >= today_avg_score 이면 유지
- recent_pool 후보는 평균보다 낮아도 freshness bonus 때문에 평가 대상에 포함한다
- 단 minimum_safe_score 미만은 어떤 경우에도 게시 금지

기본값:
- minimum_safe_score = 50
- freshness_bonus_recent_1h = +10
- backlog_above_average_bonus = +5
- duplicate_penalty = -30
- risk_penalty는 기존 로직 유지

최종 점수:
final_score =
  base_score
  + freshness_score
  + backlog_above_average_bonus
  + engagement_prediction_score
  - duplication_penalty
  - risk_penalty

선택 규칙:
1. 오늘 READY_TO_PUBLISH 전체를 조회한다.
2. 오늘 평균 점수 today_avg_score를 계산한다.
3. recent_pool은 모두 평가 대상에 포함한다.
4. backlog_pool은 score >= today_avg_score 인 것만 평가 대상에 포함한다.
5. Facebook 과거 게시물 반응 데이터를 조회해 engagement_prediction_score를 계산한다.
6. final_score가 가장 높은 1건을 선택한다.
7. final_score가 같으면 최근 수집 뉴스 우선.
8. 그래도 같으면 base_score 높은 뉴스 우선.
9. 그래도 같으면 collected_at 최신순.
10. 선택된 후보가 minimum_safe_score 이상이면 FacebookPublisher.publish() 호출.
11. 게시 성공 시 POSTED 처리.
12. 게시 실패 시 FAILED_RETRYABLE 또는 FAILED 처리.
13. 나머지 후보는 READY_TO_PUBLISH로 유지한다.

Facebook 반응 데이터:
- FACEBOOK_PAGE_ACCESS_TOKEN 사용
- 최근 게시물 조회:
  /{FACEBOOK_PAGE_ID}/feed?fields=id,message,created_time,permalink_url,shares,comments.summary(true),reactions.summary(true)
- 댓글 조회 가능하면:
  /{post_id}/comments?fields=id,message,created_time,like_count,comment_count
- 비슷한 주제의 과거 게시물이 reactions/comments/shares가 높으면 engagement_prediction_score 가산
- 부정 댓글/스팸 신호가 많으면 감점
- Facebook 조회수는 직접 제공되지 않을 수 있으니 reactions/comments/shares 중심으로 계산

24시간 종료 정책:
- 00:00 새 cycle 시작 시 이전 cycle의 READY_TO_PUBLISH 후보는 EXPIRED 또는 SKIPPED_DAILY_RESET 처리
- 삭제하지 말고 archive로 남김
- 새 cycle에서는 이전 후보를 평가하지 않음

로그:
매 실행마다 아래를 남겨줘.
- cycle_id
- recent_pool_count
- backlog_pool_count
- candidate_pool_count
- today_avg_score
- minimum_safe_score
- selected_news_id
- selected_title
- base_score
- freshness_score
- engagement_prediction_score
- final_score
- publish_attempted
- publish_result
- no_publish_reason
- remaining_ready_count

dry-run:
실제 게시 없이 현재 시점 후보 평가 결과를 보여줘.
- recent_pool top 5
- backlog_pool top 5
- final candidate top 10
- selected candidate
- score breakdown
- 게시 여부 판단

추가 수정:
최근 1시간 내 수집 기사가 없는 경우에도 게시기가 멈추면 안 된다.
게시기는 매시간 실행될 때 recent_pool뿐 아니라 오늘 00:00 이후 READY_TO_PUBLISH 상태로 남아있는 daily_backlog_pool도 반드시 조회해야 한다.

정책:
- recent_pool이 있으면 freshness bonus를 부여해 우선 평가한다.
- recent_pool이 없거나 점수가 낮으면 daily_backlog_pool에서 최고 점수 후보를 선택한다.
- daily_backlog_pool 후보는 today_avg_score 이상이면 우선 후보로 유지한다.
- 단, today_avg_score 미만이어도 minimum_safe_score 이상이고 다른 후보가 없으면 fallback 후보가 될 수 있다.
- minimum_safe_score 미만은 게시하지 않는다.
- 게시되지 않은 READY_TO_PUBLISH 후보는 00:00 전까지 절대 SKIPPED 처리하지 않는다.
- 00:00 새 cycle 시작 시 남은 READY_TO_PUBLISH만 EXPIRED 처리한다.
- cooldown은 오직 Facebook 게시 성공 후에만 적용한다.

목표:
새 기사 수집이 없는 시간대에도 오늘 쌓인 후보 중 가장 나은 기사 1개가 1시간마다 올라가야 한다.

추가 수정:

24시간 daily cycle 종료 시, 전날 READY_TO_PUBLISH 상태로 남아있는 미게시 뉴스는 삭제하지 말고 post_expired 플래그만 처리해줘.

정책:
- 수집된 news/article 원본 데이터는 절대 삭제하지 않는다.
- 00:00 새 cycle 시작 전에 이전 cycle의 미게시 READY_TO_PUBLISH 후보를 게시 대상에서 제외한다.
- 제외 방식은 delete가 아니라 flag/update 방식으로 처리한다.

필드 정책:
기존 필드가 있으면 재사용하고, 없으면 아래 필드를 추가한다.

- post_expired BOOLEAN DEFAULT FALSE
- post_expired_at DATETIME NULL
- post_expired_reason VARCHAR(100) NULL
- cycle_id VARCHAR(10) 또는 DATE
- publish_status VARCHAR(50)

전날 만료 처리:
- 조건:
  - cycle_id < today_cycle_id
  - publish_status = 'READY_TO_PUBLISH'
  - facebook_posted_yn = false 또는 posted_at is null
- 처리:
  - post_expired = true
  - post_expired_at = now()
  - post_expired_reason = 'DAILY_CYCLE_EXPIRED'
  - publish_status = 'POST_EXPIRED'

주의:
- raw news/article 데이터는 그대로 유지한다.
- source_url, title, summary, content, collected_at, score 등 기존 수집 데이터는 변경하지 않는다.
- post_expired는 “Facebook 게시 후보에서 제외됨”을 뜻할 뿐, 뉴스 데이터 폐기를 뜻하지 않는다.
- 이후 분석/통계/학습 데이터로 계속 사용할 수 있어야 한다.

게시 후보 조회 조건:
앞으로 Facebook 게시 후보를 조회할 때는 반드시 아래 조건을 포함한다.

- cycle_id = today_cycle_id
- publish_status = 'READY_TO_PUBLISH'
- post_expired = false
- posted_at is null

daily reset 실행 시 로그:
- expired_count
- target_cycle_id
- new_cycle_id
- expired_at
- reason = DAILY_CYCLE_EXPIRED

관리자 화면/API:
- 오늘 READY_TO_PUBLISH 수
- 전날 POST_EXPIRED 수
- 전체 수집 뉴스 수
- 게시 완료 수
- 게시 만료 수
를 구분해서 보여줘.

중요:
post_expired 처리는 하루 게시 사이클 관리를 위한 플래그일 뿐이고, 수집 데이터 삭제나 실패 처리로 보면 안 된다.

### 타임스탬프 수정내용 ###

SQLite 저장소 사용 로직을 완전히 제거하고, 소셜뉴스/채용정보/콘텐츠 수집 데이터 저장소를 PostgreSQL로 통일해줘.

현재 문제:
- PostgreSQL에는 social_news 스키마와 관련 테이블이 이미 설계되어 있다.
- 그런데 실제 뉴스 봇 런타임은 NEWS_BOT_SQLITE_DB가 있으면 logs/news.db SQLite 파일을 우선 사용한다.
- 그래서 DBeaver에서 보는 PostgreSQL 데이터와 관리자 화면/봇 데이터가 서로 다르다.
- 수집 데이터가 SQLite 파일에 계속 쌓이면 용량도 커지고 운영/백업/분석에 부적합하다.

결론:
SQLite는 더 이상 사용하지 않는다.
local/dev 전용 fallback도 남기지 않는다.
기본 저장소는 무조건 PostgreSQL이다.

수정 목표:
1. NEWS_BOT_SQLITE_DB 관련 로직 제거
2. SQLite 연결/초기화/테이블 생성/마이그레이션 코드 제거
3. logs/news.db를 런타임 저장소로 사용하는 모든 경로 제거
4. social_news 관련 모든 데이터는 PostgreSQL social_news 스키마에 저장
5. 관리자 API도 PostgreSQL만 조회
6. 앱 시작 시 SQLite 관련 환경변수가 있으면 무시하거나 WARN 로그 출력
7. .env.example / README / 설정 문서에서 NEWS_BOT_SQLITE_DB 제거
8. 테스트 코드도 SQLite 기반이면 PostgreSQL test schema 또는 mock repository로 변경

대상 데이터:
- raw_item
- normalized_item
- candidate
- pipeline_cycle
- pipeline_step_log
- pipeline_error_log
- publish_log
- telegram_notify_log
- 향후 채용정보/직업정보/콘텐츠 관련 테이블

PostgreSQL 스키마:
- social_news

요구사항:
- 기존 PostgreSQL 테이블을 우선 재사용한다.
- 컬럼이 부족하면 migration을 추가한다.
- repository/dao/service 계층에서 SQLite 분기 제거
- storage backend 선택 로직 제거
- `NEWS_BOT_STORAGE`, `NEWS_BOT_SQLITE_DB`, `sqlite`, `news.db` 관련 코드를 검색해서 제거하거나 PostgreSQL 전용으로 대체
- 앱 시작 로그에는 PostgreSQL 연결 정보만 민감정보 제외하고 표시
- 관리자 화면의 storage backend 표시는 PostgreSQL 고정 또는 제거

기존 SQLite 데이터 처리:
- logs/news.db에 남은 데이터는 삭제하지 않는다.
- 단, 앱에서 더 이상 읽지 않는다.
- 필요하면 별도 one-time migration script만 제공한다.
- migration script는 수동 실행용이어야 하며 런타임 자동 실행 금지.
- migration script 이름 예:
  scripts/migrate_sqlite_news_to_postgres.py
- migration은 중복 방지를 위해 source_url, normalized_url, candidate id, external id 등 기존 unique 기준을 사용한다.

검증:
1. 앱 실행 시 SQLite 파일을 열지 않는지 확인
2. 뉴스 수집 실행 후 PostgreSQL social_news.raw_item에 데이터 저장 확인
3. 정규화 후 social_news.normalized_item 저장 확인
4. 후보 생성 후 social_news.candidate 저장 확인
5. 게시 로그가 social_news.publish_log에 저장되는지 확인
6. 관리자 화면 수치와 PostgreSQL 쿼리 결과가 일치하는지 확인
7. 코드 전체에서 NEWS_BOT_SQLITE_DB, sqlite, news.db 사용 흔적이 없는지 확인

작업 완료 후 알려줄 것:
- SQLite 사용 코드가 있던 위치
- 제거/수정한 파일 목록
- PostgreSQL 전용 저장 흐름
- 추가한 migration 파일
- 수동 SQLite → PostgreSQL 이전 방법
- 검증 SQL

