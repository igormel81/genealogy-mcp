import asyncio
import unittest

from genealogy_mcp import places
from genealogy_mcp.server import server


def call(name, args):
    return asyncio.run(server.call_tool(name, args)).structured_content


class SouthernBessarabia(unittest.TestCase):
    def test_districts(self):
        for text, key in (("Болград", "bolgrad"), ("Измаильский уезд", "ismail"), ("Ізмаїльський район", "ismail"),
                          ("Reni", "ismail"), ("Cahul", "cahul"), ("Кагульский уезд", "cahul")):
            self.assertEqual(places.south_district(text), key, text)
        for text in ("Кишинёв", "Orhei", "children"):
            self.assertIsNone(places.south_district(text), text)

    def test_years(self):
        self.assertEqual(places.bessarabia_in(1850, "cahul")["state"], "Russian Empire")
        moldavian = places.bessarabia_in(1865, "ismail")
        self.assertIn("Moldavia", moldavian["state"])
        self.assertTrue(any("Galați" in a for a in moldavian["archives"]))
        self.assertIn("Treaty of Berlin", moldavian["note"])
        self.assertIn("border year", places.bessarabia_in(1878, "bolgrad")["border_year"])
        self.assertIn("Izmail uezd", places.bessarabia_in(1890, "cahul")["unit"])
        self.assertEqual(places.bessarabia_in(1925, "bolgrad")["state"], "Romania")
        self.assertEqual(places.bessarabia_in(1943, "cahul")["state"], "Romania")
        self.assertIn("USSR", places.bessarabia_in(1940, "ismail")["state"])
        self.assertIn("Izmail oblast", places.bessarabia_in(1950, "ismail")["unit"])
        # the rest of Bessarabia stayed Russian in 1857–1878
        self.assertEqual(places.bessarabia_in(1865)["state"], "Russian Empire")
        self.assertEqual(places.bessarabia_in(1930)["state"], "Romania")
        # today: Cahul in Moldova, Izmail and Bolgrad in Ukraine
        self.assertIn("Moldova", places.bessarabia_in(1900, "cahul")["now"])
        self.assertIn("Ukraine", places.bessarabia_in(1900, "bolgrad")["now"])

    def test_where_are_records(self):
        r = call("where_are_records", {"place": "Bolgrad", "year": 1870})
        m = r["matches"][0]
        self.assertEqual(m["province"], "Бессарабская губерния")
        self.assertIn("Moldavia", m["in_year"]["state"])
        self.assertTrue(any("Izmail" in a for a in m["in_year"]["archives"]))
        r = call("where_are_records", {"place": "Измаильский уезд"})
        self.assertTrue(any(p["state"].startswith("Principality of Moldavia") for p in r["matches"][0]["periods"]))
        self.assertEqual(call("where_are_records", {"place": "Volhynia", "year": 1870})["matches"][0].get("in_year"), None)


class Parish(unittest.TestCase):
    def test_attachment(self):
        self.assertEqual(places.parish_of("Porumbești")[0]["church_village"], "Leca")
        self.assertEqual(places.parish_of("с. Садык")[0]["church_village"], "Capaclia Nouă")
        self.assertEqual(places.parish_of("Сынково"), [])
        for e in places.PARISHES:   # never without a source
            self.assertTrue(e["source"])

    def test_tool(self):
        r = call("where_are_records", {"place": "Бессарабия", "village": "Sadâc", "lang": "ru"})
        self.assertEqual(r["parish"]["attached_to"][0]["church_village"], "Capaclia Nouă")
        self.assertTrue(any("клировые" in s.lower() for s in r["parish"]["how_to_find"]))
        r = call("where_are_records", {"place": "Тульская губерния", "village": "Сынково"})
        self.assertIsNone(r["parish"]["attached_to"])
        self.assertTrue(r["parish"]["how_to_find"])
        r = call("where_are_records", {"place": "Порумбешть", "village": "Порумбешть"})   # the village alone finds its province
        self.assertEqual(r["matches"][0]["province"], "Бессарабская губерния")



class PlaceHistoryParish(unittest.TestCase):
    def test_attachment_added(self):
        from unittest import mock
        from genealogy_mcp import online
        with mock.patch.object(online, "place_history", return_value={"query": "Porumbești", "places": []}):
            r = call("place_history", {"name": "Porumbești", "lang": "en"})
        self.assertEqual(r["parish_attachment"][0]["church_village"], "Leca")
        self.assertIn("where_are_records", r["parish_tip"])


if __name__ == "__main__":
    unittest.main()
