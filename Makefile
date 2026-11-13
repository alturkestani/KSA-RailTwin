# KSA Rail Twin: common tasks. `make setup && make test` is the README command.
# CI has no data/ symlinks, so it runs `make test MANIFEST_FLAGS=--allow-missing`. A fresh clone
# without the data/osm symlink defaults to --allow-missing too (R9); a full checkout verifies every row.
.PHONY: setup data-links test lint pytest docver manifest cost region-prompts status dashboard demo demo-serve credits report-pdf

MANIFEST_FLAGS ?= $(if $(wildcard data/osm),,--allow-missing)

setup:
	uv sync

data-links:
	./scripts/link_data.sh

test: lint pytest docver manifest

lint:
	uv run ruff check .
	uv run ruff format --check .

pytest:
	uv run pytest -q

docver:
	uv run python -m common.docver check docs prompts .claude film/script

manifest:
	uv run python -m common.manifest verify $(MANIFEST_FLAGS)

cost:
	uv run python -m common.cost_log summary

region-prompts:
	./scripts/make_region_prompts.sh

status:
	@sed -n '1,12p' docs/STATUS.md
	@grep -hE "^[A-Za-z0-9_]+: (done|blocked)" docs/status/*.md 2>/dev/null || true

# Decision dashboard (R8; manual command, never part of `make test`): build web/ and serve the API
# plus the built app on http://127.0.0.1:$(DASHBOARD_PORT). Needs `cd web && npm install` once
# (disk gate: check `df -h ~` first). Data root: RAILTWIN_DATA_ROOT / RAILTWIN_RUNS_ROOT.
DASHBOARD_PORT ?= 8765
dashboard:
	@test -d web/node_modules || { echo "web/node_modules missing: check df -h ~, then cd web && npm install"; exit 1; }
	cd web && npm run build
	uv run uvicorn api.main:app --host 127.0.0.1 --port $(DASHBOARD_PORT)

# Fixture-scale demo (R9): screening on the mini-region register -> fixture CBA -> dashboard API on
# the fixture data (started on 127.0.0.1, queried, stopped). Invented values only; outputs under
# runs/demo/ (gitignored); no download, no network. `make demo-serve` keeps the dashboard running
# and builds web/ first when web/node_modules exists (cd web && npm ci, once; check df -h ~ first).
DEMO_SEED ?= 1
demo:
	uv run python -m common.demo run --seed $(DEMO_SEED)

demo-serve:
	@if [ -d web/node_modules ]; then cd web && npm run build; else echo "web/node_modules missing: API only (cd web && npm ci to add the web app)"; fi
	uv run python -m common.demo run --seed $(DEMO_SEED) --serve --port $(DASHBOARD_PORT_DEMO)

DASHBOARD_PORT_DEMO ?= 8766

# docs/credits.md from the licence register (R9)
credits:
	uv run python -m common.licences credits --out docs/credits.md

# PDF of the feasibility report (PUBLISH_PDF_POST): docs/report/feasibility-report.pdf, A4, built
# with headless Chrome from docs/report/feasibility-report.md; then pages, links, private-name count.
report-pdf:
	uv run python -m common.report_pdf build
	uv run python -m common.report_pdf check
