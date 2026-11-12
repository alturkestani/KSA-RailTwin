"""demand.terrain on synthetic in-memory DEM arrays (no network, no files beyond the rule YAML)."""

from __future__ import annotations

import numpy as np
import pytest

from demand import terrain as T

RES = 30.0


@pytest.fixture(scope="module")
def cfg() -> dict:
    return T.load_rules()


def _grid(n: int = 201) -> tuple[np.ndarray, np.ndarray]:
    yy, xx = np.mgrid[0:n, 0:n] * RES
    return yy, xx


def _metrics(z: np.ndarray, cfg: dict, coast_km: float = 400.0) -> dict:
    n = z.shape[0]
    mask = T.disc_mask(z.shape, RES, ((n - 1) / 2, (n - 1) / 2), (n // 2 - 2) * RES)
    return dict(T.terrain_metrics(z, RES, mask, cfg), coast_km=coast_km)


def test_flat_is_flat_desert(cfg):
    rng = np.random.default_rng(1)
    z = 600.0 + rng.normal(0, 0.05, size=(201, 201))
    m = _metrics(z, cfg)
    assert m["slope_p90_deg"] < 1.0 and m["relief_m"] < 2.0
    assert T.classify(m, cfg["rule"])[0] == "flat_desert"


def test_steep_is_escarpment(cfg):
    _, xx = _grid()
    z = 1000.0 + np.tan(np.radians(30.0)) * xx  # a 30-degree plane
    m = _metrics(z, cfg)
    assert m["slope_mean_deg"] == pytest.approx(30.0, abs=0.5)
    assert T.classify(m, cfg["rule"])[0] == "escarpment_mountain"


def test_coastal_and_sabkha(cfg):
    z = np.full((201, 201), 25.0)
    assert T.classify(_metrics(z, cfg, coast_km=3.0), cfg["rule"])[0] == "coastal"
    low = np.full((201, 201), 2.0)
    cls, _, flags = T.classify(_metrics(low, cfg, coast_km=3.0), cfg["rule"])
    assert cls == "sabkha" and "sabkha_signature_dem_only" in flags


def test_dune_signature(cfg):
    yy, xx = _grid()
    # transverse dunes: 1.2 km wavelength, 40 m crest-to-trough, slopes spread over the disc
    z = 800.0 + 20.0 * np.sin(2 * np.pi * xx / 1200.0) + 5.0 * np.sin(2 * np.pi * yy / 2500.0)
    cls, _, flags = T.classify(_metrics(z, cfg), cfg["rule"])
    assert cls == "dunes" and "dune_signature_dem_only" in flags


def test_deterministic(cfg):
    rng = np.random.default_rng(7)
    z = 500.0 + np.cumsum(rng.normal(0, 0.5, size=(201, 201)), axis=1)
    a, b = _metrics(z, cfg), _metrics(z.copy(), cfg)
    assert a == b
    assert T.classify(a, cfg["rule"]) == T.classify(b, cfg["rule"])


def test_radius_rule_and_tiles(cfg):
    ext = cfg["extent"]
    assert T.radius_km(None, ext) == T.val(ext["radius_missing_pop_km"])
    assert T.radius_km(100.0, ext) == T.val(ext["radius_min_km"])
    assert T.radius_km(1e8, ext) == T.val(ext["radius_max_km"])
    assert T.tile_name(24, 46) == "Copernicus_DSM_COG_10_N24_00_E046_00_DEM"
    assert T.tiles_for((45.9, 23.9, 46.1, 24.1)) == [(23, 45), (23, 46), (24, 45), (24, 46)]
    assert all(c in T.CLASSES for c in ("flat_desert", "dunes", "sabkha", "coastal", "mixed"))
