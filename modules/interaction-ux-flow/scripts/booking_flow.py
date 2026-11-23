"""予約変更の操作と応答の順序を、プロセス内で再現する。"""

import sys
from collections.abc import Callable
from dataclasses import dataclass, replace
from inspect import signature
from itertools import count


SLOTS = {
    "11-10": "11月10日 14:00",
    "12-08": "12月8日 14:00",
    "12-10": "12月10日 14:00",
    "12-11": "12月11日 14:00",
}
OPTIONS = ("12-10", "12-11")


class FlowError(ValueError):
    """現在の画面・入力では実行できない操作。"""


@dataclass(frozen=True)
class Booking:
    id: str
    slot: str
    version: int = 1
    editable: bool = True


@dataclass(frozen=True)
class Intent:
    id: str
    booking: Booking
    target: str


@dataclass(frozen=True)
class Outcome:
    intent: Intent
    kind: str


class BookingService:
    """予約の正本と、操作IDごとの終端結果を保持する模擬サービス。"""

    def __init__(self) -> None:
        self.bookings = {
            "R-204": Booking("R-204", "12-08"),
            "R-205": Booking("R-205", "11-10", editable=False),
        }
        self.taken: set[str] = set()
        self.sent: list[Intent] = []
        self._results: dict[str, Outcome] = {}
        self._ids = count(1)

    def available(self, source: Booking) -> tuple[str, ...]:
        return tuple(slot for slot in OPTIONS if slot not in self.taken and slot != source.slot)

    def new_intent(self, booking: Booking, target: str) -> Intent:
        return Intent(f"op-{next(self._ids)}", booking, target)

    def lookup(self, operation_id: str) -> Outcome | None:
        return self._results.get(operation_id)

    def process(self, intent: Intent, *, reject: bool = False) -> Outcome:
        """処理と記録を1イベントで行う。応答の配信は呼び出し側が行う。"""
        recorded = self.lookup(intent.id)
        if recorded is not None:
            if recorded.intent != intent:
                raise FlowError("同じ操作IDで予約、版、または変更先を変えられません。")
            return recorded

        current = self.bookings[intent.booking.id]
        if reject:
            kind = "rejected"
        elif current != intent.booking:
            kind = "booking-conflict"
        elif not current.editable or intent.target not in self.available(current):
            kind = "slot-conflict"
        else:
            kind = "applied"
            self.bookings[current.id] = replace(
                current, slot=intent.target, version=current.version + 1
            )
        outcome = Outcome(intent, kind)
        self._results[intent.id] = outcome
        return outcome


@dataclass(frozen=True)
class Progress:
    phase: str = "list"
    booking: Booking | None = None
    target: str | None = None
    intent: Intent | None = None
    outcome: Outcome | None = None


