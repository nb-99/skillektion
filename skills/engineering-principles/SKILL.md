---
name: engineering-principles
description: Apply conditional engineering principles to code changes, test writing or review, performance testing already in scope, and substantial design, migration, operations, concurrency, or maintenance decisions.
---

# Engineering Principles

This is a conditional index, not a checklist to force onto every change. Select
only principles whose trigger matches the current decision. State the principle
only when it materially changes the work.

Read [always-on.md](references/always-on.md) to select the concise rules relevant
to a code modification. The sections below provide their decision triggers and
additional context.

## Principles

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
