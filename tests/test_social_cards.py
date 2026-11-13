"""SOCIAL_CARDS (Tariq, 12 Nov 2026): the social cards' text (docs/publish/social-cards.csv);
cards 6 and 7 added by PUBLISH_PDF_POST (13 Nov 2026); card 8 by FIX_PDF_CONNECTED (13 Nov 2026).

Always: eight cards in both languages, no finance jargon (English and Arabic forms) anywhere on a
card, at most 25 words of body per card (footer, credits, legend and map labels excluded), the
footer and the OSM credit on every card. With the local run outputs: every figure on a card equals
the value `film.cards.figures()` computes from the cited file, rounded as the card rounds it. With
the external volume: sixteen 1080x1350 PNGs.
"""

from __future__ import annotations

import pytest
from PIL import Image

from film import cards
from tests.localdata import needs_local

ROWS = cards.load_cards()


def test_eight_cards_two_languages() -> None:
    keys = sorted((int(r["card"]), r["lang"]) for r in ROWS)
    assert keys == [(c, lg) for c in range(1, 9) for lg in ("ar", "en")]


def test_card8_traces_the_connected_network() -> None:
    """Card 8 (FIX_PDF_CONNECTED): S6-L6 route-km, cost middle and range, riyals back per riyal,
    16 corridors and 18 required cities, all checked by `expected` (no figure unchecked)."""
    F = {
        8: {
            "km": 3241.87,
            "l6_p10": 122532.0,
            "l6_p50": 227213.0,
            "l6_p90": 860035.3,
            "l6": 0.06097,
            "corridors": 16.0,
            "cities": 18.0,
        }
    }
    assert cards.expected(8, "en", F) == {"3,242", "123", "227", "860", "0.06", "16", "18"}
    for lang in cards.LANGS:
        assert cards.check_numbers(cards.card_row(8, lang), F) == []
    assert cards.card_name(8, "en") == "card8-connected-en"
    assert len(cards.l6_required_cities()) == 18


@pytest.mark.parametrize("row", ROWS, ids=lambda r: f"card{r['card']}-{r['lang']}")
def test_no_jargon_and_short(row: dict[str, str]) -> None:
    assert cards.jargon_hits(cards.all_text(row)) == []
    assert cards.word_count(row) <= cards.MAX_WORDS


def test_jargon_check_catches_barred_terms() -> None:
    for bad in ("NPV 4,982", "BCR P50", "capex P90", "present value", "صافي القيمة الحالية"):
        assert cards.jargon_hits(bad), bad
    assert cards.jargon_hits("riyals back per riyal spent; كم ريال يرجع لكل ريال") == []


def test_footer_and_credit() -> None:
    assert "github.com/alturkestani/KSA-RailTwin" in cards.FOOTER["en"]
    assert "github.com/alturkestani/KSA-RailTwin" in cards.FOOTER["ar"]
    assert "not a government plan" in cards.FOOTER["en"]
    assert "OpenStreetMap" in cards.CREDIT and "ODbL" in cards.CREDIT
    for lang in ("en", "ar"):
        html = cards.foot_html(lang, True)
        assert "OpenStreetMap" in html and "KSA-RailTwin" in html


@needs_local(
    "runs/r6/top5/top5.csv",
    "runs/r6/l6/score/S6-L6.csv",
    "runs/cba/CBA-S1-committed-programme/draws.parquet",
    "runs/study/rj/score/score.csv",
    "runs/study/rj/times-s1/times.csv",
)
def test_every_figure_traces() -> None:
    F = cards.figures()
    assert [p for r in ROWS for p in cards.check_numbers(r, F)] == []


@pytest.mark.skipif(not cards.OUT.exists(), reason="external volume (renders) absent")
def test_pngs_1080x1350() -> None:
    for k in cards.CARDS:
        for lang in cards.LANGS:
            png = cards.OUT / f"{cards.card_name(k, lang)}.png"
            assert png.exists(), png
            assert Image.open(png).size == (cards.CW, cards.CH)
