### 타임스탬프 수정내용

뉴스 게시 콘텐츠 생성 로직을 개선해줘.

현재 문제:

* Google News RSS 기사인 경우 원문 URL 대신 Google 뉴스 해시 링크(news.google.com/rss/articles/...)가 저장된다.
* Facebook 게시 시 "Why it matters for foreign workers in Korea" 섹션이 한국어로 생성되거나 번역 품질이 일정하지 않다.
* 외국인 대상 페이지이므로 게시 본문은 영어 중심으로 구성되어야 한다.

수정 목표:
Google News 링크를 원문 기사 링크로 변환한 뒤, 외국인 구직자 관점의 영문 요약과 "Why it matters for foreign workers in Korea" 섹션을 생성하여 게시한다.

1. 원문 링크 처리

Google News 기사인 경우:

* news.google.com/rss/articles/*
* news.google.com/articles/*

수집 후 반드시 원문 기사 링크를 추출한다.

우선순위:

1. Google News redirect 해석
2. RSS source URL 확인
3. 기사 페이지 메타데이터 canonical URL 확인
4. 최종 publisher 원문 URL 저장

DB 저장:

* google_news_url
* source_url (실제 원문)
* canonical_url
* publisher_name

Facebook에는 Google 링크를 사용하지 말고 source_url 사용.

2. 기사 요약 생성

기사 내용을 기반으로 영문 요약 생성:

제약:

* 3~5줄
* 사실 중심
* 과장 금지
* 기사에 없는 내용 추가 금지

예시:

Summary:

* South Korea has announced new policies affecting foreign workers.
* The measures are expected to improve labor market flexibility.
* Employers and job seekers may see changes in hiring requirements.

3. Why it matters for foreign workers in Korea

반드시 영어로 생성.

규칙:

* 외국인 근로자 또는 한국 취업 희망자 관점
* 2~4개 bullet
* 기사 내용에서 파생 가능한 범위만 설명
* 비자, 취업, 정착, 노동시장 영향 중심

예시:

Why it matters for foreign workers in Korea

* The policy may create new employment opportunities for foreign workers.
* Visa or hiring requirements could be affected by future implementation details.
* Job seekers should monitor official announcements for updated eligibility criteria.

4. 게시 포맷

Title

Summary:

* bullet
* bullet
* bullet

Why it matters for foreign workers in Korea:

* bullet
* bullet
* bullet

Read more:
{source_url}

#KoreaJobs #WorkInKorea #ForeignWorkers #VisaInfo

5. 언어 정책

Facebook 게시용 콘텐츠:

* 영어 100%

관리자:

* 원문 언어 저장
* 한국어 번역 저장 가능

Telegram 운영 알림:

* 한국어 유지

6. 저장

candidate:

* generated_title
* generated_summary_en
* generated_why_it_matters_en
* source_url
* canonical_url
* publisher_name

7. 관리자 상세보기

표시:

* Google URL
* 원문 URL
* 기사 원문
* 영문 요약
* Why it matters
* 최종 Facebook 게시 본문

8. 검증

작업 완료 후 알려줄 것:

* Google 링크 → 원문 링크 변환 위치
* 수정한 파일 목록
* Facebook 최종 게시 예시
* 관리자 상세보기 변경 내용


### 타임스탬프 수정내용

뉴스 게시 후보 선택 로직과 Telegram 상태 메시지를 수정해줘.

현재 문제:

1. READY_TO_PUBLISH 후보가 없으면 바로 "게시 후보 없음"으로 종료한다.
2. 이미 수집된 당일 기사 중 게시되지 않은 기사들을 재평가하지 않는다.
3. 20분마다 기사 수집, 1시간마다 게시 구조인데 중간에 수집된 기사들이 게시 대기열에 유지되지 않는다.
4. 실제로는 게시 가능한 후보가 있는데도 "게시 후보 없음" 메시지가 발송된다.
5. "후보 없음"과 "쿨다운(1시간 대기)" 상태가 동일한 메시지로 표시된다.
6. Facebook 게시 실패 기사도 다음 후보군에서 재활용되지 않는다.

목표:

수집과 게시를 분리한다.

수집:

* 20분 주기

게시:

* 1시간 주기

게시기는 매 실행마다 당일 저장된 기사 전체를 기준으로 재평가하여 가장 적절한 기사 1건을 선택해야 한다.

1. 후보 재평가 로직

게시 실행 시:

조회 대상:

* READY_TO_PUBLISH
* FAILED_RETRYABLE
* SCORED
* NORMALIZED
* SKIPPED_LOW_SCORE
* 오늘 수집된 미게시 기사

제외:

* POSTED
* POST_EXPIRED
* ARCHIVED

조회 범위:
오늘 00:00 이후 수집 기사 전체

정책:
READY가 없다고 종료하지 않는다.

2. 동적 점수 완화

초기 기준:

minimum_safe_score = 50

후보가 없으면:

50 → 45 → 40

순차적으로 낮춘다.

40 미만은 게시 금지.

매 단계마다 재검색:

score >= 50

없음

score >= 45

없음

score >= 40

없음

그때만 NO_SAFE_CANDIDATE

3. 평균 점수 기반 보정

오늘 기사 평균 점수 계산.

예:

avg_score = 57

우선순위:

score >= avg_score

없으면

score >= avg_score - 5

없으면

score >= avg_score - 10

없으면

minimum_safe_score 적용

즉 절대 점수와 상대 점수를 혼합.

4. 게시 대기열 유지

20분마다 수집되더라도:

게시되지 않은 기사는 계속 대기열에 남아야 한다.

예:

09:00 수집

09:20 수집

09:40 수집

10:00 게시

이 경우:

09:20 기사

09:40 기사

가 자동으로 사라지면 안 된다.

POSTED 되기 전까지는 후보군 유지.

5. 실패 기사 처리

Facebook 실패 시:

FAILED_RETRYABLE

상태 유지.

다음 게시 사이클에 다시 평가 대상 포함.

단:

publish_attempt_count >= 3

이면

AUTO_RETRY_BLOCKED

수동 repost 가능.

6. Telegram 메시지 구분

현재 문제:

모든 상황을 "게시 후보 없음"으로 표시.

반드시 분리:

A. WAITING_COOLDOWN

마지막 게시 후 60분 미만.

예:

⏳ News Publishing Cooldown

Last post:
2026-06-03 20:05

Next publish:
2026-06-03 21:05

Remaining:
22 minutes

이 경우 후보 없음 메시지 금지.

B. NO_CANDIDATE

실제로 후보 없음.

예:

⚠️ No Publish Candidate Found

Ready:
0

Expanded:
0

Today's Articles:
0

C. NO_SAFE_CANDIDATE

기사는 있음.

하지만 점수 조건 미달.

예:

⚠️ No Safe Candidate

Today's Articles:
23

Average Score:
38

Threshold:
40

D. FACEBOOK_ERROR

게시 실패.

예:

⚠️ Facebook Publish Failed

Candidate:
123

Reason:
Permission missing

Status:
FAILED_RETRYABLE

7. 운영 로그 추가

매 게시 실행 시 저장:

ready_count

retryable_count

expanded_count

today_article_count

today_unposted_count

avg_score

threshold_used

selected_candidate_id

selected_score

selected_from_status

cooldown_remaining

publish_attempted

publish_result

no_publish_reason

8. 관리자 화면

표시:

오늘 수집 기사 수

오늘 미게시 기사 수

평균 점수

현재 threshold

READY 후보 수

FAILED_RETRYABLE 수

POSTED 수

COOLDOWN 상태

다음 게시 가능 시간

9. 핵심 원칙

READY_TO_PUBLISH가 없다는 이유로 종료하지 않는다.

게시기는 항상:

당일 저장된 기사
+
실패 기사
+
대기 기사

전체를 다시 평가해서
가장 적합한 기사 1건을 찾는다.

"게시 후보 없음"은 최후의 최후에만 발생해야 한다.

작업 완료 후 알려줄 것:

1. 기존 후보 없음 판단 위치
2. 수정한 파일 목록
3. 후보 재평가 흐름
4. Telegram 상태 분리 결과
5. 게시 대기열 유지 방식
6. 평균 점수 기반 보정 로직

### 타임스탬프 수정내용 ###

소셜 뉴스 데이터 파이프라인 정합성을 점검하고 리팩토링해줘.

현재 확인된 문제:
- social_news.candidate는 800건 이상 계속 증가한다.
- 그런데 social_news.raw_item과 social_news.normalized_item은 39건 수준으로 고정되어 있다.
- 어제도 39건, 오늘도 39건으로 보이므로 raw/normalized에 insert가 제대로 안 되거나, 중간에 delete/update/upsert로 덮어쓰는 로직이 있는 것으로 의심된다.
- candidate와 raw_item / normalized_item 수가 너무 상이해서 데이터 흐름을 검증해야 한다.

1. 원인 분석

아래를 코드와 DB 기준으로 확인해줘.

확인 대상:
- raw_item insert 로직
- normalized_item insert 로직
- candidate insert 로직
- upsert conflict key
- delete / cleanup / truncate 로직
- cycle 종료 시 정리 로직
- SQLite → PostgreSQL 마이그레이션 영향
- candidate가 raw_item_id / normalized_item_id를 제대로 참조하는지

확인할 것:
- candidate 생성 시 raw_item_id가 있는가
- candidate 생성 시 normalized_item_id가 있는가
- raw_item 없이 candidate만 생성되는 경로가 있는가
- normalized_item 없이 candidate만 생성되는 경로가 있는가
- similarity_key unique 때문에 normalized_item이 덮어써지는가
- source_url unique 때문에 raw_item이 덮어써지는가
- batch/cycle마다 candidate만 중복 생성되는가

2. 기대하는 데이터 생명주기

정상 흐름은 아래와 같아야 한다.

raw_item:
- 수집된 원천 기사 1건당 1row
- source_url 또는 canonical_url 기준 중복 가능성 체크
- 원문/구글 링크/원본 링크/source_name/raw_title/raw_summary/raw_content 저장
- 삭제하지 않음

normalized_item:
- raw_item을 정규화한 결과
- raw_item_id를 참조
- normalized title/summary/content/similarity_key 저장
- 중복이면 기존 normalized group에 연결하되 원본 raw는 보존

candidate:
- 게시 후보
- normalized_item_id 또는 topic_group_id 기준 대표 후보
- 같은 기사/주제의 중복 후보를 매번 새로 만들지 않음
- 게시 판단용 상태/점수/페북 정보 저장

3. DB 정합성 점검 SQL 작성

아래를 확인할 수 있는 SQL을 추가하거나 문서화해줘.

- 테이블별 건수
- 날짜별 raw_item 수
- 날짜별 normalized_item 수
- 날짜별 candidate 수
- raw_item 없는 candidate 수
- normalized_item 없는 candidate 수
- 같은 source_url로 중복 생성된 candidate 수
- 같은 similarity_key로 묶인 raw_item 수
- candidate가 참조하는 normalized_item 분포
- delete/update가 발생한 흔적

예시:

select count(*) from social_news.raw_item;
select count(*) from social_news.normalized_item;
select count(*) from social_news.candidate;

select date(collected_at), count(*)
from social_news.raw_item
group by date(collected_at)
order by date(collected_at) desc;

select similarity_key, count(*)
from social_news.normalized_item
group by similarity_key
having count(*) > 1
order by count(*) desc;

4. raw/normalized 39건 고정 원인 수정

원인이 upsert conflict라면:
- 기존 row를 덮어쓰더라도 collected occurrence는 별도 raw_item으로 남겨라.
- source_url이 완전히 같으면 raw_item 중복으로 보되 삭제하지 말고 duplicate flag 처리.
- normalized_item은 대표 정규화 정보로 유지하되, raw_item과 연결 테이블 또는 group_id로 관계를 남겨라.

원인이 cleanup/delete라면:
- raw_item과 normalized_item 삭제를 중단한다.
- 오래된 데이터는 삭제하지 말고 archived/post_expired flag 처리한다.

원인이 candidate 중복 생성이라면:
- candidate는 topic_group 또는 normalized_item 대표 후보 기준으로 1개만 생성한다.
- 같은 group에서 새 기사 발견 시 candidate를 새로 만들지 말고 related_source_count / duplicate_count / last_seen_at을 업데이트한다.

5. 중복 기사 그룹화

현재 관리자 목록에 중복 기사가 전부 row로 노출되어 운영이 어렵다.

수정:
- 중복/유사 기사들을 topic_group 또는 duplicate_group으로 묶는다.
- 관리자 목록은 기본적으로 대표 기사 1개만 보여준다.
- 대표 row에 중복 건수와 관련 출처 수를 표시한다.
- 상세보기에서 그룹 내부 기사 목록을 보여준다.

표시 항목:
- 대표 제목
- 대표 출처
- 대표 원문 URL
- 점수
- 게시 상태
- duplicate_count
- related_source_count
- group_item_count
- collected_at
- last_seen_at

상세보기:
- 대표 기사 원문
- Google News URL
- canonical/source URL
- 같은 URL 중복 목록
- 같은 제목 중복 목록
- 같은 주제 관련 기사 목록
- 각 기사 source_name, source_url, collected_at, status 표시

6. 관리자 목록 페이징/조회 개선

현재 소셜 뉴스 목록은 100건만 조회되는 것으로 보인다.
페이징이 있으므로 전체 데이터를 조회 가능해야 한다.

요구:
- total_count 정확히 조회
- page / size 기반 서버사이드 페이징
- 기본 size는 50 또는 100
- 전체 페이지 이동 가능
- 대표 기사만 보기 기본값
- 중복 포함 보기 옵션 제공
- 상태별 필터 제공
- source_name / title / similarity_key 검색 제공

7. 후보군 생성 정규화

게시 후보가 없다고 나오는 원인을 줄이기 위해 candidate 상태 흐름을 정규화한다.

- raw_item 수집
- normalized_item 생성/연결
- topic_group 생성/연결
- representative candidate 생성 또는 업데이트
- score 계산
- publish_status 결정

중요:
- 중복 기사는 삭제하지 않는다.
- 중복이라고 candidate를 무한 생성하지 않는다.
- 중복/관련 출처 수는 importance signal로 사용한다.
- 대표 후보 1개만 READY_TO_PUBLISH가 될 수 있다.

8. 작업 완료 후 알려줄 것

- raw_item / normalized_item 39건 고정 원인
- candidate만 증가한 원인
- 수정한 파일 목록
- 변경된 데이터 생명주기
- 추가/변경한 DB 필드
- 중복 그룹화 기준
- 관리자 목록 변경 사항
- 검증 SQL

DUPLICATE가 807건인데 대표 후보가 거의 없다.
중복 제거는 데이터를 죽이는 로직이 아니라 그룹화 로직이어야 한다.

각 duplicate_group/topic_group마다:
- 대표 후보 1개를 반드시 생성/유지
- 대표 후보는 DUPLICATE가 아니라 READY_TO_PUBLISH 또는 NORMALIZED/SCORED 상태
- 나머지만 DUPLICATE로 둔다
- DUPLICATE row는 representative_candidate_id를 참조
- 대표 후보 점수를 그룹 전체 점수로 화면에 표시

현재 DUPLICATE 807건을 대상으로 backfill해서 group별 대표 후보를 생성하고 재채점해줘.