# READ_ONLY_AUDIT REPORT: LIVING_INFO Source Spectrum Expansion Research

## 1. Pre-Review

- AREA: `LIVING_DOMAIN + DATA_SOURCE_QUALITY + SOCIAL_NEWS_COLLECTOR + SOCIAL_NEWS_CANDIDATE + CONTENT_QUEUE`
- MODE: `READ_ONLY_AUDIT`
- Risk: LOW
- Protected areas touched: NO
- Files inspected:
  - `CODEX_BOOTSTRAP.md`
  - `DOC/architecture/00_PRODUCT_NORTH_STAR.md`
  - `DOC/architecture/01_SYSTEM_GROWTH_WORKFLOW.md`
  - `DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md`
  - `DOC/architecture/03_SYSTEM_ARCHITECTURE.md`
  - `DOC/architecture/05_CODEX_HARNESS_GUIDE.md`
  - `DOC/architecture/06_WORK_AREA_REGISTRY.md`
  - `DOC/walkthrough/2026-06-27 - execute prompt.md`
  - `DOC/walkthrough/execution-history/2026-06-20/living-info-topic-card-read-only-audit-report.md`
  - `DOC/walkthrough/execution-history/2026-06-20/living-info-card-generation-guardrail-report.md`
  - `DOC/walkthrough/execution-history/2026-06-21/official-notice-attachment-review-guardrail-report.md`
  - `DOC/walkthrough/execution-history/2026-06-21/workconnect-duplicate-review-publish-pipeline-audit.md`
  - `SRC/foreign_worker_life_info_collector/content/service.py`
  - `SRC/foreign_worker_life_info_collector/content/repository.py`
  - `SRC/foreign_worker_life_info_collector/social/news/category_rotation.py`
  - `SRC/foreign_worker_life_info_collector/social/news/pipeline.py`
  - `SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py`
- Research method:
  - 기존 architecture / walkthrough / source code read-only inspection
  - 공개 웹 페이지 기반 source discovery
  - collector 실행 없음
  - DB 조회/변경 없음
  - 외부 알림/게시 없음
- External research performed: YES, public website review only
- Runtime/code changes: NO

## 2. Current Problem Definition

현재 `LIVING_INFO / LIVING_GUIDE`가 충분히 유용한 결과로 이어지지 않는 이유는 수집량 부족 하나가 아니라 source shape 문제다.

현재 흐름은 `social_news.candidate`가 `housing`, `banking`, `healthcare`, `transportation`, `insurance`, `korean_language`, `cost_of_living`, `local_community`, `education`, `settlement_life` 등으로 분류되면 `source_domain = LIVING_INFO`, `content_type = LIVING_GUIDE`로 변환할 수 있다. 그러나 최근 guardrail은 단일 뉴스 기사나 attachment-only notice가 곧바로 public-style card preview가 되는 것을 막는다. 이 방향은 맞다.

그 결과 지금 필요한 것은 더 많은 단일 기사 수집이 아니라 다음 구조다.

```text
broad source discovery
-> source evidence
-> source signal
-> topic_key / target_user / action_type tagging
-> fact point extraction
-> topic cluster
-> source-backed guide/card candidate
-> Telegram review
-> manual approval
```

현재 병목은 아래 세 가지다.

- living source pool이 뉴스/RSS/search 중심으로 기울어져 있다.
- community/blog/forum pain point는 `source_signal`로 쓸 수 있지만 아직 별도 inventory와 정책이 약하다.
- official/semi-official validation source가 topic cluster와 연결되지 않아 card candidate가 만들 근거가 부족하다.

## 3. Existing Source Coverage Summary

현재 확인된 구조:

- `social_news/category_rotation.py`
  - `SECONDARY_CATEGORIES`: `housing`, `banking`, `healthcare`, `transportation`, `insurance`, `korean_language`, `cost_of_living`, `local_community`, `education`, `settlement_life`
  - `TERTIARY_CATEGORIES`: `travel`, `lifestyle`, `culture`, `local_events`, `safety`
  - `SEARCH_KEYWORDS["SECONDARY"]`는 생활정보 키워드를 일부 포함한다.
- `content/service.py`
  - `social_news_payload()`에서 생활 카테고리는 `LIVING_INFO / LIVING_GUIDE`로 매핑된다.
  - `is_living_content()`는 `SECONDARY`, `TERTIARY` 그룹까지 생활정보로 볼 수 있다.
- `content/repository.py`
  - Telegram Review 대상은 `source_domain IN ('LIVING_INFO', 'IMMIGRATION_INFO')` 중심이다.
