# Source

This skill combines the existing Skillektion consumer's `code-review-agent`
contract with the panel, rubric, and lead-judgment structure from
`pstack/skills/interrogate` in
[`cursor/plugins`](https://github.com/cursor/plugins) at commit
`60c641e4fad674784b30abcf9f8915dea39df38d`.

It removes Cursor task configuration, fixed model lists, model-configuration
repair, and consensus-as-proof. It intentionally occupies the portable
`code-review` name instead of mirroring Matt Pocock's different two-axis review
workflow. Licensed under the MIT terms in `LICENSE.upstream`.
