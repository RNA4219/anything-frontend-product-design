"""実サイトで観察した経路を検索し、最新の記録を1条件1行で返す。"""

import argparse
import json
from pathlib import Path
import sys


DATA = Path(__file__).resolve().parents[1] / "research" / "product-journeys"
ROUNDS = ("walkthrough", "expansion")
TASKS = ("mug", "repair", "shirt", "friday", "store", "reset", "returns")
STATES = ("confirmed", "partial", "unavailable", "precondition_absent")


def compact_frame(frame, include_pairs=False):
    metrics = frame["metrics"]
    if metrics is None:
        return {"screen": frame["screen"], "metrics": None}
    result = {
        "controls": metrics["visible_controls"],
        "text_box_pct": metrics["text_box_percent"],
        "flat_band_css_px": metrics["flat_band"]["height_css_px"],
        "scroll_y_css_px": frame["scroll_y_css_px"],
    }
    if include_pairs and frame.get("measured_pairs"):
        result["measured_pairs"] = frame["measured_pairs"]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brand", help="ブランド名の部分一致（例 Spotify、紀伊國屋）")
    parser.add_argument("--task", choices=TASKS)
    parser.add_argument("--mode", choices=("desktop", "mobile"))
    parser.add_argument("--status", choices=STATES)
    parser.add_argument("--view", choices=("all", "layout", "actions"), default="all",
                        help="余白・密度だけは layout、操作の回数だけは actions")
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit には1以上を指定してください")

    latest = {}
    for edition in ROUNDS:
        rows = json.loads((DATA / edition / "visits.json").read_text(encoding="utf-8"))
        for row in rows:
            latest[row["id"]] = (edition, row)

    count = 0
    for code, (edition, row) in sorted(latest.items()):
        if args.brand and args.brand.casefold() not in row["brand"].casefold():
            continue
        if args.task and args.task != row["task"]:
            continue
        if args.mode and args.mode != row["mode"]:
            continue
        if args.status and args.status != row["status"]:
            continue
        result = {"id": code, "brand": row["brand"], "status": row["status"],
                  "previous_status": row.get("previous_status")}
        if args.view in ("all", "actions"):
            result["actions"] = row["action_counts"]
        if args.view in ("all", "layout"):
            result["start"] = compact_frame(row["frames"]["start"], args.view == "layout")
            result["end"] = compact_frame(row["frames"]["end"], args.view == "layout")
        result["finding"] = row["finding"]
        result["source"] = f"research/product-journeys/{edition}/{row['task']}.md#{code}"
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        count += 1
        if count == args.limit:
            break
    if not count:
        print("指定条件に一致する観察は0件です。", file=sys.stderr)


if __name__ == "__main__":
    main()
