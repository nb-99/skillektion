---
name: council
description: Review a change or critique a plan with strong models from several labs, verify their findings, fix the accepted ones, and repeat the review.
disable-model-invocation: true
---

# Council

Send one task to several **members**, strong models from different labs, in
parallel. Models from different labs fail differently, so each member adds an
independent view. Members work read-only. You are the host: you verify their
output, decide what holds, and make the fixes.

## 1. Prepare

- Address open pull-request comments, fix known issues, and run the relevant
  checks first, so members review the current state. Skip fixes to code the
  user plans to replace.
- Pin the subject. For a change, determine the comparison point: commit,
  merge base, branch, pull request, staged changes, or explicit files. For a
  plan or design, name the document or the decision and its constraints.
- Restate the intent in your own words: the user's goal and the problem it
  solves. Ask only when the request, diff, commits, and linked context leave
  it open.

## 2. Choose members

Use the members the user names. Otherwise choose three members from three
different labs: each lab's newest flagship model, not a higher-priced variant
of it such as a Pro or Max edition, for example Claude Opus, GPT Sol, and
Gemini. Resolve the exact model identifiers from the client's model list. Use
high reasoning effort when the client lets you set it.

Invoking this skill is the user's request to run these models, so set the
model explicitly on every member's subagent call.

A member is missing when its model is unavailable or when it fails or times
out during a round. Record every missing member and never substitute another
model, in this round or later ones. Continue with the remaining members while
they cover at least two labs; otherwise stop and tell the user. Stop as well
when the client cannot set a model per subagent call.

State the roster with exact identifiers before the first round.

## 3. Run a round

Start every member in the same turn. Use a read-only review agent for a change
and a read-only advisory agent for a plan when the client has them; otherwise
instruct a general agent that it must not edit files. If the review agent
expects one lane or category, assign all of them. Give every member the same
intent, subject, repository rules, and the checks already run, and tell it
that no findings is a valid result.

For a change, ask each member for a full review across completeness,
correctness, design and simplification, security, tests, performance, and
documentation. Each finding states:

- severity: **high** for release-blocking or materially unsafe behavior,
  **medium** for a reachable defect or significant missing requirement,
  **low** for a bounded risk with concrete impact;
- the `file:line` location and the reachable impact;
- evidence, preferably the command or test that shows the failure, with its
  output;
- a minimal fix direction.

Also ask for a score out of 10 for whether the change is ready to merge.

For a plan or design, ask each member for one recommendation, the main risks,
the assumptions, the evidence that would change the answer, and a score out of
10 for readiness.

Keep the checkout unchanged while any member of the round is running. Check
each report against the code as it arrives, and merge across reports once
every member has returned.

## 4. Judge

Filter member output; never concatenate it.

1. Merge duplicate findings and record which members raised each one.
2. Rerun each proving command, or the cheapest equivalent that does not mutate
   the repository or external systems. Trace findings without a run through
   actual callers, inputs, and boundaries before accepting them.
3. Classify every finding:
   - **Act on:** a concrete defect or a material missing requirement.
   - **Consider:** a real concern whose priority or trade-off is uncertain.
   - **Noted:** a valid low-priority observation or residual risk.
   - **Dismissed:** incorrect, unreachable, missing repository context, or
     preference only. Give the reason so the user can override it.
4. Treat agreement between members as a signal for priority, never as proof.
   Scrutinize a correctness or security finding even when one member alone
   raises it.

For a plan or design, compare the recommendations, and judge each risk and
assumption against the codebase and constraints with the same four verdicts.

## 5. Loop

A plan or design gets one round; revise and rerun only when the user asks.

For a change, after judging each round:

1. If no verified **Act on** finding remains, stop.
2. Fix the **Act on** findings and rerun the checks. Keep fixes on the original
   intent; record suggestions beyond it as follow-ups instead of implementing
   them.
3. Stop if three rounds have run, or, from round 2 on, if the mean score of
   the members that scored both this round and the previous one did not rise.
   Report the last fixes as not reviewed by the council, and ask the user
   before running another round.
4. Otherwise start the next round with every remaining member.

## Report

1. Findings by verdict and severity, with location and evidence, then the
   dismissed findings with reasons.
2. An agreement map: which members raised each finding, and where they
   disagreed.
3. The fixes made in each round, marking any that no round reviewed.
4. The score table, labeling members by model name. Write `no score` when a
   member gave none, and `missing` for a member that failed or was
   unavailable.
5. Follow-ups, open questions, and residual risk.

```markdown
## Council review

Rounds: 2

| Member | Round 1 | Round 2 |
| --- | --- | --- |
| Claude Opus | 7/10 | 9/10 |
| GPT Sol | 8/10 | 10/10 |
| Gemini | 7/10 | 9/10 |
```

When the task creates or updates a pull request, put the score table in its
description, not in a comment. Otherwise put it in the final reply only.
