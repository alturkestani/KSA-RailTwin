"""Small geodesy helpers shared by the network modules.

- `haversine_km`: great-circle distance on a sphere of radius `EARTH_RADIUS_KM`.
- `unit_vectors` / `KNearest`: nearest-neighbour search on 3-D unit vectors with a scipy cKDTree;
  chord distance is converted back to great-circle km, so the result equals the haversine distance.

The sphere radius is the IUGG mean Earth radius R1 = 6371.0088 km (Moritz 2000, "Geodetic Reference
System 1980", Journal of Geodesy 74:128-133), a standard constant, not a model assumption.
"""

from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree

EARTH_RADIUS_KM = 6371.0088  # IUGG mean radius R1 (Moritz 2000); see module docstring


def haversine_km(lat1, lon1, lat2, lon2) -> np.ndarray:
    """Great-circle km between points (degrees); broadcasts like NumPy."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dlmb = np.radians(np.asarray(lon2) - np.asarray(lon1))
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def unit_vectors(lat, lon) -> np.ndarray:
    phi, lmb = np.radians(np.asarray(lat, float)), np.radians(np.asarray(lon, float))
    return np.column_stack([np.cos(phi) * np.cos(lmb), np.cos(phi) * np.sin(lmb), np.sin(phi)])


def chord_to_km(chord) -> np.ndarray:
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.clip(np.asarray(chord) / 2, 0.0, 1.0))


class KNearest:
    """k nearest targets by great-circle distance (exact: chord order = arc order)."""

    def __init__(self, lat, lon) -> None:
        self.n = len(np.atleast_1d(lat))
        self.tree = cKDTree(unit_vectors(lat, lon))

    def query(self, lat, lon, k: int = 1) -> tuple[np.ndarray, np.ndarray]:
        """Return (km, index) arrays of shape (n_points, k), sorted by distance."""
        k = max(1, min(k, self.n))
        chord, idx = self.tree.query(unit_vectors(lat, lon), k=k)
        chord, idx = np.asarray(chord).reshape(-1, k), np.asarray(idx).reshape(-1, k)
        return chord_to_km(chord), idx
