---
name: leaving-pr-mr-comments
description: Format comments an agent posts for the user on a pull or merge request. Use whenever posting a comment or reply on a PR/MR on GitHub, GitLab, or Forgejo.
---

# Leaving PR/MR Comments

Prefix every agent-authored comment left on the user's behalf with this note
alert. GitHub, GitLab 17.10 and later, and Forgejo render it as a note box:

```md
> [!NOTE]
> 🤖 **<model> responding on behalf of <user>**

Actual comment starts here.
```

Use the verified public name of the model that wrote the comment, and the
user's name or login on the host.

If the harness does not expose a model name, use the harness name. Do not guess.

Before posting, check the entire comment, including quoted text and
attachments, for secrets and private details.

Keep the attribution inside the note and the actual reply outside it. The
context line must start with the robot emoji. Do not add a horizontal rule,
Setext underline, heading, signature footer, or a second attribution.

Apply this format to top-level PR/MR comments, inline review comments, replies
to bots or reviewers, and written explanations used before resolving or
dismissing feedback. Do not add it to PR/MR descriptions, commit messages, or
text the user explicitly asked to post verbatim without attribution.

Write the comment itself in a direct style:

- Lead with the conclusion.
- Cite the relevant code, behavior, check, or reproduction.
- Keep it concise and avoid filler, canned thanks, or status narration.
- Distinguish verified facts from judgment.

Preview the final Markdown before posting so quoting and blank lines render as
shown. After posting, verify that the host returned the comment or review URL.
Resolve a review thread only after its response was posted successfully, and
only where the host lets you resolve threads.
