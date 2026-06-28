# READ_ONLY_AUDIT REPORT: `sync_living_info()` Content Candidate Path

## 1. Pre-Review

- AREA: `LIVING_DOMAIN + CONTENT_QUEUE`
- MODE: `READ_ONLY_AUDIT`
- PURPOSE FUNCTION: WorkConnect helps foreign workers, residents, students, migrants, and movers reduce uncertainty through practical, source-backed work-and-settlement information.
- Risk: MEDIUM
- Decision: `SAFE_TO_PROCEED`
- Protected areas touched: NO
- Runtime/code changes: NO
- DB writes: NO
- Files inspected:
  - `SRC/foreign_worker_life_info_collector/storage/db/migrations/2026_06_28_living_info.sql`
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/content/repository.py`
  - `SRC/foreign_worker_life_info_collector/living_info/repository.py`
  - `SRC/foreign_worker_life_info_collector/living_info/models.py`
  - `SRC/foreign_worker_life_info_collector/living_info/service.py`

## 2. 현재 연결 상태

- `TASK 6` 이후 `social_news.candidate`의 living-classified row는 더 이상 직접 `content.content_candidate`로 들어가지 않습니다.
- living row는 `LivingInfoService.ingest_from_social_news_candidate(...)`를 통해:
  - `living_info.source_item`
  - `living_info.normalized_item`
  로 적재됩니다.
- 아직 `living_info.topic_cluster -> content.content_candidate` 승격 경로는 없습니다.
- `content.content_candidate`는 `raw_ref_table, raw_ref_id` unique contract를 이미 가지고 있어 `raw_ref_table = 'living_info.topic_cluster'` 방식과 맞습니다.

## 3. 필요한 readiness fields

`sync_living_info()`가 public 후보를 만들려면 `living_info.topic_cluster`에서 최소 아래 조건을 만족해야 합니다.

- `public_candidate_ready_yn = 'Y'`
- `validation_status IN ('VALIDATED', 'READY')`
- `cluster_status IN ('OPEN', 'READY')`
- `readiness_score >= 60`
- `evidence_count >= 1`
- `source_count >= 1`
- `topic_key` not empty
- `primary_category` not empty
- `community_signal_count`만 있고 `evidence_count = 0`인 cluster는 제외

권장 강한 조건:

- `official_source_count >= 1`이면 우선 승격 가능
- `secondary_source_count >= 1`이고 `source_spread_count >= 2`이면 승격 가능
- `community_signal_count > 0`은 가산 신호일 뿐 단독 승격 사유가 되면 안 됩니다.

## 4. `raw_ref_table = 'living_info.topic_cluster'` 설계

`content.content_candidate` payload는 아래 identity를 사용해야 합니다.

```text
raw_ref_table = "living_info.topic_cluster"
raw_ref_id = living_info.topic_cluster.id
source_domain = "LIVING_INFO"
content_type = "LIVING_GUIDE"
```

기존 `ContentRepository.upsert_candidate(payload)`는 `ON CONFLICT (raw_ref_table, raw_ref_id)`를 사용하므로 같은 topic cluster가 반복 승격되어도 동일 content candidate를 update합니다.

## 5. Telegram/card preview에 필요한 payload fields

`sync_living_info()`가 생성할 payload는 최소 아래 필드를 포함해야 합니다.

- `source_domain`: `LIVING_INFO`
- `content_type`: `LIVING_GUIDE`
- `priority_group`: `LIVING_INFO`
- `category`: `topic_cluster.primary_category`
- `title`: 영어 guide title
- `summary_en`: source-backed practical summary
- `why_it_matters_en`: foreign residents in Korea 관점 이유
- `body_en`: 3개 내외의 practical check text
- `source_url`: 대표 evidence URL
- `link_url`: 대표 evidence URL
- `source_name`: 대표 evidence source name
- `hashtags`: `#LivingInKorea #ForeignersInKorea #KoreaLife #WorkConnectKorea`
- `quality_score`, `practical_value_score`, `source_reliability_score`, `final_publish_score`
- `review_required_yn`: `true`
- `status`: `READY_TO_REVIEW`
- `raw_payload`: topic cluster evidence summary

Telegram/card preview가 안정적으로 동작하려면 대표 evidence는 `living_info.source_item`에서 가져와야 합니다.

## 6. Community-only signal 차단 기준

아래 조건이면 `content.content_candidate`를 만들면 안 됩니다.

- `evidence_count = 0`
- `official_source_count = 0`
- `secondary_source_count = 0`
- `community_signal_count > 0`
- topic cluster item이 `source_signal_id`만 있고 `normalized_item_id`가 없음

처리:

- `living_info.topic_cluster`에는 남길 수 있습니다.
- `content.content_candidate`로 승격하지 않습니다.
- 필요하면 추후 `WATCH_TOPIC_ONLY` 또는 `COMMUNITY_SIGNAL_ONLY` reason을 raw payload에 기록합니다.

## 7. 권장 repository/service 확장

`LivingInfoRepository`에 추가할 read-only method:

```text
list_ready_topic_clusters(limit: int = 100) -> list[dict]
topic_cluster_evidence(topic_cluster_id: int) -> list[dict]
```

`LivingInfoService`에 추가할 method:

```text
topic_cluster_to_content_candidate_payload(cluster: dict, evidence: list[dict]) -> dict
```

`ContentService`에 추가할 method:

```text
sync_living_info(limit: int = 100) -> dict
```

`sync_all()` 포함 여부:

- 첫 구현에서는 `sync_all()`에 포함하지 않는 것이 안전합니다.
- 명시 호출로 검증한 뒤 `sync_all()` 포함 여부를 별도 결정해야 합니다.

## 8. 추천 생성 상태

초기 구현에서는 자동 publish 후보가 아니라 운영 검토 후보로만 생성해야 합니다.

```text
status = "READY_TO_REVIEW"
review_required_yn = True
sensitive_yn = False
```

이유:

- living guide는 자체 정리 콘텐츠 성격이 강합니다.
- 실제 Facebook 게시 전에는 Telegram/Admin review가 필요합니다.
- community/trend signal이 섞일 수 있으므로 자동 공개하면 안 됩니다.

## 9. 필요한 payload 생성 규칙

대표 title:

```text
{Human-readable category} checklist for foreign residents in Korea
```

예:

- `Healthcare checklist for foreign residents in Korea`
- `Housing checklist for foreign residents in Korea`

대표 summary:

- 대표 `living_info.source_item.raw_summary`를 우선 사용합니다.
- 없으면 topic metadata 기반 deterministic summary를 만듭니다.

`why_it_matters_en`:

- `This topic can affect daily life, paperwork, payments, housing, healthcare, or local support for foreign residents in Korea.`

`body_en`:

- 공식/신뢰 source 확인
- 본인 visa/city/household 조건 확인
- 변경 가능성 때문에 source 재확인

## 10. 위험 분석

- `topic_cluster` 생성 로직이 아직 없어 실제 ready cluster가 없을 수 있습니다.
- `content_candidate` 승격은 가능하지만 evidence join이 없으면 링크/출처 품질이 약해질 수 있습니다.
- community-only signal이 실수로 승격되면 WorkConnect 목적을 해칩니다.
- `sync_all()`에 바로 포함하면 운영자가 예상하지 못한 후보가 생길 수 있습니다.
- 카드 preview 생성은 별도 guardrail이 있으므로 여기서는 직접 호출하지 않는 편이 안전합니다.

## 11. Implementation Gate

`TASK 8`은 아래 제한을 만족하면 진행 가능합니다.

- `FacebookPublisher` 수정 없음
- scheduler 수정 없음
- Telegram callback/runtime 수정 없음
- community-only cluster 차단
- `content.content_candidate` 생성은 `READY_TO_REVIEW`까지만
- `sync_all()` 자동 연결 없음
- destructive DB 변경 없음

## 12. 재시작 / 재로딩 필요 여부

- Backend restart: NO
  - 이유: 이번 TASK 7은 `READ_ONLY_AUDIT` 보고서만 작성했습니다.
- Frontend dev server restart: NO
  - 이유: Admin UI 파일은 수정하지 않았습니다.
- Browser hard refresh: NO
  - 이유: UI 변경이 없습니다.
- DB restart: NO
  - 이유: DB schema/migration 변경이 없습니다.
- Scheduler/Bot restart: NO
  - 이유: scheduler/bot runtime을 수정하지 않았습니다.
- External service restart: NO
  - 대상: Telegram/Facebook/Ollama
  - 이유: 외부 연동 코드를 수정하지 않았습니다.
- 사용자가 직접 해야 할 작업:
  1. 없음

## 13. Final Recommendation

`sync_living_info()`는 구현 가능하지만, 첫 버전은 명시 호출 전용이어야 합니다. `sync_all()` 또는 scheduler에 연결하지 말고, `living_info.topic_cluster` 중 evidence-backed ready cluster만 `content.content_candidate`의 `READY_TO_REVIEW` 후보로 올리는 방식이 안전합니다.
