from pydantic import BaseModel
from typing import Optional, Literal

class Record(BaseModel):
    doc_type: Literal["receipt", "invoice", "bank_transaction"]
    date: Optional[str] = None
    party: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    tax: Optional[float] = None
    direction: Optional[Literal["income", "expense"]] = None