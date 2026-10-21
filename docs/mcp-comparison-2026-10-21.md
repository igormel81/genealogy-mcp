# Genealogy MCP comparison — 21 October 2026

This is a source-code/documentation comparison, not an installation benchmark or an
endorsement of upstream availability. No external MCP was run against a family project,
no credentials were exported, and no family data was sent to another service. The
comparison is against genealogy-mcp 0.6.0 plus the workflow/catalogue changes in this
branch. New catalogue records are references, not live API integrations.

## Comparable implementations

| Project and primary evidence | Useful capability | Gap in this server |
|---|---|---|
| [jasiek/genealogy-plugin](https://github.com/jasiek/genealogy-plugin), [Genealogy Indexer tool](https://github.com/jasiek/genealogy-plugin/blob/master/src/genealogy_mcp/sources/genealogyindexer/tools.py), [provider directories and tests](https://github.com/jasiek/genealogy-plugin/tree/master/src/genealogy_mcp/sources) | Implemented provider-specific search clients for Geneteka, Genealogia w Archiwach, GenBaza, Lubgens, BaSIA, GenPod and Genealogy Indexer. The Indexer tool exposes OCR/Soundex modes, transliteration, collection and date filters, snippets and scan URLs. Configurable intervals/timeouts. | Our five `search_online` providers do not search these indexes. Geneteka exists in our catalogue, but catalogue presence is not a search adapter. |
| [cabout-me/gramps-mcp](https://github.com/cabout-me/gramps-mcp), [registered handlers](https://github.com/cabout-me/gramps-mcp/blob/main/src/gramps_mcp/server.py) | Gramps Web integration; typed searches and handlers for persons, families, events, citations, media and repositories; ancestor/descendant tools. | We can read/write JSON, GEDCOM and gene-archive projects but have no Gramps Web adapter or first-class citation/event/media/repository editing model. |
| [Genealogy-MCP/gedcom-mcp](https://github.com/Genealogy-MCP/gedcom-mcp) ([active upstream](https://gitlab.com/genealogy-mcp/gedcom-mcp)) | Documented structured person filters and ancestor/descendant traversal. Configurable allowed directories, input-size, result-count and depth limits. | Our substring project search and relationship-name calculator are not tree traversal. Local stdio file access lacks a unified optional directory/size policy; retain existing HTTP write/path guards when extending it. These capabilities were compared from its README/tree, not exercised here. |
| [ibarrajo/tree-analyzer-mcp](https://github.com/ibarrajo/tree-analyzer-mcp), [source coverage implementation](https://github.com/ibarrajo/tree-analyzer-mcp/blob/main/src/analysis/source_coverage.py) | Source-gap reports prioritized by generation, duplicates, timelines and circular ancestry. Source coverage code walks parents and groups facts by types. | We have GEDCOM checks and identity screening, but no combined generation-prioritized research-gap report or explicit event-level citation graph. Upstream coverage uses source tags/fact types: that alone does not prove every same-type event has evidence. |
| [JonathanReiss15/familysearch-mcp](https://github.com/JonathanReiss15/familysearch-mcp) | README documents Family Tree person/record search and pedigree tools. | Our FamilySearch references/reading plans are not a FamilySearch search connector. This project's browser-cookie/internal-endpoint method was not tested or adopted; session protection and an approved access method need separate design. |

No upstream code was copied. Similar feature names do not establish equivalent accuracy,
license compatibility or continued operation of the remote provider.

## Sources worth adding next

For the actual research pattern, digitised books and regional archive images matter more
than the number of generic tree websites. The 18–21 October cross-check added the public
library, press, registry and archive references listed in [the workflow audit](research-workflow.md#recent-source-cross-check-1821-october-2026).

Additional candidates surfaced by the comparable MCPs, still **backlog**:

- [Genealogy Indexer](https://genealogyindexer.org): directories, memorial books, military
  and school publications. The provider implementation above supports OCR-tolerant and
  phonetic searches. The provider homepage timed out during this review; verify its
  current search form, conditions and a known-positive example before adding an adapter.
- [GenBaza](https://genbaza.pl): scans and indexes. Its current homepage exposes holdings
  by archive and region; establish item access and citations before implementing search.
- [BaSIA](https://www.basia.famula.pl/en/): western Poland / Greater Poland volunteer
  indexes, linked scans, person/year/place and similarity filters. The provider describes
  free search and optional account features. Valuable for relevant Polish lines.
- [Lubgens](https://regestry.lubgens.eu): Lublin-region index, linked by
  [Geneteka](https://geneteka.genealodzy.pl). This checking connection received 403;
  do not call that a completed search or work around access restrictions.
- Genealogia w Archiwach and GenPod: investigate using the provider clients and
  documentation in genealogy-plugin; confirm the operator, current authoritative URL,
  access terms and supported collections before importing metadata. GenPod's documented
  username/password requirement is not permission to obtain or export credentials.

These are targeted regional complements, not universal alternatives to FamilySearch or
a reason to repeat work in irrelevant countries.

## Prioritized functions

1. **Reliable book/press discovery with page-level evidence.** Investigate documented
   HathiTrust, Gallica, Polona and Iverieli interfaces. A useful result needs edition,
   page/scan URL, matched text, access status and a clear distinction between index,
   snippet and original. Include negative-result scope and per-provider rate limits,
   bounded retries and cache timestamps. Start with one provider and a known-positive
   fixture; an HTML parser without that check is not a completed integration.
2. **Tree navigation and structured search.** Ancestors/descendants/relationship path,
   filters by date range/place/name, bounded depth, pagination and cycle detection.
   Operate on the existing local project; do not require uploading it elsewhere.
3. **Evidence by fact/event.** Link each assertion to document, archive locator, page,
   transcription and confidence; expose unsupported birth/marriage/parentage assertions.
   Keep contradictory evidence visible. Prioritize gaps by the current research
   question and generation, rather than declaring an entire person sourced after one
   citation. This requires a compatible data/schema design, not just another counter.
4. **OCR/transcription workflow.** Local OCR, scan coordinates/page ranges, old spelling
   variants, readable transcript vs literal reading, uncertainty marks and manual review.
   Reuse `project_coverage` for image progress; do not send scans to an external AI by
   default. A plan for reading a film is not OCR capability.
5. **Duplicates and chronology report.** Explain candidate matches with dates, places,
   relatives and conflicting evidence; propose a reviewable merge without merging
   automatically. Reuse existing GEDCOM/identity checks before adding more phonetic
   algorithms. A weighted similarity score is not proof of identity.
6. **Bounded local access.** Optional allowlisted roots, file-size ceilings and consistent
   result/depth limits for local reads, while preserving read-only custom archive folders.
7. **Optional Gramps Web connector.** Start read-only with explicit user configuration;
   citations/events/media should retain original IDs and provenance. Only valuable for
   users who actually keep their tree in Gramps.
8. **FamilySearch connector as a separate design.** Authentication, allowed API scope,
   session storage, provider limits and readonly-first operations must be reviewed before
   implementation. Do not copy another project's internal endpoint or cookie handling
   merely because its README advertises it.

## Changes already implemented from the local-practice audit

- Family → eligible registry action → existing documents → primary records → secondary
  leads; per-project policy, three active questions by default, owner/reading-room stops.
- Required lead next steps and stage-scoped source checks; an unavailable site does not
  complete a stage. Plans expose all relevant catalogue/project references, including
  books and periodicals, rather than silently dropping them by record-kind filtering.
- Read-only access to a custom archive folder and its instructions/resources without
  converting it or writing to it. JSON/GEDCOM changes automatically record corrections
  and research-log entries; gene-archive writes retain its own validation/git/build flow.
- Identity checks reject conflicting given names/localities and do not count the same
  birthplace/residence twice as independent corroboration.
- Catalogue expanded from 124 to 171 entries; date spans not verified from an inventory
  are explicitly unspecified, with access caveats and primary verification references.

The backlog above is not claimed to be implemented by these changes.
