# ai-dev-foundation

**AI-native development foundation** — a template repository for projects where AI
agents (Claude Code, ChatGPT, Gemini, Codex, ...) are the primary developers and humans
direct, decide, and review.

> **AI agents:** stop reading this file. Your entry point is [CLAUDE.md](CLAUDE.md)
> (Claude Code) or [AGENTS.md](AGENTS.md) (everyone else).

## What this template provides

| Layer | Location | Purpose |
|-------|----------|---------|
| Rules (single source of truth) | [`.ai/`](.ai/) | Guardrails, security, architecture, coding, testing, release, docs, review — every rule has a stable ID (GR-010, SEC-020, ...) |
| Agent entry points | [`CLAUDE.md`](CLAUDE.md), [`AGENTS.md`](AGENTS.md) | Operating manual + task routing table |
| Task playbooks | [`.skills/`](.skills/) | 10 vendor-neutral skills: requirements, feature, bugfix, refactor, architecture, test, security, documentation, review, release — also exposed as native Claude Code skills under `.claude/skills/` |
| Enforcement L1 | [`.claude/`](.claude/) | Claude Code hooks (command guard + auto format/lint), a read-only command allow-list, native skill wrappers, and a read-only `code-reviewer` subagent |
| Enforcement L2 | [`.pre-commit-config.yaml`](.pre-commit-config.yaml) | Any committer: secret scan, branch guard, lint, unit tests |
| Enforcement L3 | [`.github/workflows/`](.github/workflows/) | CI, CodeQL, secrets/deps/license scan, container, IaC, DAST, Scorecard, release+SBOM |
| Stable command interface | [`Makefile`](Makefile) | `make test` etc. — the only entry points automation uses |
| Stack profiles | [`profiles/`](profiles/) | Reference Makefile implementations per stack + the canonical target contract |
| Decisions | [`docs/adr/`](docs/adr/) | ADRs + decision log |
| Knowledge | [`docs/`](docs/) | Architecture, domain, API, deployment, operations, runbook, troubleshooting, roadmap, glossary |
| GitHub scaffolding | [`.github/`](.github/) | Issue forms, PR template, CODEOWNERS, labels-as-code, Dependabot; plus `renovate.json` |
| Governance bootstrap | [`scripts/setup-github.sh`](scripts/setup-github.sh) | One command applies branch protection, secret scanning, merge policy via `gh` |
| Update distribution | [`template-sync.yml`](.github/workflows/template-sync.yml) + [`.templatesyncignore`](.templatesyncignore) | Foundation updates reach downstream repos as PRs |

## Using this template

1. **Create the repo** from this template (GitHub → "Use this template").
2. **Replace placeholders**: search for `{{` — mission, stack, CODEOWNERS teams, issue
   config URLs.
3. **Wire the Makefile**: copy the closest [`profiles/`](profiles/) Makefile to the
   root (or implement `setup/format/lint/test/build` yourself) — everything else
   (hooks, CI) starts working automatically.
4. **Configure GitHub** (one-time): run `bash scripts/setup-github.sh` (requires
   `gh auth login` with admin) — it applies branch protection, secret scanning + push
   protection, private vulnerability reporting, squash-only merges, and prints the few
   remaining manual steps (Renovate app, Discussion categories, CodeQL languages,
   optional AI-review/DAST variables).
5. **Install local gates**: `make setup && pre-commit install --hook-type pre-commit
   --hook-type pre-push`.
6. **Point your agent at it**: open the repo with Claude Code (reads `CLAUDE.md`
   automatically) or tell any other agent to read `AGENTS.md`. Assign it an issue.

Full walkthrough (new machine, different account, gotchas): [docs/usage.md](docs/usage.md).

## Design principles

AI First · Secure by Default · Least Privilege · Defense in Depth · Everything as Code
(docs, policy, infra) · Convention over Configuration · Clean Architecture · DDD ·
SOLID · Twelve-Factor · GitHub Flow · Conventional Commits · SemVer.

Why it's built this way: [docs/adr/](docs/adr/). How agents behave here:
[.ai/README.md](.ai/README.md).

## License

<!-- TEMPLATE: choose a license and add LICENSE file. -->