class BookingFlow:
    """画面の状態を操作し、変更前の予約と送信済みの意図をチェックポイントに残す。"""

    def __init__(self, service: BookingService) -> None:
        self.service = service
        self.checkpoint = Progress()
        self.attached = True
        self.last_confirmed: Booking | None = None

    @property
    def phase(self) -> str:
        return self.checkpoint.phase if self.attached else "suspended"

    @property
    def current(self) -> Booking | None:
        source = self.checkpoint.booking
        return self.service.bookings[source.id] if source is not None else None

    def require(self, *phases: str) -> None:
        if self.phase not in phases:
            raise FlowError(f"状態 {self.phase} で実行できる操作を選んでください。")

    def open(self, booking_id: str) -> None:
        self.require("list")
        if booking_id not in self.service.bookings:
            raise FlowError("一覧にある予約IDを選んでください。")
        self.checkpoint = Progress("detail", self.service.bookings[booking_id])
        self.last_confirmed = self.current

    def change(self) -> None:
        self.require("detail", "conflict", "failed")
        current = self.current
        if current is None or not current.editable:
            raise FlowError("この予約は変更できません。")
        self.checkpoint = Progress("choose", current)
        self.last_confirmed = current

    def select(self, target: str) -> None:
        self.require("choose")
        source = self.checkpoint.booking
        if source is None or target not in self.service.available(source):
            raise FlowError("選択できる変更先を指定してください。")
        self.checkpoint = replace(self.checkpoint, phase="review", target=target)

    def back(self) -> None:
        self.require("detail", "choose", "review", "conflict", "failed", "complete")
        if self.phase == "review":
            self.checkpoint = replace(self.checkpoint, phase="choose")
        elif self.phase == "detail":
            self.checkpoint = Progress()
            self.last_confirmed = None
        else:
            self.last_confirmed = self.current
            self.checkpoint = Progress("detail", self.last_confirmed)

    def submit(self) -> None:
        self.require("review")
        source, target = self.checkpoint.booking, self.checkpoint.target
        assert source is not None and target is not None
        intent = self.service.new_intent(source, target)
        self.checkpoint = replace(self.checkpoint, phase="pending", intent=intent)
        self.service.sent.append(intent)

    def timeout(self) -> None:
        self.require("pending")
        self.checkpoint = replace(self.checkpoint, phase="unknown")

    def retry(self) -> None:
        self.require("unknown")
        intent = self.checkpoint.intent
        assert intent is not None
        self.checkpoint = replace(self.checkpoint, phase="pending")
        self.service.sent.append(intent)

    def receive(self, outcome: Outcome) -> bool:
        if self.phase not in ("pending", "unknown") or outcome.intent != self.checkpoint.intent:
            return False
        phases = {
            "applied": "complete",
            "slot-conflict": "conflict",
            "booking-conflict": "conflict",
            "rejected": "failed",
        }
        self.checkpoint = replace(self.checkpoint, phase=phases[outcome.kind], outcome=outcome)
        self.last_confirmed = self.current
        return True

    def check(self) -> str:
        self.require("unknown")
        intent = self.checkpoint.intent
        assert intent is not None
        outcome = self.service.lookup(intent.id)
        if outcome is None:
            self.last_confirmed = self.current
            return "操作結果は照会先で見つかりません。"
        self.receive(outcome)
        return "操作結果と現在の予約を確認しました。"

    def leave(self) -> None:
        self.attached = False

    def reopen(self) -> str | None:
        self.attached = True
        if self.phase == "pending":
            self.timeout()
        if self.phase == "unknown":
            return self.check()
        self.last_confirmed = self.current
        return None

    def describe(self) -> str:
        lines = [f"[{self.phase}]"]
        if self.phase == "list":
            for booking in self.service.bookings.values():
                status = "確定・変更可" if booking.editable else "利用済み"
                lines.append(f"{booking.id} 工作室 {SLOTS[booking.slot]}（{status}）")
            lines.append("予約を開く: open <予約ID>")
            return "\n".join(lines)
        if self.phase == "suspended":
            return "[suspended] 予約画面を閉じました。開き直す: reopen"

        current = self.last_confirmed
        source, target, intent = (
            self.checkpoint.booking, self.checkpoint.target, self.checkpoint.intent
        )
        assert current is not None and source is not None
        lines.append(f"{current.id} 工作室 最後に確認した確定日時: {SLOTS[current.slot]}")
        if self.phase == "review":
            assert target is not None
            lines.append(f"変更前: {SLOTS[source.slot]} / 変更先: {SLOTS[target]}")
        elif self.phase in ("pending", "unknown"):
            assert target is not None
            lines.append(f"依頼時の予約日時: {SLOTS[source.slot]} / 依頼した変更先: {SLOTS[target]}")
        if intent is not None:
            lines.append(f"操作ID: {intent.id}")

        if self.phase == "detail":
            if current.editable:
                lines.append("日程変更: change / 一覧に戻る: back")
            else:
                lines.extend(("利用済み・変更不可", "一覧に戻る: back"))
        elif self.phase == "choose":
            options = self.service.available(source)
            lines.extend(f"{slot} {SLOTS[slot]}" for slot in options)
            if target in options:
                lines.append(f"選択中: {SLOTS[target]}")
            if options:
                lines.append("変更先を選ぶ: select <枠ID>")
            else:
                lines.append("選べる空き枠がありません。表示中の予約は確定済みです。")
            lines.append("予約詳細に戻る: back")
        elif self.phase == "review":
            lines.append("変更を確定する: submit / 日時選択に戻る: back")
        elif self.phase == "pending":
            lines.append("変更を送信しました。応答を待っています。")
        elif self.phase == "unknown":
            lines.append("表示中の確定日時は予約の確認値です。この変更依頼の結果はまだ不明です。")
            lines.append("同じ操作IDで再送した場合、予約の変更は1回までです。")
            lines.append("依頼の結果を確認: check / 同じ変更を再送: retry")
        elif self.phase == "conflict":
            outcome = self.checkpoint.outcome
            assert outcome is not None
            reason = (
                "選択した枠は埋まりました。"
                if outcome.kind == "slot-conflict"
                else "元の予約が更新されました。"
            )
            lines.append(f"{reason} 別の日時を選ぶ: change / 予約詳細に戻る: back")
        elif self.phase == "failed":
            lines.append("変更の未適用が確定しました。日時を選び直す: change / 予約詳細に戻る: back")
        elif self.phase == "complete":
            assert target is not None
            lines.append(f"この変更依頼は {SLOTS[target]} への変更として確定しました。")
            lines.append("開き直す: reopen / 予約詳細に戻る: back")
        return "\n".join(lines)


