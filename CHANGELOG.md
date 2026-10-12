# Changelog

## 0.2.0

- **Live search** (`search_online`): Internet Archive full text (passages with the words found), WikiTree, Open
  Archives, Chronicling America, Open List; `place_history`: what a village belonged to over time (Wikidata).
- **Where the records are** (`where_are_records`): 87 provinces of the Russian Empire, the Kingdom of Poland, Galicia,
  Bukovina, East Prussia, the Baltics and the Caucasus → today's regions and archives.
- **A research project that remembers** (`project_view`, `project_save`, `project_log`, `project_transfer`): people,
  families, sources, leads, a search log with negative results, a corrections log, GEDCOM import and export; the
  gene_archive data format.
- `dna_match` (shared cM → relationships), Daitch–Mokotoff codes in `name_variants`, `cyrillic_numerals`,
  `feast_date` (church feasts and fasts, movable ones too), Hebrew and French Republican calendars in
  `convert_calendar`, Hispanic double surnames in `check_match`, Jewish given names.
- Claude Desktop extension (`.mcpb`) in every release; releases publish to PyPI and the MCP Registry when enabled.
- Benchmark: 32 questions with checkable answers (`evals/`); the tools answer all of them, checked in CI.

## 0.1.0

First release.

- 14 tools: `plan_research`, `find_sources`, `source_details`, `search_links`, `name_variants`, `normalize_date`,
  `convert_calendar`, `birth_year_from_age`, `kinship`, `check_match`, `audit_tree`, `draft_archive_request`,
  `record_guide`, `glossary`.
- A catalogue of 79 sources: worldwide, Russia and the USSR, Eastern Europe and the Baltics, Western and Northern
  Europe, the British Isles, the USA and Latin America.
- Record guides (en/ru), a glossary of old Russian terms, the research guide and prompts of gene_archive as resources.
- stdio and Streamable HTTP (`--http`) transports.
