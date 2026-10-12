"""Is the person in a found record the one we are looking for? The rule: a name is never enough —
a match needs at least two independent facts beyond the name (parents, spouse, place, year, children, estate)
and no conflict that cannot be explained."""
import re
import unicodedata

from . import names

INDEPENDENT = {   # field → (label en, label ru)
    "father_given": ("father's given name", "имя отца"), "mother_given": ("mother's given name", "имя матери"),
    "mother_surname": ("mother's maiden name", "девичья фамилия матери"),
    "spouse_given": ("spouse's given name", "имя супруга(и)"), "spouse_surname": ("spouse's surname", "фамилия супруга(и)"),
    "birth_year": ("year of birth", "год рождения"), "birth_place": ("place of birth", "место рождения"),
    "residence": ("place of residence", "место жительства"), "death_year": ("year of death", "год смерти"),
    "children": ("children's names", "имена детей"), "occupation": ("occupation or estate", "занятие или сословие"),
    "patronymic": ("patronymic", "отчество"),
}


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode() if re.search(r"[a-z]", str(s or "").lower()) else str(s or "")
    s = s.lower().replace("ё", "е").replace("ъ", "").replace("і", "и").replace("ѣ", "е")
    return re.sub(r"[^\w ]+", " ", s).strip()


def _forms(value, kind):
    if not value:
        return set()
    v = str(value).strip()
    forms = {v} | set(names.all_forms(v, kind, limit=60))
    if kind == "given":
        forms |= set(names.given_equivalents(v))
    return {_norm(x) for x in forms if x}


def _name_match(a, b, kind):
    if not a or not b:
        return None
    return bool(_forms(a, kind) & _forms(b, kind))


def _year(v):
    m = re.search(r"\d{4}", str(v or ""))
    return int(m[0]) if m else None


def _place_match(a, b):
    if not a or not b:
        return None
    wa, wb = set(_norm(a).split()), set(_norm(b).split())
    stop = {"village", "село", "деревня", "д", "с", "уезд", "губерния", "uezd", "gubernia", "province", "district", "parish", "приход"}
    wa, wb = wa - stop, wb - stop
    if not wa or not wb:
        return None
    # one shared distinctive word (a village name) is a match; also allow prefix matches for case endings
    return any(x == y or (len(x) > 4 and len(y) > 4 and (x.startswith(y[:5]) or y.startswith(x[:5]))) for x in wa for y in wb)


def check_match(known, found, year_tolerance=3, lang="en"):
    """known / found: {"given", "surname", "patronymic", "father_given", "mother_given", "mother_surname", "spouse_given",
    "spouse_surname", "birth_year", "birth_place", "residence", "death_year", "children": [...], "occupation"}.
    Returns the verdict with every compared fact."""
    ru = lang == "ru"
    rows, matches, conflicts = [], [], []

    name_ok = _name_match(known.get("surname"), found.get("surname"), "surname")
    given_ok = _name_match(known.get("given"), found.get("given"), "given")
    for field, ok, label in (("surname", name_ok, ("surname", "фамилия")), ("given", given_ok, ("given name", "имя"))):
        if ok is not None:
            rows.append({"field": field, "label": label[1 if ru else 0], "known": known.get(field), "found": found.get(field),
                         "result": "match" if ok else "differs"})

    for field, label in INDEPENDENT.items():
        a, b = known.get(field), found.get(field)
        if not a or not b:
            continue
        if field in ("birth_year", "death_year"):
            ya, yb = _year(a), _year(b)
            if ya is None or yb is None:
                continue
            diff = abs(ya - yb)
            res = "match" if diff <= year_tolerance else "near" if diff <= year_tolerance + 4 else "conflict"
        elif field in ("birth_place", "residence"):
            ok = _place_match(a, b)
            if ok is None:
                continue
            res = "match" if ok else "differs"
        elif field == "children":
            ka = [x for x in (a if isinstance(a, list) else re.split(r"[,;]", a)) if x.strip()]
            kb = [x for x in (b if isinstance(b, list) else re.split(r"[,;]", b)) if x.strip()]
            hits = sum(1 for x in ka if any(_name_match(x.strip(), y.strip(), "given") for y in kb))
            res = "match" if hits >= 2 or (hits == 1 and min(len(ka), len(kb)) == 1) else "near" if hits == 1 else "differs"
        elif field == "occupation":
            res = "match" if _norm(a) == _norm(b) or _norm(a) in _norm(b) or _norm(b) in _norm(a) else "differs"
        else:
            kind = "surname" if field.endswith("surname") else "patronymic" if field == "patronymic" else "given"
            if field == "patronymic":
                ok = _name_match(a, b, "patronymic") or _norm(a)[:4] == _norm(b)[:4]
            else:
                ok = _name_match(a, b, kind)
            res = "match" if ok else "conflict" if field in ("father_given", "mother_given", "patronymic") else "differs"
        rows.append({"field": field, "label": label[1 if ru else 0], "known": a, "found": b, "result": res})
        if res == "match":
            matches.append(field)
        elif res == "conflict":
            conflicts.append(field)

    # patronymic and father's name are one fact, birth and residence place too when they are equal
    independent = set(matches)
    if {"patronymic", "father_given"} <= independent:
        independent.discard("patronymic")
    if name_ok is False:
        verdict = "different_person"
        why = ("Фамилия не сходится ни в одном из вариантов написания." if ru else "The surname does not match in any spelling variant.")
    elif conflicts:
        verdict = "conflict"
        why = ((f"Противоречие: {', '.join(INDEPENDENT[c][1] for c in conflicts)}. Скорее всего, другой человек — или ошибка писаря; "
                "нужен третий документ.") if ru else
               (f"Conflict in: {', '.join(INDEPENDENT[c][0] for c in conflicts)}. Most likely another person — or a clerk's error; "
                "a third document is needed."))
    elif len(independent) >= 2:
        verdict = "confirmed"
        why = ("Совпадают два и больше независимых факта кроме имени — можно считать тем же человеком. Запишите, какие именно, "
               "и сошлитесь на снимок документа." if ru else
               "Two or more independent facts besides the name agree — the same person. Record which ones and cite the image.")
    elif len(independent) == 1:
        verdict = "probable"
        why = ("Совпадает один факт кроме имени — «вероятно». Ищите второй: родители, супруг, дети, двор, сословие."
               if ru else "One fact besides the name agrees — 'probable'. Look for a second one: parents, spouse, children, household, estate.")
    else:
        verdict = "insufficient"
        why = ("Совпадает только имя. Однофамилец — не родственник: без второго факта запись не связывать."
               if ru else "Only the name agrees. A namesake is not a relative: do not attach the record without more facts.")
    return {"verdict": verdict, "independent_matches": sorted(independent), "conflicts": conflicts, "explanation": why, "compared": rows}
