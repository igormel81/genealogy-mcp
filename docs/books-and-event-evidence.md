# Books and event citations

## Gallica: find a book, then its pages

```json
{"source":"gallica", "query":"Hugo", "year_from":1800, "year_to":1900}
```

Call `search_online` with those arguments. Gallica searches the OCR document index;
publication-year filters do **not** filter a person's birth year. The output includes a
stable document URL and `document_id`. A matching book has not yet established a fact.

Call `search_book_pages` to find pages in that document:

```json
{"document_id":"bpt6k5460422k", "query":"hugo", "start":0, "limit":10}
```

The document/query above is the BnF ContentSearch documentation's example. Output
includes OCR excerpts and URLs such as `/ark:/12148/.../f173.item`. `page_index` is the
scan's sequence number, **not** the printed folio/page; `printed_page` remains null.
Read the scan and record the printed page/folio yourself. An OCR snippet is a derivative,
not an exact transcription or evidence that the matching person belongs to your family.

`next_start` paginates within a book. For document search, `search_online` offers one-based SRU `start` and a bounded
`limit` (1–50, default 15). Other providers currently require `start=1`. Page excerpts use a zero-based result offset and at most 10 pages per call.
`total` is the provider's result count, `count` is the number returned in this response.
Unrecognised pages or absence from OCR cannot establish a negative finding in all scans.

Official interface references:

- [BnF SRU search](https://api.bnf.fr/fr/api-gallica-de-recherche): OCR text index,
  Dublin Core fields, publication-date comparisons and record pagination.
- [BnF document services](https://api.bnf.fr/fr/api-document-de-gallica): ContentSearch,
  page identifiers, excerpts and within-document pagination.

Only the fixed Gallica host is contacted; arbitrary document URLs are rejected. There is
one request per second per server process, a 25-second timeout, a 2 MiB response ceiling,
and up to eight successful XML responses cached in memory for ten minutes. The original
retrieval timestamp is retained on cache hits; no query cache is written to disk. Access
and throttling failures are not retried or converted to zero hits. Respect `Retry-After`
and the provider's terms; do not bypass restrictions. XML diagnostics, malformed data
and nonzero counts without result records are errors.

Verification on 21 October 2026: the documented SRU and ContentSearch examples returned
HTTP 403 from the checking connection. Contract tests use clearly synthetic XML matching
the official schema; this is not a claim that the live service responded successfully.
The on-demand `Live sources` workflow also checks document search and the BnF positive
page example. A network-restricted check emits an explicit warning; zero results or a
parser error still fail. Consult that run's actual output, not just its green status.

Other library references (HathiTrust, Polona, Iverieli and others) remain catalogue/browser
sources; this change does not claim new search APIs for them or provide local OCR.

## Event evidence: coverage, not proof

```json
{"project":"example", "root_person_id":"I1", "generations":4, "limit":100}
```

`project_evidence` reads JSON, GEDCOM and archive folders without writing, building,
converting or fetching anything online. It follows the root's biological ancestors
(adoptive links are not silently treated as biological) up to ten generations, visits
each person once, and returns at most 1,000 event rows. With no root configured it
considers all people. Closer generations are listed first, then broken/missing references.

It reviews recorded births, baptisms/christenings, deaths, burials, residence and marriages.
Only events with a date, place or event note are counted. Separate list-shaped residence
histories and custom event types are not interpreted by this version. Every event needs
its own `source_ids`; a person's/family's general source list is shown for context but
does not automatically cover that event.

Statuses:

- `missing_reference`: no reference attached to that event;
- `broken_reference`: a referenced source ID is absent from the source register;
- `needs_locator`: sources exist but at least one lacks a locator (a URL alone does not
  identify a particular archival file, folio, edition and page);
- `reference_present`: referenced source records have locators. The server has **not**
  checked whether the document proves the claim, whether the locator is correct, or
  which fields of the event it supports.

Citations expose the source title, locator, URL and up to 2,000 characters of supplied
transcription (`scope`), with an explicit truncation flag. Read the source record for the full text.
A hidden source remains hidden in the site's publication flow; this local report can
still display it to the owner and must not be copied to public output without review.
No parentage is declared proved from a marriage/birth citation. Field-level assertion
provenance, contradiction resolution, OCR and automatic tree merging remain separate work.
