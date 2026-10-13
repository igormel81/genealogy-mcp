"""A GEDCOM file as the project: the tree the user keeps in their own program (exported from MyHeritage, Ancestry,
Gramps, RootsMagic, Family Historian, webtrees…), read and changed in place.

Nothing the server does not understand is touched: every line of a record that was not changed is written back byte
for byte — other programs' own tags, media links, notes, the header. A changed record keeps its other lines too; only
the fields that changed are rewritten. Before every write the previous file is kept as <file>.bak, and before the
first one the original as <name>.before-genealogy-mcp.ged.

GEDCOM has no place for a research log, open leads or the corrections log, so those live next to the file in
<file>.research.json.
"""
import difflib
import json
import re
import shutil
from pathlib import Path

from .dates import GED_MONTHS

LINE = re.compile(r"\s*(\d+)\s+(?:@([^@]+)@\s+)?(\S+)(?: (.*))?$")
WRITABLE_CHARSETS = ("", "UTF-8", "UTF8", "ASCII")
CHUNK = 200   # a GEDCOM line is at most 255 characters: longer text goes on in CONC lines

EVENTS = {"birth": ("BIRT",), "baptism": ("CHR", "BAPM"), "death": ("DEAT",), "burial": ("BURI",)}
FIELDS = {   # what is kept in the file; other fields of a record are reported and not saved
    "person": {"id", "display_name", "given_names", "surname", "sex", "occupation", "notes", "source_ids", *EVENTS},
    "family": {"id", "partners", "children", "marriage", "notes", "source_ids"},
    "source": {"id", "title", "author", "locator", "url", "scope", "notes", "kind"},
}


def is_ged(name):
    s = str(name or "").strip()
    return s.lower().endswith((".ged", ".gedcom")) and Path(s).expanduser().is_file()


def sidecar(path):
    return Path(path).with_name(Path(path).name + ".research.json")


def original_copy(path):
    p = Path(path)
    return p.with_name(p.stem + ".before-genealogy-mcp" + p.suffix)


# ---------------------------------------------------------------- a lossless tree of lines

class Node:
    __slots__ = ("level", "xref", "tag", "value", "children", "raw")

    def __init__(self, level, tag, value="", xref="", raw=None):
        self.level, self.tag, self.value, self.xref, self.raw = level, tag, value, xref, raw
        self.children = []

    def line(self):
        if self.raw is not None:
            return self.raw
        x = f"@{self.xref}@ " if self.xref else ""
        return f"{self.level} {x}{self.tag}" + (f" {self.value}" if self.value else "")

    def lines(self):
        if self.raw is not None or (self.level is not None and self.level >= 0):
            yield self.line()
        for c in self.children:
            yield from c.lines()

    def all(self, *tags):
        return [c for c in self.children if c.tag in tags]

    def find(self, *tags):
        return next(iter(self.all(*tags)), None)

    def set(self, value):
        value = str(value)
        if value != self.value:
            self.value, self.raw = value, None

    def add(self, tag, value="", after=None):
        node = Node(self.level + 1, tag, str(value))
        if after is not None and after in self.children:
            i = self.children.index(after) + 1
        else:   # before the change date, if the record has one, else at the end
            i = next((k for k, c in enumerate(self.children) if c.tag == "CHAN"), len(self.children))
        self.children.insert(i, node)
        return node

    def remove(self, node):
        self.children.remove(node)


def parse(text):
    root = Node(-1, "")
    stack = [root]
    lines = re.split(r"\r\n|\n|\r", text)
    if lines and lines[-1] == "":
        lines.pop()
    for raw in lines:
        m = LINE.match(raw)
        if not m:   # a blank or broken line stays where it was
            stack[-1].children.append(Node(None, None, raw=raw))
            continue
        level = int(m[1])
        while stack[-1].level is not None and stack[-1].level >= level:
            stack.pop()
        node = Node(level, m[3].upper(), m[4] or "", (m[2] or "").strip(), raw=raw)
        stack[-1].children.append(node)
        stack.append(node)
    return root


def _text(node):
    """The text of a NOTE / TEXT with its CONT and CONC lines."""
    out = node.value
    for c in node.children:
        if c.tag == "CONT":
            out += "\n" + c.value
        elif c.tag == "CONC":
            out += c.value
    return out


def _chunks(s):
    out = []
    while len(s) > CHUNK:
        cut = CHUNK
        while cut > 1 and (s[cut - 1] == " " or s[cut] == " "):   # some programs drop spaces at a CONC break
            cut -= 1
        out.append(s[:cut])
        s = s[cut:]
    return out + [s]


