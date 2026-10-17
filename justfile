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
