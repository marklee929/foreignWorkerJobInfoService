### 타임스탬프 수정내용 ###

뉴스 파이프라인과 Facebook 게시 파이프라인을 분리하고, 통합 콘텐츠 게시 큐를 구축해줘.

현재 문제:
- 현재 구조는 뉴스 기사 수집/정규화/요약/게시가 하나의 news pipeline에 강하게 묶여 있다.
- 외국인 근로자/채용/비자 기사만으로는 1시간 1게시를 안정적으로 유지하기 어렵다.
- 뉴스가 부족하면 전체 게시 자동화가 멈춘다.
- WorkConnect의 장기 방향은 “Information for Living in Korea or Anywhere”이므로 뉴스뿐 아니라 생활정보, 출입국정보, 이민/비자 정보, 직업정보도 콘텐츠 후보로 다뤄야 한다.

목표:
뉴스 기사는 전체 콘텐츠 후보의 한 종류로 취급한다.
수집 파이프라인과 게시 파이프라인을 분리한다.
게시 파이프라인은 통합 content_candidate 큐에서 30분마다 최적 콘텐츠 1건을 선택해 Facebook에 게시한다.

1. 구조 개편 개념

기존:
news collect
→ normalize
→ summarize
→ score
→ publish

변경:
각 도메인별 수집 파이프라인
→ content_candidate 생성
→ 통합 콘텐츠 큐
→ content publisher가 30분마다 하나 선택
→ Facebook 게시

도메인별 수집 파이프라인:
- news_article pipeline
- living_info pipeline
- immigration_notice pipeline
- visa_info pipeline
- occupation_info pipeline
- government_notice pipeline

게시 파이프라인:
- content_publish_pipeline

2. 통합 content_candidate 테이블

새 테이블을 만들거나 기존 candidate를 확장하되, 가능하면 social_news와 분리된 content 스키마를 생성한다.

예:
content.content_candidate

필드:
- id
- source_domain
  - SOCIAL_NEWS
  - LIVING_INFO
  - IMMIGRATION_INFO
  - VISA_INFO
  - OCCUPATION_INFO
  - GOVERNMENT_NOTICE
- content_type
  - NEWS_ARTICLE
  - LIVING_GUIDE
  - IMMIGRATION_NOTICE
  - VISA_GUIDE
  - OCCUPATION_GUIDE
  - GOVERNMENT_ANNOUNCEMENT
  - GENERATED_GUIDE
- priority_group
  - PRIMARY
  - SECONDARY
  - TERTIARY
- category
  - jobs
  - work_visa
  - labor_rights
  - immigration
  - living
  - housing
  - banking
  - healthcare
  - transportation
  - insurance
  - korean_language
  - cost_of_living
  - visa_info
  - occupation
  - government_notice
- title
- summary_en
- why_it_matters_en
- body_en
- source_url
- source_name
- image_url nullable
- link_url
- hashtags
- language
- quality_score
- relevance_score
- practical_value_score
- urgency_score
- freshness_score
- source_reliability_score
- content_potential_score
- rotation_score
- final_publish_score
- sensitive_yn
- review_required_yn
- review_reason
- status
  - RAW
  - NORMALIZED
  - SUMMARIZED
  - SCORED
  - READY_TO_REVIEW
  - READY_TO_PUBLISH
  - POSTED
  - FAILED_RETRYABLE
  - POST_EXPIRED
  - ARCHIVED
- publish_attempt_count
- last_publish_error
- next_retry_at
- published_at
- facebook_post_id
- facebook_post_url
- created_at
- updated_at
- raw_ref_table
- raw_ref_id
- raw_payload jsonb

3. 기존 뉴스 후보 연결

기존 social_news.candidate는 유지한다.
다만 Facebook 게시기는 social_news.candidate를 직접 보지 말고 content.content_candidate를 본다.

뉴스 파이프라인은 최종 단계에서:
social_news.candidate
→ content.content_candidate 생성 또는 업데이트

중요:
- 뉴스 candidate와 content_candidate는 raw_ref_table/raw_ref_id로 연결
- 같은 기사 중복은 content_candidate를 무한 생성하지 않는다
- 대표 기사만 content_candidate가 된다

4. 게시 주기 변경

현재 1시간 게시 텀을 테스트 모드에서 30분으로 변경한다.

환경변수:
CONTENT_PUBLISH_INTERVAL_MINUTES=30
CONTENT_DAILY_MAX_POSTS=48
CONTENT_AUTO_PUBLISH=true 또는 false
CONTENT_PUBLISH_TEST_MODE=true

규칙:
- 게시 성공 후 30분 cooldown
- 하루 최대 48개
- 실패 시 cooldown 적용하지 않음
- 후보 없음 시 cooldown 적용하지 않음

5. 게시 선택 로직

content_publish_pipeline은 30분마다 실행된다.

선택 순서:
1. READY_TO_PUBLISH 후보 조회
2. 없으면 SCORED / SUMMARIZED / NORMALIZED 중 게시 가능한 후보 재평가
3. 민감/검토필요 콘텐츠 제외
4. 최근 24시간 카테고리별 게시 비율 확인
5. target priority group 결정
6. target group 내 최고 final_publish_score 선택
7. 없으면 다음 priority group으로 fallback
8. 선택 후보 게시
9. 게시 성공 시 POSTED
10. 실패 시 FAILED_RETRYABLE

6. 우선순위 정책

PRIMARY:
- jobs
- work_visa
- labor_rights
- immigration
- employment_policy
- government_notice

SECONDARY:
- living
- housing
- banking
- healthcare
- transportation
- insurance
- korean_language
- cost_of_living
- local_community

TERTIARY:
- travel
- lifestyle
- culture
- local_events
- safety

