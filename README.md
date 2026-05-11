# Invoice Tax MCP Server

Production-style Python service that exposes deterministic invoice-tax calculation through:

```text
/mcp             MCP Streamable HTTP endpoint for AI agents
/calculate-tax   REST JSON endpoint for simple integrations and smoke tests
```

The implementation is intentionally split so the tax engine, validation models, audit logging, and transport adapters can evolve independently.

## Requirement Coverage

| Assessment requirement | Implementation |
| --- | --- |
| AI agent can calculate invoice taxes via MCP | `app/mcp_server.py` exposes `calculate_invoice_tax_tool` through MCP Streamable HTTP. |
| Variable list of line items | `InvoiceTaxRequest.line_items` validates a non-empty list of `LineItem` objects. |
| Configurable regional logic without code changes | Rates and oversight threshold are read from `config/tax_rules.yaml`; `TAX_RULES_PATH` can point to another config file. |
| Human oversight signal when tax exceeds $40 | Response sets `requires_human_oversight` when `tax_total > oversight.tax_threshold`. |
| Performance under load with detailed audit trail | Tax calculation is stateless and CPU-light; config is cached per warm process; audit events are published asynchronously as structured JSON logs. |
| Contract safety replacing type-safe Java service | Pydantic models enforce request shape, non-empty IDs, positive quantities, positive prices, and non-empty line item lists. |
| Operational readiness | JSON logs, request/calculation IDs, Dockerfiles, SAM templates, and CI tests are included. |

## Architecture

```text
AI Agent / Client
  ↓ HTTPS
API Gateway HTTP API
  ↓
Lambda container or local Uvicorn process
  ↓
MCP transport / REST transport
  ↓
Pydantic contract validation
  ↓
Config-driven tax engine
  ↓
Structured audit log sink
```

Key boundaries:

- `app/tax_engine.py` contains business logic only.
- `app/models.py` contains request contracts and validation.
- `app/mcp_server.py` and `app/lambda_handler.py` are transport adapters.
- `app/audit_logger.py` owns audit record construction and publishing.
- `config/tax_rules.yaml` owns regional rates and oversight threshold.

## Local Setup

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

## Local REST Demo

```bash
python -m app.demo
```

## Local MCP Server

```bash
pip install -r requirements.txt
python -m app.run_mcp_http
```

The MCP endpoint is available at:

```text
http://localhost:8000/mcp
```

## REST Request Example

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

## Response Shape

```json
{
  "calculation_id": "uuid",
  "invoice_id": "INV-1001",
  "region": "TX",
  "currency": "USD",
  "subtotal": "450.00",
  "tax_total": "37.13",
  "grand_total": "487.13",
  "requires_human_oversight": false,
  "oversight_reason": null,
  "line_items": [
    {
      "sku": "SOFT-1",
      "description": "Software license",
      "category": "software",
      "quantity": 3,
      "unit_price": "150.00",
      "line_subtotal": "450.00",
      "tax_rate": "0.0825",
      "line_tax": "37.13"
    }
  ]
}
```

## Oversight Rule

`requires_human_oversight` is `true` when the total calculated tax is greater than the configured threshold. The assessment threshold is `$40.00`, configured in `config/tax_rules.yaml`:

```yaml
oversight:
  tax_threshold: 40.00
```

## Observability and Audit Design

Every successful calculation emits an `INVOICE_TAX_CALCULATED` audit record with the calculation ID, invoice ID, region, validated request, and response. The audit event is written as structured JSON for CloudWatch ingestion.

The audit/performance trade-off is handled by publishing audit events through a small `ThreadPoolExecutor`. The request path does not block on slow audit sinks, but each response still contains a `calculation_id` that can be used to correlate client output with audit logs. For stricter durability requirements, `app/audit_logger.py` is the only module that needs to change, for example to add DynamoDB, Kinesis, or SQS publishing.

## Deployment

### REST Lambda Container

```bash
docker build -f deploy/Dockerfile.lambda -t invoice-tax-mcp-server .
AWS_REGION=us-east-1 APP_NAME=invoice-tax-mcp-server ./deploy/deploy-private-ecr.sh
```

```bash
sam deploy \
  --template-file deploy/template.yaml \
  --stack-name invoice-tax-mcp-server \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides ImageUri=<PRIVATE_ECR_IMAGE_URI>
```

### MCP Streamable HTTP Lambda Container

```bash
IMAGE_TAG=mcp-v1 ./deploy/deploy-mcp-private-ecr.sh
```

```bash
sam deploy \
  --template-file deploy/template-mcp.yaml \
  --stack-name invoice-tax-mcp-server-mcp \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --resolve-image-repos \
  --parameter-overrides ImageUri=<PRIVATE_ECR_MCP_IMAGE_URI>
```

Set `MCP_ALLOWED_HOSTS` and `MCP_ALLOWED_ORIGINS` in the deployed environment to include the public API Gateway host used by reviewers.

## Repository Hygiene

Generated files are intentionally excluded from source control: virtual environments, IDE metadata, pytest caches, Python bytecode, and SAM build output. See `.gitignore`.
