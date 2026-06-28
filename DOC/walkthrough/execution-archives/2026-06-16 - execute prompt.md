### WorkConnect Harness Task ###

작업 대상:
C:\WORK\foreign_worker_job_info

반드시 먼저 읽을 문서:
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md 또는 07_WORK_AREA_REGISTRY.md
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/03_SYSTEM_ARCHITECTURE.md
- DOC/database/03_CONTENT_CURRENT.md
- DOC/database/11_TO_BE_CONTENT_FLOW.md 또는 관련 to-be content flow 문서
- DOC/flowchart/flowchart-flow-audit.md
- DOC/walkthrough 최신 문서

AREA:
CONTENT_QUEUE / SOCIAL_NEWS_CANDIDATE / DATA_SOURCE_QUALITY

MODE:
READ_ONLY_AUDIT

FOCUS:
Content Review 후보에서 반복 발생하는 중복 콘텐츠를 분석하고, 뉴스형 중복과 공지/생활/출입국/직업/채용정보형 중복을 분리하는 정책을 설계한다.

TIMEBOX:
60m

문제 배경:
Telegram Content Review 알림에 동일하거나 유사한 콘텐츠가 짧은 주기로 반복 발생한다.

예:
- 동일 고용노동부 공지 ID / 동일 링크 / 동일 제목이 오전과 오후에 반복 발송됨
- 동일 Travel And Tour World 링크가 여러 content ID로 반복됨
- 공지형 콘텐츠는 같은 출처/같은 URL 반복을 매번 후보/알림으로 남길 필요가 없음
- 단, 출처가 다른 같은 주제는 duplicate signal/source spread로 의미가 있을 수 있음

핵심 판단:
뉴스형 중복과 공지/정보형 중복은 동일하게 처리하면 안 된다.

분류해야 할 중복 유형:
1. exact duplicate
   - same source_domain
   - same canonical_url or source_url
   - same title
   - same source_name
   - same content hash

2. silent duplicate
   - 이미 동일 후보가 존재하고 상태/점수/내용 변화가 없음
   - content_candidate 새로 만들 필요 없음
   - Telegram review 다시 보낼 필요 없음
   - 기존 row의 seen_count / last_seen_at 정도만 의미 있음

3. duplicate signal
   - 같은 주제이지만 다른 출처
   - 다른 source_name / different canonical_url
   - topic spread signal로 의미 있음
   - 대표 content candidate에 source_spread_count 또는 duplicate_signal로 반영 가능

4. update duplicate
   - 같은 canonical_url이지만 title/body/updated_at/content_hash가 바뀜
   - 기존 candidate 업데이트 또는 review_required_updated 필요

확인할 것:
- 현재 content candidate 생성 시 unique/dedupe 기준이 무엇인지
- raw_ref_table/raw_ref_id 기준 중복 방지가 있는지
- source_url/canonical_url/title_hash/similarity_key가 활용되는지
- 같은 source_url이 여러 content_candidate로 생성되는지
- 같은 content_candidate가 Telegram Review로 여러 번 발송되는지
- review_sent_at, telegram_review_key, seen_count, last_seen_at 같은 개념이 있는지
- 뉴스형과 공지/정보형이 같은 duplicate policy를 쓰는지
- content_type/source_domain별 중복 정책 분기가 가능한지

도메인별 권장 정책을 문서화하라.

NEWS_ARTICLE:
- 중복 row는 일부 보관 가능
- 다른 출처 중복은 topic spread signal
- representative candidate 1개만 content candidate/publish 후보
- Telegram duplicate review는 보내지 않음

IMMIGRATION_NOTICE / GOVERNMENT_NOTICE:
- same URL / same official notice exact duplicate는 silent suppress
- 같은 주제 다른 공식 출처는 duplicate signal
- 의미 있는 업데이트만 review 재발송

LIVING_GUIDE:
- same URL duplicate는 suppress
- generic travel/crypto/lifestyle low relevance는 Telegram review 대상에서 제외 후보
- 같은 주제 다른 신뢰 출처는 signal

OCCUPATION_INFO:
- same occupation_code는 update only
- enrichment 전에는 publish 후보 아님
- duplicate Telegram review 금지

EMPLOYMENT_JOB:
- same source_job_id or canonical_url은 update only
- deadline/status/employer meaningful change만 notify

산출물:
DOC/walkthrough/YYYY-MM-DD-content-dedupe-policy-audit.md 작성

포함 내용:
- 현재 중복 생성/알림 흐름 요약
- exact duplicate / silent duplicate / duplicate signal / update duplicate 정의
- 도메인별 중복 정책
- 현재 코드/DB에서 부족한 필드
- 필요한 candidate key / telegram_review_key 제안
- suppress 가능한 Telegram 반복 사례
- CODE_TASK_CANDIDATE 목록

CODE_TASK_CANDIDATE 형식:
CODE_TASK_CANDIDATE
AREA:
MODE:
FOCUS:
WHY:
RISK:
PROTECTED AREA:
FILES LIKELY INVOLVED:
RECOMMENDED NEXT PROMPT:

금지:
- 코드 수정 금지
- DB 변경 금지
- migration 실행 금지
- Telegram notifier 수정 금지
- Facebook publisher 수정 금지
- scheduler 변경 금지
- content publisher selection 변경 금지
- raw token/env 수정 금지

검증:
- git status 확인
- 코드 변경 없음 확인
- walkthrough 작성 확인
- commit/push는 문서 변경만 있을 때 조건부 수행

Commit message 권장:
docs: audit content duplicate policy

### WorkConnect Harness Task ###

작업 대상:
C:\WORK\foreign_worker_job_info

반드시 먼저 읽을 문서:
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md 또는 07_WORK_AREA_REGISTRY.md
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
- DOC/walkthrough/YYYY-MM-DD-content-dedupe-policy-audit.md
- DOC/walkthrough 최신 문서

AREA:
TELEGRAM_REPORTING / CONTENT_QUEUE

