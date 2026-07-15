---
id: github-governance-policy
title: GitHub Governance Policy
---

# GitHub Governance Policy

These JSON files are the deterministic enforcement projection defined by ADR-0003.
Normative requirements remain in `.ai/`; every foundation minimum references its source
rule ID.

## Ownership

| File | Owner | Template Sync |
|------|-------|---------------|
| `foundation.json` | ai-dev-foundation | Updated from the foundation |
| `repository.json` | Downstream repository | Never overwritten |

Repository overrides may set `target_branch`, `enforcement_backend`, approval count,
last-push approval, required check names, one dependency-update provider, and merged
branch deletion. Unknown fields and attempts to override foundation minimums fail.

## Validate and resolve

Python 3 is required; no third-party package is used.

```bash
python3 scripts/github_governance.py validate --root .
```

The command validates both layers, verifies that every `rule_refs` ID exists, and prints
the resolved policy as stable JSON. It performs no authentication, network request, or
GitHub setting change. The legacy `scripts/setup-github.sh` does not read these files and
remains the apply entry point until later slices add `plan`, `audit`, and `apply`.

## GitHub discovery boundary

The Python module now has an internal, GET-only discovery boundary for repository,
branch, effective-rules, ruleset, legacy-protection, and security state. It pins GitHub
REST API version `2026-03-10`, validates repository and branch targets before invoking
`gh api`, uses a 30-second timeout, and retains only fields needed for governance.
Ruleset bypass identities are reduced to a boolean and never retained.

Administrator-only fields that the current token cannot read are reported as `unknown`;
mandatory repository, branch, or effective-rules reads fail closed. The module compares
this inventory with resolved policy as deterministic `compliant`, `drift`, or `unknown`
controls and reports unmanaged effective rules without changing them. Public `plan` and
`audit` CLI commands remain a later slice; no write behavior exists in this slice.
