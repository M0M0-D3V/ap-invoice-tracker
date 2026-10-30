from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class VendorStatus(str, Enum):
    ACTIVE = "active"
    HOLD = "hold"

class VendorCreate(BaseModel):
    name: str
    address: str
    email: str | None = None
    phone: str | None = None
class Vendor(VendorCreate):
    id: int
    status: VendorStatus = VendorStatus.ACTIVE

class InvoiceStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    APPROVED = "approved"
    REJECTED = "rejected"

class InvoiceCreate(BaseModel):
    vendor_id: int
    invoice_number: str | None = None
    amount: float = Field(gt=0)
    due_date: date | None = None
    po_number: str | None = None

class Invoice(InvoiceCreate):
    id: int
    status: InvoiceStatus = InvoiceStatus.PENDING

class StatusUpdate(BaseModel):
    status: InvoiceStatus

class MatchRow(BaseModel):
    invoice_id: int
    vendor_name: str
    inv_amt: Decimal
    po_amt: Decimal | None = None
    receipt_id: int | None = None