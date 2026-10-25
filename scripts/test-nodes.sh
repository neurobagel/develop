#!/usr/bin/env bash
# Two-node Neurobagel test deployment, built from this repository's stack/ and
# the locally built images (neurobagel/<image>:local, see `just images`).
#
# Ported from the recipes repository's .github/actions/test-setup, which the
# full-stack e2e tests (e2e/) and the example API responses (examples/) use:
#   portal          federation API (port 8080) and query tool (port 3000)
#   protected_node  node API (port 8000) with two OpenNeuro datasets,
#                   aggregated responses
#   open_node       node API (port 8001) with the synthetic example dataset,
#                   record-level responses
# The portal federates over both nodes as "2 OpenNeuro Datasets" and
# "BIDS Synthetic". Each deployment runs from its own copy of stack/ in
# .test-nodes/<name>/, because the graph setup writes its log into the
# deployment folder.
#
# Usage: scripts/test-nodes.sh <command> [--no-public-nodes]
#   prepare   create and configure the deployment folders
#   start     launch the deployments, wait for both graphs, connect networks
#   up        prepare, then start
#   down      stop the deployments and remove their volumes
# Granular commands, used by scripts/make-api-responses.sh:
#   start-portal | start-node <protected_node|open_node> | wait <node> | connect <node>
#   (connect: attach the portal's federation API to the node's network)
#
# --no-public-nodes (with prepare/up): the federation API federates only over
# the two local nodes, not the public Neurobagel node directory.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$ROOT/.test-nodes"
OPENNEURO_REPO="https://github.com/neurobagel/openneuro-annotations.git"
TIMEOUT="${TEST_NODES_TIMEOUT:-600}"

compose() {
  local name="$1"; shift
  (cd "$WORK/$name/stack" && docker compose -f docker-compose.noproxy.prod.yml "$@")
}

set_env() {
  # Set KEY=VALUE in a .env file, also if the line is commented out
  local file="$1" key="$2" value="$3"
  if grep -qE "^#?[[:space:]]?${key}=" "$file"; then
    sed -i -E "s|^#?[[:space:]]?${key}=.*|${key}=${value}|" "$file"
  else
    echo "${key}=${value}" >> "$file"
  fi
}

copy_stack() {
  local name="$1"
  mkdir -p "$WORK/$name"
  rm -rf "$WORK/$name/stack"
  cp -r "$ROOT/stack" "$WORK/$name/stack"
  rm -rf "$WORK/$name/stack/scripts/logs"
  cp "$WORK/$name/stack/template.env" "$WORK/$name/stack/.env"
}

prepare() {
  local public_nodes="$1"

  # Portal: federation API and query tool
  copy_stack portal
  local env="$WORK/portal/stack/.env"
  set_env "$env" COMPOSE_PROJECT_NAME portal
  set_env "$env" COMPOSE_PROFILES portal
  set_env "$env" NB_FAPI_TAG local
  set_env "$env" NB_QUERY_TAG local
  set_env "$env" NB_FEDERATE_REMOTE_PUBLIC_NODES "$public_nodes"
  # The noproxy compose file derives the query tool's API URL from a domain; point it at the local federation API
  sed -i 's|^[[:space:]]*NB_API_QUERY_URL:.*|      NB_API_QUERY_URL: http://localhost:8080|' \
    "$WORK/portal/stack/docker-compose.noproxy.prod.yml"
  echo '[{"NodeName": "2 OpenNeuro Datasets", "ApiURL": "http://protected_node-api-1:8000"},{"NodeName": "BIDS Synthetic", "ApiURL": "http://open_node-api-1:8000"}]' \
    > "$WORK/portal/stack/local_nb_nodes.json"

  # Protected node: two OpenNeuro datasets (sex and age annotations only)
  copy_stack protected_node
  rm -rf "$WORK/protected_node/openneuro-annotations" "$WORK/protected_node/openneuro_mini_data"
  git clone --quiet --depth 1 "$OPENNEURO_REPO" "$WORK/protected_node/openneuro-annotations"
  mkdir -p "$WORK/protected_node/openneuro_mini_data"
  cp "$WORK/protected_node/openneuro-annotations/jsonld/ds000001_derivative.jsonld" \
     "$WORK/protected_node/openneuro-annotations/jsonld/ds000002_derivative.jsonld" \
     "$WORK/protected_node/openneuro_mini_data/"
  env="$WORK/protected_node/stack/.env"
  set_env "$env" COMPOSE_PROJECT_NAME protected_node
  set_env "$env" LOCAL_GRAPH_DATA ../openneuro_mini_data
  set_env "$env" NB_NAPI_TAG local
  echo "testadminpassword1" > "$WORK/protected_node/stack/secrets/NB_GRAPH_ADMIN_PASSWORD.txt"
  echo "testpassword1" > "$WORK/protected_node/stack/secrets/NB_GRAPH_PASSWORD.txt"

  # Open node: the synthetic example dataset in stack/data, record-level responses
  copy_stack open_node
  env="$WORK/open_node/stack/.env"
  set_env "$env" COMPOSE_PROJECT_NAME open_node
  set_env "$env" NB_GRAPH_PORT_HOST 7201
  set_env "$env" NB_NAPI_PORT_HOST 8001
  set_env "$env" NB_RETURN_AGG false
  set_env "$env" NB_NAPI_TAG local

  echo "Prepared portal, protected_node and open_node in $WORK"
}

