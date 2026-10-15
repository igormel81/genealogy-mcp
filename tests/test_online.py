import unittest
from unittest.mock import patch

from genealogy_mcp import online


class OpenList(unittest.TestCase):
    def test_live_opensearch_format(self):
        title = "Мельников Абрам Григорьевич (1874)"
        url = "https://ru.openlist.wiki/%D0%9C%D0%B5%D0%BB%D1%8C%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2_%D0%90%D0%B1%D1%80%D0%B0%D0%BC_%D0%93%D1%80%D0%B8%D0%B3%D0%BE%D1%80%D1%8C%D0%B5%D0%B2%D0%B8%D1%87_(1874)"
        with patch.object(online, "_get", return_value=["Мельников Абрам", [title], [""], [url]]) as get:
            result = online.search("open_list", surname="Мельников", given="Абрам")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["results"], [{"title": title, "url": url, "snippet": ""}])
        self.assertIn("prefix", result["note"])
        self.assertEqual(get.call_args.args, ("https://ru.openlist.wiki/api.php", {
            "action": "opensearch", "search": "Мельников Абрам", "limit": 15, "format": "json",
        }))

    def test_query_and_limit(self):
        response = ["Мельников", ["First", "Second"], ["Description", ""], ["https://example.com/1", "https://example.com/2"]]
        with patch.object(online, "_get", return_value=response) as get:
            result = online.open_list(surname="ignored", query="Мельников", limit=1)
        self.assertEqual(get.call_args.args[1]["search"], "Мельников")
        self.assertEqual(get.call_args.args[1]["limit"], 1)
        self.assertEqual(result, [{"title": "First", "url": "https://example.com/1", "snippet": "Description"}])

    def test_empty_search_is_not_an_error(self):
        with patch.object(online, "_get", return_value=["NoSuchName", [], [], []]):
            result = online.search("open_list", query="NoSuchName")
        self.assertEqual(result["count"], 0)
        self.assertNotIn("error", result)

    def test_api_error_is_not_empty_search(self):
        response = {"error": {"code": "search-text-disabled", "info": '"text" search is disabled.'}}
        with patch.object(online, "_get", return_value=response):
            result = online.search("open_list", surname="Мельников")
        self.assertIn("search-text-disabled", result["error"])
        self.assertNotIn("count", result)

    def test_malformed_response_is_not_empty_search(self):
        for response in ({}, ["query", ["title"], [], ["url"]], ["query", {}, [], []]):
            with self.subTest(response=response), patch.object(online, "_get", return_value=response):
                result = online.search("open_list", query="query")
            self.assertIn("error", result)
            self.assertNotIn("count", result)


class PlaceHistory(unittest.TestCase):
    def test_village_with_region_falls_back_to_village_and_picks_namesake(self):
        def fake_get(url, params=None, data=None):
            if params.get("action") == "wbsearchentities":
                return {"search": [] if " " in params["search"] else [{"id": "Q1"}, {"id": "Q2"}]}
            return {}
        ents = {"Q1": {"labels": {"ru": {"value": "Сынково"}}, "descriptions": {"ru": {"value": "деревня во Владимирской области"}}},
                "Q2": {"labels": {"ru": {"value": "Сынково"}}, "descriptions": {"ru": {"value": "деревня в Тульской области"}}}}
        with patch.object(online, "_get", side_effect=fake_get), \
             patch.object(online, "_wd_entities", side_effect=lambda ids, lang: {i: ents[i] for i in ids if i in ents}):
            result = online.place_history("Сынково Тульская область")
        self.assertEqual([p["wikidata"].rsplit("/", 1)[1] for p in result["places"]], ["Q2"])

    def test_exact_hit_is_not_filtered(self):
        with patch.object(online, "_get", return_value={"search": [{"id": "Q9"}]}), \
             patch.object(online, "_wd_entities", return_value={"Q9": {"labels": {"ru": {"value": "Тула"}}}}):
            result = online.place_history("Тула")
        self.assertEqual(len(result["places"]), 1)
