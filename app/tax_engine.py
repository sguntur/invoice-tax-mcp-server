
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict
from uuid import uuid4

from app.audit_logger import build_audit_record, publish_audit_event
from app.config_loader import load_tax_rules
from app.models import InvoiceTaxRequest


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_tax_rate(config: Dict[str, Any], region: str, category: str) -> Decimal:
    region_rules = config.get("regions", {}).get(region)
    if not region_rules:
        raise ValueError(f"No tax configuration found for region: {region}")

    category_rates = region_rules.get("categories", {})
    rate = category_rates.get(category, region_rules.get("default_rate"))

    if rate is None:
        raise ValueError(f"No default tax rate configured for region: {region}")

    return Decimal(str(rate))


def calculate_invoice_tax(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = InvoiceTaxRequest.model_validate(payload)
    config = load_tax_rules()

    calculation_id = str(uuid4())

    subtotal = Decimal("0.00")
    total_tax = Decimal("0.00")
    calculated_lines = []

    for item in request.line_items:
        line_subtotal = money(item.unit_price * item.quantity)
        rate = get_tax_rate(config, request.region, item.category)
        line_tax = money(line_subtotal * rate)

        subtotal += line_subtotal
        total_tax += line_tax

        calculated_lines.append({
            "sku": item.sku,
            "description": item.description,
            "category": item.category,
            "quantity": item.quantity,
            "unit_price": str(money(item.unit_price)),
            "line_subtotal": str(line_subtotal),
            "tax_rate": str(rate),
            "line_tax": str(line_tax),
        })

    subtotal = money(subtotal)
    total_tax = money(total_tax)
    grand_total = money(subtotal + total_tax)

    threshold = Decimal(str(config["oversight"]["tax_threshold"]))
    requires_human_oversight = total_tax > threshold

    response = {
        "calculation_id": calculation_id,
        "invoice_id": request.invoice_id,
        "region": request.region,
        "currency": request.currency,
        "subtotal": str(subtotal),
        "tax_total": str(total_tax),
        "grand_total": str(grand_total),
        "requires_human_oversight": requires_human_oversight,
        "oversight_reason": (
            f"Tax total {total_tax} exceeds threshold {money(threshold)}"
            if requires_human_oversight
            else None
        ),
        "line_items": calculated_lines,
    }

    audit_record = build_audit_record(
        calculation_id=calculation_id,
        invoice_id=request.invoice_id,
        region=request.region,
        request=request.model_dump(mode="json"),
        response=response,
    )
    publish_audit_event(audit_record)

    return response
