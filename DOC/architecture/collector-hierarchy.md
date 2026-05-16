# foreign_worker_life_info_collector 하이어라키 설계

## 목적

`foreign_worker_life_info_collector`는 외국인 취업·생활정보 수집과 Facebook 뉴스 자동화를 담당하는 Python 기반 CrewTeam 패키지다.

이 문서는 폴더 구조를 기능 레이어와 데이터 정체성 레이어로 분리하기 위한 기준을 정의한다.

## 핵심 원칙

- `research`는 데이터 카테고리가 아니라 수집·검증·정규화 기능 레이어다.
- `social`은 Facebook, Telegram 등 외부 채널 연동 레이어다.
- `domains`는 데이터의 실제 정체성/카테고리 레이어다.
- `crew_team`은 직접 구현체가 아니라 작업 흐름을 조율하는 봇/오케스트레이터 레이어다.
- `storage`는 DB, JSON cache, raw data, runtime state 저장소다.
- `utils`는 문자열, URL, 해시, 날짜, 로깅 등 공통 유틸이다.
- `logs`는 실행 로그만 저장하며, 실제 로그 파일은 git에 올리지 않는다.

## 현재 문제

초기 구조에는 다음 폴더들이 최상위에 평면적으로 존재했다.

```text
config/
crawler/
crew_team/
logs/
normalizer/
parser/
quality/
research/
social/
storage/
tests/
utils/
```

이 구조는 `crawler`, `parser`, `normalizer`, `quality`가 기능적으로는 research에 속하는데 최상위에 남아 있어 역할이 섞여 보인다.

따라서 실제 리팩터링에서는 legacy wrapper를 남기더라도, 기준 구조는 아래 목표 구조를 따른다.

## 목표 구조

```text
SRC/foreign_worker_life_info_collector/
  config/
    settings.py
    keywords.py
    sources.py
    social_channels.py

  crew_team/
    social/
      news_bot.py
      facebook_publish_bot.py
      telegram_notify_bot.py
    research/
      collector_bot.py
      verifier_bot.py
      normalizer_bot.py
    lifestyle/
      immigration_bot.py
      labor_bot.py
      hospital_bot.py
      housing_bot.py

  social/
    facebook/
      page_client.py
      post_builder.py
      publish_log.py
    telegram/
      bot_client.py
      notifier.py
    news/
      models.py
      pipeline.py
      collector/
      normalizer/
      duplicate_guard/
      quality/
      repository/

  research/
    pipeline.py
    crawler/
      naver_search_collector.py
      google_search_collector.py
      local_site_collector.py
    parser/
      business_info_parser.py
      contact_parser.py
      address_parser.py
      language_parser.py
    normalizer/
      business_normalizer.py
      region_normalizer.py
      duplicate_detector.py
    quality/
      quality_score_calculator.py
      stale_data_detector.py
      source_reliability_checker.py
    repository/
      research_repository.py

  domains/
    immigration/
    labor/
    hospital/
    housing/
    translation/
    local_support/

  storage/
    db/
      sqlite_client.py
      migrations/
        schema.sql
    cache/
    state/
    raw/

  utils/
    text_normalizer.py
    url_normalizer.py
    hash_utils.py
    date_utils.py
    logging_utils.py

  logs/
  tests/
```

## 폴더별 책임

### config

프로젝트 운영 설정을 담당한다.

- 검색 키워드
- 수집 소스 목록
- social channel 설정
- 환경변수 이름 정의

실제 API token이나 secret 값은 저장하지 않는다.

### crew_team

작업을 수행하는 봇/오케스트레이터 계층이다.

직접 DB 쓰기, API 호출, 파싱 로직을 길게 구현하지 않고 `research`, `social`, `storage`, `utils` 모듈을 호출해 흐름을 조율한다.

예:

```text
news_bot
→ social.news.collector 호출
→ social.news.duplicate_guard 호출
→ social.facebook.publisher 호출
→ social.telegram.notifier 호출
```

### social

외부 채널 연동 계층이다.

- Facebook Page 게시
- Telegram 운영 알림
- Naver Blog/카페 확장 가능성
- 추후 WhatsApp/Discord/Slack 확장 가능성

뉴스는 Facebook Page 운영에 종속되는 social content이므로 `social/news` 아래에 둔다.

### research

원천 데이터 수집 기능 레이어다.

- crawler
- parser
- normalizer
- quality
- repository

`research/news`는 만들지 않는다. 뉴스는 social 콘텐츠다.

### domains

데이터의 실제 정체성을 표현한다.

- immigration: 행정사, 이민변호사, 비자 상담
- labor: 노무사, 임금체불, 산재
- hospital: 외국인 진료 가능 병원
- housing: 주거, 기숙사, 부동산
- translation: 통역/번역 기관
- local_support: 외국인 지원센터, 다문화가족지원센터

### storage

영속 저장과 임시 저장을 담당한다.

- SQLite DB
- migrations
- JSON cache
- runtime state
- raw data

DB 파일, raw data, cache 파일은 git에 올리지 않는다.

### utils

공통 유틸이다.

- text normalizer
- URL normalizer
- hash utils
- date utils
- logging helper

비즈니스 의미가 강한 정규화는 `research/normalizer`에 둔다.

### logs

실행 로그 전용이다.

실제 로그 파일은 git에 올리지 않는다.

## 리팩터링 기준

- 기존 최상위 `crawler`, `parser`, `normalizer`, `quality`는 장기적으로 `research/*` 또는 `utils/*`로 이동한다.
- 기존 import가 깨질 수 있으므로 즉시 삭제하지 않고 wrapper 또는 compatibility layer를 남길 수 있다.
- 이동 후 README와 walkthrough에 실제 위치를 반영한다.
- 작업 완료 후 dry-run 실행 결과를 walkthrough에 기록한다.
