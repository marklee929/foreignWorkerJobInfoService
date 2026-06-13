# Local Development Runtime Guide

## Purpose

This document defines development rules for WorkConnect while it is operated from a local PC before deployment to a production server.

WorkConnect is currently not running as a public production web service.

It is operated as a local web/admin system connected to local backend services, local database, local automation bots, local LLaMA/Ollama, Facebook publishing, and Telegram operation notifications.

Because the local environment is both a development environment and an operations environment, code changes must not casually break the running server, admin UI, scheduler, database access, or publishing pipeline.

## Current Runtime Assumption

Until production deployment, WorkConnect is operated as:

```text
local PC
→ local backend server
→ local admin web UI
→ local PostgreSQL
→ local automation bots
→ optional local LLaMA/Ollama
→ Facebook / Telegram external APIs
```

The system may still publish externally even though the web server is local.

Therefore, local development changes can affect real Facebook posting, Telegram notifications, collected data, and admin operations.

## Core Rule

Development must preserve local runtime stability.

A code change is not complete just because syntax is valid.

A code change is complete only when:

backend server can start
frontend web can run
frontend can communicate with backend
admin screen can load
critical status APIs respond
no protected area was changed unintentionally
UI is visually checked
logs do not show new runtime errors
## Local Server Safety

Before and after code changes, developers or Codex must verify server health.

Required checks

Check that the backend server:

starts without import errors
keeps running after first request
returns health/status response
does not crash after dashboard load
does not return unexpected 500 errors
handles CORS/preflight correctly
does not misclassify optional endpoint failure as full server failure

Check that the frontend:

builds or dev server starts
can load the admin page
can call backend APIs
does not show server disconnected incorrectly
does not create infinite polling loops
does not repeatedly call heavy APIs on route changes
Backend Restart Rule

If the backend server crashes during development:

Stop further feature work.
Identify the crash reason.
Fix the crash.
Restart the backend.
Verify health/status endpoint.
Reload admin UI.
Confirm frontend-backend communication.
Only then continue the original task.

Do not continue implementing unrelated changes while the server is broken.

Frontend-Backend Communication Rule

Any change to API routes, API client, CORS, headers, auth, response status, or endpoint return shape must be verified from both sides.

Verify:

request URL
HTTP method
response status
JSON shape
CORS headers
auth/device headers
frontend error handling
loading state
empty state
failure state

Special caution:

204 No Content

must not be treated as full server disconnection unless the endpoint explicitly means server failure.

Local Admin UI Rule

Admin UI work must be visually checked.

A UI task is not complete until the relevant screen is opened and inspected.

Check:

layout is not broken
cards align correctly
tables do not overflow unexpectedly
long text is truncated or wrapped safely
buttons are visible and understandable
Korean labels are displayed correctly
status badges are readable
loading/empty/error states are reasonable
no unrelated screen was visually damaged

If UI cannot be visually checked, the task report must say so.

Language Rule

User-facing strings in the admin UI should be Korean by default unless they are code values, API enum values, external service names, or English content intended for Facebook/public posts.

Use Korean for
admin UI labels
button labels
status descriptions
validation messages
local operation messages
user-facing error messages
Keep English for
code constants
API enum values
environment variable names
external service names
Facebook post content when English is intended
raw source article titles
technical log keys

Examples:

게시 완료
게시 대기
서버 연결 안 됨
최근 로그
수집 상태
콘텐츠 후보

Do not randomly mix Korean and English in admin UI labels unless the English term is a product/module name.

Timestamp Rule

All displayed operational timestamps should use:

YYYY-MM-DD HH24:MI:SS

Examples:

2026-06-10 21:35:12
2026-06-11 09:54:00

Avoid ambiguous formats such as:

6/10/26
오전 7:46
Tue Jun 10

If timezone matters, display or document it as KST.

Recommended:

YYYY-MM-DD HH24:MI:SS KST
Error Message Rule

Internal system messages must not become user-facing content.

Forbidden in public/generated content:

저장된 기사 본문이 없습니다.
일부 RSS/검색 결과는 원문 HTML 접근이 제한될 수 있습니다.
관리자 재게시 요청으로 즉시 Facebook 게시를 시도했습니다.
게시 기준 40점 이상을 충족했습니다.
현재 점수:
READY_TO_PUBLISH
candidate
queue
threshold
publish_status

These may appear only in:

admin diagnostics
pipeline logs
error reports
debug fields
stop reports

They must not appear in:

Facebook posts
public summaries
why-it-matters text
guide content
user-facing content candidate body
Runtime Error Handling Rule

A runtime error must be classified before fixing.

Local task error

The error is inside the current task area.

Allowed:

fix within current allowed files
verify and continue
Boundary error

The error points to another area.

Required:

stop
write report
ask for user review
Protected area error

The error involves:

admin auth
device approval
Facebook publisher
token validation
scheduler
bot state
destructive DB migration
content publisher
environment secrets

Required:

stop
do not patch blindly
write stop report
No Silent Degradation Rule

Do not hide errors by returning fake success.

Examples of forbidden behavior:

return empty dashboard because query failed
mark Facebook token invalid without Meta error code
turn bot off permanently after retryable DB error
show server disconnected because one optional endpoint failed
publish fallback content when article body is missing

Prefer explicit degraded status:

PARTIAL_FAILURE
DATA_UNAVAILABLE
TOKEN_STATUS_UNKNOWN
LINK_VALIDATION_FAILED
CONTENT_MISSING
RETRYABLE_DB_ERROR
Database Safety Rule

During local development, PostgreSQL may contain real collected data and publish history.

Do not run destructive DB changes without explicit approval.

Forbidden without approval:

DROP TABLE
TRUNCATE
DELETE bulk data
destructive ALTER
status mass rewrite
removing publish logs
removing candidates
clearing content queue

Preferred first:

SELECT diagnostics
backup
add nullable columns
add indexes
archive status
dry-run backfill
verification SQL
Migration Rule

Migration must be non-destructive first.

Preferred sequence:

add new column/table
→ backfill safely
→ verify counts
→ update UI/API
→ mark old field deprecated
→ remove only after approval

Migration reports must include:

migration file
affected tables
before/after row counts
rollback plan
verification SQL
Polling and Scheduler Rule

Frontend polling and backend scheduler changes are risky.

When changing polling:

prevent duplicate intervals
clean up interval on route leave/unmount
pause or reduce polling when document is hidden
avoid polling heavy list APIs
use summary endpoints for dashboard
do not treat one failed optional poll as full server failure

When changing scheduler:

do not change intervals casually
do not start new background loops without visibility
do not let failed cycle permanently disable bot
do not overlap same job unless locking is explicit
log next run time and cooldown state clearly
Dashboard Performance Rule

Dashboard is a status board.

It should read:

summary counts
status flags
recent logs with limit
bot status
LLaMA status
Facebook status

Dashboard must not:

load all news rows
load all content rows
load all logs
count large data in frontend
trigger collection or publishing by loading the page
Facebook and Telegram Rule

Facebook and Telegram integration may affect real external users.

Do not change the following without guarded review:

publish frequency
token validation
publish payload
content selection
retry policy
Telegram notification structure
Facebook link/message behavior

When publishing fails, preserve source error.

Do not collapse all Facebook errors into:

FACEBOOK_PAGE_ACCESS_TOKEN is invalid

Store and show:

Meta error type
code
subcode
message
fbtrace_id
internal error category
token status snapshot without raw token
Local LLaMA Rule

Local LLaMA/Ollama is optional.

The system must not fail only because local LLaMA is unavailable.

Distinguish:

automatic use off
model unloaded
Ollama server stopped
endpoint disconnected
timeout
fallback used

Do not kill or start server processes unless the task explicitly allows it.

UI Change Rule

When changing UI:

Identify affected screen.
Identify related store/API.
Check empty/loading/error states.
Check long text behavior.
Check Korean labels.
Check timestamp format.
Confirm no unrelated screen broke.

If screenshot/visual verification is not possible, report:

UI visual verification not performed

and explain why.

Code Change Boundary Rule

Same file does not mean same responsibility.

If a file contains multiple responsibilities, only modify the function/class/section related to the current task.

Example:

If admin_server.py contains dashboard routes and Facebook routes, a dashboard task must not modify Facebook token logic.

If Dashboard.vue contains summary cards and bot control toggles, a status card task must not modify bot control behavior.

Pre-Change Checklist

Before modifying code, check:

What screen or runtime path is affected?
What API endpoints are involved?
What DB tables are involved?
Could this affect auth, scheduler, publisher, or bot state?
Can I verify server health after the change?
Can I verify frontend-backend communication?
Can I visually check the UI?

If the answer is unclear, stop and write a short report before coding.

Post-Change Checklist

After modifying code, verify:

backend starts
frontend starts/builds
health/status endpoint works
target API works
admin UI loads
target screen visually OK
no new console/runtime error
logs show no new crash
protected areas not touched
timestamp format OK
Korean UI labels OK
Completion Report Requirement

Any Codex or automated development task must report:

task area
files inspected
files modified
server verification result
frontend verification result
API verification result
UI visual verification result
protected areas touched or not touched
tests/builds run
remaining risks
next recommended action
Stop Rule

Stop and report instead of continuing when:

backend cannot restart
frontend cannot connect to backend
auth is affected unexpectedly
Facebook/token/scheduler logic must be changed
DB migration becomes destructive
UI breaks outside the target screen
error source is outside current work area
verification cannot be performed
fixing requires guessing

A stopped task with a clear report is better than a completed task that breaks the local operations environment.