def run() -> None:
    service = BookingService()
    flow = BookingFlow(service)

    def take(slot: str) -> str:
        if slot not in service.available(service.bookings["R-204"]):
            raise FlowError("模擬サービスで競合させる空き枠を指定してください。")
        service.taken.add(slot)
        return f"模擬サービス: 別の利用者が {SLOTS[slot]} を確保しました。"

    def process(mode: str = "apply") -> str:
        if not service.sent or mode not in ("apply", "reject"):
            raise FlowError("送信済みの操作に process または process reject を指定してください。")
        outcome = service.process(service.sent[-1], reject=mode == "reject")
        return f"模擬サービス: {outcome.intent.id} の結果を保存しました。応答は未配信です。"

    def deliver(operation_id: str = "") -> str:
        intent = flow.checkpoint.intent
        if not operation_id and intent is not None:
            operation_id = intent.id
        outcome = service.lookup(operation_id)
        if outcome is None:
            raise FlowError("配信できる応答が見つかりません。")
        if flow.receive(outcome):
            return f"模擬サービス: {operation_id} の応答を受け取りました。"
        return f"模擬サービス: {operation_id} の応答で現在の状態は変わりません。"

    commands: dict[str, Callable[..., str | None]] = {
        "open": flow.open, "change": flow.change, "select": flow.select,
        "back": flow.back, "submit": flow.submit, "check": flow.check,
        "retry": flow.retry, "leave": flow.leave, "reopen": flow.reopen,
        "take": take, "process": process, "deliver": deliver, "timeout": flow.timeout,
    }
    print("予約変更の試作。help で操作一覧、quit で終了します。")
    print(flow.describe())
    while True:
        try:
            parts = input("> " if sys.stdin.isatty() else "").split()
        except EOFError:
            return
        if not parts:
            continue
        name, *args = parts
        if name == "quit":
            return
        if name == "help":
            print("操作: open <予約ID> / change / select <枠ID> / back / submit / check / retry / leave / reopen")
            print("模擬サービス: take <枠ID> / process [reject] / deliver [操作ID] / timeout")
            continue
        action = commands.get(name)
        if action is None:
            print("help で操作一覧を確認してください。")
            continue
        try:
            signature(action).bind(*args)
        except TypeError:
            print("引数は help で確認できます。")
            continue
        try:
            notice = action(*args)
        except FlowError as error:
            print(f"操作できません。{error}")
        else:
            if notice:
                print(notice)
        print(flow.describe())


if __name__ == "__main__":
    run()
