# Changelog

## Unreleased

- Fix false `check_match` confirmations for different given names, different villages
  sharing a province, and double-counting the same birth/residence place.
- Research order: family/registry actions, complete extraction of existing documents,
  primary records for the whole household, then secondary leads; Moldova revision routing.
- Per-project policy, active-question limits, required next steps, waiting/reading-room
  leads and structured source checks. Unavailable websites do not count as negative searches.
- Read custom archive folders without converting or writing them; expose local resources
  and project instructions. Log existing-record edits in both corrections and research logs.
- Catalogue: 171 sources, including direct regional archive catalogues, libraries and
  supporting reference works. Split the two Bessarabian websites; show unspecified date
  coverage explicitly. See docs/research-workflow.md for source references and limitations.

## 0.6.0

- Catalogue: 124 sources. New for Russia: NashiPredki (indexes of registers, revision and confession lists),
  metricabook.ru (register scans), Rodovod, Road of Memory and Immortal Regiment (WWII). New for Bessarabia, Moldova
  and Romania: genealogica.ro (with the exact-match, county and year settings and its hourly limit), Genealogy of
  Bessarabia, deportari.org, Cartea Memoriei and Dmitriev's 1772–1774 Moldavian censuses with their gaps (#5).
- **What has been read.** `project_coverage` keeps parish → year → part (births, marriages, deaths, confession and
  revision lists) → film and frames → status (complete, partial up to No. …, not found) with the sources, and answers
  what is still unread for these villages and years — a village is matched through the entries that name it. Kept in
  the project file, next to a `.ged` file in `<file>.research.json`, and for a gene-archive site in a file of this
  server, read together with the site's own `coverage` section (`gene apply` does not take coverage yet) (#7).
- **Reading unindexed FamilySearch films.** A new section of the research guide — catalogue → film → frames, finding
  the parish book with thumbnails and end-of-year summaries, full frames only for records, the variable rate limit
  (an hour's pause after HTTP 429, no parallel sessions), the volume's title page over inventory numbers — and the
  `film_reading_plan` tool: which films to read in which order, a rough request budget in sessions, what to log;
  with a project it skips what is already read and resumes partial books (#6).
- **Borders by year in `where_are_records`.** With `year`, Bessarabia is answered for that year: the south (Cahul,
  Ismail, Bolgrad — also given as a district) was Moldavian, then Romanian in 1857–1878 (Treaty of Paris 1856 → Treaty
  of Berlin 1878), all Bessarabia Romanian in 1918–1940 and 1941–1944, Soviet from June 1940 and 1944; the state, the
  county or uezd of the time and the archives to search now (Chișinău, the Izmail branch of the Odesa region archive,
  the Romanian National Archives, the civil registry), with a warning in border years (#12).
- **Parish attachment.** `where_are_records` takes a `village` and `place_history` reports it too: which church kept
  the village's books (a village without a church was recorded in a neighbouring one), with years and source, and how
  to find it out — clergy registers, consistory inventories, gazetteers, the book's own summary. Only sourced
  attachments are listed (#8).
- **Moldovan and Bessarabian surnames** in `name_variants` (found by Romanian letters and endings, or with
  `origin="moldovan"`): Romanian forms and endings (-eanu/-ean, -anu/-an, ș/ş, ț/ţ, without diacritics), Russian
  renderings (Călugăreanu = Калугаряну = Калугарян = Калугоряну), Soviet Moldavian Cyrillic (Кэлугэряну), pre-1918
  hard sign (Плешъ) and -u forms (Плешу, Pleșu); a pair from a register («Мокану, он же Плеш», "Mocanu zis Pleș") is
  split and flagged as a possible second surname; clerks' contractions (Калгаран) and recognition errors (Калугамян)
  are given as hints only, with a warning about look-alikes that are another family (Плеско / Попеско). `check_match`
  and `search_links` use the Romanian and Russian forms (#9).
- **`estimate_birth_year`** — a birth year from relatives (eldest child −27, spouse and siblings ±8, parents
  +18…+45, first marriage at about 22) and ages in records: a GEDCOM date (`BET … AND …`, or `ABT …` when the range
  is wide), the most likely year and a ready explanation sentence in English or Russian. Ages are checked against
  each other: 7 in 1850 and 22 in 1882 are flagged as likely two namesakes (#10).
- **`parent_hypothesis`** — a working hypothesis about a father from a patronymic: the given name it implies
  (Петрович → Пётр, Ильич → Илья, Кузьминична → Кузьма), candidates ranked by name, surname, village and age, the
  arguments for and against (a grandson with his name, godparents and sureties of his surname, his household listing a
  child of this name; too old, died before the birth, another name), a warning for a namesake from another village,
  the records that would settle it and a ready open lead. The evidence rule stands: a hypothesis, never a link (#11).

## 0.5.1

- `place_history` finds a village given together with its region («Сынково Тульская область», «Каменка Черкасская
  область»): Wikidata matches names only, so when the whole phrase finds nothing the settlement name is searched and
  the rest of the phrase picks the right namesake (generic words like «область», «район», «уезд» are ignored).
  Before, such a query — the very example in the tool's description — returned nothing.

## 0.5.0

- **Your own tree as the project.** The project tools take the path of a `.ged` file — the tree from MyHeritage,
  Ancestry, Gramps, RootsMagic, Family Historian, webtrees: the assistant reads and searches it and changes it in place.
  Only the changed lines are rewritten (other programs' tags, photos, notes, the header, line endings and the BOM stay
  as they were), `gedcom_changes` shows them — also with `dry_run`; a copy is kept before every write and before the
  first one; the search log, leads and corrections live in `<file>.research.json`. Files not in UTF-8 are read-only.
- README: what it does at a glance, a diagram, a quick start, badges; the Russian comparison table is whole again.

## 0.4.1

- `pip install "genealogy-mcp[site]"` installs gene-archive (now on PyPI) for your site folder in one step.
- The `gene` command is found next to the server's Python too, so a virtualenv that was not activated works
  without `GENE_CMD`.

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