- `utils/content_card_renderer.py`
  - 단일 `social_news.*` 기반 `LIVING_INFO / LIVING_GUIDE`는 `topic_key`, `topic_cluster_id`, `fact_point_id`, `card_point_id`, `source_spread_count`, `usable_point_count` 같은 evidence가 없으면 card preview를 만들지 않는다.

현재 강점:

- 뉴스/기사형 item이 무분별하게 카드 이미지로 승격되는 것을 막고 있다.
- `community source = user-need signal`이라는 architecture 원칙이 이미 존재한다.
- `same URL repeat = noise`, `same topic across reliable sources = signal`이라는 duplicate policy가 존재한다.

현재 부족한 점:

- living source inventory가 없다.
- official validation source와 community pain point를 묶는 `topic_key`가 없다.
- `source_signal_type`, `target_user`, `action_type`, `pain_point`, `validation_needed`, `validation_source_url`이 없다.
- `travel`, `lifestyle`, `culture`, `local_events`가 너무 넓어 일반 여행/라이프스타일 뉴스가 생활정보로 섞일 위험이 있다.
- 영어권 외 community뿐 아니라 베트남어, 태국어, 인도네시아어, 네팔어, 몽골어, 러시아어/우즈베크어권 pain point 탐색 전략이 아직 약하다.

## 4. Living Information Category Map

| category | user problem | likely source type | community signal useful | official validation required | content/card potential |
|---|---|---|---|---|---|
| `housing` | 전월세, 보증금, 계약서, 기숙사, 주소 이전 | local government, legal aid, housing guides, community | YES | YES | HIGH |
| `healthcare` | 건강보험, 병원 이용, 응급실, 보험료 체납 | `NHIS`, hospitals, public health offices | YES | YES | HIGH |
| `insurance` | 건강보험/국민연금/산재보험 적용 | `NHIS`, `NPS`, `COMWEL`, labor support | YES | YES | HIGH |
| `banking` | 계좌개설, 송금, 인증, 수수료 | banks, FSS, support centers | YES | YES | HIGH |
| `telecom` | SIM, 본인인증, 약정, 번호이동 | telecom official pages, support centers | YES | YES | HIGH |
| `transportation` | 교통카드, 운전면허, 국제면허, 대중교통 | police/road authority/local guides | YES | YES | MEDIUM |
| `public_services` | 주민센터, 외국인등록, 민원, 120/1345 | local government, HiKorea, call centers | YES | YES | HIGH |
| `labor_rights` | 임금체불, 계약서, 산재, 퇴직금 | MOEL, labor centers, NGOs | YES | YES | HIGH |
| `visa_adjacent_life` | 체류지 변경, 가족 초청, 서류 준비 | HiKorea, immigration support centers | YES | YES | HIGH |
| `childcare_school` | 다문화가족, 자녀 학교, 돌봄 | Danuri, education offices, local centers | YES | YES | MEDIUM |
| `korean_language` | 무료 한국어 수업, TOPIK, 지역 수업 | Danuri, global centers, universities | YES | NO/LOW | MEDIUM |
| `legal_aid` | 법률상담, 체류/임금/계약 분쟁 | KLAC, labor/immigration counseling | YES | YES | HIGH |
| `scam_fraud` | 보이스피싱, 임대 사기, 취업 사기 | police, FSS, support centers | YES | YES | HIGH |
| `emergency_safety` | 응급전화, 재난문자, 폭염/한파, 안전 | local government, Safe Korea | YES | YES | MEDIUM |
| `regional_support` | 지역별 외국인 주민 지원사업 | local governments/global centers | YES | YES | HIGH |
| `daily_life_howto` | 쓰레기, 공과금, 택배, 생활 규칙 | local government, community, blogs | YES | MEDIUM | MEDIUM |

## 5. International / Foreigner Community Source Candidates

커뮤니티는 source-backed fact가 아니라 user-need signal로만 써야 한다. 직접 인용이나 개인 사례 재게시 금지, 개인정보 저장 금지, 법률/비자/의료/금융 주장은 official/secondary source validation 전 public content 금지다.

