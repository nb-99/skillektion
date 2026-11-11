# `fj` command reference

Exact templates for `fj` (forgejo-contrib/forgejo-cli), the Forgejo CLI with
dedicated interactive UX. Templates are transcribed from `fj` 0.7.0 `--help`;
check `fj <command> --help` on the installed version, because flags shift
between releases.

- Docs: the project wiki, current as of forgejo-cli 0.5.0, at
  `https://codeberg.org/forgejo-contrib/forgejo-cli/wiki` (pages: Authentication,
  Repositories, Issues, PRs, Actions, Users, Organizations, Milestone).
- Source: `https://codeberg.org/forgejo-contrib/forgejo-cli` (Rust, `src/`).

Replace `HOST/OWNER/REPO`, `REPO`, `PR`, `ISSUE`, `TAG`, `RELEASE`, `QUERY`,
and `NAME` with target values.

## Targeting

`fj` infers the repository from the Git checkout. Make it explicit when several
remotes or repositories are in play:

- `-r HOST/OWNER/REPO` names the repository.
- `-R NAME` selects a local Git remote; `-H HOST` names the instance.
- `-C DIR` sets the working directory for the call.
- `--style minimal` is a global flag placed before the subcommand. Piping
  applies it automatically; add it when a script parses the output.
- `fj auth list` shows logged-in instances; `fj whoami` shows the current one.

## Repositories

```sh
fj repo view --repo HOST/OWNER/REPO
fj repo readme --repo HOST/OWNER/REPO
fj repo clone HOST/OWNER/REPO [PATH]                    # add -S ssh, -I KEYFILE for SSH
fj repo create NAME --description "Description" --private --remote origin --push
fj repo fork HOST/OWNER/REPO
fj repo migrate                                         # migrate or mirror an existing repo
fj repo edit --repo HOST/OWNER/REPO --description "..." --private true --default-branch main --archived false
fj repo delete --repo HOST/OWNER/REPO
fj repo star --repo HOST/OWNER/REPO                     # also unstar, star-status
fj repo watch --repo HOST/OWNER/REPO                    # also unwatch, watch-status
fj repo browse --repo HOST/OWNER/REPO
```

`repo edit` also sets `--name`, `--website`, `--template true|false`,
`--mirror-interval 8h30m0s`, `--enable-prune true|false`, `--avatar FILE`,
`--unset-avatar`.

### Units and labels

Repository units are the feature toggles: `issues`, `prs`, `actions`, `wiki`,
`packages`, `projects`, `releases`.

```sh
fj repo units --repo HOST/OWNER/REPO issues --enable false
fj repo labels --repo HOST/OWNER/REPO view
fj repo labels --repo HOST/OWNER/REPO create NAME RRGGBB --description "..." --exclusive
fj repo labels --repo HOST/OWNER/REPO edit NAME
fj repo labels --repo HOST/OWNER/REPO delete NAME
```

Label colors use the hexadecimal format shown by
`fj repo labels create --help`. A `/` in the name namespaces the
label; `--exclusive` makes it exclusive within its namespace.

## Issues

```sh
fj issue search --repo HOST/OWNER/REPO --state open 'QUERY'
fj issue search --repo HOST/OWNER/REPO --state all --labels bug,docs --assignee USERNAME
fj issue search --repo HOST/OWNER/REPO --milestones "v1.0,v1.1" --creator USERNAME --all
fj issue view --remote origin ISSUE
fj issue view --remote origin ISSUE body               # also: comments, assignees, comment N
fj issue templates --repo HOST/OWNER/REPO              # templates for issue create
fj issue create --repo HOST/OWNER/REPO "Title" --body "Description"
fj issue create --repo HOST/OWNER/REPO "Title" --body-file /abs/path.md --template "Bug Report"
fj issue create --repo HOST/OWNER/REPO "Title" --milestone "v1.0"
fj issue comment --remote origin ISSUE "Additional context"
fj issue comment --remote origin ISSUE --body-file /abs/path/comment.md
fj issue assign --remote origin ISSUE USER1 USER2
fj issue unassign --remote origin ISSUE USER1
fj issue edit --remote origin ISSUE title "New title"  # omit to open editor
fj issue edit --remote origin ISSUE body "New body"    # omit to open editor
fj issue edit --remote origin ISSUE labels --add docs --rm bug
fj issue edit --remote origin ISSUE milestone "v1.0"   # or --unset
fj issue close --remote origin ISSUE --with-msg "Closing because ..."
fj issue depend add ISSUE TARGET1 TARGET2              # also: remove, list
fj issue block add ISSUE TARGET1 TARGET2               # also: remove, list
fj issue browse --remote origin ISSUE
```

Omitting `--body`, `--body-file`, or a positional body opens the editor. If the
repository disables blank issues, `issue create` needs `--template NAME`
(list templates first with `issue templates`).

## Pull requests

