# Living Information Implementation Design and Roadmap

Date: 2026-07-02

## Scope

This report covers the third `!wc-next` block in `DOC/walkthrough/2026-07-02 - execute prompt.md`.

Mode: `DOC_ONLY`

No runtime code, DB object, scheduler, Telegram production, or Facebook behavior was changed for this design task.

## Confirmed Findings

Already solved:
- Admin UI manual Living Information prepare action now calls the prep-cycle path.
- Manual lifestyle bot input breadth was expanded from 3 generic queries / fixed `limit=1` to source-oriented defaults and configurable per-keyword limit.

Still failing:
- `living_info.topic_cluster` has 0 persisted rows.
- Dry-run preparation over 55 normalized rows produces 0 public-ready clusters.
- Existing source evidence has 0 primary/official rows.
- `sync_living_info(limit=100)` sees 0 ready topic clusters and syncs 0 card candidates.
- Existing `content.content_candidate` Living Information rows are old direct `social_news.candidate` mappings, not topic-cluster based cards.
- Operators cannot easily see readiness failure reasons from Admin UI.

## Implementation Themes

### 1. Source Collection

Current state:
- Manual lifestyle bot uses Google News RSS and Naver News.
- Google News is discovery/media-oriented.
- Naver returns 0 without protected credentials.
- No dedicated official/public Living Information source collector exists.

Problem:
- Current collection cannot reliably produce primary/official evidence.

Target state:
- Living Information has a source registry and collector path for official/public guide sources.

Implementation goal:
- Add a source registry/list first, then a guarded collector/ingestion path.

Expected verification:
- Source registry unit tests.
- Dry-run collection preview shows configured sources without live publishing.

### 2. Pipeline Diagnostics

Current state:
- Prep-cycle can dry-run, but operator visibility is weak.

Problem:
- Admin user sees "no cards" without knowing source count, official evidence count, public-ready count, or skip reasons.

Target state:
- Admin has a read-only readiness diagnostic endpoint/panel.

Implementation goal:
- Expose dry-run topic-cluster readiness summary and top reasons.

Expected verification:
- Endpoint contract test.
- Admin UI displays counts from a mocked response.

### 3. Normalization and Evidence Classification

Current state:
- All current normalized items are `NEWS_EVENT` and `validation_needed_yn = Y`.
- Source trust ranks block public readiness without official/trusted evidence.

Problem:
- Practical guide data and news events are not clearly separated enough for card readiness.

Target state:
- Official/public guides can become source evidence; news remains signal/material unless validated.

Implementation goal:
- Add explicit source-type/source-trust classification tests for official/public guide URLs.

Expected verification:
- Unit tests for NHIS/NPS/MOEL/HiKorea/Seoul source trust classification.

### 4. Topic Cluster Readiness

Current state:
- Dry-run clusters mostly score 20-45 and are not public-ready.

Problem:
- The readiness gate is doing its job, but skip reasons are not visible enough.

Target state:
- Readiness gate returns explainable skip reasons.

Implementation goal:
- Add non-destructive readiness reason aggregation.

Expected verification:
- Dry-run diagnostics include `public_ready_count = 0` and reasons such as `missing_primary_evidence` or `readiness_below_threshold`.

### 5. Candidate Mapping

Current state:
- New topic-cluster path syncs 0 rows because there are no public-ready clusters.
- Old direct social-news mappings still exist.

Problem:
- Old queue rows can confuse diagnosis.

Target state:
- Admin and reports clearly distinguish direct legacy social-news rows from topic-cluster Living Information rows.

Implementation goal:
- Add display/report distinction, not publisher changes.

Expected verification:
- Read-only query or UI label test.

### 6. Testing

Current state:
- Existing tests cover many living-info service and sync paths.
- New lifestyle bot parameter tests were added.

Problem:
- No test yet covers operator-facing readiness diagnostics.

Target state:
- Readiness diagnostics are contract-tested.

Implementation goal:
- Add endpoint/service contract tests before UI expansion.

Expected verification:
- Targeted pytest passes.

## Prioritized Roadmap

### Priority 1: Readiness Diagnostic Endpoint

WHY:
- It explains why cards are not created without running external collection or publishing.

EXPECTED EFFECT:
- Operator can see source count, official evidence count, cluster count, public-ready count, and top skip reasons.

RISK:
- Low, if read-only/dry-run only.

VERIFICATION:
- Endpoint contract test.
- No DB mutation except existing dry-run behavior.

### Priority 2: Admin UI Readiness Panel

WHY:
- Diagnostic endpoint is useful only if visible where the operator clicks prepare/sync.

EXPECTED EFFECT:
- Reduced repeated confusion around "button clicked but no cards."

RISK:
- Low to medium; UI only but must not trigger protected send/publish behavior.

VERIFICATION:
- Frontend static contract test.
- UI build if practical.

### Priority 3: Official/Public Source Registry

WHY:
- Current data has 0 primary evidence.

EXPECTED EFFECT:
- Provides bounded list for official/public Living Information source expansion.

RISK:
- Low as config/list only.

