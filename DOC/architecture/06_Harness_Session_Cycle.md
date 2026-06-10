## Harness Session Cycle

For long-running automation, Codex should work in fixed one-hour sessions.

The purpose of the one-hour session is to prevent uncontrolled long-running changes and to make progress easy for the user to inspect.

A standard session is divided as follows:

```text
00:00–00:10  Quick pre-review
00:10–00:40  Development work
00:40–00:50  Development verification
00:50–01:00  Final check and commit/push to git and Telegram summary and save it to /DOC/walkthrough/

1. Quick Pre-Review — 10 minutes

Codex must not edit code during this period.

Codex must inspect:

requested AREA
requested MODE
requested FOCUS
related architecture documents
likely files to touch
forbidden files or protected areas
possible verification method
possible stop conditions

At the end of this step, Codex must decide:

SAFE_TO_PROCEED
PROCEED_WITH_LIMITS
STOP_REQUIRES_USER_REVIEW

If the result is STOP_REQUIRES_USER_REVIEW, Codex must stop and write a stop report.

2. Development Work — 30 minutes

Codex may work only inside the approved AREA and MODE.

During this period, Codex must not expand the task scope.

Codex must not modify protected areas unless the task was explicitly approved as PROTECTED_CHANGE.

If Codex discovers that the task requires another area, it must stop instead of continuing.

3. Development Verification — 10 minutes

Codex must verify the work before reporting completion.

Depending on the task, verification may include:

backend server start check
frontend build or dev server check
API response check
unit or smoke test
UI visual check
DB read-only validation
lint or compile check
log inspection

If verification cannot be performed, Codex must say so clearly in the report.

A task is not complete only because the code was edited.

4. Final Check and Telegram Summary — 10 minutes

Codex must prepare a short final summary for the user.

If Telegram reporting is enabled, the backend automation reporter should send the summary to Telegram.

The summary must be compressed and operational.

Recommended format:

🧭 WorkConnect Harness Session Summary

Time: YYYY-MM-DD HH24:MI:SS ~ YYYY-MM-DD HH24:MI:SS KST
Area: [AREA]
Mode: [MODE]
Focus: [FOCUS]

Result:
- SAFE_TO_PROCEED / PROCEED_WITH_LIMITS / STOPPED

Done:
- ...

Changed:
- ...

Checks:
- Backend: OK / FAIL / NOT RUN
- Frontend: OK / FAIL / NOT RUN
- Tests: OK / FAIL / NOT RUN
- UI: OK / FAIL / NOT RUN

Risk:
- NONE / LOW / MEDIUM / HIGH

Needs user:
- ...

Telegram summaries must not include:

raw tokens
secrets
full stack traces
large diffs
noisy logs
private credentials

Detailed logs and long reports should remain in:

DOC/walkthrough/
Multi-Session Rule

For all-day automation, Codex should repeat one-hour sessions instead of running one long unstructured task.

After each one-hour session, Codex should either:

continue same AREA
switch AREA only if explicitly instructed
stop and wait for user review
write stop report

Codex must not silently switch areas between sessions.

If a session ends with unresolved risk, the next session must not continue implementation until the risk is reviewed.

Six-Hour Compression Rule

Every six one-hour sessions, Codex must create a compressed six-hour report.

The six-hour report should summarize:

sessions completed
areas worked on
files changed
checks performed
failures or stop reports
protected areas touched or avoided
user decisions needed
recommended next session

After the six-hour report, Codex should not start a new major phase without user review.

### Conditional Commit/Push Rule

During the final 10 minutes of each session, Codex should commit and push only when all of the following are true:

- the task stayed within the declared AREA
- no protected area was modified without approval
- backend/frontend/test verification passed, or skipped checks are clearly explained
- no known runtime-breaking error remains
- walkthrough was updated
- git diff was reviewed
- the commit message clearly describes the session result

If verification fails, Codex must not push broken work.

Instead, Codex must:

- write a walkthrough report
- write a stop report if needed
- leave changes uncommitted or commit only documentation if safe
- clearly tell the user what failed