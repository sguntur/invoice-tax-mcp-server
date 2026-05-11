# Invoice Tax MCP Server — AWS Lambda + Private ECR

This project exposes a production-style invoice tax calculation endpoint suitable for wrapping an MCP tax tool in a demo deployment.

## Architecture

```text
Client / AI Agent
  ↓ HTTPS
API Gateway HTTP API
  ↓
AWS Lambda Container
  ↓
Private Amazon ECR
  ↓
CloudWatch structured audit logs
```

## Why Private ECR Only?

AWS Lambda container images are deployed from private Amazon ECR repositories. Public ECR is not required for this architecture and has been intentionally removed.

## Run Tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest
```

## Local Demo

```bash
python -m app.demo
```

## Build Lambda Container

```bash
docker build -f deploy/Dockerfile.lambda -t invoice-tax-mcp-server .
```

## Push to Private ECR

```bash
AWS_REGION=us-east-1 APP_NAME=invoice-tax-mcp-server ./deploy/deploy-private-ecr.sh
```

## API Request

```json
{
  "invoice_id": "INV-1001",
  "region": "TX",
  "currency": "USD",
  "line_items": [
    {
      "sku": "SOFT-1",
      "description": "Software license",
      "quantity": 3,
      "unit_price": "150.00",
      "category": "software"
    }
  ]
}
```

## Oversight Rule

The response includes:

```json
"requires_human_oversight": true
```

when total calculated tax exceeds `$40.00`.

## Design Choices

- **Strategy/config pattern:** tax rules live in `config/tax_rules.yaml`, allowing regional variation without code changes.
- **Stateless engine:** safe for Lambda scaling and concurrent requests.
- **Decimal arithmetic:** avoids floating point rounding issues for money.
- **Structured JSON logging:** CloudWatch-compatible observability and audit records.
- **Non-blocking audit publishing:** keeps request latency low while still producing detailed audit events.
- **Private ECR:** enterprise-standard Lambda container deployment.

## True MCP Streamable HTTP Endpoint

This project also includes a true MCP Streamable HTTP endpoint.

```text
/calculate-tax   REST endpoint for ChatGPT Actions
/mcp             MCP Streamable HTTP endpoint
```

Main files:

```text
app/mcp_server.py
app/mcp_lambda_handler.py
deploy/template-mcp.yaml
deploy/Dockerfile.mcp-lambda
```

Deploy:

```bash
IMAGE_TAG=mcp-v1 ./deploy/deploy-mcp-private-ecr.sh

sam deploy \
  --template-file deploy/template-mcp.yaml \
  --stack-name invoice-tax-mcp-server-mcp \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --resolve-image-repos \
  --parameter-overrides ImageUri=<PRIVATE_ECR_MCP_IMAGE_URI>
```
