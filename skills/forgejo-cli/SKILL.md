---
name: forgejo-cli
description: Use fj and fgj for everyday Forgejo issues, pull requests, Actions, tags, releases, and wiki workflows.
---

# Forgejo CLI Tools

Two complementary CLIs are available:

- `fj`: Forgejo-native workflows, especially wiki Git operations, tags, repository settings, organizations, teams, and AGit pull requests.
- `fgj`: Actions run inspection and logs, JSON output, and generic authenticated Forgejo API access.

Both tools infer the repository from the current Git checkout where possible. Use an explicit repository or remote when working outside a checkout or when multiple remotes exist.

Read freely. An explicit user request that names the Forgejo target and a
bounded write action authorizes that action. Otherwise, show the exact mutation
and ask for confirmation before running it.

Always confirm immediately before destructive, irreversible,
privilege-changing, or materially broader work. This includes merging or
closing pull requests, deleting content or tags, publishing or deleting
releases, cancelling runs, changing repository access, settings, variables, or
secrets, rewriting history, and any action whose effects exceed the request.

## Which Tool To Use

| Task                                          | Use                   | Command family                       |
| --------------------------------------------- | --------------------- | ------------------------------------ |
| Issues and basic PRs                          | `fj`                  | `fj issue`, `fj pr`                  |
| Wiki pages and wiki Git clone                 | `fj`                  | `fj wiki`                            |
| Tags                                          | `fj`                  | `fj tag`                             |
| Releases and release assets                   | `fj`                  | `fj release`                         |
| Actions run list and dispatch                 | Either                | `fj actions`, `fgj actions`          |
| Actions jobs, logs, watch, rerun, cancel      | `fgj`                 | `fgj actions run`                    |
| Machine-readable list/view output             | `fgj`                 | `--json`                             |
| Unsupported Forgejo API operation             | `fgj`                 | `fgj api`                            |
| Users, organizations, teams, repository units | `fj` for dedicated UX | `fj user`, `fj org`, `fj repo units` |
| AGit pull requests                            | `fj`                  | `fj pr create --agit`                |

`fgj api` can usually reach the same server-side API operations as `fj`, but it does not provide the same dedicated workflow. Prefer `fj` for its typed Forgejo-specific commands and `fgj` when it has a better dedicated command or when direct API access is needed.

Use `fj <command> --help` or `fgj <command> --help` when unsure about a flag. Do not assume output formats are stable unless using `fgj --json`.

## Issues

Use `fj` for issue workflows:

```sh
fj issue search --repo HOST/OWNER/REPO "query"
fj issue search --repo HOST/OWNER/REPO --state all
fj issue search --repo HOST/OWNER/REPO --labels bug --assignee USERNAME
fj issue view --remote origin ISSUE
fj issue view --remote origin ISSUE comments
fj issue create --remote origin "Issue title" --body "Issue description"
fj issue create --repo HOST/OWNER/REPO "Issue title" --body-file issue.md
fj issue comment --remote origin ISSUE "Additional context"
fj issue assign --remote origin ISSUE USERNAME
fj issue edit --remote origin ISSUE title "Updated title"
fj issue edit --remote origin ISSUE body "Updated body"
fj issue edit --remote origin ISSUE labels --add documentation
fj issue close --remote origin ISSUE --with-msg "Closing because ..."
```

Omit `--body` or the positional body to edit content in the configured editor. Use `--body-file FILE` for longer text.

For JSON or an issue operation not covered by the dedicated command, use `fgj`:

```sh
fgj issue list -R HOST/OWNER/REPO --json
fgj issue view ISSUE -R HOST/OWNER/REPO --json
```

## Pull Requests

Use `fj` for normal Forgejo pull request workflows:

```sh
fj pr search --repo HOST/OWNER/REPO
fj pr search --repo HOST/OWNER/REPO --state all "query"
fj pr view PR
fj pr view PR body
fj pr view PR diff
fj pr view PR files
fj pr view PR commits
fj pr status PR
fj pr status PR --wait
fj pr create --repo HOST/OWNER/REPO \
  --base main --head feature/example \
  "Describe the change" --body-file pr-body.md
fj pr comment PR "Review comment"
fj pr checkout PR --branch-name review-PR
fj pr merge PR --method squash
fj pr close PR --with-msg "Closing because ..."
```

Prefix the title with `WIP: ` to create a draft PR. `--autofill` derives the title and body from commits. `--agit` is the Forgejo-specific workflow for creating a PR without the usual fork/push flow. Confirm immediately before using it because it can change local Git configuration and push data.

Use `fgj` when JSON output or a `fgj`-specific PR feature is more useful:

```sh
fgj pr list -R HOST/OWNER/REPO --json
fgj pr view PR -R HOST/OWNER/REPO --json
```

## Forgejo Actions

Use `fj` for a quick list of runs or to dispatch a workflow:

