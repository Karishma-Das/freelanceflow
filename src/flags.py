import pandas as pd


def unusual_spending(df, factor=3.0):
    """Flag an expense if it is more than `factor` times the median of its category.
    Needs at least 3 expenses in a category to judge."""
    d = df.copy()
    d["amount"] = pd.to_numeric(d["amount"], errors="coerce")
    d = d[(d["amount"] > 0) & (d["direction"].fillna("expense") == "expense")]
    d["category"] = d["category"].fillna("other")
    out = []
    for cat, g in d.groupby("category"):
        if len(g) < 3:
            continue
        med = g["amount"].median()
        for _, r in g.iterrows():
            if r["amount"] > factor * med:
                out.append({
                    "filename": r.get("filename", ""),
                    "category": cat,
                    "amount": r["amount"],
                    "reason": f"{r['amount']:.2f} is more than {factor:g}x the usual {med:.2f} for {cat}",
                })
    return pd.DataFrame(out, columns=["filename", "category", "amount", "reason"])