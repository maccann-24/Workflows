# Invoice Pipeline — Few-Shot Examples

Note: This workflow accepts receipt data as text OR as images of receipts. If given an image, extract vendor, date, amount, and category before processing.

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
