import asyncio
import unittest

from genealogy_mcp import hypothesis
from genealogy_mcp.server import server

CHILD = {"given": "Иван", "surname": "Колодин", "patronymic": "Петрович", "birth_year": 1885, "place": "Сынково",
         "children_given": ["Пётр", "Мария"], "godparents": ["Анна Колодина"]}
CANDIDATES = [
    {"given": "Пётр", "surname": "Колодин", "birth_year": 1855, "place": "Сынково", "children": ["Иван", "Анна"]},
    {"given": "Петр", "surname": "Колодин", "birth_year": 1850, "place": "Кобылинка"},   # namesake, next village
    {"given": "Петр", "surname": "Колодин", "birth_year": 1800, "place": "Сынково"},     # too old
    {"given": "Павел", "surname": "Колодин", "birth_year": 1855, "place": "Сынково"},    # another name
]


class ParentHypothesis(unittest.TestCase):
    def test_father_names(self):
        cases = {"Петрович": "Петр", "Васильевич": "Василий", "Андреевич": "Андрей", "Ильич": "Илья", "Кузьминична": "Кузьма",
                 "Лукич": "Лука", "Сергеевна": "Сергей", "Ivanovich": "Ivan", "Петров сын": "Петр"}
        for p, want in cases.items():
            self.assertEqual(hypothesis.father_names(p)[0], want, p)

    def test_ranking(self):
        r = hypothesis.hypothesis(CHILD, CANDIDATES)
        self.assertEqual(r["status"], "hypothesis")
        levels = {(c["candidate"]["birth_year"], c["candidate"]["given"]): c["level"] for c in r["candidates"]}
        self.assertEqual(levels[(1855, "Пётр")], "strong")
        self.assertEqual(levels[(1850, "Петр")], "moderate")   # a namesake from another village is never strong
        self.assertEqual(levels[(1800, "Петр")], "against")
        self.assertEqual(levels[(1855, "Павел")], "against")
        namesake = next(c for c in r["candidates"] if c["candidate"]["place"] == "Кобылинка")
        self.assertTrue(any("another village" in w for w in namesake["warnings"]))
        best = r["candidates"][0]
        self.assertTrue(any("grandfather" in x for x in best["for"]))
        self.assertTrue(any("godparent" in x for x in best["for"]))
        self.assertIn("baptism", r["settle_with"][0])
        self.assertIn("not a link", r["rule"])
        self.assertEqual(r["lead"]["status"], "open")

    def test_equal_candidates_and_no_candidates(self):
        twins = [{"given": "Петр", "surname": "Колодин", "birth_year": 1855, "place": "Сынково"},
                 {"given": "Пётр", "surname": "Колодин", "birth_year": 1857, "place": "Сынково"}]
        self.assertTrue(hypothesis.hypothesis(CHILD, twins)["notes"])
        r = hypothesis.hypothesis({"patronymic": "Ильич"}, None, "ru")
        self.assertIn("Илья", r["find_candidates"])
        with self.assertRaises(ValueError):
            hypothesis.hypothesis({"given": "Иван"})

    def test_tool(self):
        r = asyncio.run(server.call_tool("parent_hypothesis", {"child": CHILD, "candidates": CANDIDATES[:2], "lang": "ru"})).structured_content
        self.assertEqual(r["status"], "hypothesis")
        self.assertIn("не связь", r["rule"])


if __name__ == "__main__":
    unittest.main()
