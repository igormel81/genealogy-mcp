"""genealogy-mcp: an MCP server that gives an AI assistant a genealogist's toolkit and know-how."""
import json
import re
from importlib import resources as _res
from typing import Annotated, Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from . import __version__, audit, calendars, coverage, dates, dna, evidence, guides, kinship, letters, names, numerals, online, places, plan, soundex, sources
from . import films as film_plan
from . import project as proj

INSTRUCTIONS = """You help people research their family history. Work like a careful genealogist:
1. Start from what the person knows; ask about the oldest relatives, places (village, district, province), dates, documents at home.
2. Pin down the place as it was then (province/district/parish: place_history) and where its records are now
   (where_are_records) — records are arranged by place, not by name.
3. Make name variants (name_variants) and search with all of them: spelling, old orthography, gendered forms, transliterations.
4. Use find_sources / plan_research to pick sources for the country and period; search the open databases yourself
   (search_online) and give the user direct links for the rest (search_links).
   Go through every relevant source, not just the first one with a hit, and say which ones were checked.
5. A name is not a person: before linking a found record, run check_match — two independent facts beyond the name.
6. Cite the original (archive, fond, opis, delo, folio, or film and image), not an index; keep conflicting versions.
7. Old dates: Julian calendar in Russia until 1918 (convert_calendar), dates by church feasts (feast_date), letters as
   numbers (cyrillic_numerals); ages in records drift (birth_year_from_age). DNA: dna_match, then documents.
8. Keep the work in a project (project_view / project_save / project_log): save sources with full citations, people and
   families citing them, open leads, and every search with its result — next time start from project_view.
   If the family has a gene-archive site, pass the path of its folder as the project: you read the archive itself and
   your changes go through its checks and logs. If the tree lives in a program (MyHeritage, Ancestry, Gramps,
   RootsMagic, Family Historian…), pass the path of its GEDCOM export: you read and change that file in place.
   Show the change (dry_run) and get the user's yes before writing.
   Reading registers page by page: ask project_coverage what is still unread, plan with film_reading_plan, and mark
   every book read (complete, partial up to No. …, not found) — never read the same frames twice.
9. Archive requests are drafts (draft_archive_request): the user checks and sends them; never claim a letter was sent.
10. Living people: do not publish details about them; mark guesses as 'probably'.
Answer in the user's language; tools take lang="ru" for Russian texts."""

server = MCPServer("genealogy-mcp", title="Genealogy research toolkit", instructions=INSTRUCTIONS, version=__version__,
                   website_url="https://github.com/igormel81/genealogy-mcp")
ALLOW_FILES = True   # off in HTTP mode
RO = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
Lang = Literal["en", "ru"]


def _source_brief(s, lang):
    ru = lang == "ru"
    return {"id": s["id"], "name": s["name"], "url": s["url"], "countries": s["countries"], "years": s["years"],
            "records": s["records"], "access": sources.ACCESS.get(s["access"], (s["access"],) * 2)[1 if ru else 0],
            "about": s["about_ru" if ru else "about"], "how_to_search": s["how_ru" if ru else "how"],
            **({"has_search_link": True} if s.get("search") else {})}


@server.tool(annotations=RO)
def find_sources(
    country: Annotated[str, Field(description="Country or region: 'Ukraine', 'UA', 'Россия', 'europe', 'latin_america', 'russian_empire'; several separated by commas. Empty = any.")] = "",
    year_from: Annotated[int | None, Field(description="First year of interest")] = None,
    year_to: Annotated[int | None, Field(description="Last year of interest")] = None,
    records: Annotated[list[str] | None, Field(description="Kinds of records: " + ", ".join(sources.RECORD_KINDS))] = None,
    text: Annotated[str, Field(description="Free text to match in names and descriptions")] = "",
    include_worldwide: bool = True,
    lang: Lang = "en",
    limit: int = 25,
) -> dict[str, Any]:
    """Find genealogy databases and archives for a country (or region), period and kind of records — 124 sources across
    Russia and the former USSR, the Caucasus and Central Asia, Eastern, Western and Northern Europe, Germany, the British
    Isles, the Americas, Australia and New Zealand,
    each with what it holds and how to search it well."""
    found = sources.find(country, year_from, year_to, records, text, include_worldwide)
    return {"count": len(found), "sources": [_source_brief(s, lang) for s in found[:limit]], "more": max(0, len(found) - limit),
            "record_kinds": {k: v[1 if lang == "ru" else 0] for k, v in sources.RECORD_KINDS.items()}}


