from datetime import date

ALLOWED_CATEGORIES = {"software", "travel", "food", "office", "other"}

def validate(rec: dict) -> dict:
    reasons = []
    d = rec.get("date")
    if not d:
        reasons.append("missing date")
    else:
        try:
            dd = date.fromisoformat(str(d))
            if dd > date.today():
                reasons.append("date in the future")
            elif (date.today() - dd).days > 365 * 5:
                reasons.append("date older than 5 years")
        except ValueError:
            reasons.append("bad date format")

    amt = rec.get("amount")
    if amt is None or amt != amt:      # None or NaN
        reasons.append("missing amount")
    elif amt <= 0:
        reasons.append("amount zero or negative")

    cat = rec.get("category")
    if cat and cat not in ALLOWED_CATEGORIES:
        reasons.append("unknown category")

    party = rec.get("party")
    if not party:
        reasons.append("missing store name")

    tax, amt2 = rec.get("tax"), rec.get("amount")
    if tax and amt2 and tax > amt2:
        reasons.append("tax bigger than amount")

    return {"needs_review": len(reasons) > 0, "reasons": reasons}