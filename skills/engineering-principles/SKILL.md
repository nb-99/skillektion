---
name: engineering-principles
description: Apply a compact set of engineering principles to substantial design, migration, operations, concurrency, and maintenance decisions. Use when modifying code or when a task needs a named decision rule beyond ordinary implementation guidance.
---

# Engineering Principles

This is a conditional index, not a checklist to force onto every change. Select
only principles whose trigger matches the current decision. State the principle
only when it materially changes the work.

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

### Prove It Works

Use before declaring completion. Check the real artifact or runtime behavior,
not only compilation, a proxy, a summary, or a worker's self-report. State what
was verified and what remains uncertain.

## Completion

The principle pass is complete when each selected principle names the concrete
decision it changed and no unselected principle is added merely for ceremony.
