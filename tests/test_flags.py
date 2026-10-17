import pandas as pd
from src.flags import unusual_spending

def test_big_expense_flagged():
    df = pd.DataFrame({
        "filename": list("abcd"),
        "category": ["food"] * 4,
        "direction": ["expense"] * 4,
        "amount": [10, 12, 11, 100],
    })
    r = unusual_spending(df)
    assert list(r["filename"]) == ["d"]

def test_normal_expenses_not_flagged():
    df = pd.DataFrame({
        "filename": list("abc"),
        "category": ["food"] * 3,
        "direction": ["expense"] * 3,
        "amount": [10, 12, 11],
    })
    assert unusual_spending(df).empty