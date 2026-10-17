import ollama
r = ollama.chat(
    model="gemma3:4b",
    messages=[{
        "role": "user",
        "content": "What is the total amount on this receipt?",
        "images": ["data/real/receipt_1.png"],
    }],
)
print(r["message"]["content"])