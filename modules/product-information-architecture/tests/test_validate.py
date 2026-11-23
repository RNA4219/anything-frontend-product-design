"""Contract tests authored from plan-contract.md and the two input briefs.

These fixtures are specification examples, not benchmark-arm outputs. Mutations
exercise obligations and role-specific paths, without judging visual quality or
promoting a skill. Only the checker, contract, and input briefs informed them.
"""
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock


sys.dont_write_bytecode = True
EXTENSION = Path(__file__).resolve().parents[1]
CHECKER = EXTENSION / "checks" / "validate_plan.py"
spec = importlib.util.spec_from_file_location("product_ia_validator", CHECKER)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def by_id(items, item_id):
    return next(item for item in items if item["id"] == item_id)


def screen(screen_id, goals, features, roles, entry_roles, information):
    """Expand explicit fixture data into the contract's screen records."""
    return {
        "id": screen_id,
        "title": screen_id,
        "purpose": "対象の状況を確認して、この作業の判断を行う",
        "goal_ids": list(goals),
        "feature_ids": list(features),
        "roles": list(roles),
        "entry_for": list(entry_roles),
        "information": [
            {"id": field, "visibility": "primary", "reason": "この判断に必要"}
            for field in information
        ],
    }


def navigation(source, target, roles, label=None):
    return {
        "from": source,
        "to": target,
        "roles": list(roles),
        "label": label or target,
        "kind": "contextual",
        "rationale": "この作業に必要な対象と判断の場所へ移る",
    }


def route(goal, start, target):
    return {
        "goal_id": goal,
        "start_screen": start,
        "target_screen": target,
        "notes": "このroleの入口から必要情報がある判断場所へ進む",
    }


def plan_header(brief, decisions):
    """Copy input identity/obligations; dispositions are hand-authored below."""
    features = []
    for request in brief["feature_requests"]:
        disposition, target = decisions.get(request["id"], ("keep", None))
        feature = {
            key: copy.deepcopy(request[key])
            for key in (
                "id", "label", "object", "outcome", "roles", "goal_ids",
                "requirement_ids", "dependencies",
            )
        }
        feature.update(
            disposition=disposition,
            target=target,
            reason={
                "keep": "入力の目標と要件を満たす機能として維持する",
                "merge": "同一対象・結果・権限の別名を正本へ統合する",
                "defer": "初回に必須ではないため、確認事項とともに延期する",
                "remove": "今回の目標に対応しない提案なので採用しない",
            }[disposition],
            priority="required" if request["mandatory"] else "low",
            priority_basis="確定した必須要件と初回に必須でない要求を区別する",
        )
        features.append(feature)
    return {
        "schema_version": "1.0",
        "case_id": brief["case_id"],
        "visual_intent_id": brief["visual_intent"]["id"],
        "features": features,
        "screens": [],
        "navigation": [],
        "goal_routes": [],
        "unresolved": [],
        "decision_notes": ["既存の視覚意図を引き継ぐ。利用者による実地検証は未実施。"],
    }


def support_case():
    brief = json.loads((EXTENSION / "tests/briefs/support-triage.json").read_text())
    plan = plan_header(brief, {
        "f_my_queue": ("merge", "f_inbox"),
        "f_trends": ("defer", None),
        "f_theme": ("remove", None),
    })
    plan["screens"] = [
        screen("s_queue", ["g_triage"], ["f_inbox"], ["operator"], ["operator"],
               ["ticket_id", "summary", "severity", "due_at", "owner", "status"]),
        screen("s_assign", ["g_assign"], ["f_assign"], ["operator"], [],
               ["ticket_id", "owner", "assignment_policy"]),
        screen("s_records", ["g_find"], ["f_search", "f_history"],
               ["operator"], [], ["ticket_id", "status", "history"]),
        # The inherited fixture exposed operator-only search to managers.
        # Model a manager-specific view; do not broaden the source permission.
        screen("s_records_manager", [], ["f_history"],
               ["manager"], [], ["ticket_id", "status", "history"]),
        screen("s_audit", ["g_audit"], ["f_export"], ["manager"], ["manager"],
               ["date_range", "retention", "export_scope"]),
    ]
    plan["navigation"] = [
        navigation("s_queue", "s_assign", ["operator"]),
        navigation("s_queue", "s_records", ["operator"]),
        navigation("s_audit", "s_records_manager", ["manager"]),
    ]
    plan["goal_routes"] = [
        route("g_triage", "s_queue", "s_queue"),
        route("g_assign", "s_queue", "s_assign"),
        route("g_find", "s_queue", "s_records"),
        route("g_audit", "s_audit", "s_audit"),
    ]
    plan["unresolved"] = [{
        "id": "u_trends", "category": "function", "owner": "product",
        "impact": "g_trendsは初回に必須でないため延期する", "blocking": False,
        "question": "月別集計を再検討する時期と対象期間を決める",
    }]
    plan["decision_notes"].append("g_trendsとf_trendsは非必須のため延期し、u_trendsで追跡する。")
    return brief, plan


