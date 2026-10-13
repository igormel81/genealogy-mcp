"""A GEDCOM file as the project: read it, change it in place, lose nothing else."""
import json
import os
import tempfile
import unittest
from pathlib import Path

from genealogy_mcp import gedfile
from genealogy_mcp import project as proj

TREE = """0 HEAD
1 SOUR MYHERITAGE
2 NAME MyHeritage Family Tree Builder
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
1 _PROJECT_GUID ABC
0 @I1@ INDI
1 NAME Иван Петрович /Мельников/
2 GIVN Иван Петрович
2 SURN Мельников
1 SEX M
1 BIRT
2 DATE ABT 1880
2 PLAC Сынково, Тульская губерния
1 OBJE
2 FILE photos/ivan.jpg
1 _UID 1234
1 NOTE Длинная заметка, первая часть
2 CONC  и продолжение
2 CONT вторая строка
1 FAMS @F1@
1 CHAN
2 DATE 1 JAN 2020
0 @I2@ INDI
1 NAME Мария /Иванова/
1 SEX F
1 FAMS @F1@
0 @I3@ INDI
1 NAME Пётр /Мельников/
1 SEX M
1 BIRT Y
1 FAMC @F1@
1 ASSO @I2@
2 RELA Godmother
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
2 _FREL Natural
1 MARR
2 DATE 1905
0 @S1@ SOUR
1 TITL Метрическая книга
0 @N1@ NOTE Общая заметка
0 TRLR"""


