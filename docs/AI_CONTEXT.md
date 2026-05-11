# AI Context and Governance

## Prompts Provided

1. Build an MCP server that enables an AI agent to calculate invoice taxes.
2. Support a variable list of line items.
3. Make the solution configurable for future regional tax logic without code changes.
4. Provide an automated signal if tax exceeds $40 and requires human oversight.
5. Keep the implementation performant under load while maintaining auditability.
6. Deploy the demo to AWS Lambda behind API Gateway.
7. Use only private Amazon ECR for Lambda container image deployment.

## Governance Rules

- Tax calculation must be deterministic and not delegated to a language model.
- Regional tax rules must be configuration-driven.
- Monetary calculations must use Decimal.
- Every calculation must produce an audit event.
- Human oversight is required when total calculated tax exceeds $40.
- Public ECR must not be used for the production Lambda deployment path.
