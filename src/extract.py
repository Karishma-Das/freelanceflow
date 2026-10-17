import io, re
from datetime import date
from typing import Optional

import ollama
from PIL import Image
from pydantic import BaseModel
from src.schema import Record

MODEL = "gemma3:4b"

class Header(BaseModel):
    all_text: str                    # first: read everything
    party: Optional[str] = None      # then: store name
    date_text: Optional[str] = None  # then: date exactly as printed

AMOUNT_PROMPT = """This is a photo of a receipt. Extract these fields:
- amount: the final TOTAL paid, a number only.
- category: one of software, travel, food, office, other.
- direction: "expense".
- doc_type: "receipt".
Use null only if truly not visible. Do not guess."""

HEADER_PROMPT = """This is a photo of a receipt. Do these in order:
1. all_text: copy all the text you can read, line by line.
2. party: the store or company name, usually printed at the top or in the logo.
3. date_text: the purchase date exactly as printed (for example 03/18/2026 or 01-01-2018).
If you cannot read something, use null. Do not invent anything."""

def prepare_image(path):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    if w < 1200:                                  # enlarge small images
        s = 1200 / w
        img = img.resize((int(w * s), int(h * s)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def parse_date(text):
    """Find a date in text and return YYYY-MM-DD, or None."""
    if not text:
        return None
    m = re.search(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", text)
    if m:
        y, mo, d = map(int, m.groups())
    else:
        m = re.search(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4}|\d{2})\b", text)
        if not m:
            return None
        a, b, y = m.groups()
        a, b, y = int(a), int(b), int(y)
        if y < 100:
            y += 2000
        mo, d = (b, a) if a > 12 else (a, b)    # default is MM/DD (US style)
    try:
        return date(y, mo, d).isoformat()
    except ValueError:
        return None

def chat(prompt, img, schema):
    r = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt, "images": [img]}],
        format=schema.model_json_schema(),
        options={"temperature": 0, "num_ctx": 8192},
    )
    return schema.model_validate_json(r["message"]["content"])

def extract(image_path):
    img = prepare_image(image_path)
    rec = None
    for attempt in range(2):
        try:
            rec = chat(AMOUNT_PROMPT, img, Record)
            break
        except Exception:
            if attempt == 1:
                raise
    try:
        head = chat(HEADER_PROMPT, img, Header)
        rec.date = parse_date(head.date_text) or parse_date(head.all_text)
        rec.party = head.party
    except Exception:
        pass                       # keep amount even if header step fails
    return rec