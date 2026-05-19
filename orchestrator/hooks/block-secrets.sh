#!/bin/bash
# Pre-commit hook: prevent committing files with apparent secrets.
# Patterns: AWS keys, private keys, .env, common API key shapes.

set -e

STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
[ -z "$STAGED" ] && exit 0

VIOLATIONS=0

while IFS= read -r FILE; do
  [ -z "$FILE" ] && continue

  # Block .env files entirely
  if [[ "$FILE" == ".env" || "$FILE" == *".env" || "$FILE" == *".env."* ]]; then
    if [[ "$FILE" != *".env.example" && "$FILE" != *".env.sample" ]]; then
      echo "[block-secrets] BLOCKED: $FILE looks like an env file"
      VIOLATIONS=$((VIOLATIONS+1))
      continue
    fi
  fi

  # Block apparent secrets in content
  if [ -f "$FILE" ]; then
    if grep -qE '(AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|sk_live_[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36})' "$FILE" 2>/dev/null; then
      echo "[block-secrets] BLOCKED: $FILE contains apparent secret"
      VIOLATIONS=$((VIOLATIONS+1))
    fi
  fi
done <<< "$STAGED"

if [ "$VIOLATIONS" -gt 0 ]; then
  echo "[block-secrets] $VIOLATIONS file(s) blocked. Move secrets to .env (gitignored)."
  exit 1
fi

exit 0
