#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "[smoke] ERROR: $1" >&2
  exit 1
}

if command -v rg >/dev/null 2>&1; then
  SEARCH_TOOL="rg"
else
  SEARCH_TOOL="grep"
fi

echo "[smoke] wrapper help"
./braintrust --help >/dev/null

echo "[smoke] canonical command help"
for cmd in list get invoke diff update test promote; do
  ./braintrust "$cmd" --help >/dev/null
done

echo "[smoke] missing API key fails fast"
api_error_output="$(env -u BRAINTRUST_API_KEY -u BRAINTRUST_PROJECT_NAME ./braintrust list 2>&1 || true)"
echo "$api_error_output" | "$SEARCH_TOOL" -q "BRAINTRUST_API_KEY" || fail "Expected missing API key guidance"

echo "[smoke] missing project fails fast on project-required command"
project_error_output="$(env -u BRAINTRUST_PROJECT_NAME BRAINTRUST_API_KEY=dummy ./braintrust invoke --slug smoke-test 2>&1 || true)"
echo "$project_error_output" | "$SEARCH_TOOL" -q -- "--project or BRAINTRUST_PROJECT_NAME" || fail "Expected missing project guidance"

echo "[smoke] OK"
