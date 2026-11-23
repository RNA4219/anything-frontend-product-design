"""予約変更の入口を比較する、架空データの対話式試作。"""

import argparse
import json
from dataclasses import asdict, dataclass, replace


CHANGEABLE = "確定・変更可"
USED = "利用済み"
ROOM = "工作室"
SLOTS = {"12-10": "14:00", "12-11": "14:00"}
TARGET = "R-204"
DESTINATION = "12-10"
TASK = "12月8日 14:00の工作室の予約を12月10日 14:00へ変更し、結果を確かめる。"
UNKNOWN_TIME_TASK = (
    "12月8日の工作室の予約を12月10日 14:00へ変更したい。変更元の時刻や予約番号の控えが手元にない。"
    "表示される情報から自分の予約を特定できなければ、予約確認の通知を調べるまで変更を保留する。"
)


def show_time(date, time):
    month, day = map(int, date.split("-"))
    return f"{month}月{day}日 {time}"


@dataclass(frozen=True)
class Booking:
    id: str
    date: str
    time: str
    status: str
    room: str = ROOM

    def label(self):
        return f"{self.id} | {self.room} | {show_time(self.date, self.time)} | {self.status}"


def initial_bookings(scenario):
    bookings = [
        Booking(TARGET, "12-08", "14:00", CHANGEABLE),
        Booking("R-205", "11-10", "14:00", USED),
    ]
    if scenario in ("two-changeable", "unknown-time"):
        bookings.insert(0, Booking("R-206", "12-08", "10:00", CHANGEABLE))
    return {booking.id: booking for booking in bookings}


