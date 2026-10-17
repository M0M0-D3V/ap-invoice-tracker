from datetime import date
from enum import Enum

from pydantic import BaseModel


class InvoiceStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    APPROVED = "approved"
    REJECTED = "rejected"

class InvoiceCreate(BaseModel):
    vendor: str
    customer_name: str
    invoice_number: str
    amount: float
    due_date: date
    po_number: str | None = None

class Invoice(InvoiceCreate):
    id: int
    status: InvoiceStatus = InvoiceStatus.PENDING

class StatusUpdate(BaseModel):
    status: InvoiceStatus