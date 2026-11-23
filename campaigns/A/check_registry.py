#!/usr/bin/env python3
"""Validate SESSION A registry integrity, not source truth or usability."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

REQUIRED = {"skill_id", "domain", "trigger", "intent", "required_inputs", "decision_rules",
            "procedure", "expected_outputs", "dependencies", "exceptions", "failure_modes",
            "verification", "source_refs", "confidence", "status", "version"}
ARRAYS = {"required_inputs", "decision_rules", "procedure", "expected_outputs", "dependencies",
          "exceptions", "failure_modes", "verification", "source_refs"}
STATUSES = {"DRAFT", "ACCEPT", "REVISE", "HOLD", "REJECT"}


def canonical(url):
    x = urlsplit(url)
    return urlunsplit((x.scheme.lower(), x.netloc.lower(), x.path.rstrip("/"), x.query, ""))


def check(root):
    errors, units, sources, urls = [], {}, {}, {}
    def load(path):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise ValueError("object required")
            return value
        except (OSError, UnicodeError, ValueError) as e:
            errors.append(f"{path.name}: {e}")
            return {}
    for p in sorted((root / "registry/A/sources").glob("*.json")):
        s = load(p)
        sid, url = s.get("source_id"), s.get("url")
        if not isinstance(sid, str) or not sid or sid in sources:
            errors.append(f"{p.name}: missing or duplicate source_id")
            continue
        if not isinstance(url, str) or urlsplit(url).scheme not in {"http", "https"}:
            errors.append(f"{sid}: source URL required")
            continue
        key = canonical(url)
        if key in urls:
            errors.append(f"{sid}: duplicate source URL; consolidate with {urls[key]}")
        urls[key] = sid
        sources[sid] = s
    for p in sorted((root / "registry/A/skills").glob("*.json")):
        u = load(p)
        uid = u.get("skill_id")
        if not isinstance(uid, str) or not uid or uid in units:
            errors.append(f"{p.name}: missing or duplicate skill_id")
            continue
        units[uid] = u
        if REQUIRED - u.keys():
            errors.append(f"{uid}: missing {sorted(REQUIRED - u.keys())}")
        for k in ARRAYS:
            if not isinstance(u.get(k), list) or any(not isinstance(v, str) or not v.strip() for v in u.get(k, [])):
                errors.append(f"{uid}.{k}: string array required")
        for k in {"trigger", "intent", "domain"}:
            if not isinstance(u.get(k), str) or not u[k].strip():
                errors.append(f"{uid}.{k}: nonempty string required")
        if u.get("status") not in STATUSES:
            errors.append(f"{uid}: invalid status")
        if not isinstance(u.get("version"), str) or not re.fullmatch(r"\d+\.\d+\.\d+", u["version"]):
            errors.append(f"{uid}: invalid version")
        for k in ["decision_rules", "procedure", "verification", "source_refs"]:
            if not u.get(k):
                errors.append(f"{uid}.{k}: empty executable contract")
        if u.get("status") == "ACCEPT":
            evidence = u.get("acceptance_evidence", [])
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"{uid}: ACCEPT requires actual acceptance evidence")
            else:
                for rel in evidence:
                    if not isinstance(rel, str):
                        errors.append(f"{uid}: non-string evidence path")
                        continue
                    path = (root / rel).resolve()
                    if not path.is_relative_to(root.resolve()) or not path.is_file():
                        errors.append(f"{uid}: missing or out-of-repository evidence {rel}")
            if not u.get("acceptance_scope"):
                errors.append(f"{uid}: ACCEPT requires bounded acceptance_scope")
    for uid, u in units.items():
        for sid in u.get("source_refs", []):
            if isinstance(sid, str) and sid not in sources:
                errors.append(f"{uid}: unresolved source {sid}")
        for dep in u.get("dependencies", []):
            if isinstance(dep, str) and dep.startswith("A-IU-") and dep not in units:
                errors.append(f"{uid}: unresolved unit dependency {dep}")
    return {"status": "FAIL" if errors else "PASS", "errors": errors,
            "counts": {"units": len(units), "sources": len(sources),
                       "statuses": {s: sum(u.get("status") == s for u in units.values()) for s in sorted(STATUSES)}},
            "scope": "Registry structure and local evidence references only"}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    a = p.parse_args()
    result = check(a.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