| source | URL/search query | language | target user | category coverage | source type | access method | risks | recommended use | priority |
|---|---|---|---|---|---|---|---|---|---|
| Reddit `r/Living_in_Korea` | `https://www.reddit.com/r/Living_in_Korea/` | English | foreign residents | housing, banking, health, phones, daily life | community signal | public page/API policy review | noisy, privacy, anecdotal | monitor only / topic signal | HIGH |
| Reddit `r/korea` | `https://www.reddit.com/r/korea/` | English | broad Korea community | public services, social issues, local life | community signal | public page/API policy review | broad/noisy/politics | topic signal only | MEDIUM |
| Reddit `r/teachinginkorea` | `https://www.reddit.com/r/teachinginkorea/` | English | foreign teachers | contract, housing, health insurance, schools | community signal | public page/API policy review | job-specific, anecdotal | pain point discovery | HIGH |
| Reddit `r/Seoul` | `https://www.reddit.com/r/Seoul/` | English | Seoul residents/visitors | housing, transport, local offices, phones | community signal | public page/API policy review | travel noise | local signal only | MEDIUM |
| Expat Guide Korea | `https://www.expatguidekorea.com/` | English | foreign residents | housing, healthcare, visas, living guides | secondary support/discovery | public page/manual review | commercial bias, freshness | secondary source candidate | HIGH |
| 10 Magazine Korea | `https://10mag.com/` | English | expats/foreign residents | local life, services, events | secondary media/discovery | public page/RSS if available | lifestyle/event noise | discovery, not authority | MEDIUM |
| KoreaBridge | `https://koreabridge.net/` | English/Korean | Busan/regional foreigners | jobs, housing, local info | community/discovery | public page/manual review | mixed quality | regional signal | MEDIUM |
| Quora Korea foreigner topics | search: `Quora Korea foreigner health insurance bank account` | English | prospective movers/students | pre-arrival concerns | Q&A signal | search/manual only | low authority, stale answers | manual research only | LOW |
| YouTube Korea expat channels | search: `Korea foreigner health insurance ARC bank account` | English/multilingual | students/residents | pain points, tutorials | trend/discovery | manual only | creator bias, stale, no fact authority | trend signal only | LOW |
| TikTok Korea foreigner life | search: `Korea foreigner rent deposit health insurance SIM` | multilingual | younger residents/students | repeated pain points | trend/discovery | manual only | high noise, privacy, shallow | trend signal only | LOW |
| Facebook public expat groups | search: `Expats in Korea housing bank phone public group` | English | foreign residents | housing, jobs, phones, legal questions | community signal | manual/public only | TOS, privacy, closed groups | do not collect automatically | LOW |
| Filipino in Korea public communities | search: `Filipino in Korea housing health insurance bank account` | Tagalog/English | workers/marriage migrants | labor, remittance, healthcare | community signal | manual/public only | privacy, language quality | topic discovery | MEDIUM |
| Vietnamese in Korea public communities | search: `người Việt ở Hàn Quốc bảo hiểm y tế nhà ở ngân hàng` | Vietnamese | workers/students/families | health, housing, jobs, public offices | community signal | manual/public only | privacy, misinformation | topic discovery | MEDIUM |
| Thai workers in Korea public communities | search: `คนไทยในเกาหลี ประกันสุขภาพ เช่าบ้าน ธนาคาร` | Thai | workers/residents | labor, health, phones | community signal | manual/public only | privacy, translation risk | topic discovery | MEDIUM |
| Indonesian in Korea communities | search: `orang Indonesia di Korea asuransi kesehatan sewa rumah rekening bank` | Indonesian | workers/students | insurance, rent, banking | community signal | manual/public only | privacy, translation risk | topic discovery | MEDIUM |
| Nepali workers in Korea communities | search: `Nepali in Korea health insurance rent bank account EPS` | Nepali/English | EPS workers | labor, housing, health | community signal | manual/public only | privacy, translation risk | topic discovery | MEDIUM |
| Uzbek/Russian Korea communities | search: `узбеки в корее страховка жилье банк работа` | Russian/Uzbek | workers/students | labor, housing, banking | community signal | manual/public only | translation risk | topic discovery | LOW/MEDIUM |
| Mongolian in Korea communities | search: `Монголчууд Солонгост эрүүл мэндийн даатгал байр банк` | Mongolian | workers/students/families | insurance, housing, banking | community signal | manual/public only | translation risk | topic discovery | LOW/MEDIUM |

## 6. Korean Domestic Source Candidates