class GedcomProject(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = dict(os.environ)
        os.environ["GENEALOGY_MCP_HOME"] = str(Path(self.tmp.name) / "home")
        self.path = Path(self.tmp.name) / "tree.ged"
        self.raw = ("﻿" + TREE.replace("\n", "\r\n") + "\r\n").encode("utf-8")
        self.path.write_bytes(self.raw)
        self.p = str(self.path)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.env)
        self.tmp.cleanup()

    def text(self):
        return self.path.read_bytes().decode("utf-8-sig").replace("\r\n", "\n")

    def test_lossless(self):
        self.assertEqual(gedfile.GedFile(self.path).text().encode("utf-8"), self.raw)
        proj.log(self.p, "FamilySearch, Synkovo", "nothing")   # the log goes next to the file, the file stays
        self.assertEqual(self.path.read_bytes(), self.raw)
        self.assertFalse(Path(self.p + ".bak").exists())

    def test_read(self):
        v = proj.view(self.p)
        self.assertEqual(v["kind"], "GEDCOM file")
        self.assertEqual(v["people"], 3)
        rec = proj.view(self.p, "record", "I1")["record"]
        self.assertEqual((rec["given_names"], rec["surname"]), ("Иван Петрович", "Мельников"))
        self.assertEqual(rec["birth"], {"date": "ABT 1880", "place_as_recorded": "Сынково, Тульская губерния"})
        self.assertEqual(rec["notes"], "Длинная заметка, первая часть и продолжение\nвторая строка")
        self.assertEqual(proj.view(self.p, "record", "F1")["record"]["children"], ["I3"])
        self.assertTrue(proj.view(self.p, "search", query="сынково")["hits"])

    def test_dry_run_shows_lines_and_writes_nothing(self):
        r = proj.upsert(self.p, "person", {"id": "I3", "birth": {"date": "1906-03-15", "place": "Сынково"}}, dry_run=True)
        self.assertIn("+2 DATE 15 MAR 1906", r["gedcom_changes"])
        self.assertIn("-1 BIRT Y", r["gedcom_changes"])
        self.assertEqual(self.path.read_bytes(), self.raw)
        self.assertFalse(gedfile.sidecar(self.path).exists())

    def test_change_keeps_everything_else(self):
        s = proj.upsert(self.p, "source", {"title": "ЦГА Москвы, ф. 203, оп. 745, д. 12", "locator": "л. 5 об."})["saved"]["id"]
        self.assertEqual(s, "S2")
        proj.upsert(self.p, "person", {"id": "I3", "birth": {"date": "1906-03-15", "place": "Сынково"}},
                    reason="метрика", source_ids=[s])
        t = self.text()
        self.assertIn("1 NAME Пётр /Мельников/\n1 SEX M\n1 BIRT\n2 DATE 15 MAR 1906\n2 PLAC Сынково\n1 FAMC @F1@", t)
        self.assertIn("1 SOUR @S2@", t)
        for kept in ("1 _UID 1234", "2 FILE photos/ivan.jpg", "2 CONC  и продолжение", "2 _FREL Natural", "1 _PROJECT_GUID ABC",
                     "0 @N1@ NOTE Общая заметка", "2 RELA Godmother"):
            self.assertIn(kept, t)
        b = self.path.read_bytes()
        self.assertTrue(b.startswith(b"\xef\xbb\xbf") and b"\r\n" in b and b"\n" not in b.replace(b"\r\n", b""))
        self.assertEqual(gedfile.original_copy(self.path).read_bytes(), self.raw)
        self.assertTrue(Path(self.p + ".bak").exists())
        side = json.loads(gedfile.sidecar(self.path).read_text(encoding="utf-8"))
        self.assertEqual({c["field"] for c in side["corrections"] if c.get("person_id") == "I3"},
                         {"birth.date", "birth.place_as_recorded", "source_ids"})
        self.assertEqual(proj.view(self.p, "record", "I3")["record"]["source_ids"], ["S2"])

    def test_new_person_into_family_and_rename(self):
        r = proj.upsert(self.p, "person", {"given_names": "Анна", "surname": "Мельникова", "sex": "F", "birth": "1908",
                                           "research_status": "probable"})
        new = r["saved"]["id"]
        self.assertNotIn(new, ("I1", "I2", "I3", "N1"))
        self.assertIn("research_status", r["warnings"][0])
        proj.upsert(self.p, "family", {"id": "F1", "children": ["I3", new]})
        t = self.text()
        self.assertIn(f"2 _FREL Natural\n1 CHIL @{new}@", t)
        self.assertIn(f"0 @{new}@ INDI\n1 NAME Анна /Мельникова/\n1 SEX F\n1 BIRT\n2 DATE 1908\n1 FAMC @F1@", t)
        self.assertTrue(t.rstrip().endswith("0 TRLR"))
        proj.upsert(self.p, "person", {"id": "I1", "surname": "Мельников-Сынковский"})
        t = self.text()
        self.assertIn("1 NAME Иван Петрович /Мельников-Сынковский/\n2 GIVN Иван Петрович\n2 SURN Мельников-Сынковский", t)
        proj.upsert(self.p, "person", {"id": "I1", "notes": "Новая заметка"})
        self.assertIn("1 NOTE Новая заметка\n1 FAMS @F1@", self.text())

    def test_delete_removes_links(self):
        proj.upsert(self.p, "person", {"id": "I2"}, delete=True)
        t = self.text()
        self.assertNotIn("@I2@", t)
        self.assertIn("1 HUSB @I1@\n1 CHIL @I3@", t)
        self.assertEqual(proj.view(self.p, "record", "F1")["record"]["partners"], ["I1"])

    def test_long_note_is_split(self):
        long = "слово " * 80 + "\nвторая"
        proj.upsert(self.p, "person", {"id": "I2", "notes": long})
        self.assertTrue(all(len(x) < 255 for x in self.text().splitlines()))
        self.assertEqual(proj.view(self.p, "record", "I2")["record"]["notes"], long)

    def test_not_utf8_is_read_only(self):
        self.path.write_bytes(TREE.replace("1 CHAR UTF-8", "1 CHAR ANSI").encode("cp1251"))
        v = proj.view(self.p)
        self.assertIn("ANSI", v["read_only"])
        with self.assertRaises(ValueError):
            proj.upsert(self.p, "person", {"id": "I2", "sex": "M"})
        proj.log(self.p, "searched", "nothing")   # the log still works

    def test_export_and_import_refused(self):
        with self.assertRaises(ValueError):
            proj.export(self.p)
        with self.assertRaises(ValueError):
            proj.import_gedcom(self.p, self.p)

    def test_listed_from_env(self):
        os.environ["GENEALOGY_MCP_SITES"] = self.p
        self.assertIn(str(self.path.resolve()), proj.list_projects())

    def test_dates(self):
        self.assertEqual(gedfile.ged_date("1899-10-09"), "9 OCT 1899")
        self.assertEqual(gedfile.ged_date("ABT 1899-10"), "ABT OCT 1899")
        self.assertEqual(gedfile.ged_date("BET 1900 AND 1905"), "BET 1900 AND 1905")
        self.assertEqual(gedfile.ged_date("9 OCT 1899"), "9 OCT 1899")


if __name__ == "__main__":
    unittest.main()
