"""The bridge to gene-archive: a site folder as a project, changes through `gene apply`.
Skipped when gene-archive is not installed (CI installs it)."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from genealogy_mcp import project

HAVE_GENE = shutil.which("gene") is not None or importlib.util.find_spec("gene_archive") is not None


@unittest.skipUnless(HAVE_GENE, "gene-archive is not installed")
class SiteFolder(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = dict(os.environ)
        if not shutil.which("gene"):
            os.environ["GENE_CMD"] = f"{sys.executable} -m gene_archive.cli"
        os.environ["GENE_AUTHOR"] = "Tester"
        os.environ["GENEALOGY_MCP_HOME"] = str(Path(self.tmp.name) / "home")
        os.environ["GENEALOGY_MCP_SITE_BUILD"] = "0"
        self.site = Path(self.tmp.name) / "site"
        subprocess.run(project.gene_command() + ["init", str(self.site), "--lang", "en"], check=True, capture_output=True)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.env)
        self.tmp.cleanup()

    def tree(self):
        return json.loads((self.site / "family_tree.json").read_text(encoding="utf-8"))

    def test_bridge(self):
        site = str(self.site)
        self.assertTrue(project.is_site(site))
        self.assertFalse(project.is_site("Kolodin"))
        self.assertEqual(project.view(site)["kind"], "gene-archive site")
        r = project.upsert(site, "source", {"title": "Baptisms 1885", "locator": "Archive, fond 1, opis 1, delo 1, folio 2"},
                           dry_run=True)
        self.assertTrue(r["dry_run"])
        self.assertEqual(self.tree()["sources"], [])
        project.upsert(site, "source", {"title": "Baptisms 1885", "locator": "Archive, fond 1, opis 1, delo 1, folio 2"})
        r = project.upsert(site, "person", {"given_names": "Peter", "surname": "Kolodin", "sex": "M",
                                            "birth": {"date": "about 1855", "place": "Synkovo"}},
                           reason="from his son's baptism", source_ids=["S1"])
        pid = r["id"]
        p = next(x for x in self.tree()["people"] if x["id"] == pid)
        self.assertEqual(p["birth"], {"date": "ABT 1855", "place_as_recorded": "Synkovo"})
        self.assertEqual(p["source_ids"], ["S1"])
        project.upsert(site, "person", {"id": pid, "birth": {"date": "9.10.1855"}}, reason="the record itself")
        p = next(x for x in self.tree()["people"] if x["id"] == pid)
        self.assertEqual(p["birth"]["place_as_recorded"], "Synkovo")   # merged, not replaced
        with self.assertRaises(ValueError):
            project.upsert(site, "family", {"partners": ["I999"]})
        project.log(site, "FamilySearch: Kolodin 1850-1860", "nothing")
        self.assertEqual(self.tree()["research_log"][-1]["result"], "nothing")
        authors = subprocess.run(["git", "log", "--format=%an"], cwd=self.site, capture_output=True, text=True).stdout.split()
        self.assertGreaterEqual(authors.count("Tester"), 4)
        self.assertEqual(project.view(site, "record", pid)["sources"][0]["id"], "S1")
        out = project.export(site)
        self.assertTrue(Path(out["file"]).is_file())
        self.assertNotEqual(Path(out["file"]).parent, self.site)   # nothing written into the site folder
        with self.assertRaises(ValueError):
            project.import_gedcom(site, "0 HEAD\n0 TRLR\n")

    def test_policy_and_structured_checks_use_site_log(self):
        site = str(self.site)
        project.configure(site, {'allow_archive_requests': False})
        r = project.upsert(site, 'lead', {'title': 'Question', 'next': 'Read certificate',
                                        'status': 'active', 'expected_sources': ['familysearch']})['saved']
        project.log(site, 'FamilySearch search', 'No matching record', lead_id=r['id'],
                    source_id='familysearch', outcome='checked')
        ctx = project.view(site, 'workflow')
        self.assertFalse(ctx['policy']['allow_archive_requests'])
        self.assertEqual(ctx['source_checks'][-1]['source_id'], 'familysearch')
        project.upsert(site, 'lead', {'id': r['id'], 'stage': 'civil_registry',
                                     'checked': '2026-10-21', 'stage_result': 'family documents examined'})

    def test_listed_from_env(self):
        os.environ["GENEALOGY_MCP_SITES"] = str(self.site)
        self.assertIn(str(self.site.resolve()), project.list_projects())


if __name__ == "__main__":
    unittest.main()


class GeneCommand(unittest.TestCase):
    """`gene` is found next to this Python when the virtualenv is not activated (PATH lacks its bin)."""

    def test_next_to_python(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            gene = Path(tmp) / "gene"
            gene.write_text("")
            with mock.patch.dict(os.environ, {"PATH": "/nonexistent"}):
                os.environ.pop("GENE_CMD", None)
                with mock.patch.object(project.sys, "executable", str(Path(tmp) / "python")):
                    self.assertEqual(project.gene_command(), [str(gene)])
                    gene.unlink()
                    with self.assertRaises(ValueError):
                        project.gene_command()
