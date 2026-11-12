#!/usr/bin/env bash
# R4_ALIGN: OpenStreetMap layers for the alignment cost surface, extracted from the GCC PBF
# (manifest row osm-gcc-2026-10-14) with osmium-tool (GPL-3.0, called as an external CLI only).
# Output: data/ksa/align/osm/<layer>.{osm.pbf,geojsonseq} (gitignored; manifest rows osm-align-*).
# Map data (c) OpenStreetMap contributors, ODbL.  Usage: ./network/align_osm.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PBF=data/osm/gcc-states-latest.osm.pbf
O=data/ksa/align/osm
mkdir -p $O
osmium tags-filter -O -o $O/landuse-urban.osm.pbf $PBF wa/landuse=residential,commercial,retail,industrial
osmium tags-filter -O -o $O/protected.osm.pbf $PBF wr/boundary=protected_area,national_park wr/leisure=nature_reserve
osmium tags-filter -O -o $O/military.osm.pbf $PBF wa/landuse=military wa/military
osmium tags-filter -O -o $O/waterways.osm.pbf $PBF w/waterway=river,stream,wadi,canal,drain,ditch
osmium tags-filter -O -o $O/highways.osm.pbf $PBF w/highway=motorway,trunk,primary,motorway_link,trunk_link
osmium tags-filter -O -o $O/natural.osm.pbf $PBF wa/natural=sand,wetland,beach,water,dune wa/wetland
for n in landuse-urban protected military waterways highways natural; do
  osmium export -O -f geojsonseq --geometry-types=polygon,linestring,multipolygon \
    -o $O/$n.geojsonseq $O/$n.osm.pbf
done
