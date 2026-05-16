# foreign_worker_life_info_collector

외국인 근로자 생활정보를 수집, 검증, 정규화하고 이후 소셜 채널로 배포하기 위한 Python 패키지입니다.

이번 구조는 뉴스 자동화 파이프라인 구현 전에 기능 계층, 데이터 도메인, 저장소, 외부 채널 연동을 분리하기 위한 기준 구조입니다. 실제 토큰, API 키, `.env` 파일은 저장소에 포함하지 않습니다.

## 구조

```text
foreign_worker_life_info_collector/
  config/                 # 환경변수명, 검색 키워드, 수집 소스, 소셜 채널 설정
  crew_team/              # 봇/오케스트레이터 계층
    social/               # 뉴스 게시, Facebook 게시, Telegram 알림 봇
    research/             # 수집, 검증, 정규화 봇
    lifestyle/            # immigration/labor/hospital/housing 도메인 작업 봇
  social/                 # 외부 채널 연동 계층
    facebook/             # Facebook Page client, post builder, publish log
    telegram/             # Telegram bot client, notifier
    news/                 # Facebook Page 운영에 종속된 뉴스 콘텐츠 파이프라인
      collector/
      normalizer/
      duplicate_guard/
      quality/
      repository/
  research/               # 생활정보 수집, 파싱, 정규화, 품질 평가 기능 계층
    crawler/
    parser/
    normalizer/
    quality/
    repository/
  domains/                # 데이터의 실제 정체성/카테고리
    immigration/
    labor/
    hospital/
    housing/
    translation/
    local_support/
  storage/                # SQLite, cache, state, raw data 저장 계층
    db/
      sqlite_client.py
      migrations/
        schema.sql
    cache/
    state/
    raw/
  utils/                  # 공통 문자열, URL, hash, 날짜, logging helper
  logs/                   # 실행 로그 전용
  tests/
```

기존 `crawler`, `parser`, `normalizer`, `quality`, `crew_team/*_agent.py`, `storage/db_writer.py` 경로는 바로 삭제하지 않고 compatibility wrapper로 유지합니다. 신규 코드는 `research/*`, `crew_team/research/*_bot.py`, `storage/db/sqlite_client.py` 경로를 우선 사용합니다.

## 역할 기준

- `config`: 환경변수명, 검색 키워드, 수집 소스, 소셜 채널 설정을 관리합니다. 실제 토큰/API 키는 저장하지 않습니다.
- `crew_team`: 직접 수집, 게시, 저장 로직을 구현하지 않고 `research`, `social`, `storage` 모듈을 호출하는 오케스트레이터 역할만 합니다.
- `social`: Facebook Page 게시, Telegram 알림 등 외부 채널 연동을 담당합니다. 뉴스 자동화는 `social/news`에 둡니다.
- `research`: 생활정보 원천 데이터를 수집, 검증, 정규화하는 기능 모듈입니다. `research/news` 구조는 만들지 않습니다.
- `domains`: immigration, labor, hospital, housing, translation, local_support처럼 데이터의 실제 정체성을 표현합니다.
- `storage`: SQLite DB, JSON cache, raw data, runtime state 저장을 담당합니다.
- `utils`: 공통 문자열 정규화, URL 정규화, hash 생성, 날짜 처리, logging helper를 담당합니다.
- `logs`: 서버/작업 실행 로그만 저장합니다.

## 실행

패키지 상위 경로를 `PYTHONPATH`에 포함하고 실행합니다.

```powershell
$env:PYTHONPATH="C:\WORK\foreign_worker_job_info\SRC"
python -m foreign_worker_life_info_collector "서울 외국인 지원센터"
```

SQLite에 저장하려면 `--db`를 지정합니다.

```powershell
python -m foreign_worker_life_info_collector "경기 외국인 진료 병원" --db C:\WORK\foreign_worker_job_info\SRC\foreign_worker_life_info_collector\logs\life_info.db
```

DB 스키마는 `storage/db/migrations/schema.sql`에 있습니다. DB 파일, cache, raw data, runtime state, 실제 로그 파일은 git에 포함하지 않습니다.

## 현재 구현 상태

- Google/Naver 수집기는 외부 API 호출 없이 dry-run 가능한 placeholder adapter입니다.
- `crew_team`은 직접 수집/게시/저장 로직을 갖지 않고 `research`, `social`, `storage` 모듈을 호출하는 오케스트레이터 역할만 합니다.
- Facebook/Telegram client는 구조만 배치되어 있으며 실제 네트워크 호출은 구현되어 있지 않습니다.
- 뉴스 자동화 관련 모듈은 `social/news` 아래에 배치되어 추후 Facebook Page 콘텐츠 파이프라인으로 확장합니다.
