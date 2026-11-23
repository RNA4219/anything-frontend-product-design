#!/usr/bin/env python3
"""Executable browser checks for a permitted local developer environment.

Exit 0 = tested cases passed; 1 = observed assertion failure; 2 = BLOCKED.
Requires Playwright and its Chromium, or --executable. Never disables sandbox.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading


def exception_status(phase):
    return 'BLOCKED' if phase == 'setup' else 'ERROR_TEST_EXECUTION'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    evidence = {'status': 'BLOCKED', 'cases': [], 'screen_reader': 'NOT_RUN'}
    server = None
    phase = 'setup'
    case = None
    try:
        from playwright.sync_api import sync_playwright
        root = Path(__file__).resolve().parents[1] / 'examples'
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(root)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/booking-controls.html'
        with sync_playwright() as p:
            options = {'headless': True, 'chromium_sandbox': True}
            if args.executable: options['executable_path'] = args.executable
            browser = p.chromium.launch(**options)
            evidence['engine'] = browser.version
            page = browser.new_page(viewport={'width': 1280, 'height': 800})
            phase = 'navigation'
            case = 'load-fixture'
            page.goto(url); page.locator('#open').wait_for()
            phase = 'interaction'
            case = 'payload'
            page.locator('#payload').click()
            assert json.loads(page.locator('#payload-result').inner_text()) == {'bookingId':'R-204'}
            evidence['cases'].append({'id':'payload','result':'PASS'})
            case = 'keyboard-unavailable-cancel'
            for key in ['Enter', 'Space']:
                page.locator('#open').press(key)
                assert page.evaluate('document.activeElement.id') == 'slot'
                page.locator('#confirm').press(key)
                assert page.locator('#count').inner_text() == '0'
                page.locator('#slot').press('Escape')
                assert not page.locator('#edit').is_visible()
                assert page.evaluate('document.activeElement.id') == 'open'
            evidence['cases'].append({'id':'keyboard-unavailable-cancel','result':'PASS'})
            case = 'confirm-and-reopen-cancel'
            page.locator('#open').click(); page.locator('#slot').select_option('12月10日 14:00')
            page.locator('#confirm').press('Space')
            assert page.locator('#count').inner_text() == '1'
            page.locator('#open').click(); page.locator('#slot').press('Escape')
            assert page.locator('#count').inner_text() == '1'
            evidence['cases'].append({'id':'confirm-and-reopen-cancel','result':'PASS'})
            case = 'modal-traversal-invoker-removed'
            page.locator('#open').click()
            for _ in range(8):
                page.keyboard.press('Tab')
                assert page.evaluate('document.activeElement === document.body || document.querySelector("#edit").contains(document.activeElement)')
            page.locator('summary').click(); page.locator('#remove-opener').click(); page.locator('#cancel').click()
            assert page.evaluate('document.activeElement.id') == 'bookings'
            assert page.locator('#outside').is_enabled()
            page.locator('#outside').fill('background restored')
            assert page.locator('#outside').input_value() == 'background restored'
            evidence['cases'].append({'id':'modal-traversal-invoker-removed','result':'PASS'})
            case = 'nonmodal-preserve-outside-focus'
            page.locator('#help-open').click(); page.locator('#outside').fill('another task')
            page.evaluate('document.querySelector("#help").close()')
            assert page.evaluate('document.activeElement.id') == 'outside'
            evidence['cases'].append({'id':'nonmodal-preserve-outside-focus','result':'PASS'})
            browser.close(); evidence['status'] = 'PASS_TESTED_CASES_ONLY'
    except AssertionError as error:
        evidence.update(status='FAIL', phase=phase, case=case, reason=str(error) or 'Browser assertion failed')
    except Exception as error:
        evidence.update(status=exception_status(phase), phase=phase, case=case,
                        reason=f'{type(error).__name__}: {str(error)[:1000]}')
    finally:
        if server:
            server.shutdown(); server.server_close()
    text = json.dumps(evidence, ensure_ascii=False, indent=2)
    print(text)
    if args.output: args.output.write_text(text + '\n', encoding='utf-8')
    return 0 if evidence['status'].startswith('PASS') else 2 if evidence['status'] == 'BLOCKED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
