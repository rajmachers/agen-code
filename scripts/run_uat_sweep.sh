#!/usr/bin/env bash

set -euo pipefail

BASE="${1:-http://localhost:8000}"
OUT_DIR="${2:-/tmp/uat_sweep}"

mkdir -p "$OUT_DIR"

req() {
  local name="$1"
  local method="$2"
  local url="$3"
  local payload="${4:-}"
  local tenant_header="${5:-}"

  local out_file="$OUT_DIR/${name}.json"
  local code_file="$OUT_DIR/${name}.code"

  if [[ -n "$payload" ]]; then
    if [[ -n "$tenant_header" ]]; then
      curl -sS -o "$out_file" -w '%{http_code}' -X "$method" "$url" -H 'Content-Type: application/json' -H "x-tenant-id: $tenant_header" -d "$payload" > "$code_file"
    else
      curl -sS -o "$out_file" -w '%{http_code}' -X "$method" "$url" -H 'Content-Type: application/json' -d "$payload" > "$code_file"
    fi
  else
    if [[ -n "$tenant_header" ]]; then
      curl -sS -o "$out_file" -w '%{http_code}' -X "$method" "$url" -H "x-tenant-id: $tenant_header" > "$code_file"
    else
      curl -sS -o "$out_file" -w '%{http_code}' -X "$method" "$url" > "$code_file"
    fi
  fi
}

http_code() {
  cat "$OUT_DIR/$1.code"
}

# Reachability
curl -sS -o "$OUT_DIR/webide.html" -w '%{http_code}' http://localhost:5173 > "$OUT_DIR/webide.code"
curl -sS -o "$OUT_DIR/admin.html" -w '%{http_code}' http://localhost:5174 > "$OUT_DIR/admin.code"
curl -sS -o "$OUT_DIR/ops.html" -w '%{http_code}' http://localhost:5175 > "$OUT_DIR/ops.code"
curl -sS -o "$OUT_DIR/api_docs.html" -w '%{http_code}' http://localhost:8000/docs > "$OUT_DIR/api_docs.code"
curl -sS -o "$OUT_DIR/sim_docs.html" -w '%{http_code}' http://localhost:8020/docs > "$OUT_DIR/sim_docs.code"

req health GET "$BASE/health"

TENANT="tenant_uat_$(date +%s)"
SCENARIO="scenario_uat_$(date +%s)"
printf 'TENANT=%s\nSCENARIO=%s\n' "$TENANT" "$SCENARIO" > "$OUT_DIR/ids.txt"

# Admin
req tenant_create POST "$BASE/admin/tenants" "{\"tenant_id\":\"$TENANT\",\"name\":\"UAT Tenant\"}"
req roles POST "$BASE/admin/tenants/$TENANT/users/$TENANT-admin/roles" '{"roles":["tenant_admin","teacher","reviewer","integration_manager"]}'
req users GET "$BASE/admin/tenants/$TENANT/users"
req metering GET "$BASE/admin/tenants/$TENANT/metering"

# Academic ops
req draft POST "$BASE/authoring/context-bridge/generate" "{\"tenant_id\":\"$TENANT\",\"source_type\":\"readme\",\"source\":\"FastAPI RBAC Moodle integration evidence player\",\"title_hint\":\"UAT Track\",\"level\":\"intermediate\"}"
DRAFT_ID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["draft_id"])' "$OUT_DIR/draft.json")
req submit POST "$BASE/authoring/drafts/$DRAFT_ID/submit-review"
req approve POST "$BASE/authoring/drafts/$DRAFT_ID/approve"

req evidence_ingest POST "$BASE/evidence/sessions" "{\"tenant_id\":\"$TENANT\",\"learner_id\":\"learner-uat\",\"assignment_id\":\"assignment-uat\",\"events\":[{\"ts\":1000,\"event_type\":\"paste\",\"payload\":{\"chars\":88}},{\"ts\":1600,\"event_type\":\"paste\",\"payload\":{\"chars\":94}},{\"ts\":2300,\"event_type\":\"paste\",\"payload\":{\"chars\":101}}]}"
SESSION_ID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["session_id"])' "$OUT_DIR/evidence_ingest.json")
req replay GET "$BASE/evidence/sessions/$SESSION_ID/replay"

req ghost POST "$BASE/simulator/personas/run" "{\"tenant_id\":\"$TENANT\",\"assignment_id\":\"assignment-uat\",\"learner_id\":\"learner-uat\",\"persona\":\"cheater\"}"
GHOST_SESSION_ID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["session_id"])' "$OUT_DIR/ghost.json")

# Learner APIs
req learning POST "$BASE/learning/generate" '{"topic":"fastapi","level":"beginner","goals":["routing","validation"]}'
req assessment POST "$BASE/assessment/evaluate?mode=deterministic" '{"assignment_id":"a_uat","learner_id":"learner-uat","language":"python","repo_url":"https://example.com/repo.git","commit_hash":"uat123","tests_path":"tests"}'
req handover POST "$BASE/delivery/handover/return-to-lms" "{\"tenant_id\":\"$TENANT\",\"learner_id\":\"learner-uat\",\"assignment_id\":\"assignment-uat\",\"lms_return_url\":\"https://moodle.example/return\",\"competencies\":[{\"code\":\"coding.correctness\",\"score\":78.5,\"evidence_session_id\":\"$GHOST_SESSION_ID\"}]}"

# Simulator lifecycle
req templates GET "$BASE/simulator/scenarios/templates"
req scenario_create POST "$BASE/simulator/scenarios/templates/quick_demo" "{\"tenant_id\":\"$TENANT\",\"scenario_id\":\"$SCENARIO\",\"connector_type\":\"moodle\"}"
req scenario_run POST "$BASE/simulator/scenarios/$SCENARIO/run"
req scenario_status GET "$BASE/simulator/scenarios/$SCENARIO/status"
req scenario_report GET "$BASE/simulator/scenarios/$SCENARIO/report"
req scenario_pause POST "$BASE/simulator/scenarios/$SCENARIO/pause"
req scenario_resume POST "$BASE/simulator/scenarios/$SCENARIO/resume"
req scenario_replay POST "$BASE/simulator/scenarios/$SCENARIO/replay"
req scenario_purge DELETE "$BASE/simulator/scenarios/$SCENARIO/purge"

# Connector lifecycle
req connectors_list GET "$BASE/simulator/connectors"
req connector_get GET "$BASE/simulator/connectors/$TENANT"

# Moodle connector routes (may fail if MOODLE_TOKEN/config not set)
req moodle_catalogue POST "$BASE/connectors/moodle/catalogue/lookup" '{"query":"","include_sections":false,"limit":5}' "$TENANT"
req moodle_publish POST "$BASE/connectors/moodle/publish" '{"course_id":1,"activities":[],"dry_run":true}' "$TENANT"

echo "UAT sweep complete in $OUT_DIR"
