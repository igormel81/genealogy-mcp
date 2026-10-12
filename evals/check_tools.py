"""The free half of the benchmark: every task that names a tool is answered by that tool directly, and the answer
must contain the expected facts. Runs in CI. (The model half — evals/run.py — needs an API key.)"""
import asyncio
import json
import re
import sys
from pathlib import Path

from genealogy_mcp.server import server

TASKS = json.loads((Path(__file__).parent / "tasks.json").read_text(encoding="utf-8"))


async def main():
    bad = 0
    for t in TASKS:
        if "tool" not in t:
            continue
        name, args = t["tool"]
        r = await server.call_tool(name, args)
        text = json.dumps(r.structured_content if r.structured_content is not None else [c.text for c in r.content], ensure_ascii=False)
        missing = [e for e in t["tool_expect"] if not re.search(e, text)]
        bad += bool(missing)
        print(f"{'ok  ' if not missing else 'FAIL'} {t['id']}" + (f"  missing {missing}" if missing else ""))
    print(f"\n{sum('tool' in t for t in TASKS) - bad}/{sum('tool' in t for t in TASKS)} tool answers correct")
    return bad


if __name__ == "__main__":
    sys.exit(1 if asyncio.run(main()) else 0)
