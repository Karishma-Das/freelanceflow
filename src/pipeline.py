import os, tempfile
from src.extract import extract
from src.pdf_utils import pdf_to_images

def process_file(path):
    """Returns a list of (name, Record). A PDF gives one record per page."""
    ext = os.path.splitext(path)[1].lower()
    base = os.path.basename(path)
    results = []

    if ext == ".pdf":
        with tempfile.TemporaryDirectory() as tmp:
            pages = pdf_to_images(path, os.path.join(tmp, "page"))
            for p in pages:
                name = f"{base} ({os.path.basename(p)})"
                results.append((name, extract(p)))
    elif ext in (".png", ".jpg", ".jpeg"):
        results.append((base, extract(path)))
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return results