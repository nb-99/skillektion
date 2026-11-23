# Source

This skill combines the existing Skillektion consumer's `code-review-agent`
contract with the panel, rubric, and lead-judgment structure from
`pstack/skills/interrogate` in
[`cursor/plugins`](https://github.com/cursor/plugins) at commit
`5866df557357d005b3c0c9d3da0d9e739b4bdde3`.

It removes Cursor task configuration, fixed model lists, model-configuration
repair, and consensus-as-proof, and keeps the panel structure instead of the
upstream rewrite that routes reviewers through the pstack arena skill. At
revision `5866df5` it adopts upstream's run-proven finding standard — a finding
survives only when a rerun proves it, and reviewers report the exact command
and output — plus the intent restatement from upstream's
`in-your-own-words` skill, inlined. It intentionally occupies the portable
`code-review` name instead of mirroring Matt Pocock's different two-axis review
workflow. Unlike upstream, it is model-invocable, so that other skills such as
`council` and `drive-to-ready` can load it, and it scopes the reviewer edit
prohibition to repository files while explicitly permitting throwaway
reproduction scripts in a temporary scratch directory and temporary tool
environments such as `nix-shell -p`. Licensed under the MIT terms in
`LICENSE.upstream`.
