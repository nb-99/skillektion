---
name: forgejo-cli
description: Use fj and fgj for everyday Forgejo issues, pull requests, Actions, tags, releases, and wiki workflows.
---

# Forgejo CLI tools

## Authorization

Read freely. An explicit user request that names the Forgejo target and a
bounded write action authorizes that action. Otherwise, show the exact mutation
and ask for confirmation before running it.

Always confirm immediately before destructive, irreversible,
privilege-changing, or materially broader work. This includes merging or
closing pull requests, deleting content or tags, publishing or deleting
releases, cancelling runs, changing repository access, settings, variables, or
secrets, rewriting history, and any action whose effects exceed the request.

## Common commands

Prefer `fj --style minimal` for normal operations and `fgj` for structured output.
Replace `HOST/OWNER/REPO`, `PR`, `ISSUE`, and `QUERY` with your target values.
Commands without explicit targeting infer the repository from the checkout:

```sh
fj --style minimal pr view PR body
fj --style minimal pr view PR diff
fj --style minimal pr status PR
fj --style minimal pr status PR --wait
fj --style minimal issue view --remote origin ISSUE
fj --style minimal issue search --repo HOST/OWNER/REPO --state all 'QUERY'
```

Run independent reads in parallel. When the harness supports background commands
with completion notifications, run `status --wait` in the background and await
completion without polling. Distinguish pending policy gates from CI checks and
merge conflicts. A pending policy gate does not by itself indicate broken CI.

Search existing issues before creating one. With explicit authorization for the
target and issue creation, use an absolute body-file path, then read the created
issue back once:

```sh
fj --style minimal issue create --repo HOST/OWNER/REPO 'Issue title' --body-file /absolute/path/issue.md
```

Only after successful required checks, verification of mergeability, and
immediate confirmation of the merge, use the rebase form:

```sh
fj --style minimal pr merge PR --method rebase
```

## Tool choice and targeting

Both tools infer the repository from the checkout where possible. Use
`--repo HOST/OWNER/REPO` or `--remote NAME` with `fj`; with `fgj`, prefer
`--hostname HOST -R OWNER/REPO` to make the server explicit.

| Task                                          | Use                   | Command family                       |
| --------------------------------------------- | --------------------- | ------------------------------------ |
| Issues and basic PRs                          | `fj`                  | `fj issue`, `fj pr`                  |
| Wiki pages and wiki Git clone                 | `fj`                  | `fj wiki`                            |
| Tags                                          | `fj`                  | `fj tag`                             |
| Releases and release assets                   | `fj`                  | `fj release`                         |
| Actions run list and dispatch                 | Either                | `fj actions`, `fgj actions`          |
| Actions jobs, logs, watch, rerun, cancel        | `fgj`                 | `fgj actions run`                    |
| Machine-readable list/view output             | `fgj`                 | `--json`                             |
| Users, organizations, teams, repository units | `fj` for dedicated UX | `fj user`, `fj org`, `fj repo units` |
| AGit pull requests                            | `fj`                  | `fj pr create --agit`                |

Use command help when unsure about a flag. Before an API fallback, check
`fgj --help` once for an `api` subcommand. If the installed help lacks it, use a
supported dedicated command or another authenticated read-only path if needed.
Minimal text is not a stable machine-readable format; inspect the JSON shape
before selecting fields.

## Issues

Use `fj` for issue workflows:

```sh
fj issue search --repo HOST/OWNER/REPO "QUERY"
fj issue search --repo HOST/OWNER/REPO --state all
fj issue search --repo HOST/OWNER/REPO --labels bug --assignee USERNAME
fj issue view --remote origin ISSUE
fj issue view --remote origin ISSUE comments
fj issue create --remote origin "Issue title" --body "Issue description"
fj issue comment --remote origin ISSUE "Additional context"
fj issue assign --remote origin ISSUE USERNAME
fj issue edit --remote origin ISSUE title "Updated title"
fj issue edit --remote origin ISSUE body "Updated body"
fj issue edit --remote origin ISSUE labels --add documentation
fj issue close --remote origin ISSUE --with-msg "Closing because ..."
```

Omit `--body` or the positional body to edit content in the configured editor. Use `--body-file FILE` for longer text.

