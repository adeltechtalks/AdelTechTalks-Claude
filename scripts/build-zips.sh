#!/usr/bin/env bash
# Builds downloads/<skill>.zip for every skill under skills/<category>/<skill>/.
# Each zip holds a single top-level <skill>/ folder (the layout Claude.ai expects);
# the skill's README.md is left out since it's a GitHub page, not part of the skill.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p downloads
for skill_md in skills/*/*/SKILL.md; do
  dir=$(dirname "$skill_md")
  name=$(basename "$dir")
  out="$PWD/downloads/$name.zip"
  rm -f "$out"
  (cd "$(dirname "$dir")" && zip -qrX "$out" "$name" -x "$name/README.md" "*/.DS_Store" "*/__pycache__/*")
  echo "built downloads/$name.zip"
done
