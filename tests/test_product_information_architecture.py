import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "modules" / "product-information-architecture" / "examples" / "booking_choice.py"
ENTRIES = {"status": "group changeable", "room": "group workshop"}


class BookingChoiceTest(unittest.TestCase):
    def run_mock(self, variant, *operations, scenario="base", exit_code=0, interactive=False):
        command = [sys.executable, "-X", "utf8", str(SCRIPT), "--variant", variant, "--scenario", scenario]
        if not interactive:
            command.extend(("--steps", *operations))
        run = subprocess.run(
            command,
            cwd=ROOT,
            input="\n".join((*operations, "quit", "")) if interactive else "",
            capture_output=True,
            encoding="utf-8",
            timeout=10,
        )
        self.assertEqual(run.returncode, exit_code, run.stdout + run.stderr)
        result = json.loads(run.stdout.splitlines()[-1].removeprefix("RESULT "))
        return run.stdout, result

    def test_both_entries_change_and_reopen_same_booking(self):
        results = {}
        for variant, entry in ENTRIES.items():
            with self.subTest(variant=variant):
                operations = (entry, "open R-204", "slot 12-10", "confirm", "reopen", entry, "open R-204")
                transcript, result = self.run_mock(variant, *operations)
                self.assertIn("変更前 12月8日 14:00\n変更後 12月10日 14:00", transcript)
                self.assertIn("R-204 | 工作室 | 12月10日 14:00 | 確定・変更可", transcript.split("> reopen")[1])
                self.assertEqual(result["opened_ids"], ["R-204", "R-204"])
                self.assertEqual(result["commands"], [{"command": op, "accepted": True} for op in operations])
                self.assertEqual(result["data"], "synthetic")
                self.assertTrue(result["booking-change-find"])
                self.assertTrue(result["booking-change-confirm"])
                change, = result["changes"]
                self.assertEqual((change["before"]["id"], change["before"]["date"]), ("R-204", "12-08"))
                self.assertEqual((change["after"]["id"], change["after"]["date"]), ("R-204", "12-10"))
                self.assertEqual(change["after"]["time"], "14:00")
                self.assertEqual(result["bookings"][1]["date"], "11-10")
                results[variant] = result
        self.assertEqual(results["status"]["bookings"], results["room"]["bookings"])

    def test_wrong_status_group_then_recovery(self):
        transcript, result = self.run_mock(
            "status", "group used", "open R-204", "open R-205", "slot 12-10", "confirm", "reopen",
            "group changeable", "open R-204", "slot 12-10", "confirm", "reopen", "group changeable", "open R-204",
        )
        self.assertIn("open R-205 | 工作室 | 11月10日 14:00 | 利用済み", transcript)
        self.assertEqual(
            [item["command"] for item in result["commands"] if not item["accepted"]],
            ["open R-204", "slot 12-10", "confirm"],
        )
        self.assertEqual(result["opened_ids"], ["R-205", "R-204", "R-204"])
        change, = result["changes"]
        self.assertEqual(change["before"]["id"], "R-204")
        self.assertTrue(result["booking-change-confirm"])

    def test_unconfirmed_preview_survives_as_original_after_reopen(self):
        transcript, result = self.run_mock(
            "room", "group workshop", "open R-204", "slot 12-10", "reopen", "group workshop", "open R-204",
            "confirm", exit_code=1,
        )
        self.assertIn("変更後 12月10日 14:00", transcript.split("> reopen")[0])
        self.assertIn("R-204 | 工作室 | 12月8日 14:00 | 確定・変更可", transcript.split("> reopen")[1])
        self.assertFalse(result["commands"][-1]["accepted"])
        self.assertEqual(result["changes"], [])
        self.assertEqual(result["bookings"][0]["date"], "12-08")
        self.assertTrue(result["booking-change-find"])
        self.assertFalse(result["booking-change-confirm"])

    def test_two_changeable_bookings_need_explicit_time_selection(self):
        for variant, entry in ENTRIES.items():
            with self.subTest(variant=variant):
                transcript, result = self.run_mock(
                    variant, entry, "slot 12-10", "confirm", "open R-204", "slot 12-10", "confirm", "reopen",
                    entry, "open R-204", scenario="two-changeable",
                )
                self.assertLess(transcript.index("open R-206"), transcript.index("open R-204"))
                self.assertIn("open R-206 | 工作室 | 12月8日 10:00 | 確定・変更可", transcript)
                self.assertIn("open R-204 | 工作室 | 12月8日 14:00 | 確定・変更可", transcript)
                self.assertFalse(result["commands"][1]["accepted"])
                self.assertFalse(result["commands"][2]["accepted"])
                self.assertTrue(result["booking-change-confirm"])
                self.assertEqual(
                    [(b["id"], b["date"], b["time"]) for b in result["bookings"]],
                    [("R-206", "12-08", "10:00"), ("R-204", "12-10", "14:00"), ("R-205", "11-10", "14:00")],
                )

    def test_confirming_another_eligible_booking_does_not_pass_the_task(self):
        _, result = self.run_mock(
            "room", "group workshop", "open R-206", "slot 12-10", "confirm", "reopen", "group workshop",
            "open R-204", scenario="two-changeable", exit_code=1,
        )
        change, = result["changes"]
        self.assertEqual(change["after"]["id"], "R-206")
        self.assertEqual(result["bookings"][1]["date"], "12-08")
        self.assertTrue(result["booking-change-find"])
        self.assertFalse(result["booking-change-confirm"])

    def test_missing_original_time_can_defer_without_mutation(self):
        for variant, entry in ENTRIES.items():
            with self.subTest(variant=variant):
                operations = (entry, "open R-206", "back", "open R-204", "quit")
                transcript, result = self.run_mock(variant, *operations, scenario="unknown-time", exit_code=1)
                prompt = transcript.splitlines()[0]
                self.assertIn("12月8日の工作室", prompt)
                self.assertIn("予約確認の通知", prompt)
                self.assertNotIn("12月8日 14:00", prompt)
                self.assertNotIn("R-204", prompt)
                self.assertEqual(result["opened_ids"], ["R-206", "R-204"])
                self.assertEqual(result["changes"], [])
                self.assertEqual(result["outcome"], "deferred_without_change")
                self.assertFalse(result["booking-change-find"])
                self.assertFalse(result["booking-change-confirm"])
                _, known_time = self.run_mock(variant, entry, scenario="two-changeable", exit_code=1)
                self.assertEqual(result["bookings"], known_time["bookings"])

    def test_guessing_correct_booking_without_original_time_is_not_success(self):
        transcript, result = self.run_mock(
            "room", "group workshop", "open R-204", "slot 12-10", "confirm", "reopen", "group workshop",
            "open R-204", scenario="unknown-time", exit_code=1,
        )
        self.assertIn("変更は記録されました。", transcript)
        change, = result["changes"]
        self.assertEqual((change["after"]["id"], change["after"]["date"]), ("R-204", "12-10"))
        self.assertEqual(result["outcome"], "changed_without_identification")
        self.assertFalse(result["booking-change-find"])
        self.assertFalse(result["booking-change-confirm"])

    def test_another_slot_does_not_pass_the_task(self):
        _, result = self.run_mock(
            "room", "group workshop", "open R-204", "slot 12-11", "confirm", "reopen", "group workshop",
            "open R-204", exit_code=1,
        )
        change, = result["changes"]
        self.assertEqual((change["after"]["id"], change["after"]["date"]), ("R-204", "12-11"))
        self.assertFalse(result["booking-change-confirm"])

    def test_commit_alone_does_not_pass_result_confirmation(self):
        _, result = self.run_mock(
            "room", "group workshop", "open R-204", "slot 12-10", "confirm", "reopen", exit_code=1,
        )
        self.assertEqual(result["bookings"][0]["date"], "12-10")
        self.assertFalse(result["booking-change-confirm"])

    def test_interactive_entry_uses_visible_actions(self):
        transcript, result = self.run_mock(
            "room", "group workshop", "open R-204", "slot 12-10", "confirm", "reopen", "group workshop",
            "open R-204", interactive=True,
        )
        self.assertIn("group workshop | 工作室", transcript)
        self.assertIn("open R-204 | 工作室 | 12月8日 14:00 | 確定・変更可", transcript)
        self.assertTrue(result["booking-change-confirm"])
