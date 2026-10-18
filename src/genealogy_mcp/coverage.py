"""What has already been read: parish → year → part → film and frames → status, so that nobody reads the same frames
twice and the question "what is still unread for these villages and years" has an answer.

Kept with the project:
- a project of this server: the `coverage` list in its JSON file;
- a GEDCOM file: in <file>.research.json next to it, with the logs;
- a gene-archive site folder: read from the `coverage` section of its family_tree.json when there is one, but written
  to a file of this server (coverage/<folder>-<hash>.json in the projects folder) — `gene apply` does not take
  coverage changes yet, and family_tree.json is changed only through it.
"""
import datetime
import hashlib
import json
import re

from . import gedfile
from . import project as proj

PARTS = {   # part → (en, ru)
    "births": ("births / baptisms", "родившиеся"), "marriages": ("marriages", "бракосочетавшиеся"),
    "deaths": ("deaths / burials", "умершие"), "confession": ("confession list", "исповедная ведомость"),
    "revision": ("revision list", "ревизская сказка"), "census": ("census", "перепись"), "other": ("other", "другое"),
}
PART_ALIASES = {"birth": "births", "baptisms": "births", "baptism": "births", "рождения": "births", "родившиеся": "births",
                "крещения": "births", "marriage": "marriages", "браки": "marriages", "бракосочетавшиеся": "marriages",
                "death": "deaths", "burials": "deaths", "смерти": "deaths", "умершие": "deaths", "погребения": "deaths",
                "исповедные": "confession", "исповедь": "confession", "ревизия": "revision", "ревизские": "revision"}
STATUSES = ("complete", "partial", "not_found")
REGISTER_PARTS = ("births", "marriages", "deaths")


def part(p):
    p = str(p or "").strip().lower()
    p = PART_ALIASES.get(p, p)
    if p not in PARTS:
        raise ValueError(f"part is one of {', '.join(PARTS)} (got {p!r})")
    return p


STOP = {"church", "церковь", "церкви", "храм", "село", "с", "д", "деревня", "village", "parish", "приход", "biserica", "satul",
        "of", "the", "in", "в", "st", "св", "sf"}


def _key(s):
    s = str(s or "").lower().replace("ё", "е").replace("ă", "a").replace("â", "a").replace("î", "i")
    s = s.replace("ș", "s").replace("ş", "s").replace("ț", "t").replace("ţ", "t")
    return " ".join(w for w in re.sub(r"[^\w ]+", " ", s).split() if w not in STOP)


def _word(x, y):   # one word, allowing for case endings: Сынково / Сынкова, Leca / Lecii
    if x == y:
        return True
    n = min(len(x), len(y))
    return n >= 4 and abs(len(x) - len(y)) <= 2 and x[:n - 1] == y[:n - 1] and n - 1 >= 4


def _same_place(a, b):
    """Every word of the shorter name matches a word of the longer: Capaclia Nouă ≠ Capaclia Veche."""
    a, b = _key(a).split(), _key(b).split()
    if not a or not b:
        return False
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    return all(any(_word(x, y) for y in long_) for x in short)


def _site_file(name):
    folder = proj._site(name)
    digest = hashlib.sha1(str(folder).encode("utf-8")).hexdigest()[:8]
    return proj.home() / "coverage" / f"{folder.name}-{digest}.json"


def where(name):
    """Where coverage is written for this project."""
    if gedfile.is_ged(name):
        return gedfile.sidecar(proj._site(name))
    if proj.is_site(name):
        return _site_file(name)
    return proj._path(name)


def load(name):
    """All coverage entries of the project (for a site: its own section and this server's file)."""
    if proj.is_site(name):
        tree = proj.load(name)
        own = [dict(e, origin="family_tree.json") for e in tree.get("coverage", []) if isinstance(e, dict)]
        f = _site_file(name)
        mine = json.loads(f.read_text(encoding="utf-8")).get("coverage", []) if f.exists() else []
        return own + mine
    return list(proj.load(name, create=True).get("coverage", []))


def _clean(e):
    if not isinstance(e, dict):
        raise ValueError("each entry is an object: {parish, year, part, film, frames, status, up_to, villages, source_ids, note}")
    out = {k: v for k, v in e.items() if v not in (None, "", [])}
    if not out.get("parish"):
        raise ValueError("an entry needs the parish (the church whose book it is): 'church of Leca', «Покровская церковь с. Сынково»")
    try:
        out["year"] = int(str(out.get("year", "")).strip()[:4])
    except ValueError:
        raise ValueError(f"an entry needs the year of the book: {e!r}") from None
    out["part"] = part(out.get("part"))
    out["status"] = str(out.get("status", "complete")).lower().replace(" ", "_").replace("-", "_")
    if out["status"] not in STATUSES:
        raise ValueError(f"status is one of {', '.join(STATUSES)}")
    if out["status"] == "partial" and not out.get("up_to"):
        raise ValueError("a partial entry needs up_to: how far it was read ('No. 45', 'frame 312', '15 May')")
    if isinstance(out.get("villages"), str):
        out["villages"] = [v.strip() for v in re.split(r"[,;]", out["villages"]) if v.strip()]
    if isinstance(out.get("source_ids"), str):
        out["source_ids"] = [out["source_ids"]]
    out.setdefault("date", datetime.date.today().isoformat())
    return out


def _same(a, b):
    return (_key(a.get("parish")) == _key(b.get("parish")) and a.get("year") == b.get("year") and a.get("part") == b.get("part")
            and str(a.get("film", "")).strip() == str(b.get("film", "")).strip())