@server.tool(annotations=RO)
def source_details(source_id: str, lang: Lang = "en") -> str:
    """Everything about one source from the catalogue (by id from find_sources): coverage, access, search tips."""
    s = next((x for x in sources.catalogue() if x["id"] == source_id), None)
    if not s:
        return f"Unknown source id {source_id!r}. Use find_sources to list ids."
    return sources.describe(s, lang)


@server.tool(annotations=RO)
def search_links(
    surname: str = "",
    given: str = "",
    country: str = "",
    year_from: int | None = None,
    year_to: int | None = None,
    place: str = "",
    variants: Annotated[bool, Field(description="Also make links for the main spelling variants of the surname")] = True,
) -> dict[str, Any]:
    """Ready search links (open them in a browser) in the sources that take a search URL — FamilySearch, Internet Archive
    full text, Find a Grave, Arolsen, Geneteka, Open List and others — for a name, with the name's variants."""
    srcs = [s for s in sources.find(country, year_from, year_to) if s.get("search")]
    cyr = names._cyr(surname + given)
    forms = [("original", surname, given)]   # (kind, surname, given)
    if variants and surname:
        v = names.variants(surname)
        for g in v.get("gendered", [])[:1]:
            forms.append(("original", g, ""))   # the wife or daughter: any given name
        if cyr:
            for system in ("passport", "german", "polish"):
                forms.append(("latin", names.translit(surname, system), names.translit(given, system)))
            old = " ".join(names.old_orthography(w) for w in surname.split())
            if old != surname:
                forms.append(("old", old, " ".join(names.old_orthography(w) for w in given.split())))
    seen, out = set(), []
    for s in srcs:
        cyrillic_only = "*" not in s["countries"] and set(s["countries"]) <= {"RU", "UA", "BY"}
        for kind, sur, giv in forms:
            if (kind == "latin" and cyrillic_only) or (kind == "old" and s["id"] != "archive_org"):
                continue
            if cyr and kind == "original" and not cyrillic_only and s["id"] not in ("archive_org", "familysearch", "yandex_archive", "openlist"):
                continue   # Western databases index Latin forms
            url = sources.link(s, giv, sur, year_from, year_to, place)
            if url and url not in seen:
                seen.add(url)
                out.append({"source": s["name"], "id": s["id"], "name_form": f"{giv} {sur}".strip(), "url": url})
    return {"links": out, "name_forms": list(dict.fromkeys(f"{g} {x}".strip() for _, x, g in forms)),
            "tip": "Open each link; an index hit is a pointer — open the image of the record and cite it."}


@server.tool(annotations=RO)
def where_are_records(
    place: Annotated[str, Field(description="A historical province or a modern region: «Тульская губерния», 'Volhynia', 'Бессарабия', 'Galicia', «Брянская область», 'Kyiv'")],
    lang: Lang = "en",
) -> dict[str, Any]:
    """Which archives now hold the records (parish registers, revision lists, confession lists, civil records) of a
    province of the Russian Empire, the Kingdom of Poland, Galicia, Bukovina, East Prussia, the Baltics or the Caucasus —
    borders moved, so this is often not the archive of today's region. Also works from a modern region back to the
    historical provinces it was part of."""
    found = places.find(place)
    if not found:
        return {"error": "not found", "tip": ("Find the village's uezd and province first (Wikipedia, «Списки населённых мест», "
                                              "etomesto.ru maps), then ask again with the province."),
                "known": sorted({e["names"][0] for e in places.P})}
    out = []
    for e in found:
        codes = {x["country"] for x in e["now"]}
        fs = [s for s in sources.catalogue() if s["id"] == "familysearch_catalog"]
        srcs = fs + [s for s in sources.find(",".join(codes), include_worldwide=False)
                     if set(s["records"]) & {"church", "revision", "confession", "vital", "catalogs"} and s["url"]]
        out.append({"province": e["names"][0], "other_names": e["names"][1:], "then": e["then"],
                    "now": [f"{x['region']} ({x['country']})" for x in e["now"]], "archives": e["archives"], "note": e["note"],
                    "online": [{"id": s["id"], "name": s["name"], "url": s["url"]} for s in srcs[:8]]})
    tip = ("Номер фонда ищите в путеводителе архива (guides.rusarchives.ru, archives.gov.ua, archives.gov.by) или в каталоге "
           "FamilySearch по месту; метрики — фонд духовной консистории, ревизские сказки — казённой палаты."
           if lang == "ru" else
           "Find the fond number in the archive's guide (guides.rusarchives.ru, archives.gov.ua, archives.gov.by) or in the "
           "FamilySearch catalogue by place: parish registers are in the consistory's fond, revision lists in the treasury chamber's.")
    return {"matches": out, "tip": tip}