| source | institution/type | URL/search query | category coverage | validation value | access method | risks/limitations | recommended use | priority |
|---|---|---|---|---|---|---|---|---|
| HiKorea | immigration portal | `https://www.hikorea.go.kr/` | stay, immigration, civil petitions, practical visa-adjacent life | PRIMARY | public page/manual/API unknown | session/redirect, menu pages can be hard to parse | official validation source | HIGH |
| Visa Portal | official visa portal | `https://www.visa.go.kr/` | visa application/status/basic procedure | PRIMARY | public page | not all daily-life topics | official validation source | HIGH |
| Danuri | multicultural family support portal | `https://www.liveinkorea.kr/` | family, education, childcare, life in Korea, multilingual support | PRIMARY/SECONDARY | public page | family/marriage migrant focus | source-backed guide candidate | HIGH |
| Seoul Global Center | Seoul foreign resident support | `https://global.seoul.go.kr/` | counseling, Korean classes, daily life, local programs | PRIMARY/SECONDARY | public page | Seoul-centric | regional source-backed guide | HIGH |
| Korea Support Center for Foreign Workers | foreign worker support | search: `Korea Support Center for Foreign Workers counseling` | labor, counseling, living support | SECONDARY/OFFICIAL PARTNER | public page/manual | source URL freshness needs verification | validation + support guide | HIGH |
| MOEL foreign worker/labor pages | Ministry of Employment and Labor | `https://www.moel.go.kr/` search foreign worker | labor rights, wage, contract, occupational safety | PRIMARY | public page | notice-heavy, attachment-heavy | official validation | HIGH |
| EPS / HRDK Korea | employment permit system | search: `EPS Korea foreign worker official` | EPS worker process, support, workplace movement | PRIMARY | public page | not all living domains | official validation | HIGH |
| NHIS English/foreigner pages | National Health Insurance Service | `https://www.nhis.or.kr/english/` | health insurance, eligibility, payment | PRIMARY | public page | page routing changes | official validation + card source | HIGH |
| NPS English pages | National Pension Service | `https://www.nps.or.kr/jsppage/english/main.jsp` | pension, lump-sum refund, foreigner coverage | PRIMARY | public page | topic-specific | official validation | MEDIUM/HIGH |
| Korea Legal Aid Corporation | public legal aid | `https://www.klac.or.kr/` | legal counseling, dispute support | PRIMARY/SECONDARY | public page | legal sensitivity; review required | source-backed guide with caution | HIGH |
| 1345 Immigration Contact Center | immigration helpline | search: `1345 immigration contact center Korea foreigner` | immigration inquiries, public service access | PRIMARY | public info/manual | source page may be distributed | validation/support contact | HIGH |
| 120 Dasan Call Center / local call centers | Seoul/local public service | search: `Seoul 120 foreign language counseling` | local office, public services, daily life | PRIMARY/SECONDARY | public page | region-specific | regional guide source | MEDIUM |
| local government foreign resident pages | city/district offices | search: `외국인 주민 지원센터`, `외국인 주민 생활안내` | local support, offices, programs, Korean class | PRIMARY/SECONDARY | public pages | scattered, duplicate, stale | source inventory | HIGH |
| Ansan foreign resident/multicultural pages | local government/support center | search: `안산 외국인주민지원본부` | migrant support, counseling, education, integration | PRIMARY/SECONDARY | public page | regional | regional source-backed guide | HIGH |
| Gyeonggi global/foreign resident support | province/local support | search: `경기도 외국인 주민 지원센터` | regional support, counseling, programs | PRIMARY/SECONDARY | public page | scattered | regional validation source | MEDIUM/HIGH |
| multicultural family support centers | public service network | search: `다문화가족지원센터 외국인 생활 정보` | family, childcare, language, education | PRIMARY/SECONDARY | public page/manual | family focus | source-backed content | HIGH |
| migrant worker support NGOs | NGO/support organization | search: `이주노동자 지원센터 임금체불 상담` | wage, labor, legal aid, shelters | SECONDARY | public pages/manual | NGO position/bias, privacy | validation + practical support | MEDIUM/HIGH |
| banks official foreigner pages | commercial institution | search: `foreigner bank account Korea official bank` | account opening, remittance, authentication | SECONDARY | public page/manual | bank-specific, commercial | practical guide candidate with comparison caution | MEDIUM |
| telecom official foreigner pages | commercial institution | search: `foreigner SIM Korea official telecom` | SIM, phone plan, identity verification | SECONDARY | public page/manual | commercial, plan changes | practical guide candidate with caution | MEDIUM |
| housing/lease official guides | government/legal info | search: `외국인 전월세 계약 보증금 생활법령` | lease, deposit, tenant rights | PRIMARY/SECONDARY | public page/manual | legal sensitivity | guide with review required | HIGH |
| Easy Law / 생활법령정보 | legal information service | `https://www.easylaw.go.kr/` | contract, residence, public legal topics | PRIMARY/SECONDARY | public page/manual | legal wording must not be oversimplified | validation source | HIGH |

