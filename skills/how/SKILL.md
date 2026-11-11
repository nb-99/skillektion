---
name: how
description: Explain how code, a feature flow, or a subsystem works. Use for code walkthroughs, architecture onboarding, runtime traces, and ownership or placement questions.
disable-model-invocation: true
---

# How

Build a working mental model, not an annotated source listing.

## Scope

Interpret the target from the request and current context. State a best-guess
scope when ambiguous so the user can redirect without blocking exploration.

- For one function or module, trace and explain it directly.
- For a cross-cutting subsystem, divide exploration into two to four distinct
  read-only slices, such as entry points and flow, state and data model,
  integration boundaries, and configuration or operations.

Use independent workers when available; otherwise inspect the slices
sequentially. Each slice must report components, execution flow, files read,
boundaries, surprises, and open questions. Read actual code and follow calls,
types, and data from trigger to effect.

## Explain

Synthesize the evidence into only the sections the question needs:

- **Overview:** what it is, what it does, and why the reader cares.
- **Key concepts:** the types, services, and abstractions needed for the model.
- **How it works:** trigger, ordered flow, data movement, and decision points.
- **Where it lives:** a small map of relevant files and ownership boundaries.
- **Gotchas:** surprising behavior, sharp edges, and unresolved questions.

Cite specific files and symbols. Use a diagram only when it reduces explanation
cost. Mark inferred behavior and evidence gaps. For architectural problems or
improvements, use the `code-review` or `codebase-design` skills instead; this
skill explains, it does not judge.

The task is complete when the requested flow can be traced without hand-waving.
