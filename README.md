# kg-builder

Turns technical documents (PDF datasheets, user guides, app notes) into a cited knowledge graph and an interactive explorer.

Current demo corpus: six TI C2000 motor-control documents (SPRUJ26A, SPRUIO7A, SPRT755, SSZT350, SSZT464, SSZT496) → 589 entities, 1,519 relations, each with page-level citations.

## Layout

```
SCHEMA.md            entity types, relation types, ID conventions (the ontology)
sources/             PDFs + per-page text (not in git; run kg/fetch_sources.sh)
extractions/         one JSON per extraction job (entities + relations + citations)
kg/extract.py        Claude-based extractor: PDF -> extractions/<doc>_pNNN-NNN.json
kg/build.py          merge + normalise IDs + dedupe -> graph/graph.json, graph.graphml, report.md
graph/               merged outputs
viewer/index.html    explorer (search, type/doc filters, neighbourhood focus, path finder, PDF page links)
```

## Pipeline

```bash
pip install anthropic
python3 kg/extract.py sources/newdoc.pdf --title "New document title"
python3 kg/build.py extractions graph
cp graph/graph.json viewer/graph.json
python3 -m http.server -d viewer 8000
```

`extract.py` sends 20-page chunks with SCHEMA.md as a cached system prompt and a JSON-schema-constrained output, so every relation type and entity type is from the ontology. Re-running skips chunks already extracted.

`build.py` normalises IDs (alias table + `TMS320` prefix stripping), merges entities across jobs (longest description, union of aliases/citations, majority-vote type), dedupes relations by (source, type, target) while keeping all evidence, and reports type conflicts and dangling endpoints in `graph/report.md`.

## Known limits

- Entity resolution is alias-table based; near-duplicates are found by `label/alias` collision and added to `ALIASES` by hand.
- The demo extractions were produced by parallel Claude agents following SCHEMA.md; `extract.py` automates the same step but has not yet been run against the API in this environment (no key here).
