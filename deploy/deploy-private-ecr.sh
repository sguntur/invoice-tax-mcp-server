#!/usr/bin/env bash
set -euo pipefail

APP_NAME="${APP_NAME:-invoice-tax-mcp-server}"
AWS_REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REPO_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}"

aws ecr describe-repositories --repository-names "${APP_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1   || aws ecr create-repository --repository-name "${APP_NAME}" --region "${AWS_REGION}" >/dev/null

aws ecr get-login-password --region "${AWS_REGION}"   | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

docker build -f deploy/Dockerfile.lambda -t "${APP_NAME}:latest" .
docker tag "${APP_NAME}:latest" "${REPO_URI}:latest"
docker push "${REPO_URI}:latest"

echo "Image pushed: ${REPO_URI}:latest"
