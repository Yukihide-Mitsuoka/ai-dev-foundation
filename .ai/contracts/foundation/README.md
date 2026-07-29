---
id: foundation-agent-contract-namespace
title: Foundation Agent Contract Namespace
authority: 4
read_when: [agent-contract-migration]
---

# Foundation Agent Contract Namespace

This inherited directory owns foundation agent instructions introduced by ADR-0014.
Child manifests inherit the directory root so a new contract file does not require a
new path entry in every child manifest.

The identity-free foundation entry contract is
[`agent-entry.md`](agent-entry.md). Adding it during the expand phase does not change
current agent entry behavior. `CLAUDE.md`, `AGENTS.md`, and `.skills/` remain
authoritative until a later reviewed migration activates manifest schema version 2
and an entry adapter in each child.

Template exports use
`.ai/contracts/templates/<owner>/<repository>/`. Project-owned instructions use the
protected `.ai/project/` root. The exact ordered files are declared in the protected
agent profile documented by the
[inheritance contract](../../../.github/inheritance/README.md).
