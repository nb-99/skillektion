---
name: engineering-principles
description: Use whenever writing, changing, refactoring, or reviewing code, tests, scripts, or build configuration, before the first edit. Conditional engineering principles for minimal changes, boundaries, idempotency, concurrency, migrations, debugging repeated failures, testing, measurement, and verification.
---

# Engineering Principles

This is a conditional index, not a checklist to force onto every change. At
the start of the work, select only principles whose trigger matches the
current task, and apply them throughout. Keep It Minimal applies to every
change. State a principle only when it materially changes the work.

## Principles

### Keep It Minimal

Use for every change.

- Make the smallest change that solves the stated problem. Leave unrelated
  code alone, and mention other fixes separately.
- Build for observed use. Add options, layers, guards, or validators only when
  the requirement asks for them.
- Remove dead code and redundant paths before adding new ones.
- Add a dependency only when it removes more complexity than it brings.
- Optimize only when a measurement shows the need.
- Keep each decision in one place.

### Minimize Reader Load

Use when code accumulates wrappers, indirection, hidden state, or scattered
answers. Reduce the layers between a maintainer's question and the code that
answers it. Keep mutable scope and required context small.

### Boundary Discipline

Use when external data enters the system. Parse and validate once at the
boundary, represent the valid state explicitly, then keep internal logic direct
and testable.

### Make Operations Idempotent

Use for retries, provisioning, migrations, commands, agents, and lifecycle
work. Design repeated and partially completed runs to converge on the same end
state. Detect current state before mutating it.

### Separate Before Serializing Shared State

Use when concurrent workers write the same files, branches, records, or caches.
First remove unnecessary sharing through ownership or partitioning. Serialize
only the shared writes that remain a real invariant.

### Sequence Verifiable Units

Use for migrations and multi-step delivery. Split work into units that each end
in an observable valid state, order blockers first, and verify each unit before
starting the next.

### Migrate Callers, Then Delete Legacy APIs

Use when replacing an internal API with no persisted-data or external-consumer
compatibility requirement. Migrate callers and remove the old path in the same
delivery wave. When compatibility is real, make its owner and removal condition
explicit instead.

### Redesign From First Principles

Use when a new requirement exposes a mismatch in the existing design. Ask what
the structure would be if the requirement had existed from day one, then compare
that design with an incremental change before choosing.

### Attack The Premise

Use when two or more fixes that share one premise have failed the same gate.
Write the premise down — the one sentence every failed fix assumed — and test it
directly before writing another fix that assumes it. Choose an observation that
would come out differently if the premise were false, and look at how the
failures are distributed, not only at how large they are. Follow the evidence:
if it contradicts the premise, the cause is elsewhere.

### Build The Lever

Use when repeatability, scale, or auditability justifies a reusable script,
codemod, generator, test harness, or delegate contract. Build it only when its
future value exceeds its maintenance cost and it is cheaper than direct work.

### Encode Lessons In Structure

Use when the same correction or failure recurs. Prefer an enforceable type,
test, lint, validation rule, script, repository instruction, or focused skill
over another reminder. Route historical rationale to the project's established
documentation or memory system.

### Test Behavior, Not Implementation

Use when writing, changing, or reviewing tests. Exercise the interface callers
use and assert observable results, errors, state changes, or side effects.
Choose expectations from specified behavior, reviewed reference outputs, or
explicit contracts, rather than computing them by calling or reimplementing
the code under test. Prefer assertions that fail for a relevant defect over
checks of private calls or duplicated internals.

For mocked dependencies, check meaningful payloads or resulting effects. Assert
call counts when the count itself is the contract, such as a retry limit or
at-most-once delivery. Keep legitimate tests, including negative, property-based,
compile-time, contract, reviewed snapshot, and characterization tests, when they
protect behavior or an explicit contract.

### Validate Performance Measurements

Use only while conducting performance tests or benchmarks already in scope.
This principle validates those measurements; it does not initiate benchmarking
for ordinary implementation, design ideas, or suspected performance effects.

Confirm the intended work ran successfully. Rule out errors, cached or skipped
work, unequal comparison settings, and run-to-run noise. Record the workload,
settings, run count, and spread with the result. Support bottleneck claims with
profiles or system counters from the measured run, not guesses from the code.

### Prove It Works

Use when changed behavior or an invariant is ready to exercise. Run the
narrowest executable check that covers it. For prose or non-executable metadata,
inspect the resulting artifact. Avoid unrelated suites and generic final
rechecking when earlier evidence still applies. State what was verified and
what remains uncertain.

## Completion

Select relevant principles once. The principle pass is complete when each
selected principle names the concrete decision it changed and no unselected
principle is added merely for ceremony.
