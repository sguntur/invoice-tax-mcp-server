#!/usr/bin/env bash
set -euo pipefail

APP_NAME="${APP_NAME:-invoice-tax-mcp-server}"
AWS_REGION="${AWS_REGION:-us-east-1}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
PLATFORM="${PLATFORM:-linux/amd64}"

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
REPO_URI="${ECR_REGISTRY}/${APP_NAME}"
IMAGE_URI="${REPO_URI}:${IMAGE_TAG}"

echo "App Name:     ${APP_NAME}"
echo "AWS Region:   ${AWS_REGION}"
echo "Platform:     ${PLATFORM}"
echo "Image URI:    ${IMAGE_URI}"

aws ecr describe-repositories --repository-names "${APP_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1   || aws ecr create-repository --repository-name "${APP_NAME}" --region "${AWS_REGION}" >/dev/null

aws ecr get-login-password --region "${AWS_REGION}"   | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

docker buildx inspect invoice-tax-builder >/dev/null 2>&1   || docker buildx create --name invoice-tax-builder --use

docker buildx use invoice-tax-builder

docker buildx build   --platform "${PLATFORM}"   --provenance=false   -f deploy/Dockerfile.lambda   -t "${IMAGE_URI}"   --push   .

echo ""
echo "MCP image pushed successfully:"
echo "${IMAGE_URI}"
echo ""
echo "Deploy with:"
echo "sam deploy --template-file deploy/template.yaml --stack-name invoice-tax-lambda-server --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM --resolve-image-repos --parameter-overrides ImageUri=${IMAGE_URI} TaxRulesS3Bucket=invoice-tax-config TaxRulesS3Key=tax_rules.yaml TaxRulesCacheTtlSeconds=60 ApiKey=juno_labs_ai"