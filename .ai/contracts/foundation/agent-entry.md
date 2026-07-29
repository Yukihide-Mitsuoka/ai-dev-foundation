---
id: foundation-agent-entry
title: Foundation Agent Entry Contract
authority: 3
read_when: [agent-entry, task-intake]
---

# Foundation Agent Entry Contract

This vendor-neutral contract defines the reusable foundation instructions for AI
agents. It contains no repository identity, product requirements, or stack-specific
behavior. A protected agent profile activates and composes this file; its presence
alone does not replace the repository's current entry files.

## Authority and conflicts

Apply instructions in this order: `.ai/guardrails.md`, security rules, the active
agent entry contract, routed `.ai/` rules, then `docs/`. Never resolve a conflict
silently: apply the higher authority and report the conflict.

## Task intake

1. Read `.ai/guardrails.md` completely.
2. Read `.ai/README.md` completely and use its routing table for the current task.
3. If `docs/development-handoff.md` exists and the task continues active work, read it
   completely.
4. Read every routed rule and matching skill completely before acting.
5. Discover context with indexes and repository search, then read selected sources
   completely. Broaden discovery whenever relevance or correctness is uncertain.

## Contract composition

The protected agent profile lists inputs in deterministic order:

1. foundation contract;
2. template overlays from the oldest parent to the direct parent;
3. project overlay.

Composition is `strengthen-only`. A later template or project layer may add stricter,
more specific instructions, but it must not weaken a foundation prohibition or
security boundary. Repository identity and stack-specific behavior belong only in
their owner-qualified template overlay or protected project overlay.

## Change protocol

- Trace non-trivial work to an issue, use a task branch, and deliver it through a
  reviewed pull request.
- Record structural or technology decisions in an accepted ADR before implementation.
- After every edit, run `make format` and `make lint`.
- Use only canonical `make` targets for formatting, linting, tests, builds, and
  repository diagnostics.
- Preserve unrelated worktree changes and do not weaken checks to make a change pass.

## Completion and escalation

Verify the smallest relevant checks first, then the canonical broader checks required
by the routed workflow. Review the final diff for security, correctness, tests,
documentation, and scope. Stop and ask for direction when completion requires new
authority, an irreversible action, or a material expansion of scope.