MODE:
GUARDED_FIX

FOCUS:
Content Review Telegram 알림에서 동일 후보/동일 링크/동일 상태 반복 발송을 억제하고, 의미 있는 상태 변화 또는 새 대표 후보일 때만 Review 알림을 보내도록 한다.

TIMEBOX:
60m

문제 배경:
Content Review 알림이 짧은 주기로 반복 발생한다.
공지형 콘텐츠는 같은 source_url/canonical_url/title/status/score가 반복될 때 매번 Telegram에 보낼 필요가 없다.
다만 출처가 다른 같은 주제는 duplicate signal로 내부적으로 보관할 수 있다.

목표:
Telegram Review는 “새로운 운영 판단이 필요한 경우”에만 발송한다.

발송해야 하는 경우:
- new representative content_candidate created
- status changed to READY_TO_REVIEW / READY_TO_PUBLISH
- review_required reason changed
- score crossed important threshold bucket
- source content was meaningfully updated
- duplicate signal source_count crossed threshold
- publish/token/protected error occurred

발송하지 말아야 하는 경우:
- same source_url/canonical_url already sent
- same content_candidate_id + same status + same score bucket + same message hash
- low-score repeated content
- exact duplicate official notice
- same Travel/RSS/general lifestyle low relevance item repeated
- same content already review_sent_at exists and no meaningful update

권장 dedupe key:
telegram_review_key =
content_candidate_id + status + score_bucket + message_hash

또는 content_candidate_id가 중복 생성되는 문제가 있으면:
telegram_review_key =
source_domain + content_type + canonical_url + status + score_bucket + message_hash

score_bucket 예:
- 0-39
- 40-59
- 60-79
- 80-100

구현 방향:
1. Telegram review 발송 직전 dedupe check 추가
2. 이미 같은 telegram_review_key가 sent 상태이면 발송 suppress
3. suppress 시 Telegram은 보내지 말고 operation log 또는 content log에만 기록
4. 기존 candidate에는 가능하면 review_sent_at / last_review_key / review_sent_count / last_suppressed_at 같은 필드를 사용
5. DB migration이 부담되면 우선 기존 log table 또는 JSON payload를 활용
6. destructive migration 금지
7. bulk update/delete 금지

상태/로그 권장:
- REVIEW_SENT
- REVIEW_SUPPRESSED_DUPLICATE
- REVIEW_SUPPRESSED_LOW_VALUE
- DUPLICATE_SILENT
- DUPLICATE_SIGNAL_UPDATED

주의:
이번 작업은 Telegram Review 중복 억제다.
Facebook publish path를 변경하지 않는다.
Content publish selection을 변경하지 않는다.
Scheduler interval을 변경하지 않는다.
Auth/token 영역을 변경하지 않는다.

수정 허용:
- Telegram review formatter/notifier의 dedupe check
- content review notification service
- repository read-only query or non-destructive update
- operation log 기록
- walkthrough 문서
- 단위 테스트 또는 dry-run 테스트

수정 금지:
- FacebookPublisher
- Facebook token validation
- scheduler/cooldown/daily cap
- admin auth
- content candidate scoring 대규모 변경
- DB destructive migration
- raw token/env

검증:
- 같은 candidate_id/status/message_hash 반복 시 Telegram 발송 suppress
- 다른 status로 바뀌면 발송
- score bucket이 바뀌면 발송 가능
- source content_hash가 바뀌면 발송 가능
- suppressed duplicate는 Telegram으로 보내지 않음
- operation log에는 suppress reason이 남음
- 기존 auto publish / Facebook publish 동작에 영향 없음

가능하면 테스트 케이스:
1. same content review twice -> second suppressed
2. same candidate but status changed -> sent
3. same canonical_url but different source_name -> duplicate signal, no spam
4. low-score repeated living guide -> suppressed
5. publish failure notification -> not suppressed by review dedupe

Walkthrough:
DOC/walkthrough/YYYY-MM-DD-telegram-review-dedupe.md 작성

포함 내용:
- 변경 이유
- dedupe key
- 발송 조건
- suppress 조건
- 수정 파일
- 테스트 결과
- 보호 영역 미수정 확인
- 남은 TODO

Commit/push:
검증 통과 시만 commit/push.

Commit message 권장:
fix: suppress duplicate content review telegram alerts

### WorkConnect Harness Task ###

작업 대상:
C:\WORK\foreign_worker_job_info

반드시 먼저 읽을 문서:
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md 또는 DOC/architecture/07_WORK_AREA_REGISTRY.md
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/03_SYSTEM_ARCHITECTURE.md
- DOC/database/03_CONTENT_CURRENT.md
- DOC/database/11_TO_BE_CONTENT_FLOW.md 또는 content flow 관련 최신 DB 문서
- DOC/flowchart/flowchart-flow-audit.md
- DOC/walkthrough 최신 문서

AREA:
CONTENT_QUEUE / SOCIAL_NEWS_CANDIDATE / DATA_SOURCE_QUALITY

MODE:
READ_ONLY_AUDIT

FOCUS:
Content Review 후보에서 반복 발생하는 중복 콘텐츠를 분석하고, 뉴스형 중복과 공지/생활/출입국/직업/채용정보형 중복을 분리하는 정책을 설계한다.

TIMEBOX:
60m

문제 배경:
Telegram Content Review 알림에 동일하거나 유사한 콘텐츠가 짧은 주기로 반복 발생한다.

관찰된 사례:
- 동일 고용노동부 공지 링크가 시간차를 두고 다시 Content Review 알림으로 발송됨
- 동일 Travel And Tour World 링크가 여러 content ID로 반복됨
- 공지형 콘텐츠는 같은 출처/같은 URL 반복을 매번 후보/알림으로 남길 필요가 없음
- 단, 출처가 다른 같은 주제는 duplicate signal/source spread로 의미가 있을 수 있음

핵심 판단:
뉴스형 중복과 공지/정보형 중복은 동일하게 처리하면 안 된다.

