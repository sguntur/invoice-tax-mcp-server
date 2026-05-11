# MCP Streamable HTTP Endpoint

This project supports two integration modes:

```text
/mcp             MCP Streamable HTTP endpoint for MCP-compatible clients
/calculate-tax   REST JSON endpoint for simple integrations and smoke tests
```

## Files

```text
app/mcp_server.py
app/run_mcp_http.py
deploy/Dockerfile.mcp-lambda
deploy/deploy-mcp-private-ecr.sh
deploy/template-mcp.yaml
```

## Local MCP HTTP Run

```bash
pip install -r requirements.txt
python -m app.run_mcp_http
```

The local MCP server starts on:

```text
http://localhost:8000/mcp
```

## Tool Contract

Tool name:

```text
calculate_invoice_tax_tool
```

Input envelope:

```json
{
  "invoice": {
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
}
```

Output includes invoice totals, line-level tax, `calculation_id`, and `requires_human_oversight`.

## Deploy MCP Lambda Image

Use a unique tag for every deployment:

```bash
IMAGE_TAG=mcp-v1 ./deploy/deploy-mcp-private-ecr.sh
```

Deploy:

```bash
sam deploy \
  --template-file deploy/template-mcp.yaml \
  --stack-name invoice-tax-mcp-server-mcp \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --resolve-image-repos \
  --parameter-overrides ImageUri=<PRIVATE_ECR_MCP_IMAGE_URI>
```

Output:

```text
McpServerUrl = https://<api-id>.execute-api.<region>.amazonaws.com/mcp
```

## Transport Security

The MCP server enables DNS rebinding protection. Configure these environment variables in the deployed environment:

```text
MCP_ALLOWED_HOSTS=<api-id>.execute-api.<region>.amazonaws.com
MCP_ALLOWED_ORIGINS=https://<api-id>.execute-api.<region>.amazonaws.com
```

Localhost values are included by default for local development.

## Lambda Note

This implementation is intended for stateless MCP Streamable HTTP calls. For long-lived streaming or session-heavy MCP usage, ECS/Fargate is a better hosting target.
