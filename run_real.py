import glob, os
import pandas as pd
from src.extract import extract

rows = []
for p in sorted(glob.glob("data/real/*.png")):
    try:
        d = extract(p).model_dump()
    except Exception as e:
        d = {"error": str(e)[:60]}
    d["filename"] = os.path.basename(p)
    rows.append(d)

df = pd.DataFrame(rows)
df.to_csv("data/real/results.csv", index=False)
print(df.to_string())