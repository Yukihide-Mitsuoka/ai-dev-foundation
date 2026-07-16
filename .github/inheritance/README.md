---
id: template-inheritance-contract
title: Template Inheritance Contract
---

# Template Inheritance Contract

This directory defines the child-owned, direct-parent contract from [ADR-0004](../../docs/adr/0004-harden-multi-level-template-inheritance.md).
Validation is offline and read-only; history planning and materialization are follow-ups.

## Schema version 1

`.github/inheritance/manifest.json` declares intent:

```json
{
  "schema_version": 1,
  "parent": {"repository": "acme/parent-template", "branch": "main"},
  "lock_file": ".github/inheritance/lock.json",
  "inherited_paths": [".ai/", "scripts/template_inheritance.py"],
  "protected_paths": [".gitignore", ".github/governance/repository.json", ".github/inheritance/lock.json", ".github/inheritance/manifest.json", ".github/workflows/template-sync.yml", ".templatesyncignore"]
}
```

The lock records the exact accepted parent commit:

```json
{"schema_version": 1, "parent": {"repository": "acme/parent-template", "commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}}
```

An ownership root is either a literal file or a directory prefix ending in `/`. Globs,
absolute paths, traversal, `.git`, duplicates, and overlap within or across ownership
classes are invalid. Protected roots must cover the manifest, selected lock file,
`.gitignore`, `.templatesyncignore`, local governance policy, and sync workflow.

## Validate

```bash
python3 scripts/template_inheritance.py validate --root .
```

Exit `0` prints deterministic JSON; exit `2` reports invalid input on stderr. The command
performs no network request, file write, deletion, Git operation, or GitHub API call.
