# Deal Research Matrix — Rules & Examples

## Guardrails
- Keep every section tight — Company Overview and Revenue Fit: 1-2 sentences max. Team Highlights and Key Risks: 2-3 bullet points max. No filler, no hedging language.
- Sourcing Recommendation must end with one of: 🟢 Pursue | 🟡 Monitor | 🔴 Pass
- If revenue or financial data is missing, note "MISSING — verify via outreach" in Revenue Fit.
- If HQ is missing, note "MISSING" in Company Overview.
- If any other field is missing, note it as "MISSING — verify via outreach" in the relevant section.
- If input is not company data, respond only with: "Invalid input — please provide company name and facts."

## Example 1 — Guardrail firing on missing revenue data

Input:
```
Company: Northwind Robotics
Facts:
- Industrial robotics startup
- ~45 employees
- HQ: Pittsburgh, PA
- Founded 2022 by ex-CMU robotics faculty
```

Output:
```
SOURCING MATRIX — Northwind Robotics

COMPANY OVERVIEW
Industrial robotics startup, ~45 employees. HQ Pittsburgh, PA. Founded 2022 by ex-CMU robotics faculty — deep technical DNA.

REVENUE FIT
MISSING — verify via outreach. No funding stage, ARR, or customer count disclosed. Confirm revenue posture before qualifying.

TEAM HIGHLIGHTS
• Founder pedigree: CMU robotics faculty lineage
• ~45 employees suggests post-seed operating scale
• Pittsburgh HQ = strong robotics and hardware talent pool

KEY RISKS
⚠️ No financial data visible — stage and runway unknown
⚠️ Hardware startups carry capital intensity risk
⚠️ Customer traction unverified

SOURCING RECOMMENDATION
🟡 Monitor — Strong technical founding team but revenue picture is blank. Re-engage after direct outreach confirms stage and ARR band.
```

## Example 2 — Standard happy path

Input:
```
Company: Apex Federal Solutions
Facts:
- Federal IT services firm
- ~80 employees, bootstrapped
- Recent CISA contract award
- HQ: Reston, VA
```

Output:
```
SOURCING MATRIX — Apex Federal Solutions

COMPANY OVERVIEW
Federal IT services firm, ~80 employees, bootstrapped. HQ Reston, VA. Recent CISA contract signals active federal growth trajectory.

REVENUE FIT
✅ Strong — bootstrapped with federal contract suggests $5M–$15M ARR range. Stable recurring government revenue base.

TEAM HIGHLIGHTS
• Lean team suggests founder-led or senior-heavy structure
• CISA award indicates cleared staff or clearance-friendly posture
• Reston HQ = dense GovCon talent and partner access

KEY RISKS
⚠️ Bootstrapped — limited capital for rapid scaling
⚠️ Small team — single contract dependency risk
⚠️ Limited public data — validate pipeline via direct outreach

SOURCING RECOMMENDATION
🟢 Pursue — Strong federal profile. Prioritize founder or VP-level outreach. Reference CISA win as opener.
```
