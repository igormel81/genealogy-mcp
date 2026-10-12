"""A research project that survives between conversations: people, families, sources, research leads and a log of
searches (negative results too), stored as a JSON file in the format of the gene_archive engine
(https://github.com/igormel81/gene_archive), so a project can grow into a family website.

Files live in $GENEALOGY_MCP_HOME, else ~/Documents/genealogy-mcp (or ~/genealogy-mcp).
"""
import datetime
import json
import os
import re
from pathlib import Path

from . import audit
from .dates import GED_MONTHS, normalize_date

KINDS = {"person": ("people", "I"), "family": ("families", "F"), "source": ("sources", "S"), "lead": ("research_leads", "L")}
NAME_RE = re.compile(r"[\w][\w .-]{0,59}")


def home():
    env = os.environ.get("GENEALOGY_MCP_HOME")
    if env:
        return Path(env).expanduser()
    docs = Path.home() / "Documents"
    return (docs if docs.is_dir() else Path.home()) / "genealogy-mcp"


def _path(name):
    name = str(name).strip()
    if not NAME_RE.fullmatch(name) or name.startswith(".") or ".." in name:
        raise ValueError("a project name is letters, digits, spaces, '-', '_' or '.', up to 60 characters")
    return home() / f"{name}.json"


def _today():
    return datetime.date.today().isoformat()


def empty(title=""):
    return {"title": title, "created": _today(), "root_person_id": None, "people": [], "families": [], "sources": [],
            "research_leads": [], "research_log": [], "corrections": []}


def load(name, create=False):
    p = _path(name)
    if not p.exists():
        if not create:
            raise ValueError(f"no project {name!r} (in {home()}); projects: {', '.join(list_projects()) or 'none yet'}")
        return empty(name)
    return json.loads(p.read_text(encoding="utf-8"))


