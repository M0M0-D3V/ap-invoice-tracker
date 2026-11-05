import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_get_invoice():
  response = client.get("/invoices/999")
  assert response.status_code == 404