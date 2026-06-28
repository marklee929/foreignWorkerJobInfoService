### 타임스탬프 수정내용 ###

작업 대상:
C:\WORK\foreign_worker_job_info\SRC\foreign_worker_life_info_collector

먼저 git pull 후 DOC/architecture/workflow-guide.md와 DOC/architecture/collector-hierarchy.md를 확인해라.

현재 문제:
최상위에 crawler, parser, normalizer, quality 폴더가 아직 남아 있다.
이전 작업에서 legacy wrapper로 남겨둔 것으로 보이지만, 사용자가 원하는 최종 구조는 탐색기 기준으로도 최상위 평면 폴더를 제거하는 것이다.

이번 작업 목표:
최상위 legacy wrapper 폴더를 제거하고, 실제 목표 하이어라키 기준으로 정리한다.

대상 legacy 폴더:
- crawler/
- parser/
- normalizer/
- quality/

작업 순서:
1. 각 legacy 폴더 내부 파일을 확인한다.
2. 실제 구현 파일인지 wrapper인지 구분한다.
3. 실제 구현 파일이 있으면 research/* 또는 utils/*의 적절한 위치로 이동한다.
4. 단순 wrapper라면 삭제한다.
5. 기존 import 호환이 반드시 필요하면 폴더를 남기지 말고 다음 중 하나로 처리한다.
   - foreign_worker_life_info_collector/compat.py
   - foreign_worker_life_info_collector/legacy_imports.py
   - 또는 README/DOC에 breaking change로 기록
6. __pycache__ 폴더는 삭제한다.
7. import 경로와 tests를 수정한다.
8. python -m foreign_worker_life_info_collector 실행이 깨지지 않는지 확인한다.
9. 변경 결과를 DOC/walkthrough 최신 날짜 문서에 기록한다.
10. git status 확인 후 commit/push한다.

주의:
- SRC/ForeignWorkerJobInfoService Spring 프로젝트는 수정하지 않는다.
- PyQLE-project는 수정하지 않는다.
- 실제 DB 파일, logs, cache, raw data는 커밋하지 않는다.
- 기능 구현은 하지 않는다. 이번 작업은 폴더 구조 정리만 한다.
- crawler/parser/normalizer/quality 최상위 폴더가 작업 후 탐색기에서 보이지 않아야 한다.

완료 기준:
- 최상위 crawler/parser/normalizer/quality 폴더가 제거된다.
- research/crawler, research/parser, research/normalizer, research/quality 구조가 유지된다.
- utils에는 공통 유틸만 남는다.
- 실행 테스트 또는 import 테스트 결과가 walkthrough에 기록된다.
- commit/push 완료.

커밋 메시지:
Remove legacy top-level collector wrappers


### 타임스탬프 수정내용 ###

작업 대상:
C:\WORK\foreign_worker_job_info\SRC\foreign_worker_life_info_collector

GitHub repository:
marklee929/foreignWorkerJobInfoService

먼저 최신 main을 pull 받아라.

그 다음 아래 문서를 반드시 확인해라.

1. DOC/architecture/workflow-guide.md
2. DOC/architecture/collector-hierarchy.md
3. DOC/architecture/social-news-automation.md
4. DOC/walkthrough 최신 날짜 문서

이번 작업 목표:
기존 Telegram 승인 기반 뉴스 플로우를 제거하고, social/news 기준의 완전 자동화 뉴스 업데이트 파이프라인을 구현한다.

현재 기존 흐름:
SEARCH NAVER FOR FOREIGNER WORK NEWS IN ENGLISH
→ SELECT BEST CANDIDATE
→ SEND IT TO TELEGRAM
→ USER APPROVE / REJECT / KEEP
→ APPROVED ONLY PUBLISH

변경할 목표 흐름:
SEARCH NAVER FOR FOREIGNER WORK NEWS IN ENGLISH/KOREAN
→ COLLECT CANDIDATE NEWS
→ NORMALIZE
→ SAVE CANDIDATES INTO DATABASE
→ SUMMARIZE
→ DUPLICATE CHECK
→ OPTIONAL LOCAL LLAMA RELEVANCE/DUPLICATE CHECK
→ SELECT BEST CANDIDATE AUTOMATICALLY
→ AUTO PUBLISH TO FACEBOOK
→ SEND PUBLISH RESULT TO TELEGRAM FOR USER CHECK ONLY
→ SAVE PUBLISH RESULT INTO DATABASE
→ CONTINUE NEXT CYCLE

중요:
Telegram 승인/거절/보류 플로우는 제거한다.
Telegram은 더 이상 승인 UI가 아니다.
Telegram은 게시 결과, 실패 사유, 중복 스킵 결과를 알려주는 운영 알림 채널이다.

작업 범위:
- SRC/foreign_worker_life_info_collector 내부만 수정한다.
- Spring 프로젝트 SRC/ForeignWorkerJobInfoService는 수정하지 않는다.
- PyQLE-project는 수정하지 않는다.
- 실제 Facebook/Telegram API 호출은 dry-run에서는 하지 않는다.
- 실제 토큰/API 키는 코드나 문서에 쓰지 않는다.

권장 모듈 위치:
social/news/

필요하면 아래 구조를 생성하거나 정리한다.

social/
  news/
    pipeline.py
    models.py
    collector/
      naver_news_collector.py
    normalizer/
      news_normalizer.py
    summarizer/
      news_summarizer.py
    evaluator/
      candidate_evaluator.py
    duplicate_guard/
      duplicate_detector.py
      llama_duplicate_checker.py
    publisher/
      facebook_publisher.py
    notifier/
      telegram_notifier.py
    repository/
      news_repository.py

shared connector가 필요하면 아래 위치를 사용한다.

social/
  facebook/
    page_client.py
    post_builder.py
  telegram/
    bot_client.py
    notifier.py

DB 요구사항:
뉴스 후보와 게시 결과를 반드시 DB에 저장한다.

필수 테이블 또는 동등한 저장 구조:
- news_candidate
- facebook_publish_log
- telegram_notify_log
- news_performance_snapshot는 추후용으로 만들어도 됨

news_candidate 상태값:
- CANDIDATE
- NORMALIZED
- SUMMARIZED
- DUPLICATE
- SKIPPED
- READY_TO_PUBLISH
- PUBLISHED
- FAILED
- NOTIFIED

중복 방지 기준:
1. canonical URL 중복
2. title hash 중복
3. similarity_key 중복
4. 최근 게시된 뉴스와 제목 유사도 비교
5. 같은 날짜/같은 키워드/같은 사건 반복 게시 방지
6. local LLaMA가 설정되어 있으면 semantic duplicate check 수행

local LLaMA 조건:
- LOCAL_LLAMA_ENDPOINT 환경변수가 있을 때만 사용한다.
- LLaMA가 없거나 timeout이면 deterministic duplicate rule로 fallback한다.
- LLaMA 결과는 advisory로만 사용하고, 전체 파이프라인을 중단시키지 않는다.
- LLaMA는 summary/relevance/semantic duplicate check에만 사용한다.
- LLaMA가 직접 publish 여부를 단독 결정하지 않게 한다.

자동 후보 선택:
candidate_evaluator는 아래 기준으로 점수를 계산한다.

- foreign_worker_relevance_score
- freshness_score
- source_reliability_score
- duplicate_risk_score
- content_clarity_score
- facebook_post_suitability_score

가장 높은 후보를 READY_TO_PUBLISH로 지정한다.
중복이면 DUPLICATE.
품질 낮으면 SKIPPED.
게시 실패하면 FAILED.

Facebook 게시:
실제 모드에서만 Facebook Page에 게시한다.
dry-run에서는 게시 내용을 생성만 하고 API 호출하지 않는다.

필수 환경변수:
- FACEBOOK_PAGE_ID
- FACEBOOK_PAGE_ACCESS_TOKEN

Telegram 알림:
게시 후 결과만 전송한다.
승인 버튼/승인 대기/approve/reject/keep 관련 코드는 제거하거나 사용하지 않는다.

필수 환경변수:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

Telegram 알림 예시:
[WorkConnect News Published]
Status: PUBLISHED
Title: ...
Source: ...
Facebook Post ID: ...
Duplicate score: ...
Summary: ...

dry-run 요구사항:
아래 명령으로 실행 가능하게 만든다.

$env:PYTHONPATH="C:\WORK\foreign_worker_job_info\SRC"
python -m foreign_worker_life_info_collector.social.news.pipeline --db .\logs\news.db --dry-run

dry-run에서는:
- sample 또는 실제 수집 후보를 사용
- DB 저장
- normalize
- summarize
- duplicate check
- evaluator 실행
- Facebook publish simulation
- Telegram notify simulation
- 상태값 업데이트
까지 수행한다.

실제 모드:
환경변수가 없으면 명확한 에러 메시지를 출력하고 실패 로그를 남긴다.
환경변수가 있으면 자동 게시 후 Telegram 결과 알림을 보낸다.

기존 승인 플로우 제거:
다음 개념/함수/상태/문구가 있다면 제거하거나 비활성화한다.

- approve
- reject
- keep
- waiting_for_approval
- send_candidate_to_telegram_for_approval
- approval callback
- user decision
- manual approval required

대신:
- auto_select
- auto_publish
- notify_publish_result
- save_publish_result

로 전환한다.

작업 완료 후:
1. 테스트 또는 dry-run 실행 결과를 확인한다.
2. DOC/walkthrough 최신 날짜 문서에 다음 내용을 기록한다.
   - 변경 파일 목록
   - 승인 플로우 제거 여부
   - dry-run 결과
   - DB 저장 확인 여부
   - 남은 문제
   - 다음 작업 시작점
3. git status 확인
4. 민감정보, DB 파일, logs 파일이 커밋 대상에 없는지 확인
5. commit/push 수행

커밋 메시지:
Implement automated social news publishing pipeline