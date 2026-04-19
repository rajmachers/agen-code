#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
TENANT_ID="${2:-tenant_smoke_$(date +%s)}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_cmd curl
require_cmd python3

request_json() {
  local method="$1"
  local url="$2"
  local payload="$3"
  local out_file="$4"
  local code

  if [[ -n "$payload" ]]; then
    code=$(curl -sS -o "$out_file" -w '%{http_code}' -X "$method" "$url" -H 'Content-Type: application/json' -d "$payload")
  else
    code=$(curl -sS -o "$out_file" -w '%{http_code}' -X "$method" "$url")
  fi

  if [[ "$code" != "200" ]]; then
    echo "Request failed: $method $url (HTTP $code)" >&2
    cat "$out_file" >&2 || true
    exit 1
  fi
}

json_field() {
  local file="$1"
  local field="$2"
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$file" "$field"
}

echo "Using BASE_URL=$BASE_URL"
echo "Using TENANT_ID=$TENANT_ID"

request_json "POST" "$BASE_URL/admin/tenants" "{\"tenant_id\":\"$TENANT_ID\",\"name\":\"Smoke Tenant\"}" "/tmp/smoke_tenant.json"
request_json "POST" "$BASE_URL/admin/tenants/$TENANT_ID/users/smoke-user/roles" '{"roles":["tenant_admin","teacher"]}' "/tmp/smoke_roles.json"
request_json "POST" "$BASE_URL/authoring/context-bridge/generate" "{\"tenant_id\":\"$TENANT_ID\",\"source_type\":\"readme\",\"source\":\"FastAPI RBAC moodle connector evidence replay\",\"title_hint\":\"Smoke Track\",\"level\":\"intermediate\"}" "/tmp/smoke_draft.json"

DRAFT_ID="$(json_field /tmp/smoke_draft.json draft_id)"
request_json "POST" "$BASE_URL/authoring/drafts/$DRAFT_ID/submit-review" "" "/tmp/smoke_draft_submit.json"
request_json "POST" "$BASE_URL/authoring/drafts/$DRAFT_ID/approve" "" "/tmp/smoke_draft_approve.json"

request_json "POST" "$BASE_URL/evidence/sessions" "{\"tenant_id\":\"$TENANT_ID\",\"learner_id\":\"smoke-learner\",\"assignment_id\":\"smoke-assignment\",\"events\":[{\"ts\":1000,\"event_type\":\"paste\",\"payload\":{\"chars\":90}},{\"ts\":1700,\"event_type\":\"paste\",\"payload\":{\"chars\":95}},{\"ts\":2500,\"event_type\":\"paste\",\"payload\":{\"chars\":110}}]}" "/tmp/smoke_evidence_ingest.json"
SESSION_ID="$(json_field /tmp/smoke_evidence_ingest.json session_id)"
request_json "GET" "$BASE_URL/evidence/sessions/$SESSION_ID/replay" "" "/tmp/smoke_evidence_replay.json"

request_json "POST" "$BASE_URL/simulator/personas/run" "{\"tenant_id\":\"$TENANT_ID\",\"assignment_id\":\"smoke-assignment\",\"learner_id\":\"smoke-learner\",\"persona\":\"cheater\"}" "/tmp/smoke_ghost.json"
GHOST_SESSION_ID="$(json_field /tmp/smoke_ghost.json session_id)"

request_json "POST" "$BASE_URL/delivery/handover/return-to-lms" "{\"tenant_id\":\"$TENANT_ID\",\"learner_id\":\"smoke-learner\",\"assignment_id\":\"smoke-assignment\",\"lms_return_url\":\"https://moodle.example/return\",\"competencies\":[{\"code\":\"algo.correctness\",\"score\":78.5,\"evidence_session_id\":\"$GHOST_SESSION_ID\"}]}" "/tmp/smoke_handover.json"

echo "Execution flow smoke test passed."
python3 - <<'PY'
import json

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

tenant = load("/tmp/smoke_tenant.json")
draft = load("/tmp/smoke_draft_approve.json")
replay = load("/tmp/smoke_evidence_replay.json")
ghost = load("/tmp/smoke_ghost.json")
handover = load("/tmp/smoke_handover.json")

print({"tenant_id": tenant.get("tenant_id"), "tenant_name": tenant.get("name")})
print({"draft_id": draft.get("draft_id"), "draft_status": draft.get("status")})
print({"replay_flags": replay.get("flags", [])})
print({"ghost_flags": ghost.get("flags", [])})
print({"handover_status": handover.get("status"), "average_score": handover.get("average_score")})
PY
