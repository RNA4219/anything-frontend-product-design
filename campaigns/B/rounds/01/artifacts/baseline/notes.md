# Booking change demo

## Files and local use

- `flow.mjs`: dependency-free ES module exporting `createFlow(api, options)`.
- `index.html`: Japanese, keyboard-operable booking change interface.
- `mock-service.mjs`: in-memory mock; it makes no external requests.
- `notes.md`: contract, assumptions, instructions, and verification notes.

Serve this directory over localhost, then open `http://127.0.0.1:8000/index.html`. ES modules normally cannot be loaded directly from a `file:` URL. This Node standard-library command serves only the three browser files:

```sh
cd /workspace/scratch/0238266812de/private/B/evaluation/round01/baseline
node --input-type=module <<'NODE'
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
const files = new Map([
  ['/', 'index.html'], ['/index.html', 'index.html'],
  ['/flow.mjs', 'flow.mjs'], ['/mock-service.mjs', 'mock-service.mjs']
]);
createServer(async (req, res) => {
  const file = files.get(new URL(req.url, 'http://127.0.0.1').pathname);
  if (!file) return res.writeHead(404).end('Not found');
  try {
    const body = await readFile(file);
    res.writeHead(200, { 'Content-Type': file.endsWith('.html')
      ? 'text/html; charset=utf-8' : 'text/javascript; charset=utf-8' });
    res.end(body);
  } catch { res.writeHead(500).end('Unable to read local demo file'); }
}).listen(8000, '127.0.0.1', () => console.log('http://127.0.0.1:8000/index.html'));
NODE
```

Stop the server with Ctrl+C. No package install, build step, external network service, or production credentials are required. Any existing local static server can also serve this directory.

## Reviewer walkthrough

1. Leave **通常の変更** selected. Choose December 10 or December 11, open **内容を確認**, and inspect both the confirmed booking and proposed date. No API call happens until **この内容で変更を依頼**.
2. After sending, the confirmed card stays at December 8. Wait about two seconds and use **結果を確認**. Only the `succeeded` response updates the confirmed card.
3. Reset the demo and select **変更が拒否される**. Submit either date. The failure leaves December 8 confirmed. Choose a different date or review a new attempt.
4. Reset and select **応答が失われる**. The initial response throws after the mock has accepted the request. The first lookup intentionally returns `not_found`; this does not release the request or mark it failed. Use another lookup, or **同じ依頼IDで再送**. The ID and payload remain unchanged. The mock executes the booking change once.
5. Reset and select **キャンセルが成立する**. Submit, then request cancellation before eight seconds elapse. Receipt changes the phase to `cancel_requested`; it does not say the request was cancelled. Wait about 1.2 seconds after receipt and check until `cancelled` is reported.
6. Reset and select **変更が先に確定する**. Submit, then request cancellation promptly. Although cancellation is accepted, the service finishes the change at about two seconds. Checking reports `succeeded`, and the new date is shown as confirmed.

The mock also permits cancellation in the normal and lost-response cases. Whether it wins depends on timing. Its final outcome is stable once reached. The demo controls cannot reset an unresolved operation.

## Controller behavior

`createFlow(api, { bookingId, currentDate, nextId })` returns exactly the requested methods. Synchronous methods return a fresh view object; asynchronous methods resolve to one. `view()` is a snapshot containing `phase`, `currentDate`, `draftDate`, `operationId`, `message`, `canSubmit`, `canCancel`, and `canCheck`. Call it immediately after starting an asynchronous action to render its in-progress state, then again after the promise resolves.

| State | Available recovery / progression |
| --- | --- |
| `editing` | Choose a date, then review. |
| `review` | Submit once or go back and edit. |
| `pending` | Check the result or request cancellation. |
| `unknown` | Check again; retry the identical submission within the 24-hour window if cancellation has never been requested; request or retry cancellation when its receipt is unconfirmed. |
| `cancel_requested` | Check for the actual final outcome. Receipt is not cancellation. |
| `failed` | Keep the confirmed booking; return to editing and review a fresh attempt. |
| `cancelled` | Keep the confirmed booking; return to editing and review a fresh attempt. |
| `succeeded` | Update the confirmed booking from the authoritative result; optionally start a new change. |

