"""Other calendars in old records: church feasts («на Покров», «в Петров пост»), Easter, the Hebrew calendar
(Jewish metric books and tombstones) and the French Republican calendar (France and its conquests, 1793–1805)."""
import datetime
import re

from .dates import _from_jdn, _jdn_greg, _jdn_jul


def _iso(y, m, d):
    return f"{y:04d}-{m:02d}-{d:02d}"


def julian_to_gregorian(y, m, d):
    return _from_jdn(_jdn_jul(y, m, d), julian=False)


def gregorian_to_julian(y, m, d):
    return _from_jdn(_jdn_greg(y, m, d), julian=True)


# ---------------------------------------------------------------- Easter

def orthodox_easter(year):
    """Julian-calendar date of Orthodox Easter (Pascha)."""
    a, b, c = year % 4, year % 7, year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month = (d + e + 114) // 31
    day = (d + e + 114) % 31 + 1
    return year, month, day


def western_easter(year):
    """Gregorian-calendar date of Catholic / Protestant Easter."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    month = (h + l_ - 7 * m + 114) // 31
    day = (h + l_ - 7 * m + 114) % 31 + 1
    return year, month, day


# ---------------------------------------------------------------- feasts

# key → (names people write, Julian (month, day) for Orthodox or offset from Easter, English name)
FIXED = {
    "christmas": (("рождество", "рождество христово", "christmas", "boże narodzenie", "crăciun", "navidad"), (12, 25), "Christmas"),
    "epiphany": (("крещение", "богоявление", "epiphany", "trzech króli", "boboteaza"), (1, 6), "Epiphany / Theophany"),
    "presentation": (("сретение", "candlemas", "presentation", "matki boskiej gromnicznej"), (2, 2), "Presentation (Candlemas)"),
    "annunciation": (("благовещение", "annunciation", "zwiastowanie", "buna vestire"), (3, 25), "Annunciation"),
    "st_george_spring": (("егорий вешний", "юрьев день вешний", "георгий победоносец", "st george", "św. wojciecha"), (4, 23), "St George (spring)"),
    "st_nicholas_spring": (("никола вешний", "николай вешний", "никола летний"), (5, 9), "St Nicholas (spring)"),
    "nativity_john": (("рождество иоанна предтечи", "иван купала", "иванов день", "midsummer", "st john baptist", "świętego jana", "sânziene"), (6, 24), "Nativity of John the Baptist"),
    "peter_paul": (("петров день", "петра и павла", "petrov den", "peter and paul", "piotra i pawła"), (6, 29), "Sts Peter and Paul"),
    "elijah": (("ильин день", "илья пророк", "elijah"), (7, 20), "St Elijah"),
    "transfiguration": (("преображение", "яблочный спас", "spas", "transfiguration"), (8, 6), "Transfiguration"),
    "dormition": (("успение", "dormition", "assumption", "wniebowzięcie", "adormirea"), (8, 15), "Dormition / Assumption"),
    "beheading_john": (("усекновение", "иван постный"), (8, 29), "Beheading of John the Baptist"),
    "nativity_theotokos": (("рождество богородицы", "богородичен день", "nativity of mary", "narodzenie najświętszej", "sfânta maria mică"), (9, 8), "Nativity of the Theotokos"),
    "exaltation": (("воздвижение", "exaltation of the cross", "podwyższenie krzyża", "ziua crucii"), (9, 14), "Exaltation of the Cross"),
    "protection": (("покров", "покров пресвятой богородицы", "pokrov", "protection of the theotokos"), (10, 1), "Protection of the Theotokos (Pokrov)"),
    "kazan_icon": (("казанская", "казанской иконы"), (10, 22), "Kazan Icon of the Mother of God"),
    "dmitry": (("дмитриев день", "димитрий солунский", "dimitrie"), (10, 26), "St Demetrius"),
    "cosmas_damian": (("кузьминки", "кузьма и демьян", "козьма и дамиан"), (11, 1), "Sts Cosmas and Damian"),
    "michael": (("михайлов день", "архангела михаила", "michaelmas", "sf. mihail"), (11, 8), "Archangel Michael"),
    "entry_temple": (("введение", "введение во храм", "entry into the temple", "presentation of mary", "intrarea în biserică"), (11, 21), "Entry of the Theotokos into the Temple"),
    "st_george_autumn": (("юрьев день", "егорий осенний", "егорий зимний"), (11, 26), "St George (autumn), Yuri's Day"),
    "st_nicholas_winter": (("никола зимний", "николин день", "николай чудотворец", "st nicholas", "mikołaja", "sf. nicolae"), (12, 6), "St Nicholas"),
}
MOVABLE = {   # offset in days from Easter
    "maslenitsa_sunday": (("прощёное воскресенье", "прощеное воскресенье", "масленица", "cheesefare sunday"), -49, "Forgiveness Sunday (end of Maslenitsa)"),
    "lent_start": (("великий пост", "чистый понедельник", "clean monday", "начало великого поста"), -48, "Clean Monday, start of Great Lent"),
    "ash_wednesday": (("ash wednesday", "popielec", "пепельная среда"), -46, "Ash Wednesday (Western)"),
    "lazarus_saturday": (("лазарева суббота",), -8, "Lazarus Saturday"),
    "palm_sunday": (("вербное воскресенье", "вход господень в иерусалим", "palm sunday", "niedziela palmowa", "florii"), -7, "Palm Sunday"),
    "good_friday": (("страстная пятница", "великая пятница", "good friday", "wielki piątek"), -2, "Good Friday"),
    "easter": (("пасха", "светлое воскресенье", "easter", "pascha", "wielkanoc", "paște", "pascua"), 0, "Easter"),
    "radonitsa": (("радоница", "radonitsa"), 9, "Radonitsa (day of the dead)"),
    "ascension": (("вознесение", "ascension", "wniebowstąpienie", "înălțarea"), 39, "Ascension"),
    "trinity": (("троица", "троицын день", "пятидесятница", "pentecost", "whitsun", "zielone świątki", "rusalii"), 49, "Pentecost / Trinity"),
    "spirit_day": (("духов день", "whit monday"), 50, "Whit Monday / Spirit Day"),
    "all_saints_orthodox": (("неделя всех святых",), 56, "All Saints Sunday (Orthodox)"),
    "petrov_fast_start": (("петров пост", "апостольский пост"), 57, "Start of the Apostles' (Peter's) Fast"),
    "corpus_christi": (("corpus christi", "boże ciało"), 60, "Corpus Christi (Western)"),
}
FASTS = {   # Orthodox fasts with fixed Julian dates (inclusive)
    "uspensky_fast": (("успенский пост", "dormition fast"), (8, 1), (8, 14), "Dormition Fast"),
    "filippov_fast": (("филиппов пост", "рождественский пост", "nativity fast", "advent"), (11, 15), (12, 24), "Nativity (Philip's) Fast"),
}


def _stem(w):
    """A crude stem so that Russian cases match: «Петрова поста» ~ «петров пост», «Николу зимнего» ~ «никола зимний»."""
    return w[:4]


def _same(query, alias):
    q, a = query.split(), alias.replace("ё", "е").split()
    return len(q) == len(a) and all(_stem(x) == _stem(y) for x, y in zip(q, a))


def _lookup(name):
    n = " ".join(name.lower().replace("ё", "е").split())
    n = re.sub(r"^(на|в|во|под|после|до|перед|к|on|at|before|after|na|w|we|po|przed|de|la)\s+", "", n)
    for table in (FIXED, MOVABLE, FASTS):
        for key, spec in table.items():
            if n == key or any(n == w.replace("ё", "е") or _same(n, w) or (len(n) > 4 and n in w.replace("ё", "е")) for w in spec[0]):
                return table, key, spec
    return None, None, None


def feast_date(feast, year, church="orthodox"):
    """The date of a church feast or fast in a year, in both calendars. Orthodox feasts are kept by the Julian
    calendar (the date a Russian register gives); Catholic ones by the Gregorian."""
    year = int(year)
    table, key, spec = _lookup(feast)
    if not table:
        return {"error": f"unknown feast {feast!r}", "known": sorted(list(FIXED) + list(MOVABLE) + list(FASTS))}
    orthodox = church.lower().startswith(("o", "п", "r"))
    if table is FIXED:
        m, d = spec[1]
        dates = [(year, m, d)]
    elif table is MOVABLE:
        ey, em, ed = orthodox_easter(year) if orthodox else western_easter(year)
        base = datetime.date(ey, em, ed) + datetime.timedelta(days=spec[1])
        dates = [(base.year, base.month, base.day)]
        if key == "petrov_fast_start":
            dates.append((year, 6, 28))
    else:
        dates = [(year, *spec[1]), (year, *spec[2])]
    out = []
    for y, m, d in dates:
        if orthodox:
            g = julian_to_gregorian(y, m, d)
            out.append({"julian": _iso(y, m, d), "gregorian": _iso(*g)})
        else:
            j = gregorian_to_julian(y, m, d)
            out.append({"gregorian": _iso(y, m, d), "julian": _iso(*j)})
    res = {"feast": spec[-1], "key": key, "year": year, "church": "orthodox" if orthodox else "catholic"}
    if len(out) == 1:
        res.update(out[0])
    else:
        res.update({"from": out[0], "to": out[1]})
    if orthodox:
        res["note"] = ("A Russian (or other Orthodox) register before 1918 gives the Julian date; "
                       "convert to Gregorian for a modern tree only if you mark it as converted.")
    return res


# ---------------------------------------------------------------- Hebrew calendar (Calendrical Calculations)

HEBREW_EPOCH = -1373427   # R.D. of 1 Tishrei AM 1
HEB_MONTHS = {1: "Nisan", 2: "Iyar", 3: "Sivan", 4: "Tammuz", 5: "Av", 6: "Elul", 7: "Tishrei", 8: "Cheshvan", 9: "Kislev",
              10: "Tevet", 11: "Shevat", 12: "Adar", 13: "Adar II"}
HEB_ALIASES = {"nissan": 1, "iyyar": 2, "tamuz": 4, "ab": 5, "tishri": 7, "heshvan": 8, "marcheshvan": 8, "cheshvan": 8,
               "kislew": 9, "teves": 10, "tebet": 10, "shvat": 11, "sh'vat": 11, "adar i": 12, "adar 1": 12, "adar ii": 13,
               "adar 2": 13, "adar sheni": 13, "нисан": 1, "ияр": 2, "сиван": 3, "таммуз": 4, "тамуз": 4, "ав": 5, "элул": 6,
               "тишрей": 7, "хешван": 8, "мархешван": 8, "кислев": 9, "тевет": 10, "шват": 11, "адар": 12, "адар ii": 13, "адар бет": 13}


def heb_leap(y):
    return (7 * y + 1) % 19 < 7


def _elapsed(y):
    months = (235 * y - 234) // 19
    parts = 12084 + 13753 * months
    days = 29 * months + parts // 25920
    return days + 1 if (3 * (days + 1)) % 7 < 3 else days


def _delay(y):
    ny0, ny1, ny2 = _elapsed(y - 1), _elapsed(y), _elapsed(y + 1)
    return 2 if ny2 - ny1 == 356 else 1 if ny1 - ny0 == 382 else 0


def heb_new_year(y):
    return HEBREW_EPOCH + _elapsed(y) + _delay(y)


def _month_len(m, y):
    days = heb_new_year(y + 1) - heb_new_year(y)
    if m in (2, 4, 6, 10, 13) or (m == 12 and not heb_leap(y)) or (m == 8 and days % 10 != 5) or (m == 9 and days % 10 == 3):
        return 29
    return 30


def _months(y):
    """Months of year y in order, from Tishrei."""
    last = 13 if heb_leap(y) else 12
    return list(range(7, last + 1)) + list(range(1, 7))


def fixed_from_hebrew(y, m, d):
    rd = heb_new_year(y)
    for mm in _months(y):
        if mm == m:
            return rd + d - 1
        rd += _month_len(mm, y)
    raise ValueError("no such month in this year")


def hebrew_from_fixed(rd):
    y = (rd - HEBREW_EPOCH) * 98496 // 35975351
    while heb_new_year(y + 1) <= rd:
        y += 1
    while heb_new_year(y) > rd:
        y -= 1
    start = heb_new_year(y)
    for m in _months(y):
        n = _month_len(m, y)
        if rd < start + n:
            return y, m, rd - start + 1
        start += n
    raise AssertionError


def _heb_month(name):
    n = name.strip().lower()
    if n.isdigit():
        return int(n)
    for k, v in HEB_MONTHS.items():
        if v.lower() == n:
            return k
    return HEB_ALIASES.get(n)


def hebrew_to_gregorian(text):
    """'15 Nisan 5784' / '15 нисан 5784' → the Gregorian date (the day begins at the previous sunset)."""
    m = re.fullmatch(r"\s*(\d{1,2})\s+(.+?)\s+(\d{4})\s*", text)
    if not m or not _heb_month(m[2]):
        raise ValueError("format: '15 Nisan 5784'")
    y, mon, d = int(m[3]), _heb_month(m[2]), int(m[1])
    if mon == 12 and heb_leap(y) and "ii" not in m[2].lower():
        pass   # Adar in a leap year means Adar I
    if mon == 13 and not heb_leap(y):
        mon = 12
    rd = fixed_from_hebrew(y, mon, d)
    g = datetime.date.fromordinal(rd)
    return {"hebrew": f"{d} {HEB_MONTHS[mon] if not (mon == 12 and heb_leap(y)) else 'Adar I'} {y}",
            "gregorian": g.isoformat(), "julian": _iso(*gregorian_to_julian(g.year, g.month, g.day)),
            "note": "A Hebrew day starts at sunset: an event 'on the night of' may fall on the previous civil date."}


def gregorian_to_hebrew(date):
    y, m, d = map(int, re.fullmatch(r"\s*(\d{4})-(\d{1,2})-(\d{1,2})\s*", str(date)).groups())
    hy, hm, hd = hebrew_from_fixed(datetime.date(y, m, d).toordinal())
    name = "Adar I" if hm == 12 and heb_leap(hy) else HEB_MONTHS[hm]
    return {"gregorian": _iso(y, m, d), "hebrew": f"{hd} {name} {hy}"}


# ---------------------------------------------------------------- French Republican calendar (An I – An XIV)

REP_MONTHS = ["Vendémiaire", "Brumaire", "Frimaire", "Nivôse", "Pluviôse", "Ventôse", "Germinal", "Floréal", "Prairial",
              "Messidor", "Thermidor", "Fructidor", "jours complémentaires"]
ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10, "xi": 11, "xii": 12, "xiii": 13, "xiv": 14}
SEXTILE = {3, 7, 11}   # years with a sixth complementary day


def _rep_new_year(an):
    d = datetime.date(1792, 9, 22)
    for y in range(1, an):
        d += datetime.timedelta(days=366 if y in SEXTILE else 365)
    return d


def republican_to_gregorian(text):
    """'18 Brumaire an VIII' → 1799-11-09. Valid for An I (1792) – An XIV (1805)."""
    m = re.fullmatch(r"\s*(\d{1,2})\s+([^\d]+?)\s+(?:an\s+)?([ivxlIVXL]+|\d{1,2})\s*", text, flags=re.I)
    if not m:
        raise ValueError("format: '18 Brumaire an VIII'")
    an = int(m[3]) if m[3].isdigit() else ROMAN.get(m[3].lower())
    month = next((i for i, n in enumerate(REP_MONTHS) if n.lower().replace("ô", "o").replace("é", "e")[:4] ==
                  m[2].strip().lower().replace("ô", "o").replace("é", "e")[:4]), None)
    if not an or not 1 <= an <= 14 or month is None:
        raise ValueError("unknown month or year (An I – An XIV)")
    day = int(m[1])
    g = _rep_new_year(an) + datetime.timedelta(days=month * 30 + day - 1)
    return {"republican": f"{day} {REP_MONTHS[month]} an {an}", "gregorian": g.isoformat()}


def gregorian_to_republican(date):
    g = datetime.date.fromisoformat(str(date).strip())
    for an in range(1, 15):
        start, end = _rep_new_year(an), _rep_new_year(an + 1)
        if start <= g < end:
            n = (g - start).days
            return {"gregorian": g.isoformat(), "republican": f"{n % 30 + 1} {REP_MONTHS[n // 30]} an {an}"}
    raise ValueError("the Republican calendar was used from 22 Sep 1792 to 31 Dec 1805")
