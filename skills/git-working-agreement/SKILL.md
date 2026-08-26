---
name: git-working-agreement
description: When making changes to a repository, use this skill.
---

# Git Working Agreement

- Make changes on worktrees, or alternatively a feature branch. Never on main unless specified or asked to.
- Branch and worktree names should be descriptive and use proper prefixes.
- Ask before performing destructive actions or rewriting history.
- Prefer fast-forward/rebase merges; create a merge commit only when fast-forward/rebase is impossible or explicitly requested.
- Update a feature branch by rebasing it onto its base branch rather than merging the base branch into it; when it is behind `origin/main`, fetch and rebase onto `origin/main` rather than using a merge-based pull.
- Use git cli commands to interact with repositories; `gh` for GitHub, `glab` for GitLab.
- Never post comments, reviews, or any write actions on PRs/issues without explicit confirmation first.
- For commit messages, use the `git-conventional-commits` skill.
