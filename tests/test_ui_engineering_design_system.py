"""予約変更をローカル HTTP 上の実ブラウザーで検証する。"""

import contextlib
import functools
import os
from pathlib import Path
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

try:
    from playwright.sync_api import expect, sync_playwright
except ModuleNotFoundError as error:
    if error.name != "playwright":
        raise
    sync_playwright = None


EXAMPLE = (
    Path(__file__).resolve().parents[1]
    / "modules" / "ui-engineering-design-system" / "examples" / "booking-change"
)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@unittest.skipUnless(sync_playwright, "ブラウザー試験には Playwright が必要")
class BookingChangeBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = functools.partial(QuietHandler, directory=str(EXAMPLE))
        resources = contextlib.ExitStack()
        cls.addClassCleanup(resources.close)
        server = resources.enter_context(ThreadingHTTPServer(("127.0.0.1", 0), handler))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        resources.callback(thread.join)
        resources.callback(server.shutdown)
        cls.url = f"http://127.0.0.1:{server.server_port}/"
        playwright = resources.enter_context(sync_playwright())
        channel = os.environ.get("BOOKING_BROWSER_CHANNEL")
        cls.browser = playwright.chromium.launch(channel=channel)
        resources.callback(cls.browser.close)
        print(f"予約変更ブラウザー: {cls.browser.version} ({channel or 'chromium'})")

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1024, "height": 768})
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.assertEqual(self.errors, [])

    def element(self, element_id):
        return self.page.locator(f"#{element_id}")

    def state(self, state):
        expect(self.element("booking-app")).to_have_attribute("data-state", state)

    def open(self, scenario=""):
        suffix = f"?scenario={scenario}" if scenario else ""
        self.page.goto(self.url + suffix)
        self.state("list")

    def review_first_slot(self):
        self.element("open-change").click()
        self.element("slot-10").check()
        self.element("review-change").click()
        self.state("confirm")

    def assert_date(self, element_id, expected):
        date = self.element(element_id)
        expect(date).to_be_visible()
        expect(date).to_have_text(expected)

    def assert_no_horizontal_scroll(self):
        self.assertTrue(self.page.evaluate(
            "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
        ))

    def test_keyboard_completion_and_reload(self):
        self.open()
        expect(self.page.get_by_text("R-204", exact=False).first).to_be_visible()
        expect(self.page.get_by_text("R-205", exact=False).first).to_be_visible()
        key = self.page.keyboard
        key.press("Tab")
        expect(self.element("open-change")).to_be_focused()
        key.press("Enter")
        self.state("choose")
        expect(self.element("choose-heading")).to_be_focused()
        key.press("Tab")
        expect(self.element("slot-10")).to_be_focused()
        key.press("Space")
        key.press("ArrowRight")
        expect(self.element("slot-11")).to_be_checked()
        key.press("ArrowLeft")
        expect(self.element("slot-10")).to_be_checked()
        key.press("Tab")
        expect(self.element("review-change")).to_be_focused()
        key.press("Enter")
        self.state("confirm")
        expect(self.element("confirm-heading")).to_be_focused()
        self.assert_date("before-date", "12月8日 14:00")
        self.assert_date("after-date", "12月10日 14:00")
        for _ in range(2):
            if self.element("submit-change").evaluate("(button) => document.activeElement === button"):
                break
            key.press("Tab")
        expect(self.element("submit-change")).to_be_focused()
        key.press("Enter")
        self.state("success")
        expect(self.element("success-heading")).to_be_focused()
        self.page.reload()
        self.state("list")
        self.assert_date("current-date", "12月10日 14:00")

    def test_edit_selection_preserves_choice_and_focus(self):
        self.open()
        self.review_first_slot()
        self.element("edit-selection").click()
        self.state("choose")
        expect(self.element("slot-10")).to_be_checked()
        expect(self.element("slot-10")).to_be_focused()
        self.element("slot-11").check()
        self.element("review-change").click()
        self.element("submit-change").click()
        self.state("success")
        self.page.reload()
        self.assert_date("current-date", "12月11日 14:00")

    def test_touch_at_320_css_pixels_recovers_from_conflict(self):
        with self.browser.new_context(
            viewport={"width": 320, "height": 700}, has_touch=True, is_mobile=True,
        ) as mobile:
            self.page = mobile.new_page()
            self.page.on("pageerror", lambda error: self.errors.append(str(error)))
            self.open("conflict")
            self.assert_no_horizontal_scroll()
            self.element("open-change").tap()
            self.page.locator("label").filter(has=self.element("slot-10")).tap()
            self.element("review-change").tap()
            self.assert_no_horizontal_scroll()
            self.element("submit-change").tap()
            self.state("conflict")
            expect(self.element("slot-10")).to_be_disabled()
            self.assert_date("choose-current-date", "12月8日 14:00")
            self.assert_no_horizontal_scroll()
            self.page.locator("label").filter(has=self.element("slot-11")).tap()
            self.element("review-change").tap()
            self.element("submit-change").tap()
            self.state("success")
            self.assert_no_horizontal_scroll()
            self.assert_date("success-date", "12月11日 14:00")

    def test_unknown_applied_requires_check_and_survives_reload(self):
        self.open("unknown-applied")
        self.review_first_slot()
        self.element("submit-change").focus()
        self.page.keyboard.press("Space")
        self.state("pending")
        expect(self.element("submit-change")).to_be_focused()
        expect(self.page.get_by_role("status")).to_contain_text("送信しています")
        self.page.keyboard.press("Space")
        self.state("unknown")
        self.page.reload()
        self.state("unknown")
        expect(self.element("unknown-heading")).to_be_focused()
        expect(self.element("submit-change")).to_be_hidden()
        self.element("check-current").click()
        self.state("checking")
        expect(self.page.get_by_role("status")).to_contain_text("予約を確認しています")
        self.state("success")
        self.assert_applied_once("unknown-applied")
        expect(self.element("success-heading")).to_be_focused()
        self.page.reload()
        self.state("list")
        self.assert_date("current-date", "12月10日 14:00")

    def assert_applied_once(self, scenario):
        record = self.page.evaluate(
            "(scenario) => JSON.parse(localStorage.getItem('booking-change-demo:v1:' + scenario))",
            scenario,
        )
        self.assertEqual(record["appliedCount"], 1)
        self.assertIsNone(record["operation"])

    def test_unknown_unapplied_rechecks_before_retry(self):
        self.open("unknown-unapplied")
        self.review_first_slot()
        self.element("submit-change").click()
        self.state("unknown")
        self.element("check-current").click()
        self.state("unchanged")
        expect(self.element("unchanged-heading")).to_be_focused()
        self.assert_date("unchanged-date", "12月8日 14:00")
        self.element("retry-change").click()
        self.state("confirm")
        self.assert_date("after-date", "12月10日 14:00")
        self.element("submit-change").click()
        self.state("success")
        self.assert_applied_once("unknown-unapplied")
        self.page.reload()
        self.assert_date("current-date", "12月10日 14:00")

    def test_storage_write_failure_never_reports_success(self):
        self.open()
        self.review_first_slot()
        self.page.evaluate("""() => {
            Storage.prototype.setItem = () => {
                throw new DOMException("試験用の保存エラー", "QuotaExceededError");
            };
        }""")
        self.element("submit-change").click()
        self.state("storage-error")
        self.page.reload()
        self.state("list")
        self.assert_date("current-date", "12月8日 14:00")


if __name__ == "__main__":
    unittest.main()
