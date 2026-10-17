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
        until docker logs api-test_graph-1 2>&1 | grep -q "FINISHED UPLOADING DATA"; do
          if [ "$elapsed" -ge "$timeout" ]; then
            echo "Timed out waiting for graph setup" >&2; docker logs api-test_graph-1; exit 1
          fi
          sleep 1; elapsed=$((elapsed + 1))
        done
        uv sync --group dev
        uv run pytest -m "integration or not integration"
        ;;
      *) echo "No tests configured for '{{tool}}'" >&2; exit 1 ;;
    esac

# Lint GitHub workflows and shell scripts
lint:
    actionlint
    shellcheck scripts/*.sh

# Build a tool's Docker image
build tool:
    #!/usr/bin/env bash
    set -euo pipefail
    case "{{tool}}" in
      *) echo "No image build configured for '{{tool}}'" >&2; exit 1 ;;
    esac

# Check that protected paths of imported tools are unchanged
check-unchanged:
    scripts/check-unchanged.sh