def mark(name, entries, dry_run=False):
    """Adds or replaces entries (one per parish, year, part and film). Returns what changed."""
    new = [_clean(e) for e in (entries if isinstance(entries, list) else [entries])]
    if gedfile.is_ged(name) or not proj.is_site(name):
        data = proj.load(name, create=True)
        cov = data.setdefault("coverage", [])
    else:
        f = _site_file(name)
        side = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"site": str(proj._site(name)), "coverage": []}
        cov = side["coverage"]
    changed = []
    for e in new:
        old = next((x for x in cov if _same(x, e)), None)
        if old is not None:
            changed.append({"entry": e, "previous": dict(old)})
            old.clear()
            old.update(e)
        else:
            cov.append(e)
            changed.append({"entry": e, "previous": None})
    out = {"saved": changed, "file": str(where(name)), "dry_run": dry_run}
    if proj.is_site(name):
        out["note"] = ("Kept next to the site, not in family_tree.json: gene apply does not take coverage yet. "
                       "It is read together with the site's own coverage section.")
    if dry_run:
        return out
    if gedfile.is_ged(name):
        gedfile.save(proj._site(name), data)   # the tree is unchanged: only the file next to it is written
    elif proj.is_site(name):
        f.parent.mkdir(parents=True, exist_ok=True)
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(side, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(f)
    else:
        proj.save(name, data)
    return out


def _years(year_from, year_to, entries):
    ys = [e["year"] for e in entries if isinstance(e.get("year"), int)]
    y1 = int(year_from) if year_from else (min(ys) if ys else None)
    y2 = int(year_to) if year_to else (max(ys) if ys else y1)
    if y1 is None:
        raise ValueError("give year_from and year_to")
    if y2 < y1:
        y1, y2 = y2, y1
    if y2 - y1 > 200:
        raise ValueError("at most 200 years at a time")
    return y1, y2


def _ranges(years):
    out, start, prev = [], None, None
    for y in sorted(years):
        if start is None:
            start = prev = y
        elif y == prev + 1:
            prev = y
        else:
            out.append(f"{start}" if start == prev else f"{start}–{prev}")
            start = prev = y
    if start is not None:
        out.append(f"{start}" if start == prev else f"{start}–{prev}")
    return out


def _of_place(entries, place):
    """Entries of the place's parish: the village named in any entry of a parish brings in all of that parish's books."""
    parishes = {_key(e.get("parish")) for e in entries
                if _same_place(place, e.get("parish")) or any(_same_place(place, v) for v in e.get("villages", []))}
    return [e for e in entries if _key(e.get("parish")) in parishes]


def unread(name, places, year_from=None, year_to=None, parts=None, lang="en", entries=None):
    """For each place (a parish or a village): which years of which parts are read, partly read, not found or unread."""
    ru = lang == "ru"
    entries = load(name) if entries is None else entries
    places = [p for p in (places if isinstance(places, list) else re.split(r"[,;]", places or "")) if str(p).strip()]
    want = [part(p) for p in (parts or REGISTER_PARTS)]
    if not places:
        places = list(dict.fromkeys(e["parish"] for e in entries if e.get("parish")))
        if not places:
            return {"places": [], "note": "Nothing is recorded as read yet." if not ru else "Пока ничего не отмечено как прочитанное."}
    out = []
    for place in places:
        mine = _of_place(entries, place)
        y1, y2 = _years(year_from, year_to, mine)
        parishes = sorted({e["parish"] for e in mine})
        res = {"place": place, "parishes": parishes, "years": f"{y1}–{y2}", "parts": {}}
        for p in want:
            done, partial, missing, todo = [], [], [], []
            for y in range(y1, y2 + 1):
                es = [e for e in mine if e.get("year") == y and e.get("part") == p]
                st = {e.get("status") for e in es}
                if "complete" in st:
                    done.append(y)
                elif "partial" in st:
                    e = next(e for e in es if e.get("status") == "partial")
                    partial.append({"year": y, "up_to": e.get("up_to"), "film": e.get("film"), "frames": e.get("frames")})
                elif "not_found" in st:
                    missing.append({"year": y, "film": next((e.get("film") for e in es if e.get("film")), None),
                                    "note": next((e.get("note") for e in es if e.get("note")), None)})
                else:
                    todo.append(y)
            res["parts"][p] = {"read": _ranges(done), "partial": partial, "not_found": missing, "unread": _ranges(todo)}
        if not mine:
            res["note"] = ("Nothing read yet for this place. If it is a village, find its parish first (where_are_records with "
                           "village=…): the books are kept by the church, often in a neighbouring village."
                           if not ru else "По этому месту ещё ничего не прочитано. Если это село — сначала найдите его приход "
                           "(where_are_records с village=…): книги ведёт церковь, часто в соседнем селе.")
        out.append(res)
    tip = ("Read the 'unread' years first and finish the 'partial' ones from where they stop; 'not_found' means the book was "
           "not on that film — look for another copy (the second copy in the consistory fond, another film, the archive)."
           if not ru else "Сначала читайте годы из «unread», «partial» дочитывайте с места остановки; «not_found» — книги на этой "
           "плёнке нет: ищите другой экземпляр (второй экземпляр в фонде консистории, другую плёнку, архив).")
    return {"places": out, "tip": tip}


def listing(name, places=None, limit=500):
    es = load(name)
    if places:
        picked = []
        for pl in (places if isinstance(places, list) else [places]):
            picked += [e for e in _of_place(es, pl) if e not in picked]
        es = picked
    es = sorted(es, key=lambda e: (_key(e.get("parish")), e.get("year", 0), e.get("part", "")))
    return {"coverage": es[:limit], "count": len(es), "file": str(where(name))}


__all__ = ["mark", "unread", "listing", "load", "PARTS", "STATUSES"]