NET = ToolAnnotations(readOnlyHint=True, openWorldHint=True)


@server.tool(annotations=NET)
def search_online(
    source: Annotated[Literal["internet_archive", "chronicling_america", "wikitree", "open_archives", "open_list"],
                      Field(description="; ".join(f"{k}: {v[1]}" for k, v in online.SOURCES.items()))],
    surname: str = "",
    given: str = "",
    year_from: int | None = None,
    year_to: int | None = None,
    place: str = "",
    query: Annotated[str, Field(description="Free text instead of the name fields (e.g. a phrase for the full-text search)")] = "",
) -> dict[str, Any]:
    """Search an open database live and get the matching records back (title, date, place, link, snippet).
    Sends the query to that one site only. Run it for each name form from name_variants; for FamilySearch, Geneteka,
    Find a Grave and other sites without an open API use search_links."""
    return online.search(source, surname=surname, given=given, year_from=year_from, year_to=year_to, place=place, query=query)


@server.tool(annotations=NET)
def place_history(name: Annotated[str, Field(description="A village, town or district, as precise as possible: «Сынково Тульская область»")], lang: Lang = "ru") -> dict[str, Any]:
    """Look a place up in Wikidata: what administrative units it was part of (with years where known), coordinates and the
    Wikipedia article — a first step to the uezd, province and parish of a village. Sends the name to Wikidata."""
    try:
        return online.place_history(name, lang)
    except Exception as e:   # noqa: BLE001 — network or format problems become a message for the assistant
        return {"error": f"Wikidata did not answer: {e}"}


@server.tool(annotations=RO)
def plan_research(
    country: str = "",
    year_from: int | None = None,
    year_to: int | None = None,
    question: Annotated[str, Field(description="What we want to find out, with what is known")] = "",
    lang: Lang = "en",
) -> dict[str, Any]:
    """A step-by-step research plan for a country and period: which records exist, which guides to read and which
    sources to search, in order (free and country-specific first)."""
    return plan.plan(country, year_from, year_to, question, lang)


@server.tool(annotations=RO)
def film_reading_plan(
    parish: Annotated[str, Field(description="The church whose books to read, with its village: «Покровская церковь с. Сынково», 'church of Leca'")],
    year_from: int,
    year_to: int | None = None,
    parts: Annotated[list[str] | None, Field(description="Parts to read: " + ", ".join(coverage.PARTS) + "; default births, marriages, deaths")] = None,
    films: Annotated[list[dict[str, Any]] | None, Field(description="Films from the FamilySearch Catalog entry: [{film (DGS number), years ('1860-1875'), frames (images on the film, if shown), item, note}]; empty = how to find them")] = None,
    project: Annotated[str, Field(description="A project (name, site folder or .ged path) whose coverage marks what is already read; it is skipped")] = "",
    order: Literal["newest_first", "oldest_first"] = "newest_first",
    lang: Lang = "en",
) -> dict[str, Any]:
    """A plan for reading unindexed FamilySearch films page by page for a parish, years and parts: which films to read
    in which order, thumbnails to find the book (title pages, end-of-year summaries naming the church) and full frames
    only for the record pages, a rough request budget split into sessions under the site's variable rate limit (pause at
    least an hour after HTTP 429, no parallel sessions), and what to log with project_coverage."""
    entries = None
    if project:
        got = _safe(coverage.load, project)
        if isinstance(got, dict):
            return got
        entries = got
    try:
        return film_plan.plan(parish, year_from, year_to, parts, films, entries, order, lang)
    except ValueError as e:
        return {"error": str(e)}


