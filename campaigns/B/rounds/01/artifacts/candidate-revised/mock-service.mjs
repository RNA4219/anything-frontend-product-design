/** Local-only, reload-persistent simulation; no HTTP requests. */
export function createMockService({ storage, key = 'booking-change-mock-v1', delay = 350, now = Date.now } = {}) {
  let mode = 'normal';
  let lookupFault = false;
  let memory = null;
  const initial = () => ({ currentDate: '2026-12-08T14:00', operations: {}, mutationCount: 0, submitCalls: 0, lookupCalls: 0, cancelCalls: 0 });
  function read() {
    if (!storage) return memory ??= initial();
    const raw = storage.getItem(key);
    return raw ? JSON.parse(raw) : initial();
  }
  function write(state) {
    if (storage) storage.setItem(key, JSON.stringify(state));
    else memory = state;
  }
  function wait() { return new Promise(resolve => setTimeout(resolve, delay)); }
  function settle(state) {
    for (const op of Object.values(state.operations)) {
      if (op.status === 'pending' && now() >= op.readyAt) {
        op.status = op.finish;
        if (op.status === 'succeeded') {
          state.currentDate = op.targetDate;
          state.mutationCount += 1;
        }
      }
    }
    write(state);
  }
  function result(state, op) {
    return { status: op.status, currentDate: state.currentDate, ...(op.status === 'failed' ? { message: '希望枠を確保できませんでした。もう一つの候補を選べます。' } : {}) };
  }
  return {
    setMode(value) { mode = value; },
    failNextLookup() { lookupFault = true; },
    reset() { write(initial()); lookupFault = false; },
    inspect() { const state = read(); settle(state); return structuredClone(state); },
    async submit(payload) {
      const state = read();
      settle(state);
      state.submitCalls += 1;
      let op = state.operations[payload.requestId];
      // This mock's deduplication window, like the fixture's, is 24 hours.
      if (op && now() - op.createdAt >= 24 * 60 * 60 * 1000) op = null;
      if (op) {
        if (op.bookingId !== payload.bookingId || op.targetDate !== payload.targetDate) {
          write(state);
          throw new Error('A request ID cannot identify changed payload');
        }
      } else {
        op = {
          ...payload, mode, createdAt: now(),
          readyAt: now() + (mode === 'cancellation' ? 12000 : mode === 'race' ? 700 : 2500),
          status: mode === 'rejected' ? 'failed' : 'pending', finish: 'succeeded',
        };
        state.operations[payload.requestId] = op;
      }
      write(state);
      const response = result(state, op);
      await wait();
      if (op.mode === 'lost') throw new Error('Simulated lost response after acceptance');
      return response;
    },
    async lookup(requestId) {
      const shouldFail = lookupFault;
      lookupFault = false;
      const state = read();
      state.lookupCalls += 1;
      settle(state);
      write(state);
      await wait();
      if (shouldFail) throw new Error('Simulated lookup transport failure');
      const latest = read();
      settle(latest);
      const op = latest.operations[requestId];
      if (!op || now() - op.createdAt >= 24 * 60 * 60 * 1000) return { status: 'not_found' };
      return result(latest, op);
    },
    async cancel(requestId) {
      const state = read();
      state.cancelCalls += 1;
      settle(state);
      const op = state.operations[requestId];
      if (op?.status === 'pending' && op.mode !== 'race') {
        op.finish = 'cancelled';
        op.readyAt = now() + 1500;
      }
      write(state);
      await wait();
      return { accepted: true };
    },
  };
}
