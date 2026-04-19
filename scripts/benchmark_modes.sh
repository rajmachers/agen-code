#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
RUNS="${2:-5}"

if ! [[ "$RUNS" =~ ^[0-9]+$ ]] || [[ "$RUNS" -lt 1 ]]; then
  echo "RUNS must be a positive integer" >&2
  exit 1
fi

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_cmd curl
require_cmd awk
require_cmd sort
require_cmd wc

wait_for_health() {
  local health_url="$1/health"
  local retries=60
  local i
  for ((i = 1; i <= retries; i++)); do
    if curl -fsS "$health_url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  echo "Health check failed for $health_url" >&2
  exit 1
}

run_series() {
  local label="$1"
  local url="$2"
  local payload="$3"
  local output_prefix="$4"
  local times_file="$5"

  : > "$times_file"
  echo "$label x$RUNS"

  local i
  for ((i = 1; i <= RUNS; i++)); do
    local out_file="/tmp/${output_prefix}_${i}.json"
    local line
    local code
    local t

    line=$(curl --max-time 30 -sS -o "$out_file" -w '%{http_code} %{time_total}' \
      -X POST "$url" -H 'Content-Type: application/json' -d "$payload")

    code=$(echo "$line" | awk '{print $1}')
    t=$(echo "$line" | awk '{print $2}')

    echo "$t" >> "$times_file"
    echo "run=$i time=${t}s code=$code bytes=$(wc -c < "$out_file")"
  done
}

median_from_file() {
  local file="$1"
  sort -n "$file" | awk -v n="$RUNS" 'NR==int((n+1)/2){print $1}'
}

ASSESS_PAYLOAD='{"assignment_id":"bench-a","learner_id":"bench-u","language":"python","repo_url":"https://example.com/repo.git","commit_hash":"bench123","tests_path":"tests"}'
LEARN_PAYLOAD='{"topic":"fastapi","level":"beginner","goals":["routing","validation"]}'

wait_for_health "$BASE_URL"

run_series "assessment deterministic" "$BASE_URL/assessment/evaluate?mode=deterministic" "$ASSESS_PAYLOAD" "assess_det" "/tmp/bench_assess_det_times.txt"
run_series "assessment llm" "$BASE_URL/assessment/evaluate?mode=llm" "$ASSESS_PAYLOAD" "assess_llm" "/tmp/bench_assess_llm_times.txt"
run_series "learning" "$BASE_URL/learning/generate" "$LEARN_PAYLOAD" "learn" "/tmp/bench_learn_times.txt"

echo "assessment_deterministic_median=$(median_from_file /tmp/bench_assess_det_times.txt)s"
echo "assessment_llm_median=$(median_from_file /tmp/bench_assess_llm_times.txt)s"
echo "learning_median=$(median_from_file /tmp/bench_learn_times.txt)s"