def _set_text(node, text):
    node.children = [c for c in node.children if c.tag not in ("CONT", "CONC")] if node.children else []
    lines = str(text).split("\n")
    first = _chunks(lines[0])
    node.set(first[0])
    tail = [("CONC", x) for x in first[1:]]
    for line in lines[1:]:
        parts = _chunks(line)
        tail += [("CONT", parts[0])] + [("CONC", x) for x in parts[1:]]
    for i, (tag, value) in enumerate(tail):
        node.children.insert(i, Node(node.level + 1, tag, value))


def _ptr(rid):
    return f"@{rid}@"


def _ids(node, tag):
    return [c.value.strip()[1:-1] for c in node.all(tag) if c.value.strip().startswith("@")]


def _iso_to_ged(m):
    y, mo, d = m[1], m[2], m[3]
    return " ".join(x for x in (str(int(d)) if d else "", GED_MONTHS[int(mo) - 1] if mo else "", y) if x)


def ged_date(d):
    """'1899-10-09' → '9 OCT 1899'; 'ABT 1899-10' → 'ABT OCT 1899'; GEDCOM dates stay as they are."""
    return re.sub(r"\b(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?\b", _iso_to_ged, str(d or "").strip())


# ---------------------------------------------------------------- the file

class GedFile:
    def __init__(self, path):
        self.path = Path(path).expanduser()
        raw = self.path.read_bytes()
        self.bom = raw.startswith(b"\xef\xbb\xbf")
        self.readonly = ""
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", errors="replace")
            self.readonly = "the file is not in UTF-8"
        self.nl = "\r\n" if "\r\n" in text else "\n"
        self.trailing = text.endswith(("\n", "\r"))
        self.root = parse(text)
        head = self.record_by_tag("HEAD")
        char = ((head.find("CHAR") if head else None) or Node(1, "CHAR")).value.strip().upper()
        if char not in WRITABLE_CHARSETS:
            self.readonly = f"the file is in {char}"
        if self.readonly:
            self.readonly += ": export the tree from your program again as GEDCOM in UTF-8 to make changes in it"

    def text(self):
        body = self.nl.join(self.root.lines()) + (self.nl if self.trailing else "")
        return ("﻿" if self.bom else "") + body

    def record_by_tag(self, tag):
        return next((c for c in self.root.children if c.tag == tag), None)

    def records(self, tag):
        return {c.xref: c for c in self.root.children if c.tag == tag and c.xref}

    def xrefs(self):
        return {c.xref for c in self.root.children if c.xref}

    # ------------------------------------------------ reading: the project's structure

    def _event(self, node):
        if node is None:
            return None
        ev = {}
        if node.find("DATE"):
            ev["date"] = node.find("DATE").value.strip()
        if node.find("PLAC"):
            ev["place_as_recorded"] = node.find("PLAC").value.strip()
        if _ids(node, "SOUR"):
            ev["source_ids"] = _ids(node, "SOUR")
        return ev

    def _notes(self, rec, url=False):
        return [c for c in rec.all("NOTE") if not c.value.startswith("@") and _text(c).startswith("http") == url]

    def person(self, n):
        p = {"id": n.xref}
        name = n.find("NAME")
        given, surname = "", ""
        if name:
            m = re.match(r"([^/]*)(?:/([^/]*)/?)?", name.value)
            given, surname = (m[1] or "").strip(), (m[2] or "").strip()
            given = given or (name.find("GIVN").value.strip() if name.find("GIVN") else "")
            surname = surname or (name.find("SURN").value.strip() if name.find("SURN") else "")
        p["given_names"], p["surname"] = given, surname
        p["display_name"] = " ".join(x for x in (given, surname) if x) or "?"
        if n.find("SEX"):
            p["sex"] = n.find("SEX").value.strip()[:1].upper()
        for key, tags in EVENTS.items():
            ev = self._event(n.find(*tags))
            if ev:
                p[key] = ev
        if n.find("OCCU"):
            p["occupation"] = n.find("OCCU").value.strip()
        notes = self._notes(n)
        if notes:
            p["notes"] = "\n\n".join(_text(x) for x in notes)
        if _ids(n, "SOUR"):
            p["source_ids"] = _ids(n, "SOUR")
        return p

    def family(self, n):
        f = {"id": n.xref, "partners": _ids(n, "HUSB") + _ids(n, "WIFE"), "children": _ids(n, "CHIL")}
        m = self._event(n.find("MARR"))
        if m is not None:
            f["marriage"] = m
        notes = self._notes(n)
        if notes:
            f["notes"] = "\n\n".join(_text(x) for x in notes)
        if _ids(n, "SOUR"):
            f["source_ids"] = _ids(n, "SOUR")
        return f

    def source(self, n):
        s = {"id": n.xref, "title": (n.find("TITL").value.strip() if n.find("TITL") else "") or n.xref, "kind": "record"}
        for key, tag in (("author", "AUTH"), ("locator", "PUBL")):
            if n.find(tag):
                s[key] = _text(n.find(tag)).strip()
        if n.find("TEXT"):
            s["scope"] = _text(n.find("TEXT"))
        urls = self._notes(n, url=True)
        if urls:
            s["url"] = _text(urls[0]).strip()
        notes = self._notes(n)
        if notes:
            s["notes"] = "\n\n".join(_text(x) for x in notes)
        return s

    def project(self):
        return {"people": [self.person(n) for n in self.records("INDI").values()],
                "families": [self.family(n) for n in self.records("FAM").values()],
                "sources": [self.source(n) for n in self.records("SOUR").values()]}

    # ------------------------------------------------ writing: only what changed

    @staticmethod
    def _set(rec, tag, value, *alt):
        node = rec.find(tag, *alt)
        if value in (None, ""):
            if node:
                rec.remove(node)
        elif node:
            node.set(value)
        else:
            rec.add(tag, value)

    @staticmethod
    def _sync_ptrs(rec, tag, old, new):
        for rid in [x for x in old if x not in new]:
            for c in [c for c in rec.all(tag) if c.value.strip() == _ptr(rid)]:
                rec.remove(c)
        for rid in [x for x in new if x not in old]:
            same = rec.all(tag)
            rec.add(tag, _ptr(rid), after=same[-1] if same else None)

    def _set_notes(self, rec, old, new, url=False):
        if old == new:
            return
        nodes = self._notes(rec, url)
        if not new:
            for x in nodes:
                rec.remove(x)
            return
        node = nodes[0] if nodes else rec.add("NOTE")
        for x in nodes[1:]:
            rec.remove(x)
        _set_text(node, new)

    def _set_event(self, rec, tags, old, new):
        old, new = old or {}, new or {}
        if old == new:
            return
        node = rec.find(*tags)
        if not new:
            if node:
                rec.remove(node)
            return
        if node is None:
            node = rec.add(tags[0])
        if old.get("date") != new.get("date"):
            self._set(node, "DATE", ged_date(new.get("date")))
        place = new.get("place_as_recorded") or new.get("place")
        if (old.get("place_as_recorded") or old.get("place")) != place:
            self._set(node, "PLAC", place)
        self._sync_ptrs(node, "SOUR", old.get("source_ids") or [], new.get("source_ids") or [])
        if node.value == "Y" and (node.find("DATE") or node.find("PLAC")):
            node.set("")

    def patch_person(self, n, old, new):
        names = ("given_names", "surname", "display_name")
        if any(old.get(k) != new.get(k) for k in names):
            given, surname = new.get("given_names"), new.get("surname")
            if old.get("display_name") != new.get("display_name") and given == old.get("given_names") and surname == old.get("surname"):
                parts = str(new.get("display_name") or "").rsplit(" ", 1)
                given, surname = (parts[0], parts[1]) if len(parts) == 2 else (parts[0], "")
            name = n.find("NAME")
            suffix = ""
            if name:
                m = re.match(r"[^/]*/[^/]*/(.*)$", name.value)
                suffix = m[1] if m else ""
            value = f"{given or ''} /{surname or ''}/{suffix}".strip()
            if name is None:
                name = Node(1, "NAME", value)
                n.children.insert(0, name)
            name.set(value)
            for tag, v in (("GIVN", given), ("SURN", surname)):
                if name.find(tag):
                    self._set(name, tag, v)
        if old.get("sex") != new.get("sex"):
            self._set(n, "SEX", new.get("sex"))
        for key, tags in EVENTS.items():
            self._set_event(n, tags, old.get(key), new.get(key))
        if old.get("occupation") != new.get("occupation"):
            self._set(n, "OCCU", new.get("occupation"))
        self._set_notes(n, old.get("notes"), new.get("notes"))
        self._sync_ptrs(n, "SOUR", old.get("source_ids") or [], new.get("source_ids") or [])

    def patch_family(self, n, old, new, people):
        old_p, new_p = old.get("partners") or [], new.get("partners") or []
        if old_p != new_p:
            first = n.find("HUSB", "WIFE")
            at = n.children.index(first) if first else 0
            for c in n.all("HUSB", "WIFE"):
                n.remove(c)
            for i, pid in enumerate(new_p):
                sex = (people.get(pid) and people[pid].find("SEX") and people[pid].find("SEX").value.strip().upper()) or ""
                n.children.insert(at + i, Node(1, "WIFE" if sex.startswith("F") else "HUSB", _ptr(pid)))
        self._sync_ptrs(n, "CHIL", old.get("children") or [], new.get("children") or [])
        self._set_event(n, ("MARR",), old.get("marriage"), new.get("marriage"))
        self._set_notes(n, old.get("notes"), new.get("notes"))
        self._sync_ptrs(n, "SOUR", old.get("source_ids") or [], new.get("source_ids") or [])
        # the people's side of the links
        for tag, o, w in (("FAMS", old_p, new_p), ("FAMC", old.get("children") or [], new.get("children") or [])):
            for pid in set(o) - set(w):
                if pid in people:
                    self._sync_ptrs(people[pid], tag, [n.xref], [])
            for pid in set(w) - set(o):
                if pid in people and n.xref not in _ids(people[pid], tag):
                    self._sync_ptrs(people[pid], tag, [], [n.xref])

    def patch_source(self, n, old, new):
        for key, tag in (("title", "TITL"), ("author", "AUTH"), ("locator", "PUBL")):
            if old.get(key) != new.get(key):
                self._set(n, tag, new.get(key))
        if old.get("scope") != new.get("scope"):
            node = n.find("TEXT")
            if not new.get("scope"):
                if node:
                    n.remove(node)
            else:
                _set_text(node or n.add("TEXT"), new["scope"])
        self._set_notes(n, old.get("url"), new.get("url"), url=True)
        self._set_notes(n, old.get("notes"), new.get("notes"))

    def create(self, tag, rid):
        node = Node(0, tag, xref=rid)
        trlr = self.record_by_tag("TRLR")
        i = self.root.children.index(trlr) if trlr else len(self.root.children)
        self.root.children.insert(i, node)
        return node

    def delete(self, rid):
        """The record and every pointer to it (in families, citations, associations)."""
        self.root.children = [c for c in self.root.children if c.xref != rid]

        def walk(node):
            node.children = [c for c in node.children if c.value.strip() != _ptr(rid)]
            for c in node.children:
                walk(c)
        walk(self.root)

    def apply(self, data):
        """Writes the project's people, families and sources into the tree where they differ from it."""
        before = self.project()
        old = {k: {r["id"]: r for r in before[k]} for k in ("people", "families", "sources")}
        new = {k: {r["id"]: r for r in data.get(k, [])} for k in ("people", "families", "sources")}
        for coll, tag in (("sources", "SOUR"), ("people", "INDI")):
            nodes = self.records(tag)
            for rid, rec in new[coll].items():
                o = old[coll].get(rid)
                if o == rec:
                    continue
                node = nodes.get(rid) or self.create(tag, rid)
                (self.patch_source if tag == "SOUR" else self.patch_person)(node, o or {}, rec)
        people, fams = self.records("INDI"), self.records("FAM")
        for rid, rec in new["families"].items():
            o = old["families"].get(rid)
            if o != rec:
                self.patch_family(fams.get(rid) or self.create("FAM", rid), o or {}, rec, people)
        for coll in ("families", "people", "sources"):
            for rid in set(old[coll]) - set(new[coll]):
                self.delete(rid)


