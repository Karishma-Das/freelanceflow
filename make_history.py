import os
import numpy as np
import pandas as pd

np.random.seed(7)
os.makedirs("data/sample", exist_ok=True)

months = pd.period_range("2025-04", periods=18, freq="M")
rows = []
for i, m in enumerate(months):
    season = 8000 * np.sin(2 * np.pi * m.month / 12)
    income = 60000 + 700 * i + season + np.random.normal(0, 4000)
    expense = 25000 + 250 * i + 0.2 * season + np.random.normal(0, 2000)
    rows.append({"month": str(m), "income": round(income, 2), "expense": round(expense, 2)})

pd.DataFrame(rows).to_csv("data/sample/history.csv", index=False)
print("history.csv created with", len(rows), "months")