# Autonomous Execution Policy DOC_ONLY Report

## 1. 요약

- Status: COMPLETE
- AREA: `CODEX_HARNESS_DOCS + TO_BE_DOCS`
- MODE: `DOC_ONLY`
- PURPOSE FUNCTION: WorkConnect 장기 작업에서 Codex가 반복 확인 없이 안전하게 audit, design, implementation, verification, rollback, next-task generation을 이어갈 수 있도록 정책 문서를 생성했습니다.

## 2. 읽은 문서

- `CODEX_BOOTSTRAP.md`
- `DOC/architecture/00_PRODUCT_NORTH_STAR.md`
- `DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md`
- `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
- `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
- `DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md`
- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
- `DOC/architecture/06_WORK_AREA_REGISTRY.md`
- `DOC/walkthrough/2026-07-01 - execute prompt.md`

## 3. 생성 파일

- `DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md`
- `DOC/to-be/09_LONG_TERM_CODING_PIPELINE.md`
- `DOC/to-be/10_PIPELINE_REAUDIT_PLAN.md`
- `DOC/to-be/11_SOURCE_COLLECTION_AUDIT_PLAN.md`
- `DOC/to-be/12_IMPLEMENTATION_QUEUE_RULE.md`

## 4. Decision Log

Decision:
- 기존 harness의 보호영역 stop rule은 유지하고, 사용자 부재 시 계속 진행 가능한 모호함과 반드시 멈춰야 하는 안전 모호함을 분리했습니다.

Alternatives considered:
- Option A: 모든 모호함에서 즉시 stop.
- Option B: 모든 모호함에서 Codex가 임의 결정.
- Option C: safe default가 있는 모호함은 decision log로 진행하고, protected/safety ambiguity는 stop.

Selected option:
- Option C.

Why safe:
- `05_CODEX_HARNESS_GUIDE.md`와 `06_WORK_AREA_REGISTRY.md`의 protected area rule을 약화하지 않습니다.
- `DOC_ONLY` 범위 안에서 정책 문서만 생성했습니다.
- runtime code, DB, scheduler, publisher, auth/env, external API behavior를 수정하지 않았습니다.

Why other options were rejected:
- Option A는 사용자가 부재 중일 때 장기 작업이 불필요하게 멈추는 문제를 해결하지 못합니다.
- Option B는 protected boundary를 약화할 위험이 있습니다.

## 5. 주요 반영 내용

- 사용자 장기 부재를 전제로 한 bounded autonomy 정책
- architecture/code/tests/prior reports 선검토 원칙
- decision log 의무화
- retry budget
- rollback policy
- stop gates
- next task generation
- source collection audit plan
- implementation queue rule
- first-run execute prompt fallback 보존
- protected areas 보존

## 6. 검증 결과

- 대상 문서 5개 생성 확인: PASS
- runtime 파일 변경 없음: PASS
- DB/migration 변경 없음: PASS
- scheduler/publisher/auth/env 변경 없음: PASS
- execute prompt first-run fallback 적용 가능 상태 확인: PASS

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
  - Reason: 문서만 생성했습니다.

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

- `08_AUTONOMOUS_EXECUTION_POLICY.md`는 continuation policy입니다. protected area approval을 대체하지 않습니다.
- `DOC/to-be` 문서는 계획 문서이며, runtime implementation permission으로 해석하면 안 됩니다.
- 향후 실제 queue-drain 구현 작업에서는 phase별 marker boundary를 다시 검증해야 합니다.

## 10. Next CODE_TASK_CANDIDATE

```text
CODE_TASK_CANDIDATE
AREA: CODEX_HARNESS_DOCS
MODE: DOC_ONLY
PURPOSE FUNCTION:
Review `08_AUTONOMOUS_EXECUTION_POLICY.md` against actual walkthrough behavior after 3-5 executions and promote only stable rules into `05_CODEX_HARNESS_GUIDE.md`.
FOCUS:
Compare policy intent with real marker closeout, phase reporting, retry, rollback, and next-task generation behavior.
WHY:
New policy should become active harness behavior only after practical validation.
ALLOWED:
- DOC/architecture/05_CODEX_HARNESS_GUIDE.md
- DOC/architecture/08_AUTONOMOUS_EXECUTION_POLICY.md
- DOC/correction-loop/
FORBIDDEN:
- runtime code
- DB/migration
- scheduler
- publisher
- auth/env/secrets
- external API behavior
VERIFICATION:
- document diff review
- marker rule consistency check
- protected area preservation check
STOP CONDITIONS:
- policy would weaken protected boundaries
- policy conflicts with product purpose
```
