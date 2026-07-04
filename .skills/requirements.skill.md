---
name: requirements
description: Produce a requirements definition document — purpose-driven, zero-based, objective, complete
triggers: [requirements definition, 要件定義, spec a feature, write requirements, scope a project]
reads: [.ai/mission.md, .ai/documentation.md, docs/templates/requirements.md]
---

# Skill: Requirements Definition

## Purpose
Produce a requirements definition document that states what must be built and why —
derived from the goal rather than from existing artifacts, objective, and complete enough
that design and acceptance testing proceed without re-asking.

## Inputs
- The goal: the problem to solve and who has it, from a human or an issue. If it is absent
  or ambiguous enough that two reasonable implementations would diverge, clarify first
  (CLAUDE.md §13) — do not fill the gap with an assumption.
- The success definition: how the requester will judge the result as met.
- The template: [docs/templates/requirements.md](../docs/templates/requirements.md) —
  structure and required sections.
- Scope boundaries: [.ai/mission.md](../.ai/mission.md). Read other existing docs and code
  only in Process step 4, not before.

## Process
1. **Fix the purpose.** Write the objective in one sentence and the success metrics
   (measurable) before anything else. Every requirement downstream traces back to these.
2. **Derive requirements zero-based.** From the purpose alone, enumerate the requirements
   it demands. Do not consult existing documents, code, or prior solutions in this step —
   they anchor thinking to what already exists (bias). Capture the ideal set first.
3. **Trace each requirement to a purpose or success metric.** A requirement that traces to
   none is a deletion candidate, not a given.
4. **Reconcile with reality.** Now read existing assets, constraints, and platform limits;
   filter and adjust the zero-based set. Record where a constraint forces a deviation and
   why.
5. **Assign IDs and priority.** Stable IDs (FR-00x functional, NFR-00x non-functional) and
   a MoSCoW priority with a one-line basis per requirement.
6. **Fill the template top to bottom.** Define terms, assumptions, and constraints once in
   their sections; reference them by name afterward (DOC-002). Do not restate a definition.
7. **Complete the non-functional set** against the ISO/IEC 25010 characteristics that
   apply, and give each NFR a measurement method — a target with no way to verify it is
   not a requirement.
8. **Estimate infrastructure cost with assumptions stated** (region, unit prices and their
   date/source, assumed traffic/volume): fixed + usage-based, plus the increment when
   scaled. A number without its assumptions is not usable.
9. **Separate decided from undecided.** Move open items to the Open questions section; do
   not blend decided requirements with unresolved ones.
10. **Self-review** against the checklist below and `.ai/review-checklist.md`; open a
    `docs:` PR (or fold into the initiating feature PR).

## Decision criteria
- **Functional vs non-functional?** A behavior the system performs → FR. A property of how
  it performs (speed, availability, security, usability, observability) → NFR.
- **In or out of scope?** If it does not trace to the purpose, default it to non-scope and
  state it there explicitly. The non-scope list prevents the most rework.
- **Priority (MoSCoW).** Must = the purpose fails without it. Should / Could = ranked by
  contribution to a success metric. Won't = recorded and deferred, not dropped silently.
- **Requirement or design?** State what must hold and why, not how to build it. A
  requirement that names a specific technology needs a recorded reason; otherwise move the
  solution detail to design.
- **Escalate** on the CLAUDE.md §13 triggers (authentication, payments, PII schema, data
  deletion, production config) before finalizing requirements that touch them.

## Outputs
- A completed document from the template at `docs/requirements.md` (whole project) or
  `docs/requirements/<initiative>.md` (one initiative).
- Every FR/NFR carries a unique ID, a priority, and a traced purpose.
- Open questions listed separately; any §13 escalations raised.

## Checklist
- [ ] Purpose (one sentence) and measurable success metrics stated first
- [ ] Every FR/NFR has a unique ID and traces to a purpose or success metric
- [ ] Non-scope stated explicitly; each item a deliberate exclusion
- [ ] Every NFR has a measurement method (no unverifiable targets)
- [ ] Non-functional coverage checked against ISO/IEC 25010 characteristics
- [ ] Infrastructure cost estimate present, with its assumptions stated
- [ ] Terms, assumptions, and constraints defined once, referenced thereafter (DOC-002)
- [ ] Decided vs open separated; open items in the Open questions section
- [ ] Prose objective and conclusion-first; no metaphor or hedging (DOC-002)
