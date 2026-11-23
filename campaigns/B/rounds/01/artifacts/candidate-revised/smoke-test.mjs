import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createFlow } from './flow.mjs';
import { createMockService } from './mock-service.mjs';

const OLD = '2026-12-08T14:00';
const A = '2026-12-10T14:00';
const B = '2026-12-11T14:00';
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
};
function setup(overrides = {}, extraOptions = {}) {
  const calls = { submit: [], lookup: [], cancel: [] };
  let serial = 0;
  const api = {
    submit: async p => { calls.submit.push(p); return overrides.submit ? overrides.submit(p) : { status: 'pending' }; },
    lookup: async id => { calls.lookup.push(id); return overrides.lookup ? overrides.lookup(id) : { status: 'pending' }; },
    cancel: async id => { calls.cancel.push(id); return overrides.cancel ? overrides.cancel(id) : { accepted: true }; },
  };
  const flow = createFlow(api, { bookingId: 'R-204', currentDate: OLD, nextId: () => `request-${++serial}`, ...extraOptions });
  return { flow, calls };
}
function review(flow, date = A) { flow.choose(date); flow.review(); }

test('review and back are local; synchronous service success completes directly', async () => {
  const { flow, calls } = setup({ submit: () => ({ status: 'succeeded' }) });
  assert.equal(flow.view().phase, 'editing');
  flow.choose(A);
  flow.review();
  assert.equal(flow.view().canSubmit, true);
  flow.back();
  assert.equal(flow.view().draftDate, A);
  assert.equal(calls.submit.length, 0);
  flow.review();
  await flow.confirm();
  assert.equal(flow.view().phase, 'succeeded');
  assert.equal(flow.view().currentDate, A);
  assert.equal(flow.view().canCheck, false);
  assert.equal(calls.lookup.length, 0);
  assert.deepEqual(calls.submit[0], { bookingId: 'R-204', targetDate: A, requestId: 'request-1' });
});

test('invalid and unchanged dates cannot submit; changed review requires review again', async () => {
  const { flow, calls } = setup();
  for (const date of ['', 'invalid', '2026-02-31T14:00', OLD]) {
    review(flow, date);
    await flow.confirm();
    assert.equal(flow.view().canSubmit, false);
  }
  assert.equal(calls.submit.length, 0);
  review(flow);
  flow.choose(B);
  assert.equal(flow.view().phase, 'editing');
  await flow.confirm();
  assert.equal(calls.submit.length, 0);
});

test('pending currentDate is never treated as mutation confirmation', async () => {
  const { flow } = setup({ submit: () => ({ status: 'pending', currentDate: A }), lookup: () => ({ status: 'pending', currentDate: B }) });
  review(flow);
  await flow.confirm();
  assert.equal(flow.view().currentDate, OLD);
  await flow.check();
  assert.equal(flow.view().currentDate, OLD);
});

test('lost response, non-authoritative miss and lookup failure keep the original intent', async () => {
  let step = 0;
  const { flow, calls } = setup({
    submit: () => { throw Error('lost'); },
    lookup: () => {
      step += 1;
      if (step === 1) return { status: 'not_found' };
      if (step === 2) throw Error('lookup offline');
      return { status: 'succeeded', currentDate: A };
    },
  });
  review(flow);
  await flow.confirm();
  assert.equal(flow.view().phase, 'unknown');
  const id = flow.view().operationId;
  for (let i = 0; i < 2; i += 1) {
    await flow.check();
    assert.equal(flow.view().phase, 'unknown');
    assert.equal(flow.view().currentDate, OLD);
    flow.choose(B); flow.back(); flow.review(); await flow.confirm();
    assert.equal(flow.view().draftDate, A);
    assert.equal(flow.view().operationId, id);
    assert.equal(calls.submit.length, 1);
  }
  await flow.check();
  assert.equal(flow.view().currentDate, A);
  assert.ok(calls.lookup.every(value => value === id));
});

test('concurrent confirmation creates one request and consumes one request ID', async () => {
  const pending = deferred();
  const { flow, calls } = setup({ submit: () => pending.promise });
  review(flow);
  const first = flow.confirm();
  const second = flow.confirm();
  assert.equal(calls.submit.length, 1);
  assert.equal(flow.view().canSubmit, false);
  pending.resolve({ status: 'pending' });
  await Promise.all([first, second]);
  assert.equal(flow.view().operationId, 'request-1');
});

