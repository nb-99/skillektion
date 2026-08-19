---
name: technical-writing
description: Write or review documentation, READMEs, RFCs, changelogs, pull-request descriptions, and commit prose for structure, clarity, precision, and unambiguous language. Use when drafting or revising technical prose.
---

# Technical Writing

Write for a tired engineer reading once. Use four layers: document purpose,
reader-directed sentences, controlled sentence load, and unambiguous syntax.

## Choose The Document Mode

Keep one primary mode per document; split and link when modes conflict.

- **Tutorial:** learning through visible, ordered results.
- **How-to:** concise steps toward a practical goal for a competent reader.
- **Reference:** complete, dry facts organized like the system described.
- **Explanation:** bounded understanding, rationale, context, and trade-offs.

## Write Directly

- Address the reader as "you" when appropriate and use present tense.
- Name the actor and action. Prefer active voice unless the actor is irrelevant.
- Write instructions as commands and put conditions before guarded steps.
- Put the common case first and exceptions after it.
- Use headings that carry the point, numbered lists for sequences, and parallel
  bullets for unordered sets.
- Use exact symbols, paths, flags, and commands from the repository.

## Control Sentence Load

- Keep one instruction or one main thought per sentence.
- Split a sentence when the reader must backtrack to parse it.
- Use one stable term for each concept and one verb for each repeated action.
- Prefer short everyday words unless a technical term is more precise.
- Remove filler, vague attribution, invented metaphor, promotional language,
  and claims that could describe any project unchanged.
- Vary sentence length without sacrificing precision.

## Remove Ambiguity

- Put "only", "not", and other modifiers next to what they modify.
- Make every pronoun point to one obvious noun; repeat the noun when needed.
- Break up long noun strings and give every clause its own verb.
- Keep articles and conjunctions when they prevent a second reading.
- Use one name for each thing throughout the document.
- Prefer periods to punctuation that hides multiple thoughts in one sentence.

## Review

1. Does the document have one primary mode?
2. Does every instruction name the action and place its condition first?
3. Does any sentence carry two instructions or unrelated thoughts?
4. Can any word be removed without losing meaning or precision?
5. Can modifiers, pronouns, conjunctions, or noun strings be read two ways?
6. Does each concept keep one name?
7. Are symbols, paths, commands, counts, and output examples true now?
8. Does the tone fit the repository and intended reader?

Use `unslop`, when available, as an optional final style pass only when its
opinionated house style fits the requested voice. The work is complete when
every applicable check passes or the remaining exception is stated explicitly.
