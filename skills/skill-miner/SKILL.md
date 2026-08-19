---
name: skill-miner
description: Mine selected past agent sessions for repeated corrections, preferences, and workflows, then draft reusable skills. Use ONLY when the user explicitly asks to learn from chat history or turn past observations into agent guidance.
disable-model-invocation: true
---

# Skill Miner

Read [transcript-sources.md](references/transcript-sources.md) before collecting
history from a client.

## 1. Define The Scope

Ask the user to choose:

- the client or exported transcript directory;
- the project or workspace;
- a date range or explicit sessions;
- whether to create a new skill or improve an existing one;
- where drafts may be written.

Show the exact sessions or files to be read before reading transcript content.
Read only the sessions the user confirms.

Default to user messages and final assistant responses. Include other records
only when the user explicitly selects them.

This step is complete when the user has confirmed all five scope choices and
the exact sessions or files.

## 2. Collect Safely

Use the supported export method for the chosen client. Record the client,
client version, workspace, export method, and session identifiers in temporary
analysis notes.

Keep temporary exports outside the repository. Remove only temporary exports
created by this workflow; leave user-provided exports untouched. Use read-only
session operations and keep all transcript data local.

Sanitization is best-effort. Ask the user to exclude or redact sessions likely
to contain credentials, customer data, private keys, or unrelated private
conversations before analysis. If sensitive material still appears, stop that
session's analysis, write no notes from it, and ask whether to exclude it.

Analysis notes carry paraphrases only, without secret-shaped values, absolute
home paths, credentials, personal identifiers, or transcript quotations.

## 3. Extract Signals

Split the selected history into at least three sessions or time slices when
enough history exists. Analyze slices independently, using parallel read-only
workers when available.

Each worker must receive the same session boundary and privacy rules, and must
return paraphrased signals rather than quotations or raw transcript content.

Look for concrete repeated signals:

- corrections the user repeatedly makes;
- preferred response length, structure, tone, and terminology;
- recurring verification and evidence requirements;
- stable Git, review, delegation, or tool workflows;
- tasks that repeatedly need the same sequence or reference material;
- mistakes that a focused checklist could prevent.

For each signal, record only a short paraphrase, affected sessions, confidence,
and conflicts. Do not retain transcript quotations in the proposed skill.

This step is complete when every selected slice has been analyzed and its
signals recorded. With fewer than three sessions, treat every signal as at most
probable.

## 4. Corroborate

Classify a signal as:

- **strong**: appears independently in at least three sessions or time slices;
- **probable**: appears twice without contradictory evidence;
- **weak**: appears once, is ambiguous, or reflects one unusual task;
- **conflicted**: later behavior or explicit instructions contradict it.

Draft from strong signals. Discuss probable signals with the user. Exclude weak
and conflicted signals unless the user explicitly confirms them as a durable
preference.

The user's current explicit preference outranks historical inference.

This step is complete when every signal has a confidence tier and conflicts
have been identified.

## 5. Confirm Intent

Present strong and probable signals as concise paraphrases. Ask one or two
structured questions about which patterns reflect durable preferences, then
ask one open question about useful behavior that may not appear in the selected
history. Discard rejected signals. Treat confirmed preferences as strong.

## 6. Choose The Artifact

Create a skill only when the behavior has a distinct trigger and a reusable
process or body of reference. Otherwise propose the narrower home:

- a repository instruction for repository-specific rules;
- a global rule for behavior that must apply to every task;
- documentation for human knowledge;
- a lint, test, script, or configuration rule for mechanically enforceable
  behavior;
- no artifact when normal agent behavior already covers the observation.

Prefer improving an existing skill over creating an overlapping one.

## 7. Draft And Review

Use the `writing-for-agents` skill when available; otherwise follow the Agent
Skills format directly. Ask before using `unslop`, when available, as a final
prose pass because it applies an opinionated house style.

The draft must:

- use a specific trigger-oriented description;
- encode only corroborated or user-confirmed behavior;
- state observable completion criteria;
- avoid client-specific tools unless compatibility is explicit;
- contain paraphrased, corroborated behavior without transcript excerpts,
  session identifiers, private paths, credentials, or inferred personal facts;
- credit any third-party material it adapts.

Present each proposed rule with its confidence and a paraphrased evidence
summary outside the skill. Ask the user to accept, revise, or reject it.

Write the reviewed draft to the approved path only after the user approves its
content and target. Installation, commits, pushes, publishing, and pull requests
each require separate confirmation.

The workflow is complete when the user has accepted or rejected every proposed
rule, approved drafts have been written to their chosen locations, and all
temporary exports created by this workflow have been removed.

## Updating An Existing Skill

Use only sessions newer than the skill's last meaningful update. For a tracked
skill, obtain that cutoff with `git log -1 --format=%cI -- <path>`; otherwise ask
the user for it. Preserve rules that the new evidence neither contradicts nor
supersedes. Show additions, changes, and removals separately before editing.
