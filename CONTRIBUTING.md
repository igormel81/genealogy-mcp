# Contributing

[Русская версия](CONTRIBUTING.ru.md)

Suggest a source, report a broken link or a bug through the GitHub issue forms, or open a pull request. Record guides and name variants are welcome too.

## Add a source

Edit `tools/make_sources.py`, the source of the catalogue, and add one `add()` call next to related sources. Do not edit the generated `src/genealogy_mcp/data/sources.json` by hand.

```python
add(id, name, url, countries, years, records, access,
    about, about_ru, how, how_ru, search=None)
```

All fields except `search` are required:

| Field | Value |
| --- | --- |
| `id` | Unique, stable source identifier; follow existing lowercase identifiers with underscores. |
| `name` | Name of the archive or database. |
| `url` | Main catalogue or database URL. |
| `countries` | Space-separated uppercase ISO 3166-1 alpha-2 country codes, e.g. `"RU UA BY"`, `"US"`, `"GB"`; `"*"` means worldwide. Use modern codes for historical coverage. |
| `years` | Inclusive coverage tuple `(year_from, year_to)`, e.g. `(1800, 1920)`. |
| `records` | Space-separated keys from `RECORD_KINDS` in `src/genealogy_mcp/sources.py`. |
| `access` | `free`, `free_account` (free but requires sign-in), `paid`, `request` (letter or visit), or `mixed` (partly free). |
| `about`, `about_ru` | Description of the source and its coverage in English and Russian. |
| `how`, `how_ru` | Practical search instructions in English and Russian: indexes vs. images, language, restrictions and pitfalls. |
| `search` | Optional search URL template, or omit it when a direct search link is unavailable. |

The current record keys are `church`, `vital`, `census`, `revision`, `confession`, `household`, `military`, `repression`, `deportation`, `holocaust`, `forced_labour`, `displaced`, `emigration`, `newspapers`, `directories`, `books`, `graves`, `trees`, `catalogs`, `places`, `maps`, `clergy`, `nobility`. Check `RECORD_KINDS` for their meanings and the authoritative list.

A search template can use `{given}`, `{surname}`, `{year_from}`, `{year_to}`, `{place}` and `{q}`. Use only the placeholders the source supports, for example:

```text
https://example.org/search?given={given}&surname={surname}&from={year_from}&to={year_to}&place={place}&q={q}
```

The server URL-encodes substituted values and removes empty query parameters. If `q` is omitted, it combines the given name, surname and place.

Regenerate the catalogue and include both the generator change and the generated JSON in your pull request:

```sh
python3 tools/make_sources.py
```

Do not add sites that violate copyright or sell personal data. Describe access restrictions accurately; do not include credentials or private family records in issues or pull requests.

## Run checks

Use Python 3.10 or newer. From the repository root, create and activate a virtual environment, then install the package and checker:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install . pyflakes
python3 -m unittest discover tests
pyflakes src tests tools
```

Before submitting, review the diff and explain what changed. For catalogue changes, confirm the generator and tests in the pull request template.
