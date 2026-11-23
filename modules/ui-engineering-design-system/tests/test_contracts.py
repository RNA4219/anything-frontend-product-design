import copy
import importlib.util
import json
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("contracts", MODULE / "checks/contracts.py")
contracts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contracts)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.good = json.loads((MODULE / "examples/component-contracts.json").read_text())

    def codes(self, data):
        return {x["code"] for x in contracts.check(data)}

    def test_candidate_is_consistent(self):
        self.assertEqual(contracts.check(self.good), [])

    def test_seeded_baseline_detects_nine_distinct_defects(self):
        bad = json.loads((MODULE / "tests/fixtures/component-baseline.json").read_text())
        self.assertEqual(self.codes(bad), {"DESTINATION", "BUTTON_TYPE", "READONLY_TARGET", "UNGUARDED_PATH",
                         "DIALOG_OPEN", "DIALOG_CLOSE", "DIALOG_TABINDEX", "CLEANUP_OWNERSHIP", "NONMODAL_FOCUS"})

    def test_disabled_required_payload_needs_an_explicit_alternative(self):
        c = self.good["components"][2]
        c["availability"] = "native-disabled"
        self.assertIn("DISABLED_PAYLOAD", self.codes(self.good))
        c["separate_serialization"] = True
        self.assertNotIn("DISABLED_PAYLOAD", self.codes(self.good))

    def test_readonly_checkbox_and_select_are_not_readonly_text(self):
        c = self.good["components"][2]
        for tag, kind in [("input", "checkbox"), ("select", "text"), ("input", "file")]:
            c.update(element=tag, type=kind)
            self.assertIn("READONLY_TARGET", self.codes(self.good))

    def test_textarea_readonly_is_allowed(self):
        self.good["components"][2]["element"] = "textarea"
        self.assertEqual(contracts.check(self.good), [])

    def test_native_disabled_does_not_disable_anchor(self):
        self.good["components"][0]["availability"] = "native-disabled"
        self.assertIn("DISABLED_TARGET", self.codes(self.good))

    def test_custom_control_requires_explicit_responsibilities(self):
        c = self.good["components"][1]; c["element"] = "div"
        self.assertIn("CUSTOM_CONTRACT", self.codes(self.good))
        c.update(custom_reason="Existing verified library", role="button", keyboard_contract="Enter/Space activate once", focus_contract="tabindex=0")
        self.assertEqual(contracts.check(self.good), [])

    def test_custom_dialog_does_not_inherit_native_tabindex_ban(self):
        c = self.good["components"][4]
        c.update(element="div", tabindex=-1, custom_reason="Existing verified library", role="dialog", keyboard_contract="Library owns trap and escape", focus_contract="Library owns initial and restore")
        self.assertEqual(contracts.check(self.good), [])

    def test_aria_disabled_has_no_default_behavior_guarantee(self):
        c = self.good["components"][3]; c.pop("execution_paths")
        self.assertIn("GUARD_PATHS", self.codes(self.good))

    def test_nonmodal_outside_focus_must_be_preserved(self):
        self.good["components"][5]["unconditional_return"] = True
        self.assertIn("NONMODAL_FOCUS", self.codes(self.good))

    def test_duplicate_identity(self):
        self.good["components"].append(copy.deepcopy(self.good["components"][0]))
        self.assertIn("IDENTITY", self.codes(self.good))

    def test_invalid_structures_do_not_crash_or_pass(self):
        for doc in [None, [], {}, {"components":[]}, {"components":[None]}, {"components":[{}]}]:
            self.assertTrue(contracts.check(doc))
        for key in ["element", "type", "availability", "mode"]:
            doc = copy.deepcopy(self.good);doc["components"][4][key] = []
            self.assertTrue(contracts.check(doc))

    def test_string_false_is_not_a_boolean(self):
        self.good["components"][4]["background_cleanup_independent"] = "false"
        self.assertIn("STRUCTURE", self.codes(self.good))

    def test_malformed_or_unknown_submission_policy_is_rejected(self):
        for policy in [[], {}, True, 0, None, "incldue"]:
            doc = copy.deepcopy(self.good)
            doc["components"][2].update(availability="native-disabled", submit_policy=policy)
            self.assertTrue(contracts.check(doc), repr(policy))
        self.good["components"][2].pop("submit_policy")
        self.assertIn("SUBMIT_POLICY", self.codes(self.good))


if __name__ == "__main__":
    unittest.main()
