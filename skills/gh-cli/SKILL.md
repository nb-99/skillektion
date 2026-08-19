---
name: gh-cli
description: Operate on GitHub from the terminal with the gh CLI. Use for GitHub repositories, issues, pull requests, reviews, Actions/workflow runs, releases, code scanning alerts, and code search.
---

# GitHub via the `gh` CLI

Use the `gh` CLI for all GitHub operations. `gh api` covers anything without a
dedicated subcommand.

Read freely; **ask for confirmation before any write/mutation** (creating or
editing issues/PRs, commenting, reviewing, merging, releasing).

## Repos & info

```sh
gh repo view OWNER/REPO
gh api repos/OWNER/REPO
gh search repos "QUERY" --limit 10
gh search code "QUERY"            # cross-repo code search
```

## Issues

```sh
gh issue list --repo OWNER/REPO --state open
gh issue view NUMBER --repo OWNER/REPO --comments
gh issue create --repo OWNER/REPO --title T --body B   # WRITE: confirm first
gh issue comment NUMBER --body B                        # WRITE: confirm first
```

## Pull requests

```sh
gh pr list --repo OWNER/REPO
gh pr view NUMBER --comments
gh pr diff NUMBER
gh pr checks NUMBER                 # CI status
gh pr create --base main --head BRANCH --title T --body B   # WRITE: confirm
gh pr review NUMBER --approve|--request-changes -b B        # WRITE: confirm
gh pr merge NUMBER --squash                                 # WRITE: confirm
```

## Actions / workflows

```sh
gh run list --repo OWNER/REPO --limit 10
gh run view RUN_ID --log
gh run view RUN_ID --log-failed     # only failed step logs
gh run rerun RUN_ID                 # WRITE: confirm first
gh workflow list
gh workflow run WORKFLOW --ref BRANCH   # WRITE: confirm first
```

## Releases

```sh
gh release list --repo OWNER/REPO
gh release view TAG
gh release create TAG --notes N     # WRITE: confirm first
```

## Code scanning / security (via gh api)

```sh
gh api repos/OWNER/REPO/code-scanning/alerts --paginate
gh api repos/OWNER/REPO/code-scanning/alerts/ALERT_NUMBER
gh api repos/OWNER/REPO/dependabot/alerts --paginate
```

## Tips

- `--json FIELDS --jq '...'` for structured output:
  `gh pr list --json number,title,headRefName --jq '.[] | .title'`.
- `gh api --paginate` to traverse all pages.
- Authentication uses the existing `gh auth` session / `$GITHUB_TOKEN`.
