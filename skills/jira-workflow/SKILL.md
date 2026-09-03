---
name: jira-workflow
description: Fetch and work with Jira issues. Use whenever a Jira ticket id like DHEI-1234 or SDDHEI-1234 appears, or when asked to look up, read, or update a Jira issue. Covers reading issues with comments/attachments and the confirm-before-write rule.
---

# Jira workflow

Trigger: any Jira ticket id, e.g. `DHEI-1234`, `SDDHEI-1234`.

## Reading an issue

1. Use the `jira_get_issue` tool to fetch the issue by its id.
2. Fetch its comments and inspect attachment metadata such as filename, media
   type, size, author, and creation time.
3. Fetch only attachments relevant to the request or discussion. Prefer items
   referenced by the description or comments, then use filenames, media types,
   and recency to select any others. Do not fetch every attachment by default.
4. Summarize concisely: title, status, description intent, and the key points
   from comments and relevant attachments. Sacrifice grammar for concision.

## Writing / mutating

- An explicit user request that names the Jira issue and a bounded write action
  authorizes that action.
- Otherwise, present the exact change and ask for confirmation before writing.
- Always confirm immediately before destructive, irreversible,
  privilege-changing, or materially broader work, including deletion, access
  changes, and transitions or bulk edits beyond the stated request.
- Recheck the issue id and mutation before applying it.

## Linking commits / PRs

- Reference the ticket in commit footers: `Refs: DHEI-1234`.
- Don't transition tickets automatically as a side effect of other work.
