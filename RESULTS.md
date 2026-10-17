# Results

Test set: 7 real receipts (private, not in the repo), mixed quality. Model: gemma3:4b, run locally.

| Field | Correct |
|---|---|
| Amount | 6/7 |
| Date | 4/4 (receipts where the answer key has a date) |
| Store name | 3/3 (receipts where the answer key has a store name) |

- Average time per receipt: 179.5 seconds (CPU, no API cost)
- Flagged for review: 6 of 7
- Answer key corrected for receipts 2 and 3: the store name is The Home Depot, not its slogan.
- Known failures:
  - receipt_3: amount read as -354.83 (truth 54.83). Caught by the "amount zero or negative" rule.
  - receipt_4: unreadable image, but the model still returned amount 13.0 and a wrong store name. Validation flagged it only for a missing date.
  - receipt_5, 6, 7: store name not found by the model.
- Validation: 4 pytest tests passing
- Limits: small test set (7 receipts), gemma3:4b model, slow on CPU, no duplicate check, no database