#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-ballbase/youtube-parser}"
IMAGE_TAG="${IMAGE_TAG:-dev}"

# 统一镜像构建入口，便于后续接入 CI/CD。
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
