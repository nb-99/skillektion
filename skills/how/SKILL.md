---
name: how
description: Explain how code, a feature flow, or a subsystem works and where its responsibilities belong. Use for code walkthroughs, architecture onboarding, runtime traces, ownership questions, and architecture critique.
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
cost. Mark inferred behavior and evidence gaps.

## Critique

When the user asks for architectural problems or improvements, explain the
system first. Then use independent read-only critique passes when available.
Give each pass the same explanation, paths, and question. Ask each pass to find
incorrect boundaries, hidden coupling, confused ownership, fragile data flow,
and unnecessary complexity. Require a reachable impact, code evidence, and the
smallest useful improvement for every proposed issue.

Verify proposed issues against the code and classify them as:

- **Act on:** concrete problems worth fixing now.
- **Consider:** real concern with uncertain cost or priority.
- **Noted:** valid but low-priority observation.
- **Dismissed:** incorrect, missing context, or preference without impact.

Present the standalone explanation before the critique. The task is complete
when the requested flow can be traced without hand-waving and every critique
finding is verified or dismissed with a reason.
