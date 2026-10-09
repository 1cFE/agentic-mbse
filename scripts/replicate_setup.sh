#!/usr/bin/env bash
# Install the product in this checkout using the same ownership policy as target repos.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
exec uv run --project "$REPO_ROOT" agentic-mbse init "$REPO_ROOT" "$@"
