import asyncio
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from genealogy_mcp import coverage, films, gedfile

GED = Path(__file__).parent / "sample.ged"
LECA = {"parish": "church of Leca", "villages": ["Leca", "Porumbești"], "year": 1870, "part": "births", "film": "008123456",
        "frames": "112-118", "status": "complete", "source_ids": []}


class Coverage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["GENEALOGY_MCP_HOME"] = str(Path(self.tmp.name) / "home")

    def tearDown(self):
        os.environ.pop("GENEALOGY_MCP_HOME", None)
        self.tmp.cleanup()

    def test_local_project(self):
        coverage.mark("cov", [LECA, {"parish": "church of Leca", "year": 1871, "part": "births", "status": "partial", "up_to": "No. 30"},
                              {"parish": "church of Leca", "year": 1872, "part": "deaths", "status": "not_found", "film": "008123456"}])
        r = coverage.unread("cov", ["Porumbești"], 1868, 1872, ["births", "deaths"])["places"][0]
        self.assertEqual(r["parishes"], ["church of Leca"])
        self.assertEqual(r["parts"]["births"]["read"], ["1870"])
        self.assertEqual(r["parts"]["births"]["partial"][0]["up_to"], "No. 30")   # the village brings in the parish's books
        self.assertEqual(r["parts"]["births"]["unread"], ["1868–1869", "1872"])
        self.assertEqual(r["parts"]["deaths"]["not_found"][0]["year"], 1872)
        # marking the same book again replaces it and shows what was there
        again = coverage.mark("cov", [dict(LECA, status="partial", up_to="No. 4")])["saved"][0]
        self.assertEqual(again["previous"]["status"], "complete")
        self.assertEqual(len(coverage.load("cov")), 3)
        # another village: nothing read; a namesake parish is not mixed in
        self.assertIn("note", coverage.unread("cov", ["Capaclia Nouă"], 1870, 1871)["places"][0])
        self.assertFalse(coverage._same_place("Capaclia Nouă", "Capaclia Veche"))
        with self.assertRaises(ValueError):
            coverage.mark("cov", [{"parish": "Leca", "year": 1870, "part": "births", "status": "partial"}])   # no up_to
        with self.assertRaises(ValueError):
            coverage.mark("cov", [{"parish": "Leca", "year": 1870, "part": "christenings"}])

    def test_dry_run_writes_nothing(self):
        coverage.mark("dry", [LECA], dry_run=True)
        self.assertEqual(coverage.load("dry"), [])

    def test_ged_sidecar(self):
        ged = Path(self.tmp.name) / "tree.ged"
        shutil.copy(GED, ged)
        before = ged.read_bytes()
        coverage.mark(str(ged), [LECA])
        self.assertEqual(ged.read_bytes(), before)   # the tree itself is not touched
        side = json.loads(gedfile.sidecar(ged).read_text(encoding="utf-8"))
        self.assertEqual(side["coverage"][0]["parish"], "church of Leca")
        self.assertEqual(coverage.unread(str(ged), ["Leca"], 1870, 1870, ["births"])["places"][0]["parts"]["births"]["read"], ["1870"])

    def test_site_folder_kept_aside(self):
        site = Path(self.tmp.name) / "site"
        site.mkdir()
        (site / "site.json").write_text("{}", encoding="utf-8")
        tree = {"people": [], "families": [], "sources": [],
                "coverage": [{"parish": "Capaclia Nouă", "villages": ["Sadâc"], "year": 1880, "part": "births", "status": "complete"}]}
        (site / "family_tree.json").write_text(json.dumps(tree), encoding="utf-8")
        r = coverage.mark(str(site), [dict(LECA, parish="Capaclia Nouă", villages=["Sadâc"], year=1881)])
        self.assertIn("gene apply", r["note"])
        self.assertEqual(json.loads((site / "family_tree.json").read_text(encoding="utf-8")), tree)   # not written
        b = coverage.unread(str(site), ["Sadâc"], 1880, 1882, ["births"])["places"][0]["parts"]["births"]
        self.assertEqual(b["read"], ["1880–1881"])   # the site's own section and this server's file together
        self.assertEqual(b["unread"], ["1882"])

    def test_film_plan_skips_what_is_read(self):
        coverage.mark("plan", [LECA, {"parish": "church of Leca", "year": 1871, "part": "deaths", "status": "partial", "up_to": "No. 12"}])
        p = films.plan("church of Leca", 1866, 1874, None, [{"film": "008123456", "years": "1860-1872", "frames": 900},
                                                             {"film": "008999", "years": "1871–75"}], coverage.load("plan"))
        self.assertEqual(p["already_read"], ["1870 births"])
        self.assertEqual(p["reading_order"][0]["film"], "008123456")
        self.assertEqual(p["reading_order"][0]["read_years"][0], 1872)   # newest first
        self.assertEqual(p["reading_order"][0]["resume_from"], {"1871 deaths": "No. 12"})
        self.assertEqual(p["reading_order"][1]["read_years"], [1874, 1873])
        self.assertEqual(p["budget"]["thumbnails"], 1700)
        self.assertTrue(any("429" in r for r in p["rules"]))
        none = films.plan("Покровская церковь с. Сынково", 1880, 1885, ["births"], lang="ru")
        self.assertIn("каталог FamilySearch", none["reading_order"][0]["do"])

    def test_tools(self):
        from genealogy_mcp.server import server

        async def go():
            r = await server.call_tool("project_coverage", {"project": "srv", "action": "mark", "entries": [LECA]})
            self.assertEqual(r.structured_content["saved"][0]["entry"]["year"], 1870)
            r = await server.call_tool("project_coverage", {"project": "srv", "places": ["Porumbești"], "year_from": 1869, "year_to": 1870})
            self.assertEqual(r.structured_content["places"][0]["parts"]["births"]["unread"], ["1869"])
            r = await server.call_tool("film_reading_plan", {"parish": "church of Leca", "year_from": 1869, "year_to": 1870,
                                                             "films": [{"film": "1", "years": "1860-1880"}], "project": "srv"})
            self.assertEqual(r.structured_content["already_read"], ["1870 births"])
        asyncio.run(go())


if __name__ == "__main__":
    unittest.main()
