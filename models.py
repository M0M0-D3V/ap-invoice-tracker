from datetime import date
from enum import Enum

from pydantic import BaseModel


class InvoiceStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    APPROVED = "approved"
    REJECTED = "rejected"

class InvoiceCreate(BaseModel):
    vendor: str
    invoice_number: str
    amount: float
    due_date: date
    po_number: str | None = None

class Invoice(InvoiceCreate):
    id: int
    status: InvoiceStatus = InvoiceStatus.PENDING

class StatusUpdate(BaseModel):
    status: InvoiceStatus