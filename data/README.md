# data/ (gitignored)

Nothing here is committed except this file and small licence-compatible tables under `data/ksa/tables/<name>/` that carry their own `README.md` with the licence. `data/osm`, `data/jeddah` and `data/traffictwin` are symlinks into the read-only TrafficTwin checkout (`~/Documents/Projects/TrafficTwin`); never write there. Every file used by the pipeline has a row in `cities/ksa/sources.yaml` with its SHA-256 and access date (`docs/versioning.md`).
