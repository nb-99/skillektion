---
name: architecture-critique
description: Assess a subsystem's architecture for structural problems - wrong abstraction boundaries, hidden coupling, fragile data models, and complexity in the wrong places. Use when the user asks whether a design or architecture is sound, where it will hurt as it evolves, or to critique a design before building on it.
---

# Architecture Critique

Judge how a subsystem is built for what it needs to do and how it will need to
evolve. This is assessment, not line review and not a rewrite proposal.

## Explain first

Understand before judging. Produce or reuse an explanation of how the
subsystem works — the `how` skill does this — covering the flow, the data
model, and the boundaries. Critics judge from the explanation plus the code.

## Critique passes

Run one or more independent read-only critique passes; use parallel workers
when available, otherwise sequential passes with fresh attention. Give each
pass the same explanation, the relevant file paths, and the rubric below.

Each pass finds architectural problems, not line-level bugs or style issues,
and must support every finding with a concrete dependency chain or code path.
A claim that something "could use more abstraction" without showing what the
abstraction would solve is rejected. Intentional tradeoffs with clear benefits
are not issues. If the architecture is sound, say so — an empty critique is a
valid outcome.

Severity per finding:

- **Structural:** wrong abstraction boundary, broken data model, coupling
  that will block future work.
- **Concern:** real issue that makes the system harder to reason about or
  change, without being fundamentally broken.
- **Observation:** a tradeoff that might not age well, or inconsistency
  without demonstrated cost.

## Rubric

Review through whichever lenses are relevant; not every lens applies to every
subsystem.

- **Abstraction fit:** does each abstraction represent a real concept and
  carry its weight, or is it an indirection layer "in case we need it"? Are
  boundaries where things that change independently separate? Over-abstraction
  is as much a problem as under-abstraction; a flat design is fine when the
  domain is simple.
- **Data model:** do the data structures fit how the data is actually
  accessed? Flag impedance mismatches where code constantly reshapes data, and
  types that claim more structure than exists at runtime.
- **Boundary discipline:** is validation concentrated at entry points, or
  scattered through internal code? Do errors propagate cleanly? Could the
  subsystem be exercised in isolation, or does everything need to run?
- **Evolution readiness:** if the most probable next requirement landed
  tomorrow, how much would change — one file or everything? Flag hardcoded
  assumptions and legacy paths that no one depends on. Do not penalize
  hypothetical changes.
- **Complexity versus value:** is the complexity budget spent on core logic
  and tricky invariants, or on boilerplate, unnecessary indirection, and
  configuration? Does every component earn its existence?
- **Consistency:** do similar problems get similar solutions here and
  elsewhere in the codebase? Unexplained inconsistency is a maintenance
  burden; justified differences are not.

## Lead verdict

Verify each finding against the code, then classify it:

- **Act on:** concrete structural problem worth fixing now.
- **Consider:** real concern whose cost or priority is uncertain.
- **Noted:** valid, low-priority observation.
- **Dismissed:** wrong, missing context, or preference. Give the reason so
  the user can override the judgment.

Present the explanation first and the verdict below it, so a reader who only
wants to understand the system can stop after the explanation.

The critique is complete when every relevant rubric lens has a recorded result
and every finding is verified, classified, or dismissed with a reason.