test('cancellation acceptance is not cancellation; pending remains cancel_requested', async () => {
  let outcome = 'pending';
  const { flow, calls } = setup({ lookup: () => ({ status: outcome, currentDate: B }) });
  review(flow);
  await flow.confirm();
  await flow.cancel();
  assert.equal(flow.view().phase, 'cancel_requested');
  assert.equal(flow.view().currentDate, OLD);
  assert.equal(flow.view().canCancel, false);
  await flow.check();
  assert.equal(flow.view().phase, 'cancel_requested');
  outcome = 'cancelled';
  await flow.check();
  assert.equal(flow.view().phase, 'cancelled');
  assert.equal(flow.view().currentDate, OLD);
  assert.equal(calls.cancel[0], calls.lookup[0]);
});

test('success may win cancellation and late submit pending cannot undo success', async () => {
  const submitted = deferred();
  const { flow } = setup({ submit: () => submitted.promise, lookup: () => ({ status: 'succeeded', currentDate: A }) });
  review(flow);
  const sending = flow.confirm();
  await flow.cancel();
  await flow.check();
  assert.equal(flow.view().phase, 'succeeded');
  assert.equal(flow.view().currentDate, A);
  submitted.resolve({ status: 'pending', currentDate: OLD });
  await sending;
  assert.equal(flow.view().phase, 'succeeded');
  assert.equal(flow.view().currentDate, A);
});

test('late cancellation acknowledgment and late lookup cannot overwrite a terminal result', async () => {
  const submitted = deferred(), checking = deferred(), cancelling = deferred();
  const { flow, calls } = setup({ submit: () => submitted.promise, lookup: () => checking.promise, cancel: () => cancelling.promise });
  review(flow);
  const send = flow.confirm();
  const checks = [flow.check(), flow.check()];
  const cancels = [flow.cancel(), flow.cancel()];
  assert.equal(calls.lookup.length, 1);
  assert.equal(calls.cancel.length, 1);
  submitted.resolve({ status: 'succeeded', currentDate: A });
  await send;
  checking.resolve({ status: 'pending' });
  cancelling.resolve({ accepted: true });
  await Promise.all([...checks, ...cancels]);
  assert.equal(flow.view().phase, 'succeeded');
  assert.equal(flow.view().currentDate, A);
});

test('cancel transport failure retains recoverability and does not assert cancellation', async () => {
  const { flow } = setup({ cancel: () => { throw Error('lost cancel response'); }, lookup: () => ({ status: 'succeeded' }) });
  review(flow);
  await flow.confirm();
  await flow.cancel();
  assert.equal(flow.view().phase, 'unknown');
  assert.equal(flow.view().canCheck, true);
  assert.equal(flow.view().currentDate, OLD);
  await flow.check();
  assert.equal(flow.view().phase, 'succeeded');
  assert.equal(flow.view().currentDate, A);
});

test('failed changes preserve draft and allow an explicitly reviewed fresh request', async () => {
  const { flow, calls } = setup({ submit: () => ({ status: 'failed', currentDate: B }) });
  review(flow);
  await flow.confirm();
  assert.equal(flow.view().phase, 'failed');
  assert.equal(flow.view().currentDate, OLD);
  assert.equal(flow.view().draftDate, A);
  flow.back();
  review(flow, B);
  await flow.confirm();
  assert.equal(calls.submit.length, 2);
  assert.notEqual(calls.submit[0].requestId, calls.submit[1].requestId);
  assert.equal(calls.submit[0].targetDate, A);
  assert.equal(calls.submit[1].targetDate, B);
});

test('responses from an old operation cannot change a new operation', async () => {
  const oldSend = deferred();
  let submissions = 0;
  const { flow } = setup({ submit: () => ++submissions === 1 ? oldSend.promise : { status: 'pending' }, lookup: () => ({ status: 'failed' }) });
  review(flow);
  const oldPromise = flow.confirm();
  await flow.check();
  review(flow, B);
  await flow.confirm();
  const current = flow.view();
  oldSend.resolve({ status: 'succeeded', currentDate: A });
  await oldPromise;
  assert.deepEqual(flow.view(), current);
});

test('a reused ID is rejected locally before payload can be changed at the service', async () => {
  const { flow, calls } = setup({ submit: () => ({ status: 'failed' }) }, { nextId: () => 'fixed' });
  review(flow);
  await flow.confirm();
  review(flow, B);
  await flow.confirm();
  assert.equal(calls.submit.length, 1);
  assert.equal(flow.view().phase, 'review');
});

test('restored unresolved state resumes lookup only; repeated misses never resubmit', async () => {
  const resume = { phase: 'pending', operationId: 'persisted-id', draftDate: A };
  const { flow, calls } = setup({ lookup: () => ({ status: 'not_found' }) }, { resume });
  assert.equal(flow.view().phase, 'unknown');
  for (let i = 0; i < 3; i += 1) {
    await flow.check(); flow.choose(B); flow.review(); await flow.confirm();
  }
  assert.equal(calls.submit.length, 0);
  assert.equal(flow.view().operationId, 'persisted-id');
  assert.equal(flow.view().draftDate, A);
  assert.ok(calls.lookup.every(id => id === 'persisted-id'));
  assert.throws(() => setup({}, { resume: { phase: 'unknown' } }), /情報が不足/);
});

