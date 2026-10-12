"""Shared DNA (autosomal centimorgans) → the relationships it fits.

Averages and ranges are approximate values from the Shared cM Project 4.0 (Blaine T. Bettinger, March 2020,
CC BY 4.0; https://thegeneticgenealogist.com, interactive tool: https://dnapainter.com/tools/sharedcmv4).
Ranges are the 99th-percentile spans of thousands of submitted matches: overlap is huge, so a number
always fits several relationships — documents decide which.
"""

# key → (average cM, low, high, English name, Russian name, (up, down) or None)
TABLE = [
    ("parent_child", 3485, 2376, 3720, "parent / child", "родитель / ребёнок", (1, 0)),
    ("full_sibling", 2613, 1613, 3488, "full sibling", "родной брат / сестра", (1, 1)),
    ("grandparent", 1754, 984, 2462, "grandparent / grandchild", "дед, бабушка / внук, внучка", (2, 0)),
    ("aunt_uncle", 1741, 1201, 2282, "aunt, uncle / niece, nephew", "дядя, тётя / племянник, племянница", (2, 1)),
    ("half_sibling", 1759, 1160, 2436, "half-sibling", "брат / сестра по одному родителю", None),
    ("great_grandparent", 887, 485, 1486, "great-grandparent", "прадед, прабабушка / правнук", (3, 0)),
    ("great_aunt_uncle", 850, 330, 1467, "great-aunt / great-uncle", "двоюродный дед, двоюродная бабушка / внучатый племянник", (3, 1)),
    ("half_aunt_uncle", 871, 492, 1315, "half-aunt / half-uncle", "дядя, тётя по одному из родителей", None),
    ("first_cousin", 866, 396, 1397, "first cousin", "двоюродный брат / сестра", (2, 2)),
    ("half_first_cousin", 449, 156, 979, "half first cousin", "двоюродный брат / сестра по одному из родителей", None),
    ("first_cousin_1r", 433, 102, 980, "first cousin once removed", "двоюродный дядя, тётя / двоюродный племянник", (2, 3)),
    ("first_cousin_2r", 221, 33, 471, "first cousin twice removed", "двоюродный дед / двоюродный внучатый племянник", (2, 4)),
    ("second_cousin", 229, 41, 592, "second cousin", "троюродный брат / сестра", (3, 3)),
    ("second_cousin_1r", 122, 14, 353, "second cousin once removed", "троюродный дядя, тётя / троюродный племянник", (3, 4)),
    ("third_cousin", 73, 0, 234, "third cousin", "четвероюродный брат / сестра", (4, 4)),
    ("third_cousin_1r", 48, 0, 192, "third cousin once removed", "четвероюродный дядя / племянник", (4, 5)),
    ("fourth_cousin", 35, 0, 139, "fourth cousin", "пятиюродный брат / сестра", (5, 5)),
    ("fifth_cousin", 25, 0, 117, "fifth cousin", "шестиюродный брат / сестра", (6, 6)),
]
SOURCE = "Shared cM Project 4.0 (Bettinger, 2020, CC BY 4.0) — approximate; check on dnapainter.com/tools/sharedcmv4"


def _name(key, en, rus, gen, lang):
    """Names in both directions from the kinship module (so they agree with the `kinship` tool)."""
    if not gen:
        return rus if lang == "ru" else en
    from . import kinship
    a, b = kinship.name(*gen, "U", lang), kinship.name(gen[1], gen[0], "U", lang)
    return a if a == b else f"{a} — {b}"


def fits(cm, lang="en"):
    """Relationships whose range contains `cm`, nearest average first."""
    cm = float(cm)
    ru = lang == "ru"
    out = []
    for key, avg, lo, hi, en, rus, gen in TABLE:
        if lo <= cm <= hi:
            out.append({"relationship": _name(key, en, rus, gen, lang), "key": key, "average_cm": avg, "range_cm": [lo, hi]})
    out.sort(key=lambda r: abs(r["average_cm"] - cm))
    total = 6800   # shared-cM scale used by testing companies (both copies of ~3400 cM)
    note = ("Ниже 20 сМ совпадение может быть ложным или очень дальним; общий предок ищется только по документам."
            if ru else "Below 20 cM a match may be false or very distant; only documents identify the common ancestor.") if cm < 20 else ""
    if cm > 3720:
        note = ("Больше, чем у родителя с ребёнком: возможно, это вы сами или однояйцевый близнец."
                if ru else "More than parent and child: probably the same person or an identical twin.")
    return {"cm": cm, "percent_shared": round(cm / total * 100, 2), "fits": out, "note": note, "source": SOURCE}
