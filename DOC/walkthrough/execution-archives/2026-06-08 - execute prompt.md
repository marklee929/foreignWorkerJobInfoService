### 타임스탬프 수정내용 ###

뉴스/콘텐츠 게시 파이프라인의 카테고리 공급 부족 문제를 해결하기 위해 동적 카테고리 순환 큐를 추가해줘.

현재 문제:
- 외국인 근로자, 비자, 노동, 채용정책 기사만으로는 1시간 1게시를 안정적으로 유지하기 어렵다.
- 핵심 기사 후보가 없을 때 게시가 멈추거나 낮은 품질 후보가 올라간다.
- WorkConnect의 장기 테마는 “Information for Living in Korea or Anywhere”이므로 일자리뿐 아니라 생활/정착 정보도 보조 콘텐츠로 필요하다.

목표:
채용/비자/노동/출입국을 1순위로 유지하되, 후보가 부족할 때 생활정보/주거/은행/보험/교통/교육/지역/여행안전 정보를 보조 큐로 사용한다.
게시기는 매시간 하나의 최적 콘텐츠를 선택하되, 카테고리 비율과 후보 품질을 동적으로 조정한다.

1. 카테고리 정의

PRIMARY 카테고리:
- jobs
- work_visa
- foreign_worker_policy
- labor_rights
- immigration
- employment_policy
- government_notice

SECONDARY 카테고리:
- housing
- banking
- healthcare
- transportation
- insurance
- korean_language
- cost_of_living
- local_community
- education
- settlement_life

TERTIARY 카테고리:
- travel
- lifestyle
- culture
- local_events
- safety

주의:
TERTIARY는 단순 여행/라이프 콘텐츠가 아니라 외국인 정착/생활에 도움이 되는 경우만 게시 후보로 사용한다.

2. 게시 우선순위

게시 후보 선택 순서:

1. PRIMARY 중 threshold 통과 후보
2. PRIMARY 중 threshold 완화 후보
3. PRIMARY 후보가 없으면 SECONDARY 후보
4. SECONDARY도 없으면 TERTIARY 중 실용성 높은 후보
5. 그래도 없으면 오늘 저장된 미게시 후보 중 안전조건 통과 최고점

게시 중단은 최후의 최후에만 발생한다.

3. 동적 비율

기본 게시 비율:
- PRIMARY : SECONDARY = 2 : 1

후보 상황에 따라 동적 조정:
- PRIMARY 후보가 충분하면 3 : 1
- PRIMARY 후보가 부족하면 1 : 1
- PRIMARY 후보가 0이면 SECONDARY/TERTIARY로 대체
- 민감 기사/저품질 기사밖에 없으면 생활정보를 우선 사용

비율 판단 기준:
- 최근 24시간 게시 이력
- 오늘 카테고리별 후보 수
- 카테고리별 평균 점수
- 마지막 게시 카테고리
- 동일 카테고리 연속 게시 횟수

4. 카테고리별 최소 점수

PRIMARY:
- 기본 50
- 부족하면 40까지 완화 가능

SECONDARY:
- 기본 55
- 부족하면 45까지 완화 가능

TERTIARY:
- 기본 65
- 부족해도 55 미만 게시 금지

민감 기사:
- 자동 게시 금지
- REVIEW_REQUIRED

5. 카테고리별 검색 키워드

PRIMARY 검색어 예:
- foreign worker visa Korea
- Korea work visa foreign workers
- E-9 visa Korea
- E-7 visa Korea
- migrant workers Korea
- labor rights foreign workers Korea
- Korea immigration policy foreign workers
- foreign employment Korea

SECONDARY 검색어 예:
- foreigners in Korea housing
- foreigners in Korea bank account
- foreigners in Korea health insurance
- foreigners in Korea transportation
- Korea cost of living foreigners
- Korean language support foreigners
- foreign residents Korea living guide
- migrant support center Korea
- foreigners Korea rent contract

TERTIARY 검색어 예:
- Korea travel safety foreigners
- Korea local life foreigners
- Korea culture guide foreigners
- expat life Korea
- foreigners living in Seoul
- foreigners living in Busan

6. 데이터 모델 확장

