### 타임스탬프 수정내용 ###

현재 WorkConnect SaaS Admin Panel 프로젝트에 관리자 로그인 기능을 추가해줘.

목표:
비밀번호 로그인은 사용하지 않는다.
관리자 접속 시 클라이언트의 장치 식별값과 접속 IP를 확인하고, 신규 세션이면 Telegram 승인 메시지를 발송한다.
Telegram 메시지에서 OK / Cancel 버튼으로 승인 여부를 결정한다.
승인된 경우에만 관리자 화면 접근을 허용한다.
모든 내부 텍스트, 버튼, 알림, 에러 메시지는 한글로 표시한다.

요구사항:

1. 로그인 방식
- 비밀번호 입력 화면은 만들지 않는다.
- 최초 접속 시 장치 식별값(deviceId), 접속 IP, userAgent를 서버로 전송한다.
- deviceId는 브라우저 localStorage에 저장된 UUID를 사용한다.
- localStorage에 deviceId가 없으면 새 UUID를 생성해 저장한다.
- 서버는 deviceId + ip + userAgent 조합으로 관리자 접속 시도를 식별한다.

2. 세션 유지 정책
- 웹 세션으로 로그인 여부를 확인한다.
- 동일 deviceId + ip + userAgent 조합이 이미 승인된 활성 세션이면 Telegram 재승인 없이 바로 접속 허용한다.
- 사용자가 직접 로그아웃하기 전까지 세션을 제거하지 않는다.
- 브라우저 새로고침, 탭 종료, 재접속 시에도 동일 장치와 IP면 로그인 상태를 유지한다.
- 로그아웃 시에만 웹 세션과 DB 세션을 비활성화한다.

3. DB 세션 저장
다음과 같은 관리자 세션 테이블을 설계하고 마이그레이션/DDL을 추가한다.

테이블 예시:
admin_login_session

컬럼:
- id
- device_id
- ip_address
- user_agent
- status
  - PENDING
  - APPROVED
  - REJECTED
  - LOGGED_OUT
- telegram_message_id
- requested_at
- approved_at
- rejected_at
- logged_out_at
- last_seen_at
- created_at
- updated_at

조건:
- APPROVED 상태의 세션은 로그아웃 전까지 유지한다.
- 동일 device_id + ip_address + user_agent 조합에 APPROVED 세션이 있으면 재사용한다.
- PENDING 상태가 이미 있으면 중복 Telegram 메시지를 여러 번 보내지 않도록 기존 pending 세션을 재사용한다.

4. Telegram 승인
- 신규 접속 또는 승인되지 않은 접속이면 Telegram bot으로 관리자에게 승인 요청 메시지를 보낸다.
- 메시지 내용은 한글로 작성한다.

예시:
"관리자 페이지 접속 요청이 있습니다.
장치 ID: ...
IP: ...
브라우저: ...
승인하시겠습니까?"

- Inline Keyboard 버튼:
  - "승인"
  - "거부"

- 승인 버튼 클릭 시:
  - 해당 session status를 APPROVED로 변경
  - approved_at 저장
  - 사용자가 대기 중이면 프론트에서 polling 후 자동으로 관리자 화면으로 이동

- 거부 버튼 클릭 시:
  - status를 REJECTED로 변경
  - rejected_at 저장
  - 프론트에는 "접속이 거부되었습니다." 표시

5. 프론트엔드 화면
- 기존 Admin Panel 진입 전에 AuthGate 컴포넌트를 추가한다.
- 로그인 대기 화면을 만든다.
- 텍스트는 모두 한글로 표시한다.

화면 상태:
- 승인 확인 중
- Telegram 승인 대기 중
- 접속 승인 완료
- 접속 거부됨
- 서버 연결 실패
- 로그아웃 완료

예시 문구:
- "관리자 접속 확인 중입니다."
- "Telegram에서 접속 승인을 완료해주세요."
- "접속이 승인되었습니다."
- "접속이 거부되었습니다."
- "서버 연결에 실패했습니다."

6. API 설계
필요한 API를 추가한다.

예시:
POST /api/admin/auth/check
- deviceId, userAgent 전송
- 서버에서 IP 추출
- 기존 APPROVED 세션 확인
- 없으면 PENDING 세션 생성 및 Telegram 승인 요청
- 현재 상태 반환

GET /api/admin/auth/status/{sessionId}
- PENDING / APPROVED / REJECTED / LOGGED_OUT 상태 반환

POST /api/admin/auth/logout
- 현재 세션을 LOGGED_OUT 처리
- 웹 세션 제거
- DB 세션도 logged_out_at 저장

POST /api/admin/telegram/callback
- Telegram inline button callback 처리
- OK / Cancel 결과에 따라 세션 상태 변경

7. 보안 조건
- Telegram callback은 bot token 또는 secret path/token으로 검증한다.
- CORS는 기존 설정을 유지하되 관리자 API만 허용 범위를 명확히 한다.
- deviceId만으로 인증하지 말고 반드시 ip_address와 user_agent를 함께 비교한다.
- 승인되지 않은 사용자는 어떤 관리자 API도 호출할 수 없도록 한다.
- API 요청마다 현재 웹 세션의 로그인 여부를 검사한다.
- 운영 위험을 줄이기 위해 실패 메시지는 너무 자세한 내부 정보를 노출하지 않는다.

8. 라우터/가드
- Vue Router에 auth guard를 추가한다.
- 승인되지 않은 사용자는 관리자 메인 화면에 접근하지 못하고 AuthGate 화면으로 이동한다.
- 승인 완료 후 원래 접근하려던 route로 이동한다.
- 로그아웃 버튼을 사이드바 하단 또는 상단 우측에 추가한다.

9. 한글화
현재 UI의 내부 텍스트와 알림을 가능한 범위에서 한글로 변경한다.
예:
- API connection failed → API 연결 실패
- Refresh → 새로고침
- Empty list → 데이터 없음
- Run pending → 대기 항목 실행
- Logs → 로그
- Offline → 오프라인
- Read-only → 읽기 전용
- Dry run → 테스트 실행
- Selected Candidate → 선택된 후보
- Recent Logs → 최근 로그

10. 구현 후 확인
- npm run build 또는 기존 프로젝트의 빌드 명령을 실행해 오류를 확인한다.
- 백엔드가 있다면 테스트 가능한 범위에서 auth API 컴파일/실행 오류를 확인한다.
- 구현한 파일 목록과 변경 요약을 마지막에 정리한다.