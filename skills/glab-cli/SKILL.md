---
name: glab-cli
description: Operate on GitLab from the terminal with the glab CLI. Use for GitLab issues, merge requests, pipelines/CI, and releases. Mirrors the gh-cli workflow for GitLab-hosted repositories.
---

# GitLab via the `glab` CLI

Use the `glab` CLI for all GitLab operations (`glab api` covers anything without
a dedicated subcommand). Prerequisite: `glab auth status` must be authenticated.

Read freely. An explicit user request that names the GitLab target and a bounded
write action authorizes that action. Otherwise, show the exact mutation and ask
for confirmation before running it.

Always confirm immediately before destructive, irreversible,
privilege-changing, or materially broader work. This includes merges, closing
or deleting content, publishing or deleting releases, changing access or
secrets, and any action whose effects exceed the request. Recheck the project
and object identifier before every mutation.

## Repos & info

```sh
glab repo view GROUP/PROJECT
glab api projects/GROUP%2FPROJECT          # URL-encode the slash as %2F
```

## Issues

```sh
glab issue list --repo GROUP/PROJECT
glab issue view NUMBER --comments
glab issue create --title T --description D   # WRITE
glab issue note NUMBER --message M            # WRITE
```

## Merge requests

```sh
glab mr list
glab mr view NUMBER --comments
glab mr diff NUMBER
glab mr create --source-branch BRANCH --target-branch main --title T   # WRITE
glab mr approve NUMBER                                                 # WRITE
glab mr merge NUMBER --squash                                          # HIGH-RISK: confirm
```

## Pipelines / CI

```sh
glab ci list
glab ci view              # current branch's pipeline
glab ci status
glab ci trace JOB_ID      # stream a job's log
glab ci retry JOB_ID      # HIGH-RISK: confirm
```

## Releases

```sh
glab release list
glab release view TAG
glab release create TAG --notes N   # HIGH-RISK: confirm
```

## Tips

- `-R GROUP/PROJECT` (or `--repo`) targets a project from anywhere.
- `glab api --paginate <endpoint>` for raw REST access and pagination.
- When linking work, reference the issue in commit footers (`Refs: #123`).
