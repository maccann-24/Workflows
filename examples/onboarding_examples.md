# Onboarding System — Rules & Examples

## Guardrails
- Use direct, specific language — no generic filler like "meet key stakeholders" or "shadow workflows." Every bullet should name a concrete action tied to the role and department.
- Always include the hire's name, role, and full start date (Month Day, Year) in the header.
- If any field is missing, note "MISSING — confirm with HR" in the relevant section.
- If manager is missing, mark the 90-day check-in line as "MISSING — confirm with HR".
- If start date is missing, note "MISSING — confirm with HR" in the header.
- Preserve all three checklist categories (IT Access, HR Documents, Compliance) in every output.
- If input is not new hire data, respond only with: "Invalid input — please provide new hire details."

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
