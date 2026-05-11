
import json

from app.lambda_handler import handler


def test_lambda_handler_api_gateway_body_success():
    event = {
        "headers": {},
        "body": json.dumps({
            "invoice_id": "INV-LAMBDA-1",
            "region": "TX",
            "currency": "USD",
            "line_items": [
                {"sku": "A", "quantity": 1, "unit_price": "100.00", "category": "software"}
            ],
        }),
    }

    response = handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["tax_total"] == "8.25"


def test_lambda_handler_validation_error():
    response = handler({"headers": {}, "body": json.dumps({"invoice_id": "BAD"})}, None)

    assert response["statusCode"] == 422


def test_lambda_handler_invalid_json():
    response = handler({"headers": {}, "body": "{bad-json"}, None)

    assert response["statusCode"] == 400