중복 유형을 아래처럼 분리해서 현재 코드/DB가 이를 구분할 수 있는지 확인하라.

1. exact duplicate
- same source_domain
- same canonical_url or source_url
- same title
- same source_name
- same content hash

2. silent duplicate
- 이미 동일 후보가 존재하고 상태/점수/내용 변화가 없음
- content_candidate 새로 만들 필요 없음
- Telegram review 다시 보낼 필요 없음
- 기존 row의 seen_count / last_seen_at 정도만 의미 있음

3. duplicate signal
- 같은 주제이지만 다른 출처
- different source_name or different canonical_url
- topic spread signal로 의미 있음
- 대표 content candidate에 source_spread_count 또는 duplicate_signal로 반영 가능

4. update duplicate
- 같은 canonical_url이지만 title/body/updated_at/content_hash가 바뀜
- 기존 candidate 업데이트 또는 REVIEW_REQUIRED_UPDATED 필요

확인할 것:
- 현재 content candidate 생성 시 unique/dedupe 기준이 무엇인지
- raw_ref_table/raw_ref_id 기준 중복 방지가 있는지
- source_url/canonical_url/title_hash/similarity_key가 활용되는지
- 같은 source_url이 여러 content_candidate로 생성되는지
- 같은 content_candidate가 Telegram Review로 여러 번 발송되는지
- review_sent_at, telegram_review_key, seen_count, last_seen_at 같은 개념이 있는지
- 뉴스형과 공지/정보형이 같은 duplicate policy를 쓰는지
- content_type/source_domain별 중복 정책 분기가 가능한지
- score가 낮은 LIVING_INFO, generic travel, crypto, general lifestyle 콘텐츠가 왜 Review 알림으로 올라오는지

도메인별 권장 정책을 문서화하라.

NEWS_ARTICLE:
- 중복 row는 일부 보관 가능
- 다른 출처 중복은 topic spread signal
- representative candidate 1개만 content candidate/publish 후보
- Telegram duplicate review는 보내지 않음

IMMIGRATION_NOTICE / GOVERNMENT_NOTICE:
- same URL / same official notice exact duplicate는 silent suppress
- 같은 주제 다른 공식 출처는 duplicate signal
- 의미 있는 업데이트만 review 재발송

LIVING_GUIDE:
- same URL duplicate는 suppress
- generic travel/crypto/lifestyle low relevance는 Telegram review 대상에서 제외 후보
- 같은 주제 다른 신뢰 출처는 signal

OCCUPATION_INFO:
- same occupation_code는 update only
- enrichment 전에는 publish 후보 아님
- duplicate Telegram review 금지

EMPLOYMENT_JOB:
- same source_job_id or canonical_url은 update only
- deadline/status/employer meaningful change만 notify

산출물:
DOC/walkthrough/YYYY-MM-DD-content-dedupe-policy-audit.md 작성

포함 내용:
- 현재 중복 생성/알림 흐름 요약
- exact duplicate / silent duplicate / duplicate signal / update duplicate 정의
- 도메인별 중복 정책
- 현재 코드/DB에서 부족한 필드
- 필요한 candidate key / telegram_review_key 제안
- suppress 가능한 Telegram 반복 사례
- low-score review 대상 제외 기준
- CODE_TASK_CANDIDATE 목록

CODE_TASK_CANDIDATE 형식:
CODE_TASK_CANDIDATE
AREA:
MODE:
FOCUS:
WHY:
RISK:
PROTECTED AREA:
FILES LIKELY INVOLVED:
RECOMMENDED NEXT PROMPT:

금지:
- 코드 수정 금지
- DB 변경 금지
- migration 실행 금지
- Telegram notifier 수정 금지
- Facebook publisher 수정 금지
- scheduler 변경 금지
- content publisher selection 변경 금지
- raw token/env 수정 금지

검증:
- git status 확인
- 코드 변경 없음 확인
- walkthrough 작성 확인
- commit/push는 문서 변경만 있을 때 조건부 수행

Commit message 권장:
docs: audit content duplicate policy

### WorkConnect Harness Task ###

작업 대상:
C:\WORK\foreign_worker_job_info

반드시 먼저 읽을 문서:
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md 또는 DOC/architecture/07_WORK_AREA_REGISTRY.md
- DOC/architecture/00_PRODUCT_NORTH_STAR.md 또는 실제 존재하는 North Star 문서
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/03_SYSTEM_ARCHITECTURE.md
- DOC/flowchart/flowchart-flow-audit.md
- DOC/walkthrough 최신 문서

AREA:
SOCIAL_NEWS_CANDIDATE / CONTENT_QUEUE / DATA_SOURCE_QUALITY

MODE:
GUARDED_FIX

FOCUS:
WorkConnect Korea 현재 운영 단계에서 일본/미국/발리/일반 해외 이민정책/일반 여행/일반 경제/일반 정치 콘텐츠가 Content Review 또는 게시 후보로 올라오지 않도록 제외 필터와 품질 게이트를 강화한다.

TIMEBOX:
60m

문제 배경:
WorkConnect의 장기 비전은 “타국에 정착하거나 일하러 간 사람들을 위한 정보 플랫폼”이지만, 현재 운영 채널은 WorkConnect Korea이고 현재 콘텐츠 우선순위는 한국에서 일하고 살고 정착하려는 외국인이다.

최근 Content Review에 아래와 같은 부적합 후보가 올라왔다.

예:
- Japan’s “Foreigner Policy” Skirts Key Issues: No Orderly Coexistence Without Plan for Immigration
  - source: nippon.com
  - link: 없음
  - score: 0.0
  - Korea 직접 관련 없음
  - 현재 WorkConnect Korea 피드에 부적합

- Travel Confidence Tested as Bali Authorities Counter South Korea Warning...
  - 발리 여행 안전/관광 기사
  - 한국 생활/취업/정착과 직접 관련 낮음
  - 동일 링크 반복 Review 대상 부적합

