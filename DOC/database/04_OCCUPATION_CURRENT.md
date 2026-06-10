
# 04_OCCUPATION_CURRENT.md

```md
# Occupation Current DB Reference

## 1. Purpose

The `occupation` schema stores Employment24 job and occupation dictionary data.

This is not a real-time job posting schema.

Its current role is to provide reference data for:

- job names
- occupation codes
- keyword mappings
- future content generation
- future GPT answer routing
- future visa/job matching hints

## 2. Current Scope

The occupation pipeline stores dictionary-like data from Employment24 APIs.

It should not be treated as:

- active job postings
- hiring data
- employer recruitment data
- immediately publishable Facebook content

## 3. Key Tables

### 3.1 occupation.job_info

Purpose:

Stores Employment24 job information dictionary records.

Expected usage:

- job code reference
- Korean job names
- category mapping
- future search keyword seed

### 3.2 occupation.occupation_info

Purpose:

Stores occupation dictionary records.

Expected usage:

- occupation code reference
- occupation name
- occupation grouping
- future English translation
- future visa/job/living content enrichment

### 3.3 occupation.keyword_mapping

Purpose:

Maps occupation/job names to useful keywords.

Expected usage:

- search keyword generation
- multilingual keyword expansion
- content generation seed
- GPT Connect routing

### 3.4 occupation.collect_log

Purpose:

Stores collection execution logs.

Expected usage:

- collection success/failure
- started/ended time
- parsed count
- error message

### 3.5 occupation.raw_api_response

Purpose:

Preserves raw Employment24 API responses.

Expected usage:

- audit
- parser debugging
- reprocessing
- source verification

## 4. Current Logical ERD

```mermaid
erDiagram
    occupation_raw_api_response ||--o{ occupation_job_info : parsed_to
    occupation_raw_api_response ||--o{ occupation_occupation_info : parsed_to
    occupation_job_info ||--o{ occupation_keyword_mapping : may_have_keywords
    occupation_occupation_info ||--o{ occupation_keyword_mapping : may_have_keywords
    occupation_collect_log ||--o{ occupation_raw_api_response : collects
````

Note:

This is a logical ERD.
Actual physical FK constraints must be verified.

## 5. Current Data Meaning

Occupation data is a dictionary.

Example data may include:

```text
항공기 정비원
번역가
외국어 강사
제관원
```

These records are useful but incomplete.

They usually need enrichment before becoming user-facing content.

## 6. Required Enrichment Before Publishing

Before occupation data can become content candidate, it needs fields such as:

```text
occupation_name_en
search_keywords_en
industry_tags
possible_visa_tags
foreign_worker_fit
content_potential_score
content_ready_yn
source_confidence
```

Important:

Visa tags must be presented as possible relevance, not legal certainty.

## 7. Relationship to Content

Current intended future flow:

```text
occupation.occupation_info
→ enrichment
→ content.content_candidate
```

Possible content types:

```text
OCCUPATION_GUIDE
JOB_DICTIONARY_GUIDE
VISA_RELATED_JOB_GUIDE
```

Occupation data should not be automatically posted without enrichment.

## 8. Current Problems to Verify

### 8.1 Sparse Detail

Many occupation records may have only code/name and lack detailed descriptions.

### 8.2 Korean-Only Data

The raw source is likely Korean-first.

English name and explanation should be generated and reviewed.

### 8.3 No Direct Hiring Meaning

Do not display occupation dictionary data as if it were job openings.

### 8.4 Content Readiness

Need a clear `content_ready_yn` or equivalent before syncing to content.

### 8.5 API Permission Boundary

Employment24 job posting API may require enterprise/member permissions.

Do not assume job posting access is available.

## 9. Safe Uses

Safe current uses:

* admin reference screen
* keyword mapping
* future GPT answer routing
* search seed
* content enrichment queue

Unsafe current uses:

* automatic Facebook posting
* active job listing display
* visa eligibility guarantee
* employer recruitment claim

## 10. Risk Level

Risk level:

```text
LOW-MEDIUM
```

Safe changes:

* read-only UI improvements
* pagination
* keyword mapping
* enrichment draft fields
* collect log display

Requires approval:

* bulk data rewrite
* auto-sync to content
* visa tag generation as authoritative data
* public-facing occupation guide publishing

````

---
