### 타임스탬프 수정내용 ###

WorkConnect 관리자에 “출입국정보/정부발표” 파이프라인을 구축해줘.

현재 상황:
- 뉴스 자동 배포 파이프라인은 어느 정도 동작한다.
- 직업정보 API 수집은 완료했지만 원천 데이터가 코드/직업명 중심이라 보강이 필요하다.
- 다음 단계로 외국인에게 직접 영향이 큰 출입국/비자/체류 정책 정보를 공식 출처 중심으로 수집하려고 한다.

목표:
법무부, 하이코리아, 출입국외국인정책본부 등 공식 출처의 공지사항/보도자료/정책 변경 정보를 수집·정규화·요약·게시 후보화하는 파이프라인을 만든다.

중요:
이 파이프라인은 일반 뉴스가 아니라 “공식 정책/공지 데이터”다.
따라서 social_news와 분리된 immigration_info 또는 government_notice 계열로 설계한다.

1. 관리자 메뉴

현재 메뉴에 “출입국” 메뉴가 있다면 그 메뉴를 사용한다.

출입국
- 대시보드
- 정부 발표
- 비자/체류 정보
- 수집 로그
- 게시 후보

2. 데이터 출처

초기 공식 출처 후보:
- 법무부 보도자료/공지사항
- 출입국외국인정책본부 공지사항
- 하이코리아 공지사항
- 고용노동부 외국인고용 관련 공지
- EPS 외국인고용관리 공지사항

요구:
- API가 있으면 API 우선
- API가 없으면 RSS/HTML 공지 목록 수집
- 무리한 크롤링 금지
- 공식 사이트만 1차 대상
- robots.txt나 접근 제한이 있으면 수집 실패 로그를 남기고 중단

3. DB 설계

PostgreSQL 사용.
SQLite 사용 금지.

가능하면 새 스키마 생성:
immigration_info

테이블 예시:

A. immigration_info.official_notice
- id
- source
- source_name
- source_type
  - MINISTRY_OF_JUSTICE
  - HIKOREA
  - IMMIGRATION_OFFICE
  - MOEL
  - EPS
- notice_type
  - ANNOUNCEMENT
  - PRESS_RELEASE
  - VISA_POLICY
  - STAY_STATUS
  - EMPLOYMENT_POLICY
  - SUPPORT_PROGRAM
- title_ko
- title_en
- original_url
- canonical_url
- published_at
- collected_at
- updated_at
- raw_content_ko
- raw_content_en nullable
- summary_en
- why_it_matters_en
- affected_visa_types jsonb
- affected_user_groups jsonb
- region_tags jsonb
- policy_keywords jsonb
- importance_score
- urgency_level
- content_status
  - RAW_COLLECTED
  - NORMALIZED
  - SUMMARIZED
  - READY_TO_REVIEW
  - READY_TO_PUBLISH
  - POSTED
  - ARCHIVED
  - FAILED
- active_yn
- raw_response jsonb

B. immigration_info.collect_log
- id
- collector_type
- source_name
- status
- requested_count
- inserted_count
- updated_count
- skipped_count
- failed_count
- started_at
- finished_at
- error_message
- request_params jsonb

C. immigration_info.publish_log
- id
- notice_id
- facebook_post_id
- facebook_post_url
- status
- error_message
- posted_at
- created_at

4. 수집기 구조

collector를 출처별로 분리한다.

예:
- MinistryJusticeNoticeCollector
- HiKoreaNoticeCollector
- ImmigrationOfficeNoticeCollector
- MoelForeignWorkerNoticeCollector
- EpsNoticeCollector

공통 인터페이스:
collect(limit=20) -> list[OfficialNoticeItem]

OfficialNoticeItem 필드:
- source
- source_name
- notice_type
- title
- url
- published_at
- summary
- content
- raw_payload

5. 정규화

수집 후 정규화한다.

정규화 항목:
- 제목 정리
- 원문 URL canonical 처리
- 본문 텍스트 추출
- 날짜 파싱
- 중복 제거
- 비자 유형 추출
- 사용자 그룹 태그 추출

비자 유형 태그 예:
- E-9
- E-7
- E-2
- F-4
- F-6
- D-2
- D-10
- H-2
- C-3
- G-1

사용자 그룹 태그 예:
- foreign_workers
- international_students
- marriage_immigrants
- employers
- undocumented_risk
- skilled_workers
- seasonal_workers
- eps_workers

6. 요약 생성