candidate에 아래 필드를 추가하거나 기존 필드를 확장한다.

- content_category
- content_priority_group
  - PRIMARY
  - SECONDARY
  - TERTIARY
- settlement_relevance_score
- practical_value_score
- category_rotation_score
- category_selection_reason
- is_sensitive
- review_required_reason

7. 점수 계산 보강

기존 점수 외에 다음을 추가한다.

settlement_relevance_score:
- 외국인이 한국에서 생활/정착하는 데 직접 도움이 되는 정도

practical_value_score:
- 행동 가능한 정보인지
- 서류, 절차, 기관, 비용, 위치, 주의사항이 있는지

category_rotation_score:
- 최근 같은 카테고리 게시가 많으면 감점
- 오래 안 나온 카테고리는 가점

content_potential_score:
- 나중에 카드뉴스/PDF/GPT 답변으로 확장 가능한지

8. 게시 선택 로직

게시기는 아래 방식으로 동작한다.

1. 오늘 미게시 후보 전체 조회
2. POSTED / ARCHIVED / POST_EXPIRED 제외
3. 민감 기사 제외
4. 카테고리별 후보 pool 구성
5. 최근 24시간 게시 비율 확인
6. 이번 시간에 필요한 target_category_group 결정
7. target_category_group에서 최고점 후보 선택
8. 없으면 다음 우선순위 pool로 fallback
9. 선택 후보를 READY_TO_PUBLISH로 승격
10. Facebook 게시

9. Telegram/관리자 로그

게시 선택 시 아래를 로그로 남긴다.

- target_category_group
- selected_category
- primary_candidate_count
- secondary_candidate_count
- tertiary_candidate_count
- recent_24h_category_ratio
- selected_candidate_score
- selection_reason
- fallback_used
- no_publish_reason

Telegram 게시 완료 알림에도 카테고리를 표시한다.

예:
카테고리: 생활정보 / 주거
선택 사유: PRIMARY 후보 부족으로 SECONDARY 후보 중 실용성 최고 기사 선택

10. 관리자 화면

소셜 뉴스 대시보드에 추가:
- 오늘 PRIMARY 후보 수
- 오늘 SECONDARY 후보 수
- 오늘 TERTIARY 후보 수
- 최근 24시간 카테고리별 게시 수
- 현재 목표 게시 비율
- 다음 게시 예상 카테고리

목록 필터:
- content_category
- priority_group
- sensitive/review_required
- practical_value_score

상세보기:
- 카테고리 판정 이유
- settlement relevance
- practical value
- rotation score
- selection reason

11. 콘텐츠 생성 규칙

PRIMARY:
- Work/visa/labor 중심
- “foreign workers in Korea” 표현 사용

SECONDARY:
- Living/settlement 중심
- “foreigners living in Korea” 표현 사용

TERTIARY:
- culture/travel/lifestyle이지만 실용 정보 중심
- 단순 관광 홍보 금지

게시 해시태그도 카테고리별로 분리한다.

PRIMARY:
#KoreaJobs #WorkInKorea #ForeignWorkers #VisaInfo

SECONDARY:
#LivingInKorea #ForeignersInKorea #KoreaLife #WorkConnectKorea

TERTIARY:
#KoreaLife #LivingInKorea #KoreaGuide #ForeignersInKorea

12. 안전 필터

자동 게시 금지:
- 폭행/학대/사망/범죄/정치갈등/혐오/선정적 사건
- 한국어가 섞인 게시문
- 운영 로그가 섞인 게시문
- 원문 URL이 불확실한 기사
- Google RSS만 있고 원문 확인 불가

13. 작업 완료 후 알려줄 것

- 추가/수정한 카테고리 enum
- 추가한 검색 키워드
- 게시 선택 로직 변경 위치
- 카테고리별 threshold
- 관리자 화면 변경
- Telegram 로그 변경
- 테스트 결과

### 타임스탬프 수정내용 ###

뉴스 목록과 콘텐츠 관리 목록의 데이터 기준/날짜/게시 링크 표시를 정리해줘.

