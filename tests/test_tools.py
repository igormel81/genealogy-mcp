import asyncio
import json
import re
import unittest
from pathlib import Path

from genealogy_mcp import audit, dates, evidence, guides, kinship, letters, names, plan, sources

GED = Path(__file__).parent / "sample.ged"


class Sources(unittest.TestCase):
    def test_catalogue(self):
        cat = sources.catalogue()
        self.assertGreaterEqual(len(cat), 79)
        ids = [s["id"] for s in cat]
        self.assertEqual(len(ids), len(set(ids)))
        for s in cat:
            for k in ("name", "url", "countries", "years", "records", "access", "about", "about_ru", "how", "how_ru"):
                self.assertIn(k, s, s["id"])
            self.assertTrue(s["url"] == "" or s["url"].startswith(("https://", "http://")), s["id"])
            self.assertIn(s["access"], sources.ACCESS, s["id"])
            self.assertLessEqual(s["years"][0], s["years"][1], s["id"])
            for r in s["records"]:
                self.assertIn(r, sources.RECORD_KINDS, s["id"])
            for c in s["countries"]:
                self.assertTrue(c == "*" or re.fullmatch(r"[A-Z]{2}", c), s["id"])
            if s.get("search"):
                self.assertTrue(set(re.findall(r"\{(\w+)\}", s["search"])) <= {"q", "given", "surname", "year_from", "year_to", "place"}, s["id"])

    def test_bessarabia_and_russia_sources(self):
        cat = {s["id"]: s for s in sources.catalogue()}
        for sid in ("nashipredki", "metricabook", "rodovod", "doroga_pamyati", "moypolk", "genealogica_ro",
                    "bessarabia_genealogy", "deportari_md", "cartea_memoriei_md", "dmitriev_1772"):
            self.assertIn(sid, cat)
        self.assertIn("numTypos=0&prefixSearch=false", cat["genealogica_ro"]["how"])
        self.assertIn("Codru", cat["dmitriev_1772"]["how"])
        self.assertIn("Фэлчиу", cat["dmitriev_1772"]["how_ru"])
        md = {s["id"] for s in sources.find("Moldova", 1772, 1774)}
        self.assertIn("dmitriev_1772", md)
        self.assertIn("deportari_md", {s["id"] for s in sources.find("Молдова", 1949, 1949, ["deportation"])})

    def test_regions(self):
        self.assertEqual(sources.countries("Украина"), {"UA"})
        self.assertIn("BR", sources.countries("Латинская Америка"))
        self.assertIn("IT", sources.countries("europe"))

    def test_find(self):
        ids = [s["id"] for s in sources.find("Argentina", 1890, 1920)]
        self.assertIn("cemla", ids)
        self.assertIn("familysearch", ids)
        self.assertNotIn("pamyat_naroda", ids)
        first = sources.find("Italy")[0]
        self.assertIn("IT", first["countries"])
        self.assertTrue(all("military" in s["records"] for s in sources.find("RU", records=["military"])))

    def test_link(self):
        fs = next(s for s in sources.catalogue() if s["id"] == "familysearch")
        url = sources.link(fs, given="Ivan", surname="Kolodin")
        self.assertIn("q.surname=Kolodin", url)
        self.assertNotIn("birthLikeDate", url)


class Dates(unittest.TestCase):
    def test_normalize(self):
        cases = {"около 1899": "ABT 1899", "между 1900 и 1905": "BET 1900 AND 1905", "9.10.1899": "1899-10-09",
                 "9 октября 1899 г.": "9 OCT 1899", "9 de octubre de 1899": "9 OCT 1899", "October 9, 1899": "9 OCT 1899",
                 "до 1950": "BEF 1950", "1900-1905": "BET 1900 AND 1905", "hacia 1890": "ABT 1890", "1899": "1899",
                 "около 9.10.1899": "ABT 9 OCT 1899", "31.02.1900": None, "непонятно": None}
        for text, want in cases.items():
            self.assertEqual(dates.normalize_date(text), want, text)

    def test_calendar(self):
        self.assertEqual(dates.convert_calendar("1918-02-01")["result"], "1918-02-14")
        self.assertEqual(dates.convert_calendar("14.02.1918", "julian")["result"], "1918-02-01")
        self.assertEqual(dates.convert_calendar("1799-12-25")["difference_days"], 11)
        self.assertEqual(dates.convert_calendar("1850-01-01")["result"], "1850-01-13")
        with self.assertRaises(ValueError):
            dates.convert_calendar("1899")

    def test_age(self):
        r = dates.birth_year_from_age(45, "1897-01-28")
        self.assertEqual(r["exact"], "BET 1851 AND 1852")


