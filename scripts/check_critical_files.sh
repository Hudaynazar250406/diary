#!/usr/bin/env bash
set -Eeuo pipefail
# Вызывайте через bash: переносимость без обязательного chmod.
cd "$(git rev-parse --show-toplevel)"
exec "${PYTHON:-python}" scripts/check_critical_files.py
