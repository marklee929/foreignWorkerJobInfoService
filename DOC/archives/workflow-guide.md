# WorkConnect 작업 운영 가이드

이 문서는 ChatGPT 대화, GitHub 문서, Codex 작업을 연결하는 기본 운영 패턴을 정의한다.

## 목적

앱/수집기 개발 중 나온 판단과 변경 사항을 README에 누적하지 않고 `DOC/walkthrough`와 `DOC/architecture`에 분리 기록한다.

이를 통해 Codex가 최신 작업 맥락을 확인하고, 같은 작업을 반복하거나 이전 결정을 덮어쓰는 일을 줄인다.

## 문서 역할

### README.md

GitHub 방문자가 프로젝트를 빠르게 이해하기 위한 최소 소개 문서다.

README에는 다음만 둔다.

- 프로젝트 한 줄 설명
- 핵심 목적
- 주요 모듈 링크
- 최소 실행 방법
- 민감정보 주의사항
- 상세 문서 링크

README에는 날짜별 작업 기록, 긴 설계 토론, Codex 프롬프트 전문을 누적하지 않는다.

### DOC/architecture

현재 유지해야 할 구조 원칙을 정리하는 문서 위치다.

예:

- `workflow-guide.md`: 작업 운영 방식
- `collector-hierarchy.md`: collector 패키지 하이어라키
- `social-news-pipeline.md`: Facebook 뉴스 자동화 구조
- `crew-team-responsibility.md`: crew_team 역할 정의

architecture 문서는 날짜별 로그가 아니라 현재 기준으로 유지되는 설계 원칙을 담는다.

### DOC/walkthrough

날짜별 작업 흐름과 결정 기록을 저장한다.

파일명 예:

```text
DOC/walkthrough/2026-05-16-news-automation.md
DOC/walkthrough/2026-05-16-hierarchy-refactor.md
```

walkthrough 문서에는 다음을 기록한다.

- 그날의 목표
- 대화 중 결정된 구조
- Codex에게 전달한 작업 지시 요약
- 실제 완료된 내용
- 실패/중단된 내용
- 다음 작업 시작점

### DOC/database

DB 설계, 상태값, 테이블 역할, 마이그레이션 방향을 기록한다.

## 기본 작업 패턴

### 1. ChatGPT 대화에서 방향 정리

작업 전에 ChatGPT와 구조, 우선순위, 구현 범위를 정리한다.

이때 나온 결론은 다음 중 하나로 저장한다.

- 장기 구조 원칙이면 `DOC/architecture`
- 날짜별 진행 기록이면 `DOC/walkthrough`
- DB 설계면 `DOC/database`

### 2. ChatGPT가 GitHub 문서 업데이트

앱 작업 중 중요한 결정이 생기면 ChatGPT가 GitHub 문서를 갱신한다.

주의:

- 코드 구현은 Codex가 담당한다.
- ChatGPT는 주로 문서, 이슈, 작업 가이드 정리를 담당한다.
- README는 비대하게 만들지 않는다.

### 3. Codex 작업 시작 전 최신 문서 확인

Codex에게 작업을 시킬 때는 먼저 다음을 확인하게 한다.

```text
git pull
DOC/architecture/workflow-guide.md 확인
DOC/walkthrough 최신 문서 확인
관련 GitHub issue 확인
```

Codex는 최신 walkthrough를 기준으로 이미 완료된 작업과 다음 작업을 구분한다.

### 4. Codex 작업 완료 후 walkthrough 업데이트

Codex 작업이 끝나면 반드시 해당 날짜의 walkthrough를 업데이트한다.

기록 내용:

- 변경한 파일
- 실행한 테스트
- 성공/실패 결과
- 남은 문제
- 다음 작업자가 이어받을 위치

이 기록을 통해 중복 작업을 방지한다.

## Codex에게 줄 기본 프롬프트 템플릿

```text
### 타임스탬프 수정내용 ###

작업 대상:
C:\WORK\foreign_worker_job_info

먼저 최신 main을 pull 받아라.

다음 문서를 먼저 읽고 현재 작업 맥락을 파악해라.
- DOC/architecture/workflow-guide.md
- DOC/walkthrough 최신 날짜 문서
- 관련 GitHub issue

README는 프로젝트 소개용으로만 유지하고, 긴 작업 기록은 DOC/walkthrough에 남겨라.

이번 작업 범위:
[여기에 작업 범위 작성]

주의:
- 민감정보, 토큰, .env, DB 파일, logs 파일은 커밋하지 마라.
- 작업 대상 외 폴더는 수정하지 마라.
- 작업 완료 후 테스트 결과와 변경 파일 목록을 DOC/walkthrough/YYYY-MM-DD-*.md에 업데이트해라.
- git status 확인 후 commit/push까지 수행해라.
```

## 현재 프로젝트 우선순위

1. `foreign_worker_life_info_collector` 하이어라키 안정화
2. `social/news` 기반 뉴스 자동화 파이프라인 완성
3. DB 저장, 중복 제거, dry-run 검증
4. Facebook Page 자동 게시 연결
5. Telegram 결과 노티파이 연결
6. 이후 지역별 생활정보 DB 수집 시작

## 금지 원칙

- README에 모든 설계 내용을 누적하지 않는다.
- GitHub Issue 내용을 README로 그대로 복사하지 않는다.
- Codex 작업 로그를 코드 주석에 길게 남기지 않는다.
- 실제 API 토큰을 문서나 코드에 남기지 않는다.
- 완료 여부가 불명확한 작업을 완료된 것처럼 walkthrough에 쓰지 않는다.

## 완료 기준

작업 단위가 끝날 때마다 다음이 충족되어야 한다.

- 코드 변경 사항이 명확하다.
- 테스트 또는 dry-run 결과가 기록되어 있다.
- walkthrough에 다음 작업자가 이어받을 수 있는 설명이 있다.
- README는 간결하게 유지된다.
- git status가 깨끗하다.
