# `fgj` command reference

Exact templates for `fgj` (romaintb/fgj), the gh-style Forgejo CLI for
scripting, JSON output, Actions run inspection, and generic API access.
Templates follow fgj 0.6.x; features marked "0.5.0+" or "0.6.0+" need that
release or newer. Check `fgj <command> --help` on the installed version.

- README with every command and example:
  `https://codeberg.org/romaintb/fgj` — prefer the tag matching the installed
  release (`.../src/tag/v0.6.1/README.md`) over main.
- Changelog: `https://codeberg.org/romaintb/fgj/src/branch/main/CHANGELOG.md`.
- Source: `https://codeberg.org/romaintb/fgj` (Go, `cmd/*.go`).

Replace `HOST`, `OWNER/REPO`, `PR`, `ISSUE`, `RUN`, `JOB`, `QUERY`, and `NAME`
with target values.

## Targeting

- Prefer `-R HOST/OWNER/REPO` (0.6.0+) or `--hostname HOST -R OWNER/REPO` to
  make the server explicit. `-R` also works alone when the checkout identifies
  the host.
- Hostname resolution: `-R` host part or `--hostname`, then `FGJ_HOST`, then
  the Git remote, then the single configured host, then `codeberg.org`.
- List commands accept `--limit`/`-L`. `repo list`, `issue list`, `pr list`,
  `milestone list`, and `actions secret list` walk API pages up to the limit
  (default 30, `0` for all); `actions run list` and `workflow list` default to
  20 without page walking.
- `--json` works on all list and view commands. Minimal text output is not a
  stable format; select fields from JSON. `fgj issue view` wraps the object in
  `issue`; run and runner lists are arrays.

## Authentication and configuration

```sh
fgj auth login --hostname HOST                         # add --api-protocol http for plain HTTP
fgj auth login --hostname HOST --git-protocol ssh      # -p ssh: protocol for pr checkout, repo create --clone
fgj auth status                                        # per-host login state; shows api_protocol when not https
fgj auth token                                         # prints a stored token; run only on request, never quote output
fgj auth logout --hostname HOST
fgj completion zsh                                     # also: bash, fish, powershell
fgj manpages --dir ~/.local/share/man/man1
```

Token resolution order: `FGJ_TOKEN`, the host's `token_cmd`, then the stored
token. Prefer `token_cmd` over a stored plaintext token; it runs a shell
command, for example from a password manager, and takes the first line of its
output:

```yaml
hosts:
  HOST:
    user: USERNAME
    token_cmd: pass show forgejo/HOST
```

Config lives at `~/.config/fgj/config.yaml` (or `$XDG_CONFIG_HOME/fgj/config.yaml`;
`--config FILE` selects another file). A token sent over plain HTTP travels in
cleartext; store `api_protocol` per host instead of in shell profiles or
`FGJ_API_PROTOCOL`.

## Repositories

```sh
fgj repo view HOST/OWNER/REPO --json
fgj repo list                                          # own repositories
fgj repo list OWNER --hostname HOST                    # another user's or an org's repositories
fgj repo rename NEW-NAME -R HOST/OWNER/REPO            # prompts; --yes skips; updates local origin
fgj repo create NAME --hostname HOST --private --description "..." \
  --add-readme -g Go -l MIT
fgj repo clone HOST/OWNER/REPO                         # -p ssh for SSH URLs
fgj repo fork HOST/OWNER/REPO
```

`repo rename` is a material change and rewrites the local `origin` remote;
confirm before running it. `repo create --clone` clones after creating and
uses the stored `git_protocol`.

## Issues

