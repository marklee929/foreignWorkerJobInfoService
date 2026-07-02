# Living Info Autonomous Pipeline Audit

## 1. 결론

- 판정: `SAFE_TO_IMPLEMENT_MANUAL_PIPELINE_RECONNECT`
- 가장 이른 실패 계층: `Admin UI manual trigger`
- 직접 원인: `ContentManagementPage.vue`의 `Living info prepare` 버튼이 topic cluster 준비 사이클이 아니라 `POST /api/admin/content/living-info/sync`만 호출합니다.
- 결과: `living_info.normalized_item`이 있어도 `living_info.topic_cluster`가 준비되지 않으면 `content.content_candidate`가 만들어지지 않고, 그 다음 단계인 card preview / Telegram review까지 도달하지 못합니다.

## 2. 현재 파이프라인

```text
social_news.candidate
-> ContentService.sync_social_news()
-> source_domain == LIVING_INFO
-> LivingInfoService.ingest_from_social_news_candidate()
-> living_info.source_item
-> living_info.normalized_item
-> LivingInfoService.prepare_topic_clusters()
-> living_info.topic_cluster
-> ContentService.sync_living_info()
-> content.content_candidate READY_TO_REVIEW
-> ContentService.review_targets()
-> send_content_review_to_telegram()
-> build_content_card_preview()
-> content.publish_log telegram_review
```

## 3. 증거

- `ContentService.sync_social_news()`는 `LIVING_INFO` row를 `content.content_candidate`에 직접 넣지 않고 `LivingInfoService.ingest_from_social_news_candidate()`로 보냅니다.
- `ContentService.sync_living_info()`는 이미 준비된 `living_info.topic_cluster`만 읽습니다.
- `run_living_info_content_prep_cycle(dry_run=False)`는 `prepare_living_info_topic_clusters()` 후 `sync_living_info()`를 실행합니다.
- `POST /api/admin/content/living-info/prep-cycle`은 이미 존재하며 기본값은 `dryRun=true`입니다.
- `ContentManagementPage.vue`의 `syncLivingInfo()`는 `syncLivingInfoContentCandidates()`만 호출합니다.
- `syncLivingInfoContentCandidates()`는 `/api/admin/content/living-info/sync`만 호출합니다.

## 4. 왜 Telegram 카드가 운영자에게 안 갔는가

- card preview 생성은 `send_content_review_to_telegram()` 안에서만 자동 실행됩니다.
- Telegram review 대상은 `content.content_candidate`의 `LIVING_INFO` / `IMMIGRATION_INFO` 후보입니다.
- `Living info prepare` 버튼이 cluster 준비를 하지 않으면 `content.content_candidate` 자체가 부족합니다.
- content bot의 `run_content_generation_cycle()`은 `sync_all()`을 통해 social news / immigration만 동기화합니다.
- 생활정보 준비 스케줄러는 `LIVING_INFO_CONTENT_PREP_ENABLED=false`가 기본값이라 자동 실행되지 않습니다.

## 5. 보호영역 판정

- scheduler 자동 실행 정책 변경: 보호영역
- production Telegram 자동 발송 흐름 변경: 보호영역
- Facebook publisher 변경: 보호영역
- DB migration/mutation 직접 실행: 보호영역

## 6. 구현 가능한 안전 작업

1. Admin UI의 `Living info prepare` 버튼을 기존 `/api/admin/content/living-info/prep-cycle`로 연결합니다.
2. 요청 payload는 `{ limit: 100, dryRun: false }`로 하여 수동 클릭 시 cluster 준비와 candidate sync를 한 번에 실행합니다.
3. 기존 `/api/admin/content/living-info/sync` endpoint는 유지합니다.
4. 실제 Telegram 전송은 하지 않습니다.
5. 기존 bulk card preview 버튼은 유지합니다.
6. 테스트는 frontend API client와 UI contract 중심으로 보강합니다.

## 7. CODE_TASK_CANDIDATE

CODE_TASK_CANDIDATE
AREA: `LIVING_DOMAIN + CONTENT_QUEUE`
MODE: `LOW_RISK_FIX`
FOCUS: Connect Admin UI Living info prepare action to the existing prep-cycle endpoint.
WHY: Current UI runs only sync, so topic clusters are not prepared before content candidate sync.
RISK: Manual click will write topic clusters and content candidates when operator chooses the action; no scheduler or external send changes.
PROTECTED AREA: scheduler, production Telegram behavior, Facebook publisher, auth/env/secrets, migration.
FILES LIKELY INVOLVED:
- `SRC/foreign_worker_life_info_collector/admin_ui/src/services/apiClient.js`
- `SRC/foreign_worker_life_info_collector/admin_ui/src/views/ContentManagementPage.vue`
- `SRC/foreign_worker_life_info_collector/tests/test_living_info_manual_sync_endpoint_contract.py`
RECOMMENDED NEXT PROMPT: Implement the manual Living info prep-cycle UI connection without changing scheduler or Telegram production behavior.

## 8. 재시작 / 재로딩 필요 여부

- Backend restart: NO
  - 이유: 이 audit 단계에서는 runtime code를 수정하지 않았습니다.
- Frontend dev server restart: NO
  - 이유: 이 audit 단계에서는 Admin UI code를 수정하지 않았습니다.
- Browser hard refresh: NO
  - 이유: UI 변경이 없습니다.
- DB restart: NO
  - 이유: DB schema/migration 변경이 없습니다.
- Scheduler/Bot restart: NO
  - 이유: scheduler/publisher/bot runtime을 수정하지 않았습니다.
- Ollama restart: NO
  - 이유: Ollama 관련 변경이 없습니다.
