"""Dates as people write them → ISO / GEDCOM; Julian ↔ Gregorian; a birth year from an age."""
import datetime
import re

GED_MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
RU_MONTHS = ["январ", "феврал", "март", "апрел", "ма", "июн", "июл", "август", "сентябр", "октябр", "ноябр", "декабр"]
EN_MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
# Spanish, Portuguese, German, French, Polish, Romanian, Latin month stems (Latin American and European records)
OTHER_MONTHS = [
    ("ene", "jän", "janv", "janeir", "stycz", "ianuar", "januar"), ("febr", "fevere", "févr", "fév", "luty", "lut", "februar"),
    ("marz", "març", "mars", "márz", "marc", "martie", "martius"), ("abr", "avr", "kwie", "aprilie", "aprilis"),
    ("mayo", "mai", "maio", "maj", "maius"), ("jun", "juin", "junh", "czerw", "iunie", "iunius"),
    ("jul", "juil", "lip", "iulie", "iulius"), ("agost", "août", "aout", "sierp", "augustus"),
    ("sept", "setem", "wrze", "septem"), ("oct", "okt", "outu", "paźdz", "pazdz", "octob"),
    ("nov", "listop", "noiem", "novem"), ("dic", "déc", "dez", "dezem", "grud", "decem"),
]
QUALIFIERS = ((("около", "ок.", "ок", "приблизительно", "примерно", "about", "abt", "circa", "ca.", "c.", "hacia", "cerca de", "um", "vers", "około", "ok."), "ABT"),
              (("до", "ранее", "before", "bef", "antes de", "vor", "avant", "przed"), "BEF"),
              (("после", "позднее", "after", "aft", "después de", "despues de", "nach", "après", "apres", "po"), "AFT"),
              (("вычислено", "calculated", "cal"), "CAL"), (("est", "estimated", "оценочно"), "EST"))


def _month(word):
    w = word.lower().strip(".")
    for i, m in enumerate(EN_MONTHS):
        if w.startswith(m):
            return i
    for i, m in enumerate(RU_MONTHS):
        if w.startswith(m) and (i != 4 or w in ("мая", "май", "ма")):
            return i
    for i, stems in enumerate(OTHER_MONTHS):
        if any(w.startswith(s) for s in stems):
            return i
    return None


def _valid(y, mo=1, d=1):
    try:
        datetime.date(int(y), int(mo), int(d))
        return True
    except ValueError:
        return False


def _simple(text):
    """One date without qualifiers → ISO ('1899-10-09', '1899-10', '1899') or GEDCOM ('9 OCT 1899'), or None."""
    t = text.strip().rstrip(".").strip()
    t = re.sub(r"\s*(г|года?|г\.|r\.|roku|año|ano|jahr)\.?$", "", t, flags=re.I).strip()
    t = re.sub(r"\s+(de|del|do|da|w)\s+", " ", t, flags=re.I)   # «9 de octubre de 1899», «9 de outubro de 1899»
    if re.fullmatch(r"\d{4}", t):
        return t
    m = re.fullmatch(r"(\d{4})-(\d{1,2})(?:-(\d{1,2}))?", t)
    if m:
        return (f"{m[1]}-{int(m[2]):02d}" + (f"-{int(m[3]):02d}" if m[3] else "")) if _valid(m[1], m[2], m[3] or 1) else None
    m = re.fullmatch(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})", t)
    if m:
        return f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}" if _valid(m[3], m[2], m[1]) else None
    m = re.fullmatch(r"(\d{1,2})[./-](\d{4})", t)
    if m:
        return f"{m[2]}-{int(m[1]):02d}" if _valid(m[2], m[1]) else None
    m = re.fullmatch(r"(?:(\d{1,2})\.?\s+)?([^\d\s]+)\.?,?\s+(\d{3,4})", t)
    if m and _month(m[2]) is not None:
        mon = _month(m[2])
        if m[1] and not _valid(m[3], mon + 1, m[1]):
            return None
        return (f"{int(m[1])} " if m[1] else "") + GED_MONTHS[mon] + " " + m[3]
    m = re.fullmatch(r"([^\d\s]+)\s+(\d{1,2}),?\s+(\d{4})", t)   # October 9, 1899
    if m and _month(m[1]) is not None and _valid(m[3], _month(m[1]) + 1, m[2]):
        return f"{int(m[2])} {GED_MONTHS[_month(m[1])]} {m[3]}"
    return None


