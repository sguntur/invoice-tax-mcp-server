
import os

from app.tax_engine import calculate_invoice_tax


def test_calculates_tax_for_variable_line_items():
    result = calculate_invoice_tax({
        "invoice_id": "INV-1",
        "region": "TX",
        "currency": "USD",
        "line_items": [
            {"sku": "A", "quantity": 2, "unit_price": "100.00", "category": "software"},
            {"sku": "B", "quantity": 1, "unit_price": "50.00", "category": "grocery"},
        ],
    })

    assert result["subtotal"] == "250.00"
    assert result["tax_total"] == "16.50"
    assert result["grand_total"] == "266.50"
    assert result["requires_human_oversight"] is False


def test_oversight_signal_when_tax_exceeds_threshold():
    result = calculate_invoice_tax({
        "invoice_id": "INV-2",
        "region": "TX",
        "currency": "USD",
        "line_items": [
            {"sku": "A", "quantity": 10, "unit_price": "100.00", "category": "software"}
        ],
    })

    assert result["tax_total"] == "82.50"
    assert result["requires_human_oversight"] is True
    assert "exceeds threshold" in result["oversight_reason"]


def test_unknown_region_raises_value_error():
    try:
        calculate_invoice_tax({
            "invoice_id": "INV-3",
            "region": "UNKNOWN",
            "line_items": [{"sku": "A", "quantity": 1, "unit_price": "10.00"}],
        })
    except ValueError as exc:
        assert "No tax configuration" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
