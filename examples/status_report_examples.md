# Status Report Generator — Few-Shot Examples

## Example 1 — Guardrail firing on missing budget

Input:
```
Project: Data Warehouse Upgrade
Schedule: On track, sprint 3 of 5 complete
Accomplishments: ETL pipeline rebuilt, QA environment live
Risk: Minor — vendor patch delayed one week
```

Output:
```
EXECUTIVE SUMMARY
Data Warehouse Upgrade is on schedule through sprint 3 of 5, with the ETL pipeline rebuilt and the QA environment live. A minor vendor patch delay has been flagged. Budget status is pending PM confirmation.

| Area            | Status      | Notes                          |
|-----------------|-------------|--------------------------------|
| Budget          | ⚠️ Watch     | MISSING — confirm with PM      |
| Schedule        | ✅ On Track  | Sprint 3 of 5 complete         |
| Accomplishments | ✅ On Track  | ETL rebuilt, QA env live       |
| Risk            | ⚠️ Watch     | Vendor patch delayed one week  |
```

## Example 2 — Standard happy path

Input:
```
Project: Website Redesign
Budget: 60% consumed, on track
Schedule: On track
Accomplishments: Wireframes approved, dev sprint 1 complete
Risk: None identified
```

Output:
```
EXECUTIVE SUMMARY
Website Redesign is progressing on schedule with budget at 60% utilization. Wireframes have been approved and the first development sprint is complete. No risks are currently identified.

| Area            | Status      | Notes                          |
|-----------------|-------------|--------------------------------|
| Budget          | ✅ On Track  | 60% consumed, within forecast  |
| Schedule        | ✅ On Track  | Aligned to baseline            |
| Accomplishments | ✅ On Track  | Wireframes approved, sprint 1  |
| Risk            | ✅ On Track  | No risks identified            |
```
