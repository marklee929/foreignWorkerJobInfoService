chart code:
    A[Product North Star<br/>타국 정착/취업/생활 정보 플랫폼] --> B[User Need 정의<br/>일, 비자, 주거, 금융, 의료, 교통, 권리, 지원]
    
    B --> C[Source Discovery<br/>공식기관/API/뉴스/RSS/검색/생활정보/직업정보]
    
    C --> D[Raw Collection<br/>원문 URL, 제목, 본문, 발행일, 수집일, raw payload 저장]
    
    D --> E{Source Validity Gate}
    E -- invalid --> E1[BLOCK / REVIEW<br/>Google RSS only, root URL, no article URL]
    E -- valid --> F[Normalization<br/>canonical_url, language, country, category, hash, similarity_key]
    
    F --> G[Duplicate & Source Normalization]
    G --> G1{Duplicate Type}
    G1 -- same URL repeat --> G2[DUPLICATE_NOISE<br/>게시 후보 제외]
    G1 -- same topic multi-source --> G3[DUPLICATE_SIGNAL<br/>전파도/중요도 신호]
    G1 -- unique --> H[Domain Classification]
    
    H --> H1[News]
    H --> H2[Living Info]
    H --> H3[Immigration / Visa]
    H --> H4[Occupation Dictionary]
    H --> H5[Employment / Job Info]
    
    H1 --> I[User Value Evaluation]
    H2 --> I
    H3 --> I
    H4 --> I
    H5 --> I
    
    I --> I1{Quality Gate}
    I1 -- low relevance --> I2[SKIPPED<br/>한국 관련만 높고 유저 필요성 낮음]
    I1 -- content missing --> I3[CONTENT_MISSING<br/>시스템 메시지 본문 유입 차단]
    I1 -- sensitive --> I4[REVIEW_REQUIRED_SENSITIVE]
    I1 -- useful --> J[Content Candidate 생성]
    
    J --> K[Content Management Queue<br/>관리자 화면에서 확인/수정/승인/재게시]
    
    K --> L{Publish Decision}
    L -- auto safe --> M[Auto Publish]
    L -- manual review --> N[Admin Review / Edit]
    L -- reject/archive --> O[ARCHIVED / REJECTED]
    
    N --> M
    
    M --> P[Facebook WorkConnect Korea<br/>message + link 분리 게시]
    M --> Q[Telegram Operation Report]
    
    P --> R[Reaction / Feedback<br/>조회, 클릭, 댓글, 공유, 구독 전환]
    R --> S[Performance & Subscription Signal]
    
    S --> T[Knowledge Improvement<br/>체크리스트, 가이드, 반복형 정보, GPT/RAG 지식화]
    T --> B

    K --> U[Admin Frontend<br/>상태판/목록/검토/수동 게시]
    V[Backend + Local LLM] --> D
    V --> F
    V --> G
    V --> I
    V --> J
    V --> M
    
    W[Local LLM Optional<br/>중복/관련성/민감도/요약 품질 보조] --> G
    W --> I
    W --> J

이 플로우에서 지금 문제 지점
1. Source Discovery가 너무 넓게 열려 있음

“카테고리 확장”이 지금은 이런 식으로 해석되고 있어.

한국 관련 뉴스면 후보

그래서 정치, 선거, 코스피 같은 일반 뉴스가 올라옴.

수정 방향:

국가 관련성 ≠ WorkConnect 관련성

프롬프트/로직에 이렇게 박아야 함.

A country-related article is not automatically WorkConnect-relevant.
It must help a person work, live, study, immigrate, settle, or access support in the target country.
2. Source Validity Gate가 약함

Google RSS, publisher root, /path/A... 같은 링크가 최종 링크로 들어갈 수 있음.

차단 기준이 필요함.

discovery_url ≠ source_url ≠ canonical_url ≠ publishable_link_url

최종 게시에는 반드시 publishable_link_url만 써야 함.

3. Content Missing이 public content로 흘러감

가장 위험한 문제 중 하나.

저장된 기사 본문이 없습니다.
일부 RSS/검색 결과는 원문 HTML 접근이 제한될 수 있습니다.

이런 시스템 메시지가 본문/요약/why-it-matters에 들어가면 안 됨.

이건 하드블록이어야 함.

