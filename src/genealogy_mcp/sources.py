"""The catalogue of genealogy sources (data/sources.json): search by country, years and kind of record."""
import json
import re
from functools import lru_cache
from importlib import resources
from urllib.parse import quote

RECORD_KINDS = {
    "church": ("parish registers: baptisms, marriages, burials", "метрические книги: крещения, браки, погребения"),
    "vital": ("civil registration: births, marriages, deaths", "гражданская регистрация: рождения, браки, смерти"),
    "census": ("censuses and population lists", "переписи и списки населения"),
    "revision": ("revision lists (tax censuses of the Russian Empire)", "ревизские сказки"),
    "confession": ("confession lists (annual parish rolls)", "исповедные ведомости"),
    "household": ("household books and cards", "похозяйственные книги и подворные карточки"),
    "military": ("military records", "военные документы"),
    "repression": ("victims of political repression", "жертвы политических репрессий"),
    "deportation": ("deportations", "депортации"),
    "holocaust": ("victims of the Holocaust", "жертвы Холокоста"),
    "forced_labour": ("forced labour", "принудительный труд"),
    "displaced": ("displaced persons", "перемещённые лица"),
    "emigration": ("emigration and immigration, passenger lists", "эмиграция и иммиграция, списки пассажиров"),
    "newspapers": ("newspapers", "газеты"),
    "directories": ("directories, address calendars, memorial books", "справочники, адрес-календари, памятные книжки"),
    "books": ("digitised books", "оцифрованные книги"),
    "graves": ("graves and cemeteries", "захоронения и кладбища"),
    "trees": ("family trees of other researchers", "чужие семейные деревья"),
    "catalogs": ("archive catalogues and guides", "каталоги и путеводители архивов"),
    "places": ("places: history, gazetteers", "места: история, справочники"),
    "maps": ("old maps", "старые карты"),
    "clergy": ("clergy", "духовенство"),
    "nobility": ("nobility and officials", "дворянство и чиновники"),
}
REGIONS = {   # names people use → ISO country codes
    "europe": "AT BE BG BY CH CZ DE DK EE ES FI FR GB GR HR HU IE IT LT LV MD NL NO PL PT RO RS RU SE SI SK UA",
    "eastern_europe": "BY EE LT LV MD PL RO RU UA",
    "western_europe": "AT BE DE FR GB IE IT NL ES PT",
    "scandinavia": "DK FI NO SE",
    "latin_america": "AR BO BR CL CO CR CU EC GT MX PE PY UY VE",
    "russian_empire": "RU UA BY PL LT LV EE MD FI",
    "ussr": "RU UA BY MD LT LV EE KZ UZ KG TJ TM GE AM AZ",
    "central_asia": "KZ UZ KG TJ TM",
    "caucasus": "GE AM AZ RU",
    "north_america": "US CA MX",
    "oceania": "AU NZ",
    "balkans": "BG RO RS HR SI GR",
    "british_isles": "GB IE",
}
COUNTRY_NAMES = {
    "russia": "RU", "россия": "RU", "рф": "RU", "ukraine": "UA", "украина": "UA", "belarus": "BY", "беларусь": "BY", "белоруссия": "BY",
    "moldova": "MD", "молдова": "MD", "молдавия": "MD", "бессарабия": "MD", "bessarabia": "MD", "romania": "RO", "румыния": "RO",
    "poland": "PL", "польша": "PL", "lithuania": "LT", "литва": "LT", "latvia": "LV", "латвия": "LV", "estonia": "EE", "эстония": "EE",
    "ireland": "IE", "ирландия": "IE", "united kingdom": "GB", "uk": "GB", "england": "GB", "scotland": "GB", "wales": "GB",
    "великобритания": "GB", "англия": "GB", "шотландия": "GB", "usa": "US", "united states": "US", "сша": "US", "америка": "US",
    "germany": "DE", "германия": "DE", "austria": "AT", "австрия": "AT", "france": "FR", "франция": "FR", "italy": "IT", "италия": "IT",
    "spain": "ES", "испания": "ES", "portugal": "PT", "португалия": "PT", "netherlands": "NL", "нидерланды": "NL", "голландия": "NL",
    "belgium": "BE", "бельгия": "BE", "sweden": "SE", "швеция": "SE", "norway": "NO", "норвегия": "NO", "denmark": "DK", "дания": "DK",
    "finland": "FI", "финляндия": "FI", "hungary": "HU", "венгрия": "HU", "czechia": "CZ", "чехия": "CZ", "slovakia": "SK", "словакия": "SK",
    "israel": "IL", "израиль": "IL", "mexico": "MX", "мексика": "MX", "brazil": "BR", "бразилия": "BR", "argentina": "AR", "аргентина": "AR",
    "chile": "CL", "чили": "CL", "peru": "PE", "перу": "PE", "colombia": "CO", "колумбия": "CO", "cuba": "CU", "куба": "CU",
    "uruguay": "UY", "уругвай": "UY", "paraguay": "PY", "парагвай": "PY", "venezuela": "VE", "венесуэла": "VE",
    "ecuador": "EC", "эквадор": "EC", "bolivia": "BO", "боливия": "BO",
    "canada": "CA", "канада": "CA", "australia": "AU", "австралия": "AU", "new zealand": "NZ", "новая зеландия": "NZ",
    "bulgaria": "BG", "болгария": "BG", "serbia": "RS", "сербия": "RS", "croatia": "HR", "хорватия": "HR",
    "slovenia": "SI", "словения": "SI", "greece": "GR", "греция": "GR", "switzerland": "CH", "швейцария": "CH",
    "georgia": "GE", "грузия": "GE", "armenia": "AM", "армения": "AM", "azerbaijan": "AZ", "азербайджан": "AZ",
    "kazakhstan": "KZ", "казахстан": "KZ", "uzbekistan": "UZ", "узбекистан": "UZ", "kyrgyzstan": "KG", "киргизия": "KG",
    "кыргызстан": "KG", "tajikistan": "TJ", "таджикистан": "TJ", "turkmenistan": "TM", "туркмения": "TM", "туркменистан": "TM",
    "средняя азия": "central_asia", "central asia": "central_asia", "кавказ": "caucasus", "caucasus": "caucasus",
    "north america": "north_america", "северная америка": "north_america", "балканы": "balkans", "balkans": "balkans",
    "европа": "europe", "латинская америка": "latin_america", "south america": "latin_america", "южная америка": "latin_america",
    "российская империя": "russian_empire", "ссср": "ussr", "soviet union": "ussr",
}
ACCESS = {"free": ("free", "бесплатно"), "free_account": ("free, sign-in needed", "бесплатно, нужен вход"), "paid": ("paid", "платно"),
          "request": ("by request (letter, visit)", "по запросу (письмо, визит)"), "mixed": ("partly free", "частично бесплатно")}


