#!/bin/bash
# Block destructive operations unconditionally (T3).

set -e
CMD="$*"

case "$CMD" in
  *"rm -rf /"*|*"rm -rf /*"*)
    echo "[T3-BLOCK] Refusing: $CMD" >&2
    exit 1
    ;;
  *"git push --force "*main*|*"git push --force-with-lease "*main*)
    echo "[T3-BLOCK] Refusing force-push to main" >&2
    exit 1
    ;;
  *"git reset --hard "*HEAD*~*)
    echo "[T2-WARN] git reset --hard discards work. Confirm via user." >&2
    ;;
  *"DROP TABLE"*|*"DROP DATABASE"*|*"TRUNCATE"*)
    echo "[T3-BLOCK] Refusing destructive SQL: $CMD" >&2
    exit 1
    ;;
esac

exit 0
