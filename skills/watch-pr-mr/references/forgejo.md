# Forgejo with `fgj`

The script reads the pull request, the combined commit status of its head,
the base branch's protection rule, reviews with their comments, and issue
comments through `fgj api`. Verified against Forgejo 15.0; the review and
thread paths are untested. Maintainer notes on unverified behavior are in
`OPEN-QUESTIONS.md` at the skill root.

How the snapshot maps Forgejo:

- **Checks** are the commit statuses of the head, which include Forgejo
  Actions jobs. A check is required when the base branch's protection rule
  enables status checks and lists a matching context pattern. A required
  pattern that no status matches yet counts as a pending check.
- **Behind** compares the pull request's `merge_base` with the base branch
  head. **Conflicts** means `mergeable` is false on a pull request that is not
  a draft; Forgejo reports every draft as not mergeable.
- **Threads:** the API has no thread object. The script treats review
  comments on the same file line as one thread. Forgejo stores the resolution
  on the thread's first comment. A top-level comment from you that is newer
  than the thread's last comment counts as your reply.
- **Approvals** count the latest official, non-stale approval per reviewer
  against the rule's `required_approvals`.
- **Bots** have no flag in the API; logins ending in `[bot]`, `-bot`, or
  `_bot` count as bots.
- **Auto-merge** is `null`, because the API does not show whether a merge is
  scheduled.

## Draft and ready

A title prefix marks the draft. The defaults are `WIP:` and `[WIP]`; an
instance can configure others. The `draft` field is read-only.

```sh
fj pr create --repo HOST/OWNER/REPO --base main --head BRANCH "WIP: Title" --body-file /abs/body.md
fj pr edit N title "Title"     # remove the prefix to mark it ready
```

## Auto-merge

Cancel a scheduled auto-merge before working on the pull request, even though
the API cannot show whether one exists:

```sh
fgj api -X DELETE repos/OWNER/REPO/pulls/N/merge --hostname HOST
```

## Threads

The API cannot resolve a review thread, and the script sets no `thread`
handle. Reply with a top-level comment that links the review comment's URL;
the thread then no longer awaits your reply. Only a person can resolve it, in
the web UI:

```sh
fj pr comment N --body-file /abs/reply.md
```

## Checks

```sh
fj pr status N --wait                       # waits for checks only
fgj actions run view RUN --log -R HOST/OWNER/REPO
fgj actions run rerun RUN -R HOST/OWNER/REPO
```
