
from __future__ import annotations

import base64
import json
import os
from typing import Any, Dict

from pydantic import ValidationError

from app.logging_config import logger
from app.tax_engine import calculate_invoice_tax


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "cache-control": "no-store",
        },
        "body": json.dumps(body, default=str),
    }


def _parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = event.get("body")
    if body is None:
        return event

    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")

    if isinstance(body, str):
        return json.loads(body)

    if isinstance(body, dict):
        return body

    raise ValueError("Unsupported request body format.")


def _authorized(event: Dict[str, Any]) -> bool:
    expected_api_key = os.getenv("API_KEY")
    if not expected_api_key:
        return True

    headers = event.get("headers") or {}
    normalized = {str(k).lower(): v for k, v in headers.items()}
    return normalized.get("x-api-key") == expected_api_key


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    request_id = getattr(context, "aws_request_id", None)

    try:
        if not _authorized(event):
            return _response(401, {"error": "Unauthorized"})

        payload = _parse_body(event)
        result = calculate_invoice_tax(payload)

        logger.info(
            "tax_calculation_completed",
            extra={
                "aws_request_id": request_id,
                "invoice_id": result.get("invoice_id"),
                "calculation_id": result.get("calculation_id"),
                "requires_human_oversight": result.get("requires_human_oversight"),
            },
        )

        return _response(200, result)

    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON request body."})
    except ValidationError as exc:
        return _response(422, {"error": "Validation failed", "details": exc.errors()})
    except ValueError as exc:
        return _response(400, {"error": str(exc)})
    except Exception:
        logger.exception("unhandled_lambda_error", extra={"aws_request_id": request_id})
        return _response(500, {"error": "Internal server error"})


if __name__ == "__main__":
    sample_event = {
        "body": json.dumps({
            "invoice_id": "INV-LOCAL-1",
            "region": "TX",
            "currency": "USD",
            "line_items": [
                {"sku": "SKU-1", "quantity": 2, "unit_price": "100.00", "category": "software"}
            ],
        })
    }
    print(handler(sample_event, None))
