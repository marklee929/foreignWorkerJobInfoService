# WorkConnect Korea

외국인 근로자를 위한 취업 정보와 생활 지원 정보를 수집, 정리, 배포하는 서비스 프로젝트입니다.

## 핵심 목적

- 외국인 근로자에게 필요한 취업, 비자, 노동, 병원, 주거, 지역 지원 정보를 구조화합니다.
- `foreign_worker_life_info_collector`를 통해 생활정보와 소셜 뉴스 자동화 파이프라인을 확장합니다.
- Facebook Page와 Telegram 같은 외부 채널 연동은 민감정보를 저장소에 남기지 않는 방식으로 구성합니다.

## 주요 모듈

- `SRC/ForeignWorkerJobInfoService`: Spring Boot 기반 서비스 애플리케이션
- `SRC/foreign_worker_life_info_collector`: Python 기반 생활정보 수집 및 소셜 뉴스 자동화 준비 모듈
- `DOC/architecture`: 현재 유지해야 할 구조 원칙
- `DOC/walkthrough`: 날짜별 작업 진행 기록
- `DOC/database`: DB 설계, 상태값, 마이그레이션 방향

## 최소 실행

Python 수집기 dry-run:

```powershell
$env:PYTHONPATH="C:\WORK\foreign_worker_job_info\SRC"
python -m foreign_worker_life_info_collector "서울 외국인 지원센터"
```

Spring Boot 애플리케이션은 `SRC/ForeignWorkerJobInfoService` 아래의 프로젝트 설정을 기준으로 실행합니다.

## 문서

- [작업 운영 가이드](DOC/architecture/workflow-guide.md)
- [2026-05-17 walkthrough](DOC/walkthrough/2026-05-17-news-automation.md)
- [DB 문서 위치](DOC/database/README.md)
- [Python 수집기 README](SRC/foreign_worker_life_info_collector/README.md)

## 민감정보 주의

토큰, API 키, `.env`, DB 파일, 실행 로그, raw/cache/state 데이터는 커밋하지 않습니다. 공개 저장소에 올릴 수 없는 값은 환경변수 또는 로컬 전용 설정으로만 관리합니다.
