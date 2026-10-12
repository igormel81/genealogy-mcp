"""genealogy-mcp: an MCP server that gives an AI assistant a genealogist's toolkit and know-how."""
import json
from importlib import resources as _res
from typing import Annotated, Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from . import __version__, audit, dates, evidence, guides, kinship, letters, names, plan, sources

INSTRUCTIONS = """You help people research their family history. Work like a careful genealogist:
1. Start from what the person knows; ask about the oldest relatives, places (village, district, province), dates, documents at home.
2. Pin down the place as it was then (province/district/parish) — records are arranged by place, not by name.
3. Make name variants (name_variants) and search with all of them: spelling, old orthography, gendered forms, transliterations.
4. Use find_sources / plan_research to pick sources for the country and period; give the user direct links (search_links).
   Go through every relevant source, not just the first one with a hit, and say which ones were checked.
5. A name is not a person: before linking a found record, run check_match — two independent facts beyond the name.
6. Cite the original (archive, fond, opis, delo, folio, or film and image), not an index; keep conflicting versions.
7. Old dates: Julian calendar in Russia until 1918 (convert_calendar); ages in records drift (birth_year_from_age).
8. Archive requests are drafts (draft_archive_request): the user checks and sends them; never claim a letter was sent.
9. Living people: do not publish details about them; mark guesses as 'probably'.
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
    """Find genealogy databases and archives for a country (or region), period and kind of records — 79 sources across
    Russia and the former USSR, Eastern, Western and Northern Europe, the British Isles, the USA and Latin America,
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
def name_variants(
    name: str,
    kind: Annotated[Literal["surname", "given", "patronymic"], Field(description="What the name is")] = "surname",
) -> dict[str, Any]:
    """All the forms a name can take in records: spelling variants, pre-1918 orthography, male/female surname forms
    (Колодин/Колодина, Kowalski/Kowalska, Kazlauskas/Kazlauskienė), transliterations (passport, BGN, German, French,
    Polish, Romanian, Spanish, Ukrainian, scholarly) and given-name equivalents across languages (Иван = Іоаннъ = Jan = Johann = Juan)."""
    v = names.variants(name, kind)
    v["all_forms"] = names.all_forms(name, kind)
    return v


@server.tool(annotations=RO)
def normalize_date(text: str) -> dict[str, Any]:
    """A date as people write it ('около 1899', 'between 1900 and 1905', '9 de octubre de 1899', '9.10.1899') →
    ISO or GEDCOM ('ABT 1899', 'BET 1900 AND 1905', '9 OCT 1899', '1899-10-09')."""
    r = dates.normalize_date(text)
    return {"input": text, "result": r, "understood": r is not None}


@server.tool(annotations=RO)
def convert_calendar(
    date: Annotated[str, Field(description="A full date: '1899-10-09', '9.10.1899' or '9 OCT 1899'")],
    to: Literal["gregorian", "julian"] = "gregorian",
) -> dict[str, Any]:
    """Julian (old style) ↔ Gregorian (new style). Russian records before February 1918 are in the Julian calendar:
    +10 days in the 1600s, +11 in the 1700s, +12 in the 1800s, +13 in 1900–1918."""
    return dates.convert_calendar(date, to)


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
    lang: Lang = "en",
) -> str:
    """How to read and find a kind of record: parish registers, confession lists, revision lists, household books,
    WWI and WWII records, repression files, passenger lists, censuses, European civil registration, Latin America,
    evaluating evidence. Without a topic — the list."""
    text = guides.guide(topic, lang)
    if text:
        return text
    return "Topics:\n" + "\n".join(f"- {k}: {v}" for k, v in guides.topics(lang).items())


@server.tool(annotations=RO)
def glossary(term: Annotated[str, Field(description="A word from an old document, or empty for all")] = "", lang: Lang = "en") -> dict[str, str]:
    """Old Russian terms from records — estates, kinship by marriage (шурин, деверь, золовка), archive citation (фонд,
    опись, дело, лист), administrative units, pre-1918 letters — explained."""
    return guides.glossary(term, lang)


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