```sh
fj pr search --repo HOST/OWNER/REPO --state open 'QUERY'
fj pr search --repo HOST/OWNER/REPO --state all --labels bug --milestones "v1.0" --all
fj pr view PR
fj pr view PR body                                     # also: comments, labels, assignees
fj pr view PR diff                                     # also: files, commits, comment N
fj pr status PR
fj pr status PR --wait
fj pr create --repo HOST/OWNER/REPO \
  --base main --head feature/example \
  "Title" --body-file /abs/path/pr-body.md
fj pr create --repo HOST/OWNER/REPO --autofill         # title/body from commits
fj pr create --repo HOST/OWNER/REPO "Title" --milestone "v1.0" --web
fj pr comment PR "Review comment"
fj pr comment PR --body-file /abs/path/review.md
fj pr checkout PR --branch-name review-PR              # add -S ssh -I KEYFILE; ^PR for parent repo
fj pr edit PR title "New title"                        # also: body, comment, labels, milestone
fj pr edit PR labels --add bug --rm wontfix
fj pr review PR list
fj pr review PR request REVIEWER1 REVIEWER2            # or --team TEAM1 --team TEAM2
fj pr assign PR USER1 USER2                            # also: unassign
fj pr depend add PR TARGET1                            # also: remove, list, block
fj pr close PR --with-msg "Closing because ..."
fj pr merge PR --method rebase                         # also: -d delete branch, -t/-m commit message
fj pr browse PR
```

Prefix the title with `WIP: ` to create a draft PR. `--autofill` derives the
title and body from commits. Merge methods: `merge`, `rebase`, `rebase-merge`,
`squash`, `manual`, `fast-forward-only`.

### AGit pull requests

`--agit` creates a PR without the fork/push flow by pushing refs with Git
options. It can change local Git configuration and push data; confirm
immediately before using it:

```sh
fj pr create --repo HOST/OWNER/REPO --agit "Title" --head feature/example
```

## Milestones

```sh
fj milestone search --repo HOST/OWNER/REPO --state all --title "v1.0"
fj milestone create --repo HOST/OWNER/REPO --state open "v1.0" --description "..."
fj milestone edit --repo HOST/OWNER/REPO "v1.0" --new-title "v1.1" --state closed
fj milestone view --repo HOST/OWNER/REPO "v1.0"
fj milestone delete --repo HOST/OWNER/REPO "v1.0"
```

## Actions

`fj actions` lists tasks and dispatches workflows. Use `fgj` for run/job
inspection, logs, watch, rerun, and cancel.

```sh
fj actions tasks --repo HOST/OWNER/REPO                # one page holds up to 20 tasks
fj actions tasks --remote origin --page 2
fj actions dispatch --repo HOST/OWNER/REPO WORKFLOW.yml main --inputs key=value
fj actions variables --repo HOST/OWNER/REPO list       # also: create, delete
fj actions secrets --repo HOST/OWNER/REPO list         # also: create, delete
```

`variables` and `secrets` subcommands ask for values interactively; never pass
secret values as arguments.

## Releases

```sh
fj release list --repo HOST/OWNER/REPO
fj release list --repo HOST/OWNER/REPO --include-prerelease --include-draft
fj release view --repo HOST/OWNER/REPO RELEASE         # add --by-tag to name a tag
fj release create --repo HOST/OWNER/REPO RELEASE --tag TAG --body "Notes" --attach dist/file.tar.gz
fj release create --repo HOST/OWNER/REPO RELEASE --create-tag --branch main
fj release edit --repo HOST/OWNER/REPO RELEASE --body "Updated notes" --draft true
fj release edit --repo HOST/OWNER/REPO RELEASE --rename NEW-NAME --prerelease false
fj release asset create --repo HOST/OWNER/REPO RELEASE FILE [NAME]
fj release asset download --repo HOST/OWNER/REPO RELEASE NAME
fj release delete --repo HOST/OWNER/REPO RELEASE       # add --by-tag to name a tag
```

`--create-tag` makes the tag from the release name (use `--branch` to base it);
`--tag TAG` attaches the release to an existing tag. `--attach FILE:NAME` sets
an attachment name that differs from the file name. `release delete` keeps the
Git tag.

## Tags

```sh
fj tag list --repo HOST/OWNER/REPO
fj tag view --repo HOST/OWNER/REPO TAG
fj tag create --repo HOST/OWNER/REPO TAG --branch BRANCH
fj tag create --repo HOST/OWNER/REPO TAG --body "Annotated tag message"
fj tag delete --repo HOST/OWNER/REPO TAG
```

Tag changes may trigger workflows and alter repository history; confirm
deletions.

## Wiki

```sh
fj wiki contents --repo HOST/OWNER/REPO
fj wiki view --repo HOST/OWNER/REPO PAGE
fj wiki clone --repo HOST/OWNER/REPO --path ./REPO-wiki
fj wiki clone --repo HOST/OWNER/REPO --ssh --path ./REPO-wiki
fj wiki browse --repo HOST/OWNER/REPO
```

Edit pages in the cloned Git repository, then commit and push with Git.

## Users and organizations

```sh
fj user search USERNAME
fj user view USERNAME
fj user repos USERNAME                                 # also: orgs, activity, followers, following
fj user key list                                       # also: add, delete; gpg for GPG keys
fj org list
fj org view ORG
fj org members ORG
fj org team list ORG
fj org team view ORG TEAM                              # also: create, edit, delete, repo, member
fj org activity ORG
```

`fj org create`, `org edit`, `org visibility`, `user edit`, `user follow`,
`user block`, and `repo fork` cover account-level changes; check their help
before use.

## Authentication

```sh
fj auth login                                          # opens the auth page in a browser
fj auth add-token HOST                                 # store a token non-interactively
fj auth use-ssh HOST true                              # default clone protocol per instance
fj auth list
fj auth logout HOST
```
