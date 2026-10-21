"""Live search in open databases that offer a public API. Called only when the assistant uses search_online or
place_history: then the query (names, years, place) goes to that one site and nowhere else.

FamilySearch, MyHeritage, Ancestry, Geneteka, Find a Grave and JewishGen have no open API for this (or forbid automated
access): for them the server builds links (search_links) and the user searches in the browser.
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from . import __version__

UA = f"genealogy-mcp/{__version__} (+https://github.com/igormel81/genealogy-mcp)"
TIMEOUT = 25


def _get(url, params=None, data=None):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")}, doseq=True)
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers={"User-Agent": UA, "Accept": "application/json"})
    # These are read-only search queries. Retry one transient network failure;
    # missing endpoints and malformed responses must still reach the caller.
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8", errors="replace"))
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if attempt or (isinstance(error, urllib.error.HTTPError) and error.code not in (408, 429, 500, 502, 503, 504)):
                raise
            time.sleep(1)


def _q(*parts):
    return " ".join(str(p) for p in parts if p)


# ---------------------------------------------------------------- sources

def internet_archive(surname="", given="", year_from=None, year_to=None, place="", query="", limit=15):
    """Full text of digitised books (memorial books, directories, regimental histories, newspapers): returns the
    passages where the words occur and a link that opens the book on that search."""
    q = query or _q(f'"{_q(given, surname)}"' if surname else "", f'"{place}"' if place else "")
    d = _get("https://archive.org/services/search/beta/page_production/", {"user_query": q, "service_backend": "fts", "hits_per_page": limit})
    hits = []
    for h in (((d.get("response") or {}).get("body") or {}).get("hits") or {}).get("hits", []):
        f = h.get("fields") or {}
        year = f.get("year") or (str(f.get("date") or "")[:4] or None)
        if year_from and year and str(year).isdigit() and int(year) < int(year_from) - 50:
            continue
        passages = [re.sub(r"\s+", " ", t).replace("{{{", "**").replace("}}}", "**") for t in (h.get("highlight") or {}).get("text", [])[:3]]
        href = f.get("__href__") or f"/details/{f.get('identifier')}"
        hits.append({"title": f.get("title"), "year": year, "file": f.get("file_basename"),
                     "url": "https://archive.org" + href, "passages": passages})
    if not hits:   # nothing in the text: try titles and descriptions of books
        d = _get("https://archive.org/advancedsearch.php", {"q": f"({q}) AND mediatype:texts", "fl[]": ["identifier", "title", "date"],
                                                           "rows": limit, "output": "json"})
        for doc in d.get("response", {}).get("docs", []):
            hits.append({"title": doc.get("title"), "year": str(doc.get("date") or "")[:4] or None,
                         "url": f"https://archive.org/details/{doc['identifier']}", "passages": []})
    return hits


def chronicling_america(surname="", given="", year_from=None, year_to=None, place="", query="", limit=15):
    """US newspapers 1756–1963 (Library of Congress): obituaries, arrivals, naturalisations, local news."""
    q = query or _q(given, surname, place)
    params = {"q": q, "fo": "json", "c": limit}
    if year_from or year_to:
        params["dates"] = f"{year_from or 1756}/{year_to or 1963}"
    d = _get("https://www.loc.gov/collections/chronicling-america/", params)
    out = []
    for r in d.get("results", [])[:limit]:
        out.append({"title": r.get("title"), "date": r.get("date"), "place": ", ".join(r.get("location_state") or r.get("location") or [])[:120],
                    "url": r.get("url") or r.get("id"), "snippet": " ".join(r.get("description") or [])[:300]})
    return out


def wikitree(surname="", given="", year_from=None, year_to=None, place="", query="", limit=15):
    """The WikiTree single collaborative tree (free; profiles cite their sources)."""
    if not surname:
        raise ValueError("WikiTree search needs a surname")
    data = {"action": "searchPerson", "LastName": surname, "FirstName": given, "BirthLocation": place, "limit": limit,
            "fields": "Name,FirstName,LastNameAtBirth,LastNameCurrent,BirthDate,DeathDate,BirthLocation,DeathLocation"}
    if year_from or year_to:
        data["BirthDate"] = str(year_from or year_to)
        data["dateInclude"] = "both"
    d = _get("https://api.wikitree.com/api.php", data=data)
    matches = (d[0] if isinstance(d, list) and d else d).get("matches", [])
    out = []
    for m in matches[:limit]:
        out.append({"title": _q(m.get("FirstName"), m.get("LastNameAtBirth"), f"({m.get('LastNameCurrent')})" if m.get("LastNameCurrent") not in (None, m.get("LastNameAtBirth")) else ""),
                    "date": " – ".join(x if x and not x.startswith("0000") else "?" for x in (m.get("BirthDate"), m.get("DeathDate"))).replace("-00", ""),
                    "place": m.get("BirthLocation"),
                    "url": f"https://www.wikitree.com/wiki/{m.get('Name')}"})
    return out


def open_archives(surname="", given="", year_from=None, year_to=None, place="", query="", limit=15):
    """Open Archives (openarchieven.nl): civil and church records from Dutch and Belgian archives, some German and others."""
    name = query or _q(given, surname)
    if year_from or year_to:   # the API takes the period inside the name: "Jan Jansen 1850-1860"
        name += f" {year_from or year_to}-{year_to or year_from}"
    params = {"name": name, "lang": "en", "number_show": limit, "eventplace": place}
    d = _get("https://api.openarch.nl/1.1/records/search.json", params)
    out = []
    for r in (d.get("response") or {}).get("docs", [])[:limit]:
        ed = r.get("eventdate") or {}
        date = "-".join(str(ed.get(k)) for k in ("year", "month", "day") if ed.get(k))
        out.append({"title": f"{str(r.get('personname', '')).lstrip('# ')} — {r.get('relationtype', '')}, {r.get('eventtype', '')}",
                    "date": date, "place": r.get("eventplace") if isinstance(r.get("eventplace"), str) else ", ".join(r.get("eventplace") or []),
                    "archive": r.get("archive"), "url": r.get("url")})
    return out


def open_list(surname="", given="", year_from=None, year_to=None, place="", query="", limit=15):
    """Open List (ru.openlist.wiki): name/title prefix search for victims of Soviet political repression.
    The site's standard MediaWiki text/title search is disabled; its documented OpenSearch still works.
    """
    q = query or _q(surname, given)
    d = _get("https://ru.openlist.wiki/api.php", {"action": "opensearch", "search": q, "limit": limit, "format": "json"})
    if isinstance(d, dict) and d.get("error"):
        error = d["error"]
        raise ValueError(f"Open List API: {error.get('code', 'error')} — {error.get('info', '')}")
    if (not isinstance(d, list) or len(d) != 4 or any(not isinstance(values, list) for values in d[1:])
            or len(d[1]) != len(d[2]) or len(d[1]) != len(d[3])):
        raise ValueError("Open List API: unexpected OpenSearch response")
    out = []
    for title, snippet, url in zip(d[1][:limit], d[2][:limit], d[3][:limit]):
        out.append({"title": title, "url": url, "snippet": re.sub(r"<[^>]+>", "", snippet)[:300]})
    return out


SOURCES = {
    "internet_archive": (internet_archive, "Internet Archive — full text of digitised books, worldwide"),
    "chronicling_america": (chronicling_america, "Chronicling America — US newspapers 1756–1963"),
    "wikitree": (wikitree, "WikiTree — collaborative world tree"),
    "open_archives": (open_archives, "Open Archives — Dutch, Belgian and other civil and church records"),
    "open_list": (open_list, "Открытый список — жертвы политических репрессий в СССР"),
}


def search(source, **kw):
    fn = SOURCES[source][0]
    try:
        hits = fn(**kw)
        note = "Index entries and snippets point to a record: open it and cite the original."
        if source == "open_list":
            note += " Open List searches name/title prefixes; full-text search is disabled on the site."
        return {"source": source, "count": len(hits), "results": hits,
                "note": note}
    except urllib.error.HTTPError as e:
        msg = f"the site answered {e.code}"
        if e.code in (403, 429, 503):
            msg += (" — it may refuse requests from this network (some sites block data centres or other countries). "
                    "Give the user the link from search_links to open in a browser.")
        return {"source": source, "error": msg}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {"source": source, "error": f"the site did not answer: {getattr(e, 'reason', e)}"}
    except (ValueError, KeyError, IndexError, AttributeError) as e:
        return {"source": source, "error": f"unexpected answer: {e}"}


# ---------------------------------------------------------------- places (Wikidata)

def _wd_entities(ids, lang):
    d = _get("https://www.wikidata.org/w/api.php", {"action": "wbgetentities", "ids": "|".join(ids), "format": "json",
                                                    "props": "labels|claims|descriptions|sitelinks", "languages": f"{lang}|en|ru"})
    return d.get("entities", {})


def _label(e, lang):
    labels = e.get("labels", {})
    for l_ in (lang, "ru", "en"):
        if l_ in labels:
            return labels[l_]["value"]
    return e.get("id")


def _time(q):
    v = (((q or [{}])[0].get("datavalue") or {}).get("value") or {}).get("time", "")
    m = re.match(r"[+-](\d{4})", v)
    return int(m[1]) if m else None


def place_history(name, lang="ru", limit=5):
    """What a settlement belonged to over time (Wikidata P131 with start and end dates), its coordinates and
    Wikipedia article — to find the uezd, province and parish of a village."""
    def search(text, n):
        found = _get("https://www.wikidata.org/w/api.php", {"action": "wbsearchentities", "search": text, "language": lang,
                                                            "uselang": lang, "type": "item", "limit": n, "format": "json"})
        return [x["id"] for x in found.get("search", [])]

    ids, qualifiers = search(name, limit), []
    words = name.replace(",", " ").split()
    if not ids and len(words) > 1:
        # Wikidata matches labels only: «Сынково Тульская область» finds nothing, so search the settlement
        # name and use the rest («Тульская область») to pick the right namesake below
        generic = ("облас", "район", "уезд", "губер", "волос", "край", "респу", "oblas", "regio", "distr", "provi", "count", "gover")
        ids, qualifiers = search(words[0], 50), [w.lower()[:5] for w in words[1:] if len(w) > 2 and not w.lower().startswith(generic)]
    if not ids:
        return {"query": name, "places": []}
    ents = _wd_entities(ids, lang)
    parents = set()
    for e in ents.values():
        for c in e.get("claims", {}).get("P131", []):
            v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value") or {}
            if v.get("id"):
                parents.add(v["id"])
    plabels = {k: _label(v, lang) for k, v in _wd_entities(sorted(parents)[:50], lang).items()} if parents else {}
    out = []
    for qid in ids:
        e = ents.get(qid, {})
        within = []
        for c in e.get("claims", {}).get("P131", []):
            v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value") or {}
            quals = c.get("qualifiers", {})
            within.append({"unit": plabels.get(v.get("id"), v.get("id")), "from": _time(quals.get("P580")), "to": _time(quals.get("P582"))})
        coord = (((e.get("claims", {}).get("P625") or [{}])[0].get("mainsnak") or {}).get("datavalue") or {}).get("value") or {}
        wiki = (e.get("sitelinks") or {}).get(f"{lang}wiki") or (e.get("sitelinks") or {}).get("ruwiki") or (e.get("sitelinks") or {}).get("enwiki")
        out.append({"wikidata": f"https://www.wikidata.org/wiki/{qid}", "name": _label(e, lang),
                    "description": ((e.get("descriptions") or {}).get(lang) or (e.get("descriptions") or {}).get("en") or {}).get("value"),
                    "located_in": within, "coordinates": [coord.get("latitude"), coord.get("longitude")] if coord else None,
                    "wikipedia": f"https://{wiki['site'].replace('wiki', '')}.wikipedia.org/wiki/{urllib.parse.quote(wiki['title'].replace(' ', '_'))}" if wiki else None})
    if qualifiers:
        def hits(p):
            text = " ".join([p["description"] or ""] + [str(u["unit"]) for u in p["located_in"]]).lower()
            return sum(q in text for q in qualifiers)
        best = [p for p in sorted(out, key=hits, reverse=True) if hits(p)]
        out = (best or out)[:limit]
    return {"query": name, "places": out,
            "tip": "Wikidata often lists only today's district; for 1700–1917 check the Wikipedia article and «Списки населённых мест». "
                   "Then where_are_records with the province."}
