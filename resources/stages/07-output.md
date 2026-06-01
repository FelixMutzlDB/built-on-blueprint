# Stage 7 — Assemble output documents

## Steps
1. Assemble `blueprint.md` from `output_templates/spec-template.md`, pulling each
   section from its stage artifact (00–06).
2. Build the decision log from `output_templates/decision-log-template.md`
   (assumptions, rejected alternatives, open questions across all stages).
3. If `options.render_html` is true, render an HTML visualization of the blueprint
   (architecture diagram + roadmap + scorecard). Otherwise skip.
4. If `options.partner_rec` is true, append the partner section from
   `../partner_rec/README.md`. Otherwise OMIT entirely.
5. Append `../DISCLAIMER.md` verbatim as the final section.

## Output
- `blueprint.md` (primary deliverable)
- `decision-log.md`
- optional `blueprint.html`
