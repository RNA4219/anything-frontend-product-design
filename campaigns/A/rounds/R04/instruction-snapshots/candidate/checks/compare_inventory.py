#!/usr/bin/env python3
"""Compare normalized IA snapshots; comparison success never approves a migration.

Standard library only. No network, model call, source mutation or inferred mapping.
"""
import argparse
import hashlib
import json
from pathlib import Path


FIELDS = {
    "concepts": {"required": {"id", "label", "axis"},
                 "optional": {"scope", "parent_ids"}, "sets": {"parent_ids"}},
    "records": {"required": {"id", "label", "scope", "roles", "concept_ids"},
                "optional": set(), "sets": {"roles", "concept_ids"}},
    "entries": {"required": {"id", "path", "role", "scope", "concept_ids"},
                "optional": set(), "sets": {"concept_ids"}},
}
ROOT_FIELDS = {"case_id", "revision", "basis_revision", *FIELDS}


def inspect_snapshot(value, side):
    errors, ignored, indexed = [], set(), {}

    def error(path, message):
        errors.append({"location": path, "message": message})

    if not isinstance(value, dict):
        error(side, "Snapshot must be an object")
        return {}, errors, [], []
    for key in ["case_id", "revision"]:
        if not isinstance(value.get(key), str) or not value[key].strip():
            error(side + "." + key, "Nonempty string required")
    if "basis_revision" in value and (not isinstance(value["basis_revision"], str)
                                      or not value["basis_revision"].strip()):
        error(side + ".basis_revision", "Nonempty string required when supplied")
    ignored.update(side + "." + key for key in value.keys() - ROOT_FIELDS)
    for collection, spec in FIELDS.items():
        rows = value.get(collection)
        indexed[collection] = {}
        if not isinstance(rows, list):
            error(side + "." + collection, "Array required, including [] when empty")
            continue
        known = spec["required"] | spec["optional"]
        for position, row in enumerate(rows):
            loc = f"{side}.{collection}[{position}]"
            if not isinstance(row, dict):
                error(loc, "Object required")
                continue
            row_errors = len(errors)
            for key in spec["required"] - row.keys():
                error(loc + "." + key, "Required field missing")
            for key in known & row.keys():
                v = row[key]
                if key in spec["sets"]:
                    if not isinstance(v, list) or any(not isinstance(x, str) or not x.strip() for x in v):
                        error(loc + "." + key, "Array of nonempty strings required")
                    elif len(v) != len(set(v)):
                        error(loc + "." + key, "Repeated membership is ambiguous input; normalize explicitly")
                elif not isinstance(v, str) or not v.strip():
                    error(loc + "." + key, "Nonempty string required")
            ignored.update(f"{side}.{collection}[].{key}" for key in row.keys() - known)
            if len(errors) != row_errors:
                continue
            if row["id"] in indexed[collection]:
                error(loc + ".id", "Duplicate ID: " + row["id"])
                continue
            indexed[collection][row["id"]] = {
                k: sorted(row[k]) if k in spec["sets"] else row[k]
                for k in known & row.keys()
            }
    # An outside reference may indicate an intentionally partial snapshot. Report
    # it without inventing a missing node or deciding it is a product defect.
    outside = []
    concepts = indexed.get("concepts", {})
    for collection, key in [("records", "concept_ids"), ("entries", "concept_ids"),
                            ("concepts", "parent_ids")]:
        for item_id, row in indexed.get(collection, {}).items():
            for ref in row.get(key, []):
                if ref not in concepts:
                    outside.append({"location": f"{side}.{collection}.{item_id}.{key}", "id": ref})
    return indexed, errors, sorted(ignored), outside


def compare(before, after):
    old, e1, ignored1, outside1 = inspect_snapshot(before, "before")
    new, e2, ignored2, outside2 = inspect_snapshot(after, "after")
    if e1 or e2:
        return {"status": "INVALID_INPUT", "decision": "NOT_EVALUATED", "errors": e1 + e2,
                "unexamined_fields": ignored1 + ignored2}
    differences, counts = {}, {}
    for collection in FIELDS:
        left, right = old[collection], new[collection]
        changes = []
        for item_id in sorted(left.keys() & right.keys()):
            for field in sorted((left[item_id].keys() | right[item_id].keys()) - {"id"}):
                a, b = left[item_id], right[item_id]
                if (field in a) != (field in b) or a.get(field) != b.get(field):
                    changes.append({"id": item_id, "field": field,
                                    "before": {"present": field in a, "value": a.get(field)},
                                    "after": {"present": field in b, "value": b.get(field)}})
        differences[collection] = {"removed_ids": sorted(left.keys() - right.keys()),
                                   "added_ids": sorted(right.keys() - left.keys()),
                                   "changed_fields": changes}
        counts[collection] = {"before": len(left), "after": len(right)}
    warnings = []
    if before["case_id"] != after["case_id"]:
        warnings.append("case_id differs; establish that these snapshots are a meaningful comparison")
    if after.get("basis_revision") != before["revision"]:
        warnings.append("Proposed basis_revision is missing or does not match the supplied before revision")
    has_changes = any(d["removed_ids"] or d["added_ids"] or d["changed_fields"] for d in differences.values())
    if before["revision"] == after["revision"] and has_changes:
        warnings.append("Same declared revision contains different examined data")
    return {
        "status": "COMPARED", "decision": "NOT_EVALUATED",
        "basis": {"before_revision": before["revision"], "after_revision": after["revision"],
                  "proposed_basis_revision": after.get("basis_revision"),
                  "basis_matches": after.get("basis_revision") == before["revision"]},
        "counts": counts, "differences": differences, "input_warnings": warnings,
        "references_not_in_snapshot": outside1 + outside2,
        "unexamined_fields": ignored1 + ignored2,
        "checks_available": {"declared_field_comparison": True, "source_truth": False,
                             "whole_inventory_completeness": False, "semantic_equivalence": False,
                             "change_authorization": False, "runtime_findability": False,
                             "human_effectiveness": False},
        "meaning": "Differences require interpretation against intended changes and scope. Equal counts or no examined-field differences do not establish preservation, authorization or usability.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        old_bytes, new_bytes = args.before.read_bytes(), args.after.read_bytes()
        result = compare(json.loads(old_bytes), json.loads(new_bytes))
        result["input_sha256"] = {"before": hashlib.sha256(old_bytes).hexdigest(),
                                  "after": hashlib.sha256(new_bytes).hexdigest()}
    except (OSError, UnicodeError, ValueError) as err:
        result = {"status": "INVALID_INPUT", "decision": "NOT_EVALUATED", "error": str(err)}
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 2 if result["status"] == "INVALID_INPUT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
