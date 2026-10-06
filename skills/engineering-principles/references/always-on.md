# Engineering Rules

At the start of a code modification or test review, select the relevant rules
and apply them throughout the work:

- Minimize reader load: prefer direct code, small mutable scope, and answers
  close to the question they resolve.
- Validate external data once at the boundary and represent valid state
  explicitly inside it.
- Make retryable operations idempotent and design partial runs to converge.
- Remove unnecessary shared mutable state before adding synchronization.
- Sequence work into verifiable units that each leave an observable valid state.
- When compatibility is not required, migrate callers and remove the legacy path
  in the same delivery wave.
- When a requirement exposes a design mismatch, compare the incremental change
  with the design you would choose if the requirement had existed from day one.
- Build reusable automation only when repetition, scale, or auditability repays
  its maintenance cost.
- Encode recurring lessons in types, tests, validation, automation, or focused
  instructions instead of relying on reminders.
- When writing, changing, or reviewing tests, assert observable behavior or
  explicit contracts against specified behavior or reviewed reference outputs,
  not expectations computed by calling or reimplementing the code under test.
  For mocks, check meaningful payloads or effects; assert call counts when the
  count itself is the contract. Keep legitimate tests, including negative,
  property-based, compile-time, contract, reviewed snapshot, and characterization
  tests.
- Only while conducting performance tests or benchmarks already in scope,
  validate that the intended work ran successfully; rule out errors, cached or
  skipped work, unequal settings, and noise. Record workload, settings, run count,
  and spread; support bottleneck claims with measured profiles or counters.
  This rule does not initiate benchmarks for ordinary implementation, design
  ideas, or suspected performance effects.
- Use the narrowest executable check that exercises changed behavior. Inspect
  the resulting artifact for prose or non-executable metadata. Avoid unrelated
  suites and duplicate generic final checks; report remaining uncertainty.
