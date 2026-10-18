from fastapi import FastAPI, HTTPException

from models import Invoice, InvoiceCreate, InvoiceStatus, StatusUpdate

app = FastAPI(title="AP Invoice Tracker")

invoices: list[Invoice] = []
next_id = 1

ALLOWED_TRANSITIONS = {
    "pending": ["approved", "rejected"],
    "approved": ["paid"],
    "rejected": [],
    "paid": [],
}

def find_invoice(invoice_id: int) -> Invoice:
    for invoice in invoices:
        if invoice.id == invoice_id:
            return invoice
    raise HTTPException(status_code=404, detail="Invoice not found")

@app.post("/invoices", response_model=Invoice, status_code=201)
def create_invoice(invoice: InvoiceCreate):
    for inv in invoices:
        if inv.invoice_number == invoice.invoice_number:
            raise HTTPException(status_code=409, detail="Invoice number already exists")
    global next_id
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

@app.get("/health")
def health():
    return {"status": "ok"}