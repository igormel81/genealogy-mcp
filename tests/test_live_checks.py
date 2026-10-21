import io
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

from genealogy_mcp import online


class LiveChecks(unittest.TestCase):
    def run_check(self, source, result):
        def search(sid, **kw):
            return result if sid == source else {"count": 1, "results": [{"title": "test hit"}]}
        output = io.StringIO()
        with patch.object(online, "search", side_effect=search), \
             patch.object(online, "place_history", return_value={"places": [{"name": "test place"}]}), \
             patch("sys.stdout", output), self.assertRaises(SystemExit) as stopped:
            runpy.run_path(str(Path(__file__).parent / "live" / "check_online.py"), run_name="__main__")
        return stopped.exception.code, output.getvalue()

    def test_network_errors_have_a_machine_readable_kind(self):
        with patch.object(online, "_get", side_effect=TimeoutError("timed out")):
            result = online.search("chronicling_america", surname="Lincoln")
        self.assertEqual(result.get("error_kind"), "network")

    def test_runner_restricted_source_timeout_is_reported_as_a_warning(self):
        status, output = self.run_check("chronicling_america", {"error": "the site did not answer: timed out", "error_kind": "network"})
        self.assertEqual(status, 0)
        self.assertIn("SKIP chronicling_america", output)
        self.assertIn("::warning::", output)

    def test_other_sources_still_fail_on_a_network_error(self):
        status, output = self.run_check("internet_archive", {"error": "timed out", "error_kind": "network"})
        self.assertEqual(status, 1)
        self.assertIn("FAIL internet_archive", output)

    def test_bad_and_empty_responses_from_restricted_sources_still_fail(self):
        for result in ({"error": "response format changed"}, {"count": 0, "results": []}):
            with self.subTest(result=result):
                status, output = self.run_check("chronicling_america", result)
                self.assertEqual(status, 1)
                self.assertIn("FAIL chronicling_america", output)
