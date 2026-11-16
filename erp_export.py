import json

from db import get_connection

conn = get_connection()
cursor = conn.cursor(dictionary=True)

cursor.execute("""
    SELECT i.invoice_id, i.invoice_number, v.vendor_name,
           i.invoice_date, i.due_date, i.amount, i.status
    FROM invoices i
    JOIN vendors v ON i.vendor_id = v.vendor_id
""")

erp_records = []
rejected = []

for row in cursor.fetchall():
    errors = []
    if not row["invoice_number"]:
        errors.append("missing invoice_number")
    if not row["invoice_date"]:
        errors.append("missing invoice_date")
    if row["due_date"] and row["invoice_date"] and row["due_date"] < row["invoice_date"]:
        errors.append("due_date before invoice_date")

    if errors:
        rejected.append({"invoice_id": row["invoice_id"], "errors": errors})
        continue

    erp_records.append({
        "externalId": f"AP-{row['invoice_id']}",
        "tranId": row["invoice_number"],
        "entity": row["vendor_name"],
        "tranDate": row["invoice_date"].isoformat(),
        "dueDate": row["due_date"].isoformat() if row["due_date"] else None,
        "total": float(row["amount"]),
        "approvalStatus": row["status"].upper(),
    })

with open("erp_export.json", "w") as f:
    json.dump(erp_records, f, indent=2)

print(f"Exported: {len(erp_records)}, Rejected: {len(rejected)}")
for r in rejected:
    print(r)

with open("erp_rejected.json", "w") as f:
    json.dump(rejected, f, indent=2)

cursor.close()
conn.close()