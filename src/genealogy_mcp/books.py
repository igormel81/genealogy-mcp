"""Documented Gallica SRU and ContentSearch APIs; results are candidates, not evidence.

https://api.bnf.fr/fr/api-gallica-de-recherche
https://api.bnf.fr/fr/api-document-de-gallica
"""
import collections
import datetime
import html
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from . import __version__

BASE = 'https://gallica.bnf.fr'
MAX_BYTES = 2 * 1024 * 1024
_CACHE = collections.OrderedDict()
_LOCK = threading.Lock()
_LAST = 0.0
NS = {'s': 'http://www.loc.gov/zing/srw/', 'dc': 'http://purl.org/dc/elements/1.1/'}


def _xml(path, params):
    """Fixed host, bounded response, one request/second, eight in-memory cached responses.

    No retry for access denial or throttling; errors are never cached. No query is saved
    to disk. A cached response retains its original retrieval time.
    """
    global _LAST
    url = BASE + path + '?' + urllib.parse.urlencode(params)
    with _LOCK:
        now = time.monotonic()
        if url in _CACHE and now - _CACHE[url][0] < 600:
            _CACHE.move_to_end(url)
            return _CACHE[url][1], _CACHE[url][2], True
        time.sleep(max(0, 1 - (now - _LAST)))
        _LAST = time.monotonic()
        req = urllib.request.Request(url, headers={'User-Agent': f'genealogy-mcp/{__version__} (+https://github.com/igormel81/genealogy-mcp)', 'Accept': 'application/xml'})
        with urllib.request.urlopen(req, timeout=25) as response:
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError('Gallica response too large; narrow the query')
        if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
            raise ValueError('Gallica returned unsupported XML declarations')
        root = ET.fromstring(raw)
        if root.tag.rsplit('}', 1)[-1] not in ('searchRetrieveResponse', 'results'):
            raise ValueError('Gallica returned an unexpected XML root')
        diagnostics = [e for e in root.iter() if e.tag.rsplit('}', 1)[-1] == 'diagnostic']
        if diagnostics:
            raise ValueError('Gallica diagnostic: ' + ' '.join(diagnostics[0].itertext()).strip()[:300])
        expected_root = 'searchRetrieveResponse' if path == '/SRU' else 'results'
        if root.tag.rsplit('}', 1)[-1] != expected_root:
            raise ValueError('Gallica returned the wrong API response type')
        count = root.findtext('s:numberOfRecords', namespaces=NS) if root.tag.rsplit('}', 1)[-1] == 'searchRetrieveResponse' else root.get('countResults')
        if count is None or not count.isdigit():
            raise ValueError('Gallica XML: missing result count')
        items = root.findall('.//s:record', NS) if path == '/SRU' else root.findall('./items/item')
        offset = int(params.get('startRecord', 1)) - 1 if path == '/SRU' else int(params.get('startResult', 0))
        if int(count) > offset and not items:
            raise ValueError('Gallica: nonzero count without result records')
        if path != '/SRU' and any(not re.fullmatch(r'PAG_0*[1-9]\d*', item.findtext('p_id') or '') for item in items):
            raise ValueError('Gallica ContentSearch: missing page identifier')
        fetched = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _CACHE[url] = (time.monotonic(), raw, fetched)
        _CACHE.move_to_end(url)
        while len(_CACHE) > 8:
            _CACHE.popitem(last=False)
        return raw, fetched, False


def _error_call(fn, **kw):
    try:
        return fn(**kw)
    except urllib.error.HTTPError as error:
        return {'source': 'gallica', 'error': f'Gallica HTTP {error.code}; the search is incomplete. Open Gallica in your browser.',
                'error_kind': 'http', 'http_status': error.code, 'retry_after': error.headers.get('Retry-After') if error.headers else None}
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {'source': 'gallica', 'error': str(error), 'error_kind': 'network'}
    except (ValueError, ET.ParseError) as error:
        return {'source': 'gallica', 'error': str(error), 'error_kind': 'invalid_response_or_input'}


def _query(value):
    value = str(value).strip()
    if not value or len(value) > 500:
        raise ValueError('query: between 1 and 500 characters required')
    return value


def _integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'{label}: integer {low}–{high} required')
    return value


def _ark(value):
    value = str(value).strip()
    # Do not accept arbitrary hosts or URLs; only the provider's stable document IDs.
    m = re.fullmatch(r'(?:https?://gallica\.bnf\.fr/)?(?:ark:/12148/)?([a-z][a-z0-9]+)(?:/f\d+(?:\.[a-z]+)?)?', value)
    if not m:
        raise ValueError('document_id: Gallica ARK identifier or https://gallica.bnf.fr/ark:/12148/... required')
    return m[1]


