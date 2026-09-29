---
name: creating-a-pr-mr
description: Create a pull request or merge request. Use when asked to open a PR/MR.
---

# Create a PR or MR

Use the host-specific `gh-cli`, `glab-cli`, or `forgejo-cli` skill for repository operations and creation commands. Follow its authorization rules and the `git-working-agreement` skill for Git changes. This skill owns the content and reviewability checks, not the host commands.

1. Identify the repository, target branch, and proposed head branch. Before creating anything, inspect the worktree status, commits and diff from the target branch, and any existing PR/MR for the same head and target. Confirm the target branch if it cannot be inferred reliably. Account for uncommitted work: it will not appear in the PR/MR.
2. Assess the commit history shown to reviewers. Check for unrelated commits, accidental merge commits, fixup/squash commits, duplicate or misleading messages, and changes already present on the target branch. Several focused commits are fine. Report whether the history is clean, with specific reasons if it is not. If cleanup would rewrite published history or require a force-push, explain the issue and ask before doing so; do not block creation solely because history is imperfect unless the user wants to fix it first.
3. Check for repository PR/MR templates and contribution conventions. Use an applicable template's required sections. If none applies, use [the description outline](references/description-outline.md) as a guide. Base the title and description on the actual diff and intent, not just commit messages. Explain why the change is needed and how it works at a high level. Include verification actually performed and relevant reviewer guidance; state gaps plainly. Adapt or omit optional headings to fit the change. Keep the description concise and focused on the key points, only be as detailed as necessary.
4. Before creating, inspect the proposed description against the diff and check that it has intent, approach, verification, and useful reviewer guidance. Use the host's creation command with an explicit description. If a PR/MR already exists for the same head and target, update it only when requested or clearly part of the user's task; avoid a duplicate.
5. Report the PR/MR URL, verification evidence, and a separate commit-history verdict. If the history needs cleanup, name the affected commits or pattern and the recommended action. Do not claim the history is clean without inspecting the range against the target.