@server.tool(annotations=RO)
def name_variants(
    name: str,
    kind: Annotated[Literal["surname", "given", "patronymic"], Field(description="What the name is")] = "surname",
) -> dict[str, Any]:
    """All the forms a name can take in records (and its Daitch–Mokotoff Soundex codes): spelling variants, pre-1918 orthography, male/female surname forms
    (Колодин/Колодина, Kowalski/Kowalska, Kazlauskas/Kazlauskienė), transliterations (passport, BGN, German, French,
    Polish, Romanian, Spanish, Ukrainian, scholarly) and given-name equivalents across languages (Иван = Іоаннъ = Jan = Johann = Juan)."""
    v = names.variants(name, kind)
    v["all_forms"] = names.all_forms(name, kind)
    if kind == "surname":
        v["daitch_mokotoff"] = soundex.codes_for(name)
        v["daitch_mokotoff_tip"] = ("Use these codes in JewishGen and stevemorse.org 'sounds like' searches: they find spellings "
                                    "no variant list foresees.")
    return v


@server.tool(annotations=RO)
def normalize_date(text: str) -> dict[str, Any]:
    """A date as people write it ('около 1899', 'between 1900 and 1905', '9 de octubre de 1899', '9.10.1899') →
    ISO or GEDCOM ('ABT 1899', 'BET 1900 AND 1905', '9 OCT 1899', '1899-10-09')."""
    r = dates.normalize_date(text)
    return {"input": text, "result": r, "understood": r is not None}


@server.tool(annotations=RO)
def convert_calendar(
    date: Annotated[str, Field(description="'1899-10-09' / '9.10.1899' (Julian or Gregorian), '15 Nisan 5650' (Hebrew), '18 Brumaire an VIII' (French Republican)")],
    to: Literal["gregorian", "julian", "hebrew", "republican"] = "gregorian",
    from_calendar: Annotated[Literal["auto", "julian", "gregorian", "hebrew", "republican"], Field(description="The calendar of `date`; auto: Hebrew and Republican are recognised by month names, a plain date is Julian when converting to Gregorian and vice versa")] = "auto",
) -> dict[str, Any]:
    """Convert between calendars of old records: Julian (old style; Russia until February 1918: +10 days in the 1600s,
    +11 in the 1700s, +12 in the 1800s, +13 in 1900–1918), Gregorian, Hebrew (Jewish registers, tombstones) and the
    French Republican calendar (1792–1805)."""
    try:
        text = str(date).strip()
        src = from_calendar
        if src == "auto":
            if any(calendars._heb_month(w) for w in text.split()[1:-1] if not w.isdigit()) and re.search(r"\b5\d{3}\b", text):
                src = "hebrew"
            elif re.search(r"\ban\b|vend|brum|frim|niv|pluv|vent|germ|flor|prair|mess|therm|fruct", text, re.I) and not re.search(r"\d{4}", text):
                src = "republican"
        if src == "hebrew":
            r = calendars.hebrew_to_gregorian(text)
            if to == "julian":
                r["result"] = r["julian"]
            else:
                r["result"] = r["gregorian"]
            return r
        if src == "republican":
            r = calendars.republican_to_gregorian(text)
            r["result"] = r["gregorian"]
            return r
        if to in ("hebrew", "republican"):
            y, m, d = dates._ymd(text)
            if src == "julian":
                y, m, d = calendars.julian_to_gregorian(y, m, d)
            iso = f"{y:04d}-{m:02d}-{d:02d}"
            r = calendars.gregorian_to_hebrew(iso) if to == "hebrew" else calendars.gregorian_to_republican(iso)
            r["result"] = r[to]
            return r
        return dates.convert_calendar(text, to)
    except (ValueError, AttributeError) as e:
        return {"error": str(e)}


@server.tool(annotations=RO)
def feast_date(
    feast: Annotated[str, Field(description="A feast or fast as a record names it: «Покров», «Петров день», «Троица», «Пасха», «Филиппов пост», 'Michaelmas', 'Wielkanoc'…")],
    year: int,
    church: Literal["orthodox", "catholic"] = "orthodox",
) -> dict[str, Any]:
    """The date of a church feast or fast in a given year (Julian and Gregorian), including movable feasts counted from
    Easter. Records and family stories often date events by feasts: «родился на Покров», «венчались после Петрова поста»."""
    return calendars.feast_date(feast, year, church)


