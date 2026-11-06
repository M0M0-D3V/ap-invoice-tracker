import pytest
from fastapi.testclient import TestClient

from main import app, invoices, vendors

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
  vendors.clear()
  invoices.clear()

def test_get_invoice():
  response = client.get("/invoices/999")
  assert response.status_code == 404

def test_hold_vendor_status():
  # Create a vendor
  vendor_data = {
    "vendor_name": "Test Vendor",
    "address": "123 Test St",
    "email": "test@vendor.com",
    "phone": "123-456-7890"
  }
  response = client.post("/vendors", json=vendor_data)
  vendor_id = response.json()["id"]
  # Patch the vendor
  hold_response = client.patch(f"/vendors/{vendor_id}/status", params={"status": "hold"})
  assert hold_response.json()["status"] == "hold"
  assert hold_response.status_code == 200

def test_hold_vendor_invoice_rejected():
  # Create a vendor
  vendor_data = {
    "vendor_name": "Test Vendor",
    "address": "123 Test St",
    "email": "test@vendor.com",
    "phone": "123-456-7890"
  }
  response = client.post("/vendors", json=vendor_data)
  vendor_id = response.json()["id"]
  # Patch the vendor
  hold_response = client.patch(f"/vendors/{vendor_id}/status", params={"status": "hold"})
  assert hold_response.status_code == 200
  assert hold_response.json()["status"] == "hold"
  # Create an invoice for the vendor
  invoice_data = {
    "vendor_id": vendor_id,
    "invoice_number": "INV-001",
    "amount": 100.0,
    "due_date": "2024-12-31",
    "po_number": "PO-001"
  }
  invoice_response = client.post("/invoices", json=invoice_data)
  assert invoice_response.status_code == 400