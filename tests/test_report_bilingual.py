"""common.sources bilingual-check: normalisation, multiset comparison, CLI exit codes, and the
real executive summaries."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest
from typer.testing import CliRunner

from common import REPO_ROOT
from common.sources import LABEL_LINE, app, compare, tokens

HEADER = "> **Document version:** x v0.1 | 4 Nov 2026 | Author: test | Status: draft\n\n"

EN = HEADER + (
    "# Summary\n\n"
    "In the model, NPV at P90 cost is −2,958 / −724 / +1,631 SAR m; BCR P10 1.52; 41.2 %.\n"
    "Phases 2030 and 2050; ranges 3–10 km; see [run](runs/r6/top5/top5.csv) and https://x.org/9.\n"
    f"{LABEL_LINE}\n"
)
AR_WESTERN = HEADER + (
    "# الملخص\n\n"
    "في النموذج، صافي القيمة الحالية عند تكلفة P90 هو −2,958 / −725 / 1,631 مليون ريال؛ "
    "نسبة المنافع P10 هي 1.52؛ 41.2 ٪.\n"
    "المرحلتان 2030 و2050؛ النطاق 3–10 كم؛ انظر [التشغيل](runs/r6/top5/top5.csv).\n"
    f"{LABEL_LINE}\n"
    "> التسميات: ... انحراف 3–10 كم ... ±5 ٪ ... 30 م ...\n"
)
AR_INDIC = HEADER + (
    "في النموذج: −٢٬٩٥٨ / −٧٢٤ / ١٬٦٣١؛ P10 ١٫٥٢؛ ٤١٫٢ ٪؛ ٢٠٣٠ و٢٠٥٠؛ ٣–١٠ كم.\n"
    "> التسميات: ٣–١٠ كم، ±٥ ٪، ٣٠ م.\n"
    f"{LABEL_LINE}\n"
)


def _write(tmp: Path, name: str, text: str) -> Path:
    p = tmp / name
    p.write_text(text, encoding="utf-8")
    return p


def test_normalisation_and_signs() -> None:
    t = tokens("x\n−2,958 and 3–10, S6-L1, A-cba-301, (−5) 1٬234٫5 ٪ +1,631 2031–2035\n")
    assert t == Counter(
        {
            "-2958": 1,
            "3": 1,
            "10": 1,
            "6": 1,
            "1": 1,
            "301": 1,
            "-5": 1,
            "1234.5": 1,
            "1631": 1,
            "2031": 1,
            "2035": 1,
        }
    )


def test_header_links_and_urls_skipped() -> None:
    t = tokens(HEADER + "see [a 7](runs/r6/x9.csv) <https://a.b/42> https://c.d/88 end\n")
    assert t == Counter({"7": 1})


def test_label_line_skipped_only_in_arabic() -> None:
    en = HEADER + LABEL_LINE + "\n"
    ar = HEADER + LABEL_LINE + "\n" + "> ٣–١٠ كم ±٥ ٪ ٣٠ م\n"
    missing_ar, missing_en = compare(en, ar)
    assert not missing_ar and not missing_en


def test_fixture_pass_western_digits(tmp_path: Path) -> None:
    en_label_only = HEADER + LABEL_LINE + "\n"
    ar = HEADER + LABEL_LINE + "\n> التسميات: 3–10 كم، ±5 ٪، 30 م.\n"
    res = CliRunner().invoke(
        app,
        [
            "bilingual-check",
            str(_write(tmp_path, "e.md", en_label_only)),
            str(_write(tmp_path, "a.md", ar)),
        ],
    )
    assert res.exit_code == 0, res.output
    assert "PASS" in res.output


def test_fixture_pass_indic_digits(tmp_path: Path) -> None:
    en = HEADER + (
        "In the model: −2,958 / −724 / +1,631; P10 1.52; 41.2 %; 2030 and 2050; 3–10 km.\n"
        f"{LABEL_LINE}\n"
    )
    res = CliRunner().invoke(
        app,
        [
            "bilingual-check",
            str(_write(tmp_path, "e.md", en)),
            str(_write(tmp_path, "a.md", AR_INDIC)),
        ],
    )
    assert res.exit_code == 0, res.output


def test_fixture_fail_reports_missing_and_extra(tmp_path: Path) -> None:
    res = CliRunner().invoke(
        app,
        [
            "bilingual-check",
            str(_write(tmp_path, "e.md", EN)),
            str(_write(tmp_path, "a.md", AR_WESTERN)),
        ],
    )
    # The Arabic fixture writes −725 for −724 (a real mismatch); 1,631 without '+' is the same
    # value, the URL is skipped and the Arabic label rendering balances the English label line.
    assert res.exit_code == 1
    assert "FAIL" in res.output
    assert "-724" in res.output and "-725" in res.output
    assert "1631" not in res.output


def test_multiset_not_set() -> None:
    missing_ar, missing_en = compare(HEADER + "7 and 7\n", HEADER + "٧ فقط\n")
    assert missing_ar == Counter({"7": 1}) and not missing_en


def test_sign_mismatch_is_a_difference() -> None:
    missing_ar, missing_en = compare(HEADER + "−724\n", HEADER + "724\n")
    assert missing_ar == Counter({"-724": 1}) and missing_en == Counter({"724": 1})


@pytest.mark.parametrize("stem", ["executive-summary"])
def test_real_executive_summaries_match(stem: str) -> None:
    en = REPO_ROOT / "docs" / f"{stem}.en.md"
    ar = REPO_ROOT / "docs" / f"{stem}.ar.md"
    if not (en.exists() and ar.exists()):
        pytest.skip("executive summaries not written yet")
    missing_ar, missing_en = compare(en.read_text(encoding="utf-8"), ar.read_text(encoding="utf-8"))
    assert not missing_ar and not missing_en, (missing_ar, missing_en)
    assert sum(tokens(en.read_text(encoding="utf-8")).values()) > 50
