#!/usr/bin/env bash

set -euo pipefail

BASE="${1:-http://localhost:8000}"
TENANT_ID="${2:-tenant-acme}"
OUT_DIR="${3:-/tmp/moodle_readiness}"

mkdir -p "$OUT_DIR"

echo "Checking orchestrator Moodle env (without printing secrets)..."
if docker compose -f infra/docker-compose.yml exec -T orchestrator /bin/sh -lc 'python - <<"PY"
import os
base = os.getenv("MOODLE_BASE_URL", "")
token = os.getenv("MOODLE_TOKEN", "")
print(f"BASE_SET={str(bool(base)).lower()}")
print("TOKEN_SET=" + str(bool(token and token != "replace-me")).lower())
PY' > "$OUT_DIR/env_status.txt"; then
  cat "$OUT_DIR/env_status.txt"
else
  echo "Could not inspect orchestrator env via docker compose." | tee "$OUT_DIR/env_status.txt"
fi

echo "Running Moodle catalogue probe..."
curl -sS -o "$OUT_DIR/catalogue.json" -w '%{http_code}' -X POST \
  "$BASE/connectors/moodle/catalogue/lookup" \
  -H 'Content-Type: application/json' \
  -H "x-tenant-id: $TENANT_ID" \
  -d '{"query":"","include_sections":false,"limit":5}' > "$OUT_DIR/catalogue.code"

CODE="$(tr -d '\n' < "$OUT_DIR/catalogue.code")"
echo "CATALOGUE_CODE=$CODE"

if [[ "$CODE" == "200" ]]; then
  echo "READY=true"
  exit 0
fi

echo "READY=false"
if [[ -f "$OUT_DIR/catalogue.json" ]]; then
  echo "CATALOGUE_RESPONSE=$(cat "$OUT_DIR/catalogue.json")"
fi

exit 1
