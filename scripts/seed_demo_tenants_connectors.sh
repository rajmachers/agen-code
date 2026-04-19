#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
ACCESS_TOKEN="${ACCESS_TOKEN:-}"
TENANT_HEADER_NAME="${AUTH_HEADER_TENANT:-x-tenant-id}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_cmd curl

request_json() {
  local method="$1"
  local url="$2"
  local payload="$3"
  local out_file="$4"
  local ok_codes="$5"
  local tenant_header_value="${6:-}"
  local code

  local -a args
  args=(-sS -o "$out_file" -w '%{http_code}' -X "$method" "$url")

  if [[ -n "$ACCESS_TOKEN" ]]; then
    args+=(-H "Authorization: Bearer $ACCESS_TOKEN")
  fi

  if [[ -n "$tenant_header_value" ]]; then
    args+=(-H "$TENANT_HEADER_NAME: $tenant_header_value")
  fi

  if [[ -n "$payload" ]]; then
    args+=(-H 'Content-Type: application/json' -d "$payload")
  fi

  code=$(curl "${args[@]}")

  if [[ ",$ok_codes," != *",$code,"* ]]; then
    echo "Request failed: $method $url (HTTP $code)" >&2
    cat "$out_file" >&2 || true
    exit 1
  fi
}

wait_for_health() {
  local attempts=30
  local i=1
  while [[ $i -le $attempts ]]; do
    if curl -fsS "$BASE_URL/health" >/dev/null 2>&1; then
      return
    fi
    i=$((i + 1))
  done
  echo "Orchestrator health check failed at $BASE_URL/health" >&2
  exit 1
}

seed_tenant() {
  local tenant_id="$1"
  local tenant_name="$2"

  request_json \
    "POST" \
    "$BASE_URL/admin/tenants" \
    "{\"tenant_id\":\"$tenant_id\",\"name\":\"$tenant_name\",\"quotas\":{\"context_generations_daily\":300,\"evidence_sessions_daily\":2000,\"handover_daily\":2000}}" \
    "/tmp/seed_tenant_${tenant_id}.json" \
    "200,409"

  request_json \
    "POST" \
    "$BASE_URL/admin/tenants/$tenant_id/users/${tenant_id}-admin/roles" \
    '{"roles":["tenant_admin","teacher","reviewer","integration_manager"]}' \
    "/tmp/seed_roles_${tenant_id}_admin.json" \
    "200"

  request_json \
    "POST" \
    "$BASE_URL/admin/tenants/$tenant_id/users/${tenant_id}-teacher/roles" \
    '{"roles":["teacher","candidate"]}' \
    "/tmp/seed_roles_${tenant_id}_teacher.json" \
    "200"

  request_json \
    "POST" \
    "$BASE_URL/admin/tenants/$tenant_id/users/${tenant_id}-ops/roles" \
    '{"roles":["integration_manager","evaluator"]}' \
    "/tmp/seed_roles_${tenant_id}_ops.json" \
    "200"
}

seed_connector() {
  local tenant_id="$1"

  local connector_payload
  connector_payload=$(cat <<JSON
{
  "tenantId": "$tenant_id",
  "connectorType": "moodle",
  "contractVersion": "v1.0",
  "endpoints": {
    "launchResolve": "https://moodle.example.com/local/codingengine/launch",
    "outcomePush": "https://moodle.example.com/local/codingengine/outcomes",
    "health": "https://moodle.example.com/local/codingengine/health",
    "capabilities": "https://moodle.example.com/local/codingengine/capabilities"
  },
  "auth": {
    "method": "oauth2",
    "clientId": "${tenant_id}-platform-client",
    "secretRef": "vault://${tenant_id}/moodle/client-secret",
    "tokenUrl": "https://moodle.example.com/oauth2/token"
  },
  "mappings": {
    "roles": {
      "instructor": "editingteacher",
      "candidate": "student",
      "evaluator": "teacher"
    },
    "course": "courseid",
    "module": "cmid",
    "activity": "instanceid"
  },
  "capabilities": {
    "launch": true,
    "rosterSync": true,
    "competencySync": true,
    "resultRelease": true
  }
}
JSON
)

  request_json \
    "POST" \
    "$BASE_URL/simulator/connectors/configure" \
    "{\"connector\":$connector_payload}" \
    "/tmp/seed_connector_${tenant_id}.json" \
    "200"

  request_json \
    "GET" \
    "$BASE_URL/simulator/connectors/$tenant_id" \
    "" \
    "/tmp/seed_connector_get_${tenant_id}.json" \
    "200"
}

echo "Checking orchestrator health at $BASE_URL"
wait_for_health

echo "Seeding demo tenants and roles"
seed_tenant "tenant-acme" "Acme University"
seed_tenant "tenant-nova" "Nova Institute"
seed_tenant "tenant-orbit" "Orbit College"

echo "Seeding simulator connector profiles"
seed_connector "tenant-acme"
seed_connector "tenant-nova"
seed_connector "tenant-orbit"

request_json "GET" "$BASE_URL/simulator/connectors" "" "/tmp/seed_connectors_list.json" "200"

echo "Demo seed complete."
echo "Seed summary:"
echo "- Tenants: tenant-acme, tenant-nova, tenant-orbit"
echo "- Per-tenant users: <tenant>-admin, <tenant>-teacher, <tenant>-ops"
echo "- Connector type: moodle"
echo "- Frontend URLs:"
echo "  - Learner app: http://localhost:5173"
echo "  - Admin platform: http://localhost:5174"
echo "  - Academic ops: http://localhost:5175"
echo "  - API docs: http://localhost:8000/docs"
echo "  - Simulator docs: http://localhost:8020/docs"

echo "Artifacts written under /tmp/seed_*.json"
