# Booking change implementation task

Implement a small usable booking change interface and an ES module controller.
R-204 is confirmed for `2026-12-08T14:00`; the user wants
`2026-12-10T14:00` or `2026-12-11T14:00`. Keep the confirmed booking
until the service confirms a change. Let the user inspect the intended change,
submit, understand its result and recover. Do not call a real service.

Export `createFlow(api, options)` from `flow.mjs`. Options contain
`bookingId`, `currentDate`, `nextId` (a function returning a fresh request ID).
Return `choose(date)`, `review()`, async `confirm()`, async `check()`,
async `cancel()`, `back()`, and `view()`.
The view is a plain object with `phase`, `currentDate`, `draftDate`,
`operationId`, `message`, `canSubmit`, `canCancel`, `canCheck`.
Use these phase names when applicable: editing, review, pending, unknown,
failed, succeeded, cancel_requested, cancelled. These are interoperability
names, not a requirement to show every state in every flow.

Service adapter:

- `api.submit({bookingId,targetDate,requestId})` returns a Promise of
  `{status,currentDate?,message?}`. Status is pending, succeeded or failed.
  A thrown error gives no information about whether a side effect occurred.
- `api.lookup(requestId)` returns the same form, also allowing cancelled
  and not_found. not_found is a non-authoritative lookup miss, not proof the
  request never executed. A pending response may contain the last confirmed
  currentDate. Only succeeded establishes the requested mutation completed.
- `api.cancel(requestId)` returns `{accepted:true}` when the cancellation
  request is received. It does not supply a final operation outcome.
- A request ID identifies one immutable intent. This fixture's backend
  deduplicates the same request ID and identical payload for 24 hours.
  Changed payload with the same ID is rejected. No client transport primitive
  cancels an accepted backend mutation.

Also create index.html with operable controls and a local mock service so a
reviewer can try normal operation, rejected change, lost response and
cancellation. No dependencies or build step. Put all output in the assigned
directory. Describe assumptions and remaining limitations in notes.md.
