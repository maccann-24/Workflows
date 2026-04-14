# Morning Briefing Orchestrator — Few-Shot Example

## Example 1 — Guardrail firing on missing field + visible composition across all 5 types

Input:
```
1. Receipt: Lyft, Apr 8, $41.20, client pickup
2. Email — From: CEO: "Need revised headcount plan before 4pm."
3. New hire: Priya Shah, Role: PM, Dept: Product, Start: Apr 20
4. Project: Vendor Portal — Budget 45% consumed, Schedule on track, Risk: none
5. Research: Halcyon Federal — ~40 employees, DoD subcontractor, HQ Arlington
```

Output:
```
MORNING BRIEFING — April 9, 2026
Queue: 5 items routed (1 expense, 1 email, 1 hire, 1 project, 1 research)

EXPENSES
| Vendor | Date  | Amount | GL   | Status   | Note          |
|--------|-------|--------|------|----------|---------------|
| Lyft   | Apr 8 | $41.20 | 6010 | Approved | Client pickup |

HIRES
ONBOARDING PLAN — Priya Shah | PM | Start: Apr 20 | Manager: MISSING — review required
30: HR orientation, meet Product team, shadow current PM rituals
60: Own first sprint review, attend leadership standup
90: Lead one end-to-end release, 90-day check-in
IT: ☐ Laptop ☐ Email ☐ Jira   HR: ☐ I-9 ☐ Benefits   Compliance: ☐ Security ☐ Privacy

PROJECTS
Vendor Portal is on track; budget at 45%, no risks identified.
| Area     | Status     | Notes               |
|----------|------------|---------------------|
| Budget   | ✅ On Track | 45% consumed        |
| Schedule | ✅ On Track | Aligned to baseline |
| Risk     | ✅ On Track | None identified     |

INBOX
| From | Category  | Draft Reply                                                 |
|------|-----------|-------------------------------------------------------------|
| CEO  | 🔴 Urgent | "On it — revised headcount plan to you before 4pm today."   |

RESEARCH
SOURCING MATRIX — Halcyon Federal
Overview: ~40-person DoD subcontractor, HQ Arlington VA.
Revenue Fit: MISSING — verify via outreach (no disclosed revenue).
Risks: ⚠️ Small team, single-agency exposure.
Recommendation: 🟡 Monitor — validate pipeline before pursuing.
```
