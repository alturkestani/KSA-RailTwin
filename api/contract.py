"""Dashboard contract constants (contract v1.0, documented in `api/README.md`).

Nothing here is a modelling constant: the labels are imported from `common.labels`, the judge hash
is the one recorded in `docs/r6/judge-hashes.md` (row `v3-variants`), the central appraisal row is
the ranking basis of `docs/cba.md` (A-cba-001, A-cba-004), and the framing is Tariq's decision at
the R7 checkpoint (`prompts/R8.md`, "R7-checkpoint answers", item 1).
"""

from __future__ import annotations

from common.labels import ALIGNMENT_LIMITATION, LABEL

CONTRACT_VERSION = "1.0"

JUDGE = {
    "version": "v3-variants",
    "sha256": "d9fef64384e2e25f84b288962907fa25e2476d9749bf863d7bd6fb66fb70f9ee",
    "source": "docs/r6/judge-hashes.md",
}
SEED = 1

OSM_CREDIT = "© OpenStreetMap contributors"

# docs/cba.md "Ranking basis": UN WPP medium, 60 years, Green Book 2026 declining (A-cba-001/004).
CENTRAL_ROW = {"population": "un_wpp_medium", "horizon": 60, "rate_case": "greenbook_2026"}
POPULATIONS = ("un_wpp_low", "un_wpp_medium", "un_wpp_high")
POP_SHORT = {"un_wpp_low": "low", "un_wpp_medium": "medium", "un_wpp_high": "high"}

# The four map layers. Rule 5: planned lines are never drawn in the "existing" style.
LAYERS = {
    "existing": "existing",
    "committed": "committed/under procurement",
    "hypothetical": "hypothetical (ours)",
    "historical": "historical",
}

TRADE_OFF_CAPTION = "trade-off illustration only: no recommendation"
# S6-L6 (R8_L6_PANEL, Tariq 6 Nov 2026): a connectivity comparison from the connecting-set search,
# not a reach trade-off and not a search result. Pareto view only; difference mode refuses it.
COMPARISON_CAPTION = "comparison layout, not the recommended programme"
COMPARISON_LAYOUTS = ("S6-L6",)

# R7-checkpoint answer 1 (Tariq, 4 Nov 2026). All three are presented against S1.
FRAMING: dict[str, dict[str, object]] = {
    "S6-L2": {"role": "central case", "trade_off_only": False},
    "S6-L1": {
        "role": "upside case that carries the Al-Kharj spur's P90 cost risk",
        "trade_off_only": False,
    },
    "S6-L3": {"role": "reach alternative", "trade_off_only": False},
    "S6-L4": {"role": TRADE_OFF_CAPTION, "trade_off_only": True},
    "S6-L5": {"role": TRADE_OFF_CAPTION, "trade_off_only": True},
    "S6-L6": {"role": COMPARISON_CAPTION, "trade_off_only": True},
}


def caption(layout: str) -> str | None:
    """The caption a layout carries wherever it appears (None for S1 and the CP7 layouts)."""
    if layout in COMPARISON_LAYOUTS:
        return COMPARISON_CAPTION
    frame = FRAMING.get(layout)
    return TRADE_OFF_CAPTION if frame and frame["trade_off_only"] else None


BASELINE = "S1"
BASELINE_RUN = "runs/cba/CBA-S1-committed-programme"


def envelope(**body: object) -> dict[str, object]:
    """Every response that carries modelled numbers: both labels first, then the body."""
    return {"label": LABEL, "alignment_limitation": ALIGNMENT_LIMITATION, **body}
