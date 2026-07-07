# ADR-0003: Per-action "Learn more" docs, linked via externalDocs + description suffix

- **Status:** accepted
- **Date:** 2026-07-07

## Context

In the flow designer, an imported action shows only its short description (the About tab's
"Operation note"). The `input_data` envelope — the heart of every SDP call — needs far more
room than a description: every parameter explained, plus JSON/XML/SQL examples covering all
formatting variations. That documentation needs a stable, linkable home per action.

Two mechanisms can carry the link, with different guarantees:

- `externalDocs` on the operation is the Swagger 2.0 field for exactly this, and Microsoft's
  own connector schema (`schemas/apiDefinition.swagger.schema.json` in
  microsoft/PowerPlatformConnectors) explicitly allows it on operations — but no primary
  source documents whether the designer renders it as a clickable "Learn more" link.
- The operation description is provably displayed (About tab), but only as text.

Doc placement options: one section per action in the connector README (one huge page,
fragile anchors) vs a dedicated page per action (deep-linkable, room for examples).

## Decision

1. **One doc page per action** at `connectors/<name>/actions/<kebab-operationId>.md`, plus a
   generated `actions/README.md` index per connector. Learn-more URLs use the
   `github.com/...(blob)/main/...` form — these are human pages; the raw-vs-blob trap
   (LESSONS.md) applies only to definition imports.
2. **Belt and braces in the definitions:** every operation gets *both* an
   `externalDocs: {description: "Learn more", url}` *and* a trailing
   `" Learn more: <url>"` on its description — the spec-correct field plus the
   guaranteed-visible text.
3. **Docs are generated**, like the definitions: `tools/gen_action_docs.py` derives the
   parameter tables and response fields mechanically from the committed swagger (no parameter
   can be missed) and merges curated explanations/examples from its content table. The
   generated markdown is the committed, reviewed artifact.
4. **CI enforces lockstep:** `tools/check_action_docs.py` fails if an operation lacks the
   link, a link has no doc, a doc has no operation, a parameter goes unmentioned, or the
   index misses a page; the generator-sync step now also re-runs `gen_action_docs.py`.

## Consequences

- Every action self-documents from inside Power Automate; the JSON/XML/SQL formatting
  variations live one click away instead of being crammed into descriptions.
- Curated content claims are grounded: envelope grammar and payload fields were verified
  against the official on-prem V3 references (input-data, search-criteria, request_note,
  release_worklog for the shared worklog object, request closure), behaviour claims against
  this repo's live evidence; write operations carry the not-yet-live-verified caveat.
- Adding an operation now *requires* adding its content entry (generator + CI fail
  otherwise) — deliberate friction, same trade-off as the definition generator.
- If the designer some day renders operation `externalDocs` natively, nothing changes; if it
  never does, the description suffix already delivers the link. Renaming an operationId
  changes its doc URL — acceptable pre-1.0.
