from src.pipeline import process_file

for name, rec in process_file("data/real/receipt_1.pdf"):
    print(name, rec.model_dump())