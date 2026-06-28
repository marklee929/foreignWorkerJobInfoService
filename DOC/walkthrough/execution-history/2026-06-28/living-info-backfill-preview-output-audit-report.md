# READ_ONLY_AUDIT REPORT: LIVING_INFO Backfill Preview Output

## 1. 결론 요약

- AREA: `LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY`
- MODE: `READ_ONLY_AUDIT`
- PURPOSE FUNCTION: generated `LIVING_INFO` backfill preview output을 검토해 migration/backfill 추천안을 분리
- Decision: `SAFE_TO_PROCEED`
- DB write: NO
- migration execution: NO
- code modification for `TASK 2`: NO
- protected runtime area touched: NO

Preview utility의 원본 분류는 유용하지만 그대로 migration 대상으로 쓰기엔 과하게 넓습니다.

특히 `MIGRATE_NORMALIZED_ITEM` 11건 안에 generic culture/travel/politics/safety 성격의 항목이 섞여 있어, 실제 backfill 전에는 더 엄격한 human-audit recommendation을 적용해야 합니다.

## 2. 읽은 파일

- `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_preview.json`
- `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_preview.csv`
- `SRC/foreign_worker_life_info_collector/storage/generated/living_info/backfill_summary.json`
- `DOC/walkthrough/2026-06-28 - execute prompt.md`
- `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`

## 3. Preview 원본 요약

```json
{
  "total_rows_inspected": 20,
  "action_counts": {
    "DO_NOT_MIGRATE": 1,
    "LOW_VALUE_ARCHIVE": 3,
    "MIGRATE_NORMALIZED_ITEM": 11,
    "NEEDS_MANUAL_REVIEW": 5
  },
  "missing_url_count": 5,
  "already_posted_count": 13,
  "duplicate_skip_count": 0
}
```

Preview category counts:

```text
BANKING_FINANCE: 1
DAILY_LIFE: 5
EDUCATION_LANGUAGE: 1
HEALTHCARE: 2
HOUSING: 4
LOW_VALUE_NOISE: 3
REGIONAL_SUPPORT: 1
SAFETY_SCAM: 2
TRANSPORTATION: 1
```

Preview status counts:

```text
POSTED: 13
ARCHIVED: 5
READY_TO_REVIEW: 1
SCORED: 1
```

## 4. 질문별 답변

### 4.1 How many rows are worth migrating?

Strict recommendation:

- immediate `MIGRATE_NORMALIZED_ITEM`: 2
- `MIGRATE_SOURCE_ITEM`: 4
- `NEEDS_MANUAL_REVIEW` before migration: 3
- not worth migrating now: 11

즉, 20건 중 6건은 source/living evidence로 보존 가치가 있고, 3건은 URL/source 확인 후 조건부 migration 후보입니다.

### 4.2 How many are duplicate/noise?

- exact duplicate by preview output: 0
- low-value/noise after audit: 9
- do-not-migrate after audit: 2

Preview utility에서는 duplicate URL group이 없었지만, 내용 관점에서는 generic travel/culture/politics/economy/local event가 많습니다.

### 4.3 How many have missing URL?

Missing URL rows: 5

```text
124706
109423
60487
44410
25789
```

Missing URL 중 audit상 보존 후보는 `44410` 1건뿐입니다. 나머지는 low-value 또는 target-country mismatch입니다.

### 4.4 How many are low-value travel/culture/local event items?

Preview 기준 `LOW_VALUE_ARCHIVE`: 3

Audit 기준 추가 low-value: 6

총 9건은 public living guide backfill 대상이 아닙니다.

## 5. Audit Recommendation

### 5.1 `MIGRATE_NORMALIZED_ITEM`

현재 기준에서 normalized living item으로 가장 가까운 항목:

```text
109268 - K-Life Choice: Practical Korea Living Guides for Foreign Residents
73215  - Tip of the Day: Get an ARC card to make your life easier in Korea!
```

조건:

- source link 유효성 유지
- public guide 생성 전 source evidence 확인
- official validation이 필요한 법/비자/행정 claim은 별도 확인

### 5.2 `MIGRATE_SOURCE_ITEM`

source evidence로 보존할 가치가 있는 항목:

```text
135992 - Gyeonggi Province moves to close health care gap for uninsured foreign residents
146984 - KB Kookmin launches high-yield savings product for foreign residents
96225  - BI C&S Launches Outdoor AI Voice Kiosk for Multilingual Public Use
35578  - Most foreigners excluded from Korea’s oil-price relief payouts
```

주의:

- `135992`는 healthcare/sensitive 영역이라 normalized guide 전에 official validation 필요
- `146984`는 `effective_url`이 약해서 link validation 필요
- `35578`은 support/benefit 정보로 가치가 있으나 source validation 필요

### 5.3 `NEEDS_MANUAL_REVIEW`

조건부 후보:

```text
44410  - South Korea Imposes Curbs on Foreigners Buying Homes in Seoul
63842  - What foreign voters should know about Korea’s local elections
100747 - Foreign voting rights under strain as information barriers persist
```

판단:

- `44410`: housing relevance는 있으나 URL missing
- `63842`, `100747`: civic/right-to-vote content일 수 있으나 politics/general news와 경계가 있어 living guide로 만들기 전 source/actionability 확인 필요

