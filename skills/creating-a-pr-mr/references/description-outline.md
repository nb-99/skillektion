# PR/MR description outline

Use the repository's PR/MR template when one applies. Otherwise, choose headings that suit the change. These prompts describe the information reviewers need, not text to copy verbatim. Aim for a concise, easily readable description: a reviewer should get the change, the proof, and the risk in one pass. Every structural device below is optional — add one only when it carries information prose would carry less well.

## Intent

What problem or request prompted the change? What observable outcome should it produce? Link a relevant issue or design decision when it adds context.

## Approach

How does the change achieve the outcome at a high level? Explain the main design choice or behavior change without listing every edited file or repeating the diff.

Optionally, show the shape instead of telling it, using the smallest view that makes the key point:

- Pseudocode for a logic or algorithm change
- A call tree for runtime control flow
- A component tree, with state and module boundaries that matter, for a UI change
- A shallow file tree for a file-responsibility or broad refactor change
- A Mermaid diagram for component interaction, control flow, or data flow
- A diff-shaped diff, matched to the topic, when the point is what changes and the surrounding shape already exists

Place the visual next to the short text it supports. Keep only the calls, files, props, states, and boundaries needed to make the point. Several small views beat one large one; use judgment and skip the visual when prose is already clear.

## Verification

Which tests or checks ran, and what were their results? Describe any important manual checks. State what was not verified when it matters.

When showing before and after, prefer execution evidence — the exact test or command that now fails and passes — over a claim. For a visual change, a screenshot or recording of each state is the strongest evidence when the environment supports it.

## Merge danger

Optional. Call whether the change is a one-way or two-way door: a two-way door is cheap to roll back, a one-way door involves destructive actions or hard-to-reverse decisions. Give the blast radius in one word, with only the ramifications that matter. Omit the section for trivial or fully reversible changes; for a genuinely risky change, deep analysis belongs in a linked impact analysis rather than the body.

## Reviewer guidance

Where should a reviewer start? Call out subtle behavior, significant trade-offs, migrations or rollout steps, and areas of risk when relevant. Distinguish generated or mechanical changes from the logic that warrants close review. Include links to supporting context when useful.

Keep the description proportional to the change. Omit empty or inapplicable sections; fill required sections in a repository template rather than replacing its structure.
