#!/usr/bin/env bash
# Import an upstream neurobagel repository with its full history into a folder
# of this monorepo. Tags vX.Y.Z are renamed to <tag-prefix>-vX.Y.Z and bare PR
# references (#123) in commit messages become neurobagel/<repo>#123.
#
# Usage: scripts/import-tool.sh <upstream-repo> <destination-folder> <tag-prefix>
# Example: scripts/import-tool.sh federation-api tools/federation-api federation-api
set -euo pipefail
REPO="$1"; DEST="$2"; PREFIX="$3"
WORK=$(mktemp -d)

git clone "https://github.com/neurobagel/${REPO}.git" "$WORK/src"
BRANCH=$(git -C "$WORK/src" symbolic-ref --short HEAD)
UPSTREAM_HEAD=$(git -C "$WORK/src" rev-parse HEAD)

CALLBACK=$(cat <<EOF
import re
return re.sub(rb'(?<![\w/])#(\d+)', rb'neurobagel/${REPO}#\1', message)
EOF
)

( cd "$WORK/src" && git filter-repo --force \
    --to-subdirectory-filter "$DEST" \
    --tag-rename "v:${PREFIX}-v" \
    --message-callback "$CALLBACK" )
REWRITTEN_HEAD=$(git -C "$WORK/src" rev-parse HEAD)

git fetch "$WORK/src" \
  "+refs/heads/${BRANCH}:refs/remotes/import/${REPO}" \
  "+refs/tags/${PREFIX}-v*:refs/tags/${PREFIX}-v*"
git merge --allow-unrelated-histories --no-edit \
  -m "chore(migration): import ${REPO} into ${DEST}" "refs/remotes/import/${REPO}"
git update-ref -d "refs/remotes/import/${REPO}"

echo "${DEST} ${REPO} ${UPSTREAM_HEAD} ${REWRITTEN_HEAD}" >> migration/imported-heads.txt
git add migration/imported-heads.txt
git commit -m "chore(migration): record imported head of ${REPO}"
