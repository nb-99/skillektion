---
name: drive-to-ready
description: Take a change unattended to a proven, reviewed, ready PR/MR that only needs your merge, and never merge it.
disable-model-invocation: true
---

# Drive to Ready

The user invoked this skill because they are not watching. Your updates and
your final message go unread until long after you stop. You own the work from
its current state to an open PR/MR, marked ready, that passes the readiness
gate. You never merge it.

## Permissions

This request grants, for this task only, permission to:

- create a branch or worktree, commit, push this task's branch, rebase it, and
  push it with `--force-with-lease`;
- open a draft PR/MR, request automated review, reply to and resolve review
  threads, and mark the PR/MR ready;
- run the tests, checks, and run commands the repository already defines, and
  add a focused test inside its existing test setup.

It never covers merging, enabling auto-merge, entering a merge queue or merge
train, pushing to the default branch or any other branch, bypassing branch
protection, or delegating any of these. Harness approval prompts still apply.

## Steps

1. **Finish the change.** Make the smallest change that achieves the goal,
   and fix the case that happened, not every case that could. Work on a
   branch or worktree as the `git-working-agreement` skill describes.
2. **Prove it.** See "Proof".
3. **Review it locally.** Load the `code-review` skill for the diff against
   the base. When the user's request asks for a council or a multi-model
   review, load the `council` skill instead; it runs its own loop. After
   code-review, fix the **Act on** findings, prove the fixes, and review the
   changes again, for at most three rounds. Record declined findings as
   follow-ups.
4. **Open a draft.** Load the `watch-pr-mr` skill; its host reference has the
   commands for auto-merge, review requests, and marking ready. If a PR/MR
   already exists for the branch, read it with `pr-mr-watch snapshot` and turn
   off auto-merge, a merge queue, or a merge train before you push; keep its
   draft state. Rebase onto the latest base branch and push. If no PR/MR
   exists, create a draft with the `creating-a-pr-mr` skill, with one line in
   the description that says how you proved the change. No host merges a
   draft, so the draft guards against an early merge. Check for automatic
   merging again before each push, and report what you turned off. If you
   cannot prevent an automatic merge, stop and report it.
5. **Request automated review.** On GitHub, when no ruleset requests Copilot
   reviews of drafts and no other review bot has reviewed the draft, request
   `@copilot` as a reviewer. When the request fails, continue and note it in
   the report.
6. **Watch and fix** with `pr-mr-watch wait --until ready`, acting on events
   as `watch-pr-mr` describes. Prove each fix before you push it. Review
   behavior changes and meaningful conflict fixes again with `code-review`.
7. **Check readiness while it is a draft.** Continue when the readiness gate
   holds apart from the draft flag.
8. **Mark it ready**, unless it already is, then watch again with
   `wait --until ready`. Marking it ready starts Copilot's one-time automatic
   review, workflows that run on `ready_for_review`, and bots that skip
   drafts. Fix what arrives while the PR/MR stays ready, and check the gate
   again.
9. **Hand off.** See "Handoff".

Stay active from step 1 to step 9. If you end your turn while checks or bots
are pending, the work stops, because nobody will prompt you again. Wait with
the `watch-pr-mr` script so that something wakes you when the PR/MR changes.

## Proof

Proof is evidence you observed yourself in this session: command output, a
reproduction, a screenshot. Use the most direct proof the change allows:

- Reproduce the original failure, apply the fix, then watch the same
  reproduction pass.
- Run the checks that the repository's CI runs, such as typecheck, lint, and
  tests.
- Add one focused test that fails without the fix, when the behavior has none
  and the repository has a test setup.
- For UI and runtime behavior, run the app with the repository's own commands
  and look at the change, when its instructions allow that without asking.
  Green mocked tests do not prove that the user experience works. Attach
  screenshots to the PR/MR description when you took them.

When proof needs more than the repository's own tests, checks, and run
commands, such as computer use, browser automation, simulators or devices, a
dev server against shared services, or new test tooling, ask the user. When
you cannot prove a change, you do not have full confidence; ask the user.

## Readiness gate

The readiness gate passes when all of these hold on the latest head:

- `pr-mr-watch wait --until ready` exited 0, and `pr-mr-watch snapshot`
  reports `gate.verdict` as `ready` or `waiting-for-review`. The verdict
  covers checks, review bots, threads awaiting your reply, the base branch,
  and conflicts.
- Your proof and review cover the final diff, including conflict fixes.
- You fixed or answered in writing every review bot finding and every
  requested change.
- Nothing will merge it without the user: the snapshot's `auto_merge` is not
  true, and no merge queue or merge train holds it.

Only `gate.human` may remain: a missing approval, or a reviewer's re-review
after you fixed or answered their requested changes.

## Asking the user

A question in a normal message goes unseen, and the thread looks done. Ask
through the harness's question tool, so the thread shows that it is waiting.
Put all the context in the question: the PR/MR link, what stops you, and the
options with your recommendation first.

Ask only when you cannot continue alone:

- You cannot prove the change.
- Proof needs a test method outside the repository's own tests and commands.
- The readiness gate cannot pass, and you cannot fix that yourself.
- The next step is outside the permissions above: deleting data, touching
  production, changing things outside the repository, closing a PR/MR, or
  force-pushing another branch.
- The goal is ambiguous in a way that changes the result.
- Another PR/MR makes this one obsolete.

Decide everything else yourself with sensible defaults, and list those
decisions in the report. If no question tool is available, or it returns no
answer, take the safe path: leave the PR/MR open and unmerged, and start your
final message with the question.

## Handoff

Fetch the base branch and read the live PR/MR with `pr-mr-watch snapshot`.
Confirm that it is open, not a draft, and not set to merge without the user.
If someone else merged it, report that instead. Then report one outcome:

- **Ready to merge:** the readiness gate passes with verdict `ready`.
- **Waiting for review:** the readiness gate passes with verdict
  `waiting-for-review`. Confirm that the `gate.human` item is the actual
  reason the PR/MR cannot merge.
- **Stuck:** the readiness gate does not pass, for example because a
  `pending` item never clears. Say what prevents readiness, what you tried,
  and what is needed, following "Asking the user".

Report the PR/MR link, the final head, the outcome, your proof, the review
outcome from code-review or council and from review bots, the decisions you
made for the user, declined findings as follow-ups, and remaining risks. State
that the PR/MR is still open and unmerged.
