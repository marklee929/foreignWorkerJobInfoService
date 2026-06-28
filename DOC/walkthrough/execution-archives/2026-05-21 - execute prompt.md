### 타임스탬프 수정내용 ###

WorkConnect Admin Panel 대시보드 UI를 운영 목적에 맞게 정리해줘.

현재 화면에서 불필요하거나 목적이 불분명한 요소를 제거하고, 용어를 통일해줘.

요구사항:

1. 상단 검색창 제거
- 현재 상단의 검색어 입력창은 대시보드 목적과 맞지 않으므로 제거한다.
- 관리자가 대시보드에서 검색 후 이동하는 흐름은 현재 필요 없다.
- 상단 바는 상태/알림/설정/로그아웃 중심으로 단순화한다.

2. 우측 상단 API 연결 상태 배지 제거
- API 연결 상태는 정상 동작의 기본 전제이므로 상단에 계속 노출하지 않는다.
- API 또는 DB 연결이 끊기는 경우에는 화면 상단 고정 배지가 아니라 알림/로그/Telegram 알림으로 처리한다.
- 우측 상단에는 알림 버튼, 설정 버튼, 로그아웃 버튼만 남긴다.

3. 상단 요약 카드 정리
현재 상단 카드 중 다음 항목은 제거한다.
- DB 상태
- API 상태

이유:
- DB/API 연결은 운영 기본 조건이며, 정상 상태를 계속 카드로 보여줄 필요가 없다.
- 장애 발생 시에는 알림/실시간 운영 로그/Telegram으로 전달하면 된다.

4. 용어 통일
현재 화면에서 “봇”, “모듈” 용어가 혼용되고 있다.
사용자 관점에서는 “봇”으로 통일한다.

예:
- 활성 모듈 → 활성 봇
- 비활성 모듈 → 비활성 봇
- 모듈 실행 정책 → 봇 실행 정책
- DB 모듈 상태 → 봇 상태 또는 제거
- module_config 관련 설명은 내부 데이터명으로만 유지하고 화면 문구에는 “봇”을 사용한다.

단, 개발 코드나 DB 테이블명이 module_config인 경우에는 무리하게 변경하지 말고 UI 표시 문구만 “봇”으로 바꾼다.

5. 상단 요약 카드 구성 변경
상단 카드는 운영자가 실제로 봐야 하는 지표만 남긴다.

추천 카드:
- 오늘 후보
- 게시 완료
- 중복 제거
- 활성 봇
- 비활성 봇
- 실패

각 카드에는 숫자와 짧은 보조 문구만 표시한다.

6. 연결 상태 영역 정리
현재 “연결 상태” 카드에서 DB/API 상태를 상세히 보여주는 부분은 대시보드 핵심 영역에서 제거하거나 접는다.
DB/API 장애는 실시간 운영 로그와 알림으로만 보여준다.

7. Local LLaMA 영역은 유지
Local LLaMA는 실제 운영 기능과 관련 있으므로 유지한다.
다만 상태값은 한글로 표시한다.

예:
- CONNECTED → 연결됨
- DISCONNECTED → 연결 안 됨
- STARTING → 시작 중
- ERROR → 오류
- DISABLED → 비활성

8. 봇 상태 영역 유지
봇 상태는 대시보드 핵심 영역으로 유지한다.
표시는 단순하게 한다.

예:
- 소셜 뉴스 봇
- 실행 중 / 중지됨 / 장애
- 시작/종료 토글

9. 실시간 운영 로그 강화
대시보드 하단의 “실시간 운영 로그”를 더 중심 요소로 배치한다.
표시 내용:
- 뉴스 수집 시작/완료
- 후보 기사 제목
- 요약 완료
- 중복 제외
- 점수 평가
- 게시 대기
- 게시 완료
- 오류 발생

10. 전체 방향
대시보드는 설정 페이지가 아니라 “현재 운영 상태를 빠르게 보는 화면”으로 정리한다.
정상인 DB/API 상태를 계속 보여주지 말고, 이상 발생 시에만 알림으로 노출한다.
UI 문구는 모두 한글로 유지한다.

구현 후 프론트엔드 빌드 오류를 확인하고, 변경 파일 목록과 변경 요약을 정리해줘.

### 타임스탬프 수정내용 ###

WorkConnect Admin Panel에서 News Collector 봇과 Facebook Posting 봇을 활성화해줘.

목표:
뉴스를 수집하면 자동으로 중복 확인, 텍스트 검증, Local LLaMA 요약, 포인트 평가를 수행한 뒤 관리자 확인 없이 Facebook에 바로 게시한다.
게시 완료 후 Telegram으로 요약본, 원문 기사 링크, Facebook 게시 링크를 전송한다.
모든 처리 결과는 DB에 저장해서 나중에 Local LLaMA로 저장 기사 분석 및 2차 콘텐츠 생성에 활용할 수 있게 한다.

요구사항:

1. 활성화할 봇
다음 봇을 활성화 상태로 변경한다.

- Naver News Collector
- Google News Collector
- Facebook Publish
- Telegram Notify

가능하면 RSS News Collector는 아직 대기 상태로 유지한다.

2. 자동 파이프라인 흐름
뉴스 수집 후 다음 순서로 자동 실행한다.

1) 뉴스 수집
2) 중복 확인
3) 본문/텍스트 유효성 확인
4) Local LLaMA 요약
5) 포인트 평가
6) Facebook 자동 게시
7) Telegram 결과 알림
8) 전체 결과 DB 저장

관리자 승인 단계는 사용하지 않는다.
수집된 뉴스가 조건을 통과하면 바로 게시한다.