class Names(unittest.TestCase):
    def test_gendered(self):
        self.assertEqual(names.gendered("Колодин"), ["Колодина"])
        self.assertIn("Сынковский", names.gendered("Сынковская"))
        self.assertEqual(names.gendered("Толстой"), ["Толстая"])
        self.assertEqual(names.gendered("Kowalska"), ["Kowalski"])
        self.assertIn("Kazlauskienė", names.gendered("Kazlauskas"))
        self.assertEqual(names.gendered("Smith"), [])

    def test_translit(self):
        self.assertEqual(names.translit("Щукин", "passport"), "Shchukin")
        self.assertEqual(names.translit("Щукин", "german"), "Schtschukin")
        self.assertEqual(names.translit("Щукин", "polish"), "Szczukin")
        self.assertEqual(names.translit("Мельников", "romanian"), "Melnicov")
        self.assertEqual(names.translit("Евгений Яковлев", "bgn"), "Yevgeniy Yakovlev")

    def test_old_and_variants(self):
        self.assertEqual(names.old_orthography("Колодин"), "Колодинъ")
        self.assertEqual(names.old_orthography("Георгий"), "Георгій")
        v = names.variants("Колодин")
        self.assertIn("Калодин", v["spelling"])
        self.assertIn("Kolodin", v["latin"]["passport"])
        self.assertIn("Johann", names.given_equivalents("Иван"))
        self.assertIn("Juan", names.given_equivalents("John"))
        self.assertEqual(names.patronymic_forms("Петрович"), ["Петровна", "Петров", "Петров сын"])


class Kinship(unittest.TestCase):
    def test_names(self):
        self.assertEqual(kinship.describe(path="father brother son")["ru"], "двоюродный брат")
        self.assertEqual(kinship.describe(path="сын брата отца")["en"], "first cousin")
        self.assertEqual(kinship.describe(path="отец матери")["ru"], "дед")
        self.assertEqual(kinship.describe(3, 3, "M")["ru"], "троюродный брат")
        self.assertEqual(kinship.describe(3, 3, "M")["en"], "second cousin")
        self.assertEqual(kinship.describe(2, 4, "F")["en"], "first cousin twice removed")
        self.assertEqual(kinship.describe(3, 1, "M")["ru"], "двоюродный дед")
        self.assertEqual(kinship.describe(3, 1, "M")["en"], "great-uncle")
        self.assertEqual(kinship.describe(1, 3, "F")["ru"], "внучатая племянница")
        self.assertEqual(kinship.describe(4, 0, "F")["ru"], "прапрабабушка")
        self.assertEqual(kinship.describe(2, 2, "M")["dna_shared_percent_expected"], 12.5)
        self.assertEqual(kinship.describe(path="wife brother")["dna_shared_percent_expected"], 0.0)
        with self.assertRaises(ValueError):
            kinship.describe(path="son father")


