---
name: architecture-review
description: Assess the architecture of a codebase or subsystem and find the structural problems worth fixing - shallow modules, hidden coupling, scattered validation, data models that fight their use, and complexity in the wrong places. Use when the user asks whether a design is sound, where it will hurt as it evolves, or which refactors would pay off.
---

# Architecture Review

Judge how a subsystem is built for what it does and for the changes it actually
receives. This is assessment, not line review and not an implementation plan.
Read only; change nothing.

Use the `codebase-design` vocabulary: **module**, **interface**, **depth**,
**seam**, **adapter**. A module is **deep** when a small interface hides a lot
of behaviour, **shallow** when the interface is nearly as complex as the
implementation.

## 1. Scope by change pressure

Restructuring pays off where code keeps changing. If the user named a target,
review that. Otherwise find the **hotspots**:

- `git log --since="12 months ago" --name-only --format= | sort | uniq -c |
  sort -rn` shows churn per file; aggregate by directory for module churn.
- Files from different modules that change together in the same commits show
  **co-change coupling**: a dependency the import graph may not show. Check
  the top pairs.

Read `GLOSSARY.md`, ADRs (`docs/adr/`), and design notes in the area first. A
documented decision is an intentional trade-off; reopen it only when the
review shows concrete friction the decision did not anticipate.

## 2. Build the model

Trace one or two real flows from trigger to effect through the actual code:
entry points, data model, module interfaces, and where data enters and leaves.
Write a short explanation of how it works before judging anything. For a large
subsystem, explore independent slices in parallel read-only passes when
available.

## 3. Examine

Apply each lens that fits; record "no issue" for lenses checked and clean.

- **Depth:** apply the **deletion test** to suspected pass-through modules:
  delete it mentally; if complexity vanishes it was shallow, if it reappears
  across callers it earns its keep. Flag concepts that require bouncing
  between many small modules to understand.
- **Seams:** one adapter is a hypothetical seam, two adapters make a real one.
  Flag interfaces with a single implementation that exist "in case", and
  missing seams where tests must reach past the interface.
- **Coupling:** follow co-change pairs and cross-module imports. Flag modules
  that know each other's internals or must change in lockstep.
- **Data model:** flag code that constantly reshapes data between layers, and
  types that claim more structure than exists at runtime.
- **Edges:** validation belongs where external data enters, once. Flag checks
  scattered through internal code, and errors that lose context while
  propagating.
- **Evolution:** name the most probable next change, from history, issues, or
  the user. Count the modules it would touch. Do not score hypothetical
  changes.
- **Complexity budget:** is complexity spent on core logic and real
  invariants, or on boilerplate, indirection, and configuration?
- **Consistency:** similar problems should get similar solutions; flag
  unexplained divergence only.

## 4. Evidence rule

Every finding cites a concrete dependency chain, code path, or co-change
history with file references. A claim that something "could use more
abstraction" without showing what the abstraction would remove is not a
finding. Over-abstraction is as much a defect as under-abstraction; a flat
design is right for a simple domain. A sound architecture with no findings is
a valid result: say so.

Severity: **Structural** (wrong seam, broken data model, coupling that blocks
likely work), **Concern** (harder to reason about or change, not broken), or
**Observation** (a trade-off that may age badly, without demonstrated cost).

## 5. Verdict

Verify each finding against the code, then classify it:

- **Act on:** concrete structural problem worth fixing now.
- **Consider:** real concern whose cost or priority is uncertain.
- **Noted:** valid, low-priority observation.
- **Dismissed:** wrong, missing context, documented trade-off, or preference.
  Give the reason so the user can override it.

For each **Act on** finding, describe the target shape in plain words: which
behaviour moves behind which interface, what callers stop knowing, and which
tests get simpler. Add a small before/after sketch only when it explains
faster than prose. Do not design the full interface.

## Output

1. How it works: the short explanation from step 2. A reader who only wants
   to understand the system can stop here.
2. Scope: the target, and the hotspots and co-change pairs that drove it.
3. Findings by verdict, with severity, evidence, and target shape.
4. Lenses checked without findings, and gaps in the evidence.

The review is complete when every applicable lens has a recorded result and
every finding is verified and classified, or dismissed with a reason.
