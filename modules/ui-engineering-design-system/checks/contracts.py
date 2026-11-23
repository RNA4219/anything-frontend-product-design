#!/usr/bin/env python3
"""Validate declared UI contracts, not rendered DOM or accessibility conformance."""
import argparse
import json
from pathlib import Path

READONLY_TYPES = {"text", "search", "url", "tel", "email", "password", "date",
                  "month", "week", "time", "datetime-local", "number"}
DISABLABLE = {"button", "input", "select", "textarea", "fieldset", "optgroup", "option"}


def check(document):
    findings = []

    def add(path, code, message):
        findings.append({"path": path, "code": code, "severity": "error", "message": message})

    if not isinstance(document, dict) or not isinstance(document.get("components"), list) or not document["components"]:
        add("components", "STRUCTURE", "Provide a nonempty components array.")
        return findings
    seen = set()
    for n, c in enumerate(document["components"]):
        p = f"components[{n}]"
        if not isinstance(c, dict):
            add(p, "STRUCTURE", "Each component must be an object.")
            continue
        cid = c.get("component_id")
        if not isinstance(cid, str) or not cid.strip() or cid in seen:
            add(p + ".component_id", "IDENTITY", "Use a unique nonempty component ID.")
        else:
            seen.add(cid)
        invalid = False
        for key in ("intent", "element", "accessible_name"):
            if not isinstance(c.get(key), str) or not c[key].strip():
                add(p + "." + key, "REQUIRED", "Provide an explicit nonempty string.")
                invalid = True
        for key in ("type", "availability", "mode", "open_method", "close_method", "submit_policy"):
            if key in c and not isinstance(c[key], str):
                add(p + "." + key, "STRUCTURE", "Expected a string.")
                invalid = True
        for key in ("separate_serialization", "background_cleanup_independent", "traps_focus", "unconditional_return"):
            if key in c and not isinstance(c[key], bool):
                add(p + "." + key, "STRUCTURE", "Expected a boolean, not a string or number.")
                invalid = True
        if invalid:
            continue
        intent, tag = c["intent"], c["element"]
        if (intent == "input" or "submit_policy" in c) and c.get("submit_policy") not in ("include", "omit", "not-applicable"):
            add(p + ".submit_policy", "SUBMIT_POLICY", "Declare include, omit, or not-applicable; unknown policies cannot pass.")
        if intent not in ("navigation", "action", "input", "dialog"):
            add(p + ".intent", "INTENT", "Unsupported intent; extend the contract explicitly.")
        if intent == "navigation" and (not isinstance(c.get("destination"), str) or not c["destination"].strip()):
            add(p + ".destination", "DESTINATION", "Navigation requires a destination.")
        if tag == "button" and c.get("type") not in ("button", "submit", "reset"):
            add(p + ".type", "BUTTON_TYPE", "Declare button type to preserve form intent.")
        native = ((intent == "navigation" and tag == "a") or (intent == "action" and tag == "button")
                  or (intent == "input" and tag in ("input", "textarea", "select"))
                  or (intent == "dialog" and tag == "dialog"))
        if not native:
            for key in ("custom_reason", "role", "keyboard_contract", "focus_contract"):
                if not isinstance(c.get(key), str) or not c[key].strip():
                    add(p + "." + key, "CUSTOM_CONTRACT", "Custom semantics require a reason and explicit ownership.")
        availability = c.get("availability", "enabled")
        if availability not in ("enabled", "native-disabled", "aria-disabled", "readonly"):
            add(p + ".availability", "AVAILABILITY", "Unknown availability state.")
        if availability == "native-disabled":
            if tag not in DISABLABLE:
                add(p + ".element", "DISABLED_TARGET", "This element does not support native disabled.")
            if c.get("submit_policy") == "include" and c.get("separate_serialization") is not True:
                add(p + ".submit_policy", "DISABLED_PAYLOAD", "Disabled native controls are omitted from FormData; specify separate serialization if needed.")
        if availability == "readonly" and not (tag == "textarea" or (tag == "input" and c.get("type", "text") in READONLY_TYPES)):
            add(p + ".availability", "READONLY_TARGET", "readonly does not apply to this control type.")
        if availability == "aria-disabled":
            paths = c.get("execution_paths")
            if not isinstance(paths, list) or not paths:
                add(p + ".execution_paths", "GUARD_PATHS", "List every public execution entry point.")
            else:
                for i, entry in enumerate(paths):
                    if not isinstance(entry, dict) or not isinstance(entry.get("name"), str) or not entry["name"].strip() or entry.get("guarded") is not True:
                        add(f"{p}.execution_paths[{i}]", "UNGUARDED_PATH", "Each declared entry point needs a common availability guard.")
            if not isinstance(c.get("unavailable_reason"), str) or not c["unavailable_reason"].strip():
                add(p + ".unavailable_reason", "REASON", "Record an explanation reachable without a pointer.")
        if intent == "dialog":
            if c.get("mode") not in ("modal", "nonmodal"):
                add(p + ".mode", "MODALITY", "Declare modal or nonmodal.")
            if tag == "dialog":
                if "tabindex" in c:
                    add(p + ".tabindex", "DIALOG_TABINDEX", "Do not put tabindex on native dialog.")
                expected = "showModal" if c.get("mode") == "modal" else "show"
                if c.get("open_method") != expected:
                    add(p + ".open_method", "DIALOG_OPEN", "Match the native opening method to modality.")
                if c.get("close_method") not in ("close", "requestClose", "form-dialog"):
                    add(p + ".close_method", "DIALOG_CLOSE", "Use a close algorithm, not direct open-attribute removal.")
            if c.get("background_cleanup_independent") is not True:
                add(p + ".background_cleanup_independent", "CLEANUP_OWNERSHIP", "Background cleanup must not depend on invoker existence.")
            for key in ("initial_focus", "focus_owner", "return_fallback"):
                if not isinstance(c.get(key), str) or not c[key].strip():
                    add(p + "." + key, "FOCUS_CONTRACT", "Record focus target, owner, and fallback policy.")
            if c.get("mode") == "nonmodal" and (c.get("traps_focus") is not False or c.get("unconditional_return") is not False):
                add(p + ".mode", "NONMODAL_FOCUS", "Do not impose modal traps or unconditional return on nonmodal content.")
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        results = check(json.loads(args.file.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError) as error:
        print(json.dumps({"status": "INVALID_INPUT", "error": str(error)}))
        return 2
    print(json.dumps({"status": "FAIL" if results else "PASS_DECLARATIONS_ONLY", "findings": results,
                      "limitation": "No DOM, event, layout or assistive-technology behavior is verified."}, ensure_ascii=False, indent=2))
    return 1 if results else 0


if __name__ == "__main__":
    raise SystemExit(main())
