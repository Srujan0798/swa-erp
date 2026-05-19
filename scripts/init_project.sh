#!/bin/bash
# One-time project initialization. Run after cloning.

set -e
cd "$(dirname "$0")/.."

echo "=== swa-erp init ==="

# 1. Generate .env from .env.example with a real SECRET_KEY
if [ ! -f .env ]; then
  echo "[1/4] Creating .env from .env.example..."
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  sed "s/replace-with-openssl-rand-hex-32/$SECRET/" .env.example > .env
  echo "       .env created with generated SECRET_KEY"
else
  echo "[1/4] .env already exists — skipping"
fi

# 2. Initialize git if needed
if [ ! -d .git ]; then
  echo "[2/4] git init..."
  git init -b main
  git add .
  git commit -m "chore: initial project structure from OS-Setup v1.1"
else
  echo "[2/4] git already initialized"
fi

# 3. Install pre-commit hooks
if command -v pre-commit > /dev/null; then
  echo "[3/4] Installing pre-commit hooks..."
  pre-commit install || true
else
  echo "[3/4] pre-commit not installed — skipping (install via: pip install pre-commit)"
fi

# 4. Reminder
echo "[4/4] Done."
echo ""
echo "Next steps:"
echo "  1. Open Claude Code (or Kimi) in this directory"
echo "  2. Run: /status"
echo "  3. Run: /dispatch wave-1"
echo "  4. Open OpenCode CLI windows, paste task files from work/wave-1/"
