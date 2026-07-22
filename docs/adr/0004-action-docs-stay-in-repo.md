# ADR-0004: Action docs stay in-repo — GitHub wiki rejected, Pages is the escape hatch

- **Status:** accepted
- **Date:** 2026-07-22

## Context

ADR-0003 put one doc page per action at `connectors/<name>/actions/<kebab-operationId>.md`,
linked from each operation by a `github.com/.../blob/main/...` URL. That makes the maker's
"Learn more" click land on a file page with repo chrome — a file browser header and a
Code/Preview/Blame toggle wrapped around the prose.

The GitHub wiki is the obvious alternative host: cleaner reading chrome, a `_Sidebar.md`
navigation tree, and its own search scoped to just the docs — real value across 55 pages.
Its usual objection does not apply here, either: GitHub restricts public-repo wiki editing to
collaborators by default, so this would not be an open wiki.

What does apply is that a wiki is a **separate git repository** (`<repo>.wiki.git`) with no
pull requests:

- The six invariants in `tools/check_action_docs.py` — Learn-more link present, link resolves,
  no orphan docs, every parameter mentioned, index complete — are checked against files on
  disk in this repo, by `validate.yml`. Hosting the pages elsewhere makes all six
  unenforceable. Actions can *react* to wiki edits (the `gollum` event) but cannot gate them.
- ADR-0003 §3 rests on the generated markdown being the committed, reviewed artifact. Wiki
  writes bypass review entirely.
- The pages carry relative links out to the rest of the repo (`../README.md`,
  `../../../LESSONS.md`, `../../../templates/`, `../../../docs/test-evidence/`). Across
  repositories every one of them breaks.
- Wikis are absent from clones and forks, so `connectors/<name>/` stops being the
  self-contained unit (definition + properties + README + action docs) that it is today.
- Per GitHub's own wiki documentation, search engines index a wiki only for repositories with
  500 or more stars; below that the pages are invisible to web search, and wikis sit outside
  GitHub code search as well. GitHub's documentation points at Pages for indexable docs.

GitHub Pages gives the same presentation win with none of those losses, at the cost of a site
build pipeline — ceremony this repo does not yet warrant at the Core + Public tier (ADR-0002).

## Decision

1. **Action docs stay in-repo**, as ADR-0003 specifies. The wiki stays disabled; it is not a
   host for any documentation in this project.
2. **If presentation becomes the real complaint, the answer is GitHub Pages**, built from
   these same files — source of truth in-repo, CI still gating, relative links intact,
   pages indexable.
3. **Keep Learn-more URL construction centralized** in `action_doc_url()`
   (`tools/gen_swagger.py`). It is the single producer of the URLs baked into all four
   definitions, so repointing them at another host stays a one-function change plus a
   regenerate.

## Consequences

- The maker's "Learn more" click keeps landing on a `blob/main` page with repo chrome. That
  is the accepted cost, bought back by CI-enforced lockstep between definitions and docs.
- Nothing changes in the definitions or the generators; this ADR records a rejected option so
  the question is not reopened from scratch. ADR-0003 is unchanged and not superseded.
- The Pages path is deliberately unbuilt. Reaching for it should be triggered by evidence
  that readers want it, not by the fact that it is available.
- Because the action doc pages live under `connectors/`, a future Pages build needs a step
  that gathers them into the site's docs root — worth knowing before estimating that work.
