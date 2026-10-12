"""The version is the same in every place a release reads it from."""
import json
import re
import unittest
from pathlib import Path

import genealogy_mcp

ROOT = Path(__file__).resolve().parent.parent


class Version(unittest.TestCase):
    def test_same_everywhere(self):
        v = genealogy_mcp.__version__
        pyproject = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M)
        self.assertEqual(pyproject.group(1), v, "pyproject.toml")
        server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
        self.assertEqual(server["version"], v, "server.json")
        self.assertEqual({p["version"] for p in server.get("packages", [])} or {v}, {v}, "server.json packages")
        manifest = json.loads((ROOT / "mcpb" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], v, "mcpb/manifest.json: run tools/make_mcpb.py")


if __name__ == "__main__":
    unittest.main()