def catalog_case():
    brief = json.loads((EXTENSION / "tests/briefs/course-catalog.json").read_text())
    plan = plan_header(brief, {
        "f_topics": ("merge", "f_catalog"),
        "f_workshops": ("merge", "f_catalog"),
        "f_wishlist": ("merge", "f_favorites"),
        "f_news": ("remove", None),
    })
    plan["screens"] = [
        screen("s_catalog", ["g_discover"], ["f_catalog"], ["learner"], ["learner"],
               ["title", "level", "schedule", "price", "topic"]),
        screen("s_compare", ["g_compare"], ["f_compare"], ["learner"], [],
               ["title", "level", "schedule", "price", "prerequisites", "venue"]),
        screen("s_detail", ["g_decide"], ["f_details"], ["learner"], [],
               ["title", "prerequisites", "seats", "price", "schedule", "enroll_link"]),
        screen("s_saved", ["g_saved"], ["f_favorites"], ["learner"], [],
               ["title", "schedule", "price"]),
        screen("s_publish", ["g_publish"], ["f_publish"], ["editor"], ["editor"],
               ["title", "publication_status"]),
    ]
    plan["navigation"] = [
        navigation("s_catalog", "s_compare", ["learner"]),
        navigation("s_catalog", "s_detail", ["learner"]),
        navigation("s_catalog", "s_saved", ["learner"]),
        navigation("s_compare", "s_detail", ["learner"]),
    ]
    plan["goal_routes"] = [
        route("g_discover", "s_catalog", "s_catalog"),
        route("g_compare", "s_catalog", "s_compare"),
        route("g_decide", "s_catalog", "s_detail"),
        route("g_saved", "s_catalog", "s_saved"),
        route("g_publish", "s_publish", "s_publish"),
    ]
    return brief, plan


