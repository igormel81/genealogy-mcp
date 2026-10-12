"""The benchmark: the same genealogy questions to a Claude model without tools and with genealogy-mcp.

    pip install anthropic .
    python evals/run.py                       # both modes, every task, claude-opus-5-5
    python evals/run.py --mode tools --only pokrov_1885,dna_870 --effort low
    python evals/run.py --dry                 # list tasks and tools, no API calls

Every run calls the Claude API and costs money (31 tasks × 2 modes). Credentials: ANTHROPIC_API_KEY or an
`ant auth login` profile. Results go to evals/results/<model>-<date>.json; a task passes when the final answer
matches every regular expression in its "expect".
"""
import argparse
import asyncio
import datetime
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TASKS = json.loads((HERE / "tasks.json").read_text(encoding="utf-8"))
SYSTEM = "You are a careful genealogist. Answer the question; be brief and give the exact value asked for."
SKIP_TOOLS = {"project_save", "project_log", "project_transfer", "project_view"}   # no files written during a benchmark


def mcp_tools():
    from genealogy_mcp.server import server
    tools = asyncio.run(server.list_tools())
    return [{"name": t.name, "description": t.description or "", "input_schema": t.input_schema} for t in tools if t.name not in SKIP_TOOLS]


def call_tool(name, args):
    from genealogy_mcp.server import server
    r = asyncio.run(server.call_tool(name, args))
    data = r.structured_content if r.structured_content is not None else [getattr(c, "text", "") for c in r.content]
    text = json.dumps(data, ensure_ascii=False)
    return text[:20000], bool(isinstance(data, dict) and data.get("error")) or bool(getattr(r, "is_error", False))


def ask(client, model, effort, question, tools):
    import anthropic
    messages = [{"role": "user", "content": question}]
    calls = []
    for _ in range(12):   # at most 12 model turns per task
        kwargs = dict(model=model, max_tokens=16000, system=SYSTEM, messages=messages,
                      output_config={"effort": effort}, betas=["server-side-fallback-2026-07-01"], fallbacks="default")
        if tools:
            kwargs["tools"] = tools
        try:
            response = client.beta.messages.create(**kwargs)
        except anthropic.APIStatusError as e:
            return {"error": f"{e.status_code}: {e.message}", "calls": calls}
        if response.stop_reason == "refusal":
            return {"answer": "", "refused": True, "calls": calls, "served_by": response.model}
        uses = [b for b in response.content if b.type == "tool_use"]
        if response.stop_reason != "tool_use" or not uses:
            text = "\n".join(b.text for b in response.content if b.type == "text")
            return {"answer": text, "calls": calls, "served_by": response.model,
                    "tokens": {"in": response.usage.input_tokens, "out": response.usage.output_tokens}}
        messages.append({"role": "assistant", "content": response.content})   # keep thinking blocks as they are
        results = []
        for u in uses:
            out, is_err = call_tool(u.name, u.input)
            calls.append(u.name)
            results.append({"type": "tool_result", "tool_use_id": u.id, "content": out, **({"is_error": True} if is_err else {})})
        messages.append({"role": "user", "content": results})
    return {"error": "too many turns", "calls": calls}


def grade(task, answer):
    return all(re.search(e, answer or "", flags=re.I) for e in task["expect"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--mode", default="both", choices=["both", "bare", "tools"])
    ap.add_argument("--only", default="", help="comma-separated task ids")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    tasks = [t for t in TASKS if not a.only or t["id"] in a.only.split(",")]
    os.environ.setdefault("GENEALOGY_MCP_HOME", tempfile.mkdtemp())
    tools = mcp_tools()
    if a.dry:
        print(f"{len(tasks)} tasks, {len(tools)} tools: {', '.join(t['name'] for t in tools)}")
        return 0
    import anthropic
    client = anthropic.Anthropic()
    modes = ["bare", "tools"] if a.mode == "both" else [a.mode]
    rows, score = [], {m: 0 for m in modes}
    for t in tasks:
        row = {"id": t["id"], "question": t["question"]}
        for m in modes:
            r = ask(client, a.model, a.effort, t["question"], tools if m == "tools" else None)
            r["pass"] = grade(t, r.get("answer"))
            score[m] += r["pass"]
            row[m] = r
        rows.append(row)
        print(t["id"].ljust(22), "  ".join(f"{m}:{'PASS' if row[m]['pass'] else 'fail'}" for m in modes), flush=True)
    print("\n" + "  ".join(f"{m}: {score[m]}/{len(tasks)}" for m in modes))
    out = HERE / "results" / f"{a.model}-{a.effort}-{datetime.date.today().isoformat()}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"model": a.model, "effort": a.effort, "score": score, "tasks": len(tasks), "rows": rows},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"→ {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
