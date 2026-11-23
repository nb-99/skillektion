# GitLab with `glab`

The script reads the merge request, its head pipeline's jobs, discussions,
reviewers, and approvals through `glab api`. Projects are addressed by their
URL-encoded path, for example `projects/group%2Fproject`. Each call reads up
to 100 jobs or discussions.

Jobs with `allow_failure` count as optional checks. A blocking manual job
counts as failing until someone starts it. A head pipeline for an older commit
counts as pending, and so does a missing pipeline when the project requires
one. While GitLab is still checking the merge request (`checking`,
`unchecked`, `preparing`, `approvals_syncing`), the gate lists the status as
pending. Merge blocks that the snapshot does not model, such as
`discussions_not_resolved` or `jira_association_missing`, appear as
`host status: <detailed_merge_status>` blockers. GitLab reports one status at a
time, and a draft reports `draft_status`, which hides the others.

## Draft and ready

```sh
glab mr create --draft --title T --description-file /abs/body.md
glab mr update N --ready
glab mr update N --draft
```

## Auto-merge and merge trains

`merge_when_pipeline_succeeds` in the snapshot's source data means auto-merge
is on. Cancelling it also removes the merge request from a merge train:

```sh
glab api -X POST "projects/PROJECT/merge_requests/N/cancel_auto_merge"   # GitLab 19.5+
glab api -X POST "projects/PROJECT/merge_requests/N/cancel_merge_when_pipeline_succeeds"   # older
```

The older endpoint returns `201` with `"status": "error"` when auto-merge was
off; read the `status` field.

## Threads

The `thread` handle of a snapshot item is the discussion ID:

```sh
glab api -X POST "projects/PROJECT/merge_requests/N/discussions/DISCUSSION_ID/notes" -F body=@/abs/reply.md
glab api -X PUT "projects/PROJECT/merge_requests/N/discussions/DISCUSSION_ID" -f resolved=true
glab mr note N --message M                                               # top-level comment
```

## Pipelines

```sh
glab ci status --live        # watch the current branch's pipeline by hand
glab ci trace JOB_ID
glab ci retry JOB_ID
```