- Crypto in South Korea: The Ultimate Guide
  - 일반 crypto guide
  - 외국인 생활/취업/정착 핵심 정보 아님
  - 낮은 점수면 Review 대상 제외 필요

- 한국 국내 선거/정치/증시/일반 경제 기사
  - target country relevance는 있을 수 있으나 WorkConnect relevance가 낮음
  - 외국인의 일/비자/생활/정착/지원 행동에 직접 연결되지 않으면 제외

핵심 원칙:
A country-related article is not automatically WorkConnect-relevant.
The item must help someone work, live, study, immigrate, settle, or access support in the target country.

현재 단계의 target country:
Korea

현재 단계의 primary audience:
foreigners who work, live, study, immigrate, or settle in Korea.

목표:
한국 직접 관련성이 낮거나, 외국인의 실질 행동/판단에 도움이 되지 않는 콘텐츠가 Content Review/Telegram/Facebook 후보로 올라오지 않게 한다.

수정 범위:
- candidate quality gate
- content promotion gate
- review eligibility gate
- low relevance suppression
- system message / missing link blocking
- domain/category penalty
- walkthrough 문서

수정 금지:
- FacebookPublisher
- Facebook token validation
- scheduler interval
- bot ON/OFF state
- admin auth
- DB destructive migration
- raw token/env
- 실제 외부 API 호출
- Facebook publish payload 변경

1. Quick Pre-Review 먼저 수행

코드 수정 전에 아래를 확인하라.

- 현재 candidate/content promotion 기준
- country relevance 계산 위치
- Korea relevance 계산 위치
- foreign_worker_relevance/user_need/actionability 개념 유무
- Content Review Telegram 발송 기준
- score가 0 또는 낮은 후보가 Review로 올라오는 이유
- Link가 "-" 또는 empty인데 Review로 올라오는 이유
- source_domain/content_type/category별 필터 위치
- LIVING_INFO가 너무 넓게 잡히는지
- global reference / Japan / US / Bali / travel / crypto / politics / stock market 필터가 있는지

Pre-review decision:
- SAFE_TO_PROCEED
- PROCEED_WITH_LIMITS
- STOP_REQUIRES_USER_REVIEW

STOP 조건:
- FacebookPublisher를 수정해야만 해결 가능할 때
- scheduler를 수정해야만 해결 가능할 때
- admin auth/token 영역을 건드려야 할 때
- DB destructive migration이 필요할 때
- candidate selection 전체를 대규모 재작성해야 할 때

2. 제외 필터 기준

아래 조건은 기본적으로 Content Review/Auto Publish 후보에서 제외하거나 강하게 낮춰라.

Hard block 후보:

A. 링크 없음
- link_url is null
- link_url = "-"
- source_url empty
- canonical_url empty
- publishable_link_url missing

처리:
BLOCKED_SOURCE_INVALID 또는 CONTENT_INVALID_LINK
Telegram Review 발송 금지

B. 현재 target country와 직접 관련 없음
- Japan-only immigration policy
- US-only immigration/labor policy
- Bali/travel safety story
- other-country domestic policy

단, 비교 분석용으로 별도 GLOBAL_REFERENCE 저장은 가능하지만 현재 WorkConnect Korea Content Review에는 올리지 않는다.

처리:
GLOBAL_REFERENCE_ONLY
NO_TELEGRAM_REVIEW
NO_AUTO_PUBLISH

C. 일반 여행/관광
- travel confidence
- tourism promotion
- destination safety
- airline/tourism market
- generic travel guide

한국 생활/정착 실용 정보로 연결되지 않으면 제외.

D. 일반 crypto/투자/금융상품
- crypto guide
- stock market milestone
- generic investment article

외국인 생활 필수 금융 정보가 아니면 제외.
예외:
- foreigner bank account
- remittance
- tax
- national pension
- health insurance payment
- wage payment

E. 국내 정치/선거/정당/대통령 지지율
한국 관련성은 있어도 WorkConnect relevance 낮음.
비자/노동/외국인 정책 직접 영향이 없으면 제외.

F. 시스템 메시지 또는 본문 결손
아래 문구가 title/summary/body/why-it-matters/Facebook message에 포함되면 public content 후보 금지.

예:
- 저장된 기사 본문이 없습니다.
- 일부 RSS/검색 결과는 원문 HTML 접근이 제한될 수 있습니다.
- No article body was saved.
- Content unavailable.
- Failed to fetch article.
- Parser error.
- Access denied.
- 관리자 재게시 요청
- 게시 기준
- 현재 점수
- READY_TO_PUBLISH
- candidate
- queue
- threshold
- publish_status

처리:
CONTENT_MISSING or CONTENT_INVALID_SYSTEM_TEXT
Telegram Review 발송 금지 또는 admin diagnostics only

3. Penalty 기준

Hard block까지는 아니지만 낮은 우선순위로 내려야 하는 항목:

- general economy without foreign resident actionability
- generic public campaign unrelated to foreigners
- disability/employment campaign not targeted to foreigners
- company PR without practical user action
- government meeting announcement without outcome
- event/award ceremony
- public partnership MOU
- general safety inspection not applicable to foreign residents

예:
고용노동부 공지라도 제목이 “시상식 개최”, “MOU 체결”, “회의 개최”, “캠페인”이면 자동 Review/Publish 후보로 올리지 말고 LOW_USER_NEED 또는 WATCH_TOPIC 처리.

4. Watch Topic 처리

완전히 버리면 안 되는 주제는 WATCH_TOPIC으로 남겨라.

예:
- 최저임금위원회 회의 개최
  - 지금은 게시 가치 낮음
  - 최저임금 결정/변경 발표 시 콘텐츠화 가치 높음
  - WATCH_TOPIC: MINIMUM_WAGE_2026

- 외국인 정책 관련 해외 사례
  - 현재 Korea 피드에는 부적합
  - GLOBAL_REFERENCE로 저장 가능
  - 추후 국가 확장/비교 콘텐츠 후보