```sh
fgj issue list -R HOST/OWNER/REPO --json
fgj issue list -R HOST/OWNER/REPO -l bug,enhancement -a '@me' -L 100
fgj issue list -R HOST/OWNER/REPO -S 'QUERY' --state all
fgj issue view ISSUE -R HOST/OWNER/REPO --json | jq '.issue | {title, updated_at, body}'
fgj issue create -R HOST/OWNER/REPO -t "Title" -F - <<'EOF'   # body from stdin; -F FILE for a file
Body text.
EOF
fgj issue create -R HOST/OWNER/REPO -t "Title" -l bug -l enhancement -m MILESTONE
fgj issue comment ISSUE -b "Additional context" -R HOST/OWNER/REPO
fgj issue comment ISSUE -F /abs/path/comment.md -R HOST/OWNER/REPO
fgj issue close ISSUE -c "Closing because ..." -R HOST/OWNER/REPO
fgj issue reopen ISSUE -c "Reopening because ..." -R HOST/OWNER/REPO   # 0.5.0+
fgj issue edit ISSUE -t "New title" -R HOST/OWNER/REPO
fgj issue edit ISSUE -F /abs/path/new-body.md -R HOST/OWNER/REPO
fgj issue edit ISSUE --add-assignee '@me' --remove-assignee USERNAME -R HOST/OWNER/REPO
fgj issue edit ISSUE -m MILESTONE --remove-milestone -R HOST/OWNER/REPO   # --remove-milestone alone
fgj issue edit ISSUE --add-label docs --remove-label bug -R HOST/OWNER/REPO
```

`-F/--body-file` takes a file; `-F -` reads standard input. `@me` means the
authenticated user. `issue edit --body ""` clears the body.

## Labels and milestones

Deletions prompt for confirmation; `--yes` skips it and needs prior
confirmation under the authorization rules.

```sh
fgj label list -R HOST/OWNER/REPO --json
fgj label create NAME -R HOST/OWNER/REPO -c RRGGBB -d "Description" [--exclusive] [-f]
fgj label edit NAME -R HOST/OWNER/REPO -n NEW-NAME -c COLOR
fgj label delete NAME -R HOST/OWNER/REPO

fgj milestone list -R HOST/OWNER/REPO --state all
fgj milestone create "v1.0" -R HOST/OWNER/REPO -d "Description" --due 2026-06-30
fgj milestone edit "v1.0" -R HOST/OWNER/REPO --title "v1.1" --state closed
fgj milestone delete "v1.0" -R HOST/OWNER/REPO
```

Label colors accept `#`-prefixed hex and named colors. `-f/--force` on
`create` updates an existing label or milestone instead of failing.

## Pull requests

```sh
fgj pr list -R HOST/OWNER/REPO --json
fgj pr view PR -R HOST/OWNER/REPO --json
fgj pr status -R HOST/OWNER/REPO --json                # 0.5.0+: current branch, created, assigned
fgj pr diff PR -R HOST/OWNER/REPO --patch              # 0.6.0+; --name-only lists changed files
fgj pr diff -R HOST/OWNER/REPO                         # PR for the current branch
fgj pr create -R HOST/OWNER/REPO -t "Title" -B main -b "Body"
fgj pr create -R HOST/OWNER/REPO -t "Title" -F /abs/path/pr-body.md   # -F - reads stdin
fgj pr create -R HOST/OWNER/REPO -t "Title" -H feature/example         # default head: current branch
fgj pr comment PR -b "Review comment" -R HOST/OWNER/REPO
fgj pr checkout PR -R HOST/OWNER/REPO                  # 0.5.0+; -b NAME, --force, --detach
fgj pr edit PR -t "New title" --add-label bug --add-assignee '@me' -R HOST/OWNER/REPO
fgj pr edit PR --add-reviewer USERNAME -R HOST/OWNER/REPO
fgj pr close PR -c "Closing because ..." -R HOST/OWNER/REPO
fgj pr close PR -c "Closing because ..." -d -R HOST/OWNER/REPO        # -d deletes the remote branch
fgj pr reopen PR -c "Reopening because ..." -R HOST/OWNER/REPO        # 0.5.0+
fgj pr merge PR --merge-method squash -R HOST/OWNER/REPO
```

`pr checkout` mutates the local Git state. `-d` on close safely skips fork
branches; confirm `pr close -d` and every merge immediately before running
them. `pr merge` reports non-200 API responses as errors rather than claiming
success (0.6.0+ fix).

## Actions

Use the API run ID from metadata, not the repository display index; the two
are not interchangeable arguments. Job IDs identify jobs; the job log endpoint
rejects a job's task ID.

