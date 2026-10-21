"""Contract fixtures model the documented BnF XML, with invented bibliographic text."""
import io
import unittest
import urllib.error
from unittest.mock import patch

from genealogy_mcp import books, online, server

SRU = b'''<s:searchRetrieveResponse xmlns:s="http://www.loc.gov/zing/srw/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<s:numberOfRecords>2</s:numberOfRecords><s:records><s:record><s:recordData><dc:dc>
<dc:title>Invented address directory</dc:title><dc:date>1885</dc:date>
<dc:identifier>http://gallica.bnf.fr/ark:/12148/bpt6k12345z</dc:identifier>
<dc:rights>Check provider conditions</dc:rights></dc:dc></s:recordData></s:record></s:records></s:searchRetrieveResponse>'''
PAGES = b'''<results countResults="12"><items><item><p_id>PAG_0000173</p_id>
<content>Invented &lt;span class="highlight"&gt;Example&lt;/span&gt; passage</content>
</item></items></results>'''


class Books(unittest.TestCase):
    def test_search_ocr_and_publication_years_with_pagination(self):
        with patch.object(books, '_xml', return_value=(SRU, '2026-10-21T00:00:00Z', False)) as fetch:
            result = online.search('gallica', surname='Example', year_from=1880, year_to=1900, limit=1)
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['total'], 2)
        self.assertEqual(result['next_start'], 2)
        self.assertEqual(result['results'][0]['document_id'], 'bpt6k12345z')
        self.assertEqual(result['results'][0]['match_scope'], 'document_ocr_index')
        self.assertIn('text all "Example" and dc.date >= "1880"', fetch.call_args.args[1]['query'])

    def test_search_tool_pagination_and_no_silent_unsupported_offset(self):
        with patch.object(books, '_xml', return_value=(SRU, '', False)) as fetch:
            result = server.search_online('gallica', query='Example', start=2, limit=1)
        self.assertEqual(fetch.call_args.args[1]['startRecord'], 2)
        self.assertIsNone(result['next_start'])
        self.assertIn('error', online.search('wikitree', surname='Example', start=2))
        self.assertIn('error', online.search('unknown', query='Example'))

    def test_page_link_preserves_scan_number_and_ocr_provenance(self):
        with patch.object(books, '_xml', return_value=(PAGES, '2026-10-21T00:00:00Z', False)):
            result = server.search_book_pages('https://gallica.bnf.fr/ark:/12148/bpt6k12345z', 'Example')
        self.assertEqual(result['next_start'], 1)
        row = result['results'][0]
        self.assertEqual(row['page_index'], 173)
        self.assertIsNone(row['printed_page'])
        self.assertEqual(row['url'], 'https://gallica.bnf.fr/ark:/12148/bpt6k12345z/f173.item')
        self.assertEqual(row['excerpt'], 'Invented Example passage')
        self.assertEqual(row['text_kind'], 'provider_ocr_excerpt')

    def test_empty_is_distinct_from_malformed_or_access_error(self):
        with patch.object(books, '_xml', return_value=(b'<results countResults="0"><items/></results>', '', False)):
            self.assertEqual(books.pages('bpt6k12345z', 'Example')['count'], 0)
        for raw in (b'<results/>', b'<results countResults="1"/>', b'<html/>'):
            with self.subTest(raw=raw), patch.object(books, '_xml', return_value=(raw, '', False)):
                result = books.pages('bpt6k12345z', 'Example')
                self.assertIn('error', result)
                self.assertNotIn('count', result)
        error = urllib.error.HTTPError('https://gallica.bnf.fr', 429, 'Rate limit', {'Retry-After': '60'}, None)
        with patch.object(books, '_xml', side_effect=error):
            result = books.pages('bpt6k12345z', 'Example')
        self.assertEqual(result['http_status'], 429)
        self.assertEqual(result['retry_after'], '60')
        self.assertNotIn('count', result)

    def test_input_limits_and_cql_escaping(self):
        for doc in ('https://evil.example/ark:/12148/x', '../secrets', 'file:///tmp/x'):
            self.assertIn('error', books.pages(doc, 'Example'))
        for kwargs in ({'query': ''}, {'query': 'Example', 'limit': 51}, {'query': 'Example', 'start': 0},
                       {'query': 'Example', 'year_from': 1900, 'year_to': 1880}):
            self.assertIn('error', books.search(**kwargs))
        with patch.object(books, '_xml', return_value=(SRU, '', False)) as fetch:
            books.search('Example" or dc.title all "Other')
        self.assertIn('\\" or dc.title all \\"', fetch.call_args.args[1]['query'])

    def test_response_size_diagnostic_html_and_cache(self):
        books._CACHE.clear()
        try:
            response = io.BytesIO(SRU)
            with patch.object(books.urllib.request, 'urlopen', return_value=response) as request, patch.object(books.time, 'sleep'):
                first = books.search('Invented cache test')
                second = books.search('Invented cache test')
            self.assertEqual(request.call_count, 1)
            self.assertFalse(first['cached'])
            self.assertTrue(second['cached'])
            self.assertEqual(first['retrieved_at'], second['retrieved_at'])
            for raw in (b'<html/>', b'<!DOCTYPE x><results countResults="0"/>', b'<results><diagnostic>bad query</diagnostic></results>', b'x' * (books.MAX_BYTES + 1)):
                with patch.object(books.urllib.request, 'urlopen', return_value=io.BytesIO(raw)), patch.object(books.time, 'sleep'):
                    self.assertIn('error', books.pages('bpt6k12345z', 'not cached'))
        finally:
            books._CACHE.clear()
