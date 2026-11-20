#!/bin/bash
# Wait until ci.yml has reported on the branch head.
set -euo pipefail

branch="$1"
sha="$(git ls-remote "https://github.com/${GITHUB_REPOSITORY}.git" "refs/heads/${branch}" | awk '{print $1}')"
if [ -z "$sha" ]; then
  echo "branch ${branch} was not found" >&2
  exit 1
fi
echo "sha=${sha}" >> "$GITHUB_OUTPUT"
gh workflow run ci.yml --ref master -f "sha=${sha}"

for _ in $(seq 1 40); do
  state="$(gh api "repos/${GITHUB_REPOSITORY}/commits/${sha}/status" \
    --jq '[.statuses[] | select(.context=="ci/pytest") | .state][0]' || true)"
  echo "ci/pytest=${state:-pending}"
  if [ "$state" = "success" ]; then
    exit 0
  fi
  if [ "$state" = "failure" ] || [ "$state" = "error" ]; then
    exit 1
  fi
  sleep 15
done
echo "timed out waiting for ci/pytest" >&2
exit 1
