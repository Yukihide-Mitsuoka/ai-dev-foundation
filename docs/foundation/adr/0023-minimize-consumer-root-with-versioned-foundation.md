---
id: adr-0023
title: ADR-0023 — Minimize the consumer root while keeping a versioned Foundation
status: proposed
updated: 2026-09-23
---

# ADR-0023: Minimize the consumer root while keeping a versioned Foundation

| Field | Value |
|-------|-------|
| Status | proposed |
| Date | 2026-09-23 |
| Deciders | repository owner |
| Author | Codex (AI agent) |
| Supersedes / Superseded by | Extends ADR-0004, ADR-0007, ADR-0014, and ADR-0015; supersedes none |

## Context

The Foundation already separates reusable agent contracts from protected project
overlays (ADR-0014). Nevertheless, a new repository copies Foundation files into its
root beside project-owned files. A reader cannot reliably identify ownership or
whether a file is active from its location. The Foundation currently has 208 tracked
files, about 1.5 MiB of current file content, and 24 tracked root entries. Storage is
secondary to root readability, but every copied file also adds review and maintenance
surface to descendants.

The same repository may be used under an organization-managed AI or GitHub policy.
Some Foundation defaults, such as release and branch procedures, can differ from that
policy. Task-specific skills already load conditionally, while local hooks and some
workflows may run without a task-specific choice. The current `strengthen-only`
profile does not prove semantic compatibility with external policy.

The solution must retain reviewed direct-parent propagation, a versioned local
contract, existing security controls, and reproducible CI. A clone may be placed in
any directory or run by another agent, so no required rule may depend on an ancestor
`CLAUDE.md`, a user's home directory, or a mutable remote download.

## Options considered

### Option 1: Keep the current layout

This preserves stable paths and has no migration risk. Root ownership remains hard to
read, and optional features remain visually mixed with the consumer's own files.

### Option 2: Put the complete Foundation in an ancestor or user directory

This makes a local checkout sparse, but instruction loading depends on machine layout
and agent runtime. CI, GitHub review, and another user's clone do not receive a pinned
copy. It is suitable for personal or organization-managed additions, not the shared
source of truth.

### Option 3: Fetch a versioned Foundation at runtime

An immutable package or commit could reduce copied files. Every local agent and CI job
would then need installation, authentication, availability, and integrity checks.
Private parents add a credential boundary. This is disproportionate to the measured
storage and would add another delivery path beside Template Sync.

### Option 4: Keep reviewed local inheritance and reduce its root surface

Keep repository-local, versioned contracts. Retain root paths only for a consumer's
own files or verified tool discovery requirements. Place movable Foundation-only
content under declared Foundation-owned paths, and make task and product capabilities
explicit. This requires a staged path migration and a small residual root surface.

## Decision

Adopt Option 4. The following ownership and activation rules govern new Foundation
paths and migrations:

1. A consumer root path MUST be either repository-owned or required at that location
   by a documented tool contract. Thin `CLAUDE.md` and `AGENTS.md` entry adapters,
   project `README.md`, and tool-discovered configuration may remain. Foundation-only
   bodies and examples SHOULD use existing owned namespaces, including
   `.ai/contracts/foundation/` and `docs/foundation/`, or an explicit owned subpath
   when moving them there would misstate their purpose. Avoid a second generic
   `.foundation/` tree with duplicate authorities.
2. Each root entry MUST be inventoried before migration with its owner, discovery
   constraint, direct-parent inheritance class, and activation condition. The inventory
   MUST distinguish protected project paths from synchronized Foundation paths.
   `CHANGELOG.md`, `README.md`, `Makefile`, `.env.example`, `src/`, and project `tests/`
   remain project-owned in descendants. Existing tool entry points MUST keep working
   until a replacement is verified in a direct child.
3. Always-on safety controls, task-routed skills, and optional product or runtime
   capabilities MUST be identified separately. A feature is not considered optional
   merely because its documentation is read on demand: its hook, workflow, or required
   check must also be inactive until the consumer explicitly enables it. Existing
   descendants retain their current checks and triggers until each change is reviewed.
   No classification may silently remove or weaken a security control (GR-030).
4. Organization-managed controls are external constraints. An onboarding review MUST
   identify conflicts with Foundation requirements before activation. Neither an
   overlay nor an agent may silently weaken a Foundation MUST, and the validator MUST
   NOT claim to understand arbitrary natural-language policy. An unresolved conflict
   blocks adoption until a reviewed policy decision reconciles it.
5. The direct-parent manifest, lock, Template Sync PR, `finalize-sync`, and human
   review remain the automatic propagation path. Protected child-owned paths still
   require their existing reviewed manual port. No ancestor-directory file or remote
   runtime fetch becomes a required source. Root-path moves MUST be staged with
   updated references, tests, ownership metadata, and rollback before an old path is
   removed. Propagation proceeds one merged parent hop at a time.

The first inventory will classify paths by these concrete examples; it will not move
them merely because they appear here:

| Class | Examples | Initial treatment |
|-------|----------|-------------------|
| Fixed tool entry | `CLAUDE.md`, `AGENTS.md`, `.github/` | Keep the required path; minimize its Foundation-owned body where safe. |
| Consumer-owned | `README.md`, `Makefile`, `src/`, project `tests/` | Keep at the consumer's normal location and protect from parent overwrite. |
| Foundation-owned | `.ai/contracts/foundation/`, `docs/foundation/`, inherited `scripts/` | Group internal implementation under declared owned paths when callers and inheritance metadata can migrate together. |
| Conditional candidate | `.skills/`, `.devcontainer/`, capability-specific workflows | Audit actual triggers and security dependencies before declaring any part optional. |

## Consequences

**Positive:** consumers can identify their own root files, optional features have an
explicit activation boundary, and teams can inspect a versioned policy without relying
on a developer's directory layout. Existing review and security boundaries remain.

**Negative:** tool-required root files cannot disappear. Path migration changes many
references and may require protected child ports. Capability classification adds a
small onboarding decision. Real organization-policy conflicts still require human
review; they cannot be resolved by a path move or text validator.

Migration is expand, verify, then contract. First publish a complete root ownership and
activation inventory. Move one Foundation-only path family at a time, retaining a
working compatibility entry point where required; update manifests, ignore contracts,
documentation links, and tests in the same reviewed slice. Verify one direct child and
one multi-level child before changing the default for new consumers. Remove obsolete
paths only in separately reviewable, explicitly scoped changes. Rollback restores the
previous path mapping through a normal PR; the accepted parent lock remains the source
of provenance.

**Follow-ups:** Track implementation and fleet evidence in
[Issue #230](https://github.com/Yukihide-Mitsuoka/ai-dev-foundation/issues/230).
