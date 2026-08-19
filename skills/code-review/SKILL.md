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

State the intended outcome in one paragraph. Ask only when neither the request,
diff, commits, nor linked context establishes intent.

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
dispatch one independent read-only reviewer per relevant category in parallel
when the client supports it. Otherwise perform separate sequential passes with
fresh attention. Give each reviewer the same scope, intent, diff, repository
rules, and rubric.

Reviewer prompts must state the objective, boundaries, edit prohibition,
expected structured output, and validation allowed. Reviewers may inspect
surrounding code and run read-only checks. They must return findings with
severity, location, reachable impact, evidence, and a minimal fix direction.
Use **high** for release-blocking or materially unsafe behavior, **medium** for
reachable defects or significant missing requirements, and **low** for bounded
risks or maintainability problems with concrete impact.

## 3. Verify Findings

After every reviewer returns:

1. Merge duplicate findings and record which independent passes raised them.
2. Trace high-impact correctness and security claims through actual callers,
   boundaries, and runtime paths.
3. Reject hypothetical states prevented by validation or types.
4. Reject preference-only rewrites without concrete impact.
5. Check repository conventions and known constraints before judging a pattern.
6. Treat agreement as a signal, never proof.

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

1. Findings first, ordered by severity, with `file:line` references.
2. Open questions or assumptions.
3. Testing gaps and residual risks.
4. Brief change summary only after findings.
5. A compact agreement map showing corroborated and disputed findings when
   multiple passes ran.

If there are no actionable findings, say so explicitly and still state residual
test risk or unverified assumptions. The review is complete when every relevant
lens has a recorded result and every reported finding has been verified against
the repository context.