class PlanContractTests(unittest.TestCase):
    def assert_pass(self, brief, plan):
        result = validator.validate(brief, plan)
        self.assertEqual("PASS", result["status"], json.dumps(result, ensure_ascii=False))
        self.assertEqual([], result["issues"])
        return result

    def assert_rejected(self, brief, plan, code=None):
        result = validator.validate(brief, plan)
        self.assertEqual("FAIL", result["status"], json.dumps(result, ensure_ascii=False))
        self.assertTrue(any(issue["severity"] == "error" for issue in result["issues"]))
        if code:
            self.assertIn(code, {issue["code"] for issue in result["issues"]}, result)
        return result

    def test_two_independently_authored_normal_plans(self):
        for factory in (support_case, catalog_case):
            with self.subTest(case=factory.__name__):
                brief, plan = factory()
                before = copy.deepcopy((brief, plan))
                self.assert_pass(brief, plan)
                self.assertEqual(before, (brief, plan), "Validation must not rewrite its inputs")

    def test_same_screen_decision_and_legitimate_return_cycles_are_valid(self):
        brief, plan = catalog_case()
        plan["navigation"].append(navigation("s_detail", "s_catalog", ["learner"], "講座一覧に戻る"))
        plan["navigation"].append(navigation("s_compare", "s_catalog", ["learner"], "候補を追加する"))
        self.assert_pass(brief, plan)
        # The editor's start and target are identical and have no outgoing edge.
        self.assertEqual("s_publish", plan["goal_routes"][-1]["start_screen"])
        self.assertEqual("s_publish", plan["goal_routes"][-1]["target_screen"])

    def test_merge_chain_and_dependency_on_an_alias_are_valid(self):
        brief, plan = catalog_case()
        by_id(plan["features"], "f_topics")["target"] = "f_workshops"
        by_id(brief["feature_requests"], "f_compare")["dependencies"] = ["f_topics"]
        by_id(plan["features"], "f_compare")["dependencies"] = ["f_topics"]
        self.assert_pass(brief, plan)

    def test_requirement_only_added_enabler_is_allowed(self):
        brief, plan = support_case()
        enabler = copy.deepcopy(by_id(plan["features"], "f_history"))
        enabler.update(id="add_record_integrity", label="記録の整合性", outcome="verify-record",
                       goal_ids=[], requirement_ids=["r_archive"], dependencies=[])
        plan["features"].append(enabler)
        by_id(plan["screens"], "s_records")["feature_ids"].append(enabler["id"])
        self.assert_pass(brief, plan)

    def test_low_frequency_mandatory_export_cannot_be_removed_or_deferred(self):
        for disposition in ("remove", "defer"):
            with self.subTest(disposition=disposition):
                brief, plan = support_case()
                by_id(plan["features"], "f_export")["disposition"] = disposition
                by_id(plan["screens"], "s_audit")["feature_ids"] = []
                self.assert_rejected(brief, plan, "MANDATORY_FEATURE_LOST")

    def test_even_an_optional_request_needs_an_explicit_decision(self):
        brief, plan = support_case()
        plan["features"] = [f for f in plan["features"] if f["id"] != "f_theme"]
        self.assert_rejected(brief, plan, "UNACCOUNTED_FEATURE")

    def test_mandatory_requirement_needs_a_kept_capability(self):
        brief, plan = catalog_case()
        for feature in plan["features"]:
            feature["requirement_ids"] = [r for r in feature["requirement_ids"] if r != "r_prereq"]
        self.assert_rejected(brief, plan, "MISSING_REQUIREMENT")

    def test_must_goal_needs_a_capability_for_its_role(self):
        brief, plan = catalog_case()
        by_id(plan["features"], "f_compare")["goal_ids"] = []
        self.assert_rejected(brief, plan, "MISSING_GOAL")

    def test_merge_cannot_end_at_missing_deferred_or_cyclic_target(self):
        for mutation in ("missing", "deferred", "self_cycle", "two_node_cycle"):
            with self.subTest(mutation=mutation):
                brief, plan = catalog_case()
                alias = by_id(plan["features"], "f_topics")
                if mutation == "missing":
                    alias["target"] = "absent_feature"
                elif mutation == "deferred":
                    by_id(plan["features"], "f_catalog")["disposition"] = "defer"
                    by_id(plan["screens"], "s_catalog")["feature_ids"] = []
                elif mutation == "self_cycle":
                    alias["target"] = alias["id"]
                else:
                    alias["target"] = "f_workshops"
                    by_id(plan["features"], "f_workshops")["target"] = "f_topics"
                self.assert_rejected(brief, plan, "MERGE_CYCLE_OR_DEAD_TARGET")

    def test_merge_cannot_change_object_outcome_or_roles(self):
        changes = {"object": "audit-record", "outcome": "publish-course", "roles": ["editor"]}
        for field, value in changes.items():
            with self.subTest(field=field):
                brief, plan = catalog_case()
                by_id(plan["features"], "f_topics")[field] = value
                self.assert_rejected(brief, plan, "MERGE_SEMANTICS")

    def test_merge_target_must_preserve_alias_goals_and_requirements(self):
        for field in ("goal_ids", "requirement_ids"):
            with self.subTest(field=field):
                brief, plan = catalog_case()
                by_id(plan["features"], "f_catalog")[field] = []
                self.assert_rejected(brief, plan, "MERGE_LOST_OBLIGATION")

    def test_erasing_alias_and_target_cannot_erase_original_input_obligations(self):
        # Non-mandatory obligations isolate merge preservation from global must checks.
        for field, extra_id in (("goal_ids", "g_topic_find"), ("requirement_ids", "r_topic_find")):
            with self.subTest(field=field):
                brief, plan = catalog_case()
                brief["goals"].append({
                    "id": "g_topic_find", "role": "learner", "outcome": "トピックから候補を見つける",
                    "priority": "should", "needed_information": ["title", "topic"],
                })
                brief["requirements"].append({
                    "id": "r_topic_find", "goal_ids": ["g_topic_find"],
                    "mandatory": False, "statement": "トピック名と対象講座の関係を確認できる",
                })
                by_id(brief["feature_requests"], "f_topics")[field].append(extra_id)
                for feature_id in ("f_topics", "f_catalog"):
                    by_id(plan["features"], feature_id)[field].append(extra_id)
                if field == "requirement_ids":
                    # This offered optional route also needs a direct capability
                    # binding; keep it while the test removes only requirement IDs.
                    by_id(brief["feature_requests"], "f_topics")["goal_ids"].append("g_topic_find")
                    for feature_id in ("f_topics", "f_catalog"):
                        by_id(plan["features"], feature_id)["goal_ids"].append("g_topic_find")
                by_id(plan["screens"], "s_catalog")["goal_ids"].append("g_topic_find")
                plan["goal_routes"].append(route("g_topic_find", "s_catalog", "s_catalog"))
                self.assert_pass(brief, plan)
                for feature_id in ("f_topics", "f_catalog"):
                    by_id(plan["features"], feature_id)[field].remove(extra_id)
                self.assert_rejected(brief, plan)

    def test_only_kept_canonical_features_can_own_screen_space(self):
        brief, plan = catalog_case()
        by_id(plan["screens"], "s_catalog")["feature_ids"].append("f_topics")
        self.assert_rejected(brief, plan, "NONCANONICAL_SCREEN_FEATURE")

    def test_required_dependency_is_not_hidden_by_erasing_output_dependencies(self):
        brief, plan = support_case()
        by_id(plan["features"], "f_history")["disposition"] = "remove"
        for feature_id in ("f_assign", "f_export"):
            by_id(plan["features"], feature_id)["dependencies"] = []
        by_id(plan["screens"], "s_records")["feature_ids"].remove("f_history")
        self.assert_rejected(brief, plan, "DEPENDENCY_LOST")

    def test_unknown_dependency_is_rejected(self):
        brief, plan = catalog_case()
        by_id(plan["features"], "f_compare")["dependencies"] = ["f_nonexistent"]
        self.assert_rejected(brief, plan, "DEPENDENCY_LOST")

    def test_output_cannot_grant_operator_the_manager_only_export(self):
        brief, plan = support_case()
        by_id(plan["features"], "f_export")["roles"].append("operator")
        by_id(plan["screens"], "s_audit")["roles"].append("operator")
        plan["navigation"].append(navigation("s_queue", "s_audit", ["operator"], "監査用記録"))
        self.assert_rejected(brief, plan)

    def test_navigation_cannot_offer_an_unauthorized_destination(self):
        brief, plan = catalog_case()
        plan["navigation"].append(navigation("s_catalog", "s_publish", ["learner"], "講座を公開"))
        self.assert_rejected(brief, plan, "NAV_ROLE_LEAK")

    def test_reachability_is_computed_for_the_goals_role(self):
        brief, plan = catalog_case()
        for screen_id in ("s_catalog", "s_compare"):
            by_id(plan["screens"], screen_id)["roles"].append("editor")
        edge = next(n for n in plan["navigation"] if n["to"] == "s_compare")
        edge["roles"] = ["editor"]
        self.assert_rejected(brief, plan, "UNREACHABLE_GOAL")

    def test_missing_route_disconnected_target_and_invalid_entry_are_distinct(self):
        for mutation, code in (
            ("missing_route", "MISSING_GOAL_ROUTE"),
            ("disconnected", "UNREACHABLE_GOAL"),
            ("not_an_entry", "INVALID_START"),
            ("wrong_owner", "SCREEN_GOAL_MISMATCH"),
        ):
            with self.subTest(mutation=mutation):
                brief, plan = catalog_case()
                if mutation == "missing_route":
                    plan["goal_routes"] = [r for r in plan["goal_routes"] if r["goal_id"] != "g_compare"]
                elif mutation == "disconnected":
                    plan["navigation"] = [n for n in plan["navigation"] if n["to"] != "s_compare"]
                elif mutation == "not_an_entry":
                    by_id(plan["screens"], "s_catalog")["entry_for"] = []
                else:
                    by_id(plan["screens"], "s_compare")["goal_ids"] = []
                self.assert_rejected(brief, plan, code)

    def test_information_on_other_screens_or_behind_disclosure_is_not_primary(self):
        for mutation in ("missing", "secondary"):
            with self.subTest(mutation=mutation):
                brief, plan = catalog_case()
                decision = by_id(plan["screens"], "s_compare")
                if mutation == "missing":
                    decision["information"] = [i for i in decision["information"] if i["id"] != "price"]
                else:
                    by_id(decision["information"], "price")["visibility"] = "secondary"
                # price still exists on catalog/detail; remembering it is not sufficient.
                self.assert_rejected(brief, plan, "HIDDEN_DECISION_INFORMATION")

    def test_duplicate_and_malformed_information_do_not_silently_pass(self):
        for mutation, code in (("duplicate", "DUPLICATE_INFORMATION"), ("malformed", "SHAPE")):
            with self.subTest(mutation=mutation):
                brief, plan = catalog_case()
                information = by_id(plan["screens"], "s_compare")["information"]
                information.append(copy.deepcopy(information[0]) if mutation == "duplicate" else None)
                self.assert_rejected(brief, plan, code)

    def test_ambiguous_labels_require_overlapping_roles_and_distinct_destinations(self):
        brief, plan = catalog_case()
        plan["navigation"][0]["label"] = "Open"
        plan["navigation"][1]["label"] = "  OPEN  "
        result = validator.validate(brief, plan)
        self.assertEqual("HOLD", result["status"])
        self.assertIn("AMBIGUOUS_SIBLING_LABEL", {i["code"] for i in result["issues"]})
        brief, plan = catalog_case()
        plan["screens"].append(screen("s_landing", [], [], ["learner", "editor"], [], []))
        plan["navigation"].extend([
            navigation("s_landing", "s_catalog", ["learner"], "作業"),
            navigation("s_landing", "s_publish", ["editor"], "作業"),
        ])
        self.assert_pass(brief, plan)

    def test_unresolved_blocker_holds_and_errors_take_precedence(self):
        brief, plan = support_case()
        self.assert_pass(brief, plan)
        plan["unresolved"][0]["blocking"] = True
        result = validator.validate(brief, plan)
        self.assertEqual("HOLD", result["status"])
        self.assertIn("UNRESOLVED_BLOCKER", {i["code"] for i in result["issues"]})
        plan["visual_intent_id"] = "different_visual_intent"
        self.assert_rejected(brief, plan, "VISUAL_INTENT")

    def test_non_object_documents_and_malformed_ids_fail_without_crashing(self):
        for invalid in (None, [], "not an object", 3):
            for side in ("brief", "plan"):
                with self.subTest(side=side, value=invalid):
                    brief, plan = catalog_case()
                    self.assert_rejected(invalid if side == "brief" else brief,
                                         invalid if side == "plan" else plan, "SHAPE")
        for invalid in ({"id": "nested"}, [], None, 3, " "):
            with self.subTest(nested_id=invalid):
                brief, plan = catalog_case()
                by_id(plan["features"], "f_compare")["dependencies"] = [invalid]
                self.assert_rejected(brief, plan, "SHAPE")

    def test_brief_feature_fields_are_required_even_if_plan_supplies_them(self):
        for field in ("label", "goal_ids", "requirement_ids"):
            with self.subTest(missing_field=field):
                brief, plan = catalog_case()
                del by_id(brief["feature_requests"], "f_catalog")[field]
                self.assert_rejected(brief, plan)

    def test_invalid_input_goal_priority_cannot_disable_must_checks(self):
        brief, plan = catalog_case()
        by_id(brief["goals"], "g_compare")["priority"] = "musst"
        plan["goal_routes"] = [r for r in plan["goal_routes"] if r["goal_id"] != "g_compare"]
        self.assert_rejected(brief, plan)

    def test_input_references_must_resolve_to_declared_entities(self):
        for group, record_id, field, value in (
            ("requirements", "r_find", "goal_ids", ["g_nonexistent"]),
            ("feature_requests", "f_catalog", "goal_ids", ["g_nonexistent"]),
            ("feature_requests", "f_catalog", "requirement_ids", ["r_nonexistent"]),
            ("feature_requests", "f_catalog", "roles", ["undeclared_role"]),
            ("feature_requests", "f_catalog", "dependencies", ["f_nonexistent"]),
        ):
            with self.subTest(group=group, field=field):
                brief, plan = catalog_case()
                by_id(brief[group], record_id)[field] = value
                self.assert_rejected(brief, plan)

    def test_duplicate_ids_and_wrong_array_shapes_fail(self):
        brief, plan = catalog_case()
        plan["features"].append(copy.deepcopy(plan["features"][0]))
        self.assert_rejected(brief, plan, "DUPLICATE_ID")
        for field in ("features", "screens", "navigation", "goal_routes", "unresolved"):
            with self.subTest(field=field):
                brief, plan = catalog_case()
                plan[field] = {}
                self.assert_rejected(brief, plan, "SHAPE")

    def test_untraced_addition_and_unplaced_kept_feature_are_rejected(self):
        brief, plan = catalog_case()
        by_id(plan["features"], "f_news")["disposition"] = "keep"
        by_id(plan["screens"], "s_catalog")["feature_ids"].append("f_news")
        self.assert_rejected(brief, plan, "UNTRACED_FEATURE")
        brief, plan = catalog_case()
        by_id(plan["screens"], "s_saved")["feature_ids"] = []
        self.assert_rejected(brief, plan, "UNPLACED_FEATURE")

    def test_case_version_and_visual_intent_identity_are_preserved(self):
        for field, value, code in (
            ("case_id", "another-case", "CASE_MISMATCH"),
            ("schema_version", "9.0", "VERSION"),
            ("visual_intent_id", "new-brand", "VISUAL_INTENT"),
        ):
            with self.subTest(field=field):
                brief, plan = catalog_case()
                plan[field] = value
                self.assert_rejected(brief, plan, code)


