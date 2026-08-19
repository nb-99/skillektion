# Transcript Sources

Use supported exports and explicit user selection. Client history formats and
paths change; inspect current command help or official documentation before
collecting data.

## OpenCode

OpenCode provides the preferred automated path:

```sh
opencode --version
opencode session list --format json
opencode export SESSION_ID --sanitize
```

Run `session list` from the selected project directory. Filter its JSON by the
confirmed date range when needed, first inspecting the current output to locate
its timestamp field. Then ask the user to select session IDs before exporting
them. Always use `--sanitize`, while treating its redaction as best-effort.
Record the chosen binary version because multiple OpenCode installations can
maintain separate histories.

Use only `session list` and `export` operations. Treat compacted or pruned
history as incomplete.

## GitHub Copilot In VS Code

Ask the user to run **Chat: Export Chat...** for selected sessions and provide
the resulting JSON files. Use those files rather than Copilot's internal
session store.

## Claude Code

Prefer user-selected exports. An adapter may use the supported Agent SDK
`listSessions()` and `getSessionMessages()` APIs after showing the selected
sessions. Verify these names against the installed SDK documentation and use
only the selected workspace.

## Codex CLI

Codex does not provide a stable bulk transcript export command. Accept
user-selected files from `${CODEX_HOME:-~/.codex}/sessions` only as an
experimental input. Treat the JSONL record schema as version-specific.

## Generic Exports

For any other client, accept user-selected JSON, JSONL, or Markdown exports.
Stop when roles or session boundaries cannot be determined reliably.
