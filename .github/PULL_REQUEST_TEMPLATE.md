## What & why

<!-- One concern per PR. -->

## Checklist

- [ ] Definitions validate: `npx @apidevtools/swagger-cli validate connectors/<name>/apiDefinition.swagger.json`
- [ ] V3 definition changes made in `tools/gen_swagger.py` and regenerated (`python tools/gen_swagger.py`) — the committed JSON matches the generator output
- [ ] `CHANGELOG.md` updated under `## [Unreleased]` for user-visible changes
- [ ] No API keys (even truncated), no private hostnames in the diff
- [ ] No write operations tested against the shared public demo
- [ ] Conventional Commit message(s)
