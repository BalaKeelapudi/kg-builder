#!/usr/bin/env python3
"""Extract entities and relations from a PDF with Claude, following SCHEMA.md.

Usage:
  python3 kg/extract.py sources/mydoc.pdf [--doc-id mydoc] [--pages-per-chunk 20]

Writes extractions/<doc_id>_pNNN-NNN.json per chunk; then run kg/build.py to merge.
Requires `pip install anthropic` and an API key (ANTHROPIC_API_KEY or `ant auth login`).
Text comes from `pdftotext -layout` (poppler-utils).
"""
import argparse, json, os, subprocess, sys
import anthropic

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = "claude-opus-5-5"

ENTITY_TYPES = ["Device", "EvaluationKit", "Component", "Peripheral", "Software", "Algorithm", "Motor",
                "Concept", "Feature", "BuildLevel", "Parameter", "Application", "Document"]
REL_TYPES = ["is_a", "part_of", "contains", "based_on", "runs_on", "supports", "uses", "implements", "requires",
             "compatible_with", "connects_to", "estimates", "controls", "configures", "measures", "protects",
             "produces", "input_to", "enables", "precedes", "extends", "targets", "documented_in",
             "alternative_to", "related_to"]
SOURCE = {"type": "object", "properties": {"doc": {"type": "string"}, "page": {"type": "integer"}},
          "required": ["doc", "page"], "additionalProperties": False}
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string"}, "label": {"type": "string"},
                "type": {"type": "string", "enum": ENTITY_TYPES},
                "description": {"type": "string"},
                "aliases": {"type": "array", "items": {"type": "string"}},
                "properties": {"type": "array", "items": {
                    "type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
                    "required": ["key", "value"], "additionalProperties": False}},
                "sources": {"type": "array", "items": SOURCE},
            },
            "required": ["id", "label", "type", "description", "aliases", "properties", "sources"],
            "additionalProperties": False}},
        "relations": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "source": {"type": "string"}, "target": {"type": "string"},
                "type": {"type": "string", "enum": REL_TYPES},
                "evidence": {"type": "string"},
                "sources": {"type": "array", "items": SOURCE},
            },
            "required": ["source", "target", "type", "evidence", "sources"],
            "additionalProperties": False}},
    },
    "required": ["entities", "relations"],
    "additionalProperties": False,
}


def pdf_pages(path):
    text = subprocess.run(["pdftotext", "-layout", path, "-"], check=True, capture_output=True, text=True).stdout
    return text.split("\f")


def extract_chunk(client, schema_md, doc_id, title, pages, first_page):
    body = "\n\n".join(f"<page number=\"{first_page + i}\">\n{p}\n</page>" for i, p in enumerate(pages) if p.strip())
    prompt = (f"Document id: `{doc_id}` — {title}\n"
              f"Extract the knowledge graph for PDF pages {first_page}–{first_page + len(pages) - 1}. "
              f"Cite each fact with doc `{doc_id}` and the page number shown on its <page> tag. "
              f"Return `properties` as a list of key/value pairs.\n\n{body}")
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=64000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
        system=[{"type": "text", "text": "You build a knowledge graph from technical documentation. "
                 "Follow this schema and its ID conventions exactly.\n\n" + schema_md,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise RuntimeError(f"model declined pages {first_page}+: {msg.stop_details}")
    if msg.stop_reason == "max_tokens":
        raise RuntimeError(f"output truncated for pages {first_page}+; lower --pages-per-chunk")
    data = json.loads(next(b.text for b in msg.content if b.type == "text"))
    for e in data["entities"]:  # list of pairs -> dict, matching build.py's input format
        e["properties"] = {p["key"]: p["value"] for p in e["properties"]}
    return data, msg.usage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--doc-id", help="defaults to the file name, e.g. spruj26a")
    ap.add_argument("--title", default="")
    ap.add_argument("--pages-per-chunk", type=int, default=20)
    ap.add_argument("--out", default=os.path.join(ROOT, "extractions"))
    a = ap.parse_args()

    doc_id = (a.doc_id or os.path.splitext(os.path.basename(a.pdf))[0]).lower()
    schema_md = open(os.path.join(ROOT, "SCHEMA.md")).read()
    pages = pdf_pages(a.pdf)
    while pages and not pages[-1].strip():
        pages.pop()
    os.makedirs(a.out, exist_ok=True)
    client = anthropic.Anthropic()

    for start in range(0, len(pages), a.pages_per_chunk):
        chunk = pages[start:start + a.pages_per_chunk]
        lo, hi = start + 1, start + len(chunk)
        out = os.path.join(a.out, f"{doc_id}_p{lo:03d}-{hi:03d}.json")
        if os.path.exists(out):
            print(f"skip {out} (exists)")
            continue
        try:
            data, usage = extract_chunk(client, schema_md, doc_id, a.title, chunk, lo)
        except anthropic.RateLimitError as e:
            sys.exit(f"rate limited on pages {lo}-{hi}; re-run to resume: {e}")
        except anthropic.APIStatusError as e:
            sys.exit(f"API error {e.status_code} on pages {lo}-{hi}: {e.message}")
        except anthropic.APIConnectionError as e:
            sys.exit(f"connection error on pages {lo}-{hi}; re-run to resume: {e}")
        json.dump(data, open(out, "w"), indent=1, ensure_ascii=False)
        print(f"{out}: {len(data['entities'])} entities, {len(data['relations'])} relations "
              f"(in {usage.input_tokens}, out {usage.output_tokens})")


if __name__ == "__main__":
    main()
