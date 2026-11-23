#!/usr/bin/env python3
"""Dependency-free structural checks for a Product Design / IA plan.

No model calls, no network access, no writes except the explicit --output.
PASS is a structural result, not a usability or promotion claim.
"""
import argparse
import json
from pathlib import Path


def validate(brief, plan):
    issues = []

    def add(code, location, symptom, category="information_architecture", severity="error"):
        issues.append(dict(code=code, location=location, symptom=symptom,
                           category=category, severity=severity))

    def objects(doc, key, fields):
        value = doc.get(key)
        if not isinstance(value, list):
            add("SHAPE", key, "Expected an array", "implementation")
            return []
        valid = []
        for i, obj in enumerate(value):
            if not isinstance(obj, dict) or any(k not in obj or not isinstance(obj[k], t) for k, t in fields.items()):
                add("SHAPE", f"{key}[{i}]", "Missing field or wrong value type", "implementation")
            else:
                valid.append(obj)
        return valid

    if not isinstance(brief, dict) or not isinstance(plan, dict):
        return {"status":"FAIL", "issues":[{"code":"SHAPE", "location":"$", "symptom":"Expected JSON objects", "category":"implementation", "severity":"error"}]}

    for field in ("schema_version", "case_id", "visual_intent_id"):
        if not isinstance(plan.get(field), str):
            add("SHAPE", field, "Expected a string", "implementation")
    if plan.get("schema_version") != "1.0":
        add("VERSION", "schema_version", "Unsupported contract version", "implementation")
    if plan.get("case_id") != brief.get("case_id"):
        add("CASE_MISMATCH", "case_id", "Plan and brief identify different cases", "function")
    if not isinstance(brief.get("visual_intent"), dict) or plan.get("visual_intent_id") != brief.get("visual_intent", {}).get("id"):
        add("VISUAL_INTENT", "visual_intent_id", "Existing visual intent was not preserved", "visual")

    roles = objects(brief, "roles", {"id":str, "label":str})
    goals = objects(brief, "goals", {"id":str, "role":str, "outcome":str, "priority":str, "needed_information":list})
    requirements = objects(brief, "requirements", {"id":str, "goal_ids":list, "mandatory":bool, "statement":str})
    requests = objects(brief, "feature_requests", {"id":str, "label":str, "object":str, "outcome":str, "roles":list, "goal_ids":list, "requirement_ids":list, "dependencies":list, "mandatory":bool})
    features = objects(plan, "features", {"id":str, "label":str, "disposition":str, "object":str, "outcome":str, "roles":list, "goal_ids":list, "requirement_ids":list, "dependencies":list, "reason":str, "priority":str, "priority_basis":str})
    screens = objects(plan, "screens", {"id":str, "title":str, "purpose":str, "goal_ids":list, "feature_ids":list, "roles":list, "entry_for":list, "information":list})
    nav = objects(plan, "navigation", {"from":str, "to":str, "label":str, "roles":list, "kind":str, "rationale":str})
    routes = objects(plan, "goal_routes", {"goal_id":str, "start_screen":str, "target_screen":str, "notes":str})
    unresolved = objects(plan, "unresolved", {"id":str, "category":str, "owner":str, "impact":str, "blocking":bool, "question":str})
    if not isinstance(plan.get("decision_notes"), list) or any(not isinstance(x, str) for x in plan.get("decision_notes", [])):
        add("SHAPE", "decision_notes", "Expected an array of strings", "implementation")

    # Validate list members before using them as dict/set keys. Invalid input must not crash.
    for group, fields in ((goals,["needed_information"]),(requirements,["goal_ids"]),(requests,["roles","goal_ids","requirement_ids","dependencies"]),(features,["roles","goal_ids","requirement_ids","dependencies"]),(screens,["goal_ids","feature_ids","roles","entry_for"]),(nav,["roles"])):
        for obj in group:
            for field in fields:
                if any(not isinstance(v, str) or not v.strip() for v in obj[field]):
                    add("SHAPE", f"{obj.get('id',obj.get('from'))}.{field}", "Expected nonempty string IDs", "implementation")
    if any(x["code"] == "SHAPE" for x in issues):
        return {"status":"FAIL", "issues":issues}

    def indexed(items, name):
        out = {}
        for obj in items:
            if not obj["id"].strip() or obj["id"] in out:
                add("DUPLICATE_ID", name, "Empty or duplicate ID", "implementation")
            out[obj["id"]] = obj
        return out

    rr, gg, qq, ff, ss = indexed(roles,"roles"), indexed(goals,"goals"), indexed(requirements,"requirements"), indexed(features,"features"), indexed(screens,"screens")
    reqs = indexed(requests,"feature_requests")
    for g in goals:
        if g["priority"] not in ("must", "should", "could"):
            add("ENUM",g["id"],"Input goal priority must be must/should/could","implementation")
    for r in requirements:
        for gid in r["goal_ids"]:
            if gid not in gg: add("UNKNOWN_GOAL",r["id"],gid,"function")
    for source in requests:
        for field, registry, code in (("roles",rr,"UNKNOWN_ROLE"),("goal_ids",gg,"UNKNOWN_GOAL"),("requirement_ids",qq,"UNKNOWN_REQUIREMENT"),("dependencies",reqs,"UNKNOWN_DEPENDENCY")):
            for value in source[field]:
                if value not in registry: add(code,source["id"],value,"function")
    for role, source in [(g["role"],g["id"]) for g in goals]:
        if role not in rr:
            add("UNKNOWN_ROLE",source,role,"function")
    for feature_id in reqs:
        if feature_id not in ff:
            add("UNACCOUNTED_FEATURE",feature_id,"Input feature has no keep/merge/defer/remove decision","function")

    def resolve(feature_id):
        seen = set()
        while feature_id in ff:
            if feature_id in seen:
                return None
            seen.add(feature_id)
            f = ff[feature_id]
            if f["disposition"] == "keep":
                return feature_id
            if f["disposition"] != "merge" or not isinstance(f.get("target"), str):
                return None
            feature_id = f["target"]
        return None

    for f in features:
        loc = f"features.{f['id']}"
        if f["id"] not in reqs and not f["id"].startswith("add_"):
            add("UNDECLARED_FEATURE",loc,"Additional feature ID must start with add_","function")
        if f["disposition"] not in ("keep","merge","defer","remove") or f["priority"] not in ("required","high","medium","low"):
            add("ENUM",loc,"Invalid disposition or priority","implementation")
        if not f["reason"].strip() or not f["priority_basis"].strip():
            add("NO_REASON",loc,"Decision and priority require reasons","function")
        if "target" not in f or (f["disposition"] != "merge" and f.get("target") is not None):
            add("MERGE_TARGET",loc,"Non-merge feature must have null target","function")
        for role in f["roles"]:
            if role not in rr: add("UNKNOWN_ROLE",loc,role,"function")
        for goal in f["goal_ids"]:
            if goal not in gg: add("UNKNOWN_GOAL",loc,goal,"function")
        for req in f["requirement_ids"]:
            if req not in qq: add("UNKNOWN_REQUIREMENT",loc,req,"function")
        target = resolve(f["id"])
        if f["disposition"] == "merge":
            if target is None:
                add("MERGE_CYCLE_OR_DEAD_TARGET",loc,"Merge must resolve to a kept canonical feature","function")
            elif any(f[k] != ff[target][k] for k in ("object","outcome")) or set(f["roles"]) != set(ff[target]["roles"]):
                add("MERGE_SEMANTICS",loc,"Object, outcome and roles differ; use shared screens instead","function")
            elif not set(f["goal_ids"]).issubset(ff[target]["goal_ids"]) or not set(f["requirement_ids"]).issubset(ff[target]["requirement_ids"]):
                add("MERGE_LOST_OBLIGATION",loc,"Canonical target must preserve goals and requirements","function")
        if f["id"] in reqs and reqs[f["id"]]["mandatory"] and target is None:
            add("MANDATORY_FEATURE_LOST",loc,"Required feature was deferred/removed or merged to a dead target","function")
        if target:
            original = reqs.get(f["id"], {})
            if original and set(ff[target]["roles"]) - set(original["roles"]):
                add("ORIGIN_ROLE_EXPANSION",loc,"Canonical feature expands the input's authorized roles","function")
            if not set(original.get("goal_ids",[])).issubset(ff[target]["goal_ids"]) or not set(original.get("requirement_ids",[])).issubset(ff[target]["requirement_ids"]):
                add("ORIGIN_OBLIGATION_LOST",loc,"Canonical target does not preserve the input feature's goals/requirements","function")
            if original and (original["object"] != ff[target]["object"] or original["outcome"] != ff[target]["outcome"] or not set(original["roles"]).issubset(ff[target]["roles"])):
                add("ORIGIN_SEMANTICS_CHANGED",loc,"Input object, outcome or authorized roles changed; semantic review is required","function","hold")
            deps = set(f["dependencies"]) | set(reqs.get(f["id"],{}).get("dependencies",[]))
            for dep in deps:
                if resolve(dep) is None:
                    add("DEPENDENCY_LOST",loc,f"Active feature depends on unavailable {dep}","function")
        if f["disposition"] == "keep" and not f["goal_ids"] and not f["requirement_ids"]:
            add("UNTRACED_FEATURE",loc,"Kept feature has no goal or enabling requirement","function")

    kept = [f for f in features if f["disposition"] == "keep"]
    for r in requirements:
        if r["mandatory"] and not any(r["id"] in f["requirement_ids"] for f in kept):
            add("MISSING_REQUIREMENT",r["id"],"Mandatory requirement has no kept capability","function")
    for g in goals:
        if g["priority"] == "must" and not any(g["id"] in f["goal_ids"] and g["role"] in f["roles"] for f in kept):
            add("MISSING_GOAL",g["id"],"Must goal has no usable capability","function")

    for s in screens:
        loc = f"screens.{s['id']}"
        if not s["title"].strip() or not s["purpose"].strip(): add("SCREEN_PURPOSE",loc,"Screen needs a title and decision purpose")
        for role in s["roles"]:
            if role not in rr: add("UNKNOWN_ROLE",loc,role)
        if not set(s["entry_for"]).issubset(s["roles"]): add("ENTRY_ROLE",loc,"Entry role cannot access screen")
        for g in s["goal_ids"]:
            if g not in gg: add("UNKNOWN_GOAL",loc,g)
        for fid in s["feature_ids"]:
            if fid not in ff or ff[fid]["disposition"] != "keep": add("NONCANONICAL_SCREEN_FEATURE",loc,fid)
            elif not set(ff[fid]["roles"]).intersection(s["roles"]): add("FEATURE_ROLE",loc,fid)
        seen_info = set()
        for item in s["information"]:
            if not isinstance(item,dict) or not isinstance(item.get("id"),str) or item.get("visibility") not in ("primary","secondary") or not isinstance(item.get("reason"),str):
                add("SHAPE",loc+".information","Invalid information record","implementation")
                continue
            if item["id"] in seen_info: add("DUPLICATE_INFORMATION",loc,item["id"])
            seen_info.add(item["id"])
    for f in kept:
        if not any(f["id"] in s["feature_ids"] for s in screens):
            add("UNPLACED_FEATURE",f["id"],"Kept capability has no owning screen")

    edges = []
    for i,n in enumerate(nav):
        loc = f"navigation[{i}]"
        if n["from"] not in ss or n["to"] not in ss:
            add("DANGLING_NAV",loc,"Navigation endpoint does not exist")
            continue
        if n["kind"] not in ("global","local","contextual") or not n["label"].strip() or not n["rationale"].strip():
            add("NAV_LABEL",loc,"Navigation needs kind, label and rationale")
        if not n["roles"] or not set(n["roles"]).issubset(set(ss[n["from"]]["roles"]) & set(ss[n["to"]]["roles"])):
            add("NAV_ROLE_LEAK",loc,"Navigation offers a destination unavailable to a listed role")
        for old in nav[:i]:
            if n["from"] == old["from"] and n["label"].strip().casefold() == old["label"].strip().casefold() and n["to"] != old["to"] and set(n["roles"]) & set(old["roles"]):
                add("AMBIGUOUS_SIBLING_LABEL",loc,"Same label points to different sibling destinations")
        edges.append(n)

    def reachable(start, role):
        visited, pending = set(), [start]
        while pending:
            cur = pending.pop()
            if cur in visited or cur not in ss or role not in ss[cur]["roles"]: continue
            visited.add(cur)
            pending.extend(n["to"] for n in edges if n["from"] == cur and role in n["roles"])
        return visited

    for g in goals:
        matching = [r for r in routes if r["goal_id"] == g["id"]]
        if g["priority"] == "must" and not matching:
            add("MISSING_GOAL_ROUTE",g["id"],"Must goal has no entry and decision destination")
        for route in matching:
            start, end, role = route["start_screen"],route["target_screen"],g["role"]
            if start not in ss or role not in ss[start]["entry_for"]:
                add("INVALID_START",g["id"],"Route must start at a role's declared entry")
            if end not in reachable(start,role):
                add("UNREACHABLE_GOAL",g["id"],"Target is not reachable for the goal's role")
            if end not in ss: continue
            if g["id"] not in ss[end]["goal_ids"]:
                add("SCREEN_GOAL_MISMATCH",g["id"],"Target screen does not own goal")
            info = {v["id"] for v in ss[end]["information"] if isinstance(v,dict) and isinstance(v.get("id"),str) and v.get("visibility") == "primary"}
            if g["priority"] == "must":
                for missing in set(g["needed_information"]) - info:
                    add("HIDDEN_DECISION_INFORMATION",g["id"],f"Required information {missing} missing or secondary at decision destination")
    for route in routes:
        if route["goal_id"] not in gg: add("UNKNOWN_GOAL","goal_routes",route["goal_id"])
    for u in unresolved:
        if u["category"] not in ("function","information_architecture","interaction","visual","implementation") or u["owner"] not in ("A","B","C","D","product"):
            add("ENUM",u["id"],"Unknown issue category or owner","implementation")
        if u["blocking"]:
            add("UNRESOLVED_BLOCKER",u["id"],u["impact"],u["category"],"hold")

    status = "FAIL" if any(i["severity"] == "error" for i in issues) else "HOLD" if any(i["severity"] == "hold" for i in issues) else "PASS"
    return {"status":status,"issues":issues,"counts":{"goals":len(goals),"features":len(features),"kept_features":len(kept),"screens":len(screens),"navigation_edges":len(nav)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief",required=True,type=Path)
    parser.add_argument("--plan",required=True,type=Path)
    parser.add_argument("--output",type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.brief.read_text()),json.loads(args.plan.read_text()))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        result = {"status":"INVALID_INPUT","error":str(error)}
    rendered = json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(rendered,encoding="utf-8")
    print(rendered,end="")
    return 0 if result["status"] == "PASS" else 2 if result["status"] == "INVALID_INPUT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
