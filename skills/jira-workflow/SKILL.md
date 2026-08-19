---
name: jira-workflow
description: Fetch and work with Jira issues. Use whenever a Jira ticket id like DHEI-1234 or SDDHEI-1234 appears, or when asked to look up, read, or update a Jira issue. Covers reading issues with comments/attachments and the confirm-before-write rule.
---

# Jira workflow

Trigger: any Jira ticket id, e.g. `DHEI-1234`, `SDDHEI-1234`.

## Reading an issue

1. Use the `jira_get_issue` tool to fetch the issue by its id.
2. **Always also fetch its comments and attachments** — they usually hold the
   decisive context (acceptance criteria, logs, screenshots, decisions).
3. Summarize concisely: title, status, description intent, and the key points
   from comments/attachments. Sacrifice grammar for concision.

## Writing / mutating

- Always ask for explicit confirmation before any write action (creating,
  transitioning, commenting, assigning, editing).
- Present the exact change you intend to make, then wait for a yes.

## Linking commits / PRs

- Reference the ticket in commit footers: `Refs: DHEI-1234`.
- Don't transition tickets automatically as a side effect of other work.
