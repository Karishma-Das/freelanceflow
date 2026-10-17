import glob, os, time
import pandas as pd
from src.extract import extract
from src.validate import validate

rows = []
for p in sorted(glob.glob("data/real/*.png")):
    t0 = time.time()
    try:
        d = extract(p).model_dump()
    except Exception as e:
        d = {"error": str(e)[:60]}
    d["seconds"] = round(time.time() - t0, 1)
    d["filename"] = os.path.basename(p)
    rows.append(d)

df = pd.DataFrame(rows)
df = df.astype(object).where(df.notna(), None)   # turn empty cells into real "missing"

checks = df.apply(lambda r: validate(r.to_dict()), axis=1)
df["needs_review"] = [c["needs_review"] for c in checks]
df["reasons"] = ["; ".join(c["reasons"]) for c in checks]

df.to_csv("data/real/results.csv", index=False)
print(df[["filename", "date", "party", "amount", "needs_review", "reasons"]].to_string())
print("Average seconds per receipt:", round(df["seconds"].astype(float).mean(), 1))
print("Flagged for review:", int(df["needs_review"].sum()), "of", len(df))