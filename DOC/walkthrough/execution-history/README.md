# Execution History

## Purpose

`DOC/walkthrough/execution-history/` stores actual execution results from walkthrough-based Codex runs.

It exists so that phase reports are not trapped only inside a daily execute prompt file.

## Authority Boundary

This folder is not:

- an active rule source
- an implementation approval queue
- a replacement for `DOC/architecture`
- a permission source for touching runtime code, DB, scheduler, publisher, auth, env/config, or external APIs

This folder is:

- a result archive
- a place to store `PHASED_EXECUTION` reports
- a place to store per-phase result files
- context for future read-only review

Active rules remain in `DOC/architecture/`.

## Folder Pattern

Use a KST date folder:

```text
DOC/walkthrough/execution-history/YYYY-MM-DD/
```

Examples:

```text
DOC/walkthrough/execution-history/2026-06-20/PHASED_EXECUTION_REPORT.md
DOC/walkthrough/execution-history/2026-06-20/phase-01-dashboard-logs-result.md
DOC/walkthrough/execution-history/2026-06-20/phase-02-card-preview-result.md
DOC/walkthrough/execution-history/2026-06-20/phase-03-living-domain-audit-result.md
```

## Phase Report Naming

Use:

```text
phase-XX-[short-name]-result.md
```

Minimum structure:

```text
# PHASE XX Result

## 1. 결론 요약
## 2. AREA / MODE / PURPOSE FUNCTION
## 3. 수정한 파일
## 4. 검증 결과
## 5. 보호영역 touched 여부
## 6. 재시작 / 재로딩 필요 여부
## 7. 남은 위험
## 8. 다음 CODE_TASK_CANDIDATE
```

## Restart / Reload Section

Every phase result and `PHASED_EXECUTION_REPORT.md` should include:

```text
## 재시작 / 재로딩 필요 여부
```

Follow the template in `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`.

## Relationship to Other Folders

- `DOC/walkthrough/`: daily queue and same-day working record
- `DOC/walkthrough/execution-history/`: actual execution result archive
- `DOC/correction-loop/`: recurring failure patterns and harness improvement candidates
- `DOC/architecture/`: active governance and execution rules
