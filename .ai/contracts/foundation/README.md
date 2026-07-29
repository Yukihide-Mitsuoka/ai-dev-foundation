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

This expand-phase file does not change current agent entry behavior. `CLAUDE.md`,
`AGENTS.md`, and `.skills/` remain authoritative until a later reviewed migration adds
an entry contract here and activates manifest schema version 2 in each child.

Template exports use
`.ai/contracts/templates/<owner>/<repository>/`. Project-owned instructions use the
protected `.ai/project/` root. The exact ordered files are declared in the protected
agent profile documented by the
[inheritance contract](../../../.github/inheritance/README.md).