If content contains known system fallback message, mark CONTENT_MISSING or CONTENT_INVALID.
Never use it as public summary.
4. Duplicate가 단순 중복으로만 처리됨

중복은 둘로 나눠야 함.

same URL repeat = noise
same topic from multiple sources = signal

지금은 중복이 많다는 사실은 보이는데, “중복의 질”이 분리되지 않은 것 같음.

콘텐츠 후보로 올라갈 건 대표 1개고, 나머지는 topic spread signal로 남겨야 함.

5. User Value Evaluation이 약함

현재 점수는 아마 이런 쪽에 치우쳐 있음.

freshness
source reliability
Korea relevance
Facebook suitability

그런데 구독 전환에는 이 점수가 더 중요함.

user_need_score
actionability_score
repeatability_score
subscription_value_score
target_persona_score

즉 “뉴스로서 좋다”가 아니라 “유저가 반복적으로 필요로 한다”를 봐야 함.

6. Content Candidate와 Source Candidate 경계

현재 핵심 경계:

social_news.candidate = 원천 뉴스 후보
content.content_candidate = 최종 게시 콘텐츠 후보

이 경계가 흐려지면 시스템이 다시 “뉴스봇”으로 돌아감.

프롬프트에 계속 넣어야 함.

Source candidates are not publishable content by default.
Only content.content_candidate can be published.
7. Auto Publish가 너무 빨리 최종 단계로 감

자동게시가 목표이긴 한데, 초반엔 자동게시 기준이 너무 넓으면 페이지 정체성이 흐려짐.

정책은 이렇게 가야 함.

Auto publish:
- official source
- valid link
- clear content
- high user need
- low sensitivity
- no system contamination
- not generic politics/economy

Review required:
- immigration/legal
- sensitive incident
- weak source
- global reference
- unclear relevance
8. Feedback이 “조회수” 위주로만 해석됨

조회수는 늘었는데 구독이 안 생긴 이유가 여기 있음.

조회수 = 관심
구독 = 반복 필요성

그래서 feedback metric도 바뀌어야 함.

views
clicks
comments
shares
repeat topic engagement
subscription conversion
save-worthy content type
이 플로우 기준으로 다음 프롬프트를 정교화하면 이렇게 나뉨
A. Source Quality 프롬프트

목표:

잘못된 원문/링크/본문 결손을 early block

핵심 AREA:

SOCIAL_NEWS_COLLECTOR
DATA_SOURCE_QUALITY
CONTENT_QUEUE
B. Relevance Scoring 프롬프트

목표:

정치/증시/일반뉴스 차단, 정착정보 우선

핵심 AREA:

SOCIAL_NEWS_CANDIDATE
CONTENT_QUEUE
C. Content Candidate Contract 프롬프트

목표:

source candidate와 publishable content 분리

핵심 AREA:

CONTENT_QUEUE
DB_ARCHITECTURE_DOCS
D. Publishing Safety 프롬프트

목표:

Facebook 게시 전 최종 검증

핵심 AREA:

CONTENT_PUBLISHER
FACEBOOK_STATUS

단 이건 HIGH risk라 자동화 말고 guarded session.

E. Subscription Value 프롬프트

목표:

뉴스 → 반복형 가이드로 변환

핵심 AREA:

CONTENT_QUEUE
CONTENT_STRATEGY
DATA_SOURCE_QUALITY
내가 보기엔 제일 먼저 정교화할 프롬프트

지금은 이게 1순위야.

AREA: SOCIAL_NEWS_CANDIDATE / CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
FOCUS: Find why generic politics/economy/news articles are being promoted as WorkConnect content candidates, and propose rule-based gates for user_need_score, actionability_score, repeatability_score, and subscription_value_score.
TIMEBOX: 60m

이걸 먼저 돌리면 “왜 코스피/선거 기사가 올라오는지” 구조가 잡힐 거야.

한 줄 요약

현재 문제는 수집기가 아니라 승격 기준이야.

수집은 넓게 해도 됨.
하지만 콘텐츠 후보 승격은 좁고 엄격해야 함.

WorkConnect의 핵심 플로우는:

정보 수집
→ 정규화
→ 유저 필요성 판단
→ 반복형 콘텐츠 후보화
→ 안전한 게시
→ 반응 기반 개선

이 흐름으로 고정해야 해.