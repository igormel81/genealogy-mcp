"""A research plan: which records exist for this country and period, in which order to search them, and where."""
from . import guides, sources

PERIOD_RECORDS = [   # (from, to, countries or "*", kinds, guide) — what to look at, oldest last
    (1918, 2025, "RU UA BY MD", ["vital", "household", "military", "repression"], "household_book"),
    (1941, 1945, "RU UA BY MD LT LV EE", ["military"], "wwii"),
    (1914, 1918, "RU UA BY MD PL LT LV EE", ["military"], "wwi"),
    (1897, 1897, "RU UA BY MD PL LT LV EE", ["census"], "census"),
    (1720, 1920, "RU UA BY MD", ["church", "confession"], "metric_book"),
    (1719, 1858, "RU UA BY", ["revision"], "revision_list"),
    (1790, 1960, "*", ["census"], "census"),
    (1820, 1960, "US CA AR BR UY CL MX", ["emigration"], "passenger_list"),
    (1792, 2025, "FR BE NL IT DE GB IE ES PT PL AT HU RO", ["vital"], "civil_registration_europe"),
    (1500, 1950, "MX BR AR CL PE CO CU UY PY VE EC BO GT CR", ["church", "vital"], "latin_america"),
]


PINNED = ("familysearch_catalog", "familysearch", "archive_org")   # always worth it, whatever the country


def plan(country="", year_from=None, year_to=None, known="", lang="en", limit=20):
    ru = lang == "ru"
    codes = sources.countries(country)
    y1, y2 = int(year_from or 1700), int(year_to or 2000)
    steps = [
        ("Ask the oldest relatives first and collect the home archive (documents, photos with inscriptions, letters, military papers)."
         if not ru else "Сначала расспросите старших родственников и соберите домашний архив (документы, фото с надписями, письма, военные бумаги)."),
        ("Write down what is known as facts with their source; set one question (e.g. «who were the parents of X, born about 1890 in Y»)."
         if not ru else "Запишите известное как факты с источником; поставьте один вопрос («кто родители X, родившегося около 1890 г. в Y»)."),
        ("Pin the place down: what the village/town was called then, its province and district, and its parish."
         if not ru else "Уточните место: как называлось село/город тогда, в какой губернии и уезде, к какому приходу относилось."),
        ("Make the list of name variants (name_variants) and search every source with all of them."
         if not ru else "Составьте варианты имён (name_variants) и ищите во всех источниках по всем вариантам."),
    ]
    records, guide_keys = [], []
    for a, b, where, kinds, gk in PERIOD_RECORDS:
        if b < y1 or a > y2:
            continue
        if where != "*" and codes and not codes & set(where.split()):
            continue
        records += kinds
        if gk not in guide_keys:
            guide_keys.append(gk)
    records = list(dict.fromkeys(records))
    found = sources.find(country, y1, y2, records or None)
    by_access = sorted(found, key=lambda s: (PINNED.index(s["id"]) if s["id"] in PINNED else 9 if codes & set(s["countries"]) else 10, {"free": 0, "free_account": 1, "mixed": 2, "paid": 3, "request": 4}.get(s["access"], 5)))
    steps.append(("Search the free online sources (country first), newest records first — they lead back:"
                  if not ru else "Пройдите бесплатные базы (сначала по стране), от новых записей к старым — они ведут назад:"))
    steps.append(("Check a find against what you know (check_match) before attaching it; keep a log of negative results."
                  if not ru else "Каждую находку проверяйте (check_match), прежде чем добавить в древо; записывайте и отрицательные результаты."))
    steps.append(("Then archives: request what is not online (draft_archive_request); the archive guide tells which fond holds it."
                  if not ru else "Затем архивы: запросите то, чего нет в сети (draft_archive_request); путеводитель архива подскажет фонд."))
    return {
        "question": known,
        "steps": steps,
        "record_kinds": {k: sources.RECORD_KINDS.get(k, (k, k))[1 if ru else 0] for k in records},
        "guides": {k: guides.GUIDES[k]["title"][1 if ru else 0] for k in guide_keys},
        "sources": [{"id": s["id"], "name": s["name"], "url": s["url"], "access": s["access"], "years": s["years"],
                     "how": s["how_ru" if ru else "how"]} for s in by_access[:limit]],
        "more_sources": max(0, len(by_access) - limit),
    }