## 7. Keyword Strategy

### English

- `foreigner in Korea rent deposit`
- `Korea foreign resident lease contract deposit`
- `Korea ARC bank account foreigner`
- `Korea foreign resident health insurance`
- `Korea NHIS foreigner premium unpaid`
- `Korea phone plan foreigner ARC`
- `Korea SIM card foreign resident`
- `Korea labor contract foreign worker`
- `Korea unpaid wage foreign worker`
- `Korea migrant worker counseling center`
- `Korea foreign resident support center`
- `Korea driver license foreigner`
- `Korea multicultural family support center`
- `Korea foreigner legal aid`
- `Korea foreigners scam housing deposit`
- `living in Korea foreigner problems`

### Korean

- `외국인 근로자 월세 보증금`
- `외국인 전월세 계약 보증금`
- `외국인 건강보험 가입`
- `외국인 건강보험 체납 병원`
- `외국인 통장 개설`
- `외국인 해외송금 은행`
- `외국인 휴대폰 개통`
- `외국인 알뜰폰 본인인증`
- `외국인 임금체불 상담`
- `이주노동자 노동상담`
- `외국인 주민 지원센터`
- `다문화가족지원센터 한국어 교육`
- `외국인 운전면허 교환`
- `외국인 법률구조 상담`
- `외국인 보증금 사기`
- `외국인 주민 생활안내`

### Tagalog / Filipino

- `Filipino in Korea health insurance`
- `Pinoy Korea unpaid salary`
- `Filipino Korea bank account ARC`
- `Filipino Korea rent deposit`
- `OFW Korea labor contract`
- `Korea remittance Filipino worker`

### Vietnamese

- `người Việt ở Hàn Quốc bảo hiểm y tế`
- `người Việt ở Hàn Quốc thuê nhà tiền cọc`
- `người Việt Hàn Quốc mở tài khoản ngân hàng`
- `lao động Việt Nam tại Hàn Quốc tiền lương chưa trả`
- `người Việt ở Hàn Quốc đăng ký cư trú`

### Thai

- `คนไทยในเกาหลี ประกันสุขภาพ`
- `คนไทยในเกาหลี เช่าบ้าน เงินมัดจำ`
- `แรงงานไทยในเกาหลี เงินเดือนค้าง`
- `คนไทยเกาหลี เปิดบัญชีธนาคาร`
- `ซิมโทรศัพท์ เกาหลี คนต่างชาติ`

### Indonesian

- `orang Indonesia di Korea asuransi kesehatan`
- `orang Indonesia di Korea sewa rumah deposit`
- `pekerja Indonesia Korea gaji tidak dibayar`
- `orang Indonesia Korea buka rekening bank`
- `SIM card Korea orang asing`

### Nepali

- `Nepali in Korea health insurance`
- `Nepali worker Korea unpaid salary`
- `Nepali in Korea rent deposit`
- `Nepali Korea bank account ARC`
- `EPS worker Korea labor counseling Nepali`

### Uzbek / Russian

- `узбеки в корее медицинская страховка`
- `узбеки в корее аренда депозит`
- `работа в корее невыплата зарплаты`
- `иностранцы в корее банковский счет`
- `Корея ARC телефонная сим карта`

### Mongolian

- `Монголчууд Солонгост эрүүл мэндийн даатгал`
- `Солонгост байр түрээс барьцаа`
- `Солонгост цалин өгөхгүй ажил олгогч`
- `Солонгост банкны данс нээх`
- `Солонгост гадаад иргэн утасны дугаар`

## 8. Community Signal Policy

Allowed use:

- 반복 질문/불편/위험 신호 탐지
- language/community-specific pain point 발견
- `topic_candidate`, `pain_point`, `target_user`, `action_type` 후보 생성
- official validation source를 찾기 위한 검색 힌트
- topic cluster의 demand score 보조 신호

Forbidden use:

- 개인 게시글 원문 저장/재게시
- 댓글/사례 직접 인용
- 개인 이름, 연락처, 회사명, 주소, 카카오톡 ID, 얼굴/이미지 등 PII 저장
- 커뮤니티 주장을 법률/비자/의료/금융 사실로 사용
- closed/private/login-only community scraping
- public content의 source link를 커뮤니티 게시글로 직접 사용하는 것

