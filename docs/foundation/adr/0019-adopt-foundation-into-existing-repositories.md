---
id: adr-0019
title: ADR-0019 — Adopt the foundation into existing repositories
status: proposed
updated: 2026-09-02
---

# ADR-0019: Adopt the foundation into existing repositories

| Field | Value |
|-------|-------|
| Status | proposed |
| Date | 2026-09-02 |
| Deciders | repository owner |
| Author | Codex (AI agent) |
| Supersedes / Superseded by | Extends ADR-0004, ADR-0014, and ADR-0015; supersedes ADR-0008 only by adding one named Japanese guide exception |

## Context

`Use this template` creates a child whose inherited files match one exact parent commit.
The existing `bootstrap-child` command verifies that condition before it writes the
manifest, lock, agent profile, ignore contract, and reviewed child-owned payloads. An
existing repository does not satisfy that precondition: parent-owned paths can be
missing or different, and project-owned paths can use names the parent export does not
yet classify.

Operators can copy files manually, but that does not prove complete ownership,
executable modes, direct-parent provenance, or repeatability. Recreating the repository
from a template would discard or rewrite useful history. Adding another long-running
template transport would duplicate the existing reviewed Template Sync path and increase
approval and drift risk.

The adoption mechanism must preserve existing history and project content, fail closed
on ownership ambiguity, keep every reviewed change within GR-020, and join the current
inheritance model only after the complete inherited tree matches one exact parent
commit. It must not claim an accepted lock while inherited content is incomplete, add a
second continuing transport, or add routine AI context. The repository owner also
requires the operator guide to be written in Japanese as a narrowly named human-facing
exception to ADR-0008.

## Options considered

### Option 1: Keep manual adoption

Document file-copy and metadata-editing steps without a reconciler. This adds no code,
but omissions and accidental overwrites remain dependent on operator inspection. The
result cannot be proven idempotent before review.

### Option 2: Recreate the repository from the template

Create a new templated repository and replay the existing project into it. The bootstrap
path remains unchanged, but repository history, settings, open work, and integrations
must be migrated. The disruption is disproportionate to adding a bounded adoption path.

### Option 3: Adopt an external template updater

Use a second tool such as a subtree or general template reapplication system. This can
copy files into an existing repository, but it does not share the current manifest,
protected-path, direct-parent, agent-profile, or single-flight review contracts. Keeping
it after adoption would create two inheritance transports.

### Option 4: Copy and activate the complete contract in one adoption PR

Add a distinct `adopt-child` operation to `template_inheritance.py`. It uses the direct
parent's existing export and exact commit, reports every ownership or content conflict
before writing, and copies the inherited tree plus activation metadata in one PR. This
is atomic, but a normal parent export commonly exceeds GR-020. A broad bot or adoption
exception would weaken the shared review boundary, while splitting the PR after writing
the accepted lock would leave a misleading partial contract.

### Option 5: Prepare bounded exact copies, then activate once

Use one local `adopt-child` operation with separate preparation and activation phases.
Preparation copies only exact parent-owned content in bounded reviewed slices and does
not create or advance the inheritance contract. Activation remains blocked until every
inherited path matches the same exact parent commit; it then writes the small metadata
and reviewed child-owned boundary payload. Template Sync stays disabled until activation
merges and remains the only scheduled transport afterward.

## Decision

Adopt Option 5.

`adopt-child` MUST be a one-time, local, idempotent operation distinct from strict
template-copy bootstrap. Its default mode MUST be read-only. The operator MUST select
the closest currently applicable maintained parent by the repository's primary
deliverable and MUST NOT skip an applicable intermediate template. The plan MUST require
a clean non-default child branch, credential-free GitHub origins for the child and
direct parent, an exact full parent commit on that parent's declared first-parent branch,
and the parent's validated inheritance export.

The plan MUST classify the complete adoption surface at least as:

- inherited content already identical to the exact parent;
- missing inherited content that can be added byte-for-byte with its executable mode;
- conflicting inherited content that requires human resolution;
- existing or required child-owned content that remains protected; and
- tracked content with no declared owner that requires an ownership decision.

