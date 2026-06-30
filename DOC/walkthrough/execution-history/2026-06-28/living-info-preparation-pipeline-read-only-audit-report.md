# READ_ONLY_AUDIT REPORT: Living Info Preparation Pipeline

## 1. 결론

- Final status: `READ_ONLY_AUDIT_COMPLETE_PARTIAL`
- 현재 `living_info.topic_cluster -> content.content_candidate READY_TO_REVIEW` 경로는 서비스 내부에 구현되어 있습니다.
- 하지만 `sync_all()`, scheduler, command/API, Admin UI entrypoint에는 아직 연결되어 있지 않습니다.
- 따라서 현재 상태는 `manually callable only`이며 운영 파이프라인 기준으로는 `partially connected`입니다.
- 이번 작업은 감사 전용입니다. 파일/코드/DB/runtime 변경은 하지 않았습니다.

## 2. Current connected path

현재 구현된 내부 경로:

```text
ContentService.sync_living_info()
-> LivingInfoService.list_ready_topic_clusters()
-> LivingInfoRepository.list_ready_topic_clusters()
-> LivingInfoService.topic_cluster_evidence()
-> LivingInfoRepository.topic_cluster_evidence()
-> LivingInfoService.topic_cluster_to_content_candidate_payload()
-> ContentRepository.upsert_candidate()
-> content.content_candidate
```

관련 파일과 함수:

- `SRC/foreign_worker_life_info_collector/content/service.py`
  - `ContentService.sync_living_info()`
  - `ContentService.sync_all()`
- `SRC/foreign_worker_life_info_collector/living_info/service.py`
  - `LivingInfoService.topic_cluster_to_content_candidate_payload(...)`
  - `topic_cluster_to_content_candidate_payload(...)`
- `SRC/foreign_worker_life_info_collector/living_info/repository.py`
  - `LivingInfoRepository.list_ready_topic_clusters(...)`
  - `LivingInfoRepository.topic_cluster_evidence(...)`
- `SRC/foreign_worker_life_info_collector/content/repository.py`
  - `ContentRepository.upsert_candidate(...)`

생성 payload identity:

```text
raw_ref_table = "living_info.topic_cluster"
raw_ref_id = topic_cluster.id
source_domain = "LIVING_INFO"
content_type = "LIVING_GUIDE"
status = "READY_TO_REVIEW"
review_required_yn = True
```

## 3. Missing path

자동 준비 파이프라인으로 보기 위해 빠진 연결:

- `ContentService.sync_all()`은 현재 `sync_social_news()`와 `sync_immigration()`만 호출합니다.
- `ContentService.sync_all()`은 `sync_living_info()`를 호출하지 않습니다.
- `run_content_generation_cycle()`은 `content_service().sync_all(limit=500)`만 호출합니다.
- `run_content_bot_loop()`는 `run_content_generation_cycle(...)`만 반복합니다.
- `/api/admin/content/sync`는 `content_service().sync_all(...)`만 호출합니다.
- Admin UI `syncContentCandidates()`는 `/api/admin/content/sync`만 호출합니다.
- `sync_living_info()`를 직접 호출하는 API/command/scheduler entrypoint는 발견되지 않았습니다.
- `living_info.source_item / normalized_item`에서 `topic_cluster / topic_cluster_item`를 만드는 clusterer 운영 경로도 아직 보이지 않습니다.

## 4. Ready-to-review 가능 여부

가능합니다. 조건은 아래와 같습니다.

`LivingInfoRepository.list_ready_topic_clusters(...)` 기준:

```text
public_candidate_ready_yn = 'Y'
validation_status IN ('VALIDATED', 'READY')
cluster_status IN ('OPEN', 'READY')
readiness_score >= 60
source_count >= 1
evidence_count >= 1
```

`LivingInfoRepository.topic_cluster_evidence(...)`는 아래 join을 사용합니다.

```text
living_info.topic_cluster_item
-> living_info.normalized_item
-> living_info.source_item
```

따라서 `source_signal_id`만 있는 community-only cluster는 evidence-backed content candidate로 승격되지 않습니다.

테스트 근거:

