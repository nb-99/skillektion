# Review Rubric

Apply only the lenses relevant to the change.

## Completeness

- Does the change implement the requested behavior end to end?
- Are callers, migrations, configuration, errors, docs, and cleanup included?
- Does anything remain in a half-migrated or contradictory state?

## Correctness

- Trace happy and failure paths, boundary values, retries, concurrency, and
  partial prior runs.
- Show the reachable execution path for a claimed bug.
- Distinguish a root-cause fix from a guard that only hides the symptom.

## Simplification And Architecture

- Does responsibility sit at the correct boundary and abstraction level?
- Do data structures match domain and access patterns?
- Can indirection, configuration, or compatibility scaffolding be removed?
- Do not penalize simple code for lacking an abstraction.

## Security

- Trace untrusted inputs to sensitive sinks.
- Check authentication, authorization, secret exposure, unsafe shell/SQL/HTML,
  path handling, and time-of-check/time-of-use risks.
- Report only reachable security issues, not generic possibilities.

## Quality

- Follow repository conventions and instructions.
- Flag unclear names, hidden state, duplicated policy, stale comments, and
  lengthy comments that structure or naming could replace.
- Prefer the smallest correct fix over speculative extensibility.

## Tests And Verification

- Do tests cover behavior rather than implementation details?
- Does a bug fix reproduce the defect before proving the fix?
- Are integration boundaries and failure paths exercised?
- Treat weakened assertions, removed coverage, hard-coded behavior, or
  production changes justified only by tests as test gaming, not evidence of
  correctness.
- Verify actual artifacts instead of trusting summaries or proxy signals.

## Performance

- Identify changed hot paths, algorithmic growth, repeated I/O, excessive
  allocations, fan-out, and unbounded work.
- Require measurement or a traceable cost model for performance findings.

## Documentation

- Do instructions, examples, schemas, migration notes, and operational docs
  match the implemented behavior?
- Remove stale or redundant prose and preserve rationale the code cannot express.