공식 공지는 한국어일 가능성이 높으므로 영어 요약을 생성한다.

Facebook 게시용 생성 규칙:
- 영어 100%
- 공식 발표 내용만 요약
- 과장 금지
- 법률 자문처럼 단정 금지
- “check official source” 문구 포함 가능
- visa/stay/employment impact 중심

포맷:

Title

Summary:
- ...
- ...
- ...

Why it matters for foreigners in Korea:
- ...
- ...
- ...

Official source:
[link]

#KoreaVisa #ImmigrationKorea #WorkInKorea #ForeignersInKorea

주의:
- “foreign workers”만이 아니라 foreigners in Korea로 넓게 표현
- 출입국/체류 정보는 구직자뿐 아니라 유학생, 결혼이민자, 고용주도 대상

7. 중요도 점수

뉴스 점수와 별도로 공식 공지 중요도 점수를 만든다.

importance_score 구성:
- visa impact
- employment impact
- legal/status impact
- affected group size
- official source reliability
- urgency
- freshness

우선순위:
- 비자/체류자격 변경: HIGH
- 신청 기간/마감일: HIGH
- 외국인 고용 제도 변경: HIGH
- 단순 행사/홍보: LOW
- 일반 보도자료: MEDIUM

8. 게시 정책

공식 공지는 신뢰도가 높지만 법적 민감성이 있으므로 자동 게시 전 검토 단계를 둔다.

초기 정책:
- importance_score >= 70 이면 READY_TO_REVIEW
- 관리자가 승인하면 READY_TO_PUBLISH
- 완전 자동 게시는 추후 활성화

단, 실험 모드에서는:
- AUTO_PUBLISH_OFF 기본값
- dry-run 가능

9. 관리자 API

GET /admin/immigration/dashboard
- 총 공지 수
- 오늘 수집 수
- source별 수
- visa tag별 수
- 최근 수집 상태
- READY_TO_REVIEW 수
- POSTED 수

GET /admin/immigration/notices
- 목록
- page, size
- keyword
- source_type
- notice_type
- visa_type
- content_status
- importance_min

GET /admin/immigration/notices/{id}
- 상세

POST /admin/immigration/collect
- 전체 수집 실행

POST /admin/immigration/collect/{source}
- 특정 출처 수집 실행

POST /admin/immigration/notices/{id}/summarize
- 요약 재생성

POST /admin/immigration/notices/{id}/approve
- 게시 승인

POST /admin/immigration/notices/{id}/publish
- Facebook 게시

GET /admin/immigration/collect-logs
- 수집 로그

10. 관리자 화면

출입국 > 대시보드
- 총 공식 공지
- 오늘 수집
- 출처별 수
- 비자 태그별 수
- 검토 대기
- 게시 완료
- 최근 수집 로그

출입국 > 정부 발표 목록
컬럼:
- 상태
- 제목
- 출처
- 유형
- 비자 태그
- 대상 그룹
- 중요도
- 발행일
- 수집일
- 게시 여부

상세:
- 원문 제목
- 원문 URL
- 원문 본문
- 영어 요약
- Why it matters
- 영향 비자
- 영향 대상
- 중요도 점수
- raw_response
- 수집 로그
- 게시 로그

버튼:
- 원문 열기
- 요약 재생성
- 검토 승인
- Facebook 게시
- 보관 처리

11. 중복 처리

공식 공지는 같은 내용이 여러 출처에 재게시될 수 있다.

정책:
- 같은 original_url은 중복
- 같은 title + published_at은 중복
- 같은 정책 내용이 여러 기관에 올라오면 related_notice로 묶음
- 삭제하지 말고 duplicate_group_id로 관리

12. 검증

작업 완료 후 확인:
- 출입국 메뉴 접근 가능
- official_notice 테이블 생성
- collect_log 저장
- 수동 수집 버튼 동작
- 공식 출처 1개 이상에서 데이터 수집
- 목록/상세 조회 가능
- 영어 요약 생성 가능
- READY_TO_REVIEW 상태 생성
- 승인 후 게시 후보 전환 가능

13. 작업 완료 후 알려줄 것

- 실제 구현한 출처 목록
- API/RSS/HTML 중 어떤 방식으로 수집했는지
- 추가한 DB migration
- 추가한 테이블
- 추가한 관리자 API
- 추가한 관리자 화면 경로
- 수집 실행 방법
- 검증 SQL
- 아직 막힌 출처와 이유