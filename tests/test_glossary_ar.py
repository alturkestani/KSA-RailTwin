"""docs/glossary.ar.md (FIX_R8 item 2): the preferred Arabic form of every glossary term appears in
the Arabic executive summary wherever the English summary uses the concept, and no rejected form
appears in any Arabic deliverable (the summary, the Arabic figure titles, Arabic strings in web/
and api/)."""

from __future__ import annotations

import csv
import re

import pytest

from common import REPO_ROOT
from common.figures import SPECS

AR_SUMMARY = REPO_ROOT / "docs/executive-summary.ar.md"
EN_SUMMARY = REPO_ROOT / "docs/executive-summary.en.md"
GLOSSARY = REPO_ROOT / "docs/glossary.ar.md"
ARABIC = re.compile(r"[؀-ۿ]")

# (English trigger in the EN summary, preferred Arabic form). Verbatim from Tariq where the
# glossary says so.
TERMS = [
    ("upside case", "الحالة الأعلى عائداً"),
    ("committed programme", "الملتزم به"),
    ("Robust NPV", "صافي القيمة الحالية الصامد (robust NPV)"),
    ("synthetic", "طلب تركيبي غير مُعايَر"),
    (
        "alignments are indicative",
        "ومسارات الخطوط مخططات تقريبية استرشادية بأقل تكلفة على نموذج تضاريس بدقة 30 م",
    ),
    ("running times", "أزمنة الرحلة"),
    ("judge v3", "نموذج التقييم judge v3"),
    ("seed 1", "بالبذرة العشوائية 1"),
    ("availability PPP", "الشراكة بين القطاعين العام والخاص بنظام مدفوعات الإتاحة"),
    ("every registered parameter range", "عبر جميع نطاقات المَعلَمات المسجَّلة"),
    ("contingent liability", "التزام محتمل (طارئ)"),
    ("private cushion", "هامش الحماية لدى الشريك الخاص"),
    ("net fiscal cost", "صافي التكلفة على المالية العامة"),
    ("commuter belt", "حزام لقطارات الضواحي حول الرياض"),
    ("reach alternative", "بديل التغطية الأوسع"),
    ("Al-Kharj spur", "الخط الفرعي إلى الخرج"),
    ("fares cover", "إيرادات التذاكر"),
    ("who sets passenger fares", "الجهة التي تحدد تعرفة تذاكر الركاب"),
    ("GCC Railway", "سكة حديد دول مجلس التعاون الخليجي"),
    ("screening every region", "فرز جميع المناطق والمحافظات"),
    ("host line's procurement", "ضمن عقد طرح الخط المضيف"),
    (
        "wider economic impacts, freight and foreign visitors",
        "أما الآثار الاقتصادية الأوسع والشحن والزوار من خارج المملكة فلا تدخل في ترتيب الخيارات.",
    ),
    (
        "Draft, pending native-speaker review",
        "مسودة بانتظار مراجعة لغوية من متحدث أصلي (طارق)؛ لا تُستخدم خارج المستودع قبل اعتمادها.",
    ),
    ("fielded survey", "استبيان ميداني"),
]

# Rejected forms (regex), never in an Arabic deliverable.
REJECTED = {
    "أجور (ticket revenue)": r"أجور",
    "مسح (screening)": r"مسح",
    "المتفائلة (upside)": r"المتفائلة",
    "المتين (robust)": r"المتين|متين",
    "القيمة الحالية الصامدة (wrong agreement)": r"القيمة الحالية الصامدة",
    "اصطناعي (synthetic)": r"اصطناعي",
    "رسوم استرشادية (alignments)": r"رسوم استرشادية",
    "أزمنة التشغيل (travel times)": r"أزمنة التشغيل",
    "المحكم (judge)": r"المُحكِّم|المحكم",
    "البذرة without العشوائية": r"البذرة(?! العشوائية)",
    "دفعات / القائمة على الإتاحة (availability PPP)": r"دفعات الإتاحة|القائمة على الإتاحة",
    "الشراكة مع القطاع الخاص": r"الشراكة مع القطاع الخاص",
    "نطاق مسجَّل للمعاملات": r"نطاق مسجَّل للمعاملات",
    "التزام احتمالي": r"التزام احتمالي",
    "هامش الشريك الخاص": r"هامش الشريك الخاص",
    "صافي التكلفة المالية": r"صافي التكلفة المالية",
    "الركاب اليوميين": r"الركاب اليوميين",
    "بديل الوصول": r"بديل الوصول",
    "فرع الخرج": r"(?<!ال)فرع الخرج",
    "مجلس التعاون without الخليجي": r"مجلس التعاون(?! الخليجي)",
    "مشتريات الخط المضيف": r"مشتريات الخط المضيف",
    "القادمون من الخارج / خارج الترتيب": r"القادمون من الخارج|خارج الترتيب",
    "الملتزم without به/بها": r"الملتزم(?! به| بها)",
}


def _ar_deliverables() -> dict[str, str]:
    """Every Arabic deliverable text (file label -> Arabic text)."""
    out = {"docs/executive-summary.ar.md": AR_SUMMARY.read_text(encoding="utf-8")}
    out["common/figures.py title_ar"] = "\n".join(s.title_ar for s in SPECS)
    with (REPO_ROOT / "docs/deck-figures/figures.csv").open(encoding="utf-8") as fh:
        out["docs/deck-figures/figures.csv title_ar"] = "\n".join(
            r["title_ar"] for r in csv.DictReader(fh)
        )
    for base in ("web/src", "api"):
        for p in sorted((REPO_ROOT / base).rglob("*")):
            if p.suffix in {".ts", ".tsx", ".py", ".json", ".html"} and p.is_file():
                text = p.read_text(encoding="utf-8", errors="ignore")
                if ARABIC.search(text):
                    out[str(p.relative_to(REPO_ROOT))] = text
    return out


def test_glossary_file_lists_every_preferred_form() -> None:
    text = GLOSSARY.read_text(encoding="utf-8")
    assert text.startswith("> **Document version:** docs/glossary.ar.md v")
    for _, ar in TERMS:
        assert ar.split(" (robust NPV)")[0] in text, ar
    assert "§typography" in text


@pytest.mark.parametrize(("en", "ar"), TERMS, ids=[t[0] for t in TERMS])
def test_preferred_form_where_the_concept_is_used(en: str, ar: str) -> None:
    en_text = EN_SUMMARY.read_text(encoding="utf-8")
    ar_text = AR_SUMMARY.read_text(encoding="utf-8")
    if en in en_text:
        assert ar in ar_text, f"concept '{en}' is in the EN summary but '{ar}' not in the AR one"


@pytest.mark.parametrize(("name", "pattern"), list(REJECTED.items()), ids=list(REJECTED))
def test_rejected_form_absent(name: str, pattern: str) -> None:
    hits = [
        f"{label}: …{m.group(0)}…"
        for label, text in _ar_deliverables().items()
        for m in re.finditer(pattern, text)
    ]
    assert not hits, f"rejected form {name}: {hits}"


def test_robust_npv_glossed_once_then_alone() -> None:
    text = AR_SUMMARY.read_text(encoding="utf-8")
    term = "صافي القيمة الحالية الصامد"
    assert text.count(f"{term} (robust NPV)") == 1
    assert text.index(term) == text.index(f"{term} (robust NPV)")
    assert text.count(term) > 1
    assert "robust NPV" not in text.replace(f"{term} (robust NPV)", "")
