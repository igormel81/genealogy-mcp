"""Queries that previously omitted documented collections or suggested the wrong custodian."""
import unittest

from genealogy_mcp import places, sources


class ReferenceRouting(unittest.TestCase):
    def test_documented_years_are_searchable(self):
        for country, year, source_id in (
            ("PL", 1940, "jri_poland"),
            ("UA", 1941, "gesher_galicia"),
            ("EE", 2025, "bbld"),
            ("US", 1790, "stevemorse"),
            ("NZ", 2010, "paperspast"),
            ("AU", 1995, "trove"),
            ("AU", 1860, "naa"),
            ("DE", 1495, "bundesarchiv"),
            ("DE", 1490, "ddb"),
            ("KZ", 1720, "kazakhstan_archives"),
            ("KG", 2015, "kyrgyzstan_archives"),
        ):
            with self.subTest(source=source_id, year=year):
                ids = {s["id"] for s in sources.find(country, year, year)}
                self.assertIn(source_id, ids)

    def test_country_queries_and_record_custodians(self):
        self.assertIn("erivan", {p["id"] for p in places.find("AZ")})
        self.assertIn("transcaspian", {p["id"] for p in places.find("KZ")})
        self.assertNotIn("turkmenistan_archives", {
            s["id"] for s in sources.find("TM", records=["vital"], include_worldwide=False)
        })
        self.assertNotIn("naa", {
            s["id"] for s in sources.find("AU", 1901, 2000, records=["census"], include_worldwide=False)
        })
