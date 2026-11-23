export const INITIAL_DATE = '2026-12-08T14:00';

export const SCENARIOS = {
  normal: { name: '通常の変更', help: '依頼後、約2秒で変更が確定します。「結果を確認」で確定を確認できます。' },
  rejected: { name: '変更が拒否される', help: '希望日時が満席として拒否されます。元の予約は保持されます。' },
  lost: { name: '応答が失われる', help: '依頼は届きますが最初の送信応答が失われます。最初の照会も未検出になります。同じIDで確認・再送できます。' },
  cancellation: { name: 'キャンセルが成立する', help: '変更完了まで8秒あります。キャンセルを依頼し、約1.2秒後に結果を確認してください。' },
  cancellation_race: { name: '変更が先に確定する', help: 'キャンセルが受け付けられても、変更の完了が先になります。受付と最終結果の違いを確認できます。' }
};

/** Entirely in-memory demonstration service. Uses no network or production data. */
export function createMockService(scenario = 'normal') {
  if (!Object.hasOwn(SCENARIOS, scenario)) throw new TypeError('Unknown demo scenario');
  const operations = new Map();
  const timers = new Set();
  let currentDate = INITIAL_DATE;
  let disposed = false;

  function later(action, ms) {
    const timer = setTimeout(() => {
      timers.delete(timer);
      if (!disposed) action();
    }, ms);
    timers.add(timer);
    return timer;
  }

  function pause(ms) {
    // Transport timers always resolve; reset is disabled while a request is unresolved.
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function snapshot(op) {
    return {
      status: op.status,
      currentDate,
      ...(op.status === 'failed' ? { message: '希望日時に空きがありません。' } : {})
    };
  }

  function finish(op, status) {
    if (op.status !== 'pending' || disposed) return;
    op.status = status;
    if (status === 'succeeded') currentDate = op.targetDate;
  }

  const api = {
    async submit(payload) {
      if (disposed) throw new Error('Demo service was reset');
      let op = operations.get(payload.requestId);
      if (op) {
        if (op.bookingId !== payload.bookingId || op.targetDate !== payload.targetDate) {
          throw new Error('A request ID cannot identify a different payload');
        }
        await pause(250);
        return snapshot(op);
      }
      op = {
        bookingId: payload.bookingId,
        targetDate: payload.targetDate,
        requestId: payload.requestId,
        status: scenario === 'rejected' ? 'failed' : 'pending',
        lookupMissRemaining: scenario === 'lost' ? 1 : 0,
        cancellationRequested: false
      };
      operations.set(op.requestId, op);
      if (op.status === 'pending') {
        later(() => finish(op, 'succeeded'), scenario === 'cancellation' ? 8000 : 2000);
      }
      await pause(450);
      if (scenario === 'lost') throw new Error('Simulated lost submit response');
      return snapshot(op);
    },

    async lookup(requestId) {
      await pause(250);
      if (disposed) throw new Error('Demo service was reset');
      const op = operations.get(requestId);
      if (!op) return { status: 'not_found' };
      if (op.lookupMissRemaining > 0) {
        op.lookupMissRemaining -= 1;
        return { status: 'not_found' };
      }
      return snapshot(op);
    },

    async cancel(requestId) {
      await pause(250);
      if (disposed) throw new Error('Demo service was reset');
      const op = operations.get(requestId);
      if (op && op.status === 'pending' && !op.cancellationRequested) {
        op.cancellationRequested = true;
        if (scenario !== 'cancellation_race') {
          later(() => finish(op, 'cancelled'), 1200);
        }
      }
      // Receipt never claims that the mutation was cancelled.
      return { accepted: true };
    }
  };

  return {
    api,
    dispose() {
      disposed = true;
      for (const timer of timers) clearTimeout(timer);
      timers.clear();
    }
  };
}
