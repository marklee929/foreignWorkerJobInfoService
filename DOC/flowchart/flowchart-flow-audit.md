# Flowchart Flow Audit

Time:

```text
Report date: 2026-06-13 KST
Mode: DOC_ONLY
Code changes: NONE
```

## Scope

Reviewed:

- `DOC/flowchart/flowchart-definition.md`
- `DOC/flowchart/mermaid-diagram.png` as the rendered companion artifact

Purpose:

- Review the intended end-to-end flow.
- Identify improvement and correction points.
- Record future work candidates without changing code, DB, scheduler, Facebook publisher, tokens, or runtime state.

## Current Flow Summary

The flowchart defines this target path:

```text
Product North Star
-> User Need
-> Source Discovery
-> Raw Collection
-> Source Validity Gate
-> Normalization
-> Duplicate & Source Normalization
-> Domain Classification
-> User Value Evaluation
-> Content Candidate
-> Content Management Queue
-> Publish Decision
-> Facebook / Telegram
-> Feedback Signal
-> Knowledge Improvement
-> User Need
```

The most important architectural intent is correct:

```text
source candidate != publishable content
content.content_candidate = final publishable object
```

The weak point is not broad collection. Broad collection is acceptable. The weak point is promotion: generic source items can still move too far toward content candidates or publish-ready state unless every gate has a strict contract.

## Findings

1. Source discovery is intentionally broad, but relevance ownership is unclear.

   The flowchart says country-related articles are not automatically WorkConnect-relevant. That rule should be treated as a hard contract at the User Value Evaluation stage. A Korea-related article should only advance when it helps a target user work, live, study, immigrate, settle, or access support.

2. URL lifecycle needs four separate fields, not one overloaded URL.

   The flowchart correctly separates:

   ```text
   discovery_url
   source_url
   canonical_url
   publishable_link_url
   ```

   The current operational problems around Google RSS URLs, publisher root URLs, and legacy `/path/A...` links show why this distinction matters. Final publishing should use only `publishable_link_url`, produced by a final link validation gate.

3. Content Missing must be a terminal validation state for public content.

   System fallback text such as "stored article body is missing" must never enter public summary, title, why-it-matters, or Facebook message fields. If content contains known fallback/system messages, the candidate should be marked `CONTENT_MISSING` or `CONTENT_INVALID` and stay out of auto publishing.

4. Duplicate handling should preserve signal, not only suppress rows.

   The flowchart's distinction is important:

   ```text
   same URL repeat = duplicate noise
   same topic from multiple sources = duplicate signal
   ```

   A representative content candidate should absorb the topic-spread signal, while repeated URLs and low-value duplicates stay out of the publish queue.

5. User Value Evaluation needs subscription-oriented scoring.

   Existing scoring concepts such as freshness, source reliability, Korea relevance, and Facebook suitability are necessary but not enough. The flowchart correctly calls for:

   ```text
   user_need_score
   actionability_score
   repeatability_score
   subscription_value_score
   target_persona_score
   ```

   These scores should decide whether a source item becomes WorkConnect content, not just whether it is recent or newsworthy.

6. Direct source-schema publishing remains the highest-risk boundary.

   The target architecture says source candidates are not publishable by default and only `content.content_candidate` can be published. Any remaining direct `social_news.candidate -> Facebook` path should be treated as transition behavior and protected before modification.

7. Auto publish should remain narrow.

   The flowchart's publish safety rule is sound:

   Auto publish only when all are true:

   - official or reliable source
   - valid publishable link
   - clear content
   - high user need
   - low sensitivity
   - no system-message contamination
   - not generic politics/economy/general news

   Review required:

   - immigration/legal interpretation
   - sensitive incident
   - weak or unclear source
   - global reference with weak local actionability
   - unclear WorkConnect relevance

8. Feedback loop should optimize for repeat need, not raw reach.

   Views alone can reward generic or sensational articles. The flowchart should treat clicks, comments, saves, shares, repeat topic engagement, and subscription conversion as stronger signals than impressions.

9. Admin dashboard needs to show gate-level reasons.

   The flowchart has many gates, but the operator needs to see why an item is blocked:

   - source invalid
   - content missing
   - duplicate noise
   - duplicate signal absorbed
   - low user need
   - low actionability
   - sensitive review
   - invalid publishable link
   - content candidate not created

   Without gate-level visibility, the system looks like it "stopped" even when it is correctly blocking unsafe or low-value items.

## Recommended Corrections

1. Make `Content Candidate` the only final publishing boundary.

   Correction:

   ```text
   Source schemas collect and classify.
   content.content_candidate owns final message, final link, validation state, approval state, and publish state.
   Facebook publisher reads only final content candidates.
   ```

2. Add a strict promotion contract from source candidate to content candidate.

   Required promotion fields:

   - target persona
   - user need category
   - actionability reason
   - subscription value reason
   - publishable link validation result
   - content completeness validation result
   - sensitivity review result
   - duplicate signal handling result