class Evidence(unittest.TestCase):
    def test_verdicts(self):
        k = {"given": "Иван", "surname": "Колодин", "father_given": "Пётр", "birth_year": 1885, "spouse_given": "Анна"}
        f = {"given": "Іоаннъ", "surname": "Колодинъ", "father_given": "Петр", "birth_year": "ABT 1887", "spouse_given": "Ганна"}
        self.assertEqual(evidence.check_match(k, f)["verdict"], "confirmed")
        self.assertEqual(evidence.check_match({"given": "Ivan", "surname": "Kolodin"}, {"given": "Иван", "surname": "Колодин"})["verdict"], "insufficient")
        self.assertEqual(evidence.check_match({"surname": "Kolodin", "birth_year": 1885}, {"surname": "Колодина", "birth_year": 1886})["verdict"], "probable")
        self.assertEqual(evidence.check_match({"surname": "Kolodin", "father_given": "Peter"}, {"surname": "Колодин", "father_given": "Николай"})["verdict"], "conflict")
        self.assertEqual(evidence.check_match({"surname": "Kolodin"}, {"surname": "Smirnov"})["verdict"], "different_person")


class Audit(unittest.TestCase):
    def test_gedcom(self):
        r = audit.report(str(GED))
        c = r["counts"]
        self.assertEqual((r["people"], r["families"], r["sources"]), (5, 1, 1))
        for code in ("death_before_birth", "born_after_mother_death", "parent_young", "possible_duplicate", "unconnected", "no_sex"):
            self.assertIn(code, c, code)
        self.assertEqual(r["items"][0]["id"], "I1")
        self.assertIn("рождения", audit.report(GED.read_text(encoding="utf-8"), "ru")["items"][0]["text"])

    def test_paths(self):
        with self.assertRaises(ValueError):
            audit.report(str(GED), allow_paths=False)
        with self.assertRaises(ValueError):
            audit.report(__file__)
        self.assertEqual(audit.report(GED.read_text(encoding="utf-8"), allow_paths=False)["people"], 5)

    def test_json(self):
        data = {"people": [{"id": "I1", "display_name": "A", "sex": "M", "birth": {"date": "1900", "source_ids": ["S1"]}}],
                "families": [], "sources": [{"id": "S1"}]}
        r = audit.report(json.dumps(data))
        self.assertEqual(r["counts"], {})


class Texts(unittest.TestCase):
    def test_letters(self):
        for kind in letters.KINDS:
            d = letters.draft(kind, person="Колодин Иван Петрович")
            self.assertIn("Колодин Иван Петрович", d["body"])
            self.assertIn("[", d["body"])
        self.assertIn("ЦАМО", letters.draft("military")["body"])

    def test_guides_plan(self):
        for k in guides.GUIDES:
            self.assertTrue(guides.guide(k, "en").startswith("# "))
            self.assertTrue(guides.guide(k, "ru").startswith("# "))
        self.assertIn("шурин", guides.glossary("брат жены", "ru") or guides.glossary("шурин", "ru"))
        p = plan.plan("Россия", 1850, 1945, lang="ru")
        self.assertIn("metric_book", p["guides"])
        self.assertIn(p["sources"][0]["id"], {s["id"] for s in sources.find("RU", include_worldwide=False)})
        p = plan.plan("Brazil", 1880, 1950)
        self.assertIn("latin_america", p["guides"])
        self.assertNotIn("metric_book", p["guides"])


class Server(unittest.TestCase):
    def test_server(self):
        from genealogy_mcp.server import server

        async def go():
            tools = {t.name for t in await server.list_tools()}
            self.assertGreaterEqual(len(tools), 14)
            r = await server.call_tool("kinship", {"path": "father brother son"})
            self.assertEqual(r.structured_content["ru"], "двоюродный брат")
            r = await server.call_tool("search_links", {"surname": "Колодин", "given": "Иван", "country": "RU"})
            urls = [x["url"] for x in r.structured_content["links"]]
            self.assertTrue(any("q.surname=Kolodin" in u for u in urls))
            r = await server.call_tool("find_sources", {"country": "latin_america", "lang": "ru"})
            self.assertGreater(r.structured_content["count"], 5)
            r = await server.call_tool("audit_tree", {"file": str(GED)})
            self.assertIn("counts", r.structured_content)
            templates = {t.uri_template for t in await server.list_resource_templates()}
            self.assertIn("genealogy://guide/research/{lang}", templates)
            prompts = {p.name for p in await server.list_prompts()}
            self.assertIn("start_research", prompts)
        asyncio.run(go())


if __name__ == "__main__":
    unittest.main()
