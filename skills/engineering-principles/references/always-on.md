# Engineering Rules

At the start of a code modification, select the relevant rules and apply them
throughout the work:

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
- Use the narrowest executable check that exercises changed behavior. Inspect
  the resulting artifact for prose or non-executable metadata. Avoid unrelated
  suites and duplicate generic final checks; report remaining uncertainty.
