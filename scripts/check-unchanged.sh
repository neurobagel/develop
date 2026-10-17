#!/usr/bin/env bash
# Fail if any protected path of an imported tool differs from its imported head,
# except for the exact paths listed in migration/allowed-changes.txt.
set -euo pipefail
status=0
while read -r dest _repo _upstream rewritten; do
  [[ -z "${dest:-}" ]] && continue
  dirs=$(awk -v d="$dest" '$1 == d { $1 = ""; print }' migration/protected-paths.txt)
  for dir in $dirs; do
    changes=$(git diff --name-only "$rewritten" HEAD -- "$dest/$dir" \
      | grep -vxF -f migration/allowed-changes.txt || true)
    if [[ -n "$changes" ]]; then
      echo "CHANGED under $dest/$dir:"; echo "$changes"; status=1
    fi
  done
done < migration/imported-heads.txt
[[ $status -eq 0 ]] && echo "OK: protected paths unchanged"
exit $status