def save(name, data):
    p = _path(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.with_suffix(".json.bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(p)
    return p


def list_projects():
    h = home()
    return sorted(p.stem for p in h.glob("*.json")) if h.is_dir() else []


def _next_id(items, prefix):
    nums = [int(x["id"][1:]) for x in items if re.fullmatch(prefix + r"\d+", str(x.get("id", "")))]
    return f"{prefix}{max(nums, default=0) + 1}"


def _find(data, rid):
    for coll, _ in KINDS.values():
        for x in data[coll]:
            if x["id"] == rid:
                return coll, x
    return None, None


def _flat(obj, prefix=""):
    out = {}
    for k, v in obj.items():
        if isinstance(v, dict):
            out.update(_flat(v, f"{prefix}{k}."))
        else:
            out[prefix + k] = v
    return out


def _merge(old, new):
    """Fields of `new` over `old`; nested dicts (events) are merged too; None removes a field."""
    out = dict(old)
    for k, v in new.items():
        if v is None:
            out.pop(k, None)
        elif isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def _normalize_person(rec, warnings):
    if rec.get("given_names") or rec.get("surname"):
        if not rec.get("display_name"):
            rec["display_name"] = " ".join(x for x in (rec.get("given_names"), rec.get("surname")) if x)
    for ev in ("birth", "death", "burial"):
        e = rec.get(ev)
        if isinstance(e, str):   # "1899" or "about 1899, Synkovo"
            rec[ev] = e = {"date": e}
        if isinstance(e, dict):
            if "place" in e and "place_as_recorded" not in e:
                e["place_as_recorded"] = e.pop("place")
            if e.get("date"):
                n = normalize_date(e["date"])
                if n and n != e["date"]:
                    e["date"] = n
                elif not n:
                    warnings.append(f"{ev}: date {e['date']!r} not understood; kept as written")
    if rec.get("sex"):
        rec["sex"] = str(rec["sex"]).upper()[:1].replace("М", "M").replace("Ж", "F")


def upsert(name, kind, record, reason="", source_ids=None, delete=False):
    """Creates or updates a record; every changed field of an existing record goes to `corrections`."""
    if kind not in KINDS:
        raise ValueError(f"kind is one of {', '.join(KINDS)}")
    data = load(name, create=True)
    coll, prefix = KINDS[kind]
    rec = dict(record or {})
    warnings = []
    rid = rec.get("id")
    if delete:
        _, old = _find(data, rid)
        if not old:
            raise ValueError(f"no record {rid}")
        data[coll] = [x for x in data[coll] if x["id"] != rid]
        for f in data["families"]:
            for k in ("partners", "children"):
                f[k] = [x for x in f.get(k, []) if x != rid]
        data["corrections"].append({"record": rid, "field": "*", "previous": old, "current": None, "reason": reason or "deleted",
                                    "date": _today()})
        save(name, data)
        return {"deleted": rid}
    if kind == "person":
        _normalize_person(rec, warnings)
    if kind == "family":
        people = {p["id"] for p in data["people"]}
        for k in ("partners", "children"):
            bad = [x for x in rec.get(k, []) if x not in people]
            if bad:
                raise ValueError(f"{k}: no such people {bad}")
        if isinstance(rec.get("marriage"), dict) and rec["marriage"].get("date"):
            rec["marriage"]["date"] = normalize_date(rec["marriage"]["date"]) or rec["marriage"]["date"]
    if kind == "lead":
        rec.setdefault("status", "open")
        rec.setdefault("record", rec.get("title", ""))
    if source_ids:
        rec["source_ids"] = sorted(set(rec.get("source_ids", [])) | set(source_ids))
    srcs = {s["id"] for s in data["sources"]}
    missing = [s for s in rec.get("source_ids", []) if s not in srcs]
    if missing:
        raise ValueError(f"no such sources {missing}: save the source first (kind='source')")
    _, old = _find(data, rid) if rid else (None, None)
    if old is not None:
        before = _flat(old)
        merged = _merge(old, rec)
        after = _flat(merged)
        changed = [k for k in set(before) | set(after) if before.get(k) != after.get(k)]
        for k in sorted(changed):
            data["corrections"].append({("person_id" if kind == "person" else "family_id" if kind == "family" else "record"): rid,
                                        "field": k, "previous": before.get(k), "current": after.get(k),
                                        "reason": reason or "updated", "source_ids": source_ids or [], "date": _today()})
        old.clear()
        old.update(merged)
        out = old
    else:
        rec["id"] = _next_id(data[coll], prefix)
        if kind == "source":
            rec.setdefault("kind", "record")
            if not rec.get("title"):
                raise ValueError("a source needs a title (and ideally locator: archive, fond, opis, delo, folio — or URL)")
        if kind == "person" and not rec.get("display_name"):
            raise ValueError("a person needs given_names and/or surname")
        data[coll].append(rec)
        out = rec
        if kind == "person" and not data.get("root_person_id"):
            data["root_person_id"] = rec["id"]
    save(name, data)
    return {"saved": out, "warnings": warnings, "project": name}


def log(name, action, result, scope=""):
    """A line in the research log: what was searched, where, what came out — 'nothing found' counts."""
    data = load(name, create=True)
    entry = {"date": _today(), "action": action, "result": result, **({"scope": scope} if scope else {})}
    data["research_log"].append(entry)
    save(name, data)
    return {"logged": entry, "entries": len(data["research_log"])}


def _brief(p):
    b, d = (p.get("birth") or {}), (p.get("death") or {})
    years = f"{b.get('date', '?')} – {d.get('date', '')}".strip(" –") if b or d else ""
    return {"id": p["id"], "name": p.get("display_name"), "years": years, "birth_place": b.get("place_as_recorded")}


def view(name, what="summary", rid="", query="", lang="en"):
    data = load(name)
    if what == "summary":
        open_leads = [x for x in data["research_leads"] if x.get("status") != "closed"]
        return {"project": name, "file": str(_path(name)), "people": len(data["people"]), "families": len(data["families"]),
                "sources": len(data["sources"]), "root_person_id": data.get("root_person_id"),
                "people_list": [_brief(p) for p in data["people"][:200]],
                "open_leads": open_leads[:30], "recent_log": data["research_log"][-15:],
                "checks": audit.report(json.dumps(data), lang=lang, limit=15)["items"]}
    if what == "record":
        coll, rec = _find(data, rid)
        if not rec:
            raise ValueError(f"no record {rid}")
        out = {"record": rec}
        if coll == "people":
            out["as_child_in"] = [f for f in data["families"] if rid in f.get("children", [])]
            out["as_partner_in"] = [f for f in data["families"] if rid in f.get("partners", [])]
            out["corrections"] = [c for c in data["corrections"] if c.get("person_id") == rid][-20:]
        used = set(rec.get("source_ids", [])) | {s for e in ("birth", "death", "burial", "marriage") for s in (rec.get(e) or {}).get("source_ids", [])}
        out["sources"] = [s for s in data["sources"] if s["id"] in used]
        return out
    if what == "search":
        q = query.lower()
        hits = []
        for coll, _ in KINDS.values():
            for x in data[coll]:
                if q in json.dumps(x, ensure_ascii=False).lower():
                    hits.append(x)
        hits += [x for x in data["research_log"] if q in json.dumps(x, ensure_ascii=False).lower()]
        return {"query": query, "hits": hits[:50]}
    if what == "log":
        return {"research_log": data["research_log"][-100:]}
    if what == "checks":
        return audit.report(json.dumps(data), lang=lang)
    raise ValueError("what: summary | record | search | log | checks")


# ---------------------------------------------------------------- GEDCOM

def _ged_date(d):
    m = re.fullmatch(r"(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?", str(d or ""))
    if not m:
        return str(d or "")
    return " ".join(x for x in ((str(int(m[3])) if m[3] else ""), (GED_MONTHS[int(m[2]) - 1] if m[2] else ""), m[1]) if x)


def _cont(level, tag, text):
    lines = str(text).splitlines() or [""]
    out = [f"{level} {tag} {lines[0]}".rstrip()]
    out += [f"{level + 1} CONT {x}".rstrip() for x in lines[1:]]
    return out


def to_gedcom(data):
    out = ["0 HEAD", "1 SOUR genealogy-mcp", "1 GEDC", "2 VERS 5.5.1", "2 FORM LINEAGE-LINKED", "1 CHAR UTF-8"]
    fams_of = {}
    for f in data["families"]:
        for x in f.get("partners", []):
            fams_of.setdefault(x, {"s": [], "c": []})["s"].append(f["id"])
        for x in f.get("children", []):
            fams_of.setdefault(x, {"s": [], "c": []})["c"].append(f["id"])
    for p in data["people"]:
        out.append(f"0 @{p['id']}@ INDI")
        given = p.get("given_names") or (p.get("display_name") or "").split(" ")[0]
        out.append(f"1 NAME {given} /{p.get('surname', '')}/".replace("  ", " "))
        if p.get("sex") in ("M", "F"):
            out.append(f"1 SEX {p['sex']}")
        for ev, tag in (("birth", "BIRT"), ("death", "DEAT"), ("burial", "BURI")):
            e = p.get(ev)
            if e:
                out.append(f"1 {tag}")
                if e.get("date"):
                    out.append(f"2 DATE {_ged_date(e['date'])}")
                if e.get("place_as_recorded"):
                    out.append(f"2 PLAC {e['place_as_recorded']}")
                out += [f"2 SOUR @{s}@" for s in e.get("source_ids", [])]
        out += [f"1 SOUR @{s}@" for s in p.get("source_ids", [])]
        if p.get("notes"):
            out += _cont(1, "NOTE", p["notes"])
        out += [f"1 FAMC @{f}@" for f in fams_of.get(p["id"], {}).get("c", [])]
        out += [f"1 FAMS @{f}@" for f in fams_of.get(p["id"], {}).get("s", [])]
    people = {p["id"]: p for p in data["people"]}
    for f in data["families"]:
        out.append(f"0 @{f['id']}@ FAM")
        for x in f.get("partners", []):
            out.append(f"1 {'WIFE' if people.get(x, {}).get('sex') == 'F' else 'HUSB'} @{x}@")
        out += [f"1 CHIL @{c}@" for c in f.get("children", [])]
        m = f.get("marriage")
        if m:
            out.append("1 MARR")
            if m.get("date"):
                out.append(f"2 DATE {_ged_date(m['date'])}")
            if m.get("place_as_recorded") or m.get("place"):
                out.append(f"2 PLAC {m.get('place_as_recorded') or m.get('place')}")
        out += [f"1 SOUR @{s}@" for s in f.get("source_ids", [])]
    for s in data["sources"]:
        out.append(f"0 @{s['id']}@ SOUR")
        out.append(f"1 TITL {s.get('title', s['id'])}")
        if s.get("locator"):
            out.append(f"1 PUBL {s['locator']}")
        if s.get("url"):
            out += _cont(1, "NOTE", s["url"])
        if s.get("scope"):
            out += _cont(1, "TEXT", s["scope"])
    out.append("0 TRLR")
    return "\n".join(out) + "\n"


def export(name, fmt="gedcom"):
    data = load(name)
    p = _path(name)
    if fmt == "gedcom":
        dest = p.with_suffix(".ged")
        dest.write_text(to_gedcom(data), encoding="utf-8")
    else:
        dest = p
    return {"file": str(dest), "format": fmt, "people": len(data["people"])}


def import_gedcom(name, path_or_text, allow_paths=True):
    """A new project from a GEDCOM file (from MyHeritage, Ancestry, Gramps, Geni…)."""
    if _path(name).exists():
        raise ValueError(f"project {name!r} exists: import into a new project name")
    parsed = audit.load(path_or_text, allow_paths)
    data = empty(name)
    for p in parsed.get("people", []):
        rec = {"id": p["id"], "display_name": p.get("display_name", "?"), "sex": p.get("sex", "U")}
        parts = (p.get("display_name") or "").rsplit(" ", 1)
        rec["given_names"], rec["surname"] = (parts[0], parts[1]) if len(parts) == 2 else (parts[0], "")
        for ev in ("birth", "death"):
            e = p.get(ev)
            if e:
                rec[ev] = {k2: v for k2, v in {"date": e.get("date"), "place_as_recorded": e.get("place"),
                                                "source_ids": e.get("source_ids")}.items() if v}
        if p.get("source_ids"):
            rec["source_ids"] = p["source_ids"]
        data["people"].append(rec)
    data["families"] = parsed.get("families", [])
    data["sources"] = [{"id": s["id"], "title": s.get("title") or s["id"], "kind": "record"} for s in parsed.get("sources", [])]
    if data["people"]:
        data["root_person_id"] = data["people"][0]["id"]
    data["research_log"].append({"date": _today(), "action": "imported GEDCOM", "result": f"{len(data['people'])} people"})
    save(name, data)
    return {"project": name, "people": len(data["people"]), "families": len(data["families"]), "sources": len(data["sources"]),
            "file": str(_path(name)), "note": "Imported ids are the file's own; new records get new ids only if they do not clash."}
