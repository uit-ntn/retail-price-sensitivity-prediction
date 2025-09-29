#!/usr/bin/env bash
set -euo pipefail

REGION="${AWS_REGION:-ap-southeast-1}"
REPO_URI="${1:-REPLACE_ME_ECR_REPOSITORY_URL}" # eg 123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/retail-forecast-dev-server
IMAGE_TAG="${2:-$(git rev-parse --short HEAD)}"
CONTEXT_DIR="${3:-../../server}"

aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$(echo "$REPO_URI" | awk -F/ '{print $1}')"
docker build -t "$REPO_URI:$IMAGE_TAG" -f "$CONTEXT_DIR/DockerFile" "$CONTEXT_DIR"
docker push "$REPO_URI:$IMAGE_TAG"
echo "Pushed: $REPO_URI:$IMAGE_TAG"
