#!/usr/bin/env bash
# GEO_VERIFY clean rerun (docs/geo-verify.md section 1). Run from anywhere; cds to the repo root.
set -e
cd "$(dirname "$0")/../../.."
R="uv run --with rasterio python -m screening.geo_verify.cli"
$R backtest --seed 1
uv run --with rasterio python -m screening.geo_verify.scripts.geo_sweep
$R estimate --seed 1 --which no-pop
$R estimate --seed 1 --which secondary
$R stations --seed 1
G="محافظة القرى"
$R seat --seed 1 --lat 29.8833333 --lon 40.2166667 --governorate-ar "$G" --label AlQara:wikidata-Q65040833
$R seat --seed 1 --lat 20.2507795 --lon 41.3503986 --governorate-ar "$G" --label AlQara:osm-label-4975708122
$R seat --seed 1 --lat 20.2475218 --lon 41.3607144 --governorate-ar "$G" --label AlQara:osm-seat-9327998071
$R seat --seed 1 --lat 20.394 --lon 41.328 --governorate-ar "$G" --label AlQara:citypopulation-S-cp1-005
G="محافظة وادي الدواسر"
$R seat --seed 1 --lat 20.4602516 --lon 44.799553 --governorate-ar "$G" --label WadiDawasir:osm-city-2632133047
$R seat --seed 1 --lat 20.482531 --lon 44.7672925 --governorate-ar "$G" --label WadiDawasir:osm-village-AlKhamasin-1236411997
$R validate-geocodes --seed 1
$R served-rerun --seed 1
$R apply-notes --seed 1
