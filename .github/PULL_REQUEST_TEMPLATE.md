## What & why

<!-- One concern per PR. -->

Refs #<!-- driving issue number — plain Refs, no closing keywords; a human closes after verifying -->

## Checklist

- [ ] Driving issue referenced as `Refs #NN` (no auto-close keywords), if there is one
- [ ] Definitions validate: `npx @apidevtools/swagger-cli validate connectors/<name>/apiDefinition.swagger.json`
- [ ] V3 definition changes made in `tools/gen_swagger.py` and regenerated (`python tools/gen_swagger.py`) — the committed JSON matches the generator output
- [ ] `CHANGELOG.md` updated under `## [Unreleased]` for user-visible changes
- [ ] No API keys (even truncated), no private hostnames, no real personal names in the diff
- [ ] No write operations tested against the shared public demo
- [ ] Conventional Commit message(s)
- [ ] An ADR added under [`docs/adr/`](docs/adr/) for any notable decision
