# WorkConnect Project Overview - 2026-06-09

## Scope

This document summarizes the current WorkConnect codebase after reviewing the admin server, admin UI, social news pipeline, content hub, occupation/job data, immigration notice modules, Facebook/Telegram integrations, LLaMA controls, DB migrations, and existing design docs.

## Runtime Structure

- `SRC/ForeignWorkerJobInfoService`: Spring Boot service for legacy WorkNet/job API integration.
- `SRC/foreign_worker_life_info_collector/api/admin_server.py`: Python admin API for the Vue operations UI.
- `SRC/foreign_worker_life_info_collector/admin_ui`: Vue/Vite admin console.
- `SRC/foreign_worker_life_info_collector/social/news`: social news collection, normalization, scoring, duplicate guard, Facebook publishing, and Telegram notification.
- `SRC/foreign_worker_life_info_collector/content`: unified publishing hub backed by `content.content_candidate`.
- `SRC/foreign_worker_life_info_collector/occupation`: employment/job-code dictionary collection and enrichment base.
- `SRC/foreign_worker_life_info_collector/immigration`: official immigration notice collection and content conversion.
- `SRC/foreign_worker_life_info_collector/storage/db/migrations`: PostgreSQL schema and migration scripts.

## Admin Screens

- Dashboard: operational summary, bot state, LLaMA state, recent logs, and recent candidate preview. It should remain summary/count based and must not load full source tables.
- Social News: source-news management for collected articles, duplicate groups, article text, score state, and source/content linkage.
- Content Management: final Facebook publishing queue. It should show `content.content_candidate`, not every raw news duplicate.
- Occupation/Job Info: dictionary and enrichment workflow, not a content feed by itself.
- Immigration Notices: official notices, summarization/review, and planned content handoff.
- Job Collector: WorkNet/employment job collection status and logs.

## Data Flow

```text
Collectors
  -> raw source tables
  -> normalized/scored domain rows
  -> content.content_candidate for publishable items only
  -> Facebook publisher
  -> publish logs and source-row status update
```

Important boundary:

- `social_news.candidate` is source-news operational data.
- `content.content_candidate` is final publishable content.
- Duplicate, skipped, archived, invalid, and non-representative news rows should not become active content candidates.

## Current Strengths

- PostgreSQL repositories and migrations exist for social news, content, immigration, and occupation modules.
- Dashboard already has a summary API and paged log APIs.
- News candidate list has pagination and joins to `content.content_candidate`.
- Content hub already stores `raw_ref_table` and `raw_ref_id`, which is the right integration contract.
- Facebook publisher separates `message` and `link` and validates link-card URL quality.
- LLaMA status distinguishes local/managed endpoint state enough to build clearer UI wording.

## Main Problems Found

- Several UI/API strings are encoding-damaged and should be cleaned in a separate text-only pass.
- Dashboard polling was too frequent for an operations screen and could repeatedly call multiple endpoints during route stays.
- Content publishing could bypass the stricter Facebook message/link validation used by the social news publisher.
- Content list date meaning is still easy to confuse: original published/collected time, content created/updated time, and posted time need separate labels.
- Direct news publishing still exists beside content publishing; this should be reduced gradually behind a feature flag or scheduler migration.
- Occupation/job data needs enrichment fields before it can be useful as publishable content.

## Changes Applied In This Pass

- Dashboard silent refresh now uses a 30-second TTL.
- Dashboard polling stops while the document is hidden and refreshes when visible again.
- Unified content publishing now validates Facebook message text and link-card URL before dry-run or real publish.
- Social news publisher now blocks operational/admin text in Facebook messages in addition to Korean text.
- Dashboard summary Hangul-regex SQL was normalized to explicit Unicode escapes.

## Priority