For JSON, use `fgj`. Issue views wrap the object in `issue`, rather than returning
bare issue fields. Verify the shape for your installed version:

```sh
fgj issue list --hostname HOST -R OWNER/REPO --json
fgj issue view ISSUE --hostname HOST -R OWNER/REPO --json | jq '.issue | {title, updated_at, body}'
```

## Pull requests

Use `fj` for normal Forgejo pull request workflows:

```sh
fj pr search --repo HOST/OWNER/REPO
fj pr search --repo HOST/OWNER/REPO --state all "QUERY"
fj pr view PR
fj pr view PR files
fj pr view PR commits
fj pr create --repo HOST/OWNER/REPO \
  --base main --head feature/example \
  "Describe the change" --body-file pr-body.md
fj pr comment PR "Review comment"
fj pr checkout PR --branch-name review-PR
fj pr close PR --with-msg "Closing because ..."
```

Prefix the title with `WIP: ` to create a draft PR. `--autofill` derives the title and body from commits. `--agit` is the Forgejo-specific workflow for creating a PR without the usual fork/push flow. Confirm immediately before using it because it can change local Git configuration and push data.

Use `fgj` when JSON output or a `fgj`-specific PR feature is more useful:

```sh
fgj pr list --hostname HOST -R OWNER/REPO --json
fgj pr view PR --hostname HOST -R OWNER/REPO --json
```

## Forgejo Actions

Use `fj` for a quick list of runs or to dispatch a workflow:

```sh
fj actions tasks --repo HOST/OWNER/REPO
fj actions tasks --remote origin --page 2
fj actions dispatch --repo HOST/OWNER/REPO WORKFLOW.yml REF
fj actions dispatch --remote origin WORKFLOW.yml main --inputs key=value
```

Use `fgj` for detailed run inspection. Filter JSON in the initial command rather
than dumping the full run history. Run and PR lists are arrays; verify the shape
for your installed version:

```sh
fgj actions run list --hostname HOST -R OWNER/REPO --json | jq '[.[] | select(.workflow_id == "WORKFLOW.yml")][0:4]'
fgj actions run view RUN --verbose
fgj actions run view RUN --log
fgj actions run view RUN --job JOB --log
fgj actions run watch RUN
fgj actions run rerun RUN
fgj actions run cancel RUN
```

Use the API run ID returned in metadata, not the repository run index or display
number. A run's API ID and repository display index can differ and are not
interchangeable command arguments. Job IDs identify jobs.

If fetching job logs returns HTTP 404, stop equivalent requests and report the
logs unavailable through that path. Metadata may still be available through
`--verbose`; use another read-only path only if needed. A log-fetch failure does
not prove that all versions lack log support.

Use `fgj` for structured Actions data and broader workflow management:

```sh
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
fgj actions secret list --hostname HOST -R OWNER/REPO
fgj actions variable list --hostname HOST -R OWNER/REPO
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

Prefer `fj` for tags. If the installed `fgj` help lacks a dedicated tag command,
use an API fallback only after the capability check above.

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
fgj release list --hostname HOST -R OWNER/REPO --json
fgj release view RELEASE --hostname HOST -R OWNER/REPO --json
fgj release create RELEASE --hostname HOST -R OWNER/REPO -t TAG -n "Release notes"
fgj release upload RELEASE --hostname HOST -R OWNER/REPO dist/artifact.tar.gz
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

Edit pages in the cloned Git repository, then commit and push with Git. If the
installed `fgj` help lacks a dedicated wiki command, use `fj`. An API fallback
does not replace the wiki Git workflow.

## Targeting and safety

- Prefer explicit `--repo HOST/OWNER/REPO` or `--remote NAME` when multiple remotes or repositories are in play.
- Use read-only commands such as search, view, status, list, and contents before mutating commands.
- Recheck the repository, branch, issue/PR number, run ID, job ID, tag, or release name before remote changes.
- Treat merge, close, tag, release, dispatch, rerun, cancel, delete, and Actions configuration commands as mutating operations.
- Treat API mutations with the same authorization rules as dedicated commands.
- Never expose credentials, private keys, or Actions secret values in arguments, output, files, or chat.
