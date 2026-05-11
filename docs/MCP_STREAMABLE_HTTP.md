# True MCP Streamable HTTP Endpoint

This project now supports two integration modes:

```text
/calculate-tax   REST JSON endpoint for ChatGPT Actions
/mcp             MCP Streamable HTTP endpoint for MCP-compatible clients
```

## Added Files

```text
app/mcp_server.py
app/mcp_lambda_handler.py
app/run_mcp_http.py
deploy/Dockerfile.mcp-lambda
deploy/Dockerfile.mcp-http
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

## Lambda Note

This implementation is intended for stateless MCP Streamable HTTP calls. For long-lived streaming/session-heavy MCP usage, ECS/Fargate is a better hosting target.