VERIFICATION:
- Source registry test.
- No live external requests.

### Priority 4: Official/Public Collector Dry-Run Preview

WHY:
- Source registry must eventually feed source items.

EXPECTED EFFECT:
- Creates path toward primary evidence without immediate publishing.

RISK:
- Guarded; external HTTP behavior and parsing need careful constraints.

VERIFICATION:
- Mocked fetch tests.
- No credentials required.

### Priority 5: Topic Readiness Reason Aggregation

WHY:
- Current readiness failure is explainable but scattered.

EXPECTED EFFECT:
- Better reports and Admin diagnostics.

RISK:
- Low if additive and read-only.

VERIFICATION:
- Service tests for reason aggregation.

### Priority 6: Community Signal Design

WHY:
- Community can reveal user needs but must not become authoritative content.

EXPECTED EFFECT:
- Future signal path without unsafe scraping or quoting.

RISK:
- Future/protected depending on platform/API.

VERIFICATION:
- Design-only until explicit policy approval.

## Target Architecture

Current flow:

```text
Lifestyle bot
-> Google News RSS / Naver News
-> social_news.candidate
-> living_info.source_item
-> living_info.normalized_item
-> topic-cluster dry-run says not public-ready
-> sync_living_info sees 0 ready clusters
-> no new Living Information cards
```

Target flow:

```text
Living source registry
-> official/public source collector preview
-> source evidence preservation
-> normalized guide/news/signal classification
-> topic cluster readiness with reason aggregation
-> public-ready topic clusters only
-> content candidate sync from living_info.topic_cluster
-> Telegram review dry-run/guarded path
-> public delivery only after existing approval gates
```

Expected Living Card Flow:

```text
official/public source evidence
+ trusted media or repeated practical signal
-> readiness >= 60
-> validation_status READY or VALIDATED
-> content_candidate READY_TO_REVIEW
-> operator review
-> existing publish boundaries
```

## Executable Implementation Queue

### Task 1: Read-Only Readiness Diagnostic Endpoint

AREA:
`LIVING_DOMAIN + CONTENT_QUEUE`

MODE:
`LOW_RISK_FIX`

PURPOSE FUNCTION:
Expose why Living Information cards are not ready without publishing or mutating production state.

SUCCESS CRITERIA:
- Endpoint returns source count, dry-run cluster count, public-ready count, and top skip reasons.
- Existing prep-cycle behavior remains unchanged.
- Tests pass.

STOP CONDITIONS:
- implementation would require live external collection
- implementation would send Telegram/Facebook output
- implementation would mutate DB outside existing dry-run code

VERIFICATION:
- Python contract test
- `py_compile`

### Task 2: Admin UI Readiness Panel

AREA:
`LIVING_DOMAIN + ADMIN_UI`

MODE:
`LOW_RISK_FIX`

PURPOSE FUNCTION:
Show readiness diagnostics next to the Living Information prepare action.

SUCCESS CRITERIA:
- UI calls diagnostic endpoint.
- UI shows counts and skip reasons.
- No publisher/send action is added.

STOP CONDITIONS:
- UI change touches auth, publisher, Telegram callback, or scheduler state.

VERIFICATION:
- frontend contract/static test
- build if available

### Task 3: Official/Public Source Registry

AREA:
`LIVING_DOMAIN + SOCIAL_NEWS_COLLECTOR + TO_BE_DOCS`

MODE:
`LOW_RISK_FIX`

PURPOSE FUNCTION:
Create a bounded source list for official/public Living Information evidence.

SUCCESS CRITERIA:
- registry includes source name, URL/domain, category, trust level, and intended use
- tests verify official source classification
- no live fetching

STOP CONDITIONS:
- source requires credentials, private access, or terms-sensitive scraping

VERIFICATION:
- registry unit test

### Task 4: Official/Public Collector Dry-Run Preview

AREA:
`LIVING_DOMAIN + SOCIAL_NEWS_COLLECTOR`

MODE:
`GUARDED_FIX`

PURPOSE FUNCTION:
Preview official/public source collection using mocked or safe HTTP boundaries.

SUCCESS CRITERIA:
- collector can be tested without credentials
- source evidence fields are preserved
- no external publishing

STOP CONDITIONS:
- credentials required
- private/closed source needed
- broad scraping policy unclear

VERIFICATION:
- mocked collector tests

### Task 5: Readiness Reason Aggregation

AREA:
`LIVING_DOMAIN + CONTENT_QUEUE`

MODE:
`LOW_RISK_FIX`

PURPOSE FUNCTION:
Make topic-cluster readiness failure reasons machine-readable.

SUCCESS CRITERIA:
- dry-run diagnostics include reason counts
- tests cover missing primary evidence and readiness below threshold

STOP CONDITIONS:
- readiness thresholds would be loosened without evidence

VERIFICATION:
- service unit tests

## Next Executable Task

Pick Task 1: Read-Only Readiness Diagnostic Endpoint.

It is the highest-priority safe task because it improves operator visibility without changing scheduler, publisher, auth, env, DB schema, or external collection behavior.
