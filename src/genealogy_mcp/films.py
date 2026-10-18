"""A plan for reading unindexed FamilySearch films page by page: which films and books to read in which order, about how
many requests it takes (thumbnails to find the book, full frames to read it) and what to log, so the work survives a
rate-limit pause and nobody reads the same frames twice."""
import math
import re

from . import coverage

# rough full frames per year of a rural parish register (a frame is usually one opening: two pages)
FRAMES_PER_YEAR = {"births": 8, "marriages": 3, "deaths": 6, "confession": 15, "revision": 30, "census": 30, "other": 10}
FILM_FRAMES = 800          # an average film when the catalogue does not say
SAFE_FULL_FRAMES = 200     # full frames per session that stay under the limit even after a recent refusal
SAFE_THUMBNAILS = 2500     # thumbnails per session


def _span(v):
    """'1860-1875', '1860–75', [1860, 1875], 1860 → (1860, 1875)."""
    if isinstance(v, (list, tuple)) and v:
        a, b = int(v[0]), int(v[-1])
        return min(a, b), max(a, b)
    ys = [int(x) for x in re.findall(r"\d{4}", str(v or ""))]
    m = re.search(r"(\d{4})\s*[-–—]\s*(\d{2})(?!\d)", str(v or ""))
    if m:
        ys = [int(m[1]), int(m[1][:2] + m[2])]
    return (min(ys), max(ys)) if ys else None


