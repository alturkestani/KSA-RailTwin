> **Document version:** cities/ksa/zones/README.md v0.2 | 1 Nov 2026 | Author: R1a builder; R4 builder (commute_minutes_r4.parquet) | Status: draft

# cities/ksa/zones — administrative zones, settlement universe, economic nodes

Small derived tables committed under rule 8. Rebuild: `uv run python -m rail.osm extract` (KSA polygon), `uv run python -m network.zones admin`, `uv run python -m network.zones settlements --grid data/ksa/grids/sau_ppp_2020_UNadj_constrained.tif --grid-manifest-id worldpop-sau-2020-100m-unadj-constrained`, then `uv run python -m network.distances` (distance fields) and `uv run python -m network.econ` (economic nodes).

| file | content | licence and attribution |
|---|---|---|
| `ksa.geojson` | Saudi Arabia, OSM relation 307584, simplified ~100 m | derived database of OpenStreetMap: (c) OpenStreetMap contributors, ODbL 1.0 |
| `regions.geojson` | 13 regions (OSM admin_level 4, ISO 3166-2 codes) | ODbL 1.0, as above |
| `governorates.geojson` | 149 governorate polygons (OSM admin_level 6), region by containment; simplified ~200 m (A-r1a-003) | ODbL 1.0, as above |
| `settlements.parquet` | every OSM place=city/town/village/hamlet node in KSA plus unmatched pilot rows; governorate, region, population with type, source, status, method and licence per row; distance fields | ODbL 1.0 (OSM); WorldPop 2020 grid estimates CC BY 4.0, "WorldPop (www.worldpop.org), University of Southampton, doi:10.5258/SOTON/WP00684"; tabulated figures cite their S- source (GASTAT via aggregators, `secondary`) |
| `economic_nodes.csv` / `.parquet` | 168 nodes (136 located): airport 27, border 12, energy 5, giga-project 11, Hajj/Umrah 10, heritage 8, industrial city 40, mining 10, port 12, tourism 4, university 29; one source id per row | facts cited per row; OSM positions ODbL 1.0; Wikidata positions CC0 |

Populations of type `grid` are **derived estimates** (status `unverified`) and are not census figures; back-test against the tabulated rows: `docs/network.md`. Governorate polygons are OSM boundaries, not GASTAT's official boundaries (GASTAT's primary list was unreachable on 31 Oct 2026; working list `docs/gastat-regions.md`).

- `commute_minutes_r4.parquet` (R4, CP4-5a): register row x metro: straight-line km, OSRM road minutes and km (free flow, national MLD files), rail in-vehicle minutes on the S0 network where an existing line has a station within 10 km of both ends, and `commute_min` = min(road, rail). Built by `uv run python -m screening.commute_r4 minutes --seed 1`; derived from OpenStreetMap (ODbL, (c) OpenStreetMap contributors) via OSRM. Label: screening input, not a forecast.
