"""Checks that every source in the catalogue still answers. Run weekly by .github/workflows/links.yml.

    python3 tools/check_links.py [--json report.json]

Exit code 1 when a site is gone (404/410, DNS failure). Timeouts and 403 from bot protection are reported
as warnings: many archive sites refuse robots but work in a browser.
"""
import json
import socket
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CAT = Path(__file__).resolve().parent.parent / "src" / "genealogy_mcp" / "data" / "sources.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36 genealogy-mcp-linkcheck"


def check(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return "ok", r.status
    except urllib.error.HTTPError as e:
        return ("dead" if e.code in (404, 410) else "warn"), e.code
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.gaierror):
            return "dead", "dns"
        return "warn", str(e.reason)[:80]
    except (TimeoutError, OSError) as e:
        return "warn", str(e)[:80]


def main():
    sources = [s for s in json.loads(CAT.read_text(encoding="utf-8")) if s.get("url")]
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda s: (s["id"], s["url"], *check(s["url"])), sources))
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