def plan(parish, year_from, year_to, parts=None, films=None, project_entries=None, order="newest_first", lang="en"):
    ru = lang == "ru"
    if not str(parish or "").strip():
        raise ValueError("name the parish (its church and village) — books are kept by the church")
    y1, y2 = int(year_from), int(year_to or year_from)
    if y2 < y1:
        y1, y2 = y2, y1
    if y2 - y1 > 150:
        raise ValueError("at most 150 years at a time")
    want = [coverage.part(p) for p in (parts or coverage.REGISTER_PARTS)]

    # what is already read (from the project's coverage)
    done, partial = set(), {}
    if project_entries:
        st = coverage.unread("", [parish], y1, y2, want, lang, entries=project_entries)["places"][0]["parts"]
        for p, r in st.items():
            for rng in r["read"]:
                a, b = (_span(rng) or (None, None))
                if a:
                    done |= {(y, p) for y in range(a, b + 1)}
            for x in r["partial"]:
                partial[(x["year"], p)] = x.get("up_to")
    todo = [(y, p) for y in range(y1, y2 + 1) for p in want if (y, p) not in done]
    years_desc = order != "oldest_first"

    steps, budget_thumbs, budget_full = [], 0, 0
    films = [f if isinstance(f, dict) else {"film": str(f)} for f in (films or [])]
    if not films:
        steps.append({"step": 1, "do": (
            "Find the films: FamilySearch Catalog → search by place (country → province → district → village or parish), "
            "open the entry with the church's registers (метрические книги) and note each film number (DGS) with its years "
            "and item. Then call film_reading_plan again with films=[{film, years, frames}]."
            if not ru else
            "Найдите плёнки: каталог FamilySearch → поиск по месту (страна → губерния → уезд → село или приход), откройте "
            "запись с метрическими книгами церкви и выпишите каждую плёнку (номер DGS) с годами и пунктом (item). Потом "
            "вызовите film_reading_plan снова с films=[{film, years, frames}]."),
            "url": "https://www.familysearch.org/search/catalog"})
        uncovered = sorted({y for y, _ in todo})
    else:
        def cover(f):
            if f.get("years"):
                return _span(f["years"])
            return _span([f["year_from"], f.get("year_to") or f["year_from"]]) if f.get("year_from") else None
        todo_set = set(todo)
        ranked = []
        for f in films:
            sp = cover(f)
            ys = [y for y, _ in todo if sp and sp[0] <= y <= sp[1]] if sp else []
            ranked.append((f, sp, sorted(set(ys), reverse=years_desc)))
        ranked.sort(key=lambda x: (-len(x[2]), -(x[1][1] if x[1] else 0) if years_desc else (x[1][0] if x[1] else 9999)))
        covered = set()
        n = 0
        for f, sp, ys in ranked:
            ys = [y for y in ys if y not in covered]
            if not ys:
                continue
            covered |= set(ys)
            n += 1
            frames = int(f.get("frames") or FILM_FRAMES)
            parts_here = {y: [p for p in want if (y, p) in todo_set] for y in ys}
            full = sum(FRAMES_PER_YEAR[p] for y in ys for p in parts_here[y]) + len(ys)   # + the year's summary page
            budget_thumbs += frames
            budget_full += full
            resume = {f"{y} {p}": partial[(y, p)] for y in ys for p in parts_here[y] if (y, p) in partial}
            steps.append({
                "step": n, "film": f.get("film"), **({"item": f["item"]} if f.get("item") else {}), "film_years": f"{sp[0]}–{sp[1]}" if sp else None,
                "read_years": ys, "parts": want,
                "do": ((f"Thumbnails first (up to ~{frames}): find the title page of the {parish} book for each year, its parts "
                        "and the end-of-year summary that names the church. Note the frame range of each year. Then open full "
                        f"frames only for the record pages (~{full}).")
                       if not ru else
                       (f"Сначала миниатюры (до ~{frames}): найдите титульный лист книги {parish} за каждый год, её части и "
                        "итоговую ведомость в конце года, где назван храм. Запишите диапазон кадров каждого года. Потом крупно "
                        f"открывайте только страницы с записями (~{full}).")),
                **({"resume_from": resume} if resume else {}),
                **({"note": f["note"]} if f.get("note") else {})})
        uncovered = sorted({y for y, _ in todo} - covered)
    sessions = max(math.ceil(budget_full / SAFE_FULL_FRAMES), math.ceil(budget_thumbs / SAFE_THUMBNAILS)) if budget_full else 0
    out = {
        "parish": parish, "years": f"{y1}–{y2}", "parts": want,
        "already_read": sorted(f"{y} {p}" for y, p in done) or None,
        "to_read": len(todo),
        "reading_order": steps,
        "not_on_listed_films": uncovered if films else None,
        "budget": {
            "thumbnails": budget_thumbs, "full_frames": budget_full, "sessions": sessions,
            "assumes": ("Full frames per year of a rural parish: " + ", ".join(f"{p} {FRAMES_PER_YEAR[p]}" for p in want) +
                        f", plus one summary page; a film of {FILM_FRAMES} frames when its size is not given. A large town "
                        "parish needs several times more." if not ru else
                        "Полных кадров в год у сельского прихода: " + ", ".join(f"{p} {FRAMES_PER_YEAR[p]}" for p in want) +
                        f", плюс итоговая ведомость; плёнка — {FILM_FRAMES} кадров, если её размер не указан. Городскому "
                        "приходу нужно в разы больше.")} if films else None,
        "rules": ([
            "The limit is not fixed: from a few thousand thumbnails to about 250 full frames after a recent refusal. Keep "
            f"a session to about {SAFE_FULL_FRAMES} full frames.",
            "After HTTP 429 (too many requests) stop for at least an hour; do not retry at once.",
            "One session at a time: parallel tabs or scripts share the limit and lengthen the block.",
            "Trust the title page and table of contents of the volume, not the file number of the inventory or the catalogue.",
        ] if not ru else [
            "Лимит не постоянный: от нескольких тысяч миниатюр до примерно 250 полных кадров после недавнего отказа. "
            f"Держите сессию в пределах ~{SAFE_FULL_FRAMES} полных кадров.",
            "После HTTP 429 (слишком много запросов) — пауза не меньше часа, без немедленных повторов.",
            "Одна сессия за раз: параллельные вкладки и скрипты делят лимит и продлевают блокировку.",
            "Верьте титулу и оглавлению тома, а не номеру дела в описи или каталоге.",
        ]),
        "log": {
            "how": ("After each book, save what was read with project_coverage (action='mark') — complete, partial with "
                    "up_to (the last record number read) or not_found — and cite the film and frames. Save each record "
                    "found as a source (film, image, archive, fond, opis, delo, folio)." if not ru else
                    "После каждой книги отметьте прочитанное в project_coverage (action='mark') — complete, partial с up_to "
                    "(последний прочитанный номер записи) или not_found — с плёнкой и кадрами. Каждую найденную запись "
                    "сохраните как источник (плёнка, кадр, архив, фонд, опись, дело, лист)."),
            "entry": {"parish": parish, "villages": ["…"], "year": y2 if years_desc else y1, "part": want[0],
                      "film": (films[0].get("film") if films else "…"), "frames": "…–…", "status": "complete | partial | not_found",
                      "up_to": "No. … (for partial)", "source_ids": []},
        },
    }
    return {k: v for k, v in out.items() if v is not None}
