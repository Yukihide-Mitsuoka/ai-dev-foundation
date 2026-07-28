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
| Baseline | `AGENTS.md`, `CLAUDE.md`, `.ai/README.md`, `.ai/guardrails.md` | Active handoff and runtime-owned instructions |
| Declared task route | Baseline, selected skill, every file in its `reads` declaration | Task-specific sources found through bounded discovery |

Discovered sources are excluded from the ceiling because quality requires reading every
relevant source. A budget cannot justify omitting one.

## Recorded change

| State | Baseline bytes | Baseline words |
|-------|---------------:|---------------:|
| Before ADR-0012 route implementation | 18,565 | 2,625 |
| After PR #88 | 17,561 | 2,472 |

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
their protected entry documents can legitimately differ.

The largest route on 2026-07-29 is `requirements`: approximately 44,231 bytes and 6,245
words. A PR that intentionally increases a ceiling states the reason and confirms that
no narrower route preserves completeness.

**Update trigger:** update this guide and the budget constants together whenever the
baseline file set, mandatory skill routes, measurement method, or ceiling changes.
