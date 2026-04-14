# Email Triage — Few-Shot Examples

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
