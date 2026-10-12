import unittest

from genealogy_mcp import calendars, dna, evidence, names, numerals, soundex


class DM(unittest.TestCase):
    def test_published_examples(self):
        # examples from the Daitch–Mokotoff description (Avotaynu / JewishGen)
        self.assertEqual(soundex.dm_soundex("Moskowitz"), ["645740"])
        self.assertEqual(soundex.dm_soundex("Moskovitz"), ["645740"])
        self.assertEqual(set(soundex.dm_soundex("Auerbach")), {"097500", "097400"})
        self.assertEqual(set(soundex.dm_soundex("Ohrbach")), {"097500", "097400"})
        self.assertEqual(soundex.dm_soundex("Lipshitz"), ["874400"])
        self.assertEqual(set(soundex.dm_soundex("Peters")), {"739400", "734000"})
        self.assertEqual(set(soundex.dm_soundex("Peterson")), {"739460", "734600"})
        self.assertEqual(set(soundex.dm_soundex("Jackson")), {"154600", "454600", "145460", "445460"})
        self.assertEqual(set(soundex.dm_soundex("Schwarzenegger")), {"474659", "479465"})

    def test_cyrillic(self):
        self.assertIn("686570", soundex.codes_for("Мельников"))
        self.assertEqual(soundex.dm_soundex("Kołodin"), soundex.dm_soundex("Kolodin"))


class Numerals(unittest.TestCase):
    def test_parse_format(self):
        self.assertEqual(numerals.parse("҂аѡ҃п"), 1880)
        self.assertEqual(numerals.parse("ѳі"), 19)
        self.assertEqual(numerals.parse("к҃г"), 23)
        self.assertIsNone(numerals.parse("щука"))
        for n in (1, 11, 16, 23, 100, 1763, 1880, 1917):
            self.assertEqual(numerals.parse(numerals.format(n)), n)
        self.assertEqual(numerals.format(16).replace("҃", ""), "ѕі")
        self.assertEqual(numerals.find_all("ѳі҃ октября ҂аѡ҃п года"), [("ѳі҃", 19), ("҂аѡ҃п", 1880)])


class Calendars(unittest.TestCase):
    def test_easter(self):
        self.assertEqual(calendars.julian_to_gregorian(*calendars.orthodox_easter(2024)), (2024, 5, 5))
        self.assertEqual(calendars.western_easter(2024), (2024, 3, 31))
        self.assertEqual(calendars.western_easter(2000), (2000, 4, 23))

    def test_feasts(self):
        r = calendars.feast_date("на Покров", 1885)
        self.assertEqual((r["julian"], r["gregorian"]), ("1885-10-01", "1885-10-13"))
        self.assertEqual(calendars.feast_date("после Петрова поста", 1890)["key"], "petrov_fast_start")
        self.assertEqual(calendars.feast_date("на Николу зимнего", 1900)["gregorian"], "1900-12-19")
        self.assertEqual(calendars.feast_date("Wielkanoc", 2024, "catholic")["gregorian"], "2024-03-31")
        self.assertIn("error", calendars.feast_date("день рождения", 1900))

    def test_hebrew(self):
        self.assertEqual(calendars.hebrew_to_gregorian("1 Tishrei 5785")["gregorian"], "2024-10-03")
        self.assertEqual(calendars.hebrew_to_gregorian("15 Nisan 5784")["gregorian"], "2024-04-23")
        self.assertEqual(calendars.hebrew_to_gregorian("14 Adar II 5784")["gregorian"], "2024-03-24")
        self.assertEqual(calendars.gregorian_to_hebrew("2019-09-30")["hebrew"], "1 Tishrei 5780")
        for rd in range(690000, 700000, 37):   # round trip over ~27 years
            y, m, d = calendars.hebrew_from_fixed(rd)
            self.assertEqual(calendars.fixed_from_hebrew(y, m, d), rd)

    def test_republican(self):
        self.assertEqual(calendars.republican_to_gregorian("18 Brumaire an VIII")["gregorian"], "1799-11-09")
        self.assertEqual(calendars.republican_to_gregorian("9 Thermidor an II")["gregorian"], "1794-07-27")
        self.assertEqual(calendars.gregorian_to_republican("1795-10-05")["republican"], "13 Vendémiaire an 4")
        with self.assertRaises(ValueError):
            calendars.gregorian_to_republican("1810-01-01")


class DNA(unittest.TestCase):
    def test_fits(self):
        keys = [f["key"] for f in dna.fits(870)["fits"]]
        self.assertIn("first_cousin", keys)
        self.assertNotIn("parent_child", keys)
        self.assertEqual(dna.fits(3500)["fits"][0]["key"], "parent_child")
        self.assertTrue(dna.fits(10)["note"])
        self.assertIn("троюродный", dna.fits(229, "ru")["fits"][0]["relationship"])


class Names(unittest.TestCase):
    def test_jewish_and_hispanic(self):
        self.assertIn("Моисей", names.given_equivalents("Мовша"))
        self.assertIn("Jacob", names.given_equivalents("Янкель"))
        r = evidence.check_match({"surname": "Pérez García", "given": "Juan"}, {"surname": "Pérez", "given": "Juan"})
        self.assertEqual(r["compared"][0]["result"], "match")
        self.assertEqual(evidence.check_match({"surname": "Pérez"}, {"surname": "Gómez"})["verdict"], "different_person")




class Places(unittest.TestCase):
    def test_find(self):
        from genealogy_mcp import places
        self.assertEqual([e["id"] for e in places.find("Тульская губерния")], ["tula"])
        self.assertEqual([e["id"] for e in places.find("Bessarabia")], ["bessarabia"])
        self.assertIn("chernigov", [e["id"] for e in places.find("Брянская область")])
        self.assertEqual(places.find("Атлантида"), [])
        ids = [e["id"] for e in places.P]
        self.assertEqual(len(ids), len(set(ids)))
        for e in places.P:
            self.assertTrue(e["archives"] and e["now"], e["id"])


if __name__ == "__main__":
    unittest.main()
