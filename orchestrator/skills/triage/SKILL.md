---
name: triage
description: Categorize incoming work — bug / feature / question / scope creep — and route appropriately.
version: 1.0.0
allowed-tools:
  - write_file
  - read_file
  - search_files
  - patch
  - terminal
invocation: agent
subagent: true
---

# triage

## Categories
| Category | Route |
|---|---|
| Bug in current wave | Open task brief in active wave's work/ |
| Bug in shipped wave | Hotfix branch + ADR if behavior change |
| Feature in scope | New task in active wave OR new wave |
| Feature out of scope | Update PRD via to-prd, schedule into future wave |
| Question about behavior | Spawn interviewer agent |
| Scope creep request | Flag to user; if accepted, ADR + PRD update |

## Steps
1. Read the user's request
2. Pick category from table
3. If unclear → ask user via interviewer
4. Don't dispatch anything until category is clear