기본 비율:
- PRIMARY 2
- SECONDARY 1

테스트 모드:
- PRIMARY 2 : SECONDARY 1 : TERTIARY 1 가능
- 단 PRIMARY 후보가 있으면 PRIMARY 우선
- PRIMARY가 없을 때 SECONDARY 사용
- SECONDARY도 없으면 TERTIARY 사용

7. 카테고리별 threshold

PRIMARY:
- 기본 50
- 후보 부족 시 40까지 완화

SECONDARY:
- 기본 55
- 후보 부족 시 45까지 완화

TERTIARY:
- 기본 65
- 후보 부족 시 55까지 완화
- 55 미만 게시 금지

공통 차단:
- final message에 한글 포함
- 운영 로그 포함
- source_url/link_url 부적절
- 민감 기사 자동 게시
- 폭행/범죄/사망/정치갈등/혐오성 콘텐츠

8. 콘텐츠 생성 규칙

모든 content_candidate는 최종 게시 가능한 영어 본문을 가져야 한다.

필수:
- title
- summary_en
- why_it_matters_en
- link_url
- hashtags

Facebook message 생성:
Title

Summary:
- ...
- ...
- ...

Why it matters for foreigners in Korea:
- ...
- ...
- ...

Read more here: [link]

#...

Graph API payload:
- message
- link

message에는 긴 URL을 넣지 않는다.
link 파라미터에 link_url을 넣는다.

9. 생활정보 파이프라인 추가

living_info pipeline을 1차 skeleton으로 만든다.

초기 카테고리:
- housing
- banking
- healthcare
- transportation
- insurance
- korean_language
- cost_of_living
- local_community

수집 방식:
- 초기에는 검색 키워드 기반 뉴스/정보 페이지 수집
- 공식/신뢰 가능한 출처 우선
- 수집 결과를 content_candidate로 변환

검색 키워드 예:
- foreigners in Korea housing
- foreigners in Korea bank account
- foreigners in Korea health insurance
- foreigners in Korea transportation
- foreigners in Korea rent contract
- Korea cost of living foreigners
- Korean language support foreigners
- foreign residents Korea living guide

10. 이민/비자 정보 파이프라인 추가

immigration_info / visa_info pipeline skeleton을 만든다.

대상:
- 법무부
- 하이코리아
- 출입국외국인정책본부
- 고용노동부 외국인고용
- EPS
- 기타 공식 출처

초기 목적:
- 공식 공지/정책 변경/비자 안내 수집
- 영어 요약 생성
- content_candidate로 변환
- 자동 게시 전 REVIEW_REQUIRED 기본 적용 가능

카테고리:
- immigration
- visa_info
- stay_status
- work_visa
- government_notice
- employment_policy

11. 관리자 화면 변경

새 메뉴 또는 대시보드 추가:
콘텐츠 관리

하위 메뉴:
- 콘텐츠 대시보드
- 통합 후보
- 뉴스 기사
- 생활정보
- 출입국/비자정보
- 게시 로그
- 카테고리 설정

콘텐츠 대시보드 표시:
- 오늘 생성 후보 수
- 오늘 게시 수
- 다음 게시 가능 시간
- 30분 cooldown 상태
- 하루 최대 게시 수 / 현재 게시 수
- 카테고리별 후보 수
- 카테고리별 게시 수
- PRIMARY/SECONDARY/TERTIARY 비율
- 실패 후보 수
- 검토 필요 후보 수

통합 후보 목록:
- 상태
- 제목
- content_type
- category
- priority_group
- final_publish_score
- source_name
- link_url
- posted 여부
- created_at

상세:
- 최종 Facebook message
- link_url
- image_url
- summary_en
- why_it_matters_en
- 점수 breakdown
- 원천 데이터
- 게시 로그
- 재생성 버튼
- 수동 게시 버튼

12. Telegram 알림 변경

게시 완료 알림:
- content_type
- category
- priority_group
- final_publish_score
- title
- source_url
- facebook_post_url

게시 없음 알림:
- READY 후보 없음
- 전체 후보 없음
- 카테고리별 후보 수
- cooldown 상태와 구분

쿨다운:
- 기본적으로 Telegram 발송하지 않음
- 운영 로그에만 남김

13. 기존 뉴스 파이프라인과 충돌 방지

기존 뉴스 게시 기능은 바로 삭제하지 말고 content publisher로 우회한다.

단계:
1. 뉴스 수집은 유지
2. 뉴스 후보 생성 유지
3. Facebook publish는 content publisher가 담당
4. 기존 news auto publish는 비활성화 또는 wrapper로 변경

환경변수:
NEWS_DIRECT_FACEBOOK_PUBLISH=false
CONTENT_PUBLISHER_ENABLED=true

14. 검증

검증해야 할 것:
- 기존 뉴스 후보가 content_candidate로 생성됨
- 생활정보 후보가 content_candidate로 생성됨
- 출입국/비자 후보가 content_candidate로 생성됨
- content publisher가 30분 cooldown 기준으로 동작
- 하루 최대 48개 제한 동작
- Facebook payload에서 message와 link가 분리됨
- Telegram 알림에 content_type/category 표시됨
- 관리자 통합 후보 목록에서 전체 콘텐츠 확인 가능
- 기존 뉴스 게시 직접 호출은 꺼짐

15. 작업 완료 후 알려줄 것

- 추가한 DB migration
- 추가한 content_candidate 테이블
- 기존 news candidate와 연결 방식
- 추가한 content publisher 파일
- 기존 news publisher 비활성화 방식
- 생활정보 pipeline skeleton 위치
- immigration/visa pipeline skeleton 위치
- 관리자 화면 경로
- 환경변수 목록
- 검증 SQL
- 실행 방법