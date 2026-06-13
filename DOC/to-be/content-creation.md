### 타임스탬프 수정내용 ###

## Harness Status

Status: future concept requiring decomposition.

This document mixes several future work streams:

- occupation/reference data enrichment
- foreign-interest/community topic discovery
- local LLM analysis
- PDF/image content generation
- Facebook publishing
- admin UI workflow
- DB schema expansion

Do not implement this as one task.

Before implementation, split it into smaller `CODE_TASK_CANDIDATE` items mapped to:

- `OCCUPATION_DICTIONARY`
- `LIVING_DOMAIN`
- `CONTENT_QUEUE`
- `CONTENT_PUBLISHER`
- `FACEBOOK_PUBLISHER`
- `SCHEDULER_BOT_STATE`

Publishing, scheduler, token, and automatic selection changes are protected and require explicit approval.

직업정보 기반 콘텐츠 생성/게시 파이프라인을 설계하고 1차 구현해줘.

목표:
고용24 직무/직업정보 API에서 수집한 데이터를 단순 관리 데이터로만 두지 말고, 외국인 구직자 대상 콘텐츠로 재가공한다.
한국 취업에 관심 있는 해외 사용자들의 관심 글/댓글을 수집하고, 로컬 LLM으로 관심 직군을 분류한 뒤, 실제 한국 직업정보와 매핑하여 PDF/이미지 카드형 콘텐츠를 생성하고 Facebook에 게시할 수 있게 한다.

전제:
- EMPLOYEE_24_OPEN_API_JOB_KEY: 직무정보 API
- EMPLOYEE_24_OPEN_API_OCCUPATION_KEY: 직업정보 API
- FACEBOOK_PAGE_ID
- FACEBOOK_PAGE_ACCESS_TOKEN
- Facebook 게시에는 Page Access Token만 사용한다.
- 토큰은 절대 하드코딩하지 않는다.

1. 관리자 메뉴 구조
현재 “노동” 메뉴는 의미가 불명확하므로 “직업”으로 변경한다.

직업 메뉴 하위:
- 직무정보
- 직업정보
- 검색어 매핑
- 관심글 수집
- 콘텐츠 생성
- 콘텐츠 게시 로그

2. 직무/직업정보 수집
직무/직업정보는 채용공고처럼 실시간 데이터가 아니므로 수동 실행 또는 주 1회 수집으로 구성한다.

수집 데이터:
- 직무명
- 직업명
- 직무/직업 코드
- 설명
- 하는 일
- 필요 역량
- 관련 직업
- 관련 키워드
- 원문 raw response
- collected_at
- updated_at

주의:
- 채용정보 수집기와 분리한다.
- job collector / occupation collector를 별도 service로 만든다.
- 수집 원문은 raw로 보존한다.

3. 해외 관심글 수집
초기에는 Reddit 등 공개 커뮤니티를 대상으로 한다.
단, 플랫폼 약관과 API 정책을 지키는 구조로 설계한다.

수집 대상 예시:
- Korea jobs
- working in Korea
- E-9 visa Korea
- F-4 visa Korea
- factory job Korea
- teaching Korea
- welding Korea
- manufacturing Korea
- migrant worker Korea

저장 필드:
- source_platform
- source_url
- post_id
- comment_id
- author_hash 또는 익명화 ID
- title
- body
- comment_text
- language
- collected_at
- raw_json
- pii_checked_yn
- usable_for_content_yn

주의:
- 개인정보는 저장하지 않거나 해시 처리한다.
- 민감한 개인 사연은 그대로 콘텐츠화하지 않는다.
- 공개 데이터라도 원문 복붙 대신 요약/통계/인사이트로 사용한다.

4. 로컬 LLM 분석
로컬 Llama 또는 프로젝트 내 설정 가능한 local model endpoint를 사용한다.

댓글/글별 분석 결과:
- 관심 직군
- 관심 비자
- 관심 국가/지역
- 한국 취업 의도 점수
- 현실성 점수
- 위험 신호
- 콘텐츠화 가능 점수
- 관련 한국 직업 코드 후보
- 요약
- 태그

등급 예시:
- A: 콘텐츠화 매우 적합
- B: 콘텐츠화 가능
- C: 참고용
- D: 무관/위험/노이즈

