# Source

Adapted from `pstack/skills/how` in
[`cursor/plugins`](https://github.com/cursor/plugins) at commit
`5866df557357d005b3c0c9d3da0d9e739b4bdde3`.

This version replaces fixed model assignments and Cursor task configuration
with capability-based read-only exploration. It retains scoped exploration and
architectural synthesis, and keeps upstream's manual-only invocation policy.
At revision `5866df5` upstream removed the critique mode, its critic prompt,
and its critique rubric; this revision follows that removal and routes
architectural critique to the `code-review` and `codebase-design` skills.
Licensed under the MIT terms in `LICENSE.upstream`.