- `SRC/foreign_worker_life_info_collector/tests/test_content_sync_living_info.py`
  - ready cluster가 `content.content_candidate READY_TO_REVIEW`로 변환되는 테스트 존재
  - unready payload가 candidate 생성 없이 skip되는 테스트 존재

## 5. Risk areas

구현 단계에서 보호영역에 닿을 수 있는 지점:

- `scheduler`: 20m/1h 자동 연결은 `SCHEDULER_BOT_STATE` 보호영역입니다.
- `content publisher`: 자동 publish selection과 연결하면 보호영역입니다.
- `FacebookPublisher`: 이번 경로와 분리해야 합니다.
- `Telegram runtime/callback`: review 발송 시점이 바뀔 수 있으므로 별도 승인 필요합니다.
- `sync_all()`: 바로 연결하면 `/api/admin/content/sync`와 content bot loop 동작이 즉시 바뀝니다.
- `topic_clusterer`: 아직 운영 경로가 없어 `sync_living_info()`만 연결하면 처리 대상 cluster가 없을 수 있습니다.

## 6. CODE_TASK_CANDIDATE

### 1단계: manual/admin-only content preparation 연결

```text
AREA: CONTENT_QUEUE + LIVING_DOMAIN + ADMIN_UI
MODE: GUARDED_FIX
PURPOSE FUNCTION:
Allow operators to manually prepare ready living_info.topic_cluster rows as content.content_candidate READY_TO_REVIEW without scheduler or publisher changes.

FOCUS:
Add an admin-only/manual API endpoint that calls ContentService.sync_living_info() and returns seen/synced/skipped counts.

ALLOWED CHANGES:
- add explicit admin API endpoint
- add apiClient function
- optionally add admin UI button/status display
- tests for endpoint/service call

FORBIDDEN CHANGES:
- scheduler changes
- Facebook publisher changes
- content publisher changes
- Telegram runtime/callback changes
- auth/env/secrets changes
- DB migration
- auto publish

VERIFICATION:
- endpoint calls sync_living_info()
- sync_all() remains unchanged
- ready cluster creates READY_TO_REVIEW only
- community-only cluster is skipped
- no Facebook/Telegram send occurs from this endpoint

STOP CONDITIONS:
- implementation requires scheduler modification
- implementation requires publisher modification
- implementation requires auth/env changes
```

### 2단계: 승인 후 20m/1h scheduler 연결

```text
AREA: LIVING_DOMAIN + CONTENT_QUEUE + SCHEDULER_BOT_STATE
MODE: PROTECTED_CHANGE
PURPOSE FUNCTION:
Connect living_info preparation into an approved timed content-preparation pipeline after manual path is verified.

FOCUS:
Run living_info topic clustering/preparation on an approved interval, then prepare READY_TO_REVIEW content candidates without publishing.

ALLOWED CHANGES:
- scheduler wiring only after explicit approval
- interval config for living_info preparation
- operational logs
- duplicate/suppression guard

FORBIDDEN CHANGES:
- Facebook publisher changes
- content publisher auto publish
- Telegram callback changes
- auth/env/secrets changes
- destructive DB migration

VERIFICATION:
- scheduler calls only preparation, not publish
- generated content candidates remain READY_TO_REVIEW
- Telegram/Facebook output does not occur unless existing review flow explicitly handles candidates later
- logs show seen/synced/skipped counts

STOP CONDITIONS:
- approval for scheduler is missing
- publisher behavior must change
- topic_cluster ownership remains unresolved
```

## 7. 최종 판정

`READ_ONLY_AUDIT_COMPLETE_PARTIAL`

서비스 내부 준비는 되어 있지만 운영 파이프라인은 아직 연결되지 않았습니다. 다음 안전한 구현은 scheduler가 아니라 manual/admin-only `sync_living_info()` trigger입니다.

## 8. Closeout

- Runtime/code changes: NO
- DB/migration changes: NO
- Scheduler changes: NO
- Facebook publisher changes: NO
- Content publisher changes: NO
- Telegram runtime/callback changes: NO
- Auth/env/secrets changes: NO
- External API behavior changes: NO
- execute prompt updated: YES
- `[WC_EXECUTION_COMPLETE]` exact count: 1
- legacy decorated Korean completion marker count: 0
- loose completion marker count: 0
- final line is `[WC_EXECUTION_COMPLETE]`: YES
