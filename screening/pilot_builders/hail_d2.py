# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/hail-scratch/d2.py (last modified 2026-10-30 21:24 +03, pilot run PILOT_REGION_HAIL).
# Role: distance calculations (printed, copied into the register).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import sys

sys.path.insert(0, ".")
from dist import hav

hail_station = (41.7554194, 27.6835926)
north = [
    ("Hail station", hail_station),
    ("Al-Qassim station", (44.0915573, 26.4922762)),
    ("Majmaah station", (45.4197342, 25.9207722)),
    ("Al-Jawf station", (39.8376771, 29.6485411)),
]
targets = {
    "Hail city": (41.6986, 27.5209),
    "Al-Ghazalah": (41.3157, 26.7875),
    "Ash-Shamli": (40.3239, 26.8629),
    "Ash-Shanan": (42.4439, 27.175),
    "As-Sulaymi": (41.3596, 26.2903),
    "Baqa": (42.3899, 27.9103),
    "Mawqaq": (41.1756, 27.3858),
    "Simira": (42.1249, 26.4942),
    "Turubah": (42.9204, 28.2596),
    "Jubbah": (40.953, 28.0169),
    "Al-Qaid": (41.725, 27.846),
}
for k, v in targets.items():
    print(k, [(n, round(hav(v, c), 1)) for n, c in north])
