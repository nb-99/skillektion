# Source

This skill adapts `skills/full-stop` from
[`t3dotgg/tstack`](https://github.com/t3dotgg/tstack) at commit
`11e37a74d0a6868c121cd0910ab2b3bd9873b92a`, with the workflow, proof rules,
merge gate, and question rules of `skills/full-send` from the same commit
inlined.

It keeps upstream's core: unattended ownership from the current state to a
PR the user only has to merge, never merging, turning off auto-merge and merge
queues, proof observed in the session, the readiness gate, the three handoff
outcomes, staying active while checks run, and asking through the question
tool.

It changes the following:

- Renames the skill to `drive-to-ready`, makes it manual-only, and drops the
  reference to `full-send`; upstream triggers on the phrase "full stop", even
  as closing emphasis.
- Narrows the testing permission to the repository's own tests, checks, and
  run commands, and asks before other test methods; upstream overrides
  ask-first project rules for any method its proof needs.
- Opens a draft and marks it ready at the gate, then watches again for the
  reviews and workflows that marking it ready starts; upstream opens a ready
  PR.
- Requests a Copilot review on GitHub when no automatic review covers the
  draft.
- Defines the readiness gate through the `pr-mr-watch` verdict, adds the rule
  that no review thread may await a reply, and lets a requested re-review
  remain only after every requested change is fixed or answered; upstream
  lets only an approval remain. Renames the outcomes "Waiting for required
  approval" and "Blocked" to "Waiting for review" and "Stuck".
- Drops upstream's permission to ignore automated reviews that ask for human
  review; such a review is a finding to answer like any other.
- Handles an existing PR/MR by turning off automatic merging before the
  first push and keeping its draft state.
- Replaces `sol-loop` with this catalog's `code-review` skill, or `council`
  when the user asks for it, replaces `file-pr` with `creating-a-pr-mr`, and
  replaces `babysit-pr` and its `pr-wait` script with `watch-pr-mr`.
- Extends the workflow from GitHub to GitLab and Forgejo, and removes the T3
  Code tools `watch_pull_request` and `unwatch_pull_request`.

Licensed under the MIT terms in `LICENSE.upstream`.
