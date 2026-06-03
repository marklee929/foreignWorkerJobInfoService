### 타임스탬프 수정내용 ###

WorkConnect Admin Panel의 봇 운영 UI와 Local LLaMA 연동 방식을 정리해줘.

목표:
봇 운영은 별도 복잡한 설정 페이지로 만들지 않는다.
대시보드에서 봇의 현재 상태를 확인하고, 시작/종료만 토글로 제어한다.
에러나 장애가 발생하면 봇은 자동으로 중지되고 장애 상태로 표시한다.
서버 실행 시 Local LLaMA도 함께 기동되도록 구성한다.

요구사항:

1. 봇 운영 UI 단순화
- 사이드바의 “봇 운영” 메뉴는 제거하거나 “시스템” 하위로 이동한다.
- 대시보드에 “봇 상태” 카드를 추가한다.
- 봇 상태는 다음 중 하나로 표시한다.
  - 실행 중
  - 중지됨
  - 장애
  - 시작 중
  - 종료 중
- 제어는 토글 버튼 하나만 사용한다.
  - ON: 봇 시작
  - OFF: 봇 종료
- 장애 상태일 때는 토글을 OFF로 표시하고, “장애 발생” 배지를 표시한다.
- 장애 상태에서는 사용자가 다시 시작 버튼을 누르기 전까지 자동 재시작하지 않는다.

2. 봇 상태 API
다음 API를 추가 또는 정리한다.

GET /api/admin/bot/status
- 현재 봇 실행 상태 반환
- 반환 예시:
```json
{
  "status": "RUNNING",
  "label": "실행 중",
  "lastStartedAt": "...",
  "lastStoppedAt": "...",
  "lastErrorAt": null,
  "lastErrorMessage": null
}

POST /api/admin/bot/start

봇 실행 시작
이미 실행 중이면 중복 실행하지 않고 현재 상태 반환

POST /api/admin/bot/stop

봇 실행 종료
이미 중지 상태이면 현재 상태 반환

POST /api/admin/bot/reset-error

장애 상태 초기화 후 중지 상태로 변경
봇 장애 처리
수집, 정규화, 요약, 중복검사, 평가, 게시 단계 중 치명적인 예외가 발생하면 봇 상태를 ERROR로 변경한다.
ERROR 상태에서는 pipeline 실행을 중단한다.
에러 메시지는 DB 또는 로그에 저장한다.
프론트에서는 간단히 표시한다.
“장애 발생”
“마지막 오류: ...”
상세 stack trace는 화면에 노출하지 않는다.
DB 테이블
봇 상태를 저장할 테이블을 추가한다.

예시:
admin_bot_runtime

컬럼:

id
bot_key
status
RUNNING
STOPPED
ERROR
STARTING
STOPPING
last_started_at
last_stopped_at
last_error_at
last_error_message
created_at
updated_at

조건:

bot_key는 기본값 "social_news_bot" 사용
서버 재시작 후에도 마지막 상태를 DB에서 읽는다.
다만 서버 재시작 시 RUNNING이 남아있으면 실제 프로세스 상태와 비교 후 보정한다.
Local LLaMA 서버 동시 기동
현재 Local LLaMA가 실제로 연동되지 않은 것 같으므로 서버 시작 시 자동으로 Local LLaMA 실행을 시도하도록 구성한다.
.env 또는 application 설정에 다음 값을 추가한다.

예시:

LOCAL_LLAMA_ENABLED=true
LOCAL_LLAMA_COMMAND=ollama serve
LOCAL_LLAMA_ENDPOINT=http://localhost:11434
LOCAL_LLAMA_MODEL=llama3.1
백엔드 서버 시작 시 LOCAL_LLAMA_ENABLED=true이면 LOCAL_LLAMA_COMMAND를 실행한다.
이미 LLaMA 서버가 실행 중이면 중복 실행하지 않는다.
실행 전 LOCAL_LLAMA_ENDPOINT에 health check를 먼저 요청한다.
health check 성공 시 “로컬 LLaMA 연결됨”으로 표시한다.
실패 시 command 실행 후 일정 시간 재시도한다.
그래도 실패하면 “로컬 LLaMA 연결 실패”로 표시하되, 전체 백엔드 서버는 죽이지 않는다.
Local LLaMA 상태 API
다음 API를 추가한다.

GET /api/admin/llama/status

반환 예시:

{
  "enabled": true,
  "connected": true,
  "endpoint": "http://localhost:11434",
  "model": "llama3.1",
  "status": "CONNECTED",
  "message": "로컬 LLaMA 연결됨"
}

상태값:

DISABLED
STARTING
CONNECTED
DISCONNECTED
ERROR
Local LLaMA 실행 정책
서버 시작 시 한 번 자동 실행 시도
관리자 화면에서 “LLaMA 재연결” 버튼 제공
실패해도 백엔드는 정상 기동
LLaMA가 비활성 상태면 요약/평가 단계에서 LLaMA 의존 기능은 호출하지 않는다.
LLaMA 필수 모듈이 아니면 pipeline은 가능한 범위에서 계속 실행한다.
LLaMA가 필요한 단계에서는 “LLaMA 비활성으로 건너뜀” 로그를 남긴다.
대시보드 UI 변경
기존 “로컬 LLaMA” 영역은 유지하되 실제 상태 API와 연결한다.
기존 “DB 모듈 상태” 테이블은 대시보드에서 제거하거나 접는다.
그 자리에 “실시간 운영 로그” 영역을 추가한다.
실시간 로그에는 다음 정보를 간략히 표시한다.
뉴스 수집 완료
기사 제목
요약 결과
중복 검사 결과
후보 점수
게시/스킵 결과
오류 발생
로그는 최신순 또는 시간순으로 읽기 쉽게 표시한다.
사이드바 정리
사이드바는 다음처럼 정리한다.
대시보드
콘텐츠 관리
소셜 뉴스
생활 정보
출입국
노동
데이터 품질
시스템 설정

“봇 운영”은 별도 메뉴로 두지 말고 대시보드의 봇 상태 카드에서 제어한다.

한글화
관련 UI 텍스트는 모두 한글로 표시한다.

예:

RUNNING → 실행 중
STOPPED → 중지됨
ERROR → 장애
STARTING → 시작 중
STOPPING → 종료 중
Connected → 연결됨
Disconnected → 연결 안 됨
Start Bot → 봇 시작
Stop Bot → 봇 종료
Restart LLaMA → LLaMA 재연결
Last Error → 마지막 오류
구현 후 확인
프론트엔드 빌드 오류 확인
백엔드 컴파일 오류 확인
서버 실행 시 LLaMA health check 로그 확인
봇 시작/종료 토글 동작 확인
장애 상태일 때 pipeline이 중단되는지 확인
변경 파일 목록과 요약을 마지막에 정리한다.