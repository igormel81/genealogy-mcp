# genealogy-mcp — find your family history with any AI assistant

<!-- mcp-name: io.github.igormel81/genealogy-mcp -->

**[Русская версия](README.ru.md)**

[![CI](https://github.com/igormel81/genealogy-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/igormel81/genealogy-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An [MCP](https://modelcontextprotocol.io) server that turns Claude, ChatGPT, Cursor or any MCP-capable assistant into a
careful genealogist. It knows **where** the records of your ancestors are (79 archives and databases across Russia and
the former USSR, Europe, the British Isles, the USA and Latin America), **how** to search them (name variants,
transliterations, old spelling, the Julian calendar), and **when a find really is your person** — so the assistant gives
you working links and a plan instead of confident guesses.

Built from years of real research for an open family archive powered by
[gene_archive](https://github.com/igormel81/gene_archive): parish registers, revision lists, WWI and WWII databases,
repression files, emigration records — and every trap we fell into along the way.

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

## Why use it

| Without it | With genealogy-mcp |
|---|---|
| The assistant names two or three famous websites | 79 sources chosen by country, years and kind of record, each with "how to search it well" |
| Searches one spelling | Spelling variants, pre-1918 orthography, male/female forms, 9 transliteration systems, given-name equivalents (Иван = Іоаннъ = Jan = Johann = Juan) |
| Invented or broken URLs | Ready search links built from tested URL templates; a weekly job checks every site |
| "This is probably your ancestor" | An explicit evidence rule: a namesake is not a relative |
| Dates taken at face value | Julian ↔ Gregorian, birth years from ages with realistic drift, dates normalised to GEDCOM |
| Generic advice | Record guides: parish registers, confession lists, revision lists, household books, WWI/WWII, repression files, passenger lists, censuses, European civil registration, Latin American records |
| You write to archives from scratch | Request drafts for Russian ZAGS, state, military and FSB archives, and for any archive in English, Spanish or Portuguese |
| It forgets everything between chats | A research project that remembers people, sources, leads and every search |
| It cannot read old numbers and dates | Church Slavonic numerals, church feasts, Julian, Hebrew and French Republican calendars |
| "Search FamilySearch for your name" | Live search in the Internet Archive full text, WikiTree, Open Archives and Wikidata place history |
| DNA matches are a mystery | Shared cM → the relationships it fits |

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
  Riksarkivet, Digitalarkivet, Danish Family Search, HisKi, Hungaricana.
- **The Americas:** FamilySearch Latin America, AGN Mexico, Arquivo Nacional and Museu da Imigração (Brazil),
  Hemeroteca Digital, CEMLA and AGN (Argentina), Archivo Nacional (Chile), NARA, Ellis Island, Chronicling America.

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
| `project_view`, `project_save`, `project_log`, `project_transfer` | The research project between conversations: people, families, sources, leads, the search log, GEDCOM import/export |
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
