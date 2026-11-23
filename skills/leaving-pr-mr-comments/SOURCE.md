# Source

This skill adapts `skills/leaving-pr-comments` from
[`t3dotgg/tstack`](https://github.com/t3dotgg/tstack) at commit
`11e37a74d0a6868c121cd0910ab2b3bd9873b92a`.

It keeps upstream's note-alert attribution, the leak check, the direct writing
style, and the rule to resolve a thread only after its reply was posted.

It changes the following:

- Renames the skill to `leaving-pr-mr-comments` and extends it from GitHub to
  GitLab and Forgejo, which both render the same `> [!NOTE]` alert.
- Narrows the trigger to pull and merge request comments; upstream triggers on
  any GitHub comment.
- Resolves threads only where the host allows it, because the Forgejo API has
  no endpoint for resolving a review thread.

Licensed under the MIT terms in `LICENSE.upstream`.
