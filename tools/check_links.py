"""Checks that every source in the catalogue still answers. Run weekly by .github/workflows/links.yml.

    python3 tools/check_links.py [--json report.json]

Exit code 1 when a site is gone (404/410, DNS failure), confirmed by a second request. Timeouts and 403 from bot protection are reported
as warnings: many archive sites refuse robots but work in a browser.
"""
import json
import socket
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CAT = Path(__file__).resolve().parent.parent / "src" / "genealogy_mcp" / "data" / "sources.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36 genealogy-mcp-linkcheck"


def check(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    for attempt in range(2):
        retry = True
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return "ok", r.status
        except urllib.error.HTTPError as e:
            result = ("dead" if e.code in (404, 410) else "warn"), e.code
            retry = e.code in (404, 410, 408, 429, 500, 502, 503, 504)
        except urllib.error.URLError as e:
            result = ("dead", "dns") if isinstance(e.reason, socket.gaierror) else ("warn", str(e.reason)[:80])
        except (TimeoutError, OSError) as e:
            result = "warn", str(e)[:80]
        if attempt or not retry:
            return result
        time.sleep(1)


def _filled(tpl):
    """A search template with a sample name: the search pages must answer too."""
    from urllib.parse import quote
    for k, v in {"given": "John", "surname": "Smith", "year_from": "1880", "year_to": "1900", "place": "", "q": "John Smith"}.items():
        tpl = tpl.replace("{" + k + "}", quote(v))
    return tpl


def main():
    catalogue = json.loads(CAT.read_text(encoding="utf-8"))
    targets = [(s["id"], s["url"]) for s in catalogue if s.get("url")]
    targets += [(s["id"] + " (search)", _filled(s["search"])) for s in catalogue if s.get("search")]
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda t: (t[0], t[1], *check(t[1])), targets))
    dead = [r for r in results if r[2] == "dead"]
    for sid, url, state, info in results:
        if state != "ok":
            print(f"{state:4} {sid:28} {info}  {url}")
    print(f"\n{len(results)} checked: {sum(r[2] == 'ok' for r in results)} ok, "
          f"{sum(r[2] == 'warn' for r in results)} warnings, {len(dead)} dead")
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(results, indent=1))
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
