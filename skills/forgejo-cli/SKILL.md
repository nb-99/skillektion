---
name: forgejo-cli
description: Forgejo workflows from the command line. Use when working with Forgejo or Codeberg repositories, issues, pull requests, Actions, releases, tags, or wikis; tells you how Forgejo does things and whether to use fj or fgj, with exact command templates in references/.
---

# Forgejo CLI tools

Two CLIs cover Forgejo (and Codeberg) from the terminal:

- `fj` (forgejo-contrib/forgejo-cli): dedicated UX for issues, pull requests,
  milestones, releases, tags, wiki, repositories, users, and organizations.
  Interactive editor prompts, AGit support.
- `fgj` (romaintb/fgj): gh-style scripting with `--json`, filters, and
  pagination, plus Actions run and job inspection, generic REST access, and
  repository management.

Exact, ready-to-run command templates per CLI live in the references. Read one
before running anything beyond a simple view:

- Every `fj` command family with verified flags: [references/fj.md](references/fj.md)
- Every `fgj` command, JSON shapes, and version notes: [references/fgj.md](references/fgj.md)

## Authorization

Read freely. An explicit user request that names the Forgejo target and a
bounded write action authorizes that action. Otherwise, show the exact mutation
and ask for confirmation before running it.

Always confirm immediately before destructive, irreversible,
privilege-changing, or materially broader work. This includes merging or
closing pull requests, deleting content or tags, publishing or deleting
releases, cancelling runs, renaming repositories, enabling or disabling
workflows, registering or deleting runners, changing repository access,
settings, variables, or secrets, rewriting history, and any action whose
effects exceed the request.

## How Forgejo does things

Forgejo-specific facts that change how you work:

- Issues and pull requests share one index namespace per repository, so
  `#123` can be either. Recheck what a number refers to before mutating it.
- A repository's features are "units": issues, PRs, Actions, wiki, packages,
  projects, releases. They can be enabled or disabled per repository.
- The wiki is a separate Git repository alongside the code. Page-oriented
  commands exist, but real edits happen through a clone, commit, and push.
- Forgejo Actions workflows live in `.gitea/workflows/` or
  `.forgejo/workflows/`. A run contains jobs; a run's API ID differs from its
  repository display index and the two are not interchangeable arguments.
- `workflow_dispatch` runs need a workflow that declares the trigger. Jobs run
  on registered runners; runners can belong to a repository, its owner, or the
  instance.
- Labels and milestones are per-repository, not per-instance. Namespaced
  labels (`priority/high`) can be marked exclusive within their namespace.
- Multiple instances are normal (Codeberg, self-hosted, Gitea-compatible).
  Name the server explicitly when several are configured or no checkout is
  present.
- AGit is the Forgejo-specific flow for opening a pull request without a
  fork, by pushing refs with Git options.

## Tool choice

Pick by task, not habit:

| Task                                             | Use    | Command family                              |
| ------------------------------------------------ | ------ | ------------------------------------------- |
| Interactive issue, PR, milestone, label workflows | `fj`   | `fj issue`, `fj pr`, `fj milestone`, `fj repo labels` |
| Tags, releases, wiki                             | `fj`   | `fj tag`, `fj release`, `fj wiki`           |
| Users, organizations, teams, repository units    | `fj`   | `fj user`, `fj org`, `fj repo units`        |
| AGit pull requests                               | `fj`   | `fj pr create --agit`                       |
| Machine-readable list and view output            | `fgj`  | `--json`                                    |
| PR status, diff, checkout, lifecycle scripting   | `fgj`  | `fgj pr status`, `diff`, `checkout`, `close`|
| Actions run and job inspection, logs, rerun      | `fgj`  | `fgj actions run`                           |
| Runners, secrets, variables, workflow toggles    | `fgj`  | `fgj actions runner`, `secret`, `variable`  |
| Repository view, list, create, rename            | `fgj`  | `fgj repo`                                  |
| Any other REST endpoint                          | `fgj`  | `fgj api`                                   |

Either tool works for simple issue and PR reads; prefer `fgj` when a script
parses the result.

Targeting: both tools infer the repository from the checkout. With `fj`, use
`-r HOST/OWNER/REPO`, `-R REMOTE`, or `-H HOST`; with `fgj`, use
`-R HOST/OWNER/REPO` (0.6.0+) or `--hostname HOST -R OWNER/REPO`. When piping
`fj` output into a script, keep the global `--style minimal` flag.

Version reality: newer `fgj` commands (`api`, `pr checkout`, `pr status`,
`pr diff`, issue assignee and milestone editing) need fgj 0.5.0 or 0.6.0 or
later, and `fj` gains subcommands between releases. Check the installed help
before relying on a flag; the references mark version requirements.

## Workflow advice

- Run independent reads in parallel. When the harness supports background
  commands with completion notifications, run `status --wait` in the
  background and await completion without polling.
- Distinguish pending policy gates from CI failures and merge conflicts. A
  pending policy gate does not by itself indicate broken CI.
- Search existing issues before creating one. Create issues with an absolute
  body-file path, then read the created issue back once.
- Merge a PR only after required checks pass, mergeability is confirmed, and
  the user confirmed the merge immediately before. Use the rebase or squash
  form only if the project expects it.
- Filter JSON in the initial command with `jq` rather than dumping full run or
  issue history. Verify the JSON shape of your installed version before
  selecting fields.
- Treat API mutations like dedicated commands: same authorization rules.

## Targeting and safety

- Prefer explicit targeting (`-r`, `-R`, `-H`, `--hostname`) when multiple
  remotes or repositories are in play.
- Use read-only commands such as search, view, status, list, and contents
  before mutating commands.
- Recheck the repository, branch, issue/PR number, run ID, job ID, tag, or
  release name before remote changes.
- Never expose credentials, private keys, Actions secret values, or runner
  credentials in arguments, output, files, or chat.