3. Add a final publish validation gate immediately before Facebook.

   Required checks:

   - `publishable_link_url` exists and is not Google News, root URL, legacy redirect, or known invalid link
   - public message contains no system/fallback/internal text
   - generated language is acceptable for the channel
   - candidate is not sensitive unless manually approved
   - source traceability is present

4. Separate "blocked" from "failed".

   Suggested state distinction:

   - `BLOCKED_SOURCE_INVALID`
   - `BLOCKED_CONTENT_MISSING`
   - `BLOCKED_LOW_USER_VALUE`
   - `BLOCKED_SENSITIVE_REVIEW`
   - `FAILED_FETCH`
   - `FAILED_LLM`
   - `FAILED_FACEBOOK`

   Blocked means the system made a correct decision. Failed means an operation could not complete.

5. Change feedback weighting.

   Treat these as high-value signals:

   - save-worthy topic
   - repeat topic engagement
   - comments asking follow-up questions
   - clicks on practical guides
   - subscription or return-visit correlation

   Treat raw views as a weak signal unless paired with stronger engagement.

## Work Candidates

```text
CODE_TASK_CANDIDATE
AREA: SOCIAL_NEWS_CANDIDATE / CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
FOCUS: Inspect why generic politics/economy/general news items are promoted toward content candidates.
WHY: The flowchart says country relevance is not enough; WorkConnect relevance requires target-user need and actionability.
RISK: LOW-MEDIUM
PROTECTED AREA: NO, if read-only.
RECOMMENDED NEXT PROMPT: AREA: SOCIAL_NEWS_CANDIDATE / CONTENT_QUEUE / MODE: READ_ONLY_AUDIT / FOCUS: Compare recent source candidates, content candidates, and blocked/skipped reasons against user_need_score/actionability_score gaps.
```

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_QUEUE
MODE: READ_ONLY_AUDIT
FOCUS: Verify whether content.content_candidate has enough fields to own final publishing.
WHY: The flowchart depends on content candidates being final publishable objects, not mirrors of source candidates.
RISK: MEDIUM
PROTECTED AREA: NO, if read-only.
RECOMMENDED NEXT PROMPT: AREA: CONTENT_QUEUE / MODE: READ_ONLY_AUDIT / FOCUS: Inspect content candidate fields and report missing contract fields for final message, final link, validation state, source traceability, and approval state.
```

```text
CODE_TASK_CANDIDATE
AREA: DATA_SOURCE_QUALITY
MODE: READ_ONLY_AUDIT
FOCUS: Audit URL lifecycle quality for discovery_url, source_url, canonical_url, and publishable_link_url.
WHY: The flowchart identifies invalid URL promotion as a recurring source of broken Facebook posts and cleanup churn.
RISK: LOW-MEDIUM
PROTECTED AREA: NO, if read-only.
RECOMMENDED NEXT PROMPT: AREA: DATA_SOURCE_QUALITY / MODE: READ_ONLY_AUDIT / FOCUS: Sample recent source candidates and classify invalid URL patterns without changing data.
```

```text
CODE_TASK_CANDIDATE
AREA: CONTENT_PUBLISHER
MODE: PROTECTED_CHANGE
FOCUS: Add a final publish validation gate that only accepts complete content candidates with publishable_link_url.
WHY: The flowchart requires final publishing to be separated from source collection and protected from system-message contamination.
RISK: HIGH
PROTECTED AREA: YES - CONTENT_PUBLISHER, FACEBOOK_PUBLISHER, scheduler behavior, publish selection.
RECOMMENDED NEXT PROMPT: AREA: CONTENT_PUBLISHER / MODE: PROTECTED_CHANGE / FOCUS: After read-only audits, implement final validation with explicit approval.
```

```text
CODE_TASK_CANDIDATE
AREA: DASHBOARD_STATUS
MODE: READ_ONLY_AUDIT
FOCUS: Map each flowchart gate to an admin-visible status and reason.
WHY: Operators need to distinguish correct blocking from operational failure.
RISK: LOW-MEDIUM
PROTECTED AREA: NO, if read-only.
RECOMMENDED NEXT PROMPT: AREA: DASHBOARD_STATUS / MODE: READ_ONLY_AUDIT / FOCUS: Compare current dashboard labels with source validity, content completeness, duplicate, user value, sensitivity, and publish validation gates.
```

## Priority Order

1. Read-only audit of recent source candidates and content candidates against WorkConnect relevance.
2. Read-only audit of content candidate contract fields.
3. Read-only audit of URL lifecycle and publishable link quality.
4. Dashboard gate-reason visibility design.
5. Protected implementation of content-only final publishing.

## Protected Areas

Do not change without explicit implementation approval:

- final Facebook publish path
- token usage or token refresh behavior
- scheduler interval, cooldown, daily cap, or bot ON/OFF state
- automatic publish selection thresholds
- broad DB migration or bulk backfill
- external community/social source collection

## Conclusion

The flowchart's direction is sound. The main correction is to make gates explicit and enforce the boundary:

```text
collect broadly
promote narrowly
publish only content candidates
show every block reason to the operator
learn from repeat user need, not raw views
```

This is documentation only. No code, DB, environment, server, scheduler, or external publishing behavior was changed.
