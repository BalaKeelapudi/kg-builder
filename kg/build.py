#!/usr/bin/env python3
"""Merge extraction JSON files into one knowledge graph.

Usage:  python3 kg/build.py [extractions_dir] [out_dir]

Outputs (in out_dir, default ./graph):
  graph.json     merged graph {meta, entities, relations}
  graph.graphml  for Gephi / yEd / Neo4j import
  report.md      counts, type breakdown, hubs, issues found while merging
"""
import json, re, sys, glob, os
from collections import Counter, defaultdict
from xml.sax.saxutils import escape

ENTITY_TYPES = {"Device", "EvaluationKit", "Component", "Peripheral", "Software", "Algorithm",
                "Motor", "Concept", "Feature", "BuildLevel", "Parameter", "Application", "Document"}
REL_TYPES = {"is_a", "part_of", "contains", "based_on", "runs_on", "supports", "uses", "implements",
             "requires", "compatible_with", "connects_to", "estimates", "controls", "configures",
             "measures", "protects", "produces", "input_to", "enables", "precedes", "extends",
             "targets", "documented_in", "alternative_to", "related_to"}

# Known spelling variants -> canonical id (applied after normalisation).
ALIASES = {
    "spruio7": "spruio7a", "spruj26": "spruj26a", "c2000ware_mcsdk_getting_started": "spruio7a",
    "offset_calibration": "adc_offset_calibration", "motor_braking": "braking", "uart": "sci",
    "resource_explorer": "ccs_resource_explorer", "motor_identification": "motor_parameter_identification",
    "fast": "fast_estimator", "fast_observer": "fast_estimator", "instaspin_fast": "fast_estimator",
    "esmo_pll": "esmo", "enhanced_sliding_mode_observer": "esmo", "smo": "esmo",
    "phase_locked_loop": "pll", "space_vector_pwm": "svpwm", "space_vector_modulation": "svpwm",
    "field_oriented_control": "foc", "pi": "pi_controller", "pi_regulator": "pi_controller",
    "maximum_torque_per_ampere": "mtpa", "fw": "field_weakening",
    "ccs": "code_composer_studio", "ccstudio": "code_composer_studio",
    "motor_control_sdk": "motorcontrol_sdk", "c2000ware_motorcontrol_sdk": "motorcontrol_sdk",
    "c2000ware_motor_control_sdk": "motorcontrol_sdk", "mcsdk": "motorcontrol_sdk",
    "universal_lab": "universal_motor_control_lab", "universal_motor_control_project": "universal_motor_control_lab",
    "universal_project": "universal_motor_control_lab",
    "permanent_magnet_synchronous_motor": "pmsm", "brushless_dc_motor": "bldc",
    "ac_induction_motor": "acim", "configurable_logic_block": "clb",
    "comparator_subsystem": "cmpss", "enhanced_pwm": "epwm", "pwm": "epwm",
    "enhanced_qep": "eqep", "qep": "eqep", "enhanced_capture": "ecap",
    "fast_serial_interface": "fsi", "control_law_accelerator": "cla",
    "buildlevel_level1": "build_level_1", "buildlevel_level2": "build_level_2",
    "buildlevel_level3": "build_level_3", "buildlevel_level4": "build_level_4",
    "build_level1": "build_level_1", "build_level2": "build_level_2",
    "build_level3": "build_level_3", "build_level4": "build_level_4",
    "level_1": "build_level_1", "level_2": "build_level_2", "level_3": "build_level_3", "level_4": "build_level_4",
}


def norm_id(raw):
    s = raw.lower().replace("™", "").replace("®", "")
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    s = re.sub(r"^tms320_?", "", s)
    return ALIASES.get(s, s)


