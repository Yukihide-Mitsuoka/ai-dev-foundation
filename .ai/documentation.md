---
id: documentation
title: Documentation Rules
authority: 4
read_when: [documentation, feature, review]
---

# Documentation Rules

Documentation is code (Documentation as Code): versioned, reviewed in PRs, checked in CI,
and **optimized for AI readers** — explicit, structured, unambiguous.

## DOC-001: Writing style for AI readers

- One fact in one place; link (`[text](path)`) instead of repeating. Duplication causes
  contradiction drift.
- Tables and lists over prose. Absolute dates ("2026-07-02"), never "recently".
- Every doc starts with YAML frontmatter (`id`, `title`, plus `status`/`updated` where
  meaningful) and states its purpose in the first paragraph.
- Concrete examples for every rule or API. Fake credentials only (GR-002).
- English for all `.ai/` and `docs/` content (ADR-0002); user-facing docs may add
  localized versions as siblings (`README.ja.md`).
- Files use kebab-case names; headings form a strict hierarchy (one `#`, then `##`...).

## DOC-010: Document inventory and ownership

| Location | Content | Normative? |
|----------|---------|-----------|
| `.ai/` | rules for agents | yes (authority table) |
| `CLAUDE.md`, `AGENTS.md` | agent entry points | yes |
| `docs/adr/` | decisions with context | yes (accepted ADRs) |
| `docs/architecture/` | diagrams, flows, C4 | descriptive |
| `docs/domain/` | domain model, ubiquitous language | descriptive |
| `docs/api/` | API contracts (OpenAPI etc.) | contract |
| `docs/deployment/`, `docs/operations/`, `docs/runbook/`, `docs/troubleshooting/` | ops | descriptive |
| `src/modules/*/MODULE.md` | module contracts | yes |
| `README.md` | project front door | descriptive |

## DOC-030: Doc-update matrix (binding — GR-024)

When a PR contains a change of type X, it MUST update the docs listed:

| Change | Must update |
|--------|-------------|
| New/changed public API | `docs/api/`, MODULE.md, README if user-facing |
| New module / boundary change | `docs/architecture/`, MODULE.md, ADR |
| New env var / config | `.env.example`, `docs/deployment/` |
| New dependency | PR justification (GR-023); `docs/architecture/` if structural |
| Behavior change visible to users | README, CHANGELOG (via commit type) |
| New error state / failure mode | `docs/troubleshooting/`, `docs/runbook/` if ops action needed |
| New domain term | `docs/glossary.md` |
| Decision that constrains the future | ADR + `.ai/decision-log.md` |
| Change to how AI should behave | `.ai/*` (via reviewed PR) |

## DOC-040: Freshness protocol

- If you read a doc that contradicts the code: the code is usually truth for *behavior*,
  the doc for *intent*. Investigate, fix the wrong one in the current PR, note it.
- Docs describing removed features are deleted, not marked "deprecated" forever.
- Each `docs/**/README.md` lists its own update triggers; obey them.
