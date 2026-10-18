"""A birth year estimated from relatives and ages in records, as a GEDCOM date with a ready explanation, and a check
that the ages agree — two records whose ages imply birth years far apart are often two namesakes, not one person.

Rules of thumb (rural Eastern Europe, 18th–early 20th c.): the eldest known child was born when the parent was about
27 (18–45); spouses within about 8 years; siblings within about 8 years of each other's birth; a child is born when the
parents are 18–45; a first marriage at about 22 (16–35). Ages in records drift by 2–5 years and are rounded.
"""
import re

SPAN = {   # relative → (low, centre, high) offsets from the relative's year to the person's birth
    "eldest_child": (-45, -27, -18),
    "spouse": (-8, 0, 8),
    "sibling": (-8, 0, 8),
    "father": (18, 30, 45),
    "mother": (18, 27, 45),
    "first_marriage": (-35, -22, -16),
}
LABEL = {
    "eldest_child": ("the eldest child (born {y}, −27)", "году рождения старшего ребёнка ({y} − 27)"),
    "spouse": ("the spouse (born {y}, ±8)", "году рождения супруга(и) ({y} ± 8)"),
    "sibling": ("a sibling (born {y}, ±8)", "году рождения брата или сестры ({y} ± 8)"),
    "father": ("the father (born {y}, +18…+45)", "году рождения отца ({y} + 18…45)"),
    "mother": ("the mother (born {y}, +18…+45)", "году рождения матери ({y} + 18…45)"),
    "first_marriage": ("the first marriage ({y}, at about 22)", "году первого брака ({y}, около 22 лет)"),
    "age": ("age {a} in {y}{src}", "возрасту в записи {y} г. ({a}{src})"),
}


def _year(v):
    m = re.search(r"\d{4}", str(v if v is not None else ""))
    return int(m[0]) if m else None


def _age_range(age, year):
    a = int(float(age))
    return year - a - 3, year - a, year - a + 2   # loose: rounding and drift


def check_ages(ages, lang="en"):
    """[{age, date, source}] → the birth year each implies and the pairs that cannot be one person."""
    ru = lang == "ru"
    rows = []
    for x in ages or []:
        y = _year(x.get("date") or x.get("year"))
        if y is None or x.get("age") in (None, ""):
            continue
        lo, c, hi = _age_range(x["age"], y)
        rows.append({"age": x["age"], "year": y, "source": x.get("source", ""), "birth": c, "range": [lo, hi]})
    flags = []
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            d = abs(a["birth"] - b["birth"])
            if d <= 5:
                continue
            level = "two_people_likely" if d > 10 else "doubtful"
            what = (f"{a['age']} in {a['year']} → about {a['birth']}; {b['age']} in {b['year']} → about {b['birth']}: {d} years apart"
                    if not ru else
                    f"{a['age']} лет в {a['year']} г. → около {a['birth']}; {b['age']} лет в {b['year']} г. → около {b['birth']}: разница {d} лет")
            why = ((("Too far apart for age drift: most likely two people with the same name (a namesake, a cousin, a father and "
                     "son). Do not merge them: compare parents, spouse and household in each record (check_match).")
                    if level == "two_people_likely" else
                    "More than the usual drift of 2–5 years: check the reading of the age and the other facts before treating "
                    "them as one person.")
                   if not ru else
                   (("Слишком далеко для «плавающего» возраста: скорее всего, это два разных человека с одним именем "
                     "(однофамилец, двоюродный брат, отец и сын). Не объединяйте: сравните родителей, супруга и двор в каждой "
                     "записи (check_match).")
                    if level == "two_people_likely" else
                    "Больше обычного расхождения в 2–5 лет: перепроверьте прочтение возраста и другие факты, прежде чем "
                    "считать это одним человеком."))
            flags.append({"level": level, "records": [a, b], "difference": d, "what": what, "why": why})
    return rows, flags


def estimate(sex="U", eldest_child=None, spouse=None, siblings=None, father=None, mother=None, first_marriage=None,
             ages=None, lang="en"):
    ru = lang == "ru"
    sex = str(sex or "U").upper()[:1].replace("М", "M").replace("Ж", "F")
    basis = []   # (kind, low, centre, high, label)

    def add(kind, value):
        y = _year(value)
        if y is None:
            return
        lo, c, hi = SPAN[kind]
        if kind == "spouse":   # husbands were usually a few years older
            c = 3 if sex == "F" else -3 if sex == "M" else 0
        basis.append((kind, y + lo, y + c, y + hi, LABEL[kind][1 if ru else 0].format(y=y)))

    add("eldest_child", eldest_child)
    add("spouse", spouse)
    for s in (siblings or []):
        add("sibling", s)
    add("father", father)
    add("mother", mother)
    add("first_marriage", first_marriage)
    rows, flags = check_ages(ages, lang)
    for r in rows:
        src = f", {r['source']}" if r["source"] else ""
        basis.append(("age", r["range"][0], r["birth"], r["range"][1], LABEL["age"][1 if ru else 0].format(a=r["age"], y=r["year"], src=src)))
    if not basis:
        raise ValueError("give at least one relative's birth year, a first marriage year or an age in a record")

    lo, hi = max(b[1] for b in basis), min(b[3] for b in basis)
    conflict = None
    if lo > hi:   # the relatives do not agree: keep the most direct evidence
        order = ["age", "father", "mother", "sibling", "eldest_child", "spouse", "first_marriage"]
        best = sorted(basis, key=lambda b: order.index(b[0]))[0]
        conflict = (("These dates do not fit one person: " if not ru else "Эти даты не сходятся на одном человеке: ")
                    + "; ".join(f"{b[4]} → {b[1]}–{b[3]}" for b in basis)
                    + (". The estimate keeps only the most direct one." if not ru else ". В оценке оставлена только самая прямая."))
        lo, hi = best[1], best[3]
        basis_used = [best]
    else:
        basis_used = basis
    basis_all, basis = basis, basis_used
    centres = sorted(min(max(b[2], lo), hi) for b in basis)
    centre = centres[len(centres) // 2]
    gedcom = f"BET {lo} AND {hi}" if hi - lo <= 15 else f"ABT {centre}"
    words = ("; ".join(b[4] for b in basis))
    if ru:
        when = f"между {lo} и {hi} гг." if gedcom.startswith("BET") else f"около {centre} г. (возможно {lo}–{hi})"
        explanation = f"Оценка по {words}: {when}"
    else:
        when = f"between {lo} and {hi}" if gedcom.startswith("BET") else f"about {centre} (possibly {lo}–{hi})"
        explanation = f"Estimated from {words}: {when}."
    out = {"gedcom": gedcom, "range": [lo, hi], "most_likely": centre, "explanation": explanation,
           "basis": [{"from": b[0], "range": [b[1], b[3]], "centre": b[2], "used": b in basis} for b in basis_all],
           "note": ("An estimate, not a fact: save it as the person's birth date only with this explanation, and replace it "
                    "when a record of birth or baptism is found." if not ru else
                    "Это оценка, а не факт: записывайте её как дату рождения только с этим пояснением и заменяйте, когда "
                    "найдётся запись о рождении или крещении.")}
    if conflict:
        out["conflict"] = conflict
    if flags:
        out["age_conflicts"] = flags
    return out


__all__ = ["estimate", "check_ages"]