def _search(query, year_from=None, year_to=None, start=1, limit=15):
    query = _query(query)
    start = _integer(start, 1, 1000000, 'start')
    limit = _integer(limit, 1, 50, 'limit')
    for key, value in (('year_from', year_from), ('year_to', year_to)):
        if value is not None:
            _integer(value, 1, 9999, key)
    if year_from and year_to and year_from > year_to:
        raise ValueError('year_from must not exceed year_to')
    quoted = query.replace('\\', '\\\\').replace('"', '\\"')
    cql = f'text all "{quoted}"'
    if year_from:
        cql += f' and dc.date >= "{year_from}"'
    if year_to:
        cql += f' and dc.date <= "{year_to}"'
    raw, fetched, cached = _xml('/SRU', {'version': '1.2', 'operation': 'searchRetrieve', 'query': cql,
                                        'startRecord': start, 'maximumRecords': limit, 'collapsing': 'false'})
    root = ET.fromstring(raw)
    total_text = root.findtext('s:numberOfRecords', namespaces=NS)
    if total_text is None or not total_text.isdigit():
        raise ValueError('Gallica SRU: missing result count')
    rows = []
    for record in root.findall('.//s:record', NS):
        def values(key):
            return [' '.join(e.itertext()).strip() for e in record.findall('.//dc:' + key, NS)]
        ids = values('identifier')
        url = next((u for u in ids if re.fullmatch(r'https?://gallica\.bnf\.fr/ark:/12148/[a-z0-9]+(?:/.*)?', u)), '')
        if not url:
            # Metadata from partner collections need not have a Gallica ARK; expose it
            # without pretending it can be searched by ContentSearch.
            rows.append({'title': '; '.join(values('title')), 'date': '; '.join(values('date')),
                         'identifiers': ids, 'document_id': None, 'url': None, 'match_scope': 'document_ocr_index'})
            continue
        document_id = re.match(r'https?://gallica\.bnf\.fr/ark:/12148/([a-z0-9]+)', url)[1]
        rows.append({'title': '; '.join(values('title')), 'date': '; '.join(values('date')),
                     'creators': values('creator'), 'publishers': values('publisher'), 'rights': values('rights'), 'document_id': document_id,
                     'url': f'{BASE}/ark:/12148/{document_id}', 'match_scope': 'document_ocr_index'})
    total = int(total_text)
    if total and start <= total and not rows:
        raise ValueError('Gallica SRU: nonzero count without records')
    return {'source': 'gallica', 'query': query, 'count': len(rows), 'total': total, 'start': start,
            'next_start': start + len(rows) if rows and start + len(rows) <= total else None,
            'results': rows, 'retrieved_at': fetched, 'cached': cached,
            'note': 'OCR document matches, not verified people. Years filter publication dates. Use search_book_pages with a document_id for page excerpts; inspect the original scan.'}


def search(query, year_from=None, year_to=None, start=1, limit=15):
    return _error_call(_search, query=query, year_from=year_from, year_to=year_to, start=start, limit=limit)


def _pages(document_id, query, start=0, limit=10):
    document_id, query = _ark(document_id), _query(query)
    start = _integer(start, 0, 1000000, 'start')
    limit = _integer(limit, 1, 10, 'limit')
    raw, fetched, cached = _xml('/services/ContentSearch', {'ark': document_id, 'query': query, 'startResult': start})
    root = ET.fromstring(raw)
    total_text = root.get('countResults', '')
    if root.tag != 'results' or not total_text.isdigit():
        raise ValueError('Gallica ContentSearch: missing result count')
    items = root.findall('./items/item')
    rows = []
    for item in items[:limit]:
        page_id = item.findtext('p_id') or ''
        match = re.fullmatch(r'PAG_(\d+)', page_id)
        if not match or int(match[1]) < 1:
            raise ValueError('Gallica ContentSearch: missing page identifier')
        page = int(match[1])
        excerpt = html.unescape(re.sub('<[^>]*>', '', ''.join(item.find('content').itertext()) if item.find('content') is not None else ''))
        rows.append({'document_id': document_id, 'page_index': page, 'printed_page': None,
                     'url': f'{BASE}/ark:/12148/{document_id}/f{page}.item',
                     'excerpt': excerpt[:2000], 'text_kind': 'provider_ocr_excerpt'})
    total = int(total_text)
    if total and start < total and not rows:
        raise ValueError('Gallica ContentSearch: nonzero count without pages')
    return {'source': 'gallica', 'document_id': document_id, 'query': query, 'count': len(rows), 'total': total,
            'start': start, 'next_start': start + len(rows) if rows and start + len(rows) < total else None,
            'results': rows, 'retrieved_at': fetched, 'cached': cached,
            'note': 'page_index is the scan sequence, not a printed page number. OCR excerpts may be wrong; open the scan before citing a fact. No OCR hit does not establish absence from unrecognised pages.'}


def pages(document_id, query, start=0, limit=10):
    return _error_call(_pages, document_id=document_id, query=query, start=start, limit=limit)
