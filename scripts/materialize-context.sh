#!/usr/bin/env bash
# Copy a tool folder with symlinks resolved, so Docker builds see real files.
# Prints the output directory. Temporary: removed in migration Step 7b (R2).
#
# Usage: scripts/materialize-context.sh <tool-folder> [output-dir]
set -euo pipefail
SRC="$1"; OUT="${2:-$(mktemp -d)}"
mkdir -p "$OUT"
tar -C "$SRC" --exclude node_modules --exclude .venv --exclude dist -chf - . | tar -xf - -C "$OUT"
echo "$OUT"
