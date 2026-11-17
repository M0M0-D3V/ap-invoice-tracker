import xml.etree.ElementTree as ET

NS = {"soap":"http://schemas.xmlsoap.org/soap/envelope/"}

VALID_RESPONSE = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetInvoiceResponse>
      <InvoiceId>1001</InvoiceId>
      <Amount>250.00</Amount>
    </GetInvoiceResponse>
  </soap:Body>
</soap:Envelope>"""

def test_parse_invoice_id():
    root = ET.fromstring(VALID_RESPONSE)
    body = root.find("soap:Body", NS)
    invoice_id = body.find("GetInvoiceResponse/InvoiceId")
    assert invoice_id.text == "1001"

FAULT_RESPONSE = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <soap:Fault>
      <faultcode>soap:Client</faultcode>
      <faultstring>Invoice not found</faultstring>
    </soap:Fault>
  </soap:Body>
</soap:Envelope>"""

def test_fault_detected():
    root = ET.fromstring(FAULT_RESPONSE)
    body = root.find("soap:Body", NS)
    fault = body.find("soap:Fault", NS)
    assert fault is not None
    assert fault.find("faultstring").text == "Invoice not found"