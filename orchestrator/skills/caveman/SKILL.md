---
name: caveman
description: Compressed communication mode. ~75% token reduction. Use for handoffs and long-context summaries.
---

# caveman

## When to use
- Writing HANDOFF.md
- Summarizing a long debugging session into MEMORY.md
- Compacting reports for /handoff command
- Anytime context budget is tight

## Style
- Short sentences. Drop "the", "a", "it", obvious pronouns.
- Imperative verbs (not "you should X" → just "X")
- Tables and bullet lists over prose
- File paths as `path/to/file.py:42` (clickable in IDE)
- Numbers + concrete nouns; cut adjectives

## Example
Before (prose):
> The auth service has a critical bug where the JWT validation is not properly checking the expiration time, which means that expired tokens are still accepted, allowing users to maintain access indefinitely.

After (caveman):
> Bug: auth JWT skips expiry check. Expired tokens accepted. Fix at `core/security.py:88`.

## Quality
Same information density. Lower token count. Reader picks it up faster.
