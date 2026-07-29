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
- Load `.ai/workflow.md` for implementation work. Land code, tests, and required
  documentation together; record structural or technology decisions in an accepted
  ADR before implementation.
- Use the pull-request template completely. PR titles and commits follow Conventional
  Commits, releases follow SemVer, and squash merging keeps the main branch releasable.
- Complete the self-review in `.ai/review-checklist.md` before opening a PR.
- After every edit, run `make format` and `make lint`.
- Use only canonical `make` targets for formatting, linting, tests, builds, and
  repository diagnostics.
- Preserve unrelated worktree changes and do not weaken checks to make a change pass.
- Guardrails remain absolute: do not push directly to the protected main branch,
  bypass checks, fabricate results, or perform a destructive operation without
  specific approval.

## Canonical commands

Automation and agents use only these stable entry points:

```text
make setup   make format   make lint   make test   make test-unit
make test-integration   make coverage   make build   make run
make security-scan   make sbom   make clean   make doctor
```

Their binding semantics live in `profiles/README.md`. A newly instantiated repository
may retain documented no-op targets until its stack profile is wired.

## Runtime integration

Claude Code reads `.claude/README.md` completely and applies its runtime-specific
controls. Other runtimes use the capability mapping in `AGENTS.md` and must provide
equivalent formatting, linting, command-guard, skill-loading, and secret-handling
behavior.

## Escalation

Stop and ask a human when:

- rules conflict or a guardrail blocks the request;
- an architecture change lacks an accepted ADR;
- authentication, payments, personal-data schema, data deletion, production
  configuration, or spending money is involved;
- ambiguity permits materially different implementations;
- the same failing approach would be attempted a third time; or
- completion requires new authority, an irreversible action, or a material expansion
  of scope.

Report the context, options, recommendation, and specific required decision. Otherwise,
decide, act, and record reasoning in the repository's decision system.

## Definition of done

Verify the smallest relevant checks first, then the broader canonical checks required
by the routed workflow. WF-090 is authoritative: acceptance criteria met, tests green,
lint clean, documentation current, self-review complete, PR complete with green CI,
and no guardrail violated. Report exactly what was and was not verified.
