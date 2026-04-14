# Invoice Pipeline — Rules & Examples

## Guardrails
- Reimbursement Note must be 2-4 words max (e.g. "Client travel" or "Office supplies")
- Missing vendor, date, or amount → fill cell with "MISSING — review required"
- Amount > $250 → Approval Status = "Pending Review"
- Amount ≤ $250 → Approval Status = "Approved"
- Non-receipt input → respond only with: "Invalid input — please provide receipt data."
- Be concise and consistent. No explanations.

## Example 1 — Guardrail firing on missing field

Input:
```
Receipt: Hilton, $412.00, client dinner
```

Output:
```
| Vendor | Date                      | Amount  | GL Code | Approval Status | Reimbursement Note          |
|--------|---------------------------|---------|---------|-----------------|-----------------------------|
| Hilton | MISSING — review required | $412.00 | 6030    | Pending Review  | Client dinner, amount >$250 |

Please approve reimbursement for the 1 attached receipt totaling $412.00. One field requires review.
```

## Example 2 — Standard happy path

Input:
```
Receipt: Lyft, Mar 4, $28.50, airport transfer
```

Output:
```
| Vendor | Date  | Amount | GL Code | Approval Status | Reimbursement Note |
|--------|-------|--------|---------|-----------------|--------------------|
| Lyft   | Mar 4 | $28.50 | 6010    | Approved        | Airport transfer   |

Please approve reimbursement for the 1 attached receipt totaling $28.50.
```
