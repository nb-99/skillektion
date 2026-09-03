---
name: openspec-workflow
description: "Use when: working in an OpenSpec-initialized repository, creating or changing an OpenSpec proposal, applying an approved OpenSpec plan, or archiving a completed OpenSpec change."
---

# OpenSpec Workflow

Use OpenSpec only for substantive features, cross-cutting refactors, or changes
whose requirements need explicit review. Do not create an OpenSpec change for a
small, localized fix unless the user requests it.

## Explore And Propose

1. Confirm that the repository contains `openspec/` before using OpenSpec
   commands.
2. Use `/opsx:explore` when requirements, affected areas, or the solution are
   unclear. Do not write implementation code during exploration.
3. Use `/opsx:propose <change-name>` once the change has a clear outcome.
4. Ensure the proposal covers the problem, requirements, affected canonical
   specifications, design decisions where needed, and executable tasks.
5. Present the proposal and wait for user approval before `/opsx:apply`.

## Apply

1. Treat the approved proposal, specification deltas, design, and tasks as the
   implementation contract.
2. Implement tasks incrementally and run the narrowest relevant validation
   after completing each independently testable behavior or invariant.
3. Keep the proposal and task status accurate when implementation changes the
   agreed scope. Ask before materially changing the plan.

## Archive

Before `/opsx:archive`, complete all of the following:

1. Run the relevant tests, linting, type checks, and OpenSpec validation.
2. Review each delta requirement and scenario against the canonical
   `openspec/specs/**` specifications.
3. Update every affected canonical specification so it fully represents the
   implemented behavior, including changed requirements, scenarios, and
   cross-specification consequences.
4. Do not archive a change while its delta changes behavior that the canonical
   specifications omit or contradict.
5. Summarize the validation and canonical-specification updates, then ask the
   user to confirm archiving.

Use `openspec init` or `openspec update` only after explicit user approval,
because either command changes repository files.