start_portal() { compose portal up -d; }

start_node() { compose "$1" up -d; }

wait_node() {
  local name="$1" log="$WORK/$1/stack/scripts/logs/DEPLOY.log" elapsed=0
  until [ -f "$log" ] && grep "Finished setting up the Neurobagel graph backend." "$log" > /dev/null; do
    if [ "$elapsed" -ge "$TIMEOUT" ]; then
      echo "Timed out waiting for the graph of $name" >&2
      docker logs "$name-graph-1" >&2 || true
      exit 1
    fi
    sleep 2; elapsed=$((elapsed + 2))
  done
  echo "Graph of $name is ready"
}

connect() {
  # Attach the portal's federation API to a node's network, so it reaches that node's API by container name.
  # (Recipes' test setup instead attached open_node-api-1 to the protected node's network; the service name
  # `graph` then resolves to both nodes' graphs from inside that API, and it may query the wrong one.)
  local network="${1}_default"
  if ! docker inspect -f '{{json .NetworkSettings.Networks}}' portal-federation-1 | grep "\"${network}\"" > /dev/null; then
    docker network connect "$network" portal-federation-1
  fi
}

check_running() {
  local container missing=0
  for container in portal-federation-1 portal-query_federation-1 \
      protected_node-graph-1 protected_node-api-1 open_node-graph-1 open_node-api-1; do
    if [ -z "$(docker ps --filter "name=^${container}$" --format '{{.Names}}')" ]; then
      echo "Container $container is not running" >&2
      docker logs "$container" >&2 || true
      missing=1
    fi
  done
  [ "$missing" -eq 0 ] && echo "All containers are running"
  return "$missing"
}

start() {
  start_portal
  start_node protected_node
  start_node open_node
  wait_node protected_node
  wait_node open_node
  connect protected_node
  connect open_node
  check_running
}

down() {
  local name
  for name in portal protected_node open_node; do
    if [ -d "$WORK/$name/stack" ]; then
      compose "$name" down -v --remove-orphans || true
    fi
  done
}

cmd="${1:-}"; shift || true
public_nodes=True
for arg in "$@"; do
  case "$arg" in
    --no-public-nodes) public_nodes=False ;;
  esac
done

case "$cmd" in
  prepare) prepare "$public_nodes" ;;
  start) start ;;
  up) prepare "$public_nodes"; start ;;
  down) down ;;
  start-portal) start_portal ;;
  start-node) start_node "$1" ;;
  wait) wait_node "$1" ;;
  connect) connect "$1" ;;
  *) echo "Usage: $0 prepare|start|up|down [--no-public-nodes]" >&2; exit 2 ;;
esac