5. Review Eligibility Gate

Telegram Content Review로 보내기 전에 review eligibility를 확인하라.

Review로 보낼 수 있는 조건:
- valid link exists
- source trace exists
- target_country = Korea or DIRECT_KOREA/KOREA_RELATED
- user_need_score above threshold
- actionability or repeatability exists
- content is not just title repetition
- not generic politics/economy/travel/crypto
- not system-message contaminated
- not exact duplicate already reviewed

Review로 보내면 안 되는 조건:
- score = 0
- link missing
- global reference only
- low user need
- exact duplicate
- generic travel/crypto/politics/economy
- title-only content
- source body missing with no useful summary

6. 권장 상태값 또는 reason

기존 상태 체계를 깨지 말고, 가능한 범위에서 reason/category로 남겨라.

권장 reason:
- BLOCKED_SOURCE_INVALID
- BLOCKED_TARGET_COUNTRY_MISMATCH
- BLOCKED_GLOBAL_REFERENCE_ONLY
- BLOCKED_LOW_USER_NEED
- BLOCKED_GENERIC_TRAVEL
- BLOCKED_GENERIC_CRYPTO
- BLOCKED_DOMESTIC_POLITICS
- BLOCKED_GENERIC_ECONOMY
- BLOCKED_CONTENT_MISSING
- BLOCKED_SYSTEM_TEXT
- WATCH_TOPIC_ONLY
- REVIEW_ELIGIBLE
- REVIEW_SUPPRESSED_LOW_VALUE

DB migration이 필요하면 destructive migration 금지.
컬럼 추가가 부담되면 기존 JSON payload, reason field, log field를 활용하라.

7. 검증 샘플

아래 샘플이 기대대로 처리되는지 dry-run 또는 unit-level 검증하라.

A. Japan foreigner policy, link missing
Expected:
BLOCKED_SOURCE_INVALID or GLOBAL_REFERENCE_ONLY
No Telegram Review
No Auto Publish

B. Bali travel safety story
Expected:
BLOCKED_GENERIC_TRAVEL or LOW_USER_NEED
No Telegram Review unless explicitly Korea settlement related

C. Crypto in South Korea generic guide, low score
Expected:
BLOCKED_GENERIC_CRYPTO or LOW_USER_NEED
No Telegram Review

D. Korean local election/governance article
Expected:
BLOCKED_DOMESTIC_POLITICS
No Telegram Review

E. Minimum wage committee meeting announcement
Expected:
WATCH_TOPIC_ONLY
No immediate Review unless outcome/actionable change exists

F. Actual foreign worker rights notice
Expected:
REVIEW_ELIGIBLE or READY_TO_REVIEW

G. HiKorea visa manual / official medical institution lookup / immigration agency lookup
Expected:
REVIEW_ELIGIBLE, because these are repeatable official utility items

8. 산출물

수정이 가능하면 코드 변경 후 아래 walkthrough 작성:

DOC/walkthrough/YYYY-MM-DD-content-exclusion-filter-hardening.md

포함 내용:
- 어떤 필터를 추가/강화했는지
- hard block 기준
- penalty 기준
- watch topic 기준
- review eligibility 기준
- 검증 샘플 결과
- 수정 파일
- 보호 영역 미수정 확인
- 남은 TODO

만약 코드 변경이 위험하면 STOP_REPORT 작성:

DOC/walkthrough/YYYY-MM-DD-stop-report-content-exclusion-filter.md

9. 테스트/검증

가능하면 아래를 수행:
- 관련 Python 파일 py_compile
- 가능한 경우 unit/dry-run 테스트
- sample classification 테스트
- git diff 확인
- raw token/env가 diff에 없는지 확인
- Facebook/scheduler/auth 파일이 수정되지 않았는지 확인

10. Commit / Push

검증 통과 시에만 commit/push.

권장 commit message:
fix: harden content exclusion filters for low-relevance items

문서만 수정했다면:
docs: define content exclusion filter policy

### WorkConnect Harness Task ###

작업 대상:
C:\WORK\foreign_worker_job_info

반드시 먼저 읽을 문서:
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md 또는 DOC/architecture/07_WORK_AREA_REGISTRY.md
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/03_SYSTEM_ARCHITECTURE.md
- DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
- DOC/flowchart/flowchart-flow-audit.md
- DOC/walkthrough 최신 문서

AREA:
CONTENT_QUEUE / TELEGRAM_REPORTING / DATA_SOURCE_QUALITY

MODE:
GUARDED_FIX

FOCUS:
기사 링크형 콘텐츠가 아닌 순수 정보형 콘텐츠 또는 OG 이미지가 약한 정보형 콘텐츠에 대해 WorkConnect 1080x1080 PNG 템플릿에 영어 텍스트를 오버레이하고, Telegram Content Review에 완성된 preview 이미지 형태로 전송하도록 한다.

TIMEBOX:
60m

문제 배경:
WorkConnect 콘텐츠는 앞으로 아래처럼 분기한다.

1. 기사/공지 링크형 콘텐츠
- 원문 link_url이 있고 OG preview가 정상인 경우
- Facebook message + link 분리
- 이미지 자동 검색/생성 금지
- 원문 OG 이미지 사용

2. 순수 정보성 텍스트 / 자체 정리 정보 / OG가 약한 생활정보
- WorkConnect 자체 1080x1080 템플릿 PNG 사용
- 템플릿의 하얀 공간에 텍스트 오버레이
- Telegram Review에는 완성된 이미지 preview를 보냄
- 실제 Facebook 게시 전에는 관리자 확인 가능해야 함

3. 본문 불완전 / 출처 불명확 / 법적 민감 정보
- 자동 이미지 생성 금지
- REVIEW_REQUIRED 또는 CONTENT_INVALID 처리

현재 템플릿 파일은 카테고리별로 준비되어 있다.
파일명과 카테고리를 맞춰 사용하라.

