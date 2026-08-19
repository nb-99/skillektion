---
name: git-conventional-commits
description: Write git commit messages following Conventional Commits 1.0.0. Use whenever creating or amending a commit, or when a CONTRIBUTING guide is absent and a structured commit message is needed. Covers types, scopes, breaking changes, and examples.
---

# Conventional Commits

Format commit messages according to Conventional Commits 1.0.0.

If the repo has a contribution guide (e.g. `CONTRIBUTING.md`), its rules take
precedence over this skill.

## Structure

```
<type>(<optional scope>): <description>

<optional body>

<optional footer(s)>
```

- **description**: imperative mood, lowercase, no trailing period, <= ~72 chars.
- **body**: the _why_ and _what_, not the _how_. Wrap at ~72 cols. Optional.
- **footer**: `Refs: DHEI-1234`, `Co-authored-by:`, breaking-change note.

## Allowed types

`fix`, `feat`, `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `perf`,
`test`.

## Scope hints

- The scope is an optional noun naming the affected area — typically a module,
  package, component, or subsystem in this repo.
- Infer it from the touched path or the project's own convention (check recent
  `git log` for the scopes this repo already uses, and follow them).
- If a change spans many unrelated areas, prefer splitting into multiple commits.
- Omit the scope rather than invent a vague one.

## Breaking changes

A breaking change is signalled by either:

- `!` after the type/scope: `feat(api)!: drop v1 endpoints`, or
- a footer: `BREAKING CHANGE: <explanation>`.

**Do not commit a breaking change autonomously — stop and ask for confirmation
first.**

## Issue / ticket references

- If the work relates to a tracked issue, reference it in a footer rather than
  the subject: `Refs: PROJ-1234` (Jira) or `Refs: #123` (GitHub/GitLab).
- Use `Closes #123` / `Fixes #123` only when the commit actually resolves it and
  the platform supports auto-close.
- For Jira tickets, follow the `jira-workflow` skill (e.g. ids like `PROJ-1234`);
  put the id in the footer, don't transition the ticket as a side effect.

## Workflow

1. Inspect `git status` and `git diff --staged` to ground the message in the
   actual change. Stage only intended files.
2. Check recent `git log` to match the repo's existing type/scope conventions.
3. Draft the message; never auto-commit — present it and ask to proceed.
4. Do not add `Co-authored-by` or tool attribution unless asked.
