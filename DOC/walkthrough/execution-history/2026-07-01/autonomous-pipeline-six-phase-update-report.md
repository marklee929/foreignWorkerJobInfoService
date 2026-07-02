# Autonomous Pipeline Six-Phase Update Report

## 1. 요약

- Status: COMPLETE
- AREA: `CODEX_HARNESS_DOCS + TO_BE_DOCS`
- MODE: `DOC_ONLY`
- PURPOSE FUNCTION: WorkConnect 장기 Codex 작업이 audit, history save, history re-read, design, implementation, verification/rollback, closeout, next-task generation 순서로 진행되도록 문서를 정리했습니다.

## 2. 읽은 문서

- `CODEX_BOOTSTRAP.md`
- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
- `DOC/architecture/06_WORK_AREA_REGISTRY.md`
- `DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md`
- `DOC/walkthrough/2026-07-01 - execute prompt.md`
- `DOC/walkthrough/execution-history/2026-07-01/autonomous-execution-policy-doc-only-report.md`

## 3. 수정 / 이동 파일

- Updated: `DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md`
- Moved/normalized:
  - from `DOC/architecture/09_LONG_TERM_CODING_PIPELINE.md`
  - to `DOC/to-be/09_LONG_TERM_CODING_PIPELINE.md`
- Moved/normalized:
  - from `DOC/architecture/10_PIPELINE_REAUDIT_PLAN.md`
  - to `DOC/to-be/10_PIPELINE_REAUDIT_PLAN.md`
- Moved/normalized:
  - from `DOC/architecture/11_SOURCE_COLLECTION_AUDIT_PLAN.md`
  - to `DOC/to-be/11_SOURCE_COLLECTION_AUDIT_PLAN.md`
- Moved/normalized:
  - from `DOC/architecture/12_IMPLEMENTATION_QUEUE_RULE.md`
  - to `DOC/to-be/12_IMPLEMENTATION_QUEUE_RULE.md`
- Updated references:
  - `DOC/walkthrough/2026-07-01 - execute prompt.md`
  - `DOC/walkthrough/execution-history/2026-07-01/autonomous-execution-policy-doc-only-report.md`

## 4. Decision Log

Decision:
- `DOC/to-be/00~03` 파일은 존재하지 않았고, 같은 장기 파이프라인 문서가 `DOC/architecture/09~12`에 있었습니다. 현재 task의 의도와 `TO_BE_DOCS` AREA에 맞춰 `DOC/to-be/09~12`로 정리했습니다.

Alternatives considered:
- Option A: `DOC/architecture/09~12`를 그대로 유지.
- Option B: 새 `DOC/to-be/09~12`를 중복 생성.
- Option C: `DOC/architecture/09~12`를 제거하고 `DOC/to-be/09~12`로 이동/정규화.

Selected option:
- Option C.

Why safe:
- 이번 작업은 `DOC_ONLY`입니다.
- `DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md`만 active architecture로 유지하고, 세부 장기 계획은 `DOC/to-be`로 분리했습니다.
- 중복 문서 생성을 피했습니다.
- runtime code, DB, scheduler, publisher, auth/env, external API behavior는 수정하지 않았습니다.

Why other options were rejected:
- Option A는 `TO_BE_DOCS` 영역 문서를 active architecture 위치에 두는 혼선을 남깁니다.
- Option B는 같은 정책을 두 위치에 중복 생성합니다.

## 5. 반영한 6-Phase 규칙

추가/보강한 cycle:

```text
PHASE 1: Pipeline/System Audit
PHASE 2: Save Audit Report to DOC/walkthrough/execution-history/YYYY-MM-DD/
PHASE 3: Re-read the saved audit report and prior reports for the same AREA
PHASE 4: Build Target Architecture / Implementation Plan from audit findings
PHASE 5: Implement bounded changes from the plan
PHASE 6: Verify, rollback or retry if needed, save closeout report, update marker, generate next task
```

핵심 rule:

- implementation은 audit report 저장 전 시작 금지
- implementation은 saved audit report re-read 전 시작 금지
- same-AREA execution-history를 먼저 읽고 이전 findings에서 계속 진행
- audit은 안전한 다음 작업이 없을 때를 제외하고 `CODE_TASK_CANDIDATE`를 최소 1개 생성
- verification 실패 시 failure classification, retry budget, rollback, failed report 저장, next safer task 생성
- report는 audit findings, design decisions, implementation changes, verification results, rollback/retry results, remaining risks, next task를 구분

## 6. 검증 결과

- `DOC/to-be/09_LONG_TERM_CODING_PIPELINE.md` exists: PASS
- `DOC/to-be/10_PIPELINE_REAUDIT_PLAN.md` exists: PASS
- `DOC/to-be/11_SOURCE_COLLECTION_AUDIT_PLAN.md` exists: PASS
- `DOC/to-be/12_IMPLEMENTATION_QUEUE_RULE.md` exists: PASS
- old `00~03` filename references: NONE
- protected boundary weakening: NONE
- runtime file changes: NONE

## 7. 보호영역 확인

- DB/migration: not modified
- Facebook publisher: not modified
- content publisher: not modified
- scheduler/bot state: not modified
- Telegram production behavior: not modified
- auth/env/secrets: not modified
- external API behavior: not modified
- runtime code: not modified

## 8. Restart / Reload

- Backend restart:
  - NO
  - Reason: 문서만 수정했습니다.

- Frontend dev server restart:
  - NO
  - Reason: Admin UI 코드 변경이 없습니다.

- Browser hard refresh:
  - NO
  - Reason: 화면 코드 변경이 없습니다.

- DB restart:
  - NO
  - Reason: DB schema/migration 변경이 없습니다.

- Scheduler/Bot restart:
  - NO
  - Reason: scheduler/bot state 변경이 없습니다.

- External service restart:
  - NO
  - Target: none
  - Reason: 외부 서비스 호출 또는 설정 변경이 없습니다.

## 9. 남은 위험

- `DOC/to-be/09~12`는 계획 문서이며, runtime implementation permission이 아닙니다.
- 향후 `05_CODEX_HARNESS_GUIDE.md`에 일부 규칙을 승격할 때는 실제 실행 사례 3~5회 검토 후 반영하는 것이 안전합니다.

## 10. Next CODE_TASK_CANDIDATE

```text
CODE_TASK_CANDIDATE
AREA: CODEX_HARNESS_DOCS
MODE: READ_ONLY_AUDIT
PURPOSE FUNCTION:
Audit whether the new 6-phase long-running cycle is being followed in the next 3 walkthrough executions.
FOCUS:
Check audit report save, re-read, implementation plan, verification, retry/rollback, closeout marker, and next task generation.
WHY:
The new policy should be validated through real execution before promotion into stricter active harness rules.
ALLOWED:
- DOC/walkthrough/
- DOC/walkthrough/execution-history/
- DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md
- DOC/to-be/09_LONG_TERM_CODING_PIPELINE.md
- DOC/to-be/12_IMPLEMENTATION_QUEUE_RULE.md
FORBIDDEN:
- runtime code
- DB/migration
- scheduler
- publisher
- auth/env/secrets
- external API behavior
VERIFICATION:
- marker boundary check
- report existence check
- same-AREA history re-read evidence check
STOP CONDITIONS:
- protected area changes required
- task would require runtime changes
```
