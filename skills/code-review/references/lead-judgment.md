# Lead Judgment

Filter reviewer output instead of concatenating it.

- Reviewers tend to inflate nits when no defect is present. A review containing
  only preferences can correctly conclude that the change is sound.
- A hypothetical state is actionable only when callers or external inputs can
  reach it. Trace the path.
- Extraction, interfaces, or abstractions need a second real use or a concrete
  problem. Different taste is not a defect.
- A finding may reveal that the reviewer missed repository context. Check the
  surrounding code and instructions before accepting it.
- Scrutinize correctness and security findings even when only one reviewer
  raises them.
- Independent agreement raises priority, but correlated reviewers can agree and
  still be wrong.
- Show dismissed findings with reasons. Visible filtering builds trust and lets
  the user challenge the decision.
