# PHASE 3 Living Info Topic Cluster Result

## 1. 결론
- PHASE 3 `Topic Cluster Creation / Update Path` 완료.
- `living_info.normalized_item`을 `living_info.topic_cluster` / `living_info.topic_cluster_item`로 묶는 deterministic preparation path를 추가했다.
- community-only signal은 factual evidence로 사용하지 않는다.
- DB migration, scheduler, Facebook publisher, Telegram runtime behavior는 변경하지 않았다.

## 2. 수정 파일
- `SRC/foreign_worker_life_info_collector/living_info/repository.py`
- `SRC/foreign_worker_life_info_collector/living_info/service.py`
- `SRC/foreign_worker_life_info_collector/content/service.py`
- `SRC/foreign_worker_life_info_collector/api/admin_server.py`
- `SRC/foreign_worker_life_info_collector/tests/test_living_info_service.py`
- `SRC/foreign_worker_life_info_collector/tests/test_living_info_manual_sync_endpoint_contract.py`

## 3. 구현 내용
- `LivingInfoRepository.list_normalized_items_for_clustering`
  - `living_info.normalized_item` + `living_info.source_item` join 기반 source evidence 조회.
  - `TOPIC_CLUSTER_MATERIAL`, `SOURCE_EVIDENCE`만 사용.
  - `topic_key_candidate`가 없는 항목과 비활성 source는 제외.

- `LivingInfoRepository.upsert_topic_cluster_item_normalized`
  - 기존 partial unique index `ux_living_topic_cluster_item_normalized`를 사용해 normalized evidence link를 upsert.

- `LivingInfoService.prepare_topic_clusters`
  - 기본 `dry_run=True`.
  - `topic_key_candidate`, `normalized_primary_category`, `target_user`, `action_type` 기준 grouping.
  - `source_count`, `evidence_count`, `official_source_count`, `secondary_source_count`, `source_spread_count` 계산.
  - `readiness_score`, `validation_status`, `public_candidate_ready_yn`, `cluster_status` 계산.
  - `community_signal_count=0`으로 유지해서 community signal을 factual evidence로 섞지 않음.

- `ContentService.prepare_living_info_topic_clusters`
  - Admin route에서 living info cluster preparation을 호출할 수 있는 thin wrapper.

- `POST /api/admin/content/living-info/prepare-clusters`
  - 기본 dry-run.
  - `{"execute": true}`가 있을 때만 기존 living_info topic cluster tables에 저장.
  - Telegram/Facebook/publisher/scheduler 호출 없음.

## 4. 검증 결과
- py_compile 성공:
  - `foreign_worker_life_info_collector\living_info\repository.py`
  - `foreign_worker_life_info_collector\living_info\service.py`
  - `foreign_worker_life_info_collector\content\service.py`
  - `foreign_worker_life_info_collector\api\admin_server.py`
  - 관련 테스트 파일

- pytest 성공:
  - command: `python -m pytest foreign_worker_life_info_collector\tests\test_living_info_service.py foreign_worker_life_info_collector\tests\test_living_info_manual_sync_endpoint_contract.py foreign_worker_life_info_collector\tests\test_content_sync_living_info.py -q`
  - result: `15 passed in 0.07s`

## 5. 보호영역 확인
- DB/migration: 변경 없음
- scheduler: 변경 없음
- Facebook publisher/content publisher: 변경 없음
- Telegram runtime/callback: 변경 없음
- auth/env/secrets: 변경 없음
- 실제 수집/게시/external API: 실행 없음

## 6. 다음 PHASE 진행 판단
- PHASE 3 성공 기준 충족.
- PHASE 4는 scheduler 영역이므로 disabled-by-default, manual-safe, no publish 조건으로만 진행 가능.
