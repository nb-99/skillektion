# Source

Adapted from `pstack/skills/why` in
[`cursor/plugins`](https://github.com/cursor/plugins) at commit
`5866df557357d005b3c0c9d3da0d9e739b4bdde3`.

This version removes fixed models, Cursor task modes, and mandatory seven-MCP
coverage. It retains code anchoring, available-source investigation, citations,
confidence calibration, contradictions, hypotheses, explicit gaps, and
upstream's manual-only invocation policy. It adds upstream's suggested-rationale
rule, present at this revision in `references/epistemics.md`, to the main skill
file and investigator instructions. The user's rationale is tested as a
hypothesis against supporting and opposing evidence rather than merely
confirmed. The evidence and
uncertainty safeguards remain in the main skill file. At revision `5866df5`
this version adopts upstream's agent-mode investigator rule — restricted
read-only modes can strip the MCP access the search needs, so investigators
run with full tool access under an explicit no-writes rule — and inlines
upstream's concrete code-anchor commands. It keeps the confidence framework
in the main skill file instead of the upstream `references/epistemics.md`.
Licensed under the MIT terms in `LICENSE.upstream`.