def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "extractions"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "graph"
    os.makedirs(out_dir, exist_ok=True)
    issues = []
    ents, rels = {}, {}
    type_votes = defaultdict(Counter)
    files = sorted(glob.glob(os.path.join(src_dir, "*.json")))

    def srcs_of(x):
        return {(s["doc"].lower().replace("spruio7", "spruio7a").replace("spruio7aa", "spruio7a"), int(s["page"]))
                for s in x.get("sources", []) if "doc" in s and "page" in s}

    for f in files:
        data = json.load(open(f))
        for e in data.get("entities", []):
            eid = norm_id(e["id"])
            t = e.get("type", "Concept")
            if t not in ENTITY_TYPES:
                issues.append(f"{os.path.basename(f)}: unknown type {t!r} for {eid} -> Concept")
                t = "Concept"
            type_votes[eid][t] += 1 + len(e.get("sources", []))
            cur = ents.setdefault(eid, {"id": eid, "label": e.get("label") or eid, "description": "",
                                        "aliases": set(), "properties": {}, "sources": set(), "files": set()})
            desc = (e.get("description") or "").strip()
            if len(desc) > len(cur["description"]):
                cur["description"] = desc
            for a in e.get("aliases", []) or []:
                cur["aliases"].add(a)
            if e.get("label") and e["label"] != cur["label"]:
                cur["aliases"].add(e["label"])
            for k, v in (e.get("properties") or {}).items():
                cur["properties"].setdefault(k, v)
            cur["sources"] |= srcs_of(e)
            cur["files"].add(os.path.basename(f))
        for r in data.get("relations", []):
            s, t, ty = norm_id(r["source"]), norm_id(r["target"]), r.get("type", "related_to")
            if ty not in REL_TYPES:
                issues.append(f"{os.path.basename(f)}: unknown relation {ty!r} ({s}->{t}) -> related_to")
                ty = "related_to"
            if s == t:
                continue
            key = (s, t, ty)
            cur = rels.setdefault(key, {"source": s, "target": t, "type": ty, "evidence": [], "sources": set()})
            ev = (r.get("evidence") or "").strip()
            if ev and ev not in cur["evidence"]:
                cur["evidence"].append(ev)
            cur["sources"] |= srcs_of(r)

    for eid, votes in type_votes.items():
        ents[eid]["type"] = votes.most_common(1)[0][0]
        if len(votes) > 1:
            issues.append(f"type conflict for {eid}: {dict(votes)} -> {ents[eid]['type']}")
        ents[eid]["aliases"].discard(ents[eid]["label"])

    for (s, t, ty) in list(rels):
        for x in (s, t):
            if x not in ents:
                issues.append(f"dangling endpoint {x} in {s} -{ty}-> {t}; created stub")
                ents[x] = {"id": x, "label": x, "type": "Concept", "description": "", "aliases": set(),
                           "properties": {}, "sources": set(), "files": set()}

    degree = Counter()
    for (s, t, _) in rels:
        degree[s] += 1
        degree[t] += 1
    docs = sorted({d for e in ents.values() for d, _ in e["sources"]})

    entities = []
    for e in sorted(ents.values(), key=lambda x: x["id"]):
        entities.append({**{k: e[k] for k in ("id", "label", "type", "description", "properties")},
                         "aliases": sorted(e["aliases"]), "degree": degree[e["id"]],
                         "sources": [{"doc": d, "page": p} for d, p in sorted(e["sources"])]})
    relations = [{**{k: r[k] for k in ("source", "target", "type", "evidence")},
                  "sources": [{"doc": d, "page": p} for d, p in sorted(r["sources"])]}
                 for r in sorted(rels.values(), key=lambda r: (r["source"], r["type"], r["target"]))]

    meta = {"documents": docs, "entity_count": len(entities), "relation_count": len(relations),
            "extraction_files": [os.path.basename(f) for f in files]}
    json.dump({"meta": meta, "entities": entities, "relations": relations},
              open(os.path.join(out_dir, "graph.json"), "w"), indent=1, ensure_ascii=False)

    # GraphML
    g = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
         '<key id="label" for="node" attr.name="label" attr.type="string"/>',
         '<key id="type" for="node" attr.name="type" attr.type="string"/>',
         '<key id="description" for="node" attr.name="description" attr.type="string"/>',
         '<key id="rel" for="edge" attr.name="type" attr.type="string"/>',
         '<key id="evidence" for="edge" attr.name="evidence" attr.type="string"/>',
         '<graph id="kg" edgedefault="directed">']
    for e in entities:
        g.append(f'<node id="{escape(e["id"])}"><data key="label">{escape(e["label"])}</data>'
                 f'<data key="type">{e["type"]}</data><data key="description">{escape(e["description"])}</data></node>')
    for i, r in enumerate(relations):
        g.append(f'<edge id="e{i}" source="{escape(r["source"])}" target="{escape(r["target"])}">'
                 f'<data key="rel">{r["type"]}</data><data key="evidence">{escape(" | ".join(r["evidence"]))}</data></edge>')
    g += ["</graph>", "</graphml>"]
    open(os.path.join(out_dir, "graph.graphml"), "w").write("\n".join(g))

    tc = Counter(e["type"] for e in entities)
    rc = Counter(r["type"] for r in relations)
    isolated = [e["id"] for e in entities if e["degree"] == 0]
    lines = [f"# Knowledge graph build report", "",
             f"- Extraction files: {len(files)}", f"- Documents: {', '.join(docs)}",
             f"- Entities: {len(entities)}", f"- Relations: {len(relations)}",
             f"- Isolated entities: {len(isolated)}", "", "## Entity types", ""]
    lines += [f"- {t}: {n}" for t, n in tc.most_common()]
    lines += ["", "## Relation types", ""] + [f"- {t}: {n}" for t, n in rc.most_common()]
    lines += ["", "## Top hubs", ""] + [f"- {ents[i]['label']} ({i}): {d}" for i, d in degree.most_common(25)]
    lines += ["", "## Merge issues", ""] + [f"- {x}" for x in issues] + (["- none"] if not issues else [])
    if isolated:
        lines += ["", "## Isolated", ""] + [f"- {x}" for x in isolated]
    open(os.path.join(out_dir, "report.md"), "w").write("\n".join(lines) + "\n")
    print(f"{len(entities)} entities, {len(relations)} relations, {len(issues)} issues -> {out_dir}/")


if __name__ == "__main__":
    main()
