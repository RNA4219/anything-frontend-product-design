# Executable checks

Run from the repository root. Python 3.12 and Node 24 were used for the recorded results.

```sh
python3 modules/interaction-ux-flow/checks/check_registry.py
python3 -m unittest discover -s modules/interaction-ux-flow/tests -p 'test_registry.py'
node modules/interaction-ux-flow/tests/test_recovery_policy.mjs
node modules/interaction-ux-flow/tests/run_flow_trials_v4.mjs campaigns/B/rounds/01/artifacts/baseline/flow.mjs
node modules/interaction-ux-flow/tests/run_flow_trials_v4.mjs campaigns/B/rounds/01/artifacts/candidate/flow.mjs
node modules/interaction-ux-flow/tests/run_flow_trials_v4.mjs campaigns/B/rounds/01/artifacts/candidate-revised/flow.mjs
node campaigns/B/rounds/01/artifacts/candidate/smoke-test.mjs
```

**The active R01 evaluation suite is v4.** `run_flow_trials.mjs`, v2 and v3 are immutable historical evidence, retained with freeze records and documented defects. Do not use their scores to claim current conformance. See `campaigns/B/rounds/01/test-errata.md`.

## Generated UI examples

Serve `campaigns/B/rounds/01/artifacts/candidate-revised` locally with its `node serve.mjs`, then open the address printed by the server. The service is an in-memory/local-storage fixture, not a production backend. Original baseline/candidate outputs remain separately available for comparison.

## Independent DOM examination

Install jsdom 26.1.0 in your test environment, or supply its absolute module path using `B_DOM_JSDOM_PATH`. Run:

```sh
node campaigns/B/rounds/01/independent/dom_copy_probe.mjs /tmp/session-b-dom
```

This executes actual DOM events and generated module bodies with imports injected. It records visible text and service observations. It does not render layout, emulate a complete browser, test assistive technology, or measure human comprehension. The original-arm semantic findings are expected; they are not failures of the frozen 14-case controller suite. The revised candidate has a separate focused trace.

## Interpretation

A state transition assertion must be paired with its target/side-effect observation. A nonempty message does not establish truthful copy. Negative controls demonstrate selected fault detection, not exhaustive coverage. These local results are separate from CI, which this campaign has not executed.

## Form repair and reversal (R02)

```sh
node modules/interaction-ux-flow/tests/test_task_flows.mjs
node modules/interaction-ux-flow/tests/test_branch_error_regressions.mjs
```

The frozen suite contains 16 cases. The three branch-error regressions were added after independent exploratory observation and are reported separately. Initial code remains under `campaigns/B/rounds/02/artifacts/initial`; it intentionally fails E01. Serve the module examples directory to operate `repair-and-undo.html`.

## Resumption and conflicts (R03)

```sh
node modules/interaction-ux-flow/tests/test_resume_conflict.mjs
node modules/interaction-ux-flow/tests/test_resume_evidence_regressions.mjs
```

The frozen suite contains 13 cases. It uses trusted session/capability inputs and an explicit conditional-update mock. It does not implement authentication, secure storage or an HTTP adapter. Serve the module examples directory to operate `resume-and-conflict.html`. Its reopen action constructs another controller from an in-memory saved snapshot; it is not a persistence or browser recovery test.

The four evidence-retention/authority regressions were added after independent exploratory findings: a reopened task lost known success when its lookup record expired, and a stale pending lookup overwrote a newly confirmed success. The initial snapshot passes the authority case but fails the three evidence-retention cases. The third case follows the same stale-lookup risk through a transport exception, added after the first repair passed the pending-response case. A fourth case prevents terminal evidence from overriding a current reauthentication requirement. Input-state copy has a separate DOM recheck rather than a text-only model assertion.

## Reproduce the R02 independent DOM events

```sh
B_DOM_JSDOM_PATH=/absolute/path/to/jsdom node campaigns/B/rounds/02/independent/dom-events.mjs
```

This portable copy changes only environment paths. Its default output is a temporary file; archived independent results are not overwritten. The current model passes the eight representative scenarios and the exploratory inactive-error scenario. This portability rerun is not an additional independent sample.

## Partial batches (R04)

```sh
node modules/interaction-ux-flow/tests/test_batch_flow.mjs
node modules/interaction-ux-flow/tests/test_batch_boundaries.mjs
```

The original frozen suite has 13 cases. Three supplemental boundary criteria were frozen after analysis and before candidate implementation; they are reported separately. A02 covers both a late same-attempt reply and a reply from an older attempt. Serve the examples directory to operate `batch-flow.html`.

This is one declared non-atomic fixture. The same requestId is also a durable lookup reference only by its explicit contract. No test of a live Graph/AWS/AIP adapter, atomic transaction, SDK retry, arbitrary dependency graph, persistent recovery or production authorization is implied. See the R04 protocol notes for source-driven limits on generalization.
