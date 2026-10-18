import asyncio
import unittest

from genealogy_mcp import estimate
from genealogy_mcp.server import server


class EstimateBirthYear(unittest.TestCase):
    def test_from_relatives(self):
        r = estimate.estimate("M", eldest_child="1870", spouse="1845")
        self.assertEqual(r["gedcom"], "BET 1837 AND 1852")
        self.assertEqual(r["most_likely"], 1843)
        self.assertIn("eldest child", r["explanation"])
        r = estimate.estimate(father="1820", siblings=["1848", "1852"], eldest_child="1875")
        self.assertEqual(r["range"], [1844, 1856])
        ru = estimate.estimate("F", eldest_child="1870", lang="ru")
        self.assertTrue(ru["explanation"].startswith("Оценка по году рождения старшего ребёнка"))
        self.assertEqual(ru["gedcom"], "ABT 1843")   # one wide clue: about, not a 27-year range

    def test_namesakes(self):
        # 7 years old in the revision of 1850, 22 at the marriage of 1882: not one person
        r = estimate.estimate(ages=[{"age": 7, "date": "1850", "source": "revision list"}, {"age": 22, "date": "1882-10-01", "source": "marriage"}])
        self.assertEqual(r["age_conflicts"][0]["level"], "two_people_likely")
        self.assertEqual(r["age_conflicts"][0]["difference"], 17)
        self.assertIn("conflict", r)
        ok = estimate.estimate(ages=[{"age": 45, "date": "1897"}, {"age": 50, "date": "1900"}])
        self.assertNotIn("age_conflicts", ok)   # 3 years of drift is normal
        doubtful = estimate.check_ages([{"age": 30, "year": 1880}, {"age": 30, "year": 1888}])[1]
        self.assertEqual(doubtful[0]["level"], "doubtful")

    def test_tool(self):
        r = asyncio.run(server.call_tool("estimate_birth_year", {"mother_birth": "1850", "lang": "ru"})).structured_content
        self.assertEqual(r["range"], [1868, 1895])
        err = asyncio.run(server.call_tool("estimate_birth_year", {})).structured_content
        self.assertIn("error", err)


if __name__ == "__main__":
    unittest.main()