### 5.4 `LOW_VALUE_ARCHIVE`

생활정보 backfill에서 제외할 항목:

```text
159215 - Korean swimming culture explained: Guide to local pools and etiquette
124706 - Thailand/Seoul travel warning/K-pop ticket scam travel story
95565  - KOSPI Drops Below 9,000 as Foreign Investors Sell Tech Stocks
93993  - From 'Yellow Delinquent' to Fashion Brand Founder
101015 - Foreigners’ favorability toward South Korea hits record high
88143  - Foreign voters in Guro seek economic revival
59380  - 175-Year-Old Shipwreck / island festival story
29290  - Korean Marathon Safety Bill Targets Rising Foreign Runner Numbers
25789  - Seoul happiness index rises, but foreign residents cite hurdles
```

Reason:

- generic culture/travel/event/economy/politics/safety signal
- WorkConnect Korea living guide로 바로 전환하기엔 user actionability가 낮음
- 일부는 signal로는 보존 가능하지만 normalized/public guide 대상은 아님

### 5.5 `DO_NOT_MIGRATE`

명확히 제외:

```text
60487  - Investing in Japan Property: The Ultimate Guide
109423 - Expanded SST to cover more services from July 1, essentials remain tax-free [BTTV]
```

Reason:

- target country mismatch
- Korea settlement/living/work/visa actionability 없음
- missing URL 또는 source trace 약함

## 6. Migration Recommendation

권장 순서:

1. 먼저 `MIGRATE_SOURCE_ITEM` 4건과 `MIGRATE_NORMALIZED_ITEM` 2건만 migration candidate로 검토
2. `NEEDS_MANUAL_REVIEW` 3건은 URL/source/actionability 확인 전 insert 금지
3. `LOW_VALUE_ARCHIVE` 9건과 `DO_NOT_MIGRATE` 2건은 backfill insert 대상에서 제외
4. `POSTED` 상태였던 과거 row도 그대로 normalized migration하지 말고 source evidence로만 제한

권장 allowed action set for manual/dev backfill:

```text
MIGRATE_NORMALIZED_ITEM:
- 109268
- 73215

MIGRATE_SOURCE_ITEM:
- 135992
- 146984
- 96225
- 35578
```

Manual review before insert:

```text
44410
63842
100747
```

## 7. Preview Utility 개선 후보

현재 utility는 deterministic first-pass로 충분하지만, 다음 보정이 필요합니다.

- `MIGRATE_NORMALIZED_ITEM` 조건을 더 엄격하게 조정
- `source_reliability_score`가 낮고 source is `UNKNOWN`이면 normalized migration 대신 `MIGRATE_SOURCE_ITEM` 또는 `NEEDS_MANUAL_REVIEW`
- category가 `housing`이어도 title/body가 festival, politics, generic culture이면 `LOW_VALUE_ARCHIVE`
- `POSTED` row를 자동으로 normalized migration하지 말고 별도 flag 처리
- URL이 `articleView.html?idxno`처럼 약한 경우 `NEEDS_MANUAL_REVIEW`
- civic/politics 항목은 `CIVIC_RIGHTS_REVIEW` 같은 별도 reason 필요

## 8. Queue-Drain Rule 반영

사용자가 “전체 task 완료까지 진행”을 명시한 경우를 위해 `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`에 queue-drain override를 추가했습니다.

적용 원칙:

- 기본은 one queued task per user turn
- 사용자가 명시하면 sequential execution 가능
- 단, explicit approval/precondition/protected area에서는 정지
- marker는 실행된 마지막 task와 첫 pending task 사이에 유지

이번 run에서는 `TASK 3`이 migration 실행 precondition을 요구하므로 queue-drain을 더 진행하지 않았습니다.

## 9. 재시작 / 재로딩 필요 여부

- Backend restart:
  - NO
  - 이유: runtime backend code 변경 없음

- Frontend dev server restart:
  - NO
  - 이유: Admin UI 변경 없음

- Browser hard refresh:
  - NO
  - 이유: UI 변경 없음

- DB restart:
  - NO
  - 이유: DB schema/migration/data mutation 없음

- Scheduler/Bot restart:
  - NO
  - 이유: scheduler/bot runtime 변경 없음

- External service restart:
  - NO
  - 대상: 없음
  - 이유: external API behavior 변경 없음

- 사용자가 직접 해야 할 작업:
  1. `TASK 3` migration 실행 여부를 명시적으로 승인할지 결정
  2. 위 candidate ID 목록 중 실제 backfill 허용 범위를 확정

## 10. 보호영역 확인

Not touched:

- DB write
- migration execution
- Facebook publisher
- content publisher
- scheduler
- Telegram runtime behavior
- auth/env/config
- external API behavior
- actual publish/collection execution

## 11. Stop Gate

Queue-drain execution은 `TASK 3` 앞에서 중단했습니다.

Reason:

`TASK 3` requires explicit user approval before applying `living_info` migration to local PostgreSQL.

Current marker should remain immediately before:

```text
## TASK 3: Apply `living_info` Migration Only After Explicit Approval
```
