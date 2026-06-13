# Code Task Candidate Index

## Purpose

This document collects implementation candidates discovered during DOC_ONLY harness preparation.

It is not an approval to implement.

Every item must still start with a new harness prompt using:

```text
AREA:
MODE:
FOCUS:
TIMEBOX:
```

Protected or high-risk items require explicit user approval before code, DB, scheduler, Facebook, auth, env, or server changes.

## Candidate Summary

| ID | AREA | MODE | Risk | User Approval | Focus |
| --- | --- | --- | --- | --- | --- |
| CAND-001 | CONTENT_QUEUE | READ_ONLY_AUDIT | MEDIUM | No | Verify source-to-content sync boundaries and raw_ref ownership |
| CAND-002 | FACEBOOK_STATUS | READ_ONLY_AUDIT | MEDIUM-HIGH | Review before fix | Audit token status and error category reporting without publisher changes |
| CAND-003 | CONTENT_PUBLISHER | PROTECTED_CHANGE | HIGH | Yes | Move final automatic publish selection fully to content candidates |
| CAND-004 | SOCIAL_NEWS_CANDIDATE | READ_ONLY_AUDIT first | MEDIUM | No for audit | Inspect duplicate fields before duplicate_type implementation |
| CAND-005 | OCCUPATION_DICTIONARY | READ_ONLY_AUDIT | LOW-MEDIUM | No | Verify occupation data readiness for guide content |
| CAND-006 | DB_ARCHITECTURE_DOCS | READ_ONLY_AUDIT | LOW-MEDIUM | No, read-only SQL only | Inventory social_news/content tables, statuses, and publish-log ownership |
| CAND-007 | CONTENT_QUEUE | READ_ONLY_AUDIT | MEDIUM | No | Check whether content candidates are final content or source-row copies |
| CAND-008 | CONTENT_PUBLISHER | PROTECTED_CHANGE | HIGH | Yes | Retire or gate direct social_news Facebook publishing |
| CAND-009 | DASHBOARD_STATUS | READ_ONLY_AUDIT | LOW-MEDIUM | No | Verify dashboard summary/count query behavior |
| CAND-010 | CONTENT_QUEUE | READ_ONLY_AUDIT | MEDIUM | No | Inspect content API payloads and UI display gaps |
| CAND-011 | OCCUPATION_DICTIONARY | READ_ONLY_AUDIT | LOW-MEDIUM | No | Decompose occupation content creation into readiness phases |
| CAND-012 | CONTENT_PUBLISHER | PROTECTED_CHANGE | HIGH | Yes | Add occupation/living/immigration content to publish rotation |
| CAND-013 | LIVING_DOMAIN | READ_ONLY_AUDIT | MEDIUM-HIGH | No for policy audit | Draft safe community-source discovery policy |
| CAND-014 | LLAMA_STATUS | READ_ONLY_AUDIT | MEDIUM | No | Define Local LLM boundaries for topic discovery and GPT answers |
| CAND-015 | DB_ARCHITECTURE_DOCS | READ_ONLY_AUDIT | MEDIUM | No for design audit | Draft privacy-preserving topic signal data model |
| CAND-016 | CONTENT_QUEUE | READ_ONLY_AUDIT | MEDIUM | No | Define signal-to-source-backed-content workflow |
| CAND-017 | CONTENT_PUBLISHER | PROTECTED_CHANGE | HIGH | Yes | Add GPT/community-derived content only after validation and review gates |

## Recommended Execution Order

### Phase 1 - Read-Only Discovery

Start here because these tasks reduce uncertainty without changing runtime behavior.

1. CAND-006: DB inventory for social_news/content boundaries.
2. CAND-007: Content candidate final-object vs copy audit.
3. CAND-009: Dashboard summary-query audit.
4. CAND-013: Community-source policy audit.
5. CAND-014: Local LLM boundary audit.

### Phase 2 - Guarded Planning

Use Phase 1 reports before starting these.

1. CAND-004: Duplicate type and representative grouping plan.
2. CAND-010: Content API/UI validation display plan.
3. CAND-011: Occupation content readiness decomposition.
4. CAND-015: Privacy-preserving topic-signal data model.
5. CAND-016: Signal-to-source-backed-content workflow.

### Phase 3 - Protected Implementation

Do not start these without explicit approval.

1. CAND-003 / CAND-008: Content-only final publishing path and direct social-news publish retirement.
2. CAND-012: Occupation/living/immigration publish rotation.
3. CAND-017: GPT/community-derived publish integration.

## Protected Area Notes

The following areas are protected or high-risk:

- `CONTENT_PUBLISHER`
- `FACEBOOK_PUBLISHER`
- `SCHEDULER_BOT_STATE`
- `ADMIN_AUTH`
- destructive or broad DB migration
- env/secret/token handling
- external community data collection with privacy or terms risk

For protected areas, the recommended default first step is `READ_ONLY_AUDIT`, not implementation.

## Source Walkthroughs

- `DOC/walkthrough/2026-06-11-harness-session-codex-harness-docs-0014.md`
- `DOC/walkthrough/2026-06-11-harness-session-db-architecture-docs-0017.md`
- `DOC/walkthrough/2026-06-11-harness-session-design-archive-docs-0019.md`
- `DOC/walkthrough/2026-06-11-harness-session-product-source-quality-0021.md`
