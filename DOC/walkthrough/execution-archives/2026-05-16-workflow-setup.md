# 2026-05-16 Workflow Setup

## 오늘 설정한 작업 운영 방식

- ChatGPT 대화에서 나온 설계/운영 판단은 GitHub 문서로 정리한다.
- Codex는 작업 시작 시 `git pull` 후 `DOC/architecture/workflow-guide.md`, 최신 `DOC/walkthrough`, 관련 GitHub Issue를 먼저 확인한다.
- 작업 완료 후에는 변경 파일, 검증 결과, 남은 문제, 다음 작업 시작점을 walkthrough에 남긴다.

## 생성된 기준 문서

- ChatGPT가 `DOC/architecture/workflow-guide.md`를 생성했다.
- 이 문서는 README를 비대하게 만들지 않고 `DOC/architecture`, `DOC/walkthrough`, `DOC/database`에 내용을 분리하는 기준을 정의한다.

## README 운영 원칙

- README는 프로젝트 개요, 핵심 목적, 주요 모듈, 최소 실행 방법, 상세 문서 링크만 유지한다.
- 날짜별 작업 로그, Codex 작업 지시 전문, 상세 설계 토론, DB 스키마 논의는 README에 누적하지 않는다.
- 상세 내용은 `DOC/architecture`, `DOC/walkthrough`, `DOC/database`로 분리한다.

## 현재 상태

- `foreign_worker_life_info_collector` 하이어라키 정리는 완료되어 `social`, `research`, `domains`, `storage`, `utils` 기준으로 분리되어 있다.
- 기존 import 호환을 위해 legacy 경로는 wrapper로 남겨져 있다.
- `DOC/database` 문서 위치를 마련했다.

## 다음 작업

- 다음 작업은 `social/news` 기반 뉴스 자동화 파이프라인 구현이다.
- 시작 전 GitHub Issue #1을 확인하고, 실제 Facebook/Telegram API 호출 없이 dry-run 가능한 흐름부터 만든다.
- 우선순위는 뉴스 후보 DB 저장, 중복 제거, 게시 대상 선별, 게시/알림 로그 구조다.
