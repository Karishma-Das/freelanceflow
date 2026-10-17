import pandas as pd
from src.forecast import backtest, forecast_next

h = pd.read_csv("data/sample/history.csv")
months = h["month"].tolist()

for col in ["income", "expense"]:
    v = h[col].tolist()
    b, t = backtest(v, months)
    p, low, high, method, warning = forecast_next(v, months)
    print(f"\n=== {col.upper()} ===")
    print("Backtest error (lower is better):")
    print("  baseline (avg of last 3):", None if b is None else round(b))
    print("  TabPFN:", None if t is None else round(t))
    print(f"Next month: about {round(p)} (likely between {round(low)} and {round(high)})")
    print("Method used:", method)
    if warning:
        print("Warning:", warning)