---
name: git-working-agreement
description: When making changes to a repository, use this skill.
---

# Git Working Agreement

- Make changes on worktrees, or alternatively a feature branch. Never on main unless specified or asked to.
- Branch and worktree names should be descriptive and use proper prefixes.
- An explicit user request that names the repository or branch and a bounded Git
  write action authorizes that action. Otherwise, show the exact command or
  change and ask for confirmation.
- Always confirm immediately before destructive, irreversible,
  privilege-changing, or materially broader work. This includes deleting
  branches or tags, discarding changes, rewriting published history, force
  pushing, changing access, and writes outside the requested scope.
- Prefer fast-forward/rebase merges; create a merge commit only when fast-forward/rebase is impossible or explicitly requested.
- Update a feature branch by rebasing it onto its base branch rather than merging the base branch into it; when it is behind `origin/main`, fetch and rebase onto `origin/main` rather than using a merge-based pull.
- Use git cli commands to interact with repositories; `gh` for GitHub, `glab` for GitLab.
- Follow the hosting workflow's authorization rules for comments, reviews, and
  other pull-request or issue writes. When no hosting workflow is loaded, show
  the exact mutation and confirm before running it.
- For commit messages, use the `git-conventional-commits` skill.
