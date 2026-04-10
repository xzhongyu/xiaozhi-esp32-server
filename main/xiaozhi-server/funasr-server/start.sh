#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

mkdir -p funasr-runtime-resources/models

if [[ ! -f funasr-runtime-resources/hotwords.txt ]]; then
  cat > funasr-runtime-resources/hotwords.txt <<'EOF'
EOF
fi

docker compose -f docker-compose.yml up -d
docker compose -f docker-compose.yml ps
