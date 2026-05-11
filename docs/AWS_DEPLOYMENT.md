# AWS Deployment — Private ECR Only

## Flow

```text
docker build
  ↓
private Amazon ECR
  ↓
AWS Lambda container image
  ↓
API Gateway HTTP API
```

## Removed

- Public ECR publish script
- Public image distribution docs
- Public pull instructions

## Why

Public ECR is useful for open-source distribution, but Lambda production deployment should use private ECR.

## Deploy Image

```bash
AWS_REGION=us-east-1 APP_NAME=invoice-tax-mcp-server ./deploy/deploy-private-ecr.sh
```

The script prints an image URI like:

```text
123456789012.dkr.ecr.us-east-1.amazonaws.com/invoice-tax-mcp-server:latest
```

Use that URI when deploying the SAM template.

## Deploy SAM Template

```bash
sam deploy \
  --template-file deploy/template.yaml \
  --stack-name invoice-tax-mcp-server \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides ImageUri=412794759828.dkr.ecr.us-east-1.amazonaws.com/invoice-tax-mcp-server:latest
```

curl -i -X POST "https://bo33rft1g8.execute-api.us-east-1.amazonaws.com/calculate-tax" \
  -H "content-type: application/json" \
  -d '{
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
  }'