@server.tool(annotations=RO)
def cyrillic_numerals(value: Annotated[str, Field(description="Letters to read ('҂аѡ҃п', 'ѳі') or a number to write (1880), or a transcription to scan for numerals")]) -> dict[str, Any]:
    """Church Slavonic numerals in old registers and church books: ҂аѡ҃п = 1880, ѳі = 19 (11–19 are written units
    first). Reads letters, writes a number, or finds every numeral marked with a titlo in a text."""
    v = str(value).strip()
    if v.isdigit():
        try:
            return {"number": int(v), "cyrillic": numerals.format(int(v))}
        except ValueError as e:
            return {"error": str(e)}
    n = numerals.parse(v)
    if n is not None:
        return {"cyrillic": v, "number": n}
    found = numerals.find_all(v)
    return {"found": [{"cyrillic": a, "number": b} for a, b in found]} if found else {
        "error": "not a numeral; letters: а1 в2 г3 д4 є5 ѕ6 з7 и8 ѳ9 і10 к20 л30 м40 н50 ѯ60 ѻ70 п80 ч90 р100 с200 т300 у400 ф500 х600 ѱ700 ѡ800 ц900, ҂ = ×1000"}


@server.tool(annotations=RO)
def dna_match(
    shared_cm: Annotated[float, Field(description="Total shared autosomal DNA in centimorgans (cM), as AncestryDNA, MyHeritage, 23andMe, FTDNA or GEDmatch report it")],
    lang: Lang = "en",
) -> dict[str, Any]:
    """Which relationships a DNA match fits, from the amount of shared DNA (Shared cM Project 4.0 ranges), closest first.
    Several always fit: use documents (and the kinship tool) to decide."""
    return dna.fits(shared_cm, lang)


@server.tool(annotations=RO)
def birth_year_from_age(age: float, record_date: Annotated[str, Field(description="Date or year of the record that gives the age")]) -> dict[str, Any]:
    """The birth-year range implied by an age in a record (census, confession list, death record), exact and loose."""
    return dates.birth_year_from_age(age, record_date)


@server.tool(annotations=RO, name="kinship")
def kinship_tool(
    path: Annotated[str, Field(description="Steps from person A: 'father brother son', \"mother's sister's daughter\", «сын брата отца», «отец матери»")] = "",
    up: Annotated[int | None, Field(description="Or: generations from A up to the common ancestor")] = None,
    down: Annotated[int | None, Field(description="…and from the common ancestor down to B")] = None,
    sex: Literal["M", "F", "U"] = "U",
    half: bool = False,
) -> dict[str, Any]:
    """What B is to A, named in Russian, English and Romanian (троюродный брат / second cousin / văr de gradul 2,
    двоюродный дед / great-uncle), with the expected share of DNA."""
    try:
        return kinship.describe(up, down, sex, path, half)
    except ValueError as e:
        return {"error": str(e)}


@server.tool(annotations=RO)
def check_match(
    known: Annotated[dict[str, Any], Field(description="What we know about our person: given, surname, patronymic, father_given, mother_given, mother_surname, spouse_given, spouse_surname, birth_year, birth_place, residence, death_year, children (list), occupation")],
    found: Annotated[dict[str, Any], Field(description="The same fields from the found record")],
    year_tolerance: int = 3,
    lang: Lang = "en",
) -> dict[str, Any]:
    """Is the person in a found record ours? Compares fact by fact (with name variants and Julian/rounded-age tolerance)
    and gives a verdict: confirmed (2+ independent facts beyond the name), probable, insufficient, conflict or different_person."""
    return evidence.check_match(known, found, year_tolerance, lang)


@server.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False))
def audit_tree(
    file: Annotated[str, Field(description="Path to a GEDCOM (.ged) or family_tree.json file, or the GEDCOM text itself")],
    lang: Lang = "en",
    limit: int = 200,
    codes: Annotated[list[str] | None, Field(description="Only these checks: " + ", ".join(audit.CODES))] = None,
) -> dict[str, Any]:
    """Audit a family tree from any program (GEDCOM) for impossible facts (born after the mother's death, a parent under
    14, death before birth), possible duplicates and gaps (no sources, no dates, people cut off from the tree) — a to-do
    list for the next search."""
    try:
        return audit.report(file, lang, limit, codes, allow_paths=ALLOW_FILES)
    except (OSError, ValueError) as e:
        return {"error": str(e)}


