# Source

This skill adapts `skills/council` from
[`t3dotgg/tstack`](https://github.com/t3dotgg/tstack) at commit
`11e37a74d0a6868c121cd0910ab2b3bd9873b92a`.

It keeps upstream's core: one strong model per lab, read-only members, no
substitution for an unavailable member, no edits while members review the
checkout, scores per round, the pull-request score table, and the guard
against scope creep.

It changes the following:

- Makes the skill manual-only and limits it to change reviews and plan or
  design critique; upstream triggers on the word "council" for any request.
- Removes the T3 Code tools (`orchestrator_capabilities`, `delegate_task`) and
  resolves members from the client's model list, so the catalog names no fixed
  model identifiers.
- States that invoking the skill authorizes setting a model per subagent call,
  and stops on clients that cannot do that.
- Continues with the remaining members while they cover at least two labs;
  upstream stops when it cannot reach three providers.
- Adds a member output contract: severity tiers and finding fields for
  changes, a recommendation and readiness score for plans, and a report with
  an agreement map. Upstream asks for a score on code reviews only.
- Replaces upstream's summary with a verification and verdict step adapted
  from this catalog's `code-review` skill, inlined because that skill is
  manual-only and cannot be loaded from here.
- Replaces "continue until all delegates are satisfied" with an ordered loop:
  stop when no verified finding needs action, after three rounds, or when the
  mean score stops rising. Plans and designs get one round.
- Removes the non-blocking delegate option and the T3 Code rule placing the
  score table before the model and harness line.

Licensed under the MIT terms in `LICENSE.upstream`.
