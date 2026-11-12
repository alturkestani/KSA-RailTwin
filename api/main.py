"""KSA Rail Twin decision-dashboard API (contract v1.0: `api/README.md`).

Thin and file-backed, after TrafficTwin's `api/main.py` pattern: it reads registers under
`cities/ksa/`, scenarios under `scenarios/` and run outputs under `runs/`, and computes nothing but
selections and the difference against S1. Read-only: GET only. The data root is
RAILTWIN_DATA_ROOT (default: the repo root); the built web app (web/dist) is served at `/`.

    uv run uvicorn api.main:app --port 8000
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from api import data, settings
from api.contract import (
    BASELINE,
    BASELINE_RUN,
    CENTRAL_ROW,
    COMPARISON_CAPTION,
    COMPARISON_LAYOUTS,
    CONTRACT_VERSION,
    FRAMING,
    JUDGE,
    LAYERS,
    OSM_CREDIT,
    POPULATIONS,
    SEED,
    TRADE_OFF_CAPTION,
    envelope,
)
from common.labels import ALIGNMENT_LIMITATION, LABEL

GZIP_MIN_BYTES = 1024
HORIZONS = (30, 40, 60)
RATE_CASES = ("greenbook_2026", "tag_declining", "flat_5", "flat_7", "drawn")


def _root() -> data.Roots:
    return data.Roots(settings.data_root(), settings.runs_root())


def _guard(fn: Any, *args: Any) -> Any:
    try:
        return fn(*args)
    except data.NotFound as exc:
        raise HTTPException(status_code=404, detail=f"not found: {exc}") from exc
    except data.Refused as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def _check_pop(population: str) -> str:
    if population not in POPULATIONS:
        raise HTTPException(status_code=422, detail=f"population must be one of {POPULATIONS}")
    return population


def create_app() -> FastAPI:
    app = FastAPI(title="KSA Rail Twin dashboard API", version=CONTRACT_VERSION)
    app.add_middleware(GZipMiddleware, minimum_size=GZIP_MIN_BYTES)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins(),
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "label": LABEL}

    @app.get("/api/meta")
    def meta() -> dict[str, Any]:
        return {
            "label": LABEL,
            "alignment_limitation": ALIGNMENT_LIMITATION,
            "contract_version": CONTRACT_VERSION,
            "judge": JUDGE,
            "seed": SEED,
            "osm_credit": OSM_CREDIT,
            "layers": LAYERS,
            "baseline": BASELINE,
            "baseline_run": BASELINE_RUN,
            "central_row": CENTRAL_ROW,
            "framing": FRAMING,
            "trade_off_caption": TRADE_OFF_CAPTION,
            "comparison_caption": COMPARISON_CAPTION,
            "comparison_layouts": list(COMPARISON_LAYOUTS),
            "model_language": "in the model, ... (never a forecast)",
        }

    @app.get("/api/layers")
    def layers() -> dict[str, Any]:
        root = _root()
        out = {
            name: _guard(data.lines_layer, root, name) for name in LAYERS if name != "hypothetical"
        }
        out["hypothetical"] = _guard(data.hypothetical_layer, root)
        return envelope(osm_credit=OSM_CREDIT, layer_names=LAYERS, layers=out)

    @app.get("/api/layers/{layer}")
    def layer(layer: str) -> dict[str, Any]:
        if layer not in LAYERS:
            raise HTTPException(status_code=404, detail=f"layer must be one of {list(LAYERS)}")
        root = _root()
        fc = (
            _guard(data.hypothetical_layer, root)
            if layer == "hypothetical"
            else _guard(data.lines_layer, root, layer)
        )
        return envelope(osm_credit=OSM_CREDIT, layer=layer, layer_name=LAYERS[layer], **fc)

    @app.get("/api/stations")
    def stations() -> dict[str, Any]:
        return {"osm_credit": OSM_CREDIT, **_guard(data.stations, _root())}

    @app.get("/api/regions")
    def regions() -> dict[str, Any]:
        return {"osm_credit": OSM_CREDIT, **_guard(data.regions, _root())}

    @app.get("/api/register")
    def register(
        region: str | None = None,
        stage: str | None = None,
        min_population: float | None = None,
    ) -> dict[str, Any]:
        rows = _guard(data.register, _root())
        if region:
            rows = [r for r in rows if r["region"] == region]
        if stage:
            if stage not in data.STAGES:
                raise HTTPException(status_code=422, detail=f"stage must be one of {data.STAGES}")
            rows = [r for r in rows if r["stage"] == stage]
        if min_population is not None:
            rows = [r for r in rows if (r["population"] or 0) >= min_population]
        return {
            "label": "screening input, not a forecast",
            "osm_credit": OSM_CREDIT,
            "stages": list(data.STAGES),
            "count": len(rows),
            "rows": rows,
            "source": [data.CANDIDATES, data.LONGLIST, data.SCORES],
        }

    @app.get("/api/funnel")
    def funnel() -> dict[str, Any]:
        return {"label": "screening input, not a forecast", **_guard(data.funnel, _root())}

    @app.get("/api/scenarios")
    def scenarios() -> dict[str, Any]:
        return envelope(baseline=BASELINE, scenarios=_guard(data.scenarios, _root()))

    @app.get("/api/cba")
    def cba(
        population: str = CENTRAL_ROW["population"],
        horizon: int = Query(CENTRAL_ROW["horizon"]),
        rate_case: str = CENTRAL_ROW["rate_case"],
        family: str | None = None,
    ) -> dict[str, Any]:
        _check_pop(population)
        if horizon not in HORIZONS or rate_case not in RATE_CASES:
            raise HTTPException(
                status_code=422, detail=f"horizon {HORIZONS}, rate_case {RATE_CASES}"
            )
        cases = _guard(data.cba_cases, _root(), population, horizon, rate_case)
        if family:
            cases = [c for c in cases if c["family"] == family]
        return envelope(
            row={"population": population, "horizon": horizon, "rate_case": rate_case},
            baseline_run=BASELINE_RUN,
            cases=cases,
        )

    @app.get("/api/cba/{case}")
    def cba_one(
        case: str,
        population: str = CENTRAL_ROW["population"],
        horizon: int = Query(CENTRAL_ROW["horizon"]),
        rate_case: str = CENTRAL_ROW["rate_case"],
    ) -> dict[str, Any]:
        _check_pop(population)
        return envelope(**_guard(data.cba_case, _root(), case, population, horizon, rate_case))

    @app.get("/api/programmes")
    def programmes(population: str = CENTRAL_ROW["population"]) -> dict[str, Any]:
        _check_pop(population)
        return envelope(
            baseline=BASELINE,
            programmes=_guard(data.programmes, _root(), population),
        )

    @app.get("/api/programmes/{layout}")
    def programme_one(layout: str, population: str = CENTRAL_ROW["population"]) -> dict[str, Any]:
        _check_pop(population)
        return envelope(**_guard(data.programme, _root(), layout, population))

    @app.get("/api/pareto")
    def pareto() -> dict[str, Any]:
        return envelope(**_guard(data.pareto, _root()))

    @app.get("/api/fiscal")
    def fiscal() -> dict[str, Any]:
        return envelope(**_guard(data.fiscal, _root()))

    @app.get("/api/vfm")
    def vfm() -> dict[str, Any]:
        return envelope(**_guard(data.vfm, _root()))

    @app.get("/api/difference")
    def difference(scenario: str, population: str = CENTRAL_ROW["population"]) -> dict[str, Any]:
        _check_pop(population)
        return envelope(**_guard(data.difference, _root(), scenario, population))

    dist = settings.web_dist()
    if (dist / "index.html").exists():
        app.mount("/", StaticFiles(directory=dist, html=True), name="web")
    return app


app = create_app()
