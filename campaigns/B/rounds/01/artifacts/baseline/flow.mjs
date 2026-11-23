const RETRY_WINDOW_MS = 24 * 60 * 60 * 1000;
const TERMINAL = new Set(['succeeded', 'failed', 'cancelled']);
const UNRESOLVED = new Set(['pending', 'unknown', 'cancel_requested']);

/**
 * Booking change controller. No transport or storage is built into this module.
 * Every public method returns a fresh view (or a Promise for one).
 */
export function createFlow(api, options) {
  if (!api || !['submit', 'lookup', 'cancel'].every(name => typeof api[name] === 'function')) {
    throw new TypeError('api must provide submit, lookup and cancel functions');
  }
  if (!options || !isText(options.bookingId) || !isText(options.currentDate) || typeof options.nextId !== 'function') {
    throw new TypeError('bookingId, currentDate and nextId are required');
  }

  const bookingId = options.bookingId;
  const nextId = options.nextId;
  const usedIds = new Set();
  let currentDate = options.currentDate;
  let draftDate = null;
  let phase = 'editing';
  let message = '変更先を選んで、内容を確認してください。';
  let operation = null;
  let serial = 0;

  function isActive(op = operation) {
    return Boolean(op && operation === op && !TERMINAL.has(op.outcome));
  }

  function withinRetryWindow(op) {
    const elapsed = Date.now() - op.startedAt;
    return elapsed >= 0 && elapsed < RETRY_WINDOW_MS;
  }

  function view() {
    const active = isActive() && UNRESOLVED.has(phase);
    const mayRetry = active && phase === 'unknown' && !operation.submitInFlight &&
      operation.cancellation === 'none' && withinRetryWindow(operation);
    let visibleMessage = message;
    if (active && phase === 'unknown' && operation.cancellation === 'none' &&
        !operation.submitInFlight && !withinRetryWindow(operation)) {
      visibleMessage += ' 再送の安全性を保証する24時間を過ぎたか、時計が変わったため再送を停止しました。結果確認を続け、解決しなければサービス窓口でこの依頼IDを確認してください。';
    }
    return {
      phase,
      currentDate,
      draftDate,
      operationId: operation ? operation.id : null,
      message: visibleMessage,
      canSubmit: phase === 'review' || Boolean(mayRetry),
      canCancel: Boolean(active && !operation.cancelInFlight &&
        ['none', 'unknown'].includes(operation.cancellation)),
      canCheck: Boolean(active && !operation.lookupInFlight)
    };
  }

  function choose(date) {
    // An unresolved intent stays immutable, including after a lookup miss.
    if (isActive()) return view();
    if (!isText(date)) {
      message = '変更先の日時を選んでください。';
      return view();
    }
    operation = null;
    draftDate = date;
    phase = 'editing';
    message = date === currentDate
      ? '現在の予約と同じ日時です。別の変更先を選んでください。'
      : '変更先を選択しました。送信する前に内容を確認してください。';
    return view();
  }

  function review() {
    if (phase !== 'editing' || isActive()) return view();
    if (!draftDate || draftDate === currentDate) {
      message = '現在の予約と異なる変更先を選んでください。';
      return view();
    }
    phase = 'review';
    message = '現在の予約と変更先を確認してください。まだ変更依頼は送信していません。';
    return view();
  }

  function back() {
    if (isActive()) return view();
    if (phase === 'review' || TERMINAL.has(phase)) {
      operation = null;
      phase = 'editing';
      message = '変更先を選び直せます。送信前にもう一度、内容を確認してください。';
    }
    return view();
  }

  function serviceMessage(response) {
    return isText(response?.message) ? ` サービスからの案内: ${response.message}` : '';
  }

  function observeUnknown(op, callSerial, text) {
    if (!isActive(op) || callSerial < op.lastObservationSerial) return;
    op.lastObservationSerial = callSerial;
    // Cancellation receipt is retained even when the original request cannot be located.
    phase = op.cancellation === 'accepted' ? 'cancel_requested' : 'unknown';
    message = text;
    if (op.cancellation === 'accepted') {
      message += ' キャンセルの依頼は受け付けられていますが、最終結果は未確定です。';
    }
  }

  function observe(op, response, callSerial, source) {
    if (!isActive(op)) return;
    const status = response?.status;
    const validTerminal = status === 'succeeded' || status === 'failed' ||
      (source === 'lookup' && status === 'cancelled');

    // A terminal result wins over all older or later in-flight nonterminal replies.
    if (validTerminal) {
      op.outcome = status;
      phase = status;
      if (status === 'succeeded') {
        currentDate = isText(response.currentDate) ? response.currentDate : op.targetDate;
        message = op.cancellation === 'none'
          ? '予約の変更が確定しました。下の「確定済みの予約」が最新の日時です。'
          : 'キャンセルの確定前に、予約の変更が完了しました。下の「確定済みの予約」が最新の日時です。';
      } else if (status === 'failed') {
        message = '変更は成立しませんでした。確定済みの予約はそのままです。日時を選び直して再度確認できます。';
      } else {
        message = '変更依頼のキャンセルが確定しました。確定済みの予約はそのままです。';
      }
      message += serviceMessage(response);
      return;
    }

    if (callSerial < op.lastObservationSerial) return;
    if (status === 'pending') {
      op.lastObservationSerial = callSerial;
      // pending.currentDate is not confirmation that this requested mutation completed.
      phase = ['sending', 'accepted'].includes(op.cancellation) ? 'cancel_requested' : 'pending';
      if (op.cancellation === 'accepted') {
        message = 'キャンセル依頼は受け付けられました。変更の停止はまだ確定していません。結果を確認してください。';
      } else if (op.cancellation === 'sending') {
        message = 'キャンセルを依頼しています。変更の最終結果はまだ確定していません。';
      } else if (op.cancellation === 'unknown') {
        message = '変更は処理中です。キャンセル依頼の受付は確認できていません。結果確認またはキャンセルの再依頼ができます。';
      } else {
        message = '変更依頼を処理中です。確定済みの予約を保持しています。「結果を確認」で進捗を確認してください。';
      }
      message += serviceMessage(response);
    } else if (source === 'lookup' && status === 'not_found') {
      observeUnknown(op, callSerial,
        '今回の照会では依頼が見つかりませんでした。未実行という意味ではありません。同じ依頼IDを保持して、再度結果を確認してください。');
    } else {
      observeUnknown(op, callSerial,
        'サービスの応答を判定できませんでした。変更の成否は不明です。同じ依頼IDで結果を確認してください。');
    }
  }

  async function confirm() {
    if (!view().canSubmit) return view();
    if (phase === 'review') {
      let id;
      try {
        id = nextId();
        if (!isText(id) || usedIds.has(id)) throw new Error('request ID must be fresh');
      } catch {
        message = '新しい依頼IDを作成できませんでした。まだ送信していません。もう一度、変更を依頼してください。';
        return view();
      }
      usedIds.add(id);
      operation = {
        id,
        targetDate: draftDate,
        payload: Object.freeze({ bookingId, targetDate: draftDate, requestId: id }),
        startedAt: Date.now(),
        outcome: null,
        cancellation: 'none',
        submitInFlight: false,
        lookupInFlight: false,
        cancelInFlight: false,
        lastObservationSerial: 0
      };
    }
    const op = operation;
    const callSerial = ++serial;
    op.submitInFlight = true;
    phase = 'pending';
    message = '変更依頼を送信しています。結果が確定するまで、確定済みの予約を保持します。';
    try {
      const response = await api.submit(op.payload);
      observe(op, response, callSerial, 'submit');
    } catch {
      observeUnknown(op, callSerial,
        '送信の応答を受け取れませんでした。変更済みの可能性があります。同じ依頼IDで結果を確認できます。再送する場合も日時と依頼IDは変わりません。');
    } finally {
      op.submitInFlight = false;
    }
    return view();
  }

  async function check() {
    if (!view().canCheck) return view();
    const op = operation;
    const callSerial = ++serial;
    op.lookupInFlight = true;
    message = '同じ依頼IDで結果を確認しています。';
    try {
      const response = await api.lookup(op.id);
      observe(op, response, callSerial, 'lookup');
    } catch {
      observeUnknown(op, callSerial,
        '結果確認の応答を受け取れませんでした。変更の成否はまだ不明です。時間を置いて、同じ依頼IDで確認してください。');
    } finally {
      op.lookupInFlight = false;
    }
    return view();
  }

  async function cancel() {
    if (!view().canCancel) return view();
    const op = operation;
    op.cancelInFlight = true;
    op.cancellation = 'sending';
    phase = 'cancel_requested';
    message = 'キャンセルを依頼しています。受付だけでは、変更の停止は確定しません。';
    try {
      const response = await api.cancel(op.id);
      if (isActive(op)) {
        if (response?.accepted === true) {
          op.cancellation = 'accepted';
          phase = 'cancel_requested';
          message = 'キャンセル依頼は受け付けられました。まだキャンセル確定ではありません。「結果を確認」で最終結果を確認してください。';
        } else {
          op.cancellation = 'unknown';
          phase = 'unknown';
          message = 'キャンセルの受付を確認できませんでした。変更の成否も未確定です。結果を確認するか、キャンセルを再依頼してください。';
        }
      }
    } catch {
      if (isActive(op)) {
        op.cancellation = 'unknown';
        phase = 'unknown';
        message = 'キャンセルの応答を受け取れませんでした。依頼が届いた可能性があります。結果を確認するか、キャンセルを再依頼してください。';
      }
    } finally {
      op.cancelInFlight = false;
    }
    return view();
  }

  return { choose, review, confirm, check, cancel, back, view };
}

function isText(value) {
  return typeof value === 'string' && value.trim().length > 0;
}
