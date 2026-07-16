---
id: github-governance-troubleshooting
title: GitHub Governance Troubleshooting
---

# GitHub Governance Troubleshooting

This guide resolves read-only governance audit failures. It does not authorize or
perform GitHub setting changes.

## `audit` exits with status 1

**Affects:** `scripts/github_governance.py audit`

**Cause:** At least one control is `drift` or `unknown`. A required check name that is
not observed on the target branch head is also drift.

**Fix:**

1. Read the JSON `controls` entries whose `status` is not `compliant`.
2. For `drift`, review the desired policy and current GitHub state. Use the documented
   exact-confirmation `apply` flow only after the change is approved.
3. For `unknown`, rerun locally with `gh` authentication that can read repository
   administration settings.
4. For `branch.required_status_checks_observed`, verify the named workflow runs on the
   target branch and rerun the audit after it completes.

**Prevention:** Run `plan` after changing policy or required workflow names.

**Refs:** #18, ADR-0003
