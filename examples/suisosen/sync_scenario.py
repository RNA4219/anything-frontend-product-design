"""prologue.ks を単体 HTML に反映する。--check で同期状況だけを調べる。"""
import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
HTML = HERE.parents[1] / "docs" / "index.html"
OPEN = '<script id="scenario" type="text/plain">\n'
CLOSE = "</script>"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    scenario = (HERE / "prologue.ks").read_text(encoding="utf-8").rstrip("\n") + "\n"
    if "</script" in scenario.casefold():
        parser.error("台本に script の終了タグを含めることはできません")
    page = HTML.read_text(encoding="utf-8")
    if page.count(OPEN) != 1:
        parser.error("HTML 内の台本の開始位置を特定できません")
    head, _, rest = page.partition(OPEN)
    _, end, tail = rest.partition(CLOSE)
    if not end:
        parser.error("HTML 内の台本の終端がありません")
    merged = head + OPEN + scenario + end + tail
    if page != merged:
        if args.check:
            parser.exit(1, "HTML に未反映の台本変更があります\n")
        HTML.write_bytes(merged.encode("utf-8"))

if __name__ == "__main__":
    main()
