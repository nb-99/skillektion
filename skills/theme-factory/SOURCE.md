# Source

Adapted from `skills/theme-factory` in
[`anthropics/skills`](https://github.com/anthropics/skills) at commit
`41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f`.

This version makes the showcase step environment-agnostic: agents that cannot
display files summarize the theme definitions from `themes/` instead of showing
`theme-showcase.pdf`. It also fixes typos in the description and intro, adds
manual-only invocation metadata (`disable-model-invocation` plus the matching
Codex policy in `agents/openai.yaml`), and adds explicit trigger guidance to
the description. The ten theme definitions and the showcase PDF are unchanged.
Licensed under the Apache-2.0 terms in `LICENSE.upstream`.
