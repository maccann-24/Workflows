# Email Triage — Rules & Examples

## Guardrails
- Categories: 🔴 Urgent (same-day response) | 🟡 Action (response needed, not same-day) | 🟢 Info (no reply needed)
- Classify by content, not sender title alone.
- C-suite or client sender WITH an action verb or deadline → 🔴 Urgent
- C-suite or client sender with clearly informational content (FYI, heads-up, recap) → 🟢 Info
- Explicit "no action needed" language → 🟢 Info with empty draft reply
- Ambiguous category → default to 🟡 Action
- Draft replies only for 🔴 Urgent and 🟡 Action rows. Leave Draft Reply blank for 🟢 Info.
- If input is not email data, respond only with: "Invalid input — please provide email snippets."

## Example 1 — Info-category C-suite email (proves triage isn't over-flagging)

Input:
```
From: CEO: "FYI team — board meeting went well yesterday, no action needed from anyone. Sharing the recap deck for visibility only."
```

Output:
```
| From | Category | Draft Reply |
|------|----------|-------------|
| CEO  | 🟢 Info  |             |
```

## Example 2 — Standard urgent case

Input:
```
From: CEO: "Need the board deck updated before tomorrow's 9am call."
```

Output:
```
| From | Category  | Draft Reply                                                          |
|------|-----------|----------------------------------------------------------------------|
| CEO  | 🔴 Urgent | "Understood — I'll have the board deck updated before 9am tomorrow." |
```
