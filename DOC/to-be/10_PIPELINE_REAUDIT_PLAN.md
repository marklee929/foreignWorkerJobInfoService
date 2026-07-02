# Pipeline Re-Audit Plan

## Purpose

This document defines recurring re-audits for WorkConnect's long-running coding pipeline.

The goal is to prevent repeated investigation resets and ensure Codex continues from saved execution-history.

## Mandatory Re-Audit Sequence

Every re-audit must follow:

```text
1. Read active architecture docs.
2. Read today's execute prompt.
3. Read latest execution-history for the same AREA.
4. Read related previous reports.
5. Compare previous findings with current behavior.
6. Identify what changed.
7. Produce bounded CODE_TASK_CANDIDATE items.
8. Save the audit report.
```

If the same issue was already audited, continue from the latest saved finding instead of restarting from scratch.

## Required Audit Dimensions

### 1. Purpose Alignment

Check:

- whether the task still serves WorkConnect's work-and-settlement purpose
- whether generic news, travel, economy, politics, or crypto content is drifting into review/publish paths
- whether current target country scope is respected

### 2. Lifecycle Failure Layer

Classify the earliest failing layer:

```text
source discovery
-> raw collection
-> normalization
-> duplicate classification
-> domain classification
-> user value evaluation
-> content candidate
-> review eligibility
-> public delivery or operation notification
```

Do not propose one-off title or URL patches when the failure is lifecycle-level.

### 3. Source and Evidence Continuity

Check:

- source URL
- canonical URL
- source name
- original body or structured data
- raw reference table/id
- duplicate key
- prior collection logs

### 4. Implementation Continuity

Before implementation, read:

- today's audit report
- latest same-AREA report
- related previous reports
- current code
- current tests

Then decide whether the previous implementation plan still applies.

### 5. Protected Boundary Continuity

Check that the next task does not touch:

- `ADMIN_AUTH`
- `FACEBOOK_PUBLISHER`
- `CONTENT_PUBLISHER`
- `SCHEDULER_BOT_STATE`
- env/secrets/token handling
- destructive DB migration
- Telegram production behavior
- external API behavior

## Report Requirements

Reports must distinguish:

- audit findings
- design decisions
- implementation changes
- verification results
- rollback/retry results
- remaining risks
- next task

## Re-Audit Report Template

```text
# Pipeline Re-Audit Report

## 1. AREA / MODE / PURPOSE FUNCTION
## 2. Reports Re-Read
## 3. Current Behavior
## 4. Previous Findings Reused
## 5. New Findings
## 6. Earliest Failure Layer
## 7. Protected Boundary Result
## 8. CODE_TASK_CANDIDATE
## 9. Restart / Reload
```

## Stop Conditions

Stop when:

- previous reports conflict and safety impact is unclear
- implementation would require protected areas
- destructive DB changes are required
- external publishing behavior would change
- ownership ambiguity would be decided silently

## Success Criteria

- Re-audit continues from saved history.
- Same issue is not re-investigated from zero.
- Every audit either produces a bounded next task or explains why no safe next task exists.
