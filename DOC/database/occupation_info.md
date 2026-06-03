# Occupation Info Pipeline

## Purpose

`occupation` schema stores Employment24 job and occupation dictionary data. This is not real-time job posting data.

## Environment Variables

Do not commit real keys.

```env
EMPLOYEE_24_OPEN_API_JOB_KEY=
EMPLOYEE_24_OPEN_API_OCCUPATION_KEY=
EMPLOYEE_24_OPEN_API_JOB_URL=
EMPLOYEE_24_OPEN_API_OCCUPATION_URL=
EMPLOYEE_24_OPEN_API_RETURN_TYPE=XML
```

`EMPLOYEE_24_OPEN_API_EMPLOYMENT_KEY` is not used by this pipeline.

## Tables

- `occupation.job_info`
- `occupation.occupation_info`
- `occupation.keyword_mapping`
- `occupation.collect_log`
- `occupation.raw_api_response`

## Admin API

- `GET /api/admin/occupation/dashboard`
- `GET /api/admin/occupation/jobs`
- `GET /api/admin/occupation/jobs/{id}`
- `POST /api/admin/occupation/jobs/collect`
- `GET /api/admin/occupation/occupations`
- `GET /api/admin/occupation/occupations/{id}`
- `POST /api/admin/occupation/occupations/collect`
- `GET /api/admin/occupation/keyword-mappings`
- `POST /api/admin/occupation/keyword-mappings`
- `PUT /api/admin/occupation/keyword-mappings/{id}`
- `POST /api/admin/occupation/keyword-mappings/generate`
- `GET /api/admin/occupation/collect-logs`

## Verification SQL

```sql
SELECT COUNT(*) FROM occupation.job_info;
SELECT COUNT(*) FROM occupation.occupation_info;
SELECT COUNT(*) FROM occupation.keyword_mapping;
SELECT * FROM occupation.collect_log ORDER BY started_at DESC LIMIT 10;
SELECT collector_type, parsed_yn, COUNT(*) FROM occupation.raw_api_response GROUP BY collector_type, parsed_yn;
```

## Current Scope

Implemented:

- PostgreSQL schema and seed keyword mappings
- JobInfoCollector and OccupationInfoCollector
- Admin API for collection, listing, detail, mappings, and logs
- Admin UI menu renamed to `직업정보`
- Admin UI tabs for dashboard, job info, occupation info, keyword mappings, and collect logs

Not implemented yet:

- PDF generation
- Facebook card content generation by occupation
- GPT Connect answer integration
- External country/language keyword expansion
- Automatic weekly scheduler for this dictionary pipeline
