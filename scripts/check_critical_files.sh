#!/usr/bin/env bash
set -euo pipefail

critical_files=(Makefile Dockerfile docker-compose.yml .dockerignore setup.cfg)
for file in "${critical_files[@]}"; do
  test -f "$file" || { echo "Missing critical file: $file" >&2; exit 1; }
done

if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo ".env must not be tracked" >&2
  exit 1
fi

echo "Critical files and secret boundary checks passed."
