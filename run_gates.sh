#!/bin/bash
# Run all gates and commit if all pass

set -e

cd /Users/srujansai/Desktop/swa-erp

echo "=== Running Backend Gates ==="
echo "ruff..."
ruff check src/backend/ || exit 1

echo "black..."
python3 -m black --check src/backend/ || exit 1

echo "mypy..."
python3 -m mypy src/backend/ --explicit-package-bases || exit 1

echo "=== Running Frontend Gates ==="
cd /Users/srujansai/Desktop/swa-erp/src/frontend

echo "tsc..."
npx tsc --noEmit || exit 1

echo "eslint..."
npx eslint . --ext ts,tsx --max-warnings 0 || exit 1

echo "vitest with coverage..."
npx vitest run --coverage || exit 1

cd /Users/srujansai/Desktop/swa-erp

echo "=== All Gates Passed ==="
echo "Committing changes..."

git add -A
git commit -m "chore: continuous improvement - all gates green $(date -u +%Y-%m-%dT%H:%M:%SZ)" || echo "No changes to commit"
git push origin main || echo "Push failed or no changes"

echo "=== Loop iteration complete ==="
