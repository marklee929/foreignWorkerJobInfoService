### 타임스탬프 수정내용 ###

Facebook 자동 게시 포맷을 기존 수동 게시처럼 링크 카드가 붙는 방식으로 수정해줘.

현재 문제:
- 자동 게시 본문에 긴 URL이 직접 노출된다.
- 일부 게시물은 https://www.koreatimes.co.kr/path/... 같은 잘못된 redirect/path URL이 Read more로 들어간다.
- Facebook 카드/이미지 미리보기가 붙지 않는다.
- 예전 수동 게시처럼 “Read more here: [link]” + 링크 카드 형태가 나오지 않는다.

목표:
Graph API 게시 시 message와 link를 분리한다.
message에는 긴 URL을 직접 넣지 않고, 실제 기사 상세 URL을 link 파라미터로 전달해서 Facebook이 링크 카드/이미지를 생성하게 한다.

정책:
1. FacebookPublisher.publish()에서 POST /{PAGE_ID}/feed 호출 시:
   - message = 게시 본문 텍스트
   - link = 유효한 기사 상세 URL
2. message 안에는 긴 URL을 넣지 않는다.
3. message의 Read more 영역은 아래 중 하나로 짧게 표시한다.
   - Read more below.
   - Read more here: [link]
4. 실제 클릭 가능한 링크 카드는 Graph API의 link 파라미터로 생성한다.
5. HTML anchor는 사용하지 않는다. Facebook 일반 게시글에서는 `<a href>`가 동작하지 않는다.

URL 선택 우선순위:
1. article_url_valid = true 인 source_url
2. canonical_url이 실제 기사 상세 URL이면 canonical_url
3. original_url이 실제 기사 상세 URL이면 original_url
4. Google News RSS URL은 link로 사용하지 않음
5. publisher root URL은 link로 사용하지 않음
6. /path/A... 같은 legacy redirect URL보다 실제 canonical article URL을 우선 사용

잘못된 link로 판단:
- news.google.com/rss/articles
- news.google.com/articles
- publisher root URL
- 도메인만 있는 URL
- /path/A... 같이 원문 slug가 아닌 내부 redirect URL
- canonical이 Google URL인 경우
- article_url_valid_yn = false

게시 메시지 예시:
Title

Summary:
- ...
- ...
- ...

Why it matters for foreign workers in Korea:
- ...
- ...
- ...

Read more here: [link]

#KoreaJobs #WorkInKorea #ForeignWorkers #VisaInfo

Graph API payload 예시:
{
  "message": "... Read more here: [link] ...",
  "link": "https://www.koreaherald.com/article/10729435"
}

관리자 상세보기:
- final_message
- facebook_link_url
- link_valid_yn
- link_reject_reason
- payload preview
- Facebook response

중요:
message에 URL을 넣지 말고 link 파라미터를 반드시 분리해서 보내라.
링크 카드가 안 뜨면 Facebook Sharing Debugger로 해당 facebook_link_url의 og:title, og:description, og:image 접근 가능 여부를 확인할 수 있게 로그를 남겨라.