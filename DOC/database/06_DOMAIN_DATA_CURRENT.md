# 06_DOMAIN_DATA_CURRENT.md

````md
# Domain Data Current DB Reference

## 1. Purpose

This document describes current domain-specific data schemas outside of social news, content, occupation, and admin/ops.

Domain data means collected or planned data related to foreign workers' life, immigration, visa, employment, housing, healthcare, banking, transportation, and other settlement information.

The current domain data area is expected to grow over time.

## 2. Domain Data Role

Domain schemas are source/domain storage areas.

They should store collected, normalized, or official data before it becomes a publishable content candidate.

The intended flow is:

```text
domain source
→ domain raw/normalized table
→ domain candidate or official notice
→ content.content_candidate
→ content.publish_log
````

Domain data should not publish directly to Facebook.

## 3. Expected Domain Schemas

Current or planned domain schemas may include:

```text
immigration_info
living_info
visa_info
employment_info
government_notice
local_support
healthcare_info
housing_info
banking_info
transportation_info
```

Not all schemas may exist yet.

This document records the current state and clarifies future responsibilities.

## 4. Immigration Info

### Purpose

The immigration domain stores official notices and information related to:

* visa
* stay status
* immigration policy
* foreign resident policy
* government announcements
* official administrative guidance

### Expected Source Priority

Primary sources:

* Ministry of Justice
* HiKorea
* Korea Immigration Service
* EPS
* Ministry of Employment and Labor when related to foreign employment
* Korea.net official notices when applicable

### Current Expected Table Types

Possible tables:

```text
immigration_info.official_notice
immigration_info.collect_log
immigration_info.raw_item
```

### Publishing Rule

Immigration information can be legally or administratively sensitive.

Default policy:

```text
official notice
→ READY_TO_REVIEW
→ content candidate
→ manual or guarded publish
```

Automatic publishing should be conservative.

## 5. Living Info

### Purpose

The living domain stores settlement and life information useful for foreigners in Korea.

Possible topics:

* housing
* banking
* healthcare
* national health insurance
* transportation
* mobile service
* cost of living
* Korean language support
* local community
* emergency/safety information

### Current Expected Table Types

Possible future tables:

```text
living_info.item
living_info.source
living_info.category
living_info.collect_log
living_info.raw_item
```

### Publishing Rule

Living information may become content if it is practical, source-backed, and not misleading.

Examples:

```text
How foreigners can open a bank account in Korea
How national health insurance works for foreign residents
Where to find foreign resident support centers
```

## 6. Visa Info

### Purpose

The visa domain stores structured information about visa types and work eligibility.

Possible visa categories:

```text
E-7
E-9
D-2
D-10
F-2
F-4
F-5
F-6
H-2
```

### Rule

Visa information must not be presented as legal certainty unless backed by official sources.

Any generated explanation should include source reference and caution.

## 7. Employment Info

### Purpose

The employment domain may later store job posting or labor market data.

Important distinction:

```text
occupation = job/occupation dictionary
employment = actual hiring or employment-related opportunity data
```

Employment24 job posting API access may require business/member permission.

Do not assume job posting API is available.

## 8. Domain Data to Content Mapping

Domain data becomes publishable only through `content.content_candidate`.

Expected mapping:

| Domain Source                      | Content source_domain | Content type                               |
| ---------------------------------- | --------------------- | ------------------------------------------ |
| `immigration_info.official_notice` | `IMMIGRATION_INFO`    | `IMMIGRATION_NOTICE` / `GOVERNMENT_NOTICE` |
| `living_info.item`                 | `LIVING_INFO`         | `LIVING_GUIDE`                             |
| `visa_info.item`                   | `VISA_INFO`           | `VISA_GUIDE`                               |
| `occupation.occupation_info`       | `OCCUPATION_INFO`     | `OCCUPATION_GUIDE`                         |
| `employment_info.item`             | `EMPLOYMENT_INFO`     | `JOB_NOTICE` / `EMPLOYMENT_GUIDE`          |

## 9. Current Problems to Verify

### 9.1 Empty or Prototype Schemas

Some domain schemas may exist only as placeholders.

They should be marked as:

```text
PLANNED
PARTIAL
ACTIVE
DEPRECATED
```

### 9.2 Direct Publishing Risk

No domain table should publish directly to Facebook.

All public posting must pass through content candidate validation.

### 9.3 Official Source Sensitivity

Government/immigration data should be reviewed carefully before publishing.

### 9.4 Generated Content Risk

Generated summaries should not replace official source meaning.

### 9.5 Missing Source Metadata

Domain data must preserve:

* source name
* source URL
* original published date
* collected date
* language
* source trust level

## 10. Risk Level

Risk level:

```text
MEDIUM
```

Safe changes:

* source inventory
* read-only admin views
* collect log display
* schema documentation
* non-destructive indexes

Requires approval:

* automatic publishing
* legal/visa interpretation generation
* bulk backfill into content
* destructive migration

````

---