1. Keep dashboard summary APIs count/limit based.
2. Finish content/source boundary cleanup before deleting any data.
3. Move schedulers to publish from `content.content_candidate`.
4. Add indexes for common status/date/reference filters.
5. Clean mojibake strings in UI/API docs and source messages.
6. Add occupation and living/immigration enrichment before making them publishable at scale.

### 긴급 복구 작업 ###

어젯밤 자동 오버룩 작업 이후 관리자 자동 로그인, 서버 연결 상태, 소셜 뉴스 봇, Facebook 게시가 망가졌다.

현재 증상:
- 관리자 화면 우측 상단: 서버접속불가
- 소셜 뉴스 봇: deadlock detected LINE 2...
- 대시보드 count가 0으로 표시됨
- 실시간 운영 로그가 비어 있음
- 자동 포스팅이 동작하지 않음

지금부터 신규 기능 개발/리팩토링을 중단하고 복구만 수행해줘.

1. 최근 커밋/변경파일 확인
- 어젯밤 이후 수정된 파일 목록 확인
- 인증/로그인/admin middleware/CORS/API client/dashboard store/polling/bot status/news pipeline/facebook publisher 관련 변경 우선 확인
- 변경 전후 diff를 요약

2. 서버접속불가 원인 확인
- frontend API base URL 확인
- admin server 포트 확인
- /api/admin/health 또는 유사 endpoint 확인
- CORS / OPTIONS 응답 확인
- API client interceptors 변경 여부 확인
- 204 No Content 응답을 실패로 처리하고 있는지 확인
- dashboard summary/status API가 204를 반환해서 프론트가 서버접속불가로 판단하는지 확인

3. 자동 로그인 복구
- 관리자 인증 device id / telegram approval / token 저장 로직 확인
- localStorage/sessionStorage key 변경 여부 확인
- X-Device-Id / X-Admin-Telegram-Secret 헤더 처리 확인
- 승인된 device가 유지되는지 확인
- favicon/static/OPTIONS 요청이 인증 요청을 생성하지 않게 유지

4. 소셜 뉴스 봇 deadlock 복구
- deadlock detected LINE 2 원문 로그 확인
- DB transaction / lock / scheduler 중복 실행 / bot status update 쪽 확인
- 봇 ON/OFF 플래그가 deadlock으로 stuck 되었는지 확인
- deadlock 발생 시 bot 전체를 OFF로 만들지 말고 해당 cycle만 FAILED_RETRYABLE 또는 SKIPPED 처리
- lock timeout과 retry/backoff 추가

5. Facebook 게시 복구
- NEWS_DIRECT_FACEBOOK_PUBLISH / CONTENT_PUBLISHER_ENABLED 변경 확인
- 기존에 동작하던 social_news → Facebook 게시 경로가 막혔는지 확인
- content queue 전환 작업이 불완전하면 일단 기존 news direct publish 경로로 롤백
- Facebook token validation은 is_valid=true이면 invalid 처리하지 않기
- 게시 실패 원본 Meta error를 그대로 로그에 남기기

6. 롤백 기준
아래 변경이 원인으로 보이면 즉시 롤백:
- dashboard summary API가 기존 endpoint를 대체한 변경
- admin auth middleware 변경
- API client base URL/interceptor 변경
- polling/store cache가 status API를 막는 변경
- news direct publish를 content publisher로 강제 우회한 변경
- bot status 플래그를 자동 OFF로 만드는 변경

7. 검증
복구 후 반드시 확인:
- 관리자 화면 접속 가능
- 자동 로그인 유지
- /api/admin/facebook/status 정상
- /api/admin/dashboard 또는 summary 정상
- 소셜 뉴스 봇 상태 ON
- deadlock 로그 사라짐
- 최근 운영 로그 표시
- 수동 Facebook 게시 1건 dry-run 또는 실제 게시 가능
- python -m py_compile 통과
- npm run build 통과

8. 완료 보고
- 원인 파일
- 원인 커밋/변경
- 롤백/수정한 내용
- 아직 보류한 기능
- 검증 결과

