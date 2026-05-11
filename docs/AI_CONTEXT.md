# AI Context and Governance

## Prompts and Instructions Provided

1. Build an MCP server that enables an AI agent to calculate invoice taxes.
2. Support a variable list of line items.
3. Make regional tax logic configurable without code changes.
4. Provide an automated signal if calculated tax exceeds $40 and requires human oversight.
5. Keep the implementation performant under load while maintaining a detailed audit trail.
6. Preserve strict request validation because this replaces type-safe Java business logic.
7. Keep business logic decoupled from transport so MCP can be replaced with minimal friction.
8. Make the service observable and ready for containerized deployment.
9. Deploy through AWS Lambda/API Gateway using private Amazon ECR images.
10. Remove generated artifacts and stale documentation before submission.

## Governance Rules

- Tax calculation must be deterministic and must not be delegated to a language model.
- Regional tax rules and oversight threshold must be configuration-driven.
- Monetary calculations must use `Decimal` and explicit two-decimal rounding.
- Every successful calculation must produce an audit event.
- Human oversight is required when total calculated tax exceeds `$40.00`.
- Transport adapters must call the shared tax engine rather than duplicating business logic.
- Request validation must reject missing invoice IDs, empty item lists, non-positive quantities, and non-positive prices.
- Source packages must not include virtual environments, IDE state, build output, or Python cache files.
