# LESSONS

> One lesson per section, one-line summary first. Update rather than duplicate; delete what
> turns out wrong.

## RepoKit power-platform-connectors type assumes Postman generation

The type template stamps a Postman→Swagger generation pipeline. This project hand-authors
definitions (PRD non-goal: no mechanical conversion), so the pipeline files were omitted at
scaffold time (ADR-0001) and an upstream issue filed against pbnz/repo-kit.
