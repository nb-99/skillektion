---
name: technical-writing
description: Structure and review documentation, READMEs, RFCs, changelogs, and pull-request descriptions. Use when drafting or revising a technical document or PR body, to pick its document type, organize it, and keep it reviewable.
---

# Technical Writing

Write for a tired engineer reading once. This skill covers document structure;
sentence-level style comes from the global writing rules and `unslop`.

## Choose The Document Mode

Keep one primary mode per document; split and link when modes conflict.

- **Tutorial:** learning through visible, ordered results.
- **How-to:** concise steps toward a practical goal for a competent reader.
- **Reference:** complete, dry facts organized like the system described.
- **Explanation:** bounded understanding, rationale, context, and trade-offs.

## Organize

- Address the reader as "you" when appropriate and use present tense.
- Put the common case first and exceptions after it.
- Use headings that carry the point, numbered lists for sequences, and parallel
  bullets for unordered sets.
- Use exact symbols, paths, flags, and commands from the repository.
- Break up long noun strings and give every clause its own verb.

## Keep pull requests easy to review

Write the pull-request body as a concise briefing. Keep the problem, change,
verification results, and material risks inline. Link bulky logs, commit lists,
and supporting measurements instead of copying them into the body. Include a
small table when it helps the reviewer decide; keep necessary evidence visible.

## Review

1. Does the document have one primary mode?
2. Are symbols, paths, commands, counts, and output examples true now?
3. Does the tone fit the repository and intended reader?
4. For pull-request bodies, are the problem, change, verification, and material
   risks inline, with bulky supporting evidence linked?

Use `unslop`, when available, as an optional final style pass only when its
opinionated house style fits the requested voice. The work is complete when
every applicable check passes or the remaining exception is stated explicitly.
