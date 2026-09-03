# Source

This skill combines the existing Skillektion consumer's `code-review-agent`
contract with the panel, rubric, and lead-judgment structure from
`pstack/skills/interrogate` in
[`cursor/plugins`](https://github.com/cursor/plugins) at commit
`7314f723a487ec406b6369fe5865ba034cfed166`.

It removes Cursor task configuration, fixed model lists, model-configuration
repair, and consensus-as-proof. It intentionally occupies the portable
`code-review` name instead of mirroring Matt Pocock's different two-axis review
workflow. Licensed under the MIT terms in `LICENSE.upstream`.
