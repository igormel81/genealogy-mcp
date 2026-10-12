"""Audit a family tree: impossible facts, gaps, possible duplicates — a to-do list for the next search.

Reads GEDCOM (5.5.1 / 7.0, from any program: Gramps, MyHeritage, Ancestry, Geni, FamilySearch) or the
family_tree.json of the gene_archive engine.
"""
import collections
import json
import re
from pathlib import Path

from .dates import normalize_date

CODES = ("death_before_birth", "born_after_mother_death", "born_after_father_death", "parent_young", "parent_old", "married_young",
         "long_life", "possible_duplicate", "bad_date", "unconnected", "no_documents", "event_no_source", "no_dates",
         "family_no_source", "no_sex")
TEXT = {   # code → (English, Russian)
    "death_before_birth": ("{name}: death ({other}) before birth", "{name}: смерть ({other}) раньше рождения"),
    "born_after_mother_death": ("{name} was born after the death of the mother, {other}", "{name} родился(ась) после смерти матери — {other}"),
    "born_after_father_death": ("{name} was born more than a year after the death of the father, {other}", "{name} родился(ась) больше чем через год после смерти отца — {other}"),
    "parent_young": ("{other} was {age} at the birth of {name}", "{other} — {age} лет при рождении ребёнка: {name}"),
    "parent_old": ("{other} was {age} at the birth of {name}", "{other} — {age} лет при рождении ребёнка: {name}"),
    "married_young": ("{name} married at {age}", "{name}: брак в {age} лет"),
    "long_life": ("{name} lived {age} years — check the dates", "{name}: прожил(а) {age} лет — проверьте даты"),
    "possible_duplicate": ("{name} and {other} may be the same person", "{name} и {other} — возможно, один человек"),
    "bad_date": ("{name}: unreadable date «{other}»", "{name}: непонятная дата «{other}»"),
    "unconnected": ("{name} is not connected to the main tree", "{name} не связан(а) с основным древом"),
    "no_documents": ("{name}: not a single source", "{name}: нет ни одного источника"),
    "event_no_source": ("{name}: {event} date without a source", "{name}: дата события «{event}» без источника"),
    "no_dates": ("{name}: no dates of birth or death", "{name}: нет дат рождения и смерти"),
    "family_no_source": ("{name}: the family has no source", "{name}: у семьи нет источника"),
    "no_sex": ("{name}: sex not set", "{name}: не указан пол"),
}
EVENTS = {"birth": ("birth", "рождение"), "death": ("death", "смерть"), "marriage": ("marriage", "брак")}
SRC = re.compile(r"\bS\d+\b")


# ---------------------------------------------------------------- GEDCOM → the engine's structure

def _lines(text):
    for raw in text.splitlines():
        m = re.match(r"\s*(\d+)\s+(@[^@]+@\s+)?(\S+)\s?(.*)$", raw.lstrip("﻿"))
        if m:
            yield int(m[1]), (m[2] or "").strip(), m[3].upper(), m[4]


