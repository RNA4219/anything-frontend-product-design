#!/usr/bin/env python3
"""Dependency-free structural checks for a Product Design / IA plan.

No model calls, no network access, no writes except the explicit --output.
PASS is a structural result, not a usability or promotion claim.
"""
import argparse
import json
from pathlib import Path


def validate_context(brief, plan, add):
    """Version 1.1 context/retirement checks. Does not infer evidence meaning."""
    def string_list(value):
        return isinstance(value, list) and all(isinstance(x, str) and x.strip() for x in value)

    requests = {x['id']: x for x in brief['feature_requests']}
    features = {x['id']: x for x in plan['features']}
    records = brief.get('evidence')
    if not isinstance(records, list):
        add('CONTEXT_SHAPE', 'brief.evidence', 'Version 1.1 requires an evidence array', 'function')
        return
    evidence, malformed = {}, False
    for i, e in enumerate(records):
        loc = f'brief.evidence[{i}]'
        if (not isinstance(e, dict) or not all(isinstance(e.get(k), str) and e[k].strip()
                for k in ('id', 'kind', 'statement', 'coverage', 'coverage_status'))):
            add('CONTEXT_SHAPE', loc, 'Evidence needs typed identity, claim and coverage', 'function')
            malformed = True
            continue
        if e['id'] in evidence or e['kind'] not in ('requirement', 'observation', 'assumption', 'unknown') or e['coverage_status'] not in ('verified', 'partial', 'unknown'):
            add('CONTEXT_SHAPE', loc, 'Duplicate evidence ID or invalid evidence classification', 'function')
            malformed = True
        evidence[e['id']] = e
    for prefix, group in [('brief.feature_requests', requests), ('features', features)]:
        for fid, f in group.items():
            loc = f'{prefix}.{fid}'
            if not isinstance(f.get('scope'), str) or not f['scope'].strip() or not string_list(f.get('context_constraints')) or not string_list(f.get('evidence_refs')):
                add('CONTEXT_SHAPE', loc, 'Scope, context constraints and evidence references are required', 'function')
                malformed = True
                continue
            if prefix.startswith('brief') and (f.get('lifecycle') not in ('existing', 'proposed') or f.get('availability') not in ('available', 'partial', 'planned', 'unknown')):
                add('CONTEXT_SHAPE', loc, 'Lifecycle and current availability are required', 'function')
                malformed = True
            for ref in f['evidence_refs']:
                if ref not in evidence:
                    add('UNKNOWN_EVIDENCE', loc, ref, 'function')
                    malformed = True
    if malformed:
        return

    def resolve(fid):
        seen = set()
        while isinstance(fid, str) and fid in features and fid not in seen:
            seen.add(fid)
            f = features[fid]
            if f['disposition'] == 'keep':
                return f
            fid = f.get('target') if f['disposition'] == 'merge' else None
        return None

    def equivalent(source, target, loc, require_known=True):
        if source['scope'] != target['scope']:
            add('SCOPE_CHANGED', loc, 'Canonical or replacement capability changes the input data scope', 'function')
        if set(source['context_constraints']) != set(target['context_constraints']):
            add('CONTEXT_CHANGED', loc, 'Required account/device/connectivity conditions differ; verify equivalence before substitution', 'function')
        if require_known and source['scope'].casefold() in ('unknown', 'unconfirmed'):
            add('UNKNOWN_SCOPE', loc, 'Unknown scope cannot establish merge/replacement equivalence', 'function', 'hold')

    def current_replacement(source, target, loc, mode):
        actual = requests.get(target['id'])
        if actual is None or actual['availability'] in ('planned', 'unknown'):
            add(mode + '_NOT_CURRENT', loc, 'Proposed or unknown availability is not a current replacement for existing users', 'function', 'hold')
        elif actual['availability'] == 'partial':
            verified = target.get('verified_outcomes', [])
            if not string_list(verified) or source['outcome'] not in verified:
                add('PARTIAL_REPLACEMENT', loc, 'Partial availability requires evidence that this required outcome is supported', 'function', 'hold')

    for fid, source in requests.items():
        if fid not in features:
            continue  # Common checks report missing decisions.
        f, target = features[fid], resolve(fid)
        loc = f'features.{fid}'
        if target:
            equivalent(source, target, loc, f['disposition'] == 'merge')
            # An alias cannot hide its actual source scope by rewriting its own fields.
            equivalent(source, f, loc, f['disposition'] == 'merge')
            if f['disposition'] == 'merge' and source['lifecycle'] == 'existing':
                current_replacement(source, target, loc, 'MERGE')
        if f['disposition'] not in ('remove', 'defer'):
            continue
        if source['lifecycle'] == 'proposed':
            if f['disposition'] == 'defer' and (not isinstance(f.get('revisit'), str) or not f['revisit'].strip()):
                add('REVISIT_MISSING', loc, 'A deferred proposal needs an explicit reconsideration condition', 'function')
            continue
        retirement = f.get('retirement')
        if (not isinstance(retirement, dict) or retirement.get('need_status') not in ('ended', 'continued_elsewhere', 'scope_change', 'unknown')
                or not all(isinstance(retirement.get(k), str) and retirement[k].strip() for k in ('legacy_entry_action', 'data_handling', 'revisit'))
                or 'replacement' not in retirement or (retirement['replacement'] is not None and not isinstance(retirement['replacement'], str))):
            add('RETIREMENT_CONTRACT', loc, 'Existing capability withdrawal needs need status, replacement, old-entry/data disposition and reconsideration condition', 'function')
            continue
        refs = [evidence[r] for r in f['evidence_refs']]
        if retirement['need_status'] == 'unknown' or not any(e['kind'] in ('requirement', 'observation') and e['coverage_status'] == 'verified' for e in refs):
            add('RETIREMENT_EVIDENCE', loc, 'Unknown need or partial/missing evidence cannot establish safe retirement', 'function', 'hold')
        if retirement['need_status'] != 'continued_elsewhere':
            continue
        replacement = resolve(retirement['replacement'])
        if replacement is None:
            add('REPLACEMENT_UNAVAILABLE', loc, 'A continuing need requires a named kept replacement', 'function')
            continue
        equivalent(source, replacement, loc)
        if source['object'] != replacement['object'] or source['outcome'] != replacement['outcome'] or set(source['roles']) != set(replacement['roles']):
            add('REPLACEMENT_SEMANTICS', loc, 'Replacement must preserve required object, outcome and roles', 'function')
        current_replacement(source, replacement, loc, 'REPLACEMENT')


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
    if plan.get("schema_version") not in ("1.0", "1.1"):
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
            elif not set(s["roles"]).issubset(ff[fid]["roles"]):
                add("FEATURE_ROLE",loc,"Screen exposes a capability to a role outside its declared audience: " + fid)
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
                add("AMBIGUOUS_SIBLING_LABEL",loc,"Same short label reaches different destinations; inspect the context available at selection before deciding ambiguity", severity="hold")
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
            if g['priority'] == 'must' and not any(
                    fid in ff and ff[fid]['disposition'] == 'keep' and g['id'] in ff[fid]['goal_ids']
                    and role in ff[fid]['roles'] for fid in ss[end]['feature_ids']):
                add('ROUTE_CAPABILITY_MISSING', g['id'], 'Decision destination needs a kept capability that actually serves this goal and role', 'function')
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

    if plan.get('schema_version') == '1.1':
        validate_context(brief, plan, add)

    status = "FAIL" if any(i["severity"] == "error" for i in issues) else "HOLD" if any(i["severity"] == "hold" for i in issues) else "PASS"
    return {"status":status,"issues":issues,
            "checks_available":{"contract_version":plan.get('schema_version'),
                "context_and_retirement":plan.get('schema_version')=='1.1',
                "navigation_context":False,"search_coverage":False,
                "legacy_entry_identity":False,"rendered_goal_location":False,
                "human_usability":False},
            "counts":{"goals":len(goals),"features":len(features),"kept_features":len(kept),
                      "screens":len(screens),"navigation_edges":len(nav)}}


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