Validation requirement:

```text
community signal
-> topic_candidate
-> official/secondary validation source required
-> fact_point extraction
-> review candidate
```

Privacy/PII rule:

- 저장은 topic-level metadata 중심으로 제한한다.
- 개인 사례는 `pain_point_summary`처럼 익명화된 category signal로만 다룬다.
- screenshot/image/video/comment body 저장은 기본 금지다.

Quote/publication rule:

- community source text는 public content에 직접 quote하지 않는다.
- "Many foreign residents ask about..." 같은 표현도 검증 가능한 내부 통계가 생기기 전에는 조심한다.
- public card에는 official/secondary source-backed fact만 넣는다.

## 9. Source-to-Content Promotion Rules

```text
official source
-> evidence
-> source-backed guide/card candidate possible
```

공식/기관 출처는 link, body/notice/structured data, freshness가 확인되면 guide/card 후보가 될 수 있다. 법률/비자/의료/금융/노동은 Telegram Review를 유지한다.

```text
trusted media
-> signal + explainable content possible with caution
```

매체 기사는 policy change나 public issue를 설명할 수 있지만 official policy source가 아니면 단독 fact source로 쓰지 않는다.

```text
secondary support source
-> practical guide candidate possible
```

지원센터, NGO, 은행, 통신사, 병원, 학교, 지역기관은 실무 안내 출처가 될 수 있다. 단 commercial/region-specific bias를 표시하고, 민감 내용은 official source와 cross-check한다.

```text
community source
-> user-need signal only
-> requires official/secondary validation before content
```

커뮤니티는 topic demand를 만들 수 있지만 public fact가 아니다.

```text
social media trend
-> discovery signal only
-> never direct public fact
```

YouTube/TikTok/Facebook public posts는 trend discovery 이상으로 승격하지 않는다.

Promotion gate:

- `source_signal only`: community/social/Q&A/blog anecdote, unverified pain point
- `evidence only`: official page, support center page, legal guide, health insurance page
- `review candidate`: official/secondary evidence + user need + practical action exists
- `topic cluster candidate`: same `topic_key` across multiple signals/evidence
- `source-backed guide/card candidate`: at least 3 usable fact/card points + validation source
- `public content`: manual approval after review, no PII, no system text, source link valid

## 10. Safe Test-Run Plan

This is a design only. Do not execute until separately approved.

### Source set

Start with 12 sources:

- HiKorea
- Visa Portal
- Danuri
- Seoul Global Center
- NHIS English/foreigner pages
- NPS English pages
- MOEL foreign worker/labor pages
- Korea Legal Aid Corporation / Easy Law
- one local government foreign resident page
- Reddit `r/Living_in_Korea`
- Reddit `r/teachinginkorea`
- Expat Guide Korea

### Keyword set

Use 5 categories first:

- `housing`: `foreigner in Korea rent deposit`, `외국인 전월세 계약 보증금`
- `healthcare`: `Korea foreign resident health insurance`, `외국인 건강보험 가입`
- `banking`: `Korea ARC bank account foreigner`, `외국인 통장 개설`
- `telecom`: `Korea phone plan foreigner ARC`, `외국인 휴대폰 개통`
- `labor_rights`: `Korea unpaid wage foreign worker`, `외국인 임금체불 상담`

### Result limit

- official/secondary sources: max 10 pages per source by manual review
- community sources: max 20 public post titles/metadata per community, no body/comment collection
- multilingual discovery: max 5 search results per language/category

### Fields to record

- `source_name`
- `source_url`
- `source_type`
- `language`
- `country/community`
- `category`
- `topic_candidate`
- `target_user`
- `user_need_signal`
- `validation_source_needed`
- `trust_level`
- `privacy_risk`
- `actionability_score`
- `repeatability_score`
- `freshness`
- `recommendation`

### Scoring rules

- `actionability_score`
  - 0: no practical action
  - 1: vague awareness only
  - 2: user can check one thing
  - 3: clear step/contact/document/deadline
- `repeatability_score`
  - 0: one-off news
  - 1: seasonal/local only
  - 2: recurring issue
  - 3: evergreen settlement problem
- `trust_level`
  - PRIMARY: official/public authority
  - SECONDARY: support center/NGO/commercial official guide
  - SIGNAL: community/forum/social trend
- `recommendation`
  - `collect`
  - `monitor only`
  - `manual research only`
  - `do not use`

### Expected output

- source inventory draft
- top 20 `topic_candidate`
- official validation source candidates for each topic
- no public content
- no Telegram notification
- no DB write

