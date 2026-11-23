import subprocess
import sys
import unittest
from dataclasses import replace
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "modules" / "interaction-ux-flow" / "scripts" / "booking_flow.py"
SPEC = spec_from_file_location("booking_flow", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
booking_flow = module_from_spec(SPEC)
sys.modules[SPEC.name] = booking_flow
SPEC.loader.exec_module(booking_flow)


class BookingFlowTests(unittest.TestCase):
    def setUp(self):
        self.service = booking_flow.BookingService()
        self.flow = booking_flow.BookingFlow(self.service)

    def review(self, target="12-10"):
        self.flow.open("R-204")
        self.flow.change()
        self.flow.select(target)

    def send(self):
        self.flow.submit()
        return self.service.sent[-1]

    def assert_saved(self, slot, version):
        current = self.service.bookings["R-204"]
        self.assertEqual((current.slot, current.version), (slot, version))

    def test_booking_list_distinguishes_used_booking(self):
        self.assertIn("R-204 工作室 12月8日 14:00", self.flow.describe())
        self.assertIn("R-205 工作室 11月10日 14:00", self.flow.describe())
        self.flow.open("R-205")
        self.assertIn("利用済み・変更不可", self.flow.describe())
        self.assertNotIn("日程変更: change", self.flow.describe())
        with self.assertRaises(booking_flow.FlowError):
            self.flow.change()
        self.assertEqual(self.flow.phase, "detail")
        self.assertEqual(self.service.sent, [])
        self.flow.back()
        self.assertEqual(self.flow.phase, "list")

    def test_normal_commit_and_reopen(self):
        self.review()
        self.assertIn("変更前: 12月8日 14:00 / 変更先: 12月10日 14:00", self.flow.describe())
        intent = self.send()
        self.assert_saved("12-08", 1)
        outcome = self.service.process(intent)
        self.assertTrue(self.flow.receive(outcome))
        self.assertEqual(self.flow.phase, "complete")
        self.flow.leave()
        self.assertEqual(self.flow.phase, "suspended")
        self.flow.reopen()
        self.assertIn("確定日時: 12月10日 14:00", self.flow.describe())
        self.assert_saved("12-10", 2)

    def test_editing_and_interruption_keep_only_the_draft(self):
        self.review()
        self.flow.back()
        self.assertEqual(self.flow.phase, "choose")
        self.flow.leave()
        self.flow.reopen()
        self.assertEqual(self.flow.phase, "choose")
        self.assertEqual(self.flow.checkpoint.target, "12-10")
        self.assertEqual(self.service.sent, [])
        self.assert_saved("12-08", 1)
        self.flow.select("12-11")
        self.assertEqual(self.send().target, "12-11")

    def test_double_submit_and_duplicate_apply_use_one_change(self):
        self.review()
        intent = self.send()
        with self.assertRaises(booking_flow.FlowError):
            self.flow.submit()
        self.assertEqual(self.service.sent, [intent])
        outcome = self.service.process(intent)
        self.assertIs(outcome, self.service.process(intent))
        with self.assertRaises(booking_flow.FlowError):
            self.service.process(replace(intent, target="12-11"))
        self.assertTrue(self.flow.receive(outcome))
        self.assertFalse(self.flow.receive(outcome))
        self.assert_saved("12-10", 2)

    def test_slot_conflict_retains_booking_and_ignores_old_response(self):
        self.review()
        self.service.taken.add("12-10")
        first = self.send()
        conflict = self.service.process(first)
        self.assertEqual(conflict.kind, "slot-conflict")
        self.flow.receive(conflict)
        self.assertEqual(self.flow.phase, "conflict")
        self.assert_saved("12-08", 1)
        self.flow.change()
        with self.assertRaises(booking_flow.FlowError):
            self.flow.select("12-10")
        self.flow.select("12-11")
        second = self.send()
        self.assertNotEqual(first.id, second.id)
        self.assertFalse(self.flow.receive(conflict))
        self.assertEqual(self.flow.phase, "pending")
        self.flow.receive(self.service.process(second))
        self.assertEqual(self.flow.phase, "complete")
        self.assert_saved("12-11", 2)

    def test_all_slots_taken_returns_to_current_booking(self):
        self.review()
        self.service.taken.update(("12-10", "12-11"))
        intent = self.send()
        self.flow.receive(self.service.process(intent))
        self.flow.change()
        options = self.flow.describe()
        self.assertIn("選べる空き枠がありません", options)
        self.assertIn("確定日時: 12月8日 14:00", options)
        self.assertIn("予約詳細に戻る: back", options)
        self.assertNotIn("select", options)
        self.flow.back()
        self.assertEqual(self.flow.phase, "detail")
        self.assert_saved("12-08", 1)

    def test_status_recovers_a_change_committed_without_client_response(self):
        self.review()
        intent = self.send()
        committed = self.service.process(intent)
        self.flow.timeout()
        self.assertEqual(self.flow.phase, "unknown")
        self.assertIn("確定日時: 12月8日 14:00", self.flow.describe())
        self.flow.check()
        self.assertEqual(self.flow.phase, "complete")
        self.assertIn("確定日時: 12月10日 14:00", self.flow.describe())
        self.assertEqual(self.service.sent, [intent])
        self.assertFalse(self.flow.receive(committed))
        self.assert_saved("12-10", 2)

    def test_reopen_resolves_terminal_outcomes_with_no_response(self):
        cases = (("complete", False, False), ("conflict", True, False), ("failed", False, True))
        for phase, taken, reject in cases:
            with self.subTest(phase=phase):
                service = booking_flow.BookingService()
                flow = booking_flow.BookingFlow(service)
                flow.open("R-204")
                flow.change()
                flow.select("12-10")
                if taken:
                    service.taken.add("12-10")
                flow.submit()
                intent = service.sent[-1]
                outcome = service.process(intent, reject=reject)
                flow.leave()
                flow.reopen()
                self.assertEqual(flow.phase, phase)
                self.assertEqual(flow.checkpoint.outcome, outcome)
                self.assertNotIn("同じ変更を再送", flow.describe())
                self.assertEqual(service.sent, [intent])

    def test_unregistered_outcome_requires_same_intent_after_reopen(self):
        self.review()
        first = self.send()
        self.flow.leave()
        self.flow.reopen()
        self.assertEqual(self.flow.phase, "unknown")
        self.assertIn("確定日時は予約の確認値です。この変更依頼の結果はまだ不明です", self.flow.describe())
        self.assertIsNone(self.service.lookup(first.id))
        self.flow.check()
        self.assertEqual(self.flow.phase, "unknown")
        for blocked in (self.flow.change, self.flow.back, self.flow.submit):
            with self.assertRaises(booking_flow.FlowError):
                blocked()
        self.assert_saved("12-08", 1)
        self.flow.retry()
        self.assertEqual(self.service.sent, [first, first])
        original_send, retried_send = self.service.sent
        delayed = self.service.process(original_send)
        self.assertTrue(self.flow.receive(delayed))
        self.assertIs(delayed, self.service.process(retried_send))
        self.assertFalse(self.flow.receive(delayed))
        self.assertEqual(self.flow.phase, "complete")
        self.assert_saved("12-10", 2)

    def test_confirmed_failure_allows_new_intent(self):
        self.review()
        first = self.send()
        failure = self.service.process(first, reject=True)
        self.flow.timeout()
        self.flow.check()
        self.assertEqual(self.flow.phase, "failed")
        self.assert_saved("12-08", 1)
        with self.assertRaises(booking_flow.FlowError):
            self.flow.retry()
        self.flow.change()
        self.flow.select("12-10")
        second = self.send()
        self.assertNotEqual(first.id, second.id)
        self.assertIs(failure, self.service.process(first))
        self.flow.receive(self.service.process(second))
        self.assertEqual(self.flow.phase, "complete")
        self.assert_saved("12-10", 2)

    def test_external_booking_change_does_not_resolve_unknown_intent(self):
        self.review()
        first = self.send()
        self.flow.leave()
        other_tab = booking_flow.BookingFlow(self.service)
        other_tab.open("R-204")
        other_tab.change()
        other_tab.select("12-11")
        other_tab.submit()
        other_tab.receive(self.service.process(self.service.sent[-1]))
        self.flow.reopen()
        self.flow.check()
        self.assertEqual(self.flow.phase, "unknown")
        self.assertIn("確定日時: 12月11日 14:00", self.flow.describe())
        self.flow.retry()
        conflict = self.service.process(first)
        self.assertEqual(conflict.kind, "booking-conflict")
        self.flow.receive(conflict)
        self.assertEqual(self.flow.phase, "conflict")
        self.assert_saved("12-11", 2)

    def test_reopen_distinguishes_an_applied_intent_from_latest_booking(self):
        self.review()
        self.service.process(self.send())
        self.flow.leave()
        other_tab = booking_flow.BookingFlow(self.service)
        other_tab.open("R-204")
        other_tab.change()
        other_tab.select("12-11")
        other_tab.submit()
        self.service.process(self.service.sent[-1])
        self.flow.reopen()
        self.assertEqual(self.flow.phase, "complete")
        screen = self.flow.describe()
        self.assertIn("最後に確認した確定日時: 12月11日 14:00", screen)
        self.assertIn("この変更依頼は 12月10日 14:00 への変更として確定しました", screen)
        self.assert_saved("12-11", 3)

    def test_cli_recovers_and_reopens_the_saved_booking(self):
        commands = (
            "open R-204", "change", "select 12-10", "submit", "leave", "reopen",
            "check", "retry", "process", "deliver", "reopen", "quit",
        )
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT)],
            input="\n".join(commands) + "\n",
            capture_output=True,
            encoding="utf-8",
            check=True,
            cwd=ROOT,
        )
        self.assertIn("結果は照会先で見つかりません", result.stdout)
        self.assertEqual(result.stdout.count("[complete]"), 2)
        self.assertIn("確定日時: 12月10日 14:00", result.stdout)
        self.assertNotIn("操作ID: op-2", result.stdout)


if __name__ == "__main__":
    unittest.main()