현재 문제:
1. social_news 화면과 content 관리 화면의 목록 기준이 통일되지 않아 혼란스럽다.
2. 6/2에 수집된 뉴스가 content 관리 화면에서는 6/8 최신 갱신 데이터처럼 표시된다.
3. content_candidate 생성/동기화 시각이 원문 기사 수집일처럼 보인다.
4. 뉴스 목록에는 Facebook 게시글 링크가 보이는데, 정작 최종 게시 단위인 콘텐츠 관리 목록에는 Facebook 링크가 보이지 않는다.
5. content 관리에 뉴스 중복 후보가 복제되어 보이는 듯하다.

정리 원칙:
- social_news는 “뉴스 원천/기사 후보 관리 화면”
- content 관리는 “Facebook에 올릴 최종 콘텐츠 후보/게시 관리 화면”
- 두 화면은 같을 필요는 없지만, 참조 관계와 날짜 의미가 명확해야 한다.

1. content_candidate에 원천 참조 필드 확인/추가

content.content_candidate에 아래 필드를 명확히 유지한다.

- raw_ref_table
- raw_ref_id
- source_domain
- original_source_url
- original_source_name
- original_title
- original_published_at
- original_collected_at
- content_created_at
- content_updated_at
- published_at
- facebook_post_id
- facebook_post_url

주의:
created_at / updated_at은 content row 생성/수정 시각이다.
원문 기사 수집일로 보여주면 안 된다.

2. content sync 정책

social_news.candidate → content_candidate 동기화 시:

- 이미 같은 raw_ref_table + raw_ref_id가 있으면 새 row 생성하지 말고 update
- 같은 duplicate_group/topic_group 대표 기사만 content_candidate 생성
- DUPLICATE 보조 row는 content_candidate로 만들지 않음
- 대표 후보가 바뀌면 기존 content_candidate의 raw_ref_id를 갱신하거나 representative 기준으로 재연결
- 중복 기사 전체를 content_candidate로 복제하지 않음

unique constraint 권장:
- unique(raw_ref_table, raw_ref_id)
또는
- unique(source_domain, raw_ref_id)

3. 날짜 표시 정리

content 관리 목록 컬럼을 아래처럼 바꾼다.

- 상태
- 제목
- 출처 도메인
- 유형
- 분류
- 원출처
- 점수
- Facebook
- 원문 발행일
- 원문 수집일
- 콘텐츠 갱신일
- 게시일
- 제어

현재 “갱신”만 보여주는 방식은 혼란스럽다.
갱신일은 content_updated_at으로 표시하고, 원문 수집일은 original_collected_at으로 별도 표시한다.

4. Facebook 링크 위치

Facebook 게시글 링크는 content_candidate가 최종 소유한다.

게시 성공 시:
- content_candidate.facebook_post_id
- content_candidate.facebook_post_url
- content_candidate.published_at
- content_candidate.status = POSTED

를 반드시 업데이트한다.

social_news.candidate에도 기존 필드가 있으면 유지 가능하지만,
content_candidate로도 동기화해야 한다.

content 관리 목록:
- Facebook 컬럼에 게시글 링크 표시
- 게시 전이면 “-”
- 게시 실패면 실패 상태 표시

content 상세:
- Facebook 게시 URL
- Facebook post id
- 게시 로그
- 게시 payload
- 실패 원인

5. 뉴스 목록과 콘텐츠 목록 역할 분리

social_news 목록:
- 기사 원문/중복/수집 상태 확인용
- raw/news 기준
- Facebook 링크는 참고용으로만 표시 가능

content 관리 목록:
- 실제 게시 후보/게시 완료 관리용
- 최종 Facebook message 기준
- Facebook 링크 필수 표시
- 게시 가능/검토 필요/게시 완료/실패 상태 기준

6. 중복 데이터 정리

content_candidate에 중복 뉴스가 여러 건 들어갔는지 확인한다.

점검 SQL 작성:
- raw_ref_table, raw_ref_id 중복
- 같은 title/source_url 중복
- 같은 duplicate_group_id에서 여러 content_candidate 생성 여부
- POSTED인데 facebook_post_url 없는 건
- social_news에는 facebook_post_url 있는데 content_candidate에는 없는 건

