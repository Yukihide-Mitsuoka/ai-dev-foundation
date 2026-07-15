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

## Validate, plan, and audit

Python 3 is required; no third-party package is used.

```bash
python3 scripts/github_governance.py validate --root .
python3 scripts/github_governance.py plan --root . --repo OWNER/REPOSITORY
python3 scripts/github_governance.py audit --root . --repo OWNER/REPOSITORY
```

`validate` resolves both layers without authentication or network access. `plan` and
`audit` require authenticated `gh` read access and print the same stable, redacted JSON
comparison. They also verify that every required check name is observed on the target
branch head; unrelated observed checks do not create drift. All three commands make no
GitHub setting change.

| Command | Exit 0 | Exit 1 | Exit 2 |
|---------|--------|--------|--------|
| `validate` | Policy valid | — | Invalid policy or input |
| `plan` | Comparison completed, including drift or unknown state | — | Policy, input, or GitHub read failure |
| `audit` | All controls compliant | Drift or unknown state | Policy, input, or GitHub read failure |
The legacy `scripts/setup-github.sh` does not read these policies. It remains a temporary
compatibility apply path with fixed settings until the reconciler gains `apply`.

## Apply action planning boundary

The internal pure-data planner converts a complete comparison into ordered GitHub REST
requests but the public CLI does not execute them yet. The internal execution boundary
requires exact target confirmation, sends one action, reads it back, verifies it, and
replans from fresh state before selecting the next action. A repeated action or any
write, read-back, verification, or replanning failure stops with redacted partial
evidence; it never retries or weakens protection through automatic rollback.

The planner may create only `ai-dev-foundation: branch-governance` as a repository
ruleset. Organization and unrelated rules remain unmanaged, even when they have the same
name.

For API fields absent from policy schema version 1, new rulesets require up-to-date
checks and resolved review threads, but do not dismiss stale approvals or require code
owners. Changing these defaults requires a reviewed schema migration.

Each action records controls, side effects, method, endpoint, and body. Planning fails
closed on unknown state, unobserved checks, or unsafe backend updates. Discovery lists
inactive repository rulesets to prevent duplicate creation. Existing managed rulesets
may be updated only with the generated branch condition and supported rule types. The
planner preserves stricter stale-review, code-owner, merge-method, and check-integration
constraints. Extra rules, active reviewer restrictions, unknown parameters, or missing
detail block the update.

## GitHub discovery boundary

The Python module now has an internal, GET-only discovery boundary for repository,
branch, effective-rules, all repository rulesets, legacy-protection, and security. It pins GitHub
REST API version `2026-03-10`, validates repository and branch targets before invoking
`gh api`, uses a 30-second timeout, and retains only fields needed for governance.
Ruleset bypass identities are reduced to a boolean and never retained. Check runs and
commit statuses are reduced to names before comparison.

Administrator-only fields that the current token cannot read are reported as `unknown`;
mandatory repository, branch, or effective-rules reads fail closed. The module compares
this inventory with resolved policy as deterministic `compliant`, `drift`, or `unknown`
controls and reports unmanaged effective rules without changing them. Public `apply`
remains a later slice.
