# FreelanceFlow

A privacy-first AI bookkeeper for freelancers. A local open-source vision model (Gemma 3 4B via Ollama) reads receipts, my own validation rules flag bad records, and the app exports a clean CSV, shows a forecast and flags unusual spending. Documents are read on your own computer.

## What it does
1. Upload receipt images (PNG/JPG) or PDFs.
2. Gemma extracts amount, date, store name and category.
3. Validation rules flag records for human review.
4. Edit the table, then download a CSV.
5. Forecast next month's income and expenses.
6. Alerts for unusual spending.

## Results (measured)
Test set: 7 real receipts of mixed quality (kept private, not in this repo).

| Field | Correct |
|---|---|
| Amount | 6/7 |
| Date | 4/4 (receipts where the answer key has a date) |
| Store name | 3/3 (receipts where the answer key has a store name) |

- Average time per receipt: 179.5 seconds on a laptop CPU (no API cost)
- Flagged for review: 6 of 7
- 6 pytest tests passing (validation rules and spending flag)

See RESULTS.md for details.

## What failed
- receipt_3: amount read as -354.83 (truth 54.83). Caught by the "amount zero or negative" rule.
- receipt_4: unreadable image, yet the model returned an amount and a wrong store name. Validation did not catch the wrong store name.
- Store name missed on three receipts.

## Forecast
Tested on a **synthetic** 18-month history, not real freelancer data. Uses TabPFN when its license is accepted on the computer, otherwise falls back to a 3-month average. In my test run the fallback was used (baseline backtest error: income 7960, expense 2026). TabPFN is licensed for non-commercial use, so check its terms before any commercial use.

## Install
1. Install Python 3.11+ and [Ollama](https://ollama.com).
2. `ollama pull gemma3:4b`
3. `python -m venv venv`, then activate it (`source venv/Scripts/activate` in Git Bash on Windows)
4. `pip install pymupdf pydantic pandas streamlit ollama pytest pillow tabpfn`
5. `python make_history.py` (creates the demo history)
6. `streamlit run app.py`

## Limitations
- Small test set (7 receipts).
- Slow on CPU, about 3 minutes per receipt.
- PDF support tested on 1 file only.
- No duplicate check, no database, late-payer detection not built.
- Forecast not tested on real data.
- Not tax or accounting advice.

## Next steps
Local forecasting, multi-currency, duplicate detection, SQLite storage, late-payer alerts, a bigger test set.