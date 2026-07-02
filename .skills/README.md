# .skills/ — Agent Skill Library

Vendor-neutral task procedures. Each `*.skill.md` is a self-contained playbook an agent
loads **when the task matches** (routing table: `.ai/README.md`). Plain Markdown — works
with Claude Code, ChatGPT, Gemini, Codex, or a human.

## Format contract

Every skill has YAML frontmatter (`name`, `description`, `triggers`, `reads`) and these
sections, in order:

1. **Purpose** — what outcome this skill produces
2. **Inputs** — what must exist/be known before starting (and how to get it)
3. **Process** — numbered steps
4. **Decision criteria** — how to choose when the process forks
5. **Outputs** — artifacts that must exist when done
6. **Checklist** — final verification (all boxes must pass)

## Inventory

| Skill | Use when |
|-------|----------|
| [feature.skill.md](feature.skill.md) | implementing new functionality |
| [bugfix.skill.md](bugfix.skill.md) | fixing incorrect behavior |
| [refactor.skill.md](refactor.skill.md) | restructuring without behavior change |
| [architecture.skill.md](architecture.skill.md) | changing structure/boundaries/tech (needs ADR) |
| [test.skill.md](test.skill.md) | adding/improving tests |
| [security.skill.md](security.skill.md) | security hardening, vuln response, audits |
| [documentation.skill.md](documentation.skill.md) | writing/maintaining docs |
| [review.skill.md](review.skill.md) | reviewing a PR or self-reviewing |
| [release.skill.md](release.skill.md) | preparing a release |

## Claude Code native integration (optional)

To expose a skill natively, create `.claude/skills/<name>/SKILL.md` whose body is:
frontmatter (`name`, `description` copied from here) + one instruction:
"Read `.skills/<name>.skill.md` and follow it exactly." Keep `.skills/` as the single
source of truth — never fork content into the wrapper.
