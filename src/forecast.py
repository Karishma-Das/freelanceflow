import numpy as np
import pandas as pd

LAST_ERROR = ""          # remembers why TabPFN failed, if it did


def monthly_totals(df):
    """Records (date, amount, direction) -> one row per month with income and expense."""
    d = df.copy()
    d["amount"] = pd.to_numeric(d["amount"], errors="coerce")
    d = d[d["date"].notna() & d["amount"].notna()]
    if d.empty:
        return pd.DataFrame(columns=["month", "income", "expense"])
    d["month"] = pd.to_datetime(d["date"], errors="coerce").dt.to_period("M").astype(str)
    d["direction"] = d["direction"].fillna("expense")
    t = d.pivot_table(index="month", columns="direction", values="amount",
                      aggfunc="sum", fill_value=0.0)
    for c in ["income", "expense"]:
        if c not in t.columns:
            t[c] = 0.0
    return t[["income", "expense"]].reset_index()


def baseline(values, n=3):
    """Next month = average of the last n months."""
    return float(np.mean(values[-n:]))


def make_features(values, months):
    """Each row: [month number, previous month, average of the 3 months before]."""
    X, y = [], []
    for i in range(3, len(values)):
        X.append([int(months[i][5:7]), values[i - 1], np.mean(values[i - 3:i])])
        y.append(values[i])
    next_num = int(months[-1][5:7]) % 12 + 1
    last = [next_num, values[-1], np.mean(values[-3:])]
    return np.array(X, dtype=float), np.array(y, dtype=float), np.array([last], dtype=float)


def tabpfn_forecast(values, months):
    global LAST_ERROR
    try:
        from tabpfn import TabPFNRegressor
        X, y, last = make_features(values, months)
        model = TabPFNRegressor()
        model.fit(X, y)
        return float(model.predict(last)[0])
    except Exception as e:
        LAST_ERROR = str(e)[:200]
        return None


def backtest(values, months, test_n=4):
    """Hide the last test_n months one by one. Returns (baseline error, TabPFN error)."""
    base_err, pfn_err = [], []
    for k in range(test_n, 0, -1):
        train_v, train_m = values[:-k], months[:-k]
        if len(train_v) < 6:
            continue
        actual = values[-k]
        base_err.append(abs(baseline(train_v) - actual))
        p = tabpfn_forecast(train_v, train_m)
        if p is not None:
            pfn_err.append(abs(p - actual))
    b = float(np.mean(base_err)) if base_err else None
    t = float(np.mean(pfn_err)) if len(pfn_err) == len(base_err) and pfn_err else None
    return b, t


def forecast_next(values, months):
    """Returns (prediction, low, high, method, warning)."""
    values = [float(v) for v in values]
    if len(values) < 3:
        return None, None, None, "not enough data", "Need at least 3 months of data."

    warning = ""
    if len(values) < 6:
        warning = "Less than 6 months of data, treat this as rough."

    p, method = None, "average of last 3 months"
    if len(values) >= 6:
        p = tabpfn_forecast(values, months)
        if p is not None:
            method = "TabPFN"
        elif LAST_ERROR:
            warning = (warning + " TabPFN failed, used the simple average. Reason: " + LAST_ERROR).strip()
    if p is None:
        p = baseline(values)

    spread = float(np.std(values[-6:]))
    return p, max(p - spread, 0.0), p + spread, method, warning