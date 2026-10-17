from src.validate import validate

good = {"date": "2026-03-18", "party": "Shop", "amount": 10.0, "category": "food"}

def test_good_record_passes():
    assert validate(good)["needs_review"] is False

def test_negative_amount_flagged():
    r = validate({**good, "amount": -354.83})
    assert "amount zero or negative" in r["reasons"]

def test_future_date_flagged():
    r = validate({**good, "date": "2999-01-01"})
    assert "date in the future" in r["reasons"]

def test_missing_date_flagged():
    r = validate({**good, "date": None})
    assert "missing date" in r["reasons"]