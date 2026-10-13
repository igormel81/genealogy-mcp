# genealogy-mcp — find your family history with any AI assistant

<!-- mcp-name: io.github.igormel81/genealogy-mcp -->

**[Русская версия](README.ru.md)**

[![CI](https://github.com/igormel81/genealogy-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/igormel81/genealogy-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/genealogy-mcp.svg)](https://pypi.org/project/genealogy-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/genealogy-mcp.svg)](https://pypi.org/project/genealogy-mcp/)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-io.github.igormel81%2Fgenealogy--mcp-1f3b33)](https://registry.modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An [MCP](https://modelcontextprotocol.io) server that turns Claude, ChatGPT, Cursor or any MCP-capable assistant into a
careful genealogist. It knows **where** the records of your ancestors are (114 archives and databases across Russia and
the former USSR, Europe, the British Isles, the USA and Latin America), **how** to search them (name variants,
transliterations, old spelling, the Julian calendar), and **when a find really is your person** — so the assistant gives
you working links and a plan instead of confident guesses.

Built from years of real research for an open family archive powered by
[gene_archive](https://github.com/igormel81/gene_archive): parish registers, revision lists, WWI and WWII databases,
repression files, emigration records — and every trap we fell into along the way.

![You ask your assistant; genealogy-mcp knows where to look, how to search, how to read old dates and whether a find is your person, and writes into your project, your own GEDCOM tree or your family site](https://raw.githubusercontent.com/igormel81/genealogy-mcp/main/docs/overview.svg)

## At a glance

- **114 archives and databases in 55 countries**, each with what it holds and *how to search it well* — and which
  archive holds the records of a historical province today (borders moved; the answer is often not the obvious one).
- **24 tools** for the real work of a genealogist: name variants and 9 transliteration systems, Daitch–Mokotoff,
  Julian, Hebrew and French Republican calendars, dates by church feasts, Church Slavonic numerals, kinship in three
  languages, DNA, evidence checks, a tree audit, live search in open databases, archive request drafts.
- **It works on your tree, not beside it.** Point it at the `.ged` file from MyHeritage, Ancestry, Gramps or RootsMagic
  and it reads, searches and changes it in place — only the changed lines, everything else byte for byte, a copy kept,
  every change shown first. Or at a [gene-archive](https://github.com/igormel81/gene_archive) family website: changes go
  through the site's checks, logs and git history.
- **It remembers.** Sources with full citations, open leads and every search — "nothing found" included — so nobody
  searches the same place twice.
- **Honest by design.** A namesake is not a relative: a find is linked only with two independent facts beyond the name.
- **Private.** Runs on your computer; goes online only for a search you ask for, and only to that one site.
- **Any assistant:** Claude Desktop (one-click install), Claude Code, ChatGPT, Cursor, VS Code, Windsurf, Cline.
- Guides in English, Russian and Ukrainian, the main ones also in Spanish, Portuguese, Polish and German.

## Quick start

**Claude Desktop:** download `genealogy-mcp-<version>.mcpb` from the
[latest release](https://github.com/igormel81/genealogy-mcp/releases/latest) and open it.
**Claude Code:** `claude mcp add genealogy -- uvx genealogy-mcp`.
**Anything else:** `uvx genealogy-mcp` as the server command (details in [Install](#install)).

Then just ask: *"Help me find my great-grandfather. Here is what I know…"*

## What you can ask

> *My great-grandfather Ivan Kolodin was born about 1885 near Bogoroditsk, Tula province. Where do I look?*

The assistant makes a plan for Russia 1880–1945, reads the record guides, builds the name forms (Колодин / Колодина /
Колодинъ / Kolodin / Kołodin…), gives you search links for FamilySearch, the Internet Archive full text and the
Russian war databases, tells you which archive holds the parish registers and drafts the request.

> *Is this baptism record the same Ivan? It says «Іоаннъ, father Петръ, 1887, Сынково».*

`check_match` compares fact by fact with name variants and age tolerance: two independent facts beyond the name →
confirmed; one → probable; a contradiction → find a third document.

> *What is my grandmother's cousin's daughter to me? И как это по-русски?*

`kinship` → «троюродная сестра… / first cousin once removed» — in Russian, English and Romanian, with the expected DNA share.

> *Check my tree.* (a GEDCOM from Ancestry, MyHeritage, Gramps, Geni…)

`audit_tree` finds the impossible (born after the mother's death, a mother aged 10, death before birth), possible
duplicates and gaps — a to-do list for the next search.

> *The register says he was born «на Покров» 1885, the year is written ҂аѡ҃пе.*

`cyrillic_numerals` reads the year (1885), `feast_date` gives 1 October (Julian) = 13 October 1885.

> *We share 230 cM with a match on MyHeritage. Who could she be?*

`dna_match`: second cousin, first cousin twice removed, half first cousin… — and why only documents can decide.

> *Where are the parish registers of Volhynia governorate now?*

`where_are_records`: the state archives of Zhytomyr (the consistory), Rivne and Volyn — borders moved, so it is not
always the archive of today's region.

> *Remember what we found, and continue next week.*

A research project on your computer: people, sources with full citations, open leads and a log of every search —
including "nothing found" — so nobody searches the same place twice. GEDCOM in and out.

> *Write what we found into our family site.*

If your family archive is a [gene-archive](https://github.com/igormel81/gene_archive) site, give the project tools the
path of its folder: the assistant reads the archive itself — who is missing, which dates have no document — and every
change it makes goes through the site's own checks, lands in its corrections and research logs, is committed to git
under your name and rebuilds the site. It shows the change first and writes only after your yes.

> *Here is my tree — add what we found.*

Or give it the GEDCOM file of the tree you keep in MyHeritage, Ancestry, Gramps, RootsMagic, Family Historian or
webtrees: the assistant reads it, searches it and changes it in place. Only the lines of what changed are rewritten —
your program's own tags, photos, notes and the header stay byte for byte; it shows those lines before writing, keeps a
copy of the file, and keeps the search log, leads and corrections in a file next to it. Then import the file back into
your program (Family Historian and webtrees work on GEDCOM directly). Files not in UTF-8 are read-only.

## Why use it

| Without it | With genealogy-mcp |
|---|---|
| The assistant names two or three famous websites | 114 sources chosen by country, years and kind of record, each with "how to search it well" |
| Searches one spelling | Spelling variants, pre-1918 orthography, male/female forms, 9 transliteration systems, given-name equivalents (Иван = Іоаннъ = Jan = Johann = Juan) |
| Invented or broken URLs | Ready search links built from tested URL templates; a weekly job checks every site |
| "This is probably your ancestor" | An explicit evidence rule: a namesake is not a relative |
| Dates taken at face value | Julian ↔ Gregorian, birth years from ages with realistic drift, dates normalised to GEDCOM |
| Generic advice | Record guides: parish registers, confession lists, revision lists, household books, WWI/WWII, repression files, passenger lists, censuses, European civil registration, Latin American records |
| You write to archives from scratch | Request drafts for Russian ZAGS, state, military and FSB archives, and for any archive in English, Spanish or Portuguese |
| It forgets everything between chats | A research project that remembers people, sources, leads and every search |
| It cannot touch your tree | Reads and changes your own GEDCOM file in place, losing nothing, showing every change first |
| It cannot read old numbers and dates | Church Slavonic numerals, church feasts, Julian, Hebrew and French Republican calendars |
| "Search FamilySearch for your name" | Live search in the Internet Archive full text, WikiTree, Open Archives and Wikidata place history |
| DNA matches are a mystery | Shared cM → the relationships it fits |

Most genealogy MCP servers connect the assistant to one service or one file. genealogy-mcp gives it the research
method around them — where to look, how to search, how to read and weigh what it finds — and works on your own tree
file too. It runs happily next to a server for a service you use, such as a FamilySearch client.

Everything runs on your computer. The server goes online only when the assistant runs a live search
(`search_online`, `place_history`), and then sends that query to that one site.

## Coverage

- **Worldwide:** FamilySearch (records and the catalogue of unindexed images), Internet Archive full text, MyHeritage,
  Geni, WikiTree, Find a Grave, BillionGraves, Arolsen Archives, Yad Vashem, JewishGen, Matricula, Geneanet, Wikipedia.
- **Russia and the USSR:** Yandex Archive, archive guides, VGD forum, Pamyat Naroda, OBD Memorial, gwar.mil.ru,
  Open List, Immortal Barrack, Returned Names, PSTGU martyrs, Presidential and National Electronic Libraries,
  historical libraries, old maps, church history, RIA-1914, regional archives, ZAGS, TsAMO, RGVIA, RGIA, GARF.
- **Ukraine, Belarus, Moldova, Romania, Poland, the Baltics:** national archive portals and catalogues, TsDIAK,
  Geneteka, Szukajwarchiwach, epaveldas, Raduraksti, the Estonian archives.
- **Europe:** ICRC WWI prisoners, CWGC, Volksbund, ScotlandsPeople, FreeBMD, Irish civil and census records, Archion,
  GenWiki, FranceArchives, Mémoire des hommes, Antenati, PARES, Digitarq, Open Archives (NL), Belgian State Archives,
  Riksarkivet, Digitalarkivet, Danish Family Search, HisKi, Finnish Digital Archive, Hungaricana, Acta Publica (Czechia),
  Bulgarian state archives, FreeCEN, FreeREG, The National Archives, GRO, Welsh Newspapers.
- **Germany and German-speaking lands:** WWI casualty lists, GEDBAS, Online-OFB, German Digital Library, Bundesarchiv,
  Baltic Biographical Lexicon, Black Sea Germans (Odessa3), Poznań Project, Metryki.
- **Jewish genealogy:** JRI-Poland, Gesher Galicia, LitvakSIG, JewishGen, Yad Vashem, Steve Morse One-Step tools.
- **Caucasus and Central Asia:** National Archives of Georgia, the central state archives of Kazakhstan, Uzbekistan,
  Kyrgyzstan, Tajikistan and Turkmenistan.
- **The Americas:** FamilySearch Latin America, AGN Mexico, Arquivo Nacional and Museu da Imigração (Brazil),
  Hemeroteca Digital, CEMLA and AGN (Argentina), Archivo Nacional (Chile), NARA, Ellis Island, Chronicling America,
  USGenWeb, Library and Archives Canada, BAnQ (Quebec), Pier 21.
- **Australia and New Zealand:** Trove, National Archives of Australia, Papers Past, New Zealand BDM.

Record guides in English, Russian and Ukrainian, the main ones also in Spanish, Portuguese, Polish and German.

## Install

**Claude Desktop, one click:** download `genealogy-mcp-<version>.mcpb` from the
[latest release](https://github.com/igormel81/genealogy-mcp/releases/latest) and open it — Claude Desktop installs
it and asks where to keep your research projects.

For the other ways you need [uv](https://docs.astral.sh/uv/getting-started/installation/) (it fetches Python and the
package by itself).

**Claude Desktop, by hand** — Settings → Developer → Edit Config, add:

```json
{
  "mcpServers": {
    "genealogy": {
      "command": "uvx",
      "args": ["genealogy-mcp"]
    }
  }
}
```

**Claude Code:**

```sh
claude mcp add genealogy -- uvx genealogy-mcp
```

**Cursor** (`~/.cursor/mcp.json`), **Windsurf**, **Cline** — the same `mcpServers` block as for Claude Desktop.
**VS Code** (`.vscode/mcp.json`): `{"servers": {"genealogy": {"command": "uvx", "args": [ …same… ]}}}`.

**Docker:** `docker build -t genealogy-mcp .` then `docker run -i --rm genealogy-mcp` (stdio) or
`docker run --rm -p 8000:8000 genealogy-mcp --http --host 0.0.0.0` (HTTP at `/mcp`).

**Your gene-archive site** as the project: install the server together with gene-archive —
`pip install "genealogy-mcp[site]"` or `uvx --from "genealogy-mcp[site]" genealogy-mcp` (the `gene` command is found
on PATH or next to the server's Python; elsewhere set `GENE_CMD`), then name the folder in `GENEALOGY_MCP_SITES` (or in the Claude Desktop extension settings), or just give its path
to the assistant. `GENE_AUTHOR` sets the name in the git history (default: `git config user.name`).

**Your tree in a GEDCOM file** as the project: give the assistant the path of the `.ged` file (or name it in
`GENEALOGY_MCP_SITES`). Copies are kept as `tree.ged.bak` (before the last change) and `tree.before-genealogy-mcp.ged`
(before the first); the log lives in `tree.ged.research.json`.

**Clients that connect over HTTP** (ChatGPT connectors, remote agents): run
`genealogy-mcp --http --host 0.0.0.0 --port 8000` behind HTTPS and add `https://your-host/mcp`.
In HTTP mode `audit_tree` takes the GEDCOM text only, never a file path.

The package is on [PyPI](https://pypi.org/project/genealogy-mcp/) and in the [official MCP Registry](https://registry.modelcontextprotocol.io) (`io.github.igormel81/genealogy-mcp`): `uvx genealogy-mcp` installs and runs it.

## Tools

| Tool | What it does |
|---|---|
| `plan_research` | A step-by-step plan for a country and period: which records exist, guides, sources in order |
| `find_sources` | Sources by country/region (`europe`, `latin_america`, `russian_empire`…), years and record kind |
| `source_details` | One source: coverage, access, how to search |
| `where_are_records` | Which archives now hold the records of a historical province (Russian Empire, Poland, Galicia, Bukovina, East Prussia, the Baltics, the Caucasus) |
| `search_links` | Ready search URLs for a name and its variants |
| `search_online` | Live search: Internet Archive full text, Chronicling America, WikiTree, Open Archives, Open List |
| `place_history` | Wikidata: what a village belonged to over the years, coordinates, Wikipedia article |
| `name_variants` | Spelling, old orthography, gendered forms, transliterations, Daitch–Mokotoff codes, given-name equivalents (incl. Yiddish and Hebrew), patronymics |
| `normalize_date` | "около 1899", "9 de octubre de 1899" → `ABT 1899`, `9 OCT 1899` |
| `convert_calendar` | Julian ↔ Gregorian, Hebrew, French Republican |
| `feast_date` | «на Покров», «после Петрова поста», Easter, Wielkanoc… → the date in a given year |
| `cyrillic_numerals` | ҂аѡ҃п ↔ 1880 |
| `birth_year_from_age` | The birth-year range from an age in a record |
| `kinship` | The name of a relation in ru/en/ro, with the expected DNA share |
| `dna_match` | Shared cM → the relationships it fits (Shared cM Project 4.0) |
| `check_match` | Is a found record our person? A verdict with every fact compared (Hispanic double surnames too) |
| `audit_tree` | Impossible facts, duplicates and gaps in a GEDCOM or `family_tree.json` |
| `project_view`, `project_save`, `project_log`, `project_transfer` | The research project between conversations: people, families, sources, leads, the search log, GEDCOM import/export — or a gene-archive site folder, written through its checks and logs, or your own `.ged` file, changed in place |
| `draft_archive_request` | A request letter to a registry office or archive |
| `record_guide` | How to read and find a kind of record |
| `glossary` | Old Russian record terms explained |

**Resources:** `genealogy://sources` (the catalogue), `genealogy://guide/research/{en|ru}` (a full research guide),
`genealogy://guide/prompts/{en|ru}` (ready requests for each step), `genealogy://records/{topic}`, `genealogy://glossary`.
**Prompts:** start research, check a find, transcribe a record, write to an archive.

## Privacy and honesty

- The server sends nothing anywhere by itself. A live search (`search_online`, `place_history`) sends the query — names,
  years, place — to the one site searched. Research projects are files on your computer
  (`~/Documents/genealogy-mcp` or `GENEALOGY_MCP_HOME`); on a shared HTTP server they are switched off.
- The assistant you use is a separate service with its own privacy policy — think before pasting details about living
  people.
- Letters are drafts: you check and send them.
- The rules the assistant gets: cite the original, keep conflicting versions, mark guesses as "probably", never link a
  namesake without evidence.

## Benchmark

`evals/tasks.json` holds 32 questions with checkable answers: dates by church feasts, Julian, Hebrew and Republican
calendars, Cyrillic numerals, Daitch–Mokotoff, DNA, kinship, old terms, archives of historical provinces, evidence
checks, record history. `evals/check_tools.py` runs in CI and checks that the tools answer all of them correctly.
`evals/run.py` asks a Claude model the same questions without the server and with it and scores both
(needs an API key; it costs money, so it is run by hand: Actions → Benchmark).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for source fields and contribution guidelines.
A source is missing or a link moved? Edit `tools/make_sources.py`, run `python3 tools/make_sources.py` and
`python3 -m unittest discover tests`, open a pull request. Record guides live in `src/genealogy_mcp/guides.py`.

## See also

- [gene_archive](https://github.com/igormel81/gene_archive) — an open-source engine for a family archive website:
  tree, stories, documents, map, GEDCOM, an online editor and relatives' comments.

MIT License.
