# Source Collection Audit Plan

## Purpose

This document defines the source collection audit path for WorkConnect.

It focuses on source evidence, duplicate handling, domain classification, and promotion gates before content generation or public review.

## Required History Read

Before source collection implementation, Codex must read:

- today's source audit report
- latest `SOCIAL_NEWS_COLLECTOR` report
- latest `SOCIAL_NEWS_CANDIDATE` report
- latest `LIVING_DOMAIN` report
- latest `IMMIGRATION_DOMAIN` report
- related execution-history for duplicate, low-relevance, or missing-body issues

Implementation must not begin until source audit findings are saved and re-read.

## Audit Scope

Source domains:

- employment sources
- visa and immigration sources
- living information sources
- community and public trend signals
- trusted media and news sources
- occupation dictionary sources

## Source Evidence Checklist

Each item should preserve:

- `source_name`
- `source_url`
- `canonical_url`
- `publishable_link_url`
- original title
- original body or structured data
- summary or snippet when body is not available
- published date
- collected date
- source type
- language
- target country
- raw payload
- duplicate key or hash where available

Missing evidence should block or downgrade promotion.

## Promotion Gate

Before a source item becomes a content candidate:

```text
valid source evidence
-> usable link or structured official data
-> enough body/metadata
-> target country fit
-> WorkConnect user need
-> duplicate classification
-> source trust level
-> sensitivity review
-> content candidate readiness
```

## Duplicate Handling

Classify duplicates as:

- `exact duplicate`
- `silent duplicate`
- `duplicate signal`
- `update duplicate`

Same URL repeats are usually noise. Same topic from multiple reliable sources may be signal.

## Community Signal Rule

Community and trend sources are signal-first.

Rules:

- store topic signal, not personal story as public content
- avoid personal identifiers
- avoid private or access-controlled content
- validate factual claims against primary or trusted sources
- do not quote user comments directly in public content without a clear policy

## Official Notice Attachment Rule

If an official notice has ZIP/PDF/HWP/HWPX/DOC/DOCX/XLS/XLSX attachments:

- preserve attachment metadata
- do not publish from generic attachment text
- inspect or extract document content before domain classification
- use review/evidence-only state until contents are understood

## Report Requirements

Reports must distinguish:

- audit findings
- design decisions
- implementation changes
- verification results
- rollback/retry results
- remaining risks
- next task

## CODE_TASK_CANDIDATE Requirement

Every source audit must produce at least one bounded `CODE_TASK_CANDIDATE`, unless no safe next task exists.

Each candidate must include:

```text
AREA:
MODE:
PURPOSE FUNCTION:
FOCUS:
WHY:
ALLOWED:
FORBIDDEN:
VERIFICATION:
STOP CONDITIONS:
```

## Success Criteria

- Source evidence is preserved.
- Weak or irrelevant sources do not become public review items.
- Duplicates are classified before promotion.
- Community data remains signal-first.
- Implementation continues from saved audit history.