### Stop conditions

- login/private/paywalled source required
- PII appears in data that would need storage
- source TOS/API disallows collection
- topic requires legal/medical/financial conclusion without official source
- large scraping or automation would be needed

### Verification plan

- Confirm every community-derived topic has `validation_source_needed = YES`.
- Confirm no full personal story/comment body is stored.
- Confirm every guide/card candidate has a valid official/secondary source URL.
- Confirm generic travel/crypto/politics/economy items stay out of `LIVING_INFO` review candidates.

## 11. Data Model Gaps

Future fields/tables to consider. No schema change is recommended in this audit.

- `topic_key`
- `topic_cluster_id`
- `source_signal_type`
- `source_access_policy`
- `source_owner`
- `target_user`
- `action_type`
- `pain_point`
- `language_group`
- `region_in_korea`
- `validation_needed`
- `validation_source_url`
- `official_validation_status`
- `fact_point`
- `fact_point_hash`
- `card_point`
- `card_point_hash`
- `usable_for_card`
- `community_signal_count`
- `source_spread_count`
- `evidence_count`
- `privacy_risk_level`
- `trust_level`
- `last_validated_at`
- `content_fingerprint`

Likely future table concepts:

- `living.source_inventory`
- `living.source_signal`
- `living.topic_cluster`
- `living.fact_point`
- `living.card_point`

Ownership is unresolved and must be audited before migration:

- `social_news.candidate` should likely remain source/news candidate storage.
- `content.content_candidate` should remain review/publish candidate storage.
- living topic aggregation may need a separate living-domain layer rather than overloading either table.

## 12. Risk Analysis

Privacy risk:

- Community data can contain personal immigration, employment, medical, legal, and financial details.
- Direct storage of bodies/comments can create privacy exposure.
- Mitigation: metadata/topic-level signal only, no PII, no screenshots, no direct quotes.

TOS/API risk:

- Reddit/Facebook/YouTube/TikTok/Naver/Kakao access rules differ.
- Login-only/private groups must not be scraped.
- Mitigation: manual review or official API only after policy review.

Misinformation risk:

- Community answers often mix old rules, personal exceptions, rumors, or region-specific experience.
- Mitigation: community signal cannot become public fact without official/secondary validation.

Over-collection risk:

- More sources can increase noise instead of useful content.
- Mitigation: start with small manual inventory and fields, not runtime collector expansion.

Duplicate/noise risk:

- Same topic appears across multiple communities with repeated anecdotes.
- Mitigation: dedupe by `topic_key`, `language_group`, `category`, and source spread.

Classification risk:

- `travel`, `lifestyle`, `culture`, `local_events` can pull in generic low-value articles.
- Mitigation: require practical foreign resident actionability and official/secondary validation for public candidates.

Public content trust risk:

- Legal, visa, health, finance, labor topics are sensitive.
- Mitigation: Telegram Review and manual approval remain mandatory for `LIVING_INFO` guides/cards.

## 13. Recommended Roadmap

### Phase 1: READ_ONLY_AUDIT

- Build a source inventory proposal by category.
- Separate `official source`, `secondary support source`, `community signal`, `trend signal`.
- Confirm allowed access method and risk per source.

### Phase 2: DOC_ONLY

- Add `LIVING_INFO source policy` and `community signal policy` to the appropriate architecture/to-be document.
- Keep it operational, not essay-style.

### Phase 3: READ_ONLY_AUDIT

- Decide ownership of `topic_key`, `source_signal`, `fact_point`, and `card_point`.
- Compare options:
  - social/news-owned
  - content-owned
  - new living-domain layer

### Phase 4: GUARDED_FIX candidate

- Add read-only admin/source inventory view or static source inventory config.
- No collector execution.
- No DB mutation unless separately approved.

### Phase 5: GUARDED_FIX candidate

- Implement a small manual import/test-run prototype for public source discovery output.
- Output file only or dev-only endpoint.
- No publishing, no Telegram runtime behavior change.

### Phase 6: Future collector candidates

- Official/semi-official living support sources first.
- Community signal monitoring only after source ethics/TOS review.
- Generate topic clusters before guide/card candidates.