중복 content_candidate가 있으면:
- 대표 content_candidate만 유지
- 나머지는 ARCHIVED 또는 DUPLICATE_CONTENT로 상태 변경
- 삭제하지 말고 상태로 정리

7. 관리자 표시 개선

content 관리 목록에 source 기준을 명확히 표시:
- 출처 도메인: 소셜 뉴스 / 출입국 / 생활정보
- 원출처: Korea Herald, Naver News 등
- 유형: 뉴스, 생활가이드, 정부공지 등

뉴스 원천 화면에는 content 연결 상태 표시:
- content_candidate_id
- content_status
- content_posted_yn
- content_facebook_post_url

8. 작업 완료 후 알려줄 것

- content_candidate 동기화 기준
- 중복 content_candidate 정리 방식
- 날짜 컬럼 의미
- Facebook 링크 동기화 방식
- 수정한 파일 목록
- 검증 SQL

### 타임스탬프 수정내용 ###

2026-06-09 05:00:00 KST까지 WorkConnect 프로젝트 전체 오버룩을 진행해줘.

작업 시간 기준:
- 시작: 지금부터
- 종료 목표: 2026-06-09 05:00:00 KST
- 05:00 이후에는 신규 대형 작업을 시작하지 말고, 진행 중인 작업 정리/문서화/검증/커밋만 수행
- 05:00까지 완료하지 못한 항목은 TODO 문서로 넘겨라
- 출근 시간 동안 Codex 사용 쿨타임이 회복될 수 있도록 05:00 이후 장시간 작업은 중단한다

종료 조건:
- 2026-06-09 05:00:00 KST 도달
- 또는 안전하게 적용 가능한 개선이 끝나고, 남은 작업이 대규모 리팩토링뿐일 때

종료 시 반드시 수행:
1. 작업 요약 작성
2. 수정 파일 목록 작성
3. 검증 결과 작성
4. 미완료 TODO 작성
5. 마지막 커밋 또는 변경사항 보존

목표:
현재 프로젝트 전체 구조를 점검하고, 화면별 개선점 / UI 개선점 / 조회 속도 개선점 / 데이터 파이프라인 정합성 문제를 정리한 뒤, 안전하게 적용 가능한 개선은 직접 반영한다.

중요:
무작정 대규모 리팩토링하지 말 것.
먼저 전체 구조를 파악하고, 영향 범위가 작은 성능/UI/조회 개선부터 적용한다.
DB 구조 변경이 필요한 작업은 반드시 migration과 검증 SQL을 함께 작성한다.
위험한 삭제 작업 금지. 데이터 삭제 대신 ARCHIVED / DISABLED / DUPLICATE_CONTENT 같은 상태값으로 처리한다.

1. 전체 프로젝트 구조 파악

다음 영역을 확인해줘.

- 관리자 서버
- 관리자 UI
- 소셜 뉴스 파이프라인
- 콘텐츠 관리 파이프라인
- 직업정보 파이프라인
- 출입국/생활정보 예정 구조
- Facebook 게시 모듈
- Telegram 알림 모듈
- LLaMA 연결/토글 모듈
- DB repository / migration
- scheduler / bot status / env 설정
- DOC / walkthrough / to-be 문서

확인 후 프로젝트 구조 요약을 문서로 남겨라.

문서 위치:
DOC/walkthrough/2026-06-09-project-overview.md

2. 화면별 역할 정리

현재 관리자 화면의 역할을 재정의해줘.

대시보드:
- 운영 상태판
- count / status / 최근 로그만 표시
- 무거운 목록 조회 금지

소셜 뉴스:
- 원천 뉴스 수집/중복/본문/원문 확인 화면
- 기사 후보의 상태 확인
- content_candidate 연결 상태 표시

콘텐츠 관리:
- 최종 Facebook 게시 후보/게시 완료 관리 화면
- 실제 게시 본문, link_url, facebook_post_url 관리
- content_candidate 기준

직업정보:
- 고용24 직업/직무 코드 사전
- 영문명/검색어/비자태그/콘텐츠 보강 예정

출입국:
- 공식 공지/비자/체류 정책 수집 예정

생활정보:
- 정착 정보/주거/은행/보험/교통/생활비 수집 예정

