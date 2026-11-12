---
name: Data gap or source
about: A missing, outdated or unverified source, assumption or register row (see docs/good-first-issues.md)
labels: data
---

**Which row or figure** (file and id, e.g. `docs/assumptions.md` A-..., `docs/data-sources.md` row, `cities/ksa/sources.yaml` id):

**The proposed source** (publisher, title, URL, publication date, access date, page or table, licence). Published, licence-compatible material only (rule 4); never contact an agency, company or person (rule 7).

**Acceptance test** (the command that must pass, e.g. `uv run python -m common.sources check <file>`, `uv run python -m common.manifest verify`, `make test`):

Skill to follow: `source-citation`, `assumptions-register` or `licence-register` (`.claude/skills/`).
