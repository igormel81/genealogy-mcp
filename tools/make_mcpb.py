"""Builds dist-mcpb/genealogy-mcp-<version>.mcpb — a Claude Desktop extension (double-click to install).

    python3 tools/make_mcpb.py            # writes mcpb/manifest.json and the .mcpb archive
    npx -y @anthropic-ai/mcpb validate mcpb/manifest.json

The manifest lists the tools and prompts of the server (taken from the server itself, so it never goes stale).
The archive uses the "uv" server type: Claude Desktop installs Python and the dependencies itself.
"""
import asyncio
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from genealogy_mcp import __version__  # noqa: E402
from genealogy_mcp.server import server  # noqa: E402


def first_sentence(text):
    t = " ".join((text or "").split())
    return t.split(". ")[0].rstrip(".") + "." if t else ""


def manifest():
    tools = asyncio.run(server.list_tools())
    return {
        "manifest_version": "0.4",
        "name": "genealogy-mcp",
        "display_name": "Genealogy research toolkit",
        "version": __version__,
        "description": "Find your family history with Claude: 171 archives and databases, name variants, old calendars, kinship, DNA, evidence checks, a research project that remembers, edits to your own GEDCOM tree.",
        "long_description": (ROOT / "mcpb" / "long_description.md").read_text(encoding="utf-8"),
        "author": {"name": "Igor Melnikov", "url": "https://github.com/igormel81"},
        "repository": {"type": "git", "url": "https://github.com/igormel81/genealogy-mcp"},
        "homepage": "https://github.com/igormel81/genealogy-mcp",
        "documentation": "https://github.com/igormel81/genealogy-mcp#readme",
        "support": "https://github.com/igormel81/genealogy-mcp/issues",
        "icon": "icon.png",
        "server": {
            "type": "uv",
            "entry_point": "src/genealogy_mcp/server.py",
            "mcp_config": {
                "command": "uv",
                "args": ["run", "--directory", "${__dirname}", "genealogy-mcp"],
                "env": {"GENEALOGY_MCP_HOME": "${user_config.projects_folder}",
                        "GENEALOGY_MCP_SITES": "${user_config.site_folder}"},
            },
        },
        "user_config": {
            "projects_folder": {
                "type": "directory",
                "title": "Research projects folder",
                "description": "Where the research projects (people, sources, search log) are kept between conversations.",
                "default": "${DOCUMENTS}/genealogy-mcp",
                "required": False,
            },
            "site_folder": {
                "type": "directory",
                "title": "Family archive site (gene-archive), optional",
                "description": "The folder of your gene-archive site (needs gene-archive installed) — or put the path of your .ged tree file in your request.",
                "required": False,
            },
        },
        "tools": [{"name": t.name, "description": first_sentence(t.description)} for t in tools],
        "prompts_generated": True,   # the server serves its prompts (start_research, check_find, …) itself
        "keywords": ["genealogy", "family history", "ancestry", "archives", "gedcom", "dna", "russia", "ukraine", "europe", "latin america"],
        "license": "MIT",
        "privacy_policies": ["https://archive.org/about/terms.php", "https://foundation.wikimedia.org/wiki/Policy:Privacy_policy",
                             "https://www.wikitree.com/wiki/Help:Privacy", "https://www.loc.gov/legal/"],
        "compatibility": {"platforms": ["darwin", "win32", "linux"], "runtimes": {"python": ">=3.10"}},
    }


def build():
    m = manifest()
    (ROOT / "mcpb" / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out = ROOT / "dist-mcpb" / f"genealogy-mcp-{__version__}.mcpb"   # not dist/: PyPI uploads everything there
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(ROOT / "mcpb" / "manifest.json", "manifest.json")
        z.write(ROOT / "mcpb" / "icon.png", "icon.png")
        for name in ("pyproject.toml", "README.md", "LICENSE"):
            z.write(ROOT / name, name)
        for f in sorted((ROOT / "src").rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts and not f.name.endswith((".pyc", ".egg-info")) and ".egg-info" not in str(f):
                z.write(f, f.relative_to(ROOT).as_posix())
    print(f"{out} ({out.stat().st_size // 1024} KB, {len(m['tools'])} tools)")
    return out


if __name__ == "__main__":
    build()
