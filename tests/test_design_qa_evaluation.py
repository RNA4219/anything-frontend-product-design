import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKER = REPO_ROOT / "modules" / "design-qa-evaluation" / "scripts" / "check_evidence.py"


class DesignQAEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.plan = {
            "task_id": "booking-change",
            "cases": [
                {
                    "id": "confirm",
                    "requirement_id": "booking-change-confirm",
                    "path": "normal",
                    "priority": "required",
                    "method": "automated",
                    "expected": {"date_after_reload": "12-10 14:00"},
                },
                {
                    "id": "occupied",
                    "requirement_id": "booking-change-conflict",
                    "path": "failure",
                    "priority": "required",
                    "method": "manual",
                    "expected": {"previous_date": "12-08 14:00", "can_choose_again": True},
                },
                {
                    "id": "unknown-result",
                    "requirement_id": "booking-change-retry",
                    "path": "recovery",
                    "priority": "required",
                    "method": "automated",
                    "expected": {"confirmed_changes": 1},
                },
            ],
        }
        self.observations = {
            "task_id": "booking-change",
            "build": "reservation-fixture-v2",
            "observations": [],
        }

    def observe(self, case_id, /, **overrides):
        case = next(case for case in self.plan["cases"] if case["id"] == case_id)
        self.observations["observations"].append(
            {
                "case_id": case_id,
                "method": case["method"],
                "evidence": "execution.md#" + case_id,
                "actual": case["expected"].copy(),
                **overrides,
            }
        )

    def run_checker(self, *, raw_plan=None, raw_observations=None):
        with tempfile.TemporaryDirectory() as directory:
            plan = Path(directory) / "plan.json"
            log = Path(directory) / "observations.json"
            plan.write_text(raw_plan if raw_plan is not None else json.dumps(self.plan), "utf-8")
            log.write_text(
                raw_observations if raw_observations is not None else json.dumps(self.observations),
                "utf-8",
            )
            return subprocess.run(
                [sys.executable, str(CHECKER), str(plan), str(log)],
                cwd=REPO_ROOT,
                capture_output=True,
                check=False,
                timeout=10,
            )

    def assert_report(self, code, decision, coverage, statuses):
        result = self.run_checker()
        self.assertEqual(result.returncode, code, result.stderr)
        self.assertEqual(result.stderr, b"")
        report = json.loads(result.stdout)
        self.assertEqual(report["task_id"], self.plan["task_id"])
        self.assertEqual(report["build"], self.observations["build"])
        self.assertEqual(report["decision"], decision)
        self.assertEqual(report["coverage"], coverage)
        self.assertEqual([case["status"] for case in report["cases"]], statuses)
        return report["cases"]

    def assert_input_error(self, **raw_documents):
        result = self.run_checker(**raw_documents)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)

    def test_empty_observations_remain_pending(self):
        self.assert_report(1, "pending", "partial", ["not_run"] * 3)

    def test_normal_path_alone_remains_pending(self):
        self.observe("confirm")
        self.assert_report(1, "pending", "normal_only", ["pass", "not_run", "not_run"])

    def test_matching_normal_path_is_pending_when_required_paths_are_missing_from_plan(self):
        del self.plan["cases"][1:]
        self.observe("confirm")
        self.assert_report(1, "pending", "normal_only", ["pass"])

    def test_blank_evidence_and_missing_checks_do_not_count_as_observations(self):
        self.observe("confirm")
        self.observe("occupied", evidence="  \t", actual={"previous_date": "12-08 14:00"})
        self.observe("unknown-result", actual={})
        cases = self.assert_report(
            1, "pending", "normal_only", ["pass", "insufficient_evidence", "insufficient_evidence"]
        )
        self.assertEqual(cases[1]["missing"], ["can_choose_again"])
        self.assertEqual(cases[2]["missing"], ["confirmed_changes"])

    def test_missing_evidence_and_wrong_method_cannot_prove_a_failure(self):
        self.observe("confirm")
        self.observe("occupied", method="automated", actual={"previous_date": "12-10 14:00"})
        self.observe("unknown-result", actual={"confirmed_changes": 2})
        del self.observations["observations"][-1]["evidence"]
        self.assert_report(
            1, "pending", "normal_only", ["pass", "insufficient_evidence", "insufficient_evidence"]
        )

    def test_observed_conflict_regression_blocks_release_even_with_other_missing_check(self):
        self.observe("confirm")
        self.observe("occupied", actual={"previous_date": "12-10 14:00"})
        self.observe("unknown-result")
        cases = self.assert_report(1, "no_go", "all_paths_observed", ["pass", "fail", "pass"])
        self.assertEqual(cases[1]["requirement_id"], "booking-change-conflict")
        self.assertEqual(cases[1]["missing"], ["can_choose_again"])
        self.assertEqual(cases[1]["mismatched"], ["previous_date"])

    def test_equal_numeric_values_with_different_types_fail(self):
        for wrong_type in (True, 1.0, "1"):
            with self.subTest(actual=wrong_type):
                self.observations["observations"].clear()
                self.observe("unknown-result", actual={"confirmed_changes": wrong_type})
                cases = self.assert_report(1, "no_go", "partial", ["not_run", "not_run", "fail"])
                self.assertEqual(cases[2]["mismatched"], ["confirmed_changes"])

    def test_required_paths_pass_and_advisory_failure_is_reported(self):
        self.plan["cases"].append(
            {
                "id": "reminder",
                "requirement_id": "booking-change-reminder",
                "path": "normal",
                "priority": "advisory",
                "method": "manual",
                "expected": {"reminder_sent": True},
            }
        )
        self.observe("confirm")
        self.observe("occupied")
        self.observe("unknown-result")
        self.observe("reminder", actual={"reminder_sent": False})
        self.assert_report(0, "go", "all_paths_observed", ["pass", "pass", "pass", "fail"])

    def test_unknown_and_duplicate_cases_are_input_errors(self):
        self.observe("confirm", case_id="new-case")
        self.assert_input_error()
        self.observations["observations"].clear()
        self.observe("confirm")
        self.observe("confirm")
        self.assert_input_error()
        self.observations["observations"].clear()
        self.plan["cases"].append(self.plan["cases"][0].copy())
        self.assert_input_error()

    def test_extra_keys_and_non_scalar_checks_are_input_errors(self):
        for actual in (
            {"date_after_reload": "12-10 14:00", "unplanned": True},
            {"date_after_reload": ["12-10 14:00"]},
            {"date_after_reload": float("inf")},
        ):
            with self.subTest(actual=actual):
                self.observations["observations"].clear()
                self.observe("confirm", actual=actual)
                self.assert_input_error()

    def test_small_differences_between_decimals_fail(self):
        self.plan["cases"][2]["expected"]["confirmed_changes"] = 1.0
        self.observe("unknown-result")
        text = json.dumps(self.observations).replace(
            '"confirmed_changes": 1.0', '"confirmed_changes": 1.0000000000000001'
        )
        result = self.run_checker(raw_observations=text)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["decision"], "no_go")
        self.assertEqual(report["cases"][2]["mismatched"], ["confirmed_changes"])

    def test_bad_task_build_enum_and_duplicate_keys_are_input_errors(self):
        self.observations["task_id"] = "wrong-task"
        self.assert_input_error()
        self.observations["task_id"] = self.plan["task_id"]
        self.observations["build"] = ""
        self.assert_input_error()
        self.observations["build"] = "reservation-fixture-v2"
        self.observe("confirm", method="inspection")
        self.assert_input_error()
        self.observations["observations"].clear()
        self.assert_input_error(
            raw_plan='{"task_id":"wrong-task","task_id":"booking-change","cases":[]}'
        )


if __name__ == "__main__":
    unittest.main()