```sh
fgj actions run list -R HOST/OWNER/REPO --json | jq '[.[] | select(.workflow_id == "WORKFLOW.yml")][0:4]'
fgj actions run view RUN -R HOST/OWNER/REPO --verbose   # jobs without logs
fgj actions run view RUN --log                          # logs of all jobs
fgj actions run view RUN --job JOB --log                # logs of one job
fgj actions run view RUN --json                         # run plus jobs; --json blocks --log/--log-failed
fgj actions run watch RUN -R HOST/OWNER/REPO            # -i/--interval, default 5s
fgj actions run rerun RUN -R HOST/OWNER/REPO
fgj actions run cancel RUN -R HOST/OWNER/REPO
```

The `--log-failed` flag exists but currently also prints all logs; do not rely
on it for failure-only output. If fetching job logs returns HTTP 404, stop
equivalent requests and report the logs unavailable through that path; the
failure does not prove that all versions lack log support.

```sh
fgj actions workflow list -R HOST/OWNER/REPO --json
fgj actions workflow view WORKFLOW.yml -R HOST/OWNER/REPO --json
fgj actions workflow run WORKFLOW.yml -r REF -f key=value -R HOST/OWNER/REPO
fgj actions workflow enable WORKFLOW.yml -R HOST/OWNER/REPO    # Forgejo 15.0+ / Gitea 1.24+
fgj actions workflow disable WORKFLOW.yml -R HOST/OWNER/REPO

fgj actions runner list --visible -R HOST/OWNER/REPO           # --visible adds inherited runners
fgj actions runner register RUNNER-NAME -R HOST/OWNER/REPO     # prints credentials; never quote output
fgj actions runner register RUNNER-NAME --ephemeral --json -R HOST/OWNER/REPO
fgj actions runner delete RUNNER-ID -R HOST/OWNER/REPO

fgj actions secret list -R HOST/OWNER/REPO -L 100
fgj actions secret create MY_SECRET -R HOST/OWNER/REPO         # reads the value from stdin
fgj actions secret delete MY_SECRET -R HOST/OWNER/REPO

fgj actions variable list -R HOST/OWNER/REPO
fgj actions variable get MY_VAR -R HOST/OWNER/REPO
fgj actions variable create MY_VAR "value" -R HOST/OWNER/REPO
fgj actions variable update MY_VAR "new value" -R HOST/OWNER/REPO
fgj actions variable delete MY_VAR -R HOST/OWNER/REPO
```

`workflow enable/disable`, `runner register/delete`, and secret/variable
changes mutate Actions setup; confirm first. Never print, paste, or place
secret values or runner credentials in command history, logs, Git, or chat.

## Releases

```sh
fgj release list -R HOST/OWNER/REPO --json
fgj release view RELEASE -R HOST/OWNER/REPO --json      # RELEASE may be "latest"
fgj release create RELEASE -R HOST/OWNER/REPO -t TAG -n "Notes" [--draft] [--prerelease]
fgj release create RELEASE -R HOST/OWNER/REPO --notes-file - <<'EOF'   # notes from stdin
Notes text.
EOF
fgj release upload RELEASE -R HOST/OWNER/REPO dist/file.tar.gz [--clobber]
fgj release delete RELEASE -R HOST/OWNER/REPO           # prompts; --yes skips; keeps the Git tag
```

## API passthrough

`fgj api` (0.5.0+) sends an authenticated request to any Forgejo REST endpoint
without a dedicated command, such as branch protections or combined commit
status. Output is verbatim JSON; pipe it to `jq`. The `/api/v1` prefix is
added when omitted. `-f` sends string fields, `-F` sends typed fields (`true`,
numbers, `@file`), `--input` sends a raw body, `-i` includes response headers,
`--paginate --slurp` walks and wraps pages.

```sh
fgj api repos/OWNER/REPO | jq .default_branch
fgj api repos/OWNER/REPO/commits/SHA/status
fgj api repos/OWNER/REPO/branch_protections
fgj api --paginate --slurp repos/OWNER/REPO/commits | jq 'add | length'
fgj api -X PATCH repos/OWNER/REPO/issues/N -F state=closed
```

API mutations follow the same authorization rules as dedicated commands.
