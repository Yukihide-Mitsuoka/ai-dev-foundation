---
id: docs-templates-index
title: Document Templates
---

# docs/foundation/templates/ — Document Templates

Reusable skeletons for standard project documents. Copy a template out of this directory,
fill it, and delete the guidance comments. Each template names the skill that drives it.

| Template | Produces | Driven by |
|----------|----------|-----------|
| [requirements.md](requirements.md) | A requirements definition document | [.skills/requirements.skill.md](../../../.skills/requirements.skill.md) |

Templates follow the documentation rules ([.ai/documentation.md](../../../.ai/documentation.md)),
especially the writing style in DOC-002. After template instantiation, AI agents translate
the copied structure and write project-specific documents in Japanese. The
foundation-owned template files remain English (ADR-0005).

**Update trigger:** add a row here whenever a new template lands in this directory.
