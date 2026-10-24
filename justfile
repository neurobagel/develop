# Neurobagel monorepo task runner. Run `just --list` for all recipes.

# Run a tool's test suite
test tool:
    #!/usr/bin/env bash
    set -euo pipefail
    case "{{tool}}" in
      federation-api)
        cd tools/federation-api
        uv sync --group dev
        uv run pytest
        ;;
      api)
        cd tools/api
        docker compose up -d test_graph export_datasets_metadata
        timeout=120; elapsed=0
        # grep -q would close the pipe early; with pipefail, docker logs then fails on SIGPIPE
        until docker logs api-test_graph-1 2>&1 | grep "FINISHED UPLOADING DATA" >/dev/null; do
          if [ "$elapsed" -ge "$timeout" ]; then
            echo "Timed out waiting for graph setup" >&2; docker logs api-test_graph-1; exit 1
          fi
          sleep 1; elapsed=$((elapsed + 1))
        done
        uv sync --group dev
        uv run pytest -m "integration or not integration"
        ;;
      bagel-cli)
        cd tools/bagel-cli
        uv sync --group dev
        uv run pytest -m "integration or not integration"
        ;;
      query-tool)
        cd tools/query-tool
        npm ci
        npm run lint:check
        npm run format:check
        npm run typecheck
        npm run test:component
        ;;
      annotation-tool)
        cd tools/annotation-tool
        npm ci
        npm run lint:check
        npm run format:check
        npm run typecheck
        npm run test:unit
        npm run test:component
        ;;
      *) echo "No tests configured for '{{tool}}'" >&2; exit 1 ;;
    esac

# Lint GitHub workflows and shell scripts
lint:
    actionlint
    shellcheck scripts/*.sh

# Build a tool's Docker image from the repository root, tagged neurobagel/<image>:local
build tool:
    #!/usr/bin/env bash
    set -euo pipefail
    case "{{tool}}" in
      api) image=api ;;
      federation-api) image=federation_api ;;
      query-tool) image=query_tool ;;
      bagel-cli)
        # The image installs the wheel built here, the same artifact that is published to PyPI
        image=bagelcli
        rm -rf tools/bagel-cli/dist
        (cd tools/bagel-cli && uv build --wheel)
        ;;
      *) echo "No image build configured for '{{tool}}'" >&2; exit 1 ;;
    esac
    docker build -f "tools/{{tool}}/Dockerfile" -t "neurobagel/${image}:local" .

# Build the api, federation-api and query-tool images, tagged :local
images:
    just build api
    just build federation-api
    just build query-tool

# Run a local Neurobagel stack (stack/) with the :local images: node API on 8000, federation API on 8080, query tool on 3000
dev: images
    #!/usr/bin/env bash
    set -euo pipefail
    cd stack
    [ -f .env ] || cp template.env .env
    [ -f local_nb_nodes.json ] || cp local_nb_nodes.template.json local_nb_nodes.json
    NB_NAPI_TAG=local NB_FAPI_TAG=local NB_QUERY_TAG=local NB_API_QUERY_URL=http://localhost:8080 \
      docker compose up -d

# Stop the local stack started by `just dev`
dev-down:
    cd stack && docker compose down

# Start or stop the two-node test deployment (scripts/test-nodes.sh): up, down, prepare, start
test-nodes command *args:
    scripts/test-nodes.sh {{command}} {{args}}

# Build the images, start the two-node test deployment, and run the full-stack Cypress tests in e2e/
e2e: images
    scripts/test-nodes.sh up --no-public-nodes
    cd e2e && npm ci && npx cypress run --browser chrome --config excludeSpecPattern="**/simple-test.cy.js"

# Regenerate examples/api-responses/ from the APIs built from this checkout
examples: images
    scripts/make-api-responses.sh

# Check that protected paths of imported tools are unchanged
check-unchanged:
    scripts/check-unchanged.sh
