# foreign_worker_life_info_collector

`foreign_worker_life_info_collector`는 외국인 생활정보 수집팀을 위한 독립 패키지입니다. PyQLE의 실험적 `crew_team`에서 작업 분배/에이전트 구조만 일반화했고, PyQLE 철학, 자아 루프, meaning node, RUMI/IKOL 계층과 대시보드/소셜 자동화 의존성은 포함하지 않았습니다.

## 수집 대상

- 행정사
- 이민 변호사
- 노무사
- 외국인 지원센터
- 다문화가족지원센터
- 외국인 진료 가능 병원
- 통역 가능 기관
- 지역별 외국인 생활 편의 정보

## 구조

```text
foreign_worker_life_info_collector/
  config/       # 카테고리, 언어, 태그 키워드
  crawler/      # Google/Naver/local site 수집 어댑터
  parser/       # 상호명, 연락처, 주소, 언어 파서
  normalizer/   # 업종/지역/중복 정규화
  storage/      # SQLite writer와 repository
  quality/      # 품질 점수, 최신성, 출처 신뢰도
  crew_team/    # collector/verifier/normalizer/research manager
  schema.sql    # DB 테이블 초안
```

## 실행

패키지 경로를 `PYTHONPATH`에 포함한 뒤 실행합니다.

```powershell
$env:PYTHONPATH="C:\WORK\foreign_worker_job_info\SRC"
python -m foreign_worker_life_info_collector "서울 외국인 지원센터"
```

SQLite에 저장하려면 `--db`를 지정합니다.

```powershell
python -m foreign_worker_life_info_collector "경기 외국인 진료 병원" --db C:\WORK\foreign_worker_job_info\SRC\foreign_worker_life_info_collector\logs\life_info.db
```

현재 Google/Naver 수집기는 API 키 없이 import와 파이프라인 검증이 가능하도록 placeholder adapter로 구성했습니다. 실제 운영에서는 각 파일의 `collect()`를 Naver Search API, Google Programmable Search, Kakao/Naver Place API, 지자체 사이트 크롤러로 교체하면 됩니다.

## DB 모델

DB 초안은 `schema.sql`에 있습니다.

- `source_raw_data`: 원천 수집 데이터와 중복 방지 hash
- `life_service_business`: 정규화된 기관/사업장 기본 정보
- `business_language_support`: 언어 지원 근거
- `business_service_tag`: 비자, 임금체불, 산재, 통역 등 서비스 태그
- `crawl_log`: 크롤러 실행 로그
- `data_quality_score`: 중복, 최신성, 연락처 유효성, 외국인 관련성 점수

## PyQLE에서 가져온 부분

- 가져온 개념: `crew_team/core/crew_team.py`의 collector/normalizer/verifier/research manager식 역할 분리
- 제거한 부분: PyQLE logger, 의미노드/자아 루프, RUMI/IKOL, 웹 대시보드, 소셜 자동화, LMDB/대용량 로그
- 이유: 현실 서비스용 데이터 수집 파이프라인은 재현 가능한 입출력, DB 적재, 품질 점수, 외부 API 교체 가능성이 우선입니다.