LLaMA:
- 로컬/외부 LLM 상태
- 모델 unload / 서버 종료 / 자동사용 OFF 구분

각 화면별로:
- 현재 역할
- 문제점
- 개선안
- 바로 적용한 변경
- 후속 작업
을 정리해줘.

3. 대시보드 성능 개선

현재 대시보드는 화면 이동 시마다 느려지는 문제가 있다.

수정 목표:
- 대시보드는 summary API만 호출
- 전체 row 조회 금지
- count/group by/limit 기반으로 조회
- 프론트 store cache/TTL 적용
- 화면 전환 시 TTL 안이면 재조회하지 않음

확인할 것:
- 대시보드 진입 시 전체 news candidate를 list로 가져오는지
- 전체 content candidate를 가져오는지
- 전체 pipeline_log를 가져오는지
- 프론트에서 화면 전환마다 중복 API 호출하는지
- polling이 중복 등록되는지
- setInterval cleanup 누락이 있는지

적용할 것:
- GET /api/admin/dashboard/summary 또는 기존 summary API 최적화
- count 쿼리 사용
- recent logs는 limit 10~20
- dashboardStore TTL 30초
- document hidden 상태에서는 polling 중지
- 새로고침 버튼은 force refresh
- 캐시된 데이터가 있으면 먼저 표시 후 백그라운드 갱신

검증:
- Network 탭 기준 대시보드 진입 API 수 감소
- 화면 전환 후 30초 이내 재진입 시 API 재호출 없음
- summary 응답에 목록 전체가 포함되지 않음

4. 소셜 뉴스 vs 콘텐츠 관리 정합성 확인

현재 문제:
- 소셜 뉴스 목록과 콘텐츠 관리 목록의 기준이 불명확하다.
- 6/2 수집 뉴스가 콘텐츠 관리에서는 6/8 갱신 데이터처럼 보인다.
- Facebook 게시글 링크는 뉴스 쪽에 보이는데 콘텐츠 관리에는 안 보인다.
- content_candidate가 뉴스 중복 row를 복제해서 들고 있는 것처럼 보인다.

확인할 것:
- social_news.candidate와 content.content_candidate 연결 방식
- raw_ref_table / raw_ref_id 사용 여부
- 같은 social_news candidate에서 content_candidate 중복 생성 여부
- 같은 duplicate_group에서 content_candidate 여러 건 생성 여부
- facebook_post_url이 social_news에만 있고 content_candidate에 없는 케이스
- content updated_at이 원문 수집일처럼 화면에 표시되는지

수정 목표:
- social_news = 원천 뉴스 관리
- content = 최종 게시 콘텐츠 관리
- content_candidate는 뉴스 복사본이 아니라 최종 게시 후보
- 대표 뉴스 후보만 content_candidate로 생성
- DUPLICATE 보조 row는 content_candidate로 만들지 않음
- 게시 성공 시 content_candidate.facebook_post_url 반드시 업데이트
- 뉴스 화면에는 content 연결 상태 표시

콘텐츠 관리 목록 날짜 컬럼:
- 원문 발행일
- 원문 수집일
- 콘텐츠 생성일
- 콘텐츠 갱신일
- 게시일

기존 “갱신”만 보여주는 방식은 혼란스러우므로 분리해줘.

5. Facebook 게시 품질 점검

최근 문제:
- Summary가 제목 반복으로 생성됨
- Why it matters에 “관리자 재게시 요청” 같은 운영 로그가 들어감
- 한글이 최종 Facebook 게시 본문에 섞임
- Google RSS URL/잘못된 path URL이 link로 들어감
- message와 link 분리가 불완전함
- Facebook 카드가 붙지 않는 경우가 있음

확인할 것:
- FacebookPublisher payload
- message와 link 파라미터 분리 여부
- final message 생성 함수
- generated_summary_en fallback
- generated_why_it_matters_en fallback
- selection_reason / skip_reason / repost_reason / pipeline_log가 콘텐츠에 섞이는지
- 한글 포함 검증 여부
- link_url valid 검증 여부

