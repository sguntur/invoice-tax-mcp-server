
from app.tax_engine import calculate_invoice_tax


if __name__ == "__main__":
    payload = {
        "invoice_id": "INV-DEMO-001",
        "region": "TX",
        "currency": "USD",
        "line_items": [
            {"sku": "SOFT-1", "description": "Software", "quantity": 3, "unit_price": "150.00", "category": "software"},
            {"sku": "SERV-1", "description": "Service", "quantity": 2, "unit_price": "100.00", "category": "service"},
        ],
    }
    print(calculate_invoice_tax(payload))