3. 중복 확인
중복 기준:
- 원문 URL
- 제목 hash
- 본문 hash
- 유사 제목
- 최근 게시된 Facebook 링크
- 최근 저장된 기사 기록

중복이면 게시하지 않고 로그에 남긴다.

로그 예:
- "중복 기사 제외: {title}"

4. 텍스트 유효성 확인
게시 전 다음 조건을 확인한다.

- 제목 존재
- 원문 URL 존재
- 본문 또는 요약 가능한 텍스트 존재
- 한국 외국인 취업/비자/생활/노동 정보와 관련성 있음
- 너무 짧거나 광고성/스팸성 기사 제외

5. Local LLaMA 요약
Local LLaMA를 사용해 기사 요약을 생성한다.

요약 결과는 다음 구조로 만든다.

- 한 줄 요약
- 핵심 포인트 3개
- 외국인 근로자/구직자에게 중요한 이유
- 주의할 점
- 추천 해시태그

LLaMA가 연결되지 않은 경우:
- Facebook Posting은 중단한다.
- 로그에 "Local LLaMA 연결 실패로 게시 중단" 저장
- Telegram으로 장애 알림을 보낸다.

6. 포인트 평가
각 기사에 점수를 부여한다.

평가 기준:
- 한국 외국인 취업 관련성
- 비자/출입국 관련성
- 노동/임금/고용 안정성 관련성
- 생활 정보 가치
- 최신성
- 신뢰 가능한 출처 여부
- 중복 가능성

점수 예:
```json
{
  "score": 87,
  "category": "노동",
  "risk": "LOW",
  "reason": "외국인 근로자의 고용 안정성과 직접 관련된 기사"
}

기본 게시 기준:

score >= 70
risk != HIGH
duplicate=false
Facebook 자동 게시
게시 조건을 통과하면 관리자 확인 없이 Facebook Page에 바로 게시한다.

게시 내용 형식:

[한 줄 요약]

핵심 포인트
1. ...
2. ...
3. ...

외국인 근로자에게 중요한 이유
...

원문 보기:
{article_url}

#WorkConnectKorea #외국인취업 #비자정보 #한국생활

Facebook 게시 성공 후 facebook_post_id 또는 facebook_post_url을 저장한다.

Telegram 알림
Facebook 게시가 완료되면 Telegram으로 결과를 보낸다.

Telegram 메시지 예:

✅ 뉴스 자동 게시 완료

제목: ...
카테고리: ...
점수: ...
위험도: ...

요약:
...

원문 기사:
...

Facebook 게시글:
...

게시 실패 시:

⚠️ 뉴스 게시 실패

제목: ...
원인: ...
원문 기사:
...
저장 데이터
뉴스 수집부터 게시 결과까지 전체 내용을 DB에 저장한다.

저장 내용:

원문 제목
원문 URL
출처
수집 시각
원문 본문 또는 추출 텍스트
정규화 텍스트
제목 hash
본문 hash
중복 여부
Local LLaMA 요약 결과
핵심 포인트
평가 점수
평가 사유
카테고리
위험도
Facebook 게시 여부
Facebook post id
Facebook post url
Telegram 알림 여부
처리 상태
실패 사유
전체 실행 로그
DB 테이블 설계
필요하면 다음 테이블을 추가 또는 확장한다.

예시:

social_news_article

컬럼:

id
title
url
source
source_type
collected_at
raw_text
normalized_text
title_hash
content_hash
is_duplicate
duplicate_reason
summary_short
summary_points
relevance_reason
score
category
risk_level
facebook_posted
facebook_post_id
facebook_post_url
telegram_notified
status
COLLECTED
DUPLICATE_SKIPPED
TEXT_INVALID
SUMMARIZED
SCORED
POSTED
FAILED
fail_reason
created_at
updated_at

social_news_pipeline_log

컬럼:

id
article_id
step
status
message
payload_json
created_at
운영 로그
대시보드의 실시간 운영 로그에 다음 이벤트를 표시한다.
뉴스 수집 완료
중복 제외
텍스트 검증 실패
LLaMA 요약 완료
점수 평가 완료
Facebook 게시 완료
Telegram 알림 완료
실패/장애 발생
봇 상태와 장애 처리
Facebook Posting 실패가 인증 문제라면 봇 상태를 장애로 변경한다.
Local LLaMA 연결 실패 시 게시를 중단하고 장애 알림을 보낸다.
단순 기사 1건 실패는 전체 봇 장애로 보지 말고 해당 기사만 FAILED 처리한다.
연속 실패 횟수가 일정 기준 이상이면 봇 상태를 장애로 변경한다.
UI 반영
대시보드 상단의 활성 봇 수에 Facebook Posting과 Telegram Notify 활성화 상태를 반영한다.
비활성 봇 목록에서 Facebook Publish, Telegram Notify를 제거한다.
실시간 운영 로그에 게시 흐름이 보이도록 한다.
후보 목록에는 Facebook 게시 URL이 있으면 표시한다.
한글화
화면 문구와 로그 문구는 모두 한글로 표시한다.

예:

게시 완료
중복 제외
요약 완료
점수 평가 완료
Facebook 게시 완료
Telegram 알림 완료
Local LLaMA 연결 실패
구현 후 확인
프론트엔드 빌드 오류 확인
백엔드 컴파일 오류 확인
봇 시작 후 뉴스 수집 → 요약 → 게시 → Telegram 알림 흐름이 동작하는지 확인
변경 파일 목록과 요약을 마지막에 정리한다.