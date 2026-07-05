#!/usr/bin/env bash
# File shell này build và chạy researcher container ở local.
# Nó phù hợp khi muốn test môi trường gần giống production Lambda container hơn so với uvicorn thuần.
set -euo pipefail

# Các biến dưới đây gom đường dẫn và tên tài nguyên local để script dễ bảo trì.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
ENV_FILE="$REPO_ROOT/.env"
IMAGE_NAME="alex-researcher-local"
CONTAINER_NAME="alex-researcher-local"
PORT="8000"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: missing env file at $ENV_FILE" >&2
  exit 1
fi

# Khối này export toàn bộ biến từ .env để Docker build/run dùng lại cùng cấu hình.
set -a
source "$ENV_FILE"
set +a

# Nếu container cũ còn tồn tại thì xóa trước để tránh trùng tên lúc chạy lại.
if docker ps -a --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"; then
  docker rm -f "$CONTAINER_NAME" >/dev/null
fi

# Build image local với build-essential bật lên để tiện cài dependency nếu cần.
docker build \
  --build-arg INSTALL_BUILD_ESSENTIAL=true \
  -t "$IMAGE_NAME" \
  "$SCRIPT_DIR"

# Chạy container và map cổng 8000 để truy cập service từ máy local.
docker run \
  --rm \
  --name "$CONTAINER_NAME" \
  --env-file "$ENV_FILE" \
  -p "$PORT:8000" \
  "$IMAGE_NAME"
