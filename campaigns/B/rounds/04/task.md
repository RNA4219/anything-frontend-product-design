# B-R04: partial batch results and item-scoped recovery

A user selects a fixed set of records and applies the same reviewed change. The task may return mixed per-item results, arrive out of order, omit outcomes, or lose the transport response. The user needs to know what happened to each intended item, what remains unresolved, and what can safely be done next.

Use a declared non-atomic fixture with stable item IDs, per-item operation/request IDs, authoritative success/unapplied outcomes, a status lookup and a cancellation request. The fixture distinguishes a retryable terminal nonapplication from an unknown outcome. A retry time is a minimum delay, not a promise of future success. Only authorized, explicitly selected eligible items may be retried. Dependencies identify items that have not run, not successful effects that need undoing.

Do not infer these semantics for every batch API. Researchers must identify counterexamples: atomic batches, transactional rollback, accepted asynchronous jobs, envelope HTTP success with inner failures, and APIs lacking per-item query or retry support. If evidence does not support a necessary recovery action, keep the unresolved route explicit instead of inventing an endpoint.

Predeclared acceptance is in cases.json. Parent freezes executable assertions before writing the candidate. Independent critic can add exploratory probes but must report them separately. This is a contract conformance and defect-detection experiment, not another generated baseline efficacy comparison.

Scope B: the user's selected scope, item/task outcomes, available choices, truthful completion and recovery. C owns transport scheduling, pagination/virtualization, focus and ARIA mechanics. D owns broader test methodology and human effectiveness. No live production changes.
