---
name: glab-cli
description: Operate on GitLab from the terminal with the glab CLI. Use for GitLab issues, merge requests, pipelines/CI, and releases.
---

# GitLab via the `glab` CLI

Use the `glab` CLI for all GitLab operations (`glab api` covers anything without
a dedicated subcommand). Prerequisite: `glab auth status` must be authenticated.

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
glab mr create --draft --source-branch BRANCH --title T                # WRITE: draft
glab mr update NUMBER --ready                                          # WRITE: draft -> ready
glab mr update NUMBER --draft                                          # WRITE: ready -> draft
glab mr approve NUMBER                                                 # WRITE
glab mr merge NUMBER                                                   # HIGH-RISK: confirm unless requested
```

Add `--squash` only when the user requests squashing or project policy requires it.

## Pipelines / CI

```sh
glab ci list
glab ci view              # current branch's pipeline
glab ci status
glab ci trace JOB_ID      # stream a job's log
glab ci retry JOB_ID      # HIGH-RISK: confirm unless requested
```

## Releases

```sh
glab release list
glab release view TAG
glab release create TAG --notes N   # HIGH-RISK: confirm unless requested
```

## Tips

- `-R GROUP/PROJECT` (or `--repo`) targets a project from anywhere.
- `glab api --paginate <endpoint>` for raw REST access and pagination.
