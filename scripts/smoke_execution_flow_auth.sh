#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
TENANT_ID="${2:-${TENANT_ID:-}}"
ACCESS_TOKEN="${ACCESS_TOKEN:-}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_cmd curl
require_cmd python3

if [[ -z "$ACCESS_TOKEN" ]]; then
  echo "ACCESS_TOKEN is required (export ACCESS_TOKEN='<bearer token>')." >&2
  exit 1
fi

if [[ -z "$TENANT_ID" ]]; then
  echo "TENANT_ID is required (pass arg2 or export TENANT_ID)." >&2
  exit 1
fi

request_json() {
  local method="$1"
  local url="$2"
  local payload="$3"
  local out_file="$4"
  local code

  if [[ -n "$payload" ]]; then
    code=$(curl -sS -o "$out_file" -w '%{http_code}' -X "$method" "$url" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "x-tenant-id: $TENANT_ID" \
      -H 'Content-Type: application/json' \
      -d "$payload")
  else
    code=$(curl -sS -o "$out_file" -w '%{http_code}' -X "$method" "$url" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "x-tenant-id: $TENANT_ID")
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

request_json "GET" "$BASE_URL/auth/me" "" "/tmp/smoke_auth_me.json"

request_json "POST" "$BASE_URL/authoring/context-bridge/generate" "{\"tenant_id\":\"$TENANT_ID\",\"source_type\":\"readme\",\"source\":\"FastAPI RBAC moodle connector evidence replay\",\"title_hint\":\"Smoke Auth Track\",\"level\":\"intermediate\"}" "/tmp/smoke_auth_draft.json"

DRAFT_ID="$(json_field /tmp/smoke_auth_draft.json draft_id)"
request_json "POST" "$BASE_URL/authoring/drafts/$DRAFT_ID/submit-review" "" "/tmp/smoke_auth_draft_submit.json"
request_json "POST" "$BASE_URL/authoring/drafts/$DRAFT_ID/approve" "" "/tmp/smoke_auth_draft_approve.json"

request_json "POST" "$BASE_URL/evidence/sessions" "{\"tenant_id\":\"$TENANT_ID\",\"learner_id\":\"smoke-learner\",\"assignment_id\":\"smoke-assignment\",\"events\":[{\"ts\":1000,\"event_type\":\"paste\",\"payload\":{\"chars\":90}},{\"ts\":1700,\"event_type\":\"paste\",\"payload\":{\"chars\":95}},{\"ts\":2500,\"event_type\":\"paste\",\"payload\":{\"chars\":110}}]}" "/tmp/smoke_auth_evidence_ingest.json"
SESSION_ID="$(json_field /tmp/smoke_auth_evidence_ingest.json session_id)"
request_json "GET" "$BASE_URL/evidence/sessions/$SESSION_ID/replay" "" "/tmp/smoke_auth_evidence_replay.json"

request_json "POST" "$BASE_URL/simulator/personas/run" "{\"tenant_id\":\"$TENANT_ID\",\"assignment_id\":\"smoke-assignment\",\"learner_id\":\"smoke-learner\",\"persona\":\"cheater\"}" "/tmp/smoke_auth_ghost.json"
GHOST_SESSION_ID="$(json_field /tmp/smoke_auth_ghost.json session_id)"

request_json "POST" "$BASE_URL/delivery/handover/return-to-lms" "{\"tenant_id\":\"$TENANT_ID\",\"learner_id\":\"smoke-learner\",\"assignment_id\":\"smoke-assignment\",\"lms_return_url\":\"https://moodle.example/return\",\"competencies\":[{\"code\":\"algo.correctness\",\"score\":78.5,\"evidence_session_id\":\"$GHOST_SESSION_ID\"}]}" "/tmp/smoke_auth_handover.json"

echo "Strict-auth execution flow smoke test passed."
python3 - <<'PY'
import json

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

me = load("/tmp/smoke_auth_me.json")
draft = load("/tmp/smoke_auth_draft_approve.json")
replay = load("/tmp/smoke_auth_evidence_replay.json")
ghost = load("/tmp/smoke_auth_ghost.json")
handover = load("/tmp/smoke_auth_handover.json")

print({"subject": me.get("subject"), "roles": me.get("roles", []), "tenant_ids": me.get("tenant_ids", [])})
print({"draft_id": draft.get("draft_id"), "draft_status": draft.get("status")})
print({"replay_flags": replay.get("flags", [])})
print({"ghost_flags": ghost.get("flags", [])})
print({"handover_status": handover.get("status"), "average_score": handover.get("average_score")})
PY
