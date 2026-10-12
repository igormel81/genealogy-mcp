# Changelog

## 0.4.0

- **Your family site as the project.** The project tools take the path of a gene-archive site folder (or the folders
  in `GENEALOGY_MCP_SITES`, also a setting of the Claude Desktop extension): the assistant reads the archive itself,
  and every change goes through `gene apply` — the site's checks, its corrections and research logs, a git commit
  under the owner's name, a rebuild of the site. `project_save` has `dry_run` to show a change before writing it.

## 0.3.2

- Open List live search works again: the site's MediaWiki search is disabled, so `search_online` uses its OpenSearch
  (name prefixes) and reports site errors instead of an empty result.
- Translated record guides proofread (uk, pl, de, es, pt); three factual fixes: the Bundesarchiv department for
  pre-1945 military personnel (DR, Berlin-Tegel), WWI casualty lists do not always give the regiment, the French
  Republican calendar ended on 1 January 1806.
- Dockerfile (stdio and HTTP), checked in CI by starting the container and listing the tools.

## 0.3.1

Reference data checked against official sources (`docs/reference-audit-2026-10-12.md`):

- Archives: current names in Tatarstan, Buryatia, Bashkortostan, Orenburg and Uzbekistan; AGAD (fond 298) for Galician
  Greek Catholic registers; RGIA of the Far East for Amur; Erivan governorate also found by Azerbaijan (Nakhchivan),
  Transcaspian by Kazakhstan (Mangyshlak).
- Guides: civil registration in Spain from 1 January 1871, Austria — marriages from 1 August 1938, births and deaths from
  1 January 1939 (not Galicia and Bukovina), early Italian regional registers; revisions span several years, no women in
  the 1811 revision; access to repression files told apart for Ukraine (open since 2015) and Russia.
- Catalogue: 114 sources — the Central Asian entry split into five national archives with their sites; Finland's digital
  archive moved to Astia; coverage and access corrected for GRO, Pier 21, Trove, NAA, Papers Past, NZ BDM, JRI-Poland,
  Gesher Galicia, Steve Morse, Bundesarchiv, BBLD, Odessa3 and others.
- A test keeps these corrections from slipping back.

## 0.3.0

- The catalogue grows to 110 sources: Germany (WWI casualty lists, GEDBAS, Online-OFB, German Digital Library,
  Bundesarchiv), Jewish genealogy (JRI-Poland, Gesher Galicia, LitvakSIG, Steve Morse), the British Isles (FreeCEN,
  FreeREG, The National Archives, GRO, Welsh Newspapers), Canada, Australia and New Zealand, Czechia, Finland, Bulgaria,
  Georgia, Central Asia; new regions for `find_sources`: Central Asia, the Caucasus, the Balkans, North America, Oceania.
- `where_are_records`: 87 provinces — Siberia, the Far East and Central Asia added; a country name lists every
  province now (partly) in it.
- Record guides in Ukrainian (all twelve) and, for the most used topics, Spanish, Portuguese, Polish and German.
- The weekly link check also opens every search-link template.

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
