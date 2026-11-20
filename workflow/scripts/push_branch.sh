#!/bin/bash
# Push the issue branch with PR_TOKEN. The model step does not run this script.
set -euo pipefail

branch="$1"
message="$2"

git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git config user.name "github-actions[bot]"
git add -- tinydb tests
if git diff --cached --quiet; then
  echo "no product change to commit" >&2
  exit 1
fi
git commit -m "$message"
git push "https://x-access-token:${PR_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" "HEAD:refs/heads/${branch}"
echo "branch=${branch}" >> "$GITHUB_OUTPUT"