# ---------------------------------------------------------------- the project around the file

LOG_KEYS = ("title", "root_person_id", "research_leads", "research_log", "corrections")


def load(path):
    g = GedFile(path)
    data = g.project()
    side = sidecar(g.path)
    extra = json.loads(side.read_text(encoding="utf-8")) if side.exists() else {}
    data.update({"title": extra.get("title") or g.path.stem, "created": extra.get("created", ""),
                 "root_person_id": extra.get("root_person_id") or (data["people"][0]["id"] if data["people"] else None),
                 "research_leads": extra.get("research_leads", []), "research_log": extra.get("research_log", []),
                 "corrections": extra.get("corrections", []), "_xrefs": sorted(g.xrefs())})
    if g.readonly:
        data["_readonly"] = g.readonly
    return data


def save(path, data, write=True):
    """Writes the changes into the file (keeping a copy) and the logs next to it. Returns the changed lines."""
    g = GedFile(path)
    before = g.text()
    g.apply(data)
    after = g.text()
    if after != before and g.readonly:
        raise ValueError(f"{g.path.name} is not changed: {g.readonly}")
    diff = "\n".join(list(difflib.unified_diff(before.lstrip("﻿").splitlines(), after.lstrip("﻿").splitlines(),
                                               g.path.name, g.path.name, n=1, lineterm=""))[2:202])
    if write:
        if after != before:
            if not original_copy(g.path).exists():
                shutil.copy2(g.path, original_copy(g.path))
            shutil.copy2(g.path, g.path.with_name(g.path.name + ".bak"))
            tmp = g.path.with_name(g.path.name + ".tmp")
            with open(tmp, "w", encoding="utf-8", newline="") as fh:
                fh.write(after)
            tmp.replace(g.path)
        side = {k: data.get(k) for k in LOG_KEYS}
        tmp = sidecar(g.path).with_suffix(".tmp")
        tmp.write_text(json.dumps(side, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(sidecar(g.path))
    return diff
