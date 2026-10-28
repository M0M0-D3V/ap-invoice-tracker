from fastapi import FastAPI, HTTPException
from mysql.connector import IntegrityError

from db import get_connection, get_cursor
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
def update_vendor_status(vendor_id: int, status: VendorStatus):
    vendor = find_vendor(vendor_id)
    vendor.status = status
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
    with get_cursor() as cur:
        cur.execute(MATCH_SQL)
        return cur.fetchall()

@app.get("/match/mismatches")
def get_mismatches():
    with get_cursor() as cur:
        cur.execute(MATCH_SQL + " WHERE i.amount <> p.amount OR r.receipt_id IS NULL")
        return cur.fetchall()

@app.get("/db/invoices")
def get_db_invoices(vendor_id: int | None = None, min_amount: float | None = None):
    sql = """SELECT i.invoice_id, v.vendor_name, i.invoice_date, i.amount FROM invoices i JOIN vendors v ON i.vendor_id = v.vendor_id"""
    where, params = [], []
    if vendor_id is not None:
        where.append("i.vendor_id = %s")
        params.append(vendor_id)
    if min_amount is not None:
        where.append("i.amount >= %s")
        params.append(min_amount)
    if where:
        sql += " WHERE " + " AND ".join(where)
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

@app.post("/db/invoices", status_code=201)
def create_db_invoice(invoice: InvoiceCreate):
    sql = """INSERT INTO invoices (vendor_id, invoice_number, invoice_date, due_date, amount) VALUES (%s, %s, CURDATE(), %s,%s)"""
    params = (invoice.vendor_id, invoice.invoice_number,invoice.due_date, invoice.amount)
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        conn.commit()
    except IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=409, detail="Invoice number already exists")
    new_id = cur.lastrowid
    conn.close()
    return {"invoice_id": new_id, "status": "pending", **invoice.model_dump()}

@app.get("/db/invoices/{invoice_id}")
def get_db_invoice(invoice_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM invoices WHERE invoice_id = %s", (invoice_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return row

@app.get("/health")
def health():
    return {"status": "ok"}