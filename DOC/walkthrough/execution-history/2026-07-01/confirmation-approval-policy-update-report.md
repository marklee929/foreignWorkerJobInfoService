# Confirmation Approval Policy Update Report

## 1. 결론

- Status: COMPLETE
- AREA: `CODEX_HARNESS_DOCS`
- MODE: `DOC_ONLY`
- PURPOSE FUNCTION: Codex가 사용자의 실행 위임 이후 채팅 확인 질문으로 멈추지 않도록 하네스 architecture에 확인/승인 분리 규칙을 추가했습니다.

## 2. 수정 파일

- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
- `DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md`
- `DOC/correction-loop/2026-07-01_CHAT_CONFIRMATION_IDLE_FAILURE.md`

## 3. 추가한 핵심 규칙

### Chat-level confirmation 금지

사용자가 이미 아래와 같은 실행 명령을 준 경우 Codex는 채팅으로 다시 묻지 않습니다.

- `다음 요청 진행`
- `다음 테스크`
- `계속 진행`
- `쭉 진행`
- `!wc-next`
- declared `PURPOSE FUNCTION`, `AREA`, `MODE`가 있는 execute prompt

금지 문장:

- "진행할까요?"
- "적용할까요?"
- "예를 눌러주세요."
- "계속할까요?"

### Platform/tool approval 분리

Codex Desktop, shell sandbox, filesystem sandbox, connector가 띄우는 승인창은 Codex의 추론 질문이 아닙니다.

승인 거부 또는 불가 시:

```text
TOOL_APPROVAL_REJECTED
TOOL_WRITE_REJECTED
```

로 기록하고 가능한 read-only verification/reporting을 계속합니다.

### Required security approval 유지

아래는 여전히 승인 또는 stop report 대상입니다.

- auth/env/secrets/token
- production Telegram send
- Facebook publishing
- scheduler/bot state changes
- destructive DB operation or migration
- writes outside workspace
- destructive filesystem operation
- external dependency/network operation

## 4. Decision Log

Decision:
- `05_CODEX_HARNESS_GUIDE.md`에 일반 하네스 규칙을 추가하고, `08_AUTONOMOUS_EXECUTION_POLICY.md`에 장시간 부재/비대기 실행 규칙을 추가했습니다.

Alternatives considered:
- `08`에만 추가
- correction-loop만 추가
- execute prompt에만 임시 규칙 추가

Selected option:
- `05` + `08` + correction-loop 동시 반영

Why safe:
- `DOC_ONLY` 변경입니다.
- runtime code, DB, scheduler, publisher, auth/env/secrets를 변경하지 않았습니다.
- 사용자 부재 시 멈추는 실패를 하네스 레벨에서 재사용 가능하게 차단합니다.

Why other options were rejected:
- `08`에만 넣으면 일반 하네스 작업에서 누락될 수 있습니다.
- correction-loop만 넣으면 실행 규칙으로 승격되지 않습니다.
- execute prompt 임시 규칙은 다음 날짜/다음 큐에서 재사용성이 약합니다.

## 5. 검증 결과

- `rg` 확인:
  - `Confirmation and Approval Policy` 존재
  - `TOOL_APPROVAL_REJECTED` 존재
  - `TOOL_WRITE_REJECTED` 존재
  - non-idling unattended execution rule 존재

- `git diff --check`:
  - target architecture docs whitespace check 통과

## 6. 보호영역 확인

- DB/migration: not modified
- publisher: not modified
- scheduler/bot state: not modified
- Telegram production behavior: not modified
- auth/env/config/secrets: not modified
- external API behavior: not modified
- runtime code: not modified by this harness policy task

## 7. 재시작 / 재로딩 필요 여부

- Backend restart: NO
  - 이유: documentation-only 변경입니다.

- Frontend dev server restart: NO
  - 이유: 이번 policy update는 Admin UI code를 수정하지 않았습니다.

- Browser hard refresh: NO
  - 이유: 화면 코드 변경이 아닙니다.

- DB restart: NO
  - 이유: DB schema/migration 변경이 없습니다.

- Scheduler/Bot restart: NO
  - 이유: scheduler/publisher/bot runtime을 수정하지 않았습니다.

- Ollama restart: NO
  - 이유: Ollama 관련 변경이 없습니다.

## 8. 남은 주의점

- Codex Desktop의 platform approval UI는 하네스 문서로 제거할 수 없습니다.
- 단, Codex는 그 승인창을 채팅 질문으로 반복하지 않아야 합니다.
- 승인 거부 시에는 `TOOL_APPROVAL_REJECTED` 또는 `TOOL_WRITE_REJECTED`로 기록하고 가능한 안전 작업을 계속해야 합니다.