필수 수정:
- 최종 Facebook 게시 본문은 영어만 허용
- 운영 로그/점수/상태값/관리자 메시지는 게시 본문 입력으로 사용 금지
- Summary / Why it matters는 article/content 데이터만 사용
- message에는 긴 URL 넣지 말고 Graph API link 파라미터 사용
- Google RSS URL은 link로 사용 금지
- publisher root URL은 link로 사용 금지
- /path/A... 같은 임시/legacy redirect URL보다 canonical article URL 우선
- 한글 포함/운영로그 포함/부적절 link면 게시 전 차단하고 REVIEW_REQUIRED 또는 CONTENT_INVALID 처리

차단 키워드:
- 관리자
- 재게시
- 게시 기준
- 현재 점수
- READY_TO_PUBLISH
- threshold
- candidate
- queue
- publish_status
- Facebook 게시를 시도
- 즉시 Facebook

6. 민감 콘텐츠 필터 점검

민감 기사 자동 게시 방지:
- 폭행
- 학대
- 사망
- 범죄
- 정치갈등
- 혐오
- 선정적 사건
- 피해자 신상 노출 가능 기사

정책:
- 민감 기사는 REVIEW_REQUIRED_SENSITIVE
- 자동 게시 금지
- 관리자 수동 승인 후 게시 가능
- 완전히 버리지는 말고 데이터로 보관

민감 기사용 재작성 가이드:
- 자극적 표현 최소화
- 피해자 신상 과다 노출 금지
- 노동권/지원기관/비자/고용규칙 중심으로 실용화
- 확정되지 않은 사실 단정 금지

7. 콘텐츠 통합 큐 구조 점검

현재 방향:
뉴스 파이프라인과 Facebook 게시 파이프라인을 분리한다.
뉴스는 전체 콘텐츠 후보 중 하나로 취급한다.

확인할 것:
- content_candidate 테이블/모델/API가 있는지
- 뉴스 후보가 content_candidate로 동기화되는지
- 게시기는 social_news를 직접 보는지, content_candidate를 보는지
- NEWS_DIRECT_FACEBOOK_PUBLISH 같은 직접 게시 우회 플래그가 있는지
- content publisher가 별도로 존재하는지

정리 목표:
- 수집 파이프라인: 뉴스/생활정보/출입국/직업정보 등
- 게시 파이프라인: 통합 content_candidate 큐에서 선택
- 테스트 모드 게시 간격 30분
- 하루 최대 48개
- 실패 시 cooldown 적용하지 않음
- 후보 없음과 cooldown 메시지 구분

아직 구현 전이면:
- 현재 상태 분석만 하고 TODO 문서화
- 무리하게 전면 전환하지 말 것

8. 직업정보 화면 개선점 점검

현재 직업정보 API는 코드/직업명 중심이라 활용성이 낮다.

확인할 것:
- occupation/job_info 테이블
- 수집 로그
- 목록/상세 화면
- 영문명/검색어/비자태그/외국인 적합도 보강 여부

개선 방향 문서화:
- 직업정보는 콘텐츠가 아니라 기준 코드 사전
- enrichment 파이프라인 필요
- occupation_name_en
- search_keywords_en
- visa_tags
- industry_tags
- foreign_worker_fit
- content_potential_score
- content_ready_yn

가능하면 화면에 “보강 예정” 상태를 명확히 표시해줘.

9. LLaMA 토글/상태 개선점 점검

현재 문제:
- LLaMA ON/OFF가 모델 unload인지 서버 종료인지 불명확함
- 메모리 사용량 때문에 게임/일반 작업 시 꺼야 함
- 로컬/외부 서버 처리 방식 구분 필요

정리할 상태:
- LLaMA 자동 사용 ON/OFF
- 모델 unload
- Ollama 서버 종료
- 외부 서버 연결 disabled
- 로컬 서버 connected/disconnected
- current model
- endpoint

UI 문구:
- “LLaMA 모델 중지”
- “Ollama 서버 종료”
- “자동 사용 OFF”
를 구분.

10. 조회 속도 개선

전체적으로 아래 패턴을 찾아 개선해줘.