```sh
fj actions tasks --repo HOST/OWNER/REPO
fj actions tasks --remote origin --page 2
fj actions dispatch --repo HOST/OWNER/REPO WORKFLOW.yml REF
fj actions dispatch --remote origin WORKFLOW.yml main --inputs key=value
```

Use `fgj` for detailed run inspection. It supports workflow runs, job details, logs, watching, rerunning, and cancellation:

```sh
fgj actions run list -R HOST/OWNER/REPO
fgj actions run view RUN --verbose
fgj actions run view RUN --log
fgj actions run view RUN --job JOB --log
fgj actions run watch RUN
fgj actions run rerun RUN
fgj actions run cancel RUN
```

`fj` does not currently provide a command for viewing a run's jobs, step output, or logs. Use `fgj` for those operations rather than the Forgejo web UI or a raw API request.

Use `fgj` for structured Actions data and broader workflow management:

```sh
fgj actions run list --json
fgj actions workflow list
fgj actions workflow view WORKFLOW.yml
fgj actions workflow run WORKFLOW.yml -r REF -f key=value
fgj actions runner list
fgj actions secret list
fgj actions variable list
```

Use `fj` or `fgj` to list Actions configuration. Check the installed help before creating or deleting variables and secrets because exact flags differ:

```sh
fj actions variables list --repo HOST/OWNER/REPO
fj actions secrets list --repo HOST/OWNER/REPO
fgj actions secret list -R HOST/OWNER/REPO
fgj actions variable list -R HOST/OWNER/REPO
```

Never print, paste, or place secret values in command history, logs, Git, or chat.

## Tags

Use `fj` for the dedicated tag workflow:

```sh
fj tag list --repo HOST/OWNER/REPO
fj tag view --repo HOST/OWNER/REPO TAG
fj tag create --repo HOST/OWNER/REPO TAG --branch BRANCH
fj tag create --repo HOST/OWNER/REPO TAG --body "Annotated tag message"
```

`fgj` has no dedicated tag command. Use its API passthrough when JSON or scripting is needed:

```sh
fgj api repos/OWNER/REPO/tags
```

Use `fj tag delete --help` before deleting a tag. Tag changes may trigger workflows and alter repository history.

## Releases

Use `fj` for the dedicated release workflow and asset operations:

```sh
fj release list --repo HOST/OWNER/REPO
fj release list --repo HOST/OWNER/REPO --include-prerelease --include-draft
fj release view --repo HOST/OWNER/REPO RELEASE
fj release view --repo HOST/OWNER/REPO --by-tag TAG
fj release create --repo HOST/OWNER/REPO RELEASE --tag TAG
fj release create --repo HOST/OWNER/REPO RELEASE --create-tag
fj release create --repo HOST/OWNER/REPO RELEASE \
  --tag TAG --body "Release notes" --attach dist/artifact.tar.gz
```

`fgj` supports common release listing, viewing, creating, and uploading, with JSON support:

```sh
fgj release list -R HOST/OWNER/REPO --json
fgj release view RELEASE -R HOST/OWNER/REPO --json
fgj release create RELEASE -R HOST/OWNER/REPO -t TAG -n "Release notes"
fgj release upload RELEASE -R HOST/OWNER/REPO dist/artifact.tar.gz
```

Use `--draft` or `--prerelease` as appropriate. Inspect `fj release edit`, `fj release delete`, `fj release asset --help`, or the corresponding `fgj` help before changing or removing an existing release.

## Wiki

Use `fj` for wiki operations. It has both page-oriented commands and a Git clone workflow:

```sh
fj wiki contents --repo HOST/OWNER/REPO
fj wiki view --repo HOST/OWNER/REPO PAGE
fj wiki clone --repo HOST/OWNER/REPO --path ./REPO-wiki
fj wiki clone --repo HOST/OWNER/REPO --ssh --path ./REPO-wiki
```

Edit pages in the cloned Git repository, then commit and push with Git. `fgj` has no dedicated wiki command; its API passthrough does not replace the wiki Git workflow.

## API And JSON

Use `fgj` when a dedicated command is missing or when output must be machine-readable:

```sh
fgj repo view HOST/OWNER/REPO --json
fgj actions run list -R HOST/OWNER/REPO --json
fgj api repos/OWNER/REPO/commits/SHA/status | jq
```

`fgj api` is an authenticated Forgejo REST API passthrough. Use the Forgejo API documentation for endpoint and permission details. Treat API mutations with the same care as dedicated mutating commands.

## Targeting And Safety

- Prefer explicit `--repo HOST/OWNER/REPO` or `--remote NAME` when multiple remotes or repositories are in play.
- Use read-only commands such as search, view, status, list, and contents before mutating commands.
- Recheck the repository, branch, issue/PR number, run ID, job ID, tag, or release name before remote changes.
- Treat merge, close, tag, release, dispatch, rerun, cancel, delete, and Actions configuration commands as mutating operations.
- Never expose credentials, private keys, or Actions secret values in arguments, output, files, or chat.
- Use `--style minimal` with `fj` for cleaner piped output, but do not treat it as a stable machine-readable format.