test('view snapshots cannot mutate the controller', () => {
  const { flow } = setup();
  review(flow);
  const snapshot = flow.view();
  snapshot.draftDate = B;
  snapshot.currentDate = B;
  assert.equal(flow.view().draftDate, A);
  assert.equal(flow.view().currentDate, OLD);
});

for (const mode of ['normal', 'rejected', 'lost', 'cancellation', 'race']) {
  test(`local mock scenario: ${mode}`, async () => {
    let clock = 0;
    const mock = createMockService({ delay: 0, now: () => clock });
    mock.setMode(mode);
    const flow = createFlow(mock, { bookingId: 'R-204', currentDate: OLD, nextId: () => 'mock-id' });
    review(flow);
    await flow.confirm();
    if (mode === 'rejected') {
      assert.equal(flow.view().phase, 'failed');
      assert.equal(mock.inspect().mutationCount, 0);
      return;
    }
    if (mode === 'lost') assert.equal(flow.view().phase, 'unknown');
    if (mode === 'cancellation' || mode === 'race') {
      await flow.cancel();
      assert.equal(flow.view().phase, 'cancel_requested');
    }
    clock = 3000;
    await flow.check();
    const cancelled = mode === 'cancellation';
    assert.equal(flow.view().phase, cancelled ? 'cancelled' : 'succeeded');
    assert.equal(flow.view().currentDate, cancelled ? OLD : A);
    assert.equal(mock.inspect().mutationCount, cancelled ? 0 : 1);
    await flow.confirm(); await flow.check();
    assert.equal(mock.inspect().submitCalls, 1);
    assert.equal(mock.inspect().mutationCount, cancelled ? 0 : 1);
  });
}

test('mock lookup fault and expired lookup do not create a new mutation', async () => {
  let clock = 0;
  const mock = createMockService({ delay: 0, now: () => clock });
  const flow = createFlow(mock, { bookingId: 'R-204', currentDate: OLD, nextId: () => 'expiring-id' });
  review(flow);
  await flow.confirm();
  mock.failNextLookup();
  await flow.check();
  assert.equal(flow.view().phase, 'unknown');
  clock = 25 * 60 * 60 * 1000;
  await flow.check();
  assert.equal(flow.view().phase, 'unknown');
  assert.equal(flow.view().currentDate, OLD);
  flow.back(); flow.choose(B); flow.review(); await flow.confirm();
  assert.equal(mock.inspect().submitCalls, 1);
  assert.equal(mock.inspect().mutationCount, 1);
});

test('mock and controller survive reload without replaying the request', async () => {
  const records = new Map();
  const storage = { getItem: key => records.get(key) ?? null, setItem: (key, value) => records.set(key, value) };
  let clock = 0;
  const firstService = createMockService({ storage, delay: 0, now: () => clock });
  firstService.setMode('lost');
  const first = createFlow(firstService, { bookingId: 'R-204', currentDate: OLD, nextId: () => 'reload-id' });
  review(first);
  await first.confirm();
  const saved = JSON.parse(JSON.stringify(first.view()));
  const secondService = createMockService({ storage, delay: 0, now: () => clock });
  const second = createFlow(secondService, { bookingId: 'R-204', currentDate: saved.currentDate, nextId: () => 'should-not-be-used', resume: saved });
  clock = 3000;
  await second.check();
  assert.equal(second.view().currentDate, A);
  assert.equal(secondService.inspect().submitCalls, 1);
  assert.equal(secondService.inspect().mutationCount, 1);
});

test('HTML controls referenced by the UI exist; all assets are local', async () => {
  const html = await readFile(new URL('./index.html', import.meta.url), 'utf8');
  const script = await readFile(new URL('./app.mjs', import.meta.url), 'utf8');
  const ids = [...html.matchAll(/id="([^"]+)"/g)].map(match => match[1]);
  assert.equal(new Set(ids).size, ids.length);
  for (const match of script.matchAll(/\$\('([^']+)'\)/g)) assert.ok(ids.includes(match[1]), `Missing control ${match[1]}`);
  for (const name of ['review-button', 'confirm-button', 'back-button', 'check-button', 'cancel-button', 'new-change-button']) assert.ok(ids.includes(name));
  assert.match(html, /type="module" src="\.\/app\.mjs"/);
  assert.doesNotMatch(html + script, /(?:src|href)=["']https?:|fetch\s*\(|XMLHttpRequest|https?:\/\//);
});