@server.tool(annotations=RO)
def draft_archive_request(
    kind: Annotated[Literal["zags", "state_archive", "military", "repression", "generic_en", "generic_es", "generic_pt"], Field(description="; ".join(f"{k}: {v[0]}" for k, v in letters.KINDS.items()))],
    person: str = "", born: str = "", birth_place: str = "", died: str = "", death_place: str = "",
    parents: str = "", spouse: str = "", relation: Annotated[str, Field(description="Who the requester is to the person")] = "",
    what: Annotated[str, Field(description="What is requested")] = "", years: str = "", place: str = "", details: str = "",
    archive: Annotated[str, Field(description="Name and address of the archive")] = "",
    requester: str = "", requester_address: str = "",
) -> dict[str, Any]:
    """A draft letter to a registry office or an archive (Russian ZAGS, state, military and FSB archives; any archive in
    English, Spanish or Portuguese), with what to attach. Gaps are left in [brackets]. The user sends it — not the tool."""
    return letters.draft(kind, requester, requester_address, relation, person, born, birth_place, died, death_place,
                         parents, spouse, what, years, place, details, archive)


@server.tool(annotations=RO)
def record_guide(
    topic: Annotated[str, Field(description="One of: " + ", ".join(guides.GUIDES))] = "",
    lang: Annotated[Literal["en", "ru", "uk", "es", "pt", "pl", "de"], Field(description="en, ru and uk: every guide; es, pt, pl, de: the guides most used in those countries (others fall back to English)")] = "en",
) -> str:
    """How to read and find a kind of record: parish registers, confession lists, revision lists, household books,
    WWI and WWII records, repression files, passenger lists, censuses, European civil registration, Latin America,
    evaluating evidence — in English, Russian, Ukrainian, and partly Spanish, Portuguese, Polish, German. Without a
    topic — the list."""
    text = guides.guide(topic, lang)
    if text:
        return text
    return "Topics:\n" + "\n".join(f"- {k}: {v}" for k, v in guides.topics(lang).items())


@server.tool(annotations=RO)
def glossary(term: Annotated[str, Field(description="A word from an old document, or empty for all")] = "", lang: Lang = "en") -> dict[str, str]:
    """Old Russian terms from records — estates, kinship by marriage (шурин, деверь, золовка), archive citation (фонд,
    опись, дело, лист), administrative units, pre-1918 letters — explained."""
    return guides.glossary(term, lang)


# ---------------------------------------------------------------- the research project (memory between conversations)

def _local_only():
    if not ALLOW_FILES:
        raise ValueError("projects are kept on the user's computer: not available on a shared HTTP server")


def _safe(fn, *a, **kw):
    try:
        _local_only()
        return fn(*a, **kw)
    except (ValueError, OSError) as e:
        return {"error": str(e)}


WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)


@server.tool(annotations=RO)
def project_view(
    project: Annotated[str, Field(description="Project name (one per family or research question), the path of a gene-archive site folder, or the path of a .ged file (the user's own tree); empty = list the projects, site folders and trees")] = "",
    what: Literal["summary", "record", "search", "log", "checks"] = "summary",
    id: Annotated[str, Field(description="Record id for what='record' (I1, F1, S1, L1)")] = "",
    query: Annotated[str, Field(description="Text for what='search'")] = "",
    lang: Lang = "en",
) -> dict[str, Any]:
    """Read the research project kept between conversations — or a family's gene-archive site folder, or the user's own
    tree in a GEDCOM file: summary (people,
    open leads, recent searches, problems), one record with its family and sources, a text search, the full search
    log, or the tree checks. Start every session on an existing project with what='summary'."""
    if not project:
        return _safe(lambda: {"projects": proj.list_projects(), "folder": str(proj.home())})
    return _safe(proj.view, project, what, id, query, lang)


