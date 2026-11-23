---
name: watch-pr-mr
description: Wait on a pull or merge request's CI, review bots, and reviews, and act on what arrives. Use when asked to watch, monitor, or babysit a PR/MR on GitHub, GitLab, or Forgejo.
---

# Watch a PR/MR

Run `scripts/pr-mr-watch` from this skill's directory by its absolute path. It
needs Python 3 and the host's CLI with a working login: `gh` for GitHub, `glab`
for GitLab, and `fgj` for Forgejo, whose reference also uses `fj`. It detects
the host from a PR/MR URL or the `origin` remote. For commands the script does
not cover, such as marking a
PR/MR ready, turning off auto-merge, requesting a review, replying to or
resolving a thread, and rerunning a job, read the host reference:
[GitHub](references/github.md), [GitLab](references/gitlab.md), or
[Forgejo](references/forgejo.md).

## Read the state

Run `pr-mr-watch snapshot [REF]` first. REF is a number or URL; without it the
script uses the open PR/MR of the current branch. The JSON has the same fields
on every host. Its `gate` sorts what stands between the PR/MR and merging by
who has to act:

- `blockers` are yours: failing checks, conflicts, a branch behind its base,
  review threads awaiting your reply, and host-specific merge blocks.
- `pending` clears on its own: running or unreported required checks,
  requested bot reviews, and host-side merge checks.
- `human` needs a person: a missing approval or requested changes.

`gate.verdict` is `blocked`, `pending`, `waiting-for-review` (only `human` is
left), or `ready`. It ignores the draft flag, which `gate.draft` reports.
`items` lists comments, reviews, and thread comments with their author, URL,
and `thread` handle. Handle the existing blockers and unanswered items before
you wait.

## Wait

```sh
pr-mr-watch wait [REF] [--until ready|green|any-change] [--timeout 3000] [--settle 120]
```

- `ready` (default): wait until the verdict is `ready` or
  `waiting-for-review`. Use it to babysit. It never exits 0 within `--settle`
  seconds of starting, so the reviews and workflows that a push or the ready
  flip starts can register first.
- `green`: wait for checks only. Required checks count when the host reports
  them, otherwise all checks. Conflicts and closing still exit 1.
- `any-change`: return 0 on the first event, whatever it is.

The script prints one line per event and exits at the first event that needs
you, so it works as a background command that notifies on completion or as
one long foreground command. Set the harness timeout above `--timeout`.

| Exit | Meaning |
| --- | --- |
| 0 | The condition holds, or the PR/MR merged. |
| 1 | You must act: a check failed, conflicts, the PR/MR closed, or the host stayed unreachable. With `ready`, also a gate blocker or a new comment or review from someone else. |
| 2 | Bad arguments, an unknown PR/MR, or another watcher already holds this PR/MR. |
| 3 | The timeout elapsed. |

Watch each PR/MR with this script only, one watcher at a time; it refuses a
second one. Start it again after each push, after you handle an exit 1, after
an exit 3, and after a resume. It remembers what it reported, so nothing that
arrived in between is lost. When an event needs no action, start it again
without posting or saying that you are still waiting. After two timeouts in a
row with the same `pending` item, stop waiting: find out why it does not
clear, and report it as a blocker.

## Act on events

- Act only on checks and comments newer than the latest push.
- Verify every finding against the source before you change code. Fix real
  findings and failures in the intended case, preferring the fix that deletes
  or narrows code. Prove each fix before you push it.
- Keep the PR/MR at the size its goal needs. Review loops grow a change one
  cheap fix at a time. Decline unneeded tests, guards for edge cases that do
  not matter, extra compatibility, and small performance costs with a written
  reason, and list them as follow-ups.
- Tell repository failures from infrastructure flakes. Rerun a failed job only
  when the task covers it; otherwise report the flake.
- Answer every finding you fix or dismiss with the `leaving-pr-mr-comments`
  skill, in its thread when it has one. Resolve the thread after the reply
  posts, where the host allows it.
- When the branch is behind or conflicts, rebase it onto its base branch as
  the `git-working-agreement` skill describes. Push with `--force-with-lease`,
  to this task's own branch only, when the task authorizes pushing.
- If an overlapping PR/MR makes this one obsolete, stop watching and ask the
  user before closing it.

## Stop

Stop when `wait` exits 0 for the condition you need, or when the calling
skill's gate passes. Merge only when the user explicitly asked for it. Report
the PR/MR link, the gate verdict, what you fixed, what you declined and why,
and what still waits on others.