class CommandLineContractTests(unittest.TestCase):
    def invoke(self, reads):
        output = io.StringIO()
        with mock.patch.object(sys, "argv", ["validate_plan.py", "--brief", "brief.json", "--plan", "plan.json"]), \
             mock.patch.object(validator.Path, "read_text", side_effect=reads), \
             redirect_stdout(output):
            exit_code = validator.main()
        return exit_code, json.loads(output.getvalue())

    def test_pass_fail_and_hold_exit_codes(self):
        for expected_status, expected_exit in (("PASS", 0), ("FAIL", 1), ("HOLD", 1)):
            with self.subTest(status=expected_status):
                brief, plan = support_case()
                if expected_status == "FAIL":
                    plan["visual_intent_id"] = "changed"
                elif expected_status == "HOLD":
                    plan["unresolved"][0]["blocking"] = True
                exit_code, result = self.invoke([json.dumps(brief), json.dumps(plan)])
                self.assertEqual(expected_exit, exit_code)
                self.assertEqual(expected_status, result["status"])

    def test_invalid_json_missing_file_and_bad_encoding_return_exit_two(self):
        for reads in (
            ["{not valid json"],
            [FileNotFoundError("brief file not found")],
            [UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid byte")],
        ):
            with self.subTest(reads=repr(reads)):
                exit_code, result = self.invoke(reads)
                self.assertEqual(2, exit_code)
                self.assertEqual("INVALID_INPUT", result["status"])
                self.assertTrue(result["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
