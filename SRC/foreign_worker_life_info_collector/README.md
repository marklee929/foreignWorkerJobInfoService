# foreign_worker_life_info_collector

WorkConnect 관리자용 수집/게시 런타임입니다.

## 저장소

- 관리자 인증, 소셜 뉴스, 채용정보 수집 데이터는 PostgreSQL을 사용합니다.
- 기본 데이터베이스는 `foreign_worker_job_info`입니다.
- 소셜 뉴스 런타임 테이블은 `social_news` 스키마를 사용합니다.
- 채용정보 수집 런타임 테이블은 `admin.employment_job_*` 테이블을 사용합니다.
- 로컬 파일 DB는 런타임 저장소로 사용하지 않습니다.

## 실행

```powershell
$env:PYTHONPATH="C:\WORK\foreign_worker_job_info\SRC"
python -m foreign_worker_life_info_collector.api.admin_dev_server
```

또는 프로젝트 루트에서:

```powershell
.\run.bat
```

## 수동 이전

과거 로컬 파일 DB에 남은 소셜 뉴스 데이터가 필요하면 수동 이전 스크립트를 실행합니다. 이 스크립트는 런타임에서 자동 실행되지 않습니다.

```powershell
$env:PYTHONPATH="C:\WORK\foreign_worker_job_info\SRC"
python -m foreign_worker_life_info_collector.scripts.migrate_sqlite_news_to_postgres --sqlite-db C:\WORK\foreign_worker_job_info\SRC\foreign_worker_life_info_collector\logs\news.db
```

