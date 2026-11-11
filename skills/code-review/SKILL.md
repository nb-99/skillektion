---
name: code-review
description: Review implemented changes for completeness, correctness, simplification, security, quality, tests, performance, and documentation. Use for branch, pull-request, staged, or worktree reviews after a fixed comparison point is known.
disable-model-invocation: true
---

# Code Review

Run independent adversarial reviews, then apply pragmatic lead judgment. Report
findings before summary. Review only; do not change code unless the user asks in
a separate step.

Read [rubric.md](references/rubric.md) before dispatching reviewers and
[lead-judgment.md](references/lead-judgment.md) before synthesis.

## 1. Establish Scope And Intent

Determine the fixed comparison point: commit, merge base, branch, pull request,
staged changes, or explicit files. Read the diff, commits, repository
instructions, relevant surrounding code, and the originating specification or
issue when available.

State the intended outcome by restating it in your own words — use the
`in-your-own-words` skill when available. Derive the intent from the request,
diff, commits, and linked context. Ask only when none of them establishes it.

## 2. Select Review Lenses

Use every relevant lens:

- completeness;
- correctness;
- simplification and architecture;
- security;
- code and configuration quality;
- tests and verification;
- performance;
- documentation.

Skip an irrelevant lens only with a short reason. For substantial changes,
dispatch one independent reviewer per relevant category in parallel when the
client supports it. Otherwise perform separate sequential passes with fresh
attention. Give each reviewer the same scope, intent, diff, repository rules,
and rubric.

Reviewer prompts must state the objective, boundaries, edit prohibition,
expected structured output, and validation allowed. Reviewers may inspect
surrounding code and run checks that do not mutate the repository or external
systems. Apply the run-proven standard: a finding survives only when a run
backs it. Each reviewer proves findings with a failing test, a repro script,
or command output that shows the wrong behavior, and reports the exact command
and its output alongside the output the intent requires. Findings without a
run — style, naming, structure, and risks that need a future change to matter —
are reported only as lead-judgment observations, never as verified findings.
No findings is a valid result. Reviewers must return findings with severity,
location, reachable impact, evidence, the proving command and its output, and
a minimal fix direction. Use **high** for release-blocking or materially
unsafe behavior, **medium** for reachable defects or significant missing
requirements, and **low** for bounded risks or maintainability problems with
concrete impact.

## 3. Verify Findings

After every reviewer returns:

1. Merge duplicate findings and record which independent passes raised them.
2. Rerun each finding's proving command, or the cheapest equivalent that does
   not mutate the repository or external systems. Keep a finding only when the
   output shows the failure and the failure breaks the stated intent; drop the
   rest and record the count and reason per reviewer. Merge findings that
   share a root cause.
3. For findings that cannot carry a run, trace high-impact correctness and
   security claims through actual callers, boundaries, and runtime paths
   before promoting them above observation status.
4. Reject hypothetical states prevented by validation or types.
5. Reject preference-only rewrites without concrete impact.
6. Check repository conventions and known constraints before judging a pattern.
7. Treat agreement as a signal, never proof.

## 4. Lead Verdict

Classify verified findings:

- **Act on:** concrete defect or material missing requirement.
- **Consider:** real concern whose priority or trade-off is uncertain.
- **Noted:** valid low-priority observation or residual risk.
- **Dismissed:** incorrect, unreachable, duplicate, missing context, or mere
  preference. Give the reason so the user can override the judgment.

Keep **Act on** focused. If it contains many items, check whether findings are
symptoms of one root cause or whether low-value issues escaped filtering.

## Output

1. Findings first, ordered by severity, with `file:line` references, the
   proving command, and its output.
2. Lead observations: findings without a run, stated as judgment calls.
3. Dropped findings, with the count and reason per reviewer pass.
4. Open questions or assumptions.
5. Testing gaps and residual risks.
6. Brief change summary only after findings.
7. A compact agreement map showing corroborated and disputed findings when
   multiple passes ran.

If there are no actionable findings, say so explicitly and still state residual
test risk or unverified assumptions. The review is complete when every relevant
lens has a recorded result and every reported finding has been verified against
the repository context.
