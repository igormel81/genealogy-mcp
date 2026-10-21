import os
import tempfile
import unittest
from pathlib import Path

from genealogy_mcp import audit, project

GED = Path(__file__).parent / "sample.ged"


class Project(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["GENEALOGY_MCP_HOME"] = self.tmp.name

    def tearDown(self):
        os.environ.pop("GENEALOGY_MCP_HOME", None)
        self.tmp.cleanup()

    def test_workflow(self):
        project.upsert("t", "source", {"title": "Метрическая книга 1885", "locator": "ГАТО ф. 1, оп. 1, д. 1, л. 2"})
        r = project.upsert("t", "person", {"given_names": "Иван", "surname": "Колодин", "sex": "М",
                                           "birth": {"date": "около 1885", "place": "Сынково"}}, source_ids=["S1"])
        self.assertEqual(r["saved"]["birth"], {"date": "ABT 1885", "place_as_recorded": "Сынково"})
        self.assertEqual(r["saved"]["sex"], "M")
        project.upsert("t", "person", {"given_names": "Пётр", "surname": "Колодин", "sex": "M"})
        project.upsert("t", "family", {"partners": ["I2"], "children": ["I1"]})
        project.upsert("t", "person", {"id": "I1", "birth": {"date": "9.10.1885"}}, reason="запись о крещении", source_ids=["S1"])
        rec = project.view("t", "record", "I1")
        self.assertEqual(rec["record"]["birth"], {"date": "1885-10-09", "place_as_recorded": "Сынково"})   # place kept
        self.assertEqual(rec["corrections"][0]["previous"], "ABT 1885")
        self.assertEqual(rec["as_child_in"][0]["id"], "F1")
        project.log("t", "FamilySearch: Колодин 1880–1890", "ничего")
        s = project.view("t", lang="ru")
        self.assertEqual((s["people"], s["families"], s["sources"]), (2, 1, 1))
        self.assertEqual(s["recent_log"][-1]["result"], "ничего")
        self.assertTrue(any("Пётр" in c["text"] for c in s["checks"]))
        self.assertTrue(any(x.get("result") == "запись о крещении" for x in project.view("t", "search", query="крещ")["hits"]))
        self.assertEqual(project.view("t", "search", query="Сынково")["hits"][0]["id"], "I1")
        with self.assertRaises(ValueError):
            project.upsert("t", "family", {"partners": ["I9"]})
        with self.assertRaises(ValueError):
            project.upsert("t", "person", {"given_names": "X"}, source_ids=["S7"])
        project.upsert("t", "person", {"id": "I2"}, delete=True)
        self.assertEqual(project.load("t")["families"][0]["partners"], [])

    def test_gedcom_round_trip(self):
        r = project.import_gedcom("imp", str(GED))
        self.assertEqual(r["people"], 5)
        out = project.export("imp")
        back = audit.parse_gedcom(Path(out["file"]).read_text(encoding="utf-8"))
        self.assertEqual(len(back["people"]), 5)
        self.assertEqual(back["families"][0]["children"], ["I3"])
        with self.assertRaises(ValueError):
            project.import_gedcom("imp", str(GED))

    def test_names_are_safe(self):
        for bad in ("../x", "/etc/passwd", ".hidden", "a/b"):
            with self.assertRaises(ValueError):
                project.load(bad)
        self.assertEqual(project.list_projects(), [])




if __name__ == "__main__":
    unittest.main()