- A request ID is allocated at the first confirmed submission, not at date selection or review. An ID is paired with one frozen payload. Unknown-result retries reuse that ID and exact payload.
- While an operation is unresolved, `choose`, `review`, and `back` cannot discard or replace it. An invalid action returns the unchanged view rather than throwing. Repeated concurrent calls are gated per action, so double clicking submit/check/cancel does not duplicate that action while it is in flight.
- `pending.currentDate`, `failed.currentDate`, `cancelled.currentDate`, transport errors, and lookup misses never replace the locally confirmed booking. Only `succeeded` does. A successful response without `currentDate` uses the requested target date.
- Checks and cancellation may run while submission is in flight. Terminal results cannot be overwritten by late pending replies, errors, cancellation receipts, or replies belonging to an old operation. Nonterminal observations use request sequence numbers to avoid an older request's delayed response replacing a newer observation.
- Cancellation does not abort a transport or erase the request ID. Once cancellation has been attempted, resubmitting the original mutation is disabled even if cancellation receipt is unknown.
- Retries stop at 24 hours after the first submission. A detected backwards wall-clock jump also disables retries. Lookup and cancellation remain available. Request IDs are not recycled during the controller's lifetime.
- Service messages are displayed as text, not HTML. UI status updates use a polite live region. Every control has a visible label and keyboard focus indication.

## Assumptions and remaining limitations

- Dates are nonempty strings in the controller. The UI restricts choice to the two supplied dates. The controller does not infer business availability, validate every calendar format, or convert time zones. The given timestamps are assumed to be in the booking service's local time.
- `succeeded`, `failed`, and `cancelled` are authoritative terminal outcomes for one request, and the backend does not subsequently reverse them or report contradictory terminal outcomes. Invalid response forms are treated as unknown.
- The service's optional successful `currentDate` is authoritative; otherwise the requested date is used. A separate out-of-band change by another actor would require a booking refresh endpoint, which the supplied adapter does not provide.
- Cancellation receipt has no final-outcome information. A lost cancellation response can be retried with the same request ID; the adapter is assumed to tolerate repeated requests to cancel the same operation.
- The controller uses `Date.now()` for the deduplication window and assumes the client's clock is sufficiently stable. A production service should provide authoritative expiry metadata and durable reconciliation. This demo deliberately adds no alternate API or storage contract.
- Controller and mock state are in memory. Reloading or closing the page loses them; the UI warns before leaving while unresolved, subject to browser restrictions. Cross-tab coordination, crash recovery, durable request journals, authentication, and production monitoring are outside this local fixture. Do not treat reload as an operation-recovery mechanism.
- The mock's request map lasts for the page lifetime, and its deduplication retention is effectively longer than 24 hours. The controller still limits retries to the supplied 24-hour guarantee. Background timers model service work independently of whether a response is delivered.
- There is no automatic polling. The explicit **結果を確認** control lets a reviewer inspect intermediate states. A permanently unavailable service can leave a request unresolved; the controller keeps the ID and confirmed booking instead of inventing a result.
- A static localhost server is needed for browser ES module loading. No real booking service is contacted.

## Verification

Executed an isolated Node script using only `node:assert/strict`, `node:fs`, `node:child_process`, and these implementation modules. Result: **51 assertions passed**, including:

- Exact view keys; review makes no submission; repeated submit while in flight makes one call.
- Pending, failed, cancelled, malformed, and missing responses cannot change the confirmed booking.
- A non-authoritative `not_found` leaves the operation unresolved and immutable.
- Unknown-result retry uses exactly the same request ID and payload; a newly reviewed attempt after failure gets a fresh ID.
- Cancellation receipt remains provisional; cancellation can lose to successful completion.
- A lost cancellation response prevents resubmission of the original mutation while allowing result checks and another cancellation request.
- Late nonterminal replies cannot regress terminal success; replies from a completed old operation cannot overwrite a new operation.
- The 24-hour retry limit and a clock earlier than the first submission disable further submission.
- All five mock scenarios reached their expected final phase and confirmed booking date.
- The inline browser module passed Node syntax checking, and the HTML has no duplicate control IDs.

These are local smoke checks, not a saved automated test suite. No campaign tests, unrelated implementation files, external network, or production services were used. A real browser interaction / screenshot review was not performed; keyboard and layout support were implemented but not visually verified.
