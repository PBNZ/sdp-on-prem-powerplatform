# ADR-0002: Publish as a clearly-flagged personal alpha

- **Status:** accepted
- **Date:** 2026-07-06

## Context

The connectors are built and read-verified, but write operations are not yet live-verified and
nothing has run end-to-end in a real Power Platform tenant. Power Platform can create a custom
connector from a definition **URL**, which must be publicly reachable — and iterating by
re-uploading files on every test round is painful. So the repo needs to be public *now*, before
it meets the bar one would normally want for a public project.

## Decision

- **Go public as an explicitly-flagged personal alpha.** The README opens with a prominent
  warning: vibe-coded for personal use, public only for import-by-URL, writes not yet
  live-verified, no support/warranty, use with utmost caution. The GitHub About description
  carries the same flag.
- **License: Apache-2.0**, as already recorded at scaffold time in ADR-0001.
- **Adopt the full RepoKit +Public tier** despite the alpha status: LICENSE, SECURITY.md,
  CODE_OF_CONDUCT.md, contributor-facing CONTRIBUTING.md, issue/PR templates, and a
  definition-validation CI workflow (swagger-cli + generator-sync check). CONTRIBUTING sets
  the expectation that reviews may be slow.
- **Rewrite git history before the flip.** Old commits contained a truncated prefix of the
  public demo instance's API key (`<your-api-key>`) in a doc example. It is not a usable
  credential, but the policy is zero key material — even truncated — in a public history.
  `git filter-repo` scrubs the blob text and the one commit message that quoted it;
  pre-publication SHAs change. Only the author had clones, so nothing breaks.
- **The visibility flip itself is manual** (the maintainer runs it), not part of any automated
  or agent-driven step.

## Consequences

- Public readers get an honest signal: alpha, review before use, least-privilege keys.
- The raw `main` URLs of the four `apiDefinition.swagger.json` files become stable import
  targets for Power Platform.
- Anyone comparing against pre-rewrite SHAs (only the author) must re-clone.
- CI now guards PRs: definitions must validate as Swagger 2.0 and the committed V3 JSON must
  match `tools/gen_swagger.py` output.
- References to the private companion MCP project remain in the docs but are marked as
  private/not published.
