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
on ownership ambiguity, produce one reviewable initialization PR, and join the current
inheritance model after that PR merges. It must not add routine AI context. The repository
owner also requires the operator guide to be written in Japanese as a narrowly named
human-facing exception to ADR-0008.

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

### Option 4: Add a one-time adoption operation to the inheritance reconciler

Add a distinct `adopt-child` operation to `template_inheritance.py`. It uses the direct
parent's existing export and exact commit, reports every ownership or content conflict
before writing, and initializes the same child contract as `bootstrap-child`. After the
initialization PR, it has no continuing role; reviewed Template Sync remains the sole
scheduled transport.

## Decision

Adopt Option 4.

`adopt-child` MUST be a one-time, local, idempotent operation distinct from strict
template-copy bootstrap. Its default mode MUST be read-only. The plan MUST require a
clean non-default child branch, credential-free GitHub origins for the child and direct
parent, an exact full parent commit, and the parent's validated inheritance export.

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

Apply MUST require the exact repository and source commit to be repeated. It MAY write
only missing parent-owned files from the exact commit, validated inheritance metadata,
and explicitly reviewed initialization payloads. It MUST preserve existing protected
content and MUST NOT overwrite a non-identical file, delete a path, follow a symlink,
fetch, alter history or remotes, commit, push, create or merge a PR, call GitHub, enable
Template Sync, or apply repository governance. A repeated apply with the same accepted
state MUST make no change.

The initialization result MUST use the existing manifest, lock, agent-profile,
README-archive, project-overlay, Template Sync exclusion, and direct-parent contracts.
It MUST pass the normal inheritance validator and repository checks in one reviewed PR.
After merge, operators separately apply GitHub governance and opt into Template Sync;
all later parent changes use the existing direct-parent reviewed propagation path.

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
- The first reviewed PR establishes the same contract as template-created children.
- Adoption adds no second continuing transport or recurring approval path.
- The Japanese procedure is available for the operator without increasing routine AI
  context.

**Negative:**

- Adoption is more work than template initialization because every pre-existing
  ownership conflict needs a human decision.
- The inheritance reconciler gains another bounded command and additional fixtures.
- Large existing repositories can produce an adoption PR that needs reviewed slices
  before the final metadata and lock are accepted.
- The third Japanese guide must be maintained against its English authorities.

Migration is expand-only: add failing-first planner and apply tests, implement read-only
classification, add confirmed idempotent writes, then publish the Japanese guide and
allowlist update. Prove one non-production existing repository before recommending the
path generally. Rollback removes the unaccepted adoption branch; after an adoption PR is
merged, rollback is a normal reviewed child PR and lock change, not a history rewrite.

**Follow-ups:** implement `adopt-child` and bounded fixtures in
[Issue #211](https://github.com/Yukihide-Mitsuoka/ai-dev-foundation/issues/211); add the
Japanese operator guide outside default AI routes; update the language allowlist and
inheritance index; and record pilot evidence before closing the implementation issue.
