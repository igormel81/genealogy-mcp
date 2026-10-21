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


PARTICLES = {"de", "del", "de la", "y", "e", "da", "do", "dos", "das", "van", "von", "der", "di", "la", "le", "du"}


def _parts(value):
    """'Pérez García' → ['Pérez', 'García']; 'de la Cruz y Sánchez' → ['Cruz', 'Sánchez']. Hispanic records carry the
    father's and the mother's surname (Portuguese: mother's, then father's); one shared part is a match."""
    words = [w for w in re.split(r"[\s-]+", str(value)) if w and w.lower() not in PARTICLES]
    return words or [str(value)]


def _name_match(a, b, kind):
    if not a or not b:
        return None
    if kind == "surname":
        pa, pb = _parts(a), _parts(b)
        if len(pa) > 1 or len(pb) > 1:
            return any(_forms(x, kind) & _forms(y, kind) for x in pa for y in pb)
    return bool(_forms(a, kind) & _forms(b, kind))


def _year(v):
    m = re.search(r"\d{4}", str(v or ""))
    return int(m[0]) if m else None


def _place_match(a, b):
    if not a or not b:
        return None
    qualifier = r"\b(\w+)\s+(губерния|область|уезд|район|province|district|gubernia|uezd)\b"
    qa = {kind: name for name, kind in re.findall(qualifier, _norm(a))}
    qb = {kind: name for name, kind in re.findall(qualifier, _norm(b))}
    if any(qa[k] != qb[k] for k in qa.keys() & qb.keys()):
        return False

    def words(value):
        text = _norm(value)
        # A shared province is not a shared village. Remove labelled administrative
        # qualifiers, but keep settlement names; never match just a five-letter prefix.
        text = re.sub(r"\b\w+\s+(?:губерния|область|уезд|район|province|district|gubernia|uezd)\b", " ", text)
        stop = {"village", "село", "деревня", "д", "с", "город", "г", "town", "city", "parish", "приход"}
        return set(text.split()) - stop
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return None
    return wa <= wb or wb <= wa


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
            res = "match" if ok else "conflict"
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
    if {"birth_place", "residence"} <= independent and all(
        _place_match(row.get("birth_place"), row.get("residence")) is True for row in (known, found)
    ):
        independent.discard("residence")
    if name_ok is False:
        verdict = "different_person"
        why = ("Фамилия не сходится ни в одном из вариантов написания." if ru else "The surname does not match in any spelling variant.")
    elif given_ok is False:
        verdict = "conflict"
        conflicts.append("given")
        why = ("Имена различаются; без документа, объясняющего смену имени или прозвище, совпадение не подтверждено."
               if ru else "Given names differ; a record explaining the name change or alias is needed before linking them.")
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
