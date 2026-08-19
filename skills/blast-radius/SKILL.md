---
name: blast-radius
description: Analyze what a change could break beyond its diff and prove the central safety invariant with executable evidence. Use for impact analysis, risky small diffs, schema or API changes, and "what could this break?" questions.
disable-model-invocation: true
---

# Blast Radius

Find the breakage that a symbol search misses. The output is useful only when
the fact that makes the change safe is proven or explicitly marked unproven.

## Confidence Ladder

For every safety-critical claim, record the strongest evidence reached:

1. Assertion only.
2. Direct source citation.
3. Traced execution path showing the bad case cannot occur.
4. Executed script or test against the real code.
5. Reproduction in the running system.

Reach level 4 when it is reasonably cheap. Do not present lower-confidence
claims as settled facts.

## Process

1. Read the diff, changed symbols, callers, tests, and the behavior that changed.
2. State the one or two invariants on which the change's safety depends.
3. Inspect runtime boundaries a local search can miss: pinned dependencies,
   serialized data, databases, APIs, feature flags, other languages, lifecycle
   ordering, concurrency, and downstream consumers.
4. Inspect relevant commit, pull-request, issue, and design history when
   available. Distinguish historical evidence from inference.
5. Trace each plausible failure from input to effect. Separate reachable risks
   from hypothetical ones.
6. Prove the central invariant with the cheapest existing focused test, script,
   or running-system reproduction. Add a new check only when existing checks
   cannot exercise the real path.
   Keep temporary proof artifacts outside the repository, leave them
   uncommitted, and use disposable or non-production state for reproductions.
7. For a genuinely broad change, use independent read-only review passes when
   available and verify their high-impact findings against the code.

## Output

- **Change:** behavior changed, including non-obvious effects.
- **Safety invariant:** the decisive fact, confidence level, and evidence.
- **Confirmed risks:** failure path, location, likelihood, impact, and check.
- **Cleared risks:** what was investigated and why it is safe.
- **Before merge:** the cheapest regression check that exercises the real path.
- **Gaps:** unavailable evidence and every claim left unproven.

The analysis is complete when every material risk is confirmed, cleared, or
named as an evidence gap, and the central safety invariant is proven or marked
unproven.