@server.tool(annotations=WRITE)
def project_save(
    project: Annotated[str, Field(description="Project name, the path of a gene-archive site folder, or the path of a .ged file")],
    kind: Literal["person", "family", "source", "lead"],
    record: Annotated[dict[str, Any], Field(description="""Fields. person: given_names, surname, sex (M/F), birth/death/burial {date, place_as_recorded, source_ids, note}, notes, research_status ('confirmed' | 'probable' | 'unlinked_candidate').
family: partners [ids], children [ids], marriage {date, place_as_recorded, source_ids}, source_ids.
source: title, kind (parish_register, census, military, civil_record, family_document, photo, book, web…), locator (archive, fond, opis, delo, folio — or film/image), url, scope (what it says: transcription).
lead: title (what to check), record (where), person_id, url, status ('open'|'closed'), resolution.
Pass "id" to update an existing record (a field set to null is removed).""")],
    reason: Annotated[str, Field(description="Why this was added or changed — kept in the corrections log")] = "",
    source_ids: Annotated[list[str] | None, Field(description="Sources (S…) that prove it")] = None,
    delete: bool = False,
    dry_run: Annotated[bool, Field(description="Check the change and show it without writing — use it to show the user what will be saved")] = False,
) -> dict[str, Any]:
    """Add or change a person, family, source or research lead in the project. Every change of an existing record is
    logged with the old and new value, the reason and the documents. Save the source first, then cite its S-id.
    In a gene-archive site folder the change goes through `gene apply`: refused if it adds an error, logged, committed
    to git under the owner's name, and the site is rebuilt. In a .ged file only the changed lines are rewritten (everything
    else in the file stays as it was), a copy is kept, and gedcom_changes shows the lines. Ask the user before writing
    into their archive or tree."""
    return _safe(proj.upsert, project, kind, record, reason, source_ids, delete, dry_run)


@server.tool(annotations=WRITE)
def project_log(
    project: Annotated[str, Field(description="Project name, the path of a gene-archive site folder, or the path of a .ged file")],
    action: Annotated[str, Field(description="What was searched and where: 'FamilySearch index, Kolodin, Tula 1880–1890'")],
    result: Annotated[str, Field(description="What came out — 'nothing found' is a result too")],
    scope: str = "",
) -> dict[str, Any]:
    """Write a line in the project's research log, so nobody searches the same place twice. Log negative results."""
    return _safe(proj.log, project, action, result, scope)


@server.tool(annotations=WRITE)
def project_coverage(
    project: Annotated[str, Field(description="Project name, the path of a gene-archive site folder, or the path of a .ged file")],
    action: Annotated[Literal["mark", "unread", "list"], Field(description="mark: save what was read; unread: what is still unread for places and years; list: everything recorded")] = "unread",
    entries: Annotated[list[dict[str, Any]] | None, Field(description="For mark: one entry per book read — parish (the church whose book it is), villages (that church's villages in the book), year, part (" + ", ".join(coverage.PARTS) + "), film, frames ('112-140'), status (complete | partial | not_found), up_to (for partial: 'No. 45'), source_ids, note")] = None,
    places: Annotated[list[str] | None, Field(description="For unread/list: parishes or villages (a village is matched through the entries that name it)")] = None,
    year_from: int | None = None,
    year_to: int | None = None,
    parts: Annotated[list[str] | None, Field(description="For unread: the parts to check; default births, marriages, deaths")] = None,
    dry_run: Annotated[bool, Field(description="For mark: show the change without writing")] = False,
    lang: Lang = "en",
) -> dict[str, Any]:
    """What has already been read in the registers: parish → year → part → film and frames → status (complete, partial
    up to No. …, not found). Mark each book when you finish it, and ask what is still unread for these villages and
    years before opening a film — so nobody reads the same frames twice. Kept with the project (for a .ged file in the
    file next to it; for a gene-archive site in a file of this server, read together with the site's own coverage)."""
    if action == "mark":
        if not entries:
            return {"error": "give entries to mark"}
        return _safe(coverage.mark, project, entries, dry_run)
    if action == "list":
        return _safe(coverage.listing, project, places or [])
    return _safe(coverage.unread, project, places or [], year_from, year_to, parts, lang)


@server.tool(annotations=WRITE)
def project_transfer(
    project: str,
    direction: Literal["export_gedcom", "import_gedcom"],
    file: Annotated[str, Field(description="For import: path to a .ged file or the GEDCOM text")] = "",
) -> dict[str, Any]:
    """Export the project as GEDCOM 5.5.1 (for MyHeritage, Ancestry, Gramps, Geni…) next to the project file, or start a
    new project from a GEDCOM exported by another program."""
    if direction == "export_gedcom":
        return _safe(proj.export, project, "gedcom")
    return _safe(proj.import_gedcom, project, file)


# ---------------------------------------------------------------- resources