예상 템플릿 파일: 위치: SRC/foreign_worker_life_info_collector/assets/
- checklist howto template.png
- livin in korea template.png
- visa immigration template.png
- work labor right template.png
- alert review template.png

실제 프로젝트 내 저장 위치를 확인하고, 없으면 DOC 또는 static asset 경로에 복사/등록하는 방안을 보고하라.
임시 업로드 경로가 아니라 프로젝트 내 버전관리 가능한 static/template 경로로 관리해야 한다.
단, 경로 이동이 위험하면 TODO로 남긴다.

권장 최종 저장 위치 예:
SRC/foreign_worker_life_info_collector/assets/templates/content_cards/
또는
SRC/foreign_worker_life_info_collector/admin_ui/public/templates/content_cards/

단, 실제 서비스에서 Python backend가 이미지를 생성해야 한다면 backend에서 접근 가능한 assets 경로를 우선한다.

템플릿 매핑:
- VISA / IMMIGRATION UPDATE
  → visa immigration template.png
  → IMMIGRATION_INFO, VISA_INFO, IMMIGRATION_NOTICE, GOVERNMENT_NOTICE, visa_policy

- WORK / LABOR RIGHTS
  → work labor right template.png
  → labor_rights, minimum_wage, employment_policy, work_contract, industrial_accident, wage, workplace_safety

- LIVING IN KOREA
  → livin in korea template.png
  → living_info, housing, banking, healthcare, insurance, transportation, telecom, local_support

- CHECKLIST / HOW TO
  → checklist howto template.png
  → checklist, how_to, required_documents, step_by_step, preparation, application_steps

- ALERT / REVIEW REQUIRED
  → alert review template.png
  → sensitive, review_required, source_limited, legal_caution, policy_may_change, content_incomplete

기본 규칙:
- 텍스트는 반드시 영어만 사용한다.
- 한글 텍스트를 카드 이미지에 넣지 않는다.
- title/source/date 제외 모든 public-facing text는 영어여야 한다.
- 원문 제목이 한글이면 카드용 영어 제목을 생성/사용한다.
- 한글이 감지되면 CARD_TEXT_INVALID_LANGUAGE 또는 REVIEW_REQUIRED_TRANSLATION 처리한다.
- 시스템 메시지/운영 문구를 절대 카드에 넣지 않는다.

금지 텍스트:
- 저장된 기사 본문이 없습니다.
- 일부 RSS/검색 결과는 원문 HTML 접근이 제한될 수 있습니다.
- 관리자 재게시 요청
- 게시 기준
- 현재 점수
- READY_TO_PUBLISH
- candidate
- queue
- threshold
- publish_status
- Facebook 게시를 시도
- 즉시 Facebook

카드 텍스트 payload 구조:
content_card_payload = {
  "template_type": "LIVING_IN_KOREA",
  "title": "...",
  "subtitle": "...",
  "bullets": ["...", "...", "..."],
  "source": "...",
  "date": "YYYY-MM-DD",
  "footer_url": "https://www.facebook.com/profile.php?id=61581518066485"
}

footer_url:
현재 기본값은 아래 Facebook 페이지 주소를 사용한다.
https://www.facebook.com/profile.php?id=61581518066485

나중에 공식 웹사이트가 생기면 footer_url을 website URL로 변경할 수 있도록 config화한다.

날짜 표기:
카드 내부 날짜는 YYYY-MM-DD 형식을 사용한다.
운영 로그/Telegram 시간은 YYYY-MM-DD HH24:MI:SS KST 형식을 사용한다.

오버레이 좌표:
템플릿별 정확한 x/y 좌표는 이미지 크기 1080x1080 기준으로 설정한다.
하얀 영역을 침범하지 않도록 좌표와 최대 너비를 지정한다.

공통 권장 좌표:
- category badge text:
  x=700, y=75, max_width=300, font_size=34

- title:
  x=180, y=220, max_width=720, max_height=210, font_size=54, max_lines=2 또는 3

- subtitle:
  x=180, y=390, max_width=720, max_height=120, font_size=30, max_lines=3

- bullet 1:
  x=180, y=590, max_width=760, font_size=30

- bullet 2:
  x=180, y=705, max_width=760, font_size=30

- bullet 3:
  x=180, y=820, max_width=760, font_size=30

- footer source:
  x=150, y=1000, max_width=380, font_size=22

- footer date:
  x=650, y=1000, max_width=260, font_size=22

- footer url:
  x=150, y=1030, max_width=760, font_size=18

단, 각 템플릿의 실제 빈 공간이 다르므로 이미지별로 좌표를 보정할 수 있게 JSON 설정 파일로 분리하라.

권장 설정 파일:
content_card_templates.json

예:
{
  "LIVING_IN_KOREA": {
    "template_file": "livin in korea template.png",
    "category_label": "LIVING IN KOREA",
    "positions": {
      "title": {"x": 190, "y": 230, "max_width": 700, "font_size": 54, "max_lines": 3},
      "subtitle": {"x": 190, "y": 410, "max_width": 700, "font_size": 30, "max_lines": 3},
      "bullets": [
        {"x": 180, "y": 660, "max_width": 230, "font_size": 25, "max_lines": 5},
        {"x": 455, "y": 660, "max_width": 230, "font_size": 25, "max_lines": 5},
        {"x": 730, "y": 660, "max_width": 230, "font_size": 25, "max_lines": 5}
      ],
      "source": {"x": 165, "y": 1005, "max_width": 380, "font_size": 22},
      "date": {"x": 670, "y": 1005, "max_width": 260, "font_size": 22}
    }
  }
}

텍스트 렌더링 규칙:
- 자동 줄바꿈 필요
- max_width 기준으로 wrap
- max_lines 초과 시 텍스트를 자르지 말고 card generation 실패 처리 또는 summary 재생성 필요 상태로 표시
- 폰트 크기를 무한정 줄이지 말 것
- 최소 font size는 22
- title은 2~3줄까지만 허용
- bullets는 3개 이하
- bullet 하나당 80자 이하 권장
- 글자 overflow 발생 시 CARD_TEXT_OVERFLOW로 처리

