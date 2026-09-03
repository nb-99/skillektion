---
name: confluence-workflow
description: Fetch and search Telekom Confluence wiki pages. Use whenever a wiki.telekom.de link or pageId appears, or when asked to look up, read, or search Confluence/wiki content. Covers fetching by pageId, search-then-fetch, and the confirm-before-write rule.
---

# Confluence workflow

Trigger: links like `https://wiki.telekom.de/pages/viewpage.action?pageId=3691938421`,
or any request to read/search the wiki.

## Fetching a known page

- Extract the `pageId` from the URL and fetch with the telecontext
  `confluence_get_page` tool.

## Finding a page

1. Use `confluence_search` first to locate candidate pages.
2. Then fetch the full content of the best match with `confluence_get_page`
   using its `pageId`.

Don't rely on the search snippet alone — fetch the full page before reasoning
about its content.

## Writing / mutating

- An explicit user request that names the Confluence target and a bounded write
  action authorizes that action.
- Otherwise, present the exact change and ask for confirmation before writing.
- Always confirm immediately before destructive, irreversible,
  privilege-changing, or materially broader work, including deletion, moving
  page trees, access changes, and bulk edits.
- Recheck the space, page id, and mutation before applying it.
