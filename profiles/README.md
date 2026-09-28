---
id: profiles
title: Makefile Reference Implementations
---

# profiles/ — Legacy Makefile Reference Implementations

These optional Makefiles show stack-specific commands from before the Task migration.
They are not active task definitions and must not be copied over a repository's root
`Taskfile.yml`. Implement the required tasks in that repository-owned file instead.

The binding semantics live in the inherited
[Task target contract](../.ai/contracts/foundation/task-targets.md). A child may
remove these examples without removing that contract.

## Available profiles

| Profile | Stack | Source |
|---------|-------|--------|
| [terraform-gcp/](terraform-gcp/) | Terraform (GCP foundations, layered), Python tooling via uv, OPA policies, Excel SSoT generator | adapted 2026-07-02 from a production foundations project |
| [typescript-node/](typescript-node/) | Node.js + pnpm + Prettier + ESLint + tsc + Vitest | authored 2026-07-02 |
| [python-uv/](python-uv/) | Python + uv + Ruff + mypy + pytest | authored 2026-07-02 |

## Using a reference in a new project

1. Read the closest example for stack-specific commands; do not copy its Makefile.
2. Implement those commands as tasks in the root `Taskfile.yml` under the inherited
   Task contract. Keep project-specific tasks separate.
3. Verify: `task lint` on dirty code fails; `task format` fixes it;
   `task nonexistent` fails; `task test-unit` finishes in seconds.
