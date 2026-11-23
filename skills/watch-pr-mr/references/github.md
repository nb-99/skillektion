# GitHub with `gh`

The script reads the pull request through one GraphQL query per poll and one
REST compare call for the behind count. On GitHub Enterprise Server it passes
`--hostname`.

GitHub reports a required check that has not started, and rules the snapshot
does not model, only as `mergeStateStatus: BLOCKED`. When nothing else in the
gate explains `BLOCKED`, the gate lists it as pending. Drafts report `DRAFT`
instead, so these blocks show only once the pull request is ready.

## Draft and ready

```sh
gh pr create --draft --title T --body-file /abs/body.md
gh pr ready N              # draft -> ready for review
gh pr ready N --undo       # ready -> draft
```

## Auto-merge and merge queue

```sh
gh pr view N --json autoMergeRequest --jq .autoMergeRequest   # null when off
gh pr merge N --disable-auto
gh api graphql -f query='mutation($id: ID!) { dequeuePullRequest(input: {id: $id}) { clientMutationId } }' \
  -f id="$(gh pr view N --json id --jq .id)"
```

## Copilot code review

Check whether a ruleset already requests Copilot reviews for the base branch:

```sh
gh api repos/OWNER/REPO/rules/branches/BASE \
  --jq '.[] | select(.type == "copilot_code_review") | .parameters'
```

`review_draft_pull_requests` means Copilot reviews drafts, and
`review_on_push` means it reviews every push. Without either, Copilot reviews
once, when a pull request opens as ready or first leaves draft. Personal
Copilot settings can also request reviews, and the API does not show them.

Request a review, or re-request it after a push, with gh 2.88 or later. GitHub
Enterprise Server does not support it:

```sh
gh pr edit N --add-reviewer @copilot
```

Copilot reviews as `copilot-pull-request-reviewer`. Re-reviews can repeat
comments that were already resolved.

## Threads

The `thread` handle of a snapshot item is the thread's GraphQL node ID:

```sh
gh api graphql -f query='mutation($t: ID!, $b: String!) { addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $t, body: $b}) { comment { url } } }' \
  -f t=THREAD_ID -F b=@/abs/reply.md
gh api graphql -f query='mutation($t: ID!) { resolveReviewThread(input: {threadId: $t}) { thread { isResolved } } }' \
  -f t=THREAD_ID
gh pr comment N --body-file /abs/comment.md                    # top-level comment
```

## Checks

```sh
gh pr checks N --required
gh run view RUN_ID --log-failed
gh run rerun RUN_ID --failed
```

## Rate limits

GraphQL and REST have separate limits. Check GraphQL with
`gh api rate_limit --jq .resources.graphql`. When it is used up, read the pull
request through REST: `gh api repos/OWNER/REPO/pulls/N` and
`gh api repos/OWNER/REPO/commits/SHA/check-runs`.
