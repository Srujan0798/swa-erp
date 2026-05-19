---
name: status-report
description: Generate a standardized weekly project status report.
---

# status-report

## Output format
```markdown
# Status Report — Week of YYYY-MM-DD

## Wave progress
- Active wave: wave-N (Name)
- Tasks: X merged / Y total
- Velocity: X tasks/week

## Shipped this week
- (from CHANGELOG.md [Unreleased])

## In flight
- (from work/wave-N/ files without matching reports)

## Awaiting review
- (count of work/reports/wave-N/ pending /review)

## Blockers
- (BLOCKED reports, or open T2 governance items)

## Decisions made
- (new ADRs in docs/decisions/ this week)

## Next week
- (what gets dispatched / shipped per EXECUTION.md)

## Metrics
- Test coverage: X%
- CI status: green / failing N
- Performance budgets: hit / miss
```

## Anti-bloat
Use `caveman` skill for compression if the report exceeds 1 page.
