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

Everything runs on your computer. The server makes no network requests: it does not see your searches and sends
nothing anywhere.

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

You need [uv](https://docs.astral.sh/uv/getting-started/installation/) (it fetches Python and the package by itself).

**Claude Desktop** — Settings → Developer → Edit Config, add:

```json
{
  "mcpServers": {
    "genealogy": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/igormel81/genealogy-mcp", "genealogy-mcp"]
    }
  }
}
```

**Claude Code:**

```sh
claude mcp add genealogy -- uvx --from git+https://github.com/igormel81/genealogy-mcp genealogy-mcp
```

**Cursor** (`~/.cursor/mcp.json`), **Windsurf**, **Cline** — the same `mcpServers` block as for Claude Desktop.
**VS Code** (`.vscode/mcp.json`): `{"servers": {"genealogy": {"command": "uvx", "args": [ …same… ]}}}`.

**Clients that connect over HTTP** (ChatGPT connectors, remote agents): run
`genealogy-mcp --http --host 0.0.0.0 --port 8000` behind HTTPS and add `https://your-host/mcp`.
In HTTP mode `audit_tree` takes the GEDCOM text only, never a file path.

Once the package is on PyPI, `uvx genealogy-mcp` is enough.

## Tools

| Tool | What it does |
|---|---|
| `plan_research` | A step-by-step plan for a country and period: which records exist, guides, sources in order |
| `find_sources` | Sources by country/region (`europe`, `latin_america`, `russian_empire`…), years and record kind |
| `source_details` | One source: coverage, access, how to search |
| `search_links` | Ready search URLs for a name and its variants |
| `name_variants` | Spelling, old orthography, gendered forms, transliterations, given-name equivalents, patronymics |
| `normalize_date` | "около 1899", "9 de octubre de 1899" → `ABT 1899`, `9 OCT 1899` |
| `convert_calendar` | Julian ↔ Gregorian |
| `birth_year_from_age` | The birth-year range from an age in a record |
| `kinship` | The name of a relation in ru/en/ro, with the expected DNA share |
| `check_match` | Is a found record our person? A verdict with every fact compared |
| `audit_tree` | Impossible facts, duplicates and gaps in a GEDCOM or `family_tree.json` |
| `draft_archive_request` | A request letter to a registry office or archive |
| `record_guide` | How to read and find a kind of record |
| `glossary` | Old Russian record terms explained |

**Resources:** `genealogy://sources` (the catalogue), `genealogy://guide/research/{en|ru}` (a full research guide),
`genealogy://guide/prompts/{en|ru}` (ready requests for each step), `genealogy://records/{topic}`, `genealogy://glossary`.
**Prompts:** start research, check a find, transcribe a record, write to an archive.

## Privacy and honesty

- Nothing leaves your machine; the server has no network code. The assistant you use is a separate service with its
  own privacy policy — think before pasting details about living people.
- Letters are drafts: you check and send them.
- The rules the assistant gets: cite the original, keep conflicting versions, mark guesses as "probably", never link a
  namesake without evidence.

## Contributing

A source is missing or a link moved? Edit `tools/make_sources.py`, run `python3 tools/make_sources.py` and
`python3 -m unittest discover tests`, open a pull request. Record guides live in `src/genealogy_mcp/guides.py`.

## See also

- [gene_archive](https://github.com/igormel81/gene_archive) — an open-source engine for a family archive website:
  tree, stories, documents, map, GEDCOM, an online editor and relatives' comments.

MIT License.
