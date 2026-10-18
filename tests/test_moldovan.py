import asyncio
import unittest

from genealogy_mcp import evidence, moldovan, names
from genealogy_mcp.server import server


class MoldovanSurnames(unittest.TestCase):
    def test_romanian_to_russian(self):
        v = moldovan.variants("Călugăreanu")
        for f in ("Калугаряну", "Калугарян", "Калугоряну"):
            self.assertIn(f, v["russian"])
        self.assertEqual(v["soviet_moldavian"], "Кэлугэряну")
        self.assertIn("Калгаран", v["clerk_contractions"])
        self.assertIn("Călugărean", v["romanian"])
        self.assertIn("Calugareanu", v["romanian"])

    def test_russian_to_romanian(self):
        v = moldovan.variants("Калугарян")
        self.assertIn("Călugăreanu", v["romanian"])
        self.assertIn("Калугамян", v["ocr_hints"])   # what a recognised war database once gave
        self.assertNotIn("Калугамян", names.all_forms("Калугарян"))   # hints are not search-equal forms
        p = moldovan.variants("Плеш")
        self.assertIn("Pleș", p["romanian"])
        self.assertIn("Pleșu", p["romanian"])
        self.assertIn("Плешъ", p["russian"])
        self.assertIn("Плешу", p["russian"])
        self.assertIn("Попеско", moldovan.variants("Плеско")["false_friends"])

    def test_alias(self):
        self.assertEqual(moldovan.split_alias("Мокану, он же Плеш"), ["Мокану", "Плеш"])
        self.assertEqual(moldovan.split_alias("Mocanu zis Pleș"), ["Mocanu", "Pleș"])
        v = names.variants("Мокану, он же Плеш")
        self.assertEqual(v["moldovan"]["alias"]["flag"], "possible second surname")
        forms = names.all_forms("Мокану, он же Плеш")
        self.assertIn("Mocanu", forms)
        self.assertIn("Pleș", forms)

    def test_not_moldovan(self):
        self.assertNotIn("moldovan", names.variants("Колодин"))
        self.assertNotIn("moldovan", names.variants("Kowalski"))
        self.assertIn("moldovan", names.variants("Плеш", origin="moldovan"))

    def test_check_match_across_alphabets(self):
        r = evidence.check_match({"surname": "Călugăreanu", "father_given": "Vasile", "birth_year": 1880},
                                 {"surname": "Калугарян", "father_given": "Василий", "birth_year": 1881})
        self.assertEqual(r["verdict"], "confirmed")

    def test_tool(self):
        r = asyncio.run(server.call_tool("name_variants", {"name": "Калугарян"})).structured_content
        self.assertIn("Călugăreanu", r["all_forms"])
        self.assertIn("warning", r["moldovan"])
        links = asyncio.run(server.call_tool("search_links", {"surname": "Калугарян"})).structured_content
        self.assertTrue(any(f.startswith("Calugarean") for f in links["name_forms"]))


if __name__ == "__main__":
    unittest.main()
