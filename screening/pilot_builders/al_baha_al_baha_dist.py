# ruff: noqa
# Pilot builder script recovered by CP1_PREP (item 4, Q24), 31 Oct 2026.
# Origin: /tmp/al_baha_dist.py (last modified 2026-10-30 22:02 +03, pilot run PILOT_REGION_AL_BAHA).
# Role: distance calculations (printed, copied into the register).
# Outputs named in the code: none written to files.
# Archival copy: absolute paths rewritten to repository-relative ("./") or "~"; logic
# unchanged. It ran in the pilot worktree with network access (Nominatim/Overpass or
# citypopulation.de); re-running it is not part of the test suite.
# Label: pilot, proposed criteria pending CP1; screening input, not a forecast.

import math, json


def hav(a, b):
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(d))


existing = {
    "makkah_central_haramain": (21.4177, 39.7885),
    "jeddah_sulaymaniyah_haramain": (21.5167, 39.2463),
}
metro = {"taif": (21.2703, 40.4158), "abha": (18.2164, 42.5044)}
towns = {
    "Al-Baha": (20.0137941, 41.4656378),
    "Al-Aqiq": (20.2836432, 41.6560108),
    "Al-Hajrah": (20.1997012, 41.0720687),
    "Al-Makhwah": (19.7794440, 41.4355560),
    "Al-Mandaq": (20.1105064, 41.2828451),
    "Baljurashi": (19.861209, 41.560977),
    "Bani Hasan": (20.0534990, 41.3736650),
    "Ghamid az-Zinad": (19.5944390, 41.5201123),
    "Qilwah": (19.9401107, 41.2513010),
}
out = {}
for n, p in towns.items():
    ex = {k: round(hav(p, v), 1) for k, v in existing.items()}
    me = {k: round(hav(p, v), 1) for k, v in metro.items()}
    out[n] = {"existing": ex, "metro": me}
    print(f"{n:18s} existing {ex}  metro {me}")
