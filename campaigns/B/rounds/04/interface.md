# Executable fixture interface (frozen before candidate)

`createBatchFlow(api, {items, nextRequestId, now})` returns `start()`, `retry(itemIds)`, `reconcile(itemIds)`, `requestCancel(itemIds)` and `view()`.

- Each selected item has stable `id`, display `label`, and optional `dependsOn` item IDs. The selected set does not change during this task.
- `api.submit({items:[{itemId, requestId, dependsOn}]})` returns `{accepted,results}`. Each result correlates `itemId` **and** `requestId`. `requestId` is also a durable lookup reference **in this fixture only**; an adapter for an API with separate correlation/operation identities must preserve that distinction.
- Each result has one of `succeeded`, `pending`, `unknown`, `failed`, `cancelled`, `blocked`. `failed` and `blocked` are actionable as nonapplication only with `unapplied:true`; a retry also requires `retryable:true`. `nextRetryAt` is an optional minimum eligibility time in the injected clock's units. These are normalized fixture fields, not HTTP or vendor response schemas.
- `api.lookup({itemId, requestId})` returns a correlated item result. Missing/expired records do not prove nonapplication. `api.cancel({itemId,requestId})` returns a cancellation receipt, not the original operation's terminal result. Pending/unknown original outcomes remain subject to lookup.
- `view()` exposes immutable snapshots: `rows` (each `{id,status,requestId,...}`), `total`, `counts`, `finished`, `allSucceeded`, `canRetryIds`, `canReconcileIds`, `canCancelIds`, and a truthful `message`.
- `start()` is only for initial selected ready items. It never repeats an already started task. `retry(ids)` is an explicit user decision for only eligible known-unapplied items; `reconcile(ids)` looks up original references. New writes are not inferred from lookup misses.
- Declared dependencies must all be successful before retrying a blocked item. This fixture is not an arbitrary dependency workflow scheduler, and does not automatically run dependent retries.
- The fixture has current write/read/cancel permission for its selected records. Cross-account authentication, UI keyboard/focus implementation, live vendor adapters and persistent recovery are outside this round's direct tests; reuse the previous units and service contract when applicable.
