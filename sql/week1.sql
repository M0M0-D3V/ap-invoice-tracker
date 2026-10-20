CREATE DATABASE ap_invoice_tracker;
USE ap_invoice_tracker;

CREATE TABLE vendors(
	vendor_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_name VARCHAR(100) NOT NULL
);

CREATE TABLE purchase_orders (
	po_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_id INT,
    po_date DATE,
    amount DECIMAL(10,2),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

CREATE TABLE receipts (
	receipt_id INT PRIMARY KEY AUTO_INCREMENT,
	po_id INT,
	received_date DATE,
	qty_received INT,
	FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id)
);

CREATE TABLE invoices (
	invoice_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_id INT,
    po_id INT,
    invoice_date DATE,
    amount DECIMAL(10,2),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id)
);

INSERT INTO vendors (vendor_name) VALUES ('Acme Supply'), ('Bolt Hardware'), ('Coastal Paper');

INSERT INTO purchase_orders (vendor_id, po_date, amount) VALUES
(1,'2026-10-01',500.00),(2,'2026-10-02',1200.00),(3,'2026-10-03',300.00),
(1,'2026-10-05',750.00),(2,'2026-10-06',450.00);

INSERT INTO receipts (po_id, received_date, qty_received) VALUES
(1,'2026-10-04',10),(2,'2026-10-05',20),(3,'2026-10-06',5),(4,'2026-10-08',15);

INSERT INTO invoices (vendor_id, po_id, invoice_date, amount) VALUES
(1,1,'2026-10-07',500.00),(2,2,'2026-10-08',1200.00),(3,3,'2026-10-09',350.00),
(1,4,'2026-10-10',750.00),(2,5,'2026-10-11',450.00);

SELECT i.invoice_id, v.vendor_name, i.amount AS inv_amt, p.amount AS po_amt
FROM invoices i
JOIN purchase_orders p ON i.po_id = p.po_id
JOIN vendors v ON i.vendor_id = v.vendor_id;

SELECT i.invoice_id, v.vendor_name, i.amount AS inv_amt, p.amount AS po_amt, r.receipt_id
FROM invoices i
JOIN purchase_orders p ON i.po_id = p.po_id
JOIN vendors v ON i.vendor_id = v.vendor_id
LEFT JOIN receipts r ON p.po_id = r.po_id
WHERE i.amount <> p.amount OR r.receipt_id IS NULL;