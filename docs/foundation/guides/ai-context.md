---
id: ai-context-guide
title: AI Context Acquisition and Budgets
updated: 2026-07-29
---

# AI Context Acquisition and Budgets

This guide records how the foundation measures declared AI context. The binding
acquisition and quality fallback live in
[`.ai/README.md`](../../../.ai/README.md); accepted ADR-0012 records the decision.

## Measurement boundary

Measurements use UTF-8 bytes and whitespace-delimited words because they are stable
across model providers. They are regression proxies, not exact token counts.

| Measurement | Included | Excluded |
|-------------|----------|----------|
| Baseline | `AGENTS.md`, `CLAUDE.md`, `.ai/README.md`, `.ai/guardrails.md` | Active handoff and runtime-owned instructions, including `.claude/README.md` |
| Declared task route | Baseline, selected skill, every file in its `reads` declaration | Task-specific sources found through bounded discovery |

Discovered sources are excluded from the ceiling because quality requires reading every
relevant source. A budget cannot justify omitting one.

## Recorded change

| State | Baseline bytes | Baseline words |
|-------|---------------:|---------------:|
| Before ADR-0012 route implementation | 18,565 | 2,625 |
| After PR #88 | 17,561 | 2,472 |
| After entry-point deduplication | 16,553 | 2,323 |
| After Claude-specific routing | 16,329 | 2,288 |
| After AI inventory unification | 16,156 | 2,258 |

Before ADR-0012, `docs/` contained approximately 17,424 words and the foundation ADR set
plus decision log contained approximately 9,458 words. They are now discovered through
indexes and search instead of declared as directory-wide reads.

## Enforced ceilings

| Metric | Ceiling |
|--------|--------:|
| Baseline bytes | 18,500 |
| Baseline words | 2,600 |
| Any declared task-route bytes | 46,000 |
| Any declared task-route words | 6,500 |

`make doctor` rejects a directory, glob, missing file, traversal path, redundant
baseline read, or missing mandatory authority in any skill route. It enforces the
ceilings in the canonical foundation repository. Descendants always receive structural
validation and measurement output, but budget excess is initially a warning because
their protected entry documents can legitimately differ. Exact canonical baseline
wording is validated only in the foundation; descendants retain their protected local
entry wording. The strict foundation validation also pins the §12 link and all obligations
in `.claude/README.md`, although that conditional runtime file is excluded from baseline
measurement.

At 90% of either ceiling, `make doctor` emits a warning before the hard limit becomes a
failure. It also rejects an incomplete or stale foundation ADR/guide index because
bounded discovery depends on those indexes. A project-owned
`docs/development-handoff.md` remains outside the hard context budget, but receives a
warning when it exceeds 1,500 words, has an invalid or future `updated` date, or has not
been updated for more than 30 days. These handoff findings never justify skipping the
document.

The largest route remains `requirements`. On 2026-07-29, separating its procedural skill
from its standalone output template reduced the route from 44,231 bytes / 6,245 words to
41,298 bytes / 5,776 words. Entry-point deduplication then reduced every route, leaving
`requirements` at 40,290 bytes / 5,627 words. Neither change removed a mandatory source.
Routing Claude-specific details out of the shared baseline then reduced every declared
route; `requirements` became 40,066 bytes / 5,592 words without changing Claude Code
obligations. Combining the duplicate rule-ID and file inventories then reduced the
baseline to 16,156 bytes / 2,258 words and `requirements` to 39,893 bytes / 5,562 words
without removing an inventory entry. A PR that intentionally increases a ceiling states
the reason and confirms that no narrower route preserves completeness.

**Update trigger:** update this guide and the budget constants together whenever the
baseline file set, mandatory skill routes, measurement method, or ceiling changes.
