---
name: why
description: Investigate why code or a design has its current shape using source history and available organizational evidence. Use for rationale, trade-offs, regressions, postmortems, thresholds, and historical design questions.
---

# Why

Investigate intent as a historical question. Code proves mechanics, not motive.

## Evidence Rules

- Collect evidence before choosing a narrative.
- Cite claims about intent to commits, pull requests, issues, documents, chat
  links, incidents, dashboards, or comments.
- Label uncited claims as inference.
- Surface contradictions and competing hypotheses.
- State unavailable sources and unanswered questions.
- Match wording to confidence; reserve "because" for direct evidence.

## Process

1. Identify the target, question, files, line ranges, and key symbols.
2. Build a code anchor with blame and history through renames. Extract related
   commits, pull requests, ticket IDs, comments, and tests.
3. Discover evidence sources available in the current environment. Consider:
   source control, issue trackers, long-form documents, team chat,
   observability, error tracking, analytics, and incident records.
4. Search every available and relevant category. Use one narrowly scoped
   read-only investigator per category when parallel delegation is available;
   otherwise search sequentially. Record queries and null results.
5. Give investigators the same code anchor and question. Require direct
   evidence, indirect evidence, contradictions, gaps, and leads. They must not
   mutate external systems.
6. Verify high-value citations and synthesize without strengthening confidence
   language.

Use `git` for local history and the repository host CLI for pull requests when
available. Use specialized issue, document, or observability tools only when
the current environment exposes them and the user's access permits it.

## Confidence

- **Direct:** a source explicitly states the rationale.
- **Supported:** several indirect sources agree and no evidence contradicts it.
- **Inferred:** plausible from the record but never stated.
- **Speculative:** weak evidence or several equally plausible explanations.
- **Unknown:** the searched record does not answer the question.

## Output

- **Question and code anchor**
- **Direct evidence**, with citations
- **Reasonable inferences**, with the inference chain
- **Competing hypotheses**, including evidence for and against
- **Unknowns and contradictions**
- **Sources consulted**, including empty, unavailable, and irrelevant categories
- **Confidence summary**

If the investigation informs a change, finish with **Preserve / Change / Avoid /
Risk** constraints. The task is complete when every available relevant source
has a recorded outcome and every rationale claim has a confidence tier.