def parse_gedcom(text):
    people, fams, sources = {}, {}, {}
    def nid(xref, prefix):   # the file's own ids, so that the report points to the records in the user's program
        return xref.strip().strip("@") or prefix

    rec = None
    stack = []   # [(level, tag)]
    for level, xref, tag, value in _lines(text):
        stack = [s for s in stack if s[0] < level]
        if level == 0:
            rec = None
            if tag == "INDI":
                rec = people.setdefault(nid(xref, "I"), {"id": nid(xref, "I")})
                rec["_kind"] = "I"
            elif tag == "FAM":
                rec = fams.setdefault(nid(xref, "F"), {"id": nid(xref, "F"), "partners": [], "children": []})
                rec["_kind"] = "F"
            elif tag == "SOUR":
                rec = sources.setdefault(nid(xref, "S"), {"id": nid(xref, "S")})
                rec["_kind"] = "S"
            stack = [(0, tag)]
            continue
        if rec is None:
            continue
        parent = stack[-1][1] if stack else ""
        stack.append((level, tag))
        if rec["_kind"] == "I":
            if tag == "NAME" and level == 1 and "display_name" not in rec:
                rec["display_name"] = " ".join(value.replace("/", " ").split()) or "?"
            elif tag == "SEX" and level == 1:
                rec["sex"] = value.strip()[:1].upper()
            elif tag in ("BIRT", "CHR", "BAPM", "DEAT", "BURI") and level == 1:
                key = "birth" if tag in ("BIRT", "CHR", "BAPM") else "death"
                if tag in ("BIRT", "DEAT") or key not in rec:
                    rec[key] = {}
                stack[-1] = (level, key if tag in ("BIRT", "DEAT") else key + "_alt")
            elif tag == "DATE" and level == 2 and parent in ("birth", "death", "birth_alt", "death_alt"):
                rec[parent.replace("_alt", "")].setdefault("date", value.strip())
            elif tag == "PLAC" and level == 2 and parent in ("birth", "death", "birth_alt", "death_alt"):
                rec[parent.replace("_alt", "")].setdefault("place", value.strip())
            elif tag == "SOUR" and value.startswith("@"):
                sid = nid(value.strip(), "S")
                if level == 2 and parent in ("birth", "death", "birth_alt", "death_alt"):
                    rec[parent.replace("_alt", "")].setdefault("source_ids", []).append(sid)
                else:
                    rec.setdefault("source_ids", []).append(sid)
        elif rec["_kind"] == "F":
            if tag in ("HUSB", "WIFE") and level == 1:
                rec["partners"].append(nid(value.strip(), "I"))
            elif tag == "CHIL" and level == 1:
                rec["children"].append(nid(value.strip(), "I"))
            elif tag == "MARR" and level == 1:
                rec["marriage"] = {}
                stack[-1] = (level, "marriage")
            elif tag == "DATE" and parent == "marriage":
                rec["marriage"]["date"] = value.strip()
            elif tag == "SOUR" and value.startswith("@"):
                sid = nid(value.strip(), "S")
                (rec["marriage"] if parent == "marriage" else rec).setdefault("source_ids", []).append(sid)
        elif rec["_kind"] == "S" and tag == "TITL":
            rec["title"] = value.strip()
    for coll in (people, fams, sources):
        for r in coll.values():
            r.pop("_kind", None)
    return {"people": list(people.values()), "families": list(fams.values()), "sources": list(sources.values())}


def load(path_or_text, allow_paths=True):
    """A path to .ged / .json, or the GEDCOM / JSON text itself. allow_paths=False (a server open to the network)
    accepts only the text: a path would let any client read files on the server."""
    s = str(path_or_text)
    if len(s) < 1000 and "\n" not in s and not s.lstrip().startswith(("{", "0 ")):
        if not allow_paths:
            raise ValueError("this server accepts the GEDCOM text, not a file path")
        if not Path(s).expanduser().is_file():
            raise ValueError(f"no such file: {s}")
        p = Path(s).expanduser()
        if p.suffix.lower() not in (".ged", ".gedcom", ".json"):
            raise ValueError("only .ged, .gedcom or .json files")
        raw = p.read_bytes()
        s = raw.decode("utf-8-sig", errors="replace")
    if s.lstrip().startswith("{"):
        return json.loads(s)
    return parse_gedcom(s)


# ---------------------------------------------------------------- checks

def year(ev, exact=False):
    d = str((ev or {}).get("date") or "").upper()
    if exact and d.startswith(("BEF", "AFT", "BET", "FROM")):
        return None
    m = re.search(r"\d{4}", d)
    return int(m[0]) if m else None


