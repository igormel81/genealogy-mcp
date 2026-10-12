"""Live checks of the open APIs (needs the internet). Run by .github/workflows/live.yml weekly and on demand:
    python tests/live/check_online.py
Prints a sample of every answer; exit 1 when a source returns an error or nothing for a query that must have hits."""
import json
import sys

from genealogy_mcp import online

MAY_BLOCK = {"chronicling_america", "open_list"}   # refuse GitHub's data-centre addresses; reported, not failed
CASES = [
    ("internet_archive", {"query": "Памятная книжка Тульской губернии"}),
    ("internet_archive", {"surname": "Сынковский"}),
    ("chronicling_america", {"surname": "Lincoln", "given": "Abraham", "year_from": 1860, "year_to": 1861}),
    ("wikitree", {"surname": "Lincoln", "given": "Abraham"}),
    ("open_archives", {"surname": "Jansen", "given": "Jan", "year_from": 1850, "year_to": 1860}),
    ("open_list", {"surname": "Мельников"}),
]
bad = 0
for source, kw in CASES:
    r = online.search(source, **kw)
    ok = not r.get("error") and r.get("count", 0) > 0
    if not ok and source in MAY_BLOCK and "may refuse" in str(r.get("error")):
        print(f"SKIP {source}: {r['error'][:60]}")
        continue
    bad += not ok
    print(f"{'OK  ' if ok else 'FAIL'} {source} {kw} → {r.get('error') or r.get('count')}")
    for x in r.get("results", [])[:2]:
        print("     ", json.dumps(x, ensure_ascii=False)[:300])
try:
    p = online.place_history("Богородицк", "ru")
    ok = bool(p["places"])
    print(f"{'OK  ' if ok else 'FAIL'} place_history Богородицк → {json.dumps(p['places'][:1], ensure_ascii=False)[:500]}")
    bad += not ok
except Exception as e:   # noqa: BLE001
    print("FAIL place_history", e)
    bad += 1
sys.exit(1 if bad else 0)
