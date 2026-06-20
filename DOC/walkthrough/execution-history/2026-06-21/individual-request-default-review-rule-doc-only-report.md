# DOC_ONLY REPORT: Individual Request Default Review Rule

## 1. Pre-Review

* AREA: `CODEX_HARNESS_DOCS`
* MODE: `DOC_ONLY`
* Risk: `LOW`
* Protected areas touched: 없음
* Files inspected:
  * `CODEX_BOOTSTRAP.md`
  * `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  * `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  * `DOC/walkthrough/2026-06-21 - execute prompt.md`
  * `DOC/walkthrough/README.md`
  * `DOC/correction-loop/README.md`
* Files modified:
  * `CODEX_BOOTSTRAP.md`
  * `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  * `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  * `DOC/walkthrough/2026-06-21 - execute prompt.md`
  * `DOC/walkthrough/execution-history/2026-06-21/individual-request-default-review-rule-doc-only-report.md`

## 2. Changes Made

* `CODEX_BOOTSTRAP.md`
  * issue-specific follow-up 기본 동작을 `READ_ONLY_AUDIT`로 정의했다.
  * 명시적 구현 트리거가 있을 때만 runtime edit가 가능하다고 명시했다.

* `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  * `TRIGGER CARD: INDIVIDUAL_REQUEST_DEFAULT_REVIEW` 추가.
  * `TRIGGER CARD: OFFICIAL_NOTICE_ATTACHMENT_REVIEW_REQUIRED` 추가.
  * closeout rule에 `loose marker count` 실패 시 repair 또는 correction-loop 기록 의무를 추가.

* `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  * `Individual Request Default Rule` 추가.
  * `IMMIGRATION_DOMAIN` forbidden rule에 ZIP/generic attachment text publish 금지 추가.
  * `Execution card: Official Notice Attachment Review Required` 추가.

## 3. Default Review Rule Added

일반 개별 요청은 사용자가 명시적으로 구현을 요청하지 않으면 기본적으로 `READ_ONLY_AUDIT`로 처리한다.

적용 예:

* 특정 후보가 관련 있는지 확인
* 중복 또는 유사 후보가 왜 생겼는지 확인
* 카테고리/상태/source mapping이 맞는지 확인
* screenshot 또는 Telegram review item이 이상한지 확인
* official notice ZIP/PDF가 public content로 적합한지 확인

이 경우 Codex는 inspect/report만 수행하고, 필요 시 `CODE_TASK_CANDIDATE`를 작성한다.

## 4. Explicit Fix Triggers

구현이 가능한 트리거:

* `!wc-fix`
* `implement`
* `patch`
* `fix it`
* `apply the fix`
* `make the change`
* 명확한 `AREA`, `MODE`, `FOCUS`가 있는 bounded implementation prompt

`!wc-audit`는 항상 `READ_ONLY_AUDIT`다.

## 5. Closeout Reinforcement

walkthrough-driven work는 chat-only response로 끝나면 불완전하다.

필수 closeout:

* report file 저장
* today execute prompt 업데이트
* WorkConnect completion marker exact count = 1
* legacy decorated Korean marker count = 0
* loose marker count = 0
* final line is the WorkConnect completion marker

본문이나 예시에는 exact marker를 쓰지 않고 placeholder 또는 설명문으로 대체해야 한다.

## 6. Verification

* trigger card exists: YES
  * `TRIGGER CARD: INDIVIDUAL_REQUEST_DEFAULT_REVIEW`
  * `TRIGGER CARD: OFFICIAL_NOTICE_ATTACHMENT_REVIEW_REQUIRED`
* default ambiguous request behavior is `READ_ONLY_AUDIT`: YES
* `!wc-fix` remains the explicit implementation path: YES
* protected areas were not touched: YES
* WorkConnect completion marker state is valid after closeout: YES
* Runtime code changed: NO
* DB/migration changed: NO
* scheduler/publisher/Telegram runtime/auth/env/config changed: NO
* external API called: NO

## 7. Final Recommendation

앞으로 사용자가 개별 현상 확인, 중복 확인, 카테고리 적합성 확인, ZIP/PDF official notice relevance 확인을 요청하면 기본은 `READ_ONLY_AUDIT`로 처리한다.

수정은 사용자가 `!wc-fix` 또는 명확한 구현 요청을 준 뒤, 해당 `AREA/MODE/FOCUS` 안에서만 진행한다.