## 14. CODE_TASK_CANDIDATE

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY
MODE: DOC_ONLY
FOCUS:
Create a LIVING_INFO source inventory policy that classifies official, secondary, community, and trend sources.
WHY:
The current LIVING_INFO pipeline needs broader source coverage without promoting community anecdotes into public facts.
RISK: LOW
PROTECTED AREA:
DB, migration, scheduler, publisher, Telegram runtime, auth/env/config, external API calls
FILES LIKELY INVOLVED:
DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
DOC/to-be/content-creation.md
DOC/walkthrough/YYYY-MM-DD - execute prompt.md
RECOMMENDED NEXT PROMPT:
Turn the LIVING_INFO source spectrum audit into a concise operational source policy without changing runtime code.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY + COMMUNITY_SIGNAL
MODE: DOC_ONLY
FOCUS:
Define the community signal policy for Reddit, Facebook public pages, YouTube/TikTok, Naver/Daum public content, and language-specific communities.
WHY:
Community sources are useful for pain point discovery but must not become authoritative public facts.
RISK: LOW
PROTECTED AREA:
DB, migration, collector execution, publisher, Telegram runtime, auth/env/config
FILES LIKELY INVOLVED:
DOC/architecture/02_DATA_SOURCE_AND_QUALITY.md
DOC/to-be/topic-search.md
RECOMMENDED NEXT PROMPT:
Create a community signal policy with allowed use, forbidden use, validation rules, and PII boundaries.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY
MODE: READ_ONLY_AUDIT
FOCUS:
Design a safe manual test-run query sheet for LIVING_INFO source discovery.
WHY:
Before implementing collectors, the project needs to know which source/keyword combinations produce useful topic candidates.
RISK: LOW
PROTECTED AREA:
DB, migration, runtime collectors, publisher, Telegram runtime, auth/env/config, external API automation
FILES LIKELY INVOLVED:
DOC/walkthrough/YYYY-MM-DD - execute prompt.md
DOC/walkthrough/execution-history/YYYY-MM-DD/
RECOMMENDED NEXT PROMPT:
Create a manual/read-only test-run template with source_name, source_url, source_type, language, category, topic_candidate, target_user, trust_level, privacy_risk, actionability_score, repeatability_score, and recommendation.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + CONTENT_QUEUE + DATA_SOURCE_QUALITY
MODE: READ_ONLY_AUDIT
FOCUS:
Audit ownership for topic_key, source_signal, fact_point, card_point, and topic_cluster.
WHY:
The current guardrail blocks single news cards, but persistent topic-based living guide generation needs a clear owner before schema or code changes.
RISK: MEDIUM
PROTECTED AREA:
DB mutation, migration execution, publisher, scheduler, Telegram runtime, auth/env/config
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/content/service.py
SRC/foreign_worker_life_info_collector/utils/content_card_renderer.py
SRC/foreign_worker_life_info_collector/social/news/
DOC/database/
DOC/walkthrough/
RECOMMENDED NEXT PROMPT:
Review whether LIVING_INFO topic aggregation belongs in social_news, content, or a dedicated living-domain layer, and produce a migration impact analysis without implementing it.
```

```text
CODE_TASK_CANDIDATE
AREA: LIVING_DOMAIN + DATA_SOURCE_QUALITY
MODE: GUARDED_FIX
FOCUS:
Add a dev-only/manual source inventory prototype after DOC_ONLY policy is approved.
WHY:
The team needs a safe way to record source candidates and topic signals without running collectors or publishing content.
RISK: MEDIUM
PROTECTED AREA:
Publisher, scheduler, Telegram runtime, auth/env/config, external API automation
FILES LIKELY INVOLVED:
SRC/foreign_worker_life_info_collector/
DOC/walkthrough/
RECOMMENDED NEXT PROMPT:
Implement a local-only LIVING_INFO source inventory prototype that writes to a generated local JSON/CSV file, not DB, and validates no PII fields are stored.
```

## 15. Stop Conditions Encountered

No hard stop was encountered.

Implementation was intentionally not performed because this task is `READ_ONLY_AUDIT`.

Items requiring explicit future approval:

- adding or changing DB schema
- adding runtime collectors
- using Reddit/Facebook/YouTube/TikTok/Naver/Daum APIs or scraping
- collecting community post/comment bodies
- storing language-specific community data
- sending Telegram Review notifications from new living sources
- changing Facebook/content publisher selection

## 16. Final Recommendation

The safest next action is:

```text
Create a DOC_ONLY LIVING_INFO source policy and source inventory first.
Then run a small manual/read-only source discovery test.
Only after that, audit topic_key / source_signal / fact_point ownership before any collector or DB change.
```

This preserves WorkConnect quality because it broadens living-information input without weakening the rule that community sources are only user-need signals and public cards must be source-backed.