금지 패턴:
- list all 후 Python/JS에서 count
- 화면 진입마다 전체 row 조회
- pipeline_log 전체 조회
- content_candidate 전체 조회
- setInterval 중복 등록
- route 이동 후 polling cleanup 누락
- 대시보드에서 상세 목록 API 호출

개선:
- SQL count/group by
- pagination
- limit
- index
- store cache TTL
- lazy loading
- 상세는 클릭 시 로딩
- 로그는 최근 20건만

필요 index 후보:
- social_news.candidate(status)
- social_news.candidate(publish_status)
- social_news.candidate(cycle_id)
- social_news.candidate(collected_at)
- social_news.candidate(duplicate_group_id)
- content.content_candidate(status)
- content.content_candidate(content_type)
- content.content_candidate(category)
- content.content_candidate(created_at)
- content.content_candidate(raw_ref_table, raw_ref_id)
- pipeline_log(created_at)

11. UI 개선

전체 관리자 UI에서 다음을 점검해줘.

- 각 화면 제목과 설명이 역할을 잘 드러내는지
- 목록 컬럼이 너무 많아 가독성이 떨어지는지
- 날짜 의미가 불명확한지
- 상태 배지가 통일되어 있는지
- 점수 0이 “평가 안 됨”인지 “저품질”인지 구분되는지
- Facebook 링크가 최종 콘텐츠 화면에 있는지
- 게시 가능/검토 필요/게시 완료/실패 상태가 명확한지
- 새로고침/수동 실행/게시 버튼이 위험한 작업인지 구분되는지
- destructive action은 confirm이 있는지
- 모바일 또는 좁은 화면에서 깨지는지

가능한 작은 개선은 적용하고, 큰 개선은 TODO로 문서화해줘.

12. 산출물

반드시 아래 문서를 생성/업데이트해줘.

A. DOC/walkthrough/2026-06-09-project-overview.md
내용:
- 전체 구조 요약
- 화면별 역할
- 데이터 흐름
- 봇/스케줄러 구조
- 주요 문제
- 개선 우선순위

B. DOC/to-be/ADMIN_UI_IMPROVEMENT.md
내용:
- 화면별 개선점
- UI 개선점
- 조회 속도 개선점
- 데이터 정합성 개선점
- 우선순위
- 예상 작업 난이도

C. DOC/to-be/CONTENT_PIPELINE_REFACTOR.md
내용:
- 뉴스 파이프라인과 게시 파이프라인 분리 방향
- content_candidate 통합 큐 구조
- 30분 게시 테스트 구조
- 생활정보/출입국/직업정보 연결 방향
- 위험 요소

13. 직접 적용 가능한 작업

아래는 직접 적용해도 됨:
- summary API 최적화
- dashboard store cache
- polling cleanup
- 최근 로그 limit 적용
- 목록 pagination 누락 보완
- 날짜 컬럼 라벨 수정
- Facebook 링크 표시 위치 보완
- 게시 본문 한글/운영로그 차단
- dashboard UX 문구 개선
- 작은 index migration 추가

아래는 문서화만 하고 직접 적용 전 확인 필요:
- content_candidate 전체 구조 변경
- 기존 news direct publish 완전 제거
- DB 데이터 대량 정리
- 중복 content 후보 대량 archive
- 생활정보/출입국 파이프라인 대규모 구현
- LLaMA 서버 kill 기능

14. 검증

작업 완료 후 다음을 실행/확인해줘.

- python -m py_compile 관련 Python 파일
- npm run build 또는 프론트 빌드
- 대시보드 summary API 응답 확인
- 소셜 뉴스 목록 정상 조회
- 콘텐츠 관리 목록 정상 조회
- Facebook 게시 본문 생성 검증
- 최종 게시 본문에 한글/운영로그가 섞이지 않는지 확인
- dashboard 화면 전환 시 API 중복 호출 감소 여부 확인

15. 작업 완료 보고

완료 후 아래 형식으로 보고해줘.

1. 전체 구조 요약
2. 발견한 주요 문제
3. 직접 수정한 항목
4. 문서화한 TODO
5. 성능 개선 내용
6. UI 개선 내용
7. 데이터 정합성 이슈
8. 위험하거나 보류한 작업
9. 수정 파일 목록
10. 검증 결과