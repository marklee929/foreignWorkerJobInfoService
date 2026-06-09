중복 기사는 LLM 스코어링을 태우지 않는 게 맞다.
다만 현재 DUPLICATE 807건이 전부 같은 의미로 처리되고 있어 데이터 가치가 사라진다.

수정 목표:
DUPLICATE를 단일 상태로 보지 말고 duplicate_type과 duplicate metrics로 세분화해줘.

구분해야 할 것:
1. 같은 검색 사이클에서 같은 URL이 반복 수집된 SEARCH_REPEAT
2. 같은 source_url/canonical_url이 반복된 SAME_URL
3. 같은 제목과 같은 출처의 SAME_TITLE_SAME_SOURCE
4. 같은 제목이지만 다른 출처의 SAME_TITLE_DIFFERENT_SOURCE
5. 다른 출처지만 같은 기사/보도자료를 재송출한 SYNDICATED_COPY
6. 같은 주제지만 내용이 다른 RELATED_TOPIC
7. 같은 주제/사건이고 출처가 다른 SAME_TOPIC_DIFFERENT_SOURCE

정책:
- 중복 row는 LLM scoring을 하지 않는다.
- 중복 row는 대표 후보 representative_candidate_id를 참조한다.
- 중복 row에는 duplicate_type, duplicate_reason, duplicate_risk_score, source_name, source_url, canonical_url, collected_at을 저장한다.
- 대표 후보는 그룹 단위 집계값을 가진다.
  - duplicate_count
  - same_url_count
  - same_title_count
  - same_source_repeat_count
  - different_source_count
  - related_source_count
  - source_diversity_count
  - first_seen_at
  - last_seen_at
  - topic_spread_score

관리자 화면:
- 목록에는 대표 후보만 표시한다.
- 대표 후보 row에 중복 수와 출처 수를 표시한다.
- 상세보기에는 그룹 내부 중복 기사 목록을 표시한다.
- 중복 목록은 duplicate_type별로 분리해서 보여준다.
- 같은 URL 반복과 다른 출처 재송출은 반드시 구분한다.

중요:
DUPLICATE 자체는 버릴 데이터가 아니다.
같은 검색 결과 반복인지, 여러 출처에서 같은 이슈를 다룬 것인지 구분해야 한다.
여러 출처에서 반복되는 기사는 topic importance signal로 사용한다.