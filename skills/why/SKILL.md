---
name: why
description: Investigate why code or a design has its current shape using source history and available organizational evidence. Use for rationale, trade-offs, regressions, postmortems, thresholds, and historical design questions.
disable-model-invocation: true
---

# Why

Investigate intent as a historical question. Code proves mechanics, not motive.
The companion `how` skill answers what the code does and how it works; `why`
answers what forces led to its shape.

## Evidence Rules

- Collect evidence before choosing a narrative.
- Cite claims about intent to commits, pull requests, issues, documents, chat
  links, incidents, dashboards, or comments.
- Label uncited claims as inference.
- Surface contradictions and competing hypotheses.
- Treat the user's suggested rationale as a hypothesis to test, not a conclusion
  to confirm. Seek evidence for and against it, and report when the record does
  not support it.
- State unavailable sources and unanswered questions.
- Match wording to confidence; reserve "because" for direct evidence.

## Process

1. Identify the target, question, files, line ranges, and key symbols.
2. Build the code anchor inline before any delegation. Collect file paths and
   line ranges, key symbols, the last commits touching the target, pull-request
   numbers from merge commits, and linked ticket IDs. Concrete commands:
   `git blame -L <start>,<end> <file>` for last-touch commits,
   `git log --follow -p -- <file>` for history with patches through renames,
   `git log --oneline -20 -- <file>` for recent commits with pull-request
   numbers visible, and `git log -1 --format=%B <commit>` to extract them. Pull
   the bodies and discussion of substantive pull requests with the repository
   host CLI. Give this anchor to every investigator and to the synthesis step.
3. Discover evidence sources available in the current environment. Consider:
   source control, issue trackers, long-form documents, team chat,
   observability, error tracking, analytics, and incident records.
4. Search every available and relevant category. Use one investigator per
   category when parallel delegation is available; otherwise search
   sequentially. Run investigators with full tool access rather than a
   restricted read-only mode, because restricted modes can strip MCP and
   specialized tools the search needs; investigators must not write to the
   repository or mutate external systems. Record queries and null results.
5. Give investigators the same code anchor and question. Present any user-suggested
   rationale as one candidate and require evidence for and against it. Require
   direct evidence, indirect evidence, contradictions, gaps, and leads. They
   must not mutate external systems.
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
