import socket
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from genealogy_mcp import online, sources
from tools import check_links


def response(body=b'{}', status=200):
    result = MagicMock()
    result.__enter__.return_value = result
    result.read.return_value = body
    result.status = status
    return result


def http_error(code):
    return urllib.error.HTTPError('https://example.org/', code, 'test', {}, None)


class SourceLinks(unittest.TestCase):
    def test_rodovid_uses_the_existing_domain_without_changing_its_id(self):
        source = next(s for s in sources.catalogue() if s['id'] == 'rodovod')
        self.assertEqual(source['url'], 'https://ru.rodovid.org')

    @patch('time.sleep')
    def test_confirms_a_dead_link_before_reporting_it(self, sleep):
        with patch.object(check_links.urllib.request, 'urlopen', side_effect=[http_error(404), response()]):
            self.assertEqual(check_links.check('https://example.org/'), ('ok', 200))
        sleep.assert_called_once()

    @patch('time.sleep')
    def test_a_persistent_missing_page_still_fails(self, sleep):
        with patch.object(check_links.urllib.request, 'urlopen', side_effect=http_error(404)) as get:
            self.assertEqual(check_links.check('https://example.org/'), ('dead', 404))
        self.assertEqual(get.call_count, 2)

    @patch('time.sleep')
    def test_a_persistent_dns_failure_still_fails(self, sleep):
        error = urllib.error.URLError(socket.gaierror(-2, 'Name not known'))
        with patch.object(check_links.urllib.request, 'urlopen', side_effect=error) as get:
            self.assertEqual(check_links.check('https://example.org/'), ('dead', 'dns'))
        self.assertEqual(get.call_count, 2)

    @patch('time.sleep')
    def test_bot_protection_remains_a_warning_without_repeated_requests(self, sleep):
        with patch.object(check_links.urllib.request, 'urlopen', side_effect=http_error(403)) as get:
            self.assertEqual(check_links.check('https://example.org/'), ('warn', 403))
        self.assertEqual(get.call_count, 1)
        sleep.assert_not_called()


class LiveQueries(unittest.TestCase):
    @patch('time.sleep')
    def test_recovers_from_one_timeout_without_changing_the_query(self, sleep):
        with patch.object(online.urllib.request, 'urlopen', side_effect=[TimeoutError('timed out'), response(b'{"results": []}')]) as get:
            self.assertEqual(online._get('https://example.org/', {'q': 'Lincoln'}), {'results': []})
        self.assertEqual(get.call_count, 2)
        self.assertEqual(get.call_args.args[0].full_url, 'https://example.org/?q=Lincoln')
        sleep.assert_called_once()

    @patch('time.sleep')
    def test_temporary_server_failure_is_retried(self, sleep):
        with patch.object(online.urllib.request, 'urlopen', side_effect=[http_error(503), response()]):
            self.assertEqual(online._get('https://example.org/'), {})

    @patch('time.sleep')
    def test_persistent_timeouts_are_not_hidden(self, sleep):
        with patch.object(online.urllib.request, 'urlopen', side_effect=TimeoutError('timed out')) as get:
            with self.assertRaises(TimeoutError):
                online._get('https://example.org/')
        self.assertEqual(get.call_count, 2)

    @patch('time.sleep')
    def test_missing_api_endpoint_is_not_retried(self, sleep):
        with patch.object(online.urllib.request, 'urlopen', side_effect=http_error(404)) as get:
            with self.assertRaises(urllib.error.HTTPError):
                online._get('https://example.org/')
        self.assertEqual(get.call_count, 1)
        sleep.assert_not_called()

    @patch('time.sleep')
    def test_invalid_response_is_not_retried(self, sleep):
        with patch.object(online.urllib.request, 'urlopen', return_value=response(b'not JSON')) as get:
            with self.assertRaises(ValueError):
                online._get('https://example.org/')
        self.assertEqual(get.call_count, 1)
        sleep.assert_not_called()
