# Onboarding System — Few-Shot Examples

## Example 1 — Guardrail firing on missing manager

Input:
```
Name: John Park
Role: Data Analyst
Department: Finance
Start Date: May 1, 2026
Manager:
```

Output:
```
ONBOARDING PLAN — John Park | Data Analyst | Start: May 1, 2026

30 DAYS — Learn & Orient
• Complete HR orientation and benefits enrollment
• Meet direct team and key stakeholders
• Shadow existing reporting workflows

60 DAYS — Contribute
• Own first monthly data report
• Attend Finance standups independently

90 DAYS — Lead
• Present findings from first full reporting cycle
• Complete 90-day check-in with MISSING — confirm with HR

IT Access
• Laptop
• Email
• System logins

HR Documents
• Offer letter
• Direct deposit
• I-9 / W-4

Compliance
• Security training
• Data privacy policy
• Code of conduct
```

## Example 2 — Standard happy path

Input:
```
Name: Priya Raman
Role: Product Manager
Department: Product
Start Date: June 3, 2026
Manager: David Chen
```

Output:
```
ONBOARDING PLAN — Priya Raman | Product Manager | Start: June 3, 2026

30 DAYS — Learn & Orient
• Complete HR orientation and benefits enrollment
• Meet product, design, and engineering leads
• Shadow active sprint rituals and roadmap reviews

60 DAYS — Contribute
• Own backlog grooming for one product area
• Publish first competitive landscape brief

90 DAYS — Lead
• Present Q3 roadmap proposal
• Complete 90-day check-in with David Chen

IT Access
• Laptop
• Email
• System logins

HR Documents
• Offer letter
• Direct deposit
• I-9 / W-4

Compliance
• Security training
• Data privacy policy
• Code of conduct
```
