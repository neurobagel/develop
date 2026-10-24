#!/usr/bin/env bash
# Regenerate the example API responses in examples/api-responses/ from the
# APIs built from the current commit (the neurobagel/<image>:local images).
#
# Ported from neurobagel_examples' make_api_responses.yml, which recorded the
# responses from published images. Uses the two-node test deployment of
# scripts/test-nodes.sh, federating only over its two local nodes:
#   "2 OpenNeuro Datasets" (protected_node, port 8000, aggregated responses)
#   "BIDS Synthetic"       (open_node, port 8001, record-level responses)
#
# Usage: scripts/make-api-responses.sh [--prepared] [--keep]
#   --prepared  skip `scripts/test-nodes.sh prepare` (deployment folders exist)
#   --keep      leave the deployment running afterwards
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/examples/api-responses"
NODES="$ROOT/scripts/test-nodes.sh"

prepared=false; keep=false
for arg in "$@"; do
  case "$arg" in
    --prepared) prepared=true ;;
    --keep) keep=true ;;
    *) echo "Usage: $0 [--prepared] [--keep]" >&2; exit 2 ;;
  esac
done

post() {
  # post <url> <output file>
  curl -sS -X POST "$1" -H "Content-Type: application/json" -d '{}' | jq . > "$OUT/$2"
  echo "Wrote $2"
}

wait_http() {
  local url="$1" elapsed=0
  until [ "$(curl -s -o /dev/null -w '%{http_code}' "$url")" = "200" ]; do
    if [ "$elapsed" -ge 120 ]; then echo "Timed out waiting for $url" >&2; exit 1; fi
    sleep 2; elapsed=$((elapsed + 2))
  done
}

if [ "$prepared" = false ]; then
  "$NODES" prepare --no-public-nodes
fi

# Only the protected node is up: the federation API cannot reach "BIDS Synthetic"
"$NODES" start-portal
"$NODES" start-node protected_node
"$NODES" wait protected_node
"$NODES" connect protected_node
wait_http http://localhost:8080/
wait_http http://localhost:8000/

post http://localhost:8080/datasets fapi_post_datasets_partial_success_207.json
post http://localhost:8080/subjects fapi_post_subjects_partial_success_207.json

# No node API is reachable
docker stop protected_node-api-1 > /dev/null
post http://localhost:8080/datasets fapi_post_datasets_fail_207.json
post http://localhost:8080/subjects fapi_post_subjects_fail_207.json
docker start protected_node-api-1 > /dev/null
wait_http http://localhost:8000/

# Both nodes are up
"$NODES" start-node open_node
"$NODES" wait open_node
"$NODES" connect open_node
wait_http http://localhost:8001/

post http://localhost:8080/datasets fapi_post_datasets_success_200.json
post http://localhost:8080/subjects fapi_post_subjects_success_200.json

# Node API responses: counts (protected node, aggregated) and records (open node)
post http://localhost:8000/subjects napi_post_subjects_counts_results.json
post http://localhost:8001/subjects napi_post_subjects_records_results.json
# The shape of POST /datasets does not depend on response granularity, so one node is enough
post http://localhost:8000/datasets napi_post_datasets_results.json

if [ "$keep" = false ]; then
  "$NODES" down
fi