class BookingChoice:
    def __init__(self, variant, scenario):
        self.variant = variant
        self.scenario = scenario
        self.original = initial_bookings(scenario)
        self.bookings = self.original.copy()
        self.group = None
        self.selected = None
        self.pending = None
        self.commands = []
        self.opened_ids = []
        self.changes = []
        self.reopened_at = None
        self.confirmed_target_seen = False

    def groups(self):
        if self.variant == "room":
            return {"workshop": (ROOM, list(self.bookings))}
        return {
            "changeable": (CHANGEABLE, [b.id for b in self.bookings.values() if b.status == CHANGEABLE]),
            "used": (USED, [b.id for b in self.bookings.values() if b.status == USED]),
        }

    def available_slots(self, booking):
        occupied = {(b.date, b.time) for b in self.bookings.values() if b.room == booking.room}
        return {date: time for date, time in SLOTS.items() if (date, time) not in occupied}

    def show(self):
        if self.selected is not None:
            booking = self.bookings[self.selected]
            print(booking.label())
            if self.pending is not None:
                print(f"変更前 {show_time(booking.date, booking.time)}")
                print(f"変更後 {show_time(self.pending, SLOTS[self.pending])}")
                print("confirm 変更を確定 / back 候補選択へ戻る")
            elif booking.status == CHANGEABLE:
                for date, time in self.available_slots(booking).items():
                    print(f"slot {date} | {show_time(date, time)}")
            return

        if self.group is None:
            print("予約一覧")
            for key, (label, _) in self.groups().items():
                print(f"group {key} | {label}")
            return

        label, booking_ids = self.groups()[self.group]
        print(f"予約一覧 / {label}")
        for booking_id in booking_ids:
            print(f"open {self.bookings[booking_id].label()}")

    def step(self, command):
        message = self.perform(command.split())
        self.commands.append({"command": command, "accepted": message is None})
        if message is not None:
            print(f"操作できません。{message}")
        self.show()

    def perform(self, words):
        match words:
            case ["group", key] if self.group is None and key in self.groups():
                self.group = key
            case ["open", key] if self.group is not None and self.selected is None:
                _, booking_ids = self.groups()[self.group]
                if key not in booking_ids:
                    return "表示されている予約から選んでください。"
                self.selected = key
                self.opened_ids.append(key)
                if key == TARGET and self.reopened_at == len(self.changes) and self.changes:
                    booking = self.bookings[key]
                    self.confirmed_target_seen = (booking.date, booking.time) == (DESTINATION, SLOTS[DESTINATION])
            case ["slot", date] if self.selected is not None and self.pending is None:
                booking = self.bookings[self.selected]
                if booking.status != CHANGEABLE or date not in self.available_slots(booking):
                    return "この予約を指定の枠へ変更できません。"
                self.pending = date
            case ["confirm"] if self.pending is not None:
                original = self.bookings[self.selected]
                updated = replace(original, date=self.pending, time=SLOTS[self.pending])
                self.bookings[updated.id] = updated
                self.changes.append({"before": asdict(original), "after": asdict(updated)})
                self.pending = None
                print(f"変更を確定しました。{updated.label()}")
            case ["back"] if self.pending is not None:
                self.pending = None
            case ["back"] if self.selected is not None:
                self.selected = None
            case ["back"] if self.group is not None:
                self.group = None
            case ["reopen"]:
                self.group = self.selected = self.pending = None
                self.reopened_at = len(self.changes)
                print("予約一覧を再表示しました。")
            case _:
                return "現在の画面にある操作を使ってください。"
        return None

    def result(self):
        target = self.original[TARGET]
        expected = replace(target, date=DESTINATION, time=SLOTS[DESTINATION])
        unchanged = all(self.bookings[key] == value for key, value in self.original.items() if key != TARGET)
        correct_change = self.changes == [{"before": asdict(target), "after": asdict(expected)}]
        identifiable = self.scenario != "unknown-time"
        result = {
            "data": "synthetic",
            "task": "booking-change",
            "variant": self.variant,
            "scenario": self.scenario,
            "commands": self.commands,
            "opened_ids": self.opened_ids,
            "changes": self.changes,
            "bookings": [asdict(booking) for booking in self.bookings.values()],
            "booking-change-find": identifiable and TARGET in self.opened_ids,
            "booking-change-confirm": identifiable and correct_change and unchanged and self.confirmed_target_seen,
        }
        if not identifiable:
            result["outcome"] = "changed_without_identification" if self.changes else "deferred_without_change"
        return result


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="終了コード 0 は課題達成、1 は試作を終了した時点で課題未達、2 は引数エラー。",
    )
    parser.add_argument("--variant", required=True, choices=("status", "room"), help="状態別または部屋別の入口。")
    parser.add_argument(
        "--scenario", default="base", choices=("base", "two-changeable", "unknown-time"),
        help="two-changeable は同室・同日に変更可能な予約を追加。unknown-time は同じ予約で変更元の時刻が分からない課題。",
    )
    parser.add_argument(
        "--steps", nargs="+", metavar="操作",
        help='表示された操作を引数1個に1つ渡す。例 "group workshop" "open R-204"。省略すると対話入力。',
    )
    args = parser.parse_args()
    session = BookingChoice(args.variant, args.scenario)

    task = UNKNOWN_TIME_TASK if args.scenario == "unknown-time" else TASK
    print(f"架空データの試作 | {task}")
    print("back 一つ戻る / reopen 予約一覧を再表示 / quit 終了")
    session.show()
    if args.steps is not None:
        for command in args.steps:
            print(f"> {command}")
            if command == "quit":
                break
            session.step(command)
    else:
        while True:
            try:
                command = input("> ").strip()
            except EOFError:
                break
            if command == "quit":
                break
            session.step(command)
        print()

    result = session.result()
    if result.get("outcome") == "deferred_without_change":
        print("予約内容に変更はありません。予約確認の通知で対象を特定するまで保留です。")
    elif result.get("outcome") == "changed_without_identification":
        print("変更は記録されました。予約確認の通知で対象を特定できていないため、課題は未達です。")
    print("RESULT " + json.dumps(result, ensure_ascii=False))
    return 0 if result["booking-change-find"] and result["booking-change-confirm"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
