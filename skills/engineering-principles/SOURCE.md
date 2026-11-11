# Source

Adapted from the inline principles index in `pstack/skills/poteto-mode` and the
corresponding `pstack/skills/principle-*/SKILL.md` leaves in
[`cursor/plugins`](https://github.com/cursor/plugins) at commit
`5866df557357d005b3c0c9d3da0d9e739b4bdde3`.

Pstack registers principle leaves with model invocation disabled. Its
`poteto-mode` provides an inline index for multi-step tasks and loads applicable
leaves; users also invoke principle names to steer a workflow. This
adaptation consolidates selected portable rules into one conditional index and
keeps it available for automatic selection while omitting Cursor mode
mechanics. It excludes the upstream root-cause, type-system,
domain-modeling, context-window, subtraction, foundational-thinking,
outcome-execution, laziness, experience-first, design-space, and
never-block-on-the-human leaves because dedicated skills or host policy cover
them or conflict with safe clarification rules. `sources.json` records the
index path; the adapted text also derives from the sibling `principle-*` paths.
The reusable `references/always-on.md` projection keeps the concise rule set in
one source for clients that support global instructions.

This revision incorporates `principle-explain-the-number` only for performance
tests and benchmarks already in scope. It validates measurements without
initiating benchmarks for ordinary implementation, design ideas, or suspected
performance effects, and removes the upstream benchmark-checklist dependency.

At revision `5866df5` upstream sharpened `principle-attack-the-premise` to
"write the premise down and test it directly before another fix that assumes
it"; this revision adds that principle to the index and the always-on
projection. The rest of the upstream pass renames leaf-skill references and
tightens prose in files this adaptation does not carry.
Upstream's eval-result scope, mandatory per-number limiter, and skip checklist
are intentionally omitted. Bottleneck evidence is required when making a
bottleneck claim, not for every measured number. It adapts
`principle-test-behavior-not-implementation` around independent expectations and
observable behavior or explicit contracts, without upstream's assertion
blacklist, inaccurate `undefined` test, or blanket deletion rule. Legitimate
negative, property-based, compile-time, contract, reviewed snapshot, and
characterization tests remain valid, as do call counts that encode a contract.
The `principle-attack-the-premise` addition was not selected for this update.
Existing focused
verification and safe clarification rules remain unchanged.

Licensed under the MIT terms in `LICENSE.upstream`.
