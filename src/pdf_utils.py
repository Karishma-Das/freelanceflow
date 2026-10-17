import pymupdf as fitz # PyMuPDF

def pdf_to_images(pdf_path, out_prefix, max_pages=3):
    doc = fitz.open(pdf_path)
    paths = []
    for i, page in enumerate(doc):
        if i >= max_pages:      # limit pages so it stays fast
            break
        pix = page.get_pixmap(dpi=150)
        path = f"{out_prefix}_p{i+1}.png"
        pix.save(path)
        paths.append(path)
    return paths