from fastapi import FastAPI, HTTPException

from db import get_connection
from models import (Invoice, InvoiceCreate, InvoiceStatus, StatusUpdate,
                    Vendor, VendorCreate, VendorStatus)

app = FastAPI(title="AP Invoice Tracker")

invoices: list[Invoice] = []
next_id = 1

ALLOWED_TRANSITIONS = {
    "pending": ["approved", "rejected"],
    "approved": ["paid"],
    "rejected": [],
    "paid": [],
}

vendors: list[Vendor] = []
next_vendor_id = 1

def find_vendor(vendor_id: int) -> Vendor:
    for vendor in vendors:
        if vendor.id == vendor_id:
            return vendor
    raise HTTPException(status_code=404, detail="Vendor not found")

@app.post("/vendors", response_model=Vendor, status_code=201)
def create_vendor(vendor: VendorCreate):
    global next_vendor_id
    db_vendor = Vendor(id=next_vendor_id, **vendor.model_dump())
    vendors.append(db_vendor)
    next_vendor_id += 1
    return db_vendor

@app.get("/vendors", response_model=list[Vendor])
def get_vendors():
    return vendors

@app.get("/vendors/{vendor_id}", response_model=Vendor)
def get_vendor(vendor_id: int):
    return find_vendor(vendor_id)

@app.patch("/vendors/{vendor_id}/status", response_model=Vendor)
def update_vendor_status(vendor_id: int, status: str):
    vendor = find_vendor(vendor_id)
    if status not in VendorStatus.__members__:
        raise HTTPException(status_code=400, detail="Invalid status")
    vendor.status = VendorStatus[status]
    return vendor

def find_invoice(invoice_id: int) -> Invoice:
    for invoice in invoices:
        if invoice.id == invoice_id:
            return invoice
    raise HTTPException(status_code=404, detail="Invoice not found")

@app.post("/invoices", response_model=Invoice, status_code=201)
def create_invoice(invoice: InvoiceCreate):
    global next_id
    vendor = find_vendor(invoice.vendor_id)
    if vendor.status != VendorStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Vendor is not active")
    for inv in invoices:
        if inv.invoice_number == invoice.invoice_number:
            raise HTTPException(status_code=409, detail="Invoice number already exists")
    db_invoice = Invoice(id=next_id, **invoice.model_dump())
    invoices.append(db_invoice)
    next_id += 1
    return db_invoice

@app.get("/invoices", response_model=list[Invoice])
def get_invoices():
    return invoices

@app.get("/invoices/{invoice_id}", response_model=Invoice)
def get_invoice(invoice_id: int):
    return find_invoice(invoice_id)

@app.patch("/invoices/{invoice_id}/status", response_model=Invoice)
def update_invoice_status(invoice_id: int, update: StatusUpdate):
    invoice = find_invoice(invoice_id)
    if update.status not in ALLOWED_TRANSITIONS[invoice.status]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {invoice.status} to {update.status}",
        )
    invoice.status = update.status
    return invoice

@app.delete("/invoices/{invoice_id}", response_model=Invoice)
def delete_invoice(invoice_id: int):
    invoice = find_invoice(invoice_id)
    invoices.remove(invoice)
    return invoice

MATCH_SQL = """
SELECT i.invoice_id, v.vendor_name, i.amount AS inv_amt,
        p.amount AS po_amt, r.receipt_id
FROM invoices i
JOIN purchase_orders p ON i.po_id = p.po_id
JOIN vendors v ON i.vendor_id = v.vendor_id
LEFT JOIN receipts r ON p.po_id = r.po_id
"""

@app.get("/match")
def get_matches():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(MATCH_SQL)
    rows = cur.fetchall()
    conn.close()
    return rows

@app.get("/match/mismatches")
def get_mismatches():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(MATCH_SQL + " WHERE i.amount <> p.amount OR r.receipt_id IS NULL")
    rows = cur.fetchall()
    conn.close()
    return rows

@app.get("/db/invoices")
def get_db_invoices(vendor_id: int | None = None):
    sql = """SELECT i.invoice_id, v.vendor_name, i.invoice_date, i.amount FROM invoices i JOIN vendors v ON i.vendor_id = v.vendor_id"""
    params = ()
    if vendor_id is not None:
        sql += " WHERE i.vendor_id = %s"
        params = (vendor_id,)
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

@app.get("/health")
def health():
    return {"status": "ok"}