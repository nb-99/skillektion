# Open questions

Maintainer notes for `pr-mr-watch`, not instructions for running it. Each
question below is unverified; resolve it against a live instance and update
the script and host reference.

## Forgejo

Snapshots of open and closed pull requests with failing checks and top-level
comments worked against Forgejo 15.0.12 (`gitea-1.22.0` compatible). The test
repository had no pull request reviews, so every review path is untested.

1. **Inline replies:** can the API reply inside a review thread?
   `POST /repos/{owner}/{repo}/pulls/{index}/reviews/{id}/comments` adds a
   comment to a review; check whether it renders as a reply in the thread.
   Until then, the script counts a newer top-level comment from the viewer as
   the reply.
2. **Resolving threads:** the 15.0 API has no resolve endpoint. Check newer
   releases.
3. **Thread grouping:** the script groups review comments by `path` and
   `original_position` (or `position`) and reads the resolution from the
   lowest comment ID. Confirm that replies share these values and that
   outdated comments do not split a thread.
4. **Scheduled auto-merge:** the pull request object does not show a
   scheduled merge. Find a field or endpoint that does, and record what
   `DELETE /pulls/{index}/merge` returns when none is scheduled.
5. **Draft prefixes:** find out whether the API exposes the instance's
   `WORK_IN_PROGRESS_PREFIXES`.
6. **Approvals:** confirm that counting the latest official, non-stale approval
   per reviewer matches the protection rule's evaluation, including
   `dismiss_stale_approvals` and approval allowlists.
7. **Protection rules:** `GET /branch_protections` may need repository admin
   rights. Without them, checks are not marked required and approvals are not
   counted. Find a read path that works for writers.
8. **Mergeable:** Forgejo reports `mergeable: false` for drafts, conflicts,
   and while it checks a new head. The script ignores it on drafts and `wait`
   needs two polls in a row. Find a field that tells conflicts apart.
9. **Bot detection:** find a reliable bot marker instead of the login suffix.

## Other hosts

- **GitLab:** the pipeline job mapping is untested; the test merge requests
  had no pipelines. Discussions, reviewers, and approvals each read one page
  of up to 100 entries.
- **GitHub:** bot review requests are detected through the `Bot` type of
  `reviewRequests`. Confirm that a pending Copilot review request appears
  there. The unexplained `BLOCKED` mapping is untested against a live pull
  request.
