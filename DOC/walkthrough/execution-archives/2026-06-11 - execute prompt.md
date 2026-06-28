### WorkConnect Harness Run ###

작업 대상:
C:\WORK\foreign_worker_job_info

종료 목표:
2026-06-11 06:00:00 KST까지 가능한 범위에서 1시간 Harness Session Cycle을 반복한다.

이번 장기 작업의 목적:
WorkConnect 프로젝트를 운영 가능한 자동화 구조로 만들기 위해, 문서 기반 하네스 규칙을 먼저 읽고, 안전하게 점검 가능한 영역을 검토한다.
실제 코드 수정은 LOW_RISK 또는 GUARDED_FIX 범위 안에서만 수행한다.
위험한 영역은 직접 수정하지 말고 CODE_TASK_CANDIDATE 또는 STOP_REPORT로 남긴다.

필수 시작 절차:
1. git status 확인
2. git pull
3. 아래 문서 먼저 읽기
   - DOC/architecture/00_PRODUCT_NORTH_STAR.md
   - DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md
   - DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
   - DOC/architecture/03_SYSTEM_ARCHITECTURE.md
   - DOC/architecture/04_LOCAL_DEVELOPMENT_RUNTIME_GUIDE.md
   - DOC/architecture/05_CODEX_HARNESS_GUIDE.md
   - DOC/architecture/06_WORK_AREA_REGISTRY.md 또는 07_WORK_AREA_REGISTRY.md
   - DOC/database/00_DB_ARCHITECTURE_INDEX.md
   - DOC/database/01_CURRENT_DB_MAP.md
   - DOC/walkthrough 최신 문서

문서 파일명이 다르면 실제 존재하는 파일 기준으로 읽고, 파일명 불일치는 walkthrough에 기록한다.

---

## Harness Session Cycle

이 작업은 단일 1시간 세션으로 끝내지 말고, 종료 목표 시각까지 1시간 Harness Session Cycle을 반복한다.

각 세션은 다음 순서를 따른다.

```text
00:00–00:10  Quick pre-review
00:10–00:40  Development work
00:40–00:50  Development verification
00:50–01:00  Final check, walkthrough update, conditional commit/push, and Telegram summary