# Codex CLI / VS Code Approval Configuration Note Report

## 1. 결론

- Status: COMPLETE
- AREA: `CODEX_HARNESS_DOCS + TO_BE_DOCS`
- MODE: `DOC_ONLY`
- PURPOSE FUNCTION: local Codex approval prompts와 WorkConnect protected boundaries를 분리하는 문서 규칙을 추가했습니다.

## 2. 읽은 문서

- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
- `DOC/architecture/06_WORK_AREA_REGISTRY.md`
- `DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md`
- `DOC/to-be/12_IMPLEMENTATION_QUEUE_RULE.md`

## 3. 수정 파일

- `DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md`
- `DOC/to-be/12_IMPLEMENTATION_QUEUE_RULE.md`

## 4. 생성 파일

- `DOC/walkthrough/execution-history/2026-07-01/codex-cli-vscode-approval-config-note-report.md`

## 5. 반영 내용

두 문서에 `Codex CLI / VS Code Approval Configuration Note` 섹션을 추가했습니다.

추가한 핵심 내용:

- local Codex approval prompts는 tool-runtime prompts이며 WorkConnect product safety gates가 아님.
- recommended local config:

```toml
approval_policy = "never"
sandbox_mode = "danger-full-access"
```

- 위 설정은 `~/.codex/config.toml`의 top level에 둬야 하며 `[approval]` 안에 넣지 않음.
- VS Code Codex extension은 실제로 `~/.codex/config.toml`을 사용하도록 설정되어야 함.
- local approval prompt를 끄더라도 WorkConnect protected changes가 승인되는 것은 아님.

## 6. 유지한 WorkConnect stop gates

아래 보호 경계는 변경하지 않았습니다.

- auth
- env/secrets/token
- destructive DB
- real external publish
- Telegram production behavior
- Facebook/content publisher
- scheduler/bot state
- external API behavior

## 7. 기술적 편집 실패 규칙

다음은 user-confirmation trigger가 아니라고 명시했습니다.

- Technical edit failures
- string replacement failures
- patch application failures

Codex는 사용자에게 묻기 전에 같은 `AREA`와 `MODE` 안에서 다른 안전한 editing method로 재시도해야 합니다.

## 8. 검증 결과

- `rg`로 `Codex CLI / VS Code Approval Configuration Note` 섹션 존재 확인.
- `rg`로 `approval_policy = "never"` 존재 확인.
- `rg`로 `sandbox_mode = "danger-full-access"` 존재 확인.
- `rg`로 `~/.codex/config.toml`, `[approval]`, `VS Code Codex extension` 언급 확인.
- `git diff --check` 통과.

## 9. 금지 영역 확인

- runtime code: not modified
- DB: not modified
- scheduler: not modified
- Facebook/content publisher: not modified
- Telegram production behavior: not modified
- auth/env/secrets: not modified
- external API calls: not executed
- destructive commands: not executed
- today execute prompt: not modified
- `[WC_EXECUTION_COMPLETE]`: not moved

## 10. 재시작 / 재로딩 필요 여부

- Backend restart: NO
  - 이유: documentation-only 변경입니다.

- Frontend dev server restart: NO
  - 이유: Admin UI code 변경이 없습니다.

- Browser hard refresh: NO
  - 이유: 화면 코드 변경이 없습니다.

- DB restart: NO
  - 이유: DB schema/migration 변경이 없습니다.

- Scheduler/Bot restart: NO
  - 이유: scheduler/bot runtime 변경이 없습니다.

- Ollama restart: NO
  - 이유: Ollama 관련 변경이 없습니다.

## 11. 남은 불확실성

- 실제 로컬 `~/.codex/config.toml` 내용은 확인하거나 변경하지 않았습니다.
- VS Code Codex extension이 어떤 설정 경로를 사용하는지는 runtime/config 영역이므로 이번 작업에서 변경하지 않았습니다.