5. 직업정보 매핑
해외 관심글에서 나온 직군/키워드를 한국 직업정보와 매핑한다.

예:
- factory work → 생산직 / 제조 단순 종사원
- welding → 용접원
- packing → 포장원
- cleaning → 청소원
- farm work → 농업 단순 종사원
- caregiver → 요양보호사 관련 직종
- construction → 건설 단순 종사원

매핑 테이블:
- external_keyword
- language_code
- normalized_keyword
- occupation_code
- job_code
- match_score
- mapping_source
- active_yn

6. PDF/이미지 콘텐츠 생성
매핑된 직업정보를 기반으로 외국인 구직자용 콘텐츠를 생성한다.

콘텐츠 형식:
- PDF
- 이미지 카드
- Facebook 게시용 요약문

PDF 구성 예시:
- Title: Working in Korea: Welding Jobs
- What this job does
- Common workplaces
- Skills needed
- Korean words to know
- Visa/eligibility note
- Salary/check official source note
- Related job titles
- Helpful links
- Disclaimer: visa/labor rules can change, check official sources

이미지/그림:
- 직업을 설명하는 대표 이미지 또는 아이콘
- 저작권 문제 없는 생성 이미지/오픈 라이선스 이미지 사용
- 이미지 생성 기능이 없으면 placeholder 또는 템플릿 기반 카드부터 구현

주의:
- 법률/비자 정보는 단정하지 않는다.
- “가능하다/보장된다” 표현 금지.
- “check official source” 문구 포함.
- 원문 커뮤니티 댓글을 직접 인용하지 않는다.

7. 콘텐츠 게시 정책
뉴스 게시와 같은 Facebook 채널을 사용하되, 뉴스와 콘텐츠 슬롯을 분리한다.

게시 판단:
- 뉴스 후보가 강하면 뉴스 우선
- 뉴스 후보가 없거나 약하면 직업 콘텐츠 후보 게시
- 1시간에 총 게시물은 최대 1개 유지
- 같은 시간에 뉴스와 직업 콘텐츠를 동시에 올리지 않는다.
- 직업 콘텐츠는 하루 최대 1~3개 제한 가능하게 설정한다.

상태:
- CONTENT_DRAFT
- READY_TO_POST
- POSTED
- POST_FAILED
- POST_EXPIRED
- ARCHIVED

8. Facebook 게시
게시에는 FACEBOOK_PAGE_ACCESS_TOKEN 사용.

게시 메시지 예시:
Thinking about working in Korea as a welder?

Here is a simple guide:
- what the job usually involves
- common workplaces
- useful Korean words
- things to check before applying

Download/read the guide:
{pdf_url}

#WorkInKorea #ForeignWorkers #KoreaJobs

9. 관리자 화면
직업 콘텐츠 메뉴에서 아래를 볼 수 있게 한다.

- 수집된 관심글 수
- LLM 분석 대기/완료 수
- 직업 매핑 결과
- 생성된 PDF/이미지 콘텐츠
- 게시 대기 콘텐츠
- 게시 완료 콘텐츠
- Facebook 반응 요약

버튼:
- 관심글 수집 실행
- LLM 분석 실행
- 직업 매핑 실행
- 콘텐츠 생성
- dry-run 게시
- 수동 게시

10. DB/로그
필요한 테이블이 없으면 추가한다.

예시:
- occupation_info
- job_info
- occupation_keyword_mapping
- foreign_interest_raw
- foreign_interest_analysis
- occupation_content
- occupation_content_asset
- occupation_content_publish_log

11. 스케줄
- 직무/직업정보 수집: 수동 또는 주 1회
- 관심글 수집: 하루 1~4회
- LLM 분석: 수집 후 batch
- 콘텐츠 생성: 하루 1회 또는 수동
- Facebook 게시: 뉴스 게시 스케줄러와 통합하여 1시간 최대 1게시 원칙 유지

12. 작업 완료 후 알려줄 것
- 수정한 파일 목록
- 추가한 메뉴/라우터
- 추가한 테이블
- 수집/분석/생성/게시 파이프라인 설명
- dry-run 실행 방법
- Facebook 실제 게시 테스트 방법