폰트:
- 시스템에 사용 가능한 안전한 Sans 폰트 사용
- Windows 환경이면 가능한 경우 Noto Sans, Arial, Segoe UI 사용
- 한글 렌더링 목적이 아니므로 영어 가독성을 우선
- 폰트 파일을 repo에 커밋하지 말 것

카드 생성 대상:
다음 조건을 만족하는 content candidate만 카드 preview 생성 대상이다.

- content_format in CARD_IMAGE / CHECKLIST_CARD / SHORT_CARD / GUIDE_CARD
또는
- asset_policy = USE_WORKCONNECT_TEMPLATE
또는
- link_url이 없지만 source-backed structured info인 경우
또는
- OG preview를 쓰기 어려운 정보형 텍스트

다음 조건은 카드 생성 금지:
- link_url exists and OG preview is valid and content_type is NEWS_ARTICLE
- source_url/link_url missing and source evidence도 없음
- score = 0
- global reference only
- generic travel/crypto/politics/economy low relevance
- system-message contaminated
- Korean public text cannot be translated safely
- sensitive/legal content without review

Telegram Review 변경 목표:
기존에는 Telegram Content Review가 텍스트 preview만 보냈다.
이제 카드 생성 대상이면 Telegram에 완성된 1080x1080 preview 이미지를 함께 전송한다.

Telegram 메시지 구성:
- 텍스트 요약은 짧게
- 카드 이미지를 첨부
- 원문/source link가 있으면 같이 표시
- 실제 Facebook 게시로 이어지지 않는다는 운영 안내는 유지 가능
- 중복 review suppress 정책과 충돌하지 않아야 함

Telegram 메시지 예:
[Content Review]
ID: ...
Source: ...
Score: ...
Format: CARD_IMAGE
Template: LIVING_IN_KOREA
Link: ...

Preview image attached.

Check next:
- Confirm the source before publishing.
- Confirm whether this applies to work, visa, housing, healthcare, banking, or daily life.

주의:
Telegram에 raw token, secrets, full stack trace, large diff를 보내지 마라.

수정 허용:
- content card image generator module 추가
- template config JSON 추가
- Telegram review preview에 image attachment 추가
- card generation validation 추가
- walkthrough 문서 작성
- 작은 dry-run/sample generation script 추가

수정 금지:
- FacebookPublisher 수정
- Facebook 실제 게시 payload 변경
- scheduler 변경
- admin auth 변경
- token validation 변경
- DB destructive migration
- raw token/env 수정
- 자동 게시 selection logic 대규모 변경

테스트/검증:
- sample content payload로 5개 템플릿 중 최소 1개 PNG 생성
- 영어 텍스트만 들어가는지 확인
- 한글 포함 시 실패 또는 REVIEW_REQUIRED_TRANSLATION
- 텍스트 overflow 시 CARD_TEXT_OVERFLOW
- link형 NEWS_ARTICLE은 card generation 대상에서 제외되는지 확인
- Telegram image send가 dry-run 또는 mock 가능하면 테스트
- 실제 Telegram 발송은 환경변수/설정이 안전할 때만 수행
- py_compile 또는 해당 언어 compile/check 수행
- git diff에 토큰/secret이 없는지 확인

산출물:
DOC/walkthrough/YYYY-MM-DD-content-card-template-preview.md 작성

포함 내용:
- 구현 개요
- template mapping
- coordinate config
- text payload 구조
- image generation validation
- Telegram review 변경
- 테스트 결과
- 생성 샘플 경로
- 보호 영역 미수정 확인
- 남은 TODO

Commit / Push:
검증 통과 시만 commit/push.

권장 commit message:
feat: generate WorkConnect content card previews for Telegram review

중요:
이번 작업은 “정보형 콘텐츠의 Telegram Review preview를 카드 이미지로 보여주는 것”이다.
Facebook 실제 게시 로직은 변경하지 않는다.
기사 링크형 콘텐츠는 OG를 사용하고, WorkConnect 템플릿 카드는 정보형 콘텐츠에만 사용한다.

### WorkConnect Harness Task ###

작업 대상:
C:\WORK\foreign_worker_job_info

반드시 먼저 읽을 문서:
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/06_WORK_AREA_REGISTRY.md 또는 DOC/architecture/07_WORK_AREA_REGISTRY.md
- DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
- DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
- DOC/walkthrough 최신 문서

AREA:
CONTENT_QUEUE / DATA_SOURCE_QUALITY / LLAMA_STATUS

MODE:
GUARDED_FIX

FOCUS:
content text와 source link를 입력받아 로컬 LLaMA에게 WorkConnect card payload JSON을 생성하게 하고, 생성된 JSON을 기존 content card renderer util에 전달하여 1080x1080 preview PNG를 만드는 로컬 util을 구현한다.

TIMEBOX:
60m

현재 준비된 파일 구조:
assets/templates/content_cards/
- json_payloads/
  - alert_review.json
  - checklist_howto.json
  - living_in_korea.json
  - visa_immigration.json
  - work_labor_right.json
- alert review template.png
- checklist howto template.png
- content_card_templates.json
- livin in korea template.png
- visa immigration template.png
- work labor right template.png

목표 흐름:
1. 사용자가 content text와 source link를 입력한다.
2. util이 template_type을 명시적으로 받거나, category/source_domain을 기반으로 template_type을 선택한다.
3. util이 해당 template_type의 sample payload와 llama rule을 참조한다.
4. util이 로컬 LLaMA에 “JSON only”로 payload 생성을 요청한다.
5. LLaMA 응답 JSON을 validation한다.
6. validation 통과 시 content card renderer에 전달한다.
7. timestamp가 붙은 preview PNG를 생성한다.
8. 생성된 이미지 경로와 payload JSON을 출력한다.