def _doc(name):
    text = _res.files("genealogy_mcp").joinpath(f"data/docs/{name}.md").read_text(encoding="utf-8")
    note = ("> From the open-source family archive engine https://github.com/igormel81/gene_archive — "
            "`S##` and `gene …` commands refer to it; the method works with any tree program.\n\n")
    return note + text


@server.resource("genealogy://sources", mime_type="application/json", description="The full catalogue of genealogy sources")
def res_sources() -> str:
    return json.dumps(sources.catalogue(), ensure_ascii=False, indent=1)


@server.resource("genealogy://guide/research/{lang}", mime_type="text/markdown",
                 description="How to research a family history, step by step (lang: en or ru)")
def res_research_guide(lang: str) -> str:
    return _doc("research-guide.ru" if lang == "ru" else "research-guide")


@server.resource("genealogy://guide/prompts/{lang}", mime_type="text/markdown",
                 description="Ready requests to an AI assistant for every research step (lang: en or ru)")
def res_prompts(lang: str) -> str:
    return _doc("research-prompts.ru" if lang == "ru" else "research-prompts")


@server.resource("genealogy://records/{topic}", mime_type="text/markdown", description="How to read a kind of record (English)")
def res_record(topic: str) -> str:
    return guides.guide(topic, "en") or "Unknown topic. Topics: " + ", ".join(guides.GUIDES)


@server.resource("genealogy://records/{lang}/{topic}", mime_type="text/markdown",
                 description="How to read a kind of record, in en, ru, uk, es, pt, pl or de")
def res_record_lang(lang: str, topic: str) -> str:
    return guides.guide(topic, lang) or "Unknown topic. Topics: " + ", ".join(guides.GUIDES)


@server.resource("genealogy://glossary", mime_type="application/json", description="Glossary of old Russian record terms")
def res_glossary() -> str:
    return json.dumps({k: {"en": v[0], "ru": v[1]} for k, v in guides.GLOSSARY.items()}, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- prompts

@server.prompt(title="Start researching an ancestor")
def start_research(person: str, known: str = "", country: str = "") -> str:
    """Begin a family search for one person."""
    return f"""I want to research my ancestor: {person}.
What I know: {known or "(ask me)"}.
Country / region: {country or "(ask me)"}.

1. Ask me what is missing (dates, places as they were then, relatives, documents at home) — a few questions at a time.
2. Make a research plan (plan_research) and name variants (name_variants).
3. Give me direct search links (search_links) and tell me which sources to check by hand.
4. For each find, check it (check_match) before we treat it as our person, and cite the original record."""


@server.prompt(title="Check a find")
def check_find(found_record: str, what_we_know: str) -> str:
    """Is a found record about our person?"""
    return f"""Here is a record I found:
{found_record}

What we know about our person:
{what_we_know}

Extract the facts from both into fields, run check_match, and explain the verdict: which independent facts agree, what
conflicts, and what document would settle it."""


@server.prompt(title="Transcribe an old record")
def transcribe_record(record_kind: str = "metric_book", language: str = "ru") -> str:
    """Help read an attached image of an old record."""
    return f"""I attach an image of a {record_kind} record. Read it with record_guide("{record_kind}") in mind:
1. Transcribe it line by line in the original spelling (keep ѣ, і, ъ), marking unreadable parts as [?].
2. Give a modern-spelling version and a translation into {language}.
3. List the facts as fields (names, estate, place, dates — Julian, convert with convert_calendar), godparents/witnesses.
4. Write the citation: archive, fond, opis, delo, folio (or film and image number)."""


@server.prompt(title="Write to an archive")
def archive_request(person: str, what: str, archive: str = "") -> str:
    """Prepare a request to an archive or a registry office."""
    return f"""Help me write a request about {person}: I need {what}. Archive: {archive or "(help me choose)"}.
Pick the right kind (draft_archive_request), fill in everything I know, list the gaps in [brackets] and what to attach.
It is a draft: I will check and send it myself."""


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(prog="genealogy-mcp", description="Genealogy research toolkit for AI assistants (MCP server).")
    ap.add_argument("--http", action="store_true", help="serve Streamable HTTP instead of stdio (for remote clients)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    if a.http:
        global ALLOW_FILES
        ALLOW_FILES = False   # remote clients must not read files on this machine
        server.run("streamable-http", host=a.host, port=a.port, stateless_http=True)
    else:
        server.run("stdio")


if __name__ == "__main__":
    main()
