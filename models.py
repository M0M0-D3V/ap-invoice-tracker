from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class VendorStatus(str, Enum):
    ACTIVE = "active"
    HOLD = "hold"

class VendorCreate(BaseModel):
    vendor_name: str
    address: str | None = None
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
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    due_date: date | None = None
    po_number: str | None = None
    
    @field_validator("amount", mode="before")
    @classmethod
    def round_amount(cls, v) -> Decimal:
        return Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

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