def _ged(inner):
    """ISO → GEDCOM (qualifiers need GEDCOM dates)."""
    if "-" not in inner:
        return inner
    y, *rest = inner.split("-")
    return " ".join(([str(int(rest[1]))] if len(rest) > 1 else []) + ([GED_MONTHS[int(rest[0]) - 1]] if rest else []) + [y])


def normalize_date(text):
    """'около 1899' → 'ABT 1899', 'между 1900 и 1905' → 'BET 1900 AND 1905', '9.10.1899' → '1899-10-09'.
    Returns None when the text is not understood."""
    t = " ".join(str(text or "").split())
    if not t:
        return None
    low = t.lower()
    m = re.fullmatch(r"(?:между|between|bet|entre|zwischen|entre|między|miedzy)\s+(.+?)\s+(?:и|and|y|e|und|et|a)\s+(.+)", low) \
        or re.fullmatch(r"(\d{4})\s*(?:[–—-]|\.\.)\s*(\d{4})", low)
    if m:
        a, b = _simple(m[1]), _simple(m[2])
        if a and b:
            return f"BET {_ged(a)} AND {_ged(b)}"
    for words, code in QUALIFIERS:
        for w in words:
            if low.startswith(w + " "):
                inner = _simple(t[len(w) + 1:])
                if inner:
                    return f"{code} {_ged(inner)}"
    if re.fullmatch(r"(abt|bef|aft|cal|est|bet|from)\b.*", low):
        return t.upper()
    return _simple(t)


# ---------------------------------------------------------------- calendars

def _jdn_greg(y, m, d):
    a = (14 - m) // 12
    y2, m2 = y + 4800 - a, m + 12 * a - 3
    return d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


def _jdn_jul(y, m, d):
    a = (14 - m) // 12
    y2, m2 = y + 4800 - a, m + 12 * a - 3
    return d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - 32083


def _from_jdn(j, julian):
    if julian:
        b, c = 0, j + 32082
    else:
        a = j + 32044
        b = (4 * a + 3) // 146097
        c = a - 146097 * b // 4
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return year, month, day


def _ymd(date):
    m = re.fullmatch(r"\s*(\d{4})-(\d{1,2})-(\d{1,2})\s*", str(date))
    if not m:
        iso = _simple(str(date))
        m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", iso or "")
        if not m and iso and re.fullmatch(r"\d{1,2} [A-Z]{3} \d{4}", iso):
            d, mon, y = iso.split()
            return int(y), GED_MONTHS.index(mon) + 1, int(d)
    if not m:
        raise ValueError(f"need a full date (day, month, year): {date!r}")
    y, mo, d = map(int, m.groups())
    return y, mo, d


def convert_calendar(date, to="gregorian"):
    """Julian ('old style') ↔ Gregorian ('new style'). Russia switched in 1918 (1 Feb O.S. became 14 Feb),
    Romania and Bulgaria in 1919/1916, Greece in 1923; Catholic Europe and Latin America in 1582–1587."""
    y, m, d = _ymd(date)
    if to.lower().startswith(("g", "н", "new")):
        y2, m2, d2 = _from_jdn(_jdn_jul(y, m, d), julian=False)
    else:
        y2, m2, d2 = _from_jdn(_jdn_greg(y, m, d), julian=True)
    diff = abs(_jdn_greg(y, m, d) - _jdn_jul(y, m, d))
    return {"input": f"{y:04d}-{m:02d}-{d:02d}", "result": f"{y2:04d}-{m2:02d}-{d2:02d}", "to": "gregorian" if to.lower().startswith(("g", "н", "new")) else "julian",
            "difference_days": diff}


def birth_year_from_age(age, on_date):
    """'aged 45 at the census of 1897-01-28' → the birth falls in two possible years; ages in old records
    are often rounded, so a wider estimate is given as well."""
    m = re.search(r"\d{4}", str(on_date))
    if not m:
        raise ValueError(f"need a date or a year: {on_date!r}")
    year = int(m[0])
    age = float(age)
    a = int(age)
    exact = (year - a - 1, year - a)   # the birthday may be before or after the record
    return {"exact": f"BET {exact[0]} AND {exact[1]}", "loose": f"BET {year - a - 3} AND {year - a + 2}", "gedcom": f"CAL {year - a}",
            "note": "Ages in census, confession and death records are often rounded to 0 or 5 and drift by 2–5 years between records; "
                    "use the loose range when you compare records."}
