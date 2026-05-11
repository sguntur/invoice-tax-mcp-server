# AWS Deployment — Private ECR

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

AWS Lambda container images are pulled from Amazon ECR. This project uses private ECR repositories for both the REST and MCP Lambda images.

## REST Endpoint Deployment

Build and push the image:

```bash
AWS_REGION=us-east-1 APP_NAME=invoice-tax-mcp-server ./deploy/deploy-private-ecr.sh
```

The script prints an image URI like:

```text
123456789012.dkr.ecr.us-east-1.amazonaws.com/invoice-tax-mcp-server:latest
```

Deploy the SAM template:

```bash
sam deploy \
  --template-file deploy/template.yaml \
  --stack-name invoice-tax-mcp-server \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides ImageUri=<PRIVATE_ECR_IMAGE_URI>
```

## MCP Endpoint Deployment

Build and push the MCP image:

```bash
AWS_REGION=us-east-1 APP_NAME=invoice-tax-mcp-server-mcp IMAGE_TAG=mcp-v1 ./deploy/deploy-mcp-private-ecr.sh
```

Deploy the MCP SAM template:

```bash
sam deploy \
  --template-file deploy/template-mcp.yaml \
  --stack-name invoice-tax-mcp-server-mcp \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --resolve-image-repos \
  --parameter-overrides ImageUri=<PRIVATE_ECR_MCP_IMAGE_URI>
```

After deployment, set `MCP_ALLOWED_HOSTS` and `MCP_ALLOWED_ORIGINS` for the generated API Gateway host.

## Removed from Source Package

- Local virtual environment directories
- IDE metadata
- Python bytecode and pytest cache
- SAM build output
- Public image distribution instructions