def _refs(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "source_ids" and isinstance(v, list):
                out.update(map(str, v))
            _refs(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _refs(v, out)
    elif isinstance(obj, str):
        out.update(SRC.findall(obj))


def _key(name):
    return " ".join(sorted(re.sub(r"[^\w ]", " ", (name or "").lower().replace("ё", "е")).split()))


def audit(data):
    people = {p["id"]: p for p in data.get("people", [])}
    fams = data.get("families", [])
    out = []

    def add(code, rid, **params):
        out.append({"code": code, "id": rid, "params": params})

    name = lambda pid: people[pid].get("display_name") or pid   # noqa: E731
    parents = collections.defaultdict(list)
    for f in fams:
        for c in f.get("children", []) + f.get("adopted_children", []):
            parents[c].append(f)

    for pid, p in people.items():
        if p.get("placeholder"):
            continue
        for ev in ("birth", "death"):
            d = (p.get(ev) or {}).get("date")
            if d and not re.search(r"\d{3,4}", str(d)) and not normalize_date(d):
                add("bad_date", pid, name=name(pid), other=d)
        b, d = year(p.get("birth"), True), year(p.get("death"), True)
        if not (p.get("birth") or {}).get("date") and not (p.get("death") or {}).get("date"):
            add("no_dates", pid, name=name(pid))
        if p.get("sex") not in ("M", "F"):
            add("no_sex", pid, name=name(pid))
        if b and d and d < b:
            add("death_before_birth", pid, name=name(pid), other=d)
        refs = set()
        _refs({k: v for k, v in p.items() if k != "id"}, refs)
        if not refs:
            add("no_documents", pid, name=name(pid))
        else:
            for ev in ("birth", "death"):
                e = p.get(ev) or {}
                if e.get("date") and not e.get("source_ids"):
                    add("event_no_source", pid, name=name(pid), event=ev)
        if b and d and d - b > 105:
            add("long_life", pid, name=name(pid), age=d - b)
        for f in parents.get(pid, []):
            if pid in f.get("adopted_children", []):
                continue
            for par in f.get("partners", []):
                q = people.get(par)
                if not q or not b:
                    continue
                qb, qd = year(q.get("birth"), True), year(q.get("death"), True)
                if qd and q.get("sex") == "F" and b > qd:
                    add("born_after_mother_death", pid, name=name(pid), other=name(par))
                if qd and q.get("sex") == "M" and b > qd + 1:
                    add("born_after_father_death", pid, name=name(pid), other=name(par))
                if qb:
                    age = b - qb
                    if age < 14:
                        add("parent_young", par, name=name(pid), other=name(par), age=age)
                    elif age > (55 if q.get("sex") == "F" else 75):
                        add("parent_old", par, name=name(pid), other=name(par), age=age)

    for f in fams:
        partners = [x for x in f.get("partners", []) if x in people]
        m = year(f.get("marriage"), True)
        for x in partners:
            xb = year(people[x].get("birth"), True)
            if m and xb and m - xb < 15:
                add("married_young", x, name=name(x), age=m - xb)
        if (partners or f.get("children")) and not f.get("source_ids") and not (f.get("marriage") or {}).get("source_ids"):
            add("family_no_source", f["id"], name=" + ".join(name(x) for x in partners) or f["id"])

    # duplicates: the same name and birth years within 2
    by_name = collections.defaultdict(list)
    for pid, p in people.items():
        by_name[_key(p.get("display_name"))].append(pid)
    for group in by_name.values():
        for i, a in enumerate(group):
            for b2 in group[i + 1:]:
                ya, yb = year(people[a].get("birth")), year(people[b2].get("birth"))
                if ya and yb and abs(ya - yb) <= 2:
                    add("possible_duplicate", a, name=f"{name(a)} ({a})", other=f"{name(b2)} ({b2})")

    # people outside the largest connected part (or the root's part)
    links = collections.defaultdict(set)
    for f in fams:
        group = f.get("partners", []) + f.get("children", []) + f.get("adopted_children", [])
        for x in group:
            links[x].update(group)
    seen_all, parts = set(), []
    for pid in people:
        if pid in seen_all:
            continue
        part, todo = {pid}, [pid]
        while todo:
            for y in links[todo.pop()]:
                if y not in part:
                    part.add(y)
                    todo.append(y)
        seen_all |= part
        parts.append(part)
    root = data.get("root_person_id")
    main = next((p for p in parts if root in p), max(parts, key=len) if parts else set())
    for pid, p in people.items():
        if pid not in main and not p.get("placeholder") and p.get("research_status") != "unlinked_candidate":
            add("unconnected", pid, name=name(pid))

    rank = {c: i for i, c in enumerate(CODES)}
    out.sort(key=lambda h: rank[h["code"]])
    return out


def text(h, lang="en"):
    en, ru = TEXT[h["code"]]
    params = dict(h["params"])
    if "event" in params:
        params["event"] = EVENTS[params["event"]][1 if lang == "ru" else 0]
    return (ru if lang == "ru" else en).format(**params)


def report(path_or_text, lang="en", limit=200, codes=None, allow_paths=True):
    data = load(path_or_text, allow_paths)
    found = audit(data)
    if codes:
        found = [h for h in found if h["code"] in set(codes)]
    counts = collections.Counter(h["code"] for h in found)
    return {"people": len(data.get("people", [])), "families": len(data.get("families", [])), "sources": len(data.get("sources", [])),
            "counts": dict(counts), "items": [{"code": h["code"], "id": h["id"], "text": text(h, lang)} for h in found[:limit]],
            "truncated": max(0, len(found) - limit)}