이번 작업은 로컬 preview util이다.
Facebook 게시, Telegram 전송, scheduler, auth, token 영역을 수정하지 않는다.

수정 허용:
- 로컬 util 추가
- LLaMA prompt builder 추가
- card payload validation 추가
- sample payload / rule file 참조 로직 추가
- renderer util과 연결
- dry-run/sample script 추가
- walkthrough 작성

수정 금지:
- FacebookPublisher
- Facebook token validation
- scheduler
- admin auth
- DB destructive migration
- Telegram 실제 전송
- 자동 게시 selection logic
- raw token/env 수정
- 템플릿 PNG 파일 자체 수정

권장 모듈:
- SRC/foreign_worker_life_info_collector/content/card_payload_generator.py
- SRC/foreign_worker_life_info_collector/tools/generate_content_card_from_text.py

또는 기존 프로젝트 구조에 맞는 유사 위치를 사용한다.

CLI 예시:
python -m foreign_worker_life_info_collector.tools.generate_content_card_from_text ^
  --template LIVING_IN_KOREA ^
  --text "Foreign residents in Korea should keep their address, health insurance, and banking information updated." ^
  --source "WorkConnect Guide" ^
  --link "https://www.facebook.com/profile.php?id=61581518066485" ^
  --date "2026-06-16"

또는 input JSON 방식:
python -m foreign_worker_life_info_collector.tools.generate_content_card_from_text ^
  --input sample_input.json

input JSON 예:
{
  "template_type": "CHECKLIST_HOWTO",
  "content_text": "Health insurance status can affect clinic visits, visa renewals, and unpaid bills. Foreign residents should confirm payment status, keep receipts, and ask NHIS before deadlines.",
  "source": "NHIS",
  "link": "https://www.nhis.or.kr",
  "date": "2026-06-16"
}

LLaMA prompt 생성 규칙:
- 해당 template_type의 json_payloads sample을 example로 사용한다.
- 해당 template_type의 llama_rules를 사용한다.
- 출력은 JSON only.
- markdown 금지.
- 설명 문장 금지.
- code fence 금지.
- 영어만.
- template_type은 입력과 동일해야 한다.
- date는 YYYY-MM-DD.
- source는 입력 source를 우선 사용한다.
- footer_url은 "WorkConnect Korea"를 기본값으로 한다.
- bullets 개수는 template별 규칙을 따른다.
  - CHECKLIST_HOWTO: exactly 4 bullets
  - 나머지: exactly 3 bullets

JSON schema:
{
  "template_type": "...",
  "title": "...",
  "subtitle": "...",
  "bullets": ["...", "...", "..."],
  "source": "...",
  "date": "YYYY-MM-DD",
  "footer_url": "WorkConnect Korea"
}

Validation:
- JSON parse 가능해야 함
- required fields 모두 있어야 함
- template_type이 허용값이어야 함
- title/subtitle/bullets/source/footer_url에 한글이 없어야 함
- forbidden system/operation messages가 없어야 함
- bullets 개수가 template rule과 맞아야 함
- title/subtitle/bullets overflow는 renderer validation에서 잡아야 함
- link가 없거나 source가 없으면 CARD_SOURCE_INVALID 또는 REVIEW_REQUIRED_SOURCE_LIMITED 처리
- LLaMA 응답이 invalid이면 raw response를 public field에 넣지 말고 error로 반환

금지 텍스트:
- 저장된 기사 본문이 없습니다.
- 일부 RSS/검색 결과는 원문 HTML 접근이 제한될 수 있습니다.
- 관리자 재게시 요청
- 게시 기준
- 현재 점수
- READY_TO_PUBLISH
- candidate
- queue
- threshold
- publish_status
- Facebook 게시를 시도
- 즉시 Facebook

Local LLaMA 처리:
- LLaMA endpoint/model 설정은 기존 프로젝트 설정을 따른다.
- LLaMA가 꺼져 있으면 util은 실패하되 시스템 전체를 실패시키지 않는다.
- fallback으로 sample payload 기반 test mode를 지원해도 된다.
- LLaMA unavailable이면 LLAMA_UNAVAILABLE로 명확히 출력한다.
- LLaMA 응답을 바로 신뢰하지 말고 validation 후 renderer에 전달한다.

출력:
- generated_image_path
- generated_payload_path
- validation_status
- template_type
- source
- date

출력 파일명:
{template_type}_{YYYYMMDD_HHMMSS}_{short_hash}.png
{template_type}_{YYYYMMDD_HHMMSS}_{short_hash}.json

출력 위치:
SRC/foreign_worker_life_info_collector/storage/generated/content_cards/

주의:
generated output은 기본적으로 gitignore 대상이어야 한다.
샘플 output을 커밋할 필요는 없다.

테스트:
1. CHECKLIST_HOWTO input으로 JSON payload 생성
2. renderer를 통해 PNG 생성
3. generated payload와 image path 출력
4. 한글 포함 입력 테스트
   - LLaMA 결과 public text에 한글이 있으면 validation fail
5. LLaMA unavailable test
   - 명확한 error 반환
6. CHECKLIST_HOWTO bullets 3개만 생성되면 validation fail
7. ALERT_REVIEW bullets 3개면 pass

Walkthrough:
DOC/walkthrough/YYYY-MM-DD-llama-card-payload-generator.md 작성

포함 내용:
- 구현 목적
- 입력/출력 구조
- LLaMA prompt 방식
- validation 규칙
- renderer 연결 방식
- 실행 예시
- 테스트 결과
- 보호 영역 미수정 확인
- 남은 TODO

Commit / Push:
검증 통과 시에만 commit/push.

권장 commit message:
feat: generate content card payloads with local llama

중요:
이번 작업은 content text/link를 카드 payload JSON으로 변환하고 preview PNG를 생성하는 로컬 util이다.
Facebook 실제 게시, Telegram 실제 전송, scheduler, auth, token 영역은 건드리지 않는다.