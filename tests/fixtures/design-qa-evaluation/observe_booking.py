"""Edge で予約変更の自動ケースを操作し、観測値を JSON に保存する。"""

import argparse
import hashlib
import json
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright


FIXTURE = Path(__file__).resolve().parent


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def days(text):
    return [int(day) for day in re.findall(r"12月(\d+)日", text)]


def current(page):
    return days(page.locator("#current").inner_text())[0]


def count(page):
    return int(page.locator("#count").inner_text())


def review(page, slot):
    page.locator("#open").click()
    choose_and_review(page, slot)


def choose_and_review(page, slot):
    page.locator("#slot").select_option(slot)
    page.locator("#review").click()


def submit(page):
    page.locator("#submit").click()


def observe(page, base, variant):
    observations = []

    def start(scenario):
        page.goto(f"{base}?variant={variant}&scenario={scenario}")

    def capture(case_id, **actual):
        observations.append({
            "case_id": case_id,
            "method": "automated",
            "evidence": f"observe_booking.py#{case_id}",
            "actual": actual,
        })

    start("normal")
    before = current(page)
    review(page, "10")
    review_from, review_to = days(page.locator("#change").inner_text())
    submit(page)
    after = current(page)
    page.reload()
    capture(
        "confirm", before_review=before, review_from=review_from, review_to=review_to,
        after_submit=after, after_reload=current(page), commit_count=count(page),
    )

    start("conflict")
    review(page, "10")
    submit(page)
    capture("conflict-state", current_day=current(page), commit_count=count(page))
    if not page.locator("#editor").is_visible():
        page.locator("#open").click()
    choose_and_review(page, "11")
    submit(page)
    after = current(page)
    page.reload()
    capture("conflict-recover", after_submit=after, after_reload=current(page), commit_count=count(page))

    start("lost-reply")
    review(page, "10")
    submit(page)
    if page.locator("#lookup").is_visible():
        page.locator("#lookup").click()
        review(page, "10")
    submit(page)
    after = current(page)
    page.reload()
    capture("lost-reply-retry", final_day=after, after_reload=current(page), commit_count=count(page))
    return observations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=("a", "b"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    viewport = {"width": 1280, "height": 800}
    digest = hashlib.sha256((FIXTURE / "booking.html").read_bytes()).hexdigest()
    handler = partial(QuietHandler, directory=FIXTURE)
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="msedge")
                try:
                    page = browser.new_page(viewport=viewport)
                    page.set_default_timeout(5000)
                    base = f"http://127.0.0.1:{server.server_port}/booking.html"
                    document = {
                        "task_id": "booking-change",
                        "build": f"booking-{args.variant}:sha256:{digest}",
                        "automated_environment": {
                            "browser": "Microsoft Edge",
                            "version": browser.version,
                            "viewport": viewport,
                        },
                        "observations": observe(page, base, args.variant),
                    }
                finally:
                    browser.close()
        finally:
            server.shutdown()
            thread.join()

    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