An adoption payload MAY add existing project-owned paths to the parent's protected-path
baseline. It MUST NOT remove a protected baseline path, reclassify a parent-owned
inherited path, overlap owners, or leave tracked content implicitly protected. A
conflicting inherited path must be made identical to the parent in the reviewed branch,
or the adoption remains blocked. Choosing another direct parent or declining adoption
remains valid.

The plan MUST derive every protected workflow and other manual boundary from the parent
export and ignore contract. Each boundary must be reported with a required decision:
retain the child implementation, port the parent control, or block activation. A path
cannot be both inherited and protected. Protecting an existing conflicting file therefore
means declining future inheritance for that path and is valid only when the parent export
already assigns that path to the protected baseline.

Preparation apply MUST require the exact repository and source commit to be repeated.
It MAY write only a caller-selected bounded subset of missing parent-owned files from the
exact commit, preserving exact bytes and executable modes. It MUST NOT write the
manifest, lock, agent profile, Template Sync workflow, project overlay, README archive,
or any other activation payload. Every preparation PR MUST remain within GR-020 and
identify the exact parent repository and commit. Repeated preparation of an already
identical subset MUST make no change.

Preparation and activation MUST preserve existing protected content and MUST NOT
overwrite a non-identical file, delete a path, follow a symlink, fetch, alter history or
remotes, commit, push, create or merge a PR, call GitHub, enable Template Sync, or apply
repository governance. The exact source commit remains fixed across all preparation
slices; a newer parent commit starts a new plan instead of silently changing the source.

Activation MUST remain blocked until all inherited paths match the exact source commit,
including file absence, bytes, and executable modes, and every conflict, unowned path,
README ownership requirement, and manual boundary has an explicit valid result. Only
then MAY activation write the existing manifest, lock, agent-profile, README-archive,
project-overlay, Template Sync exclusion and workflow, and other reviewed child-owned
payloads. The activation PR MUST be small, pass the normal inheritance validator and
repository checks, and use Japanese explanatory prose under ADR-0020. A repository
adopted without separately publishing a validated child export is a leaf; making it an
inheritable template is a separate reviewed architecture decision.

Template Sync MUST remain disabled throughout preparation and activation. After the
activation PR merges, operators separately apply GitHub governance, configure private
parent authentication when applicable, and opt into Template Sync. All later parent
changes use the existing direct-parent reviewed propagation path. The initial inherited
tree MUST NOT be transported by Template Sync because doing so would require an
incomplete manifest, lock, agent profile, or authentication dependency before the
contract can validate.

Add one descriptive Japanese exception at
`docs/foundation/guides/adopt-existing-repository.ja.md`. The guide MUST link to the
English inheritance contract and this ADR, MUST NOT define normative behavior, and MUST
not enter baseline or general task routing. Update the exact localized-file allowlist so
all other Foundation documentation remains English under ADR-0008.

## Consequences

**Positive:**

- Existing repositories retain their history, identity, and project-owned content.
- A deterministic plan exposes missing files, conflicts, and unowned paths before any
  write.
- Bounded preparation PRs never claim that an incomplete inheritance contract is active.
- One small activation PR establishes the same contract as template-created children.
- Adoption adds no second continuing transport or recurring approval path.
- The Japanese procedure is available for the operator without increasing routine AI
  context.

**Negative:**

- Adoption is more work than template initialization because every pre-existing
  ownership conflict needs a human decision.
- The inheritance reconciler gains another bounded command and additional fixtures.
- Large parent exports require multiple one-time preparation PRs before activation.
- The exact source commit cannot advance during preparation; choosing a newer parent
  restarts the plan for any remaining content.
- The third Japanese guide must be maintained against its English authorities.

Migration is expand-only: add failing-first planner tests, implement read-only
classification, add confirmed bounded preparation, add the complete-state activation
gate, then publish the Japanese guide and allowlist update. Prove one non-production
existing repository from preparation through post-activation Template Sync before
recommending the path generally. Before activation, rollback reverts only the reviewed
preparation PRs; after activation, rollback is a normal reviewed child PR and lock
change, not a history rewrite.

**Follow-ups:** implement `adopt-child` and bounded fixtures in
[Issue #211](https://github.com/Yukihide-Mitsuoka/ai-dev-foundation/issues/211); add the
Japanese operator guide outside default AI routes; update the language allowlist and
inheritance index; and record pilot evidence before closing the implementation issue.
