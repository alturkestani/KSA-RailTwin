"""R6_V3 judge v3: variant ids pass the LineSpec id pattern (CP7-3, the one-line fix)."""

from __future__ import annotations

import re

from common.schemas import LineSpec
from optimise import layout

PATTERN = re.compile(LineSpec.model_fields["id"].metadata[0].pattern)


def test_plain_corridor_keeps_its_id() -> None:
    assert layout.variant_id({"id": "S3-branch_spur-al-kharj", "phase": 2030}) == (
        "S3-branch_spur-al-kharj"
    )


def test_variant_id_matches_linespec_pattern() -> None:
    items = [
        {"id": "S3-branch_spur-al-kharj", "line_type": "commuter"},
        {"id": "S2-trunk_gap-riyadh-jeddah", "electrified": False},
        {"id": "S3-branch_spur-at-ta-if", "track": "single", "drop_stations": ["at-ta-if"]},
    ]
    for it in items:
        vid = layout.variant_id(it)
        assert re.fullmatch(rf"{re.escape(it['id'])}-v[0-9a-f]{{8}}", vid), vid
        assert PATTERN.fullmatch(vid), vid
        assert "~" not in vid


def test_variant_id_depends_on_variant_fields_only() -> None:
    a = {"id": "S3-branch_spur-al-kharj", "phase": 2030, "line_type": "commuter"}
    b = {"id": "S3-branch_spur-al-kharj", "phase": 2050, "line_type": "commuter"}
    c = {"id": "S3-branch_spur-al-kharj", "phase": 2030, "electrified": False}
    assert layout.variant_id(a) == layout.variant_id(b)
    assert layout.variant_id(a) != layout.variant_id(c)