@lru_cache(maxsize=1)
def catalogue():
    return json.loads(resources.files("genealogy_mcp").joinpath("data/sources.json").read_text(encoding="utf-8"))


def countries(where):
    """'Ukraine', 'UA', 'europe', 'Латинская Америка' → a set of ISO codes (empty = anywhere)."""
    out = set()
    for part in re.split(r"[,;/]+", where or ""):
        p = part.strip()
        if not p:
            continue
        key = COUNTRY_NAMES.get(p.lower(), p)
        if key.lower() in REGIONS:
            out |= set(REGIONS[key.lower()].split())
        elif re.fullmatch(r"[A-Za-z]{2}", key):
            out.add(key.upper())
    return out


def find(country="", year_from=None, year_to=None, records=None, text="", include_worldwide=True):
    """Sources that cover the country (or region), overlap the years and hold the kinds of records."""
    codes = countries(country)
    kinds = set(records or [])
    out = []
    for s in catalogue():
        c = set(s["countries"])
        if codes and not (c & codes) and not (include_worldwide and "*" in c):
            continue
        if year_from and s["years"][1] < int(year_from):
            continue
        if year_to and s["years"][0] > int(year_to):
            continue
        if kinds and not kinds & set(s["records"]):
            continue
        if text and text.lower() not in json.dumps(s, ensure_ascii=False).lower():
            continue
        out.append(s)
    # sources of the country itself first, worldwide ones after
    out.sort(key=lambda s: (0 if codes & set(s["countries"]) else 1))
    return out


def link(s, given="", surname="", year_from=None, year_to=None, place="", q=""):
    """A search link for sources that have a URL template; empty fields are dropped from the query."""
    tpl = s.get("search")
    if not tpl:
        return None
    q = q or " ".join(x for x in (given, surname, place) if x)
    values = {"given": given, "surname": surname, "year_from": year_from or "", "year_to": year_to or "", "place": place, "q": q}
    url = tpl
    for k, v in values.items():
        url = url.replace("{" + k + "}", quote(str(v)))
    url = re.sub(r"[?&][\w.]+=(?=&|$)", "", url).replace("?&", "?")   # drop empty parameters
    if "?" not in url and "&" in url:
        url = url.replace("&", "?", 1)
    return url


def describe(s, lang="en"):
    ru = lang == "ru"
    kinds = ", ".join(RECORD_KINDS.get(k, (k, k))[1 if ru else 0] for k in s["records"])
    access = ACCESS.get(s["access"], (s["access"], s["access"]))[1 if ru else 0]
    years = f"{s['years'][0]}–{s['years'][1]}"
    where = ", ".join("весь мир" if c == "*" and ru else "worldwide" if c == "*" else c for c in s["countries"])
    lines = [f"**{s['name']}** — {s['url'] or ('без сайта' if ru else 'no website')}",
             f"{'Что' if ru else 'What'}: {s['about_ru' if ru else 'about']}",
             f"{'Записи' if ru else 'Records'}: {kinds}; {years}; {where}; {access}.",
             f"{'Как искать' if ru else 'How to search'}: {s['how_ru' if ru else 'how']}"]
    return "\n".join(lines)
