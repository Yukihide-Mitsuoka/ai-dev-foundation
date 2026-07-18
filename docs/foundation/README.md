---
id: foundation-docs-index
title: Foundation Documentation
---

# docs/foundation/ — Foundation Documentation

This directory contains descriptive guidance and document templates owned by
`ai-dev-foundation`. In an instantiated repository, project-owned documentation stays at
task-oriented paths directly under `docs/`; it MUST NOT be placed below this directory.

Binding AI rules remain in [`.ai/`](../../.ai/), and task procedures remain in
[`.skills/`](../../.skills/). Files here link to those sources instead of duplicating
their rules.

## Inventory

| Path | Purpose |
|------|---------|
| [requirements.md](requirements.md) | Choose the project-owned requirements location and naming |
| [templates/](templates/) | Copyable skeletons for project-owned documents |

## Template Sync ownership

Template Sync excludes `docs/**` to protect project-owned documentation and selectively
includes `docs/foundation/**`. Existing downstream repositories created before this
namespace was introduced must append this one-time exception block to the end of their
local `.templatesyncignore`:

```gitignore
docs/**
!docs/foundation/
!docs/foundation/**
```

The local `.templatesyncignore` is itself protected from synchronization. Review and
merge this change in each existing downstream repository before manually running the
Template Sync workflow. New repositories created from the updated template already have
the exception.

**Update trigger:** add or update an entry whenever foundation-owned guidance or a
template moves into, within, or out of this namespace.
