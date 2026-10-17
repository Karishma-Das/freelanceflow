import pandas as pd

truth = pd.read_csv("data/real/truth.csv", dtype=str).fillna("")
res = pd.read_csv("data/real/results.csv", dtype=str).fillna("")
df = truth.merge(res, on="filename", suffixes=("_t", "_p"))

def same(field, t, p):
    if p.strip() == "":
        return False
    if field == "amount":
        try:
            return abs(float(t) - float(p)) < 0.01
        except ValueError:
            return False
    if field == "party":
        return t.lower() in p.lower() or p.lower() in t.lower()
    return t.strip() == p.strip()

for field in ["amount", "date", "party"]:
    scored = correct = 0
    for _, row in df.iterrows():
        t, p = row[field + "_t"], row[field + "_p"]
        if t == "":
            continue
        scored += 1
        ok = same(field, t, p)
        correct += ok
        print(f"{row['filename']:15} {field:7} truth={t:25} model={p:25} {'OK' if ok else 'WRONG'}")
    if scored:
        print(f"--> {field} accuracy: {correct}/{scored}\n")