/**
 * Booking-change state machine. The service owns the outcome; currentDate is
 * only the last confirmed date. Unresolved requests are never resubmitted.
 * The optional resume snapshot is used solely by the local demonstration UI.
 */
export function createFlow(api, options) {
  if (!api || typeof api.submit !== 'function') throw new TypeError('api.submit is required');
  if (!options || typeof options.nextId !== 'function') throw new TypeError('nextId is required');
  if (!options.bookingId || !validDate(options.currentDate)) throw new TypeError('A booking ID and valid currentDate are required');

  const bookingId = options.bookingId;
  const unsettled = new Set(['pending', 'unknown', 'cancel_requested']);
  const terminal = new Set(['failed', 'succeeded', 'cancelled']);
  const usedIds = new Set();
  let currentDate = options.currentDate;
  let draftDate = null;
  let phase = 'editing';
  let message = '変更希望日時を選んでください。送信前に内容を確認できます。';
  let operation = null;

  function makeOperation(id, target) {
    return {
      id, target,
      payload: Object.freeze({ bookingId, targetDate: target, requestId: id }),
      terminal: false,
      submitBusy: false, checkBusy: false, cancelBusy: false,
      cancelAttempted: false, cancelAccepted: false,
      submitPromise: null, checkPromise: null, cancelPromise: null,
    };
  }

  // A reload may recover the same immutable intent, but never sends it again.
  if (options.resume) {
    const saved = options.resume;
    draftDate = typeof saved.draftDate === 'string' ? saved.draftDate : null;
    if (unsettled.has(saved.phase)) {
      if (typeof saved.operationId !== 'string' || !saved.operationId || !validDate(draftDate)) {
        throw new Error('保存した未確定操作の情報が不足しています。新しい変更は送信せず、操作記録を確認してください。');
      }
      operation = makeOperation(saved.operationId, draftDate);
      operation.cancelAccepted = saved.phase === 'cancel_requested';
      operation.cancelAttempted = operation.cancelAccepted || saved.canCancel === false;
      usedIds.add(operation.id);
      phase = 'unknown';
      message = '前回の変更操作を復元しました。現在の結果は未確認です。同じ操作番号で結果を確認してください。';
      if (operation.cancelAccepted) message += ' 取消要求は受付済みですが、取消完了は未確認です。';
    } else if (terminal.has(saved.phase) && typeof saved.operationId === 'string' && validDate(draftDate)) {
      operation = makeOperation(saved.operationId, draftDate);
      operation.terminal = true;
      usedIds.add(operation.id);
      phase = saved.phase;
      message = {
        succeeded: '前回、予約日時の変更成功を確認しました。表示日時は最後に確認した予約日時です。',
        failed: '前回の変更は不成立と確認済みです。希望日時を見直して、新しい変更を開始できます。',
        cancelled: '前回の日時変更処理は取消済みと確認しました。予約自体の取消ではありません。',
      }[phase];
    }
  }

  function unresolved() {
    return Boolean(operation && !operation.terminal && unsettled.has(phase));
  }

  function view() {
    return {
      phase,
      currentDate,
      draftDate,
      operationId: operation?.id ?? null,
      message,
      canSubmit: phase === 'review' && validDate(draftDate) && draftDate !== currentDate,
      canCancel: unresolved() && !operation.cancelBusy && !operation.cancelAttempted,
      canCheck: unresolved() && !operation.checkBusy,
    };
  }

  function blockEditing() {
    message = '変更結果が確定するまで、希望日時の変更や別の変更送信はできません。同じ操作番号で結果を確認してください。';
    return view();
  }

  function choose(date) {
    if (unresolved()) return blockEditing();
    operation = null;
    phase = 'editing';
    draftDate = typeof date === 'string' ? date : '';
    message = !validDate(draftDate)
      ? '有効な変更希望日時を選んでください。'
      : draftDate === currentDate
        ? '最後に確認した予約日時と同じです。別の日時を選んでください。'
        : '希望日時を選びました。「変更内容を確認」で、送信前に見直せます。';
    return view();
  }

  function review() {
    if (unresolved()) return blockEditing();
    if (!validDate(draftDate) || draftDate === currentDate) {
      phase = 'editing';
      message = '最後に確認した予約日時とは異なる、有効な希望日時を選んでください。';
      return view();
    }
    operation = null;
    phase = 'review';
    message = '対象の予約と変更前・変更後の日時を確認してください。「この内容で変更を依頼」でサービスへ送信します。';
    return view();
  }

  function back() {
    if (unresolved()) return blockEditing();
    operation = null;
    phase = 'editing';
    message = '希望日時を保持しています。日時を選び直すか、もう一度内容を確認できます。';
    return view();
  }

  function isActive(op) {
    return operation === op && !op.terminal;
  }

  function serviceMessage(result) {
    return typeof result?.message === 'string' && result.message ? ` サービスからの説明: ${result.message}` : '';
  }

  function unknown(op, explanation) {
    if (!isActive(op)) return;
    phase = 'unknown';
    message = explanation + ' 最後に確認した日時と変更希望を保持しています。同じ操作番号で結果を確認してください。';
    if (op.cancelAccepted) message += ' 取消要求の受付は確認済みですが、取消完了は未確認です。';
  }

  function applyOutcome(op, result, source) {
    if (!isActive(op)) return;
    const allowed = source === 'lookup'
      ? ['pending', 'succeeded', 'failed', 'cancelled', 'not_found']
      : ['pending', 'succeeded', 'failed'];
    if (!result || !allowed.includes(result.status)) {
      unknown(op, 'サービス応答から変更結果を判断できません。');
      return;
    }
    switch (result.status) {
      case 'succeeded':
        op.terminal = true;
        currentDate = validDate(result.currentDate) ? result.currentDate : op.target;
        phase = 'succeeded';
        message = op.cancelAttempted
          ? '変更成功を確認しました。取消の完了は確認されていません。表示日時が今回確認できた予約日時です。'
          : '予約日時の変更成功を確認しました。表示日時が今回確認できた予約日時です。';
        message += serviceMessage(result);
        break;
      case 'failed':
        op.terminal = true;
        phase = 'failed';
        message = '今回の日時変更は不成立と確認しました。希望日時を見直して、新しい変更を開始できます。' + serviceMessage(result);
        break;
      case 'cancelled':
        op.terminal = true;
        phase = 'cancelled';
        message = '日時の変更処理が取り消されたことを確認しました。予約自体の取消ではありません。' + serviceMessage(result);
        break;
      case 'pending':
        phase = op.cancelAccepted ? 'cancel_requested' : 'pending';
        message = op.cancelAccepted
          ? '変更処理の取消要求は受付済みです。取消完了はまだ確認できていません。結果を確認してください。'
          : op.cancelAttempted
            ? '日時変更は処理中です。変更の成立と取消要求の結果は未確認です。同じ操作番号で結果を確認してください。'
            : '日時変更は処理中です。変更の成立はまだ確認できていません。結果を確認するか、変更処理の取消を依頼できます。';
        message += serviceMessage(result);
        break;
      case 'not_found':
        unknown(op, '照会先に操作記録が見つかりませんでした。これは変更が実行されていない証拠ではありません。新しい変更を送信せず、再度結果を確認してください。');
        break;
    }
  }

  async function submitOperation(op) {
    try {
      applyOutcome(op, await api.submit(op.payload), 'submit');
    } catch {
      unknown(op, '送信の応答を受け取れず、変更結果を確認できません。サービス側で変更済みの可能性があります。');
    } finally {
      op.submitBusy = false;
    }
    return view();
  }

  async function confirm() {
    if (operation?.submitBusy) return operation.submitPromise;
    if (!view().canSubmit) return view();
    let id;
    try { id = options.nextId(); } catch {
      message = '操作番号を作成できませんでした。変更は送信していません。もう一度送信できます。';
      return view();
    }
    if (typeof id !== 'string' || !id || usedIds.has(id)) {
      message = '新しい操作番号を作成できませんでした。変更は送信していません。';
      return view();
    }
    usedIds.add(id);
    const op = makeOperation(id, draftDate);
    operation = op;
    op.submitBusy = true;
    phase = 'pending';
    message = '変更要求を送信しています。変更結果はまだ確認できていません。';
    op.submitPromise = submitOperation(op);
    return op.submitPromise;
  }

  async function lookupOperation(op) {
    try {
      applyOutcome(op, await api.lookup(op.id), 'lookup');
    } catch {
      unknown(op, '結果の照会に失敗しました。元の変更が失敗したかどうかは分かりません。');
    } finally {
      op.checkBusy = false;
    }
    return view();
  }

  async function check() {
    if (operation?.checkBusy) return operation.checkPromise;
    if (!view().canCheck) return view();
    const op = operation;
    op.checkBusy = true;
    message = '同じ操作番号で変更結果を照会しています。';
    op.checkPromise = lookupOperation(op);
    return op.checkPromise;
  }

  async function cancelOperation(op) {
    try {
      const result = await api.cancel(op.id);
      if (isActive(op)) {
        if (result?.accepted === true) {
          op.cancelAccepted = true;
          phase = 'cancel_requested';
          message = '変更処理の取消要求を受け付けたことを確認しました。取消完了ではありません。変更が先に完了する場合もあるため、結果を確認してください。';
        } else {
          unknown(op, '変更処理の取消要求の受付を確認できませんでした。');
        }
      }
    } catch {
      unknown(op, '取消要求の応答を受け取れませんでした。変更や取消が成立したかは未確認です。');
    } finally {
      op.cancelBusy = false;
    }
    return view();
  }

  async function cancel() {
    if (operation?.cancelBusy) return operation.cancelPromise;
    if (!view().canCancel) return view();
    const op = operation;
    op.cancelAttempted = true;
    op.cancelBusy = true;
    message = '日時の変更処理に対する取消要求を送信しています。取消はまだ確定していません。';
    op.cancelPromise = cancelOperation(op);
    return op.cancelPromise;
  }

  return Object.freeze({ choose, review, confirm, check, cancel, back, view });
}

function validDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(value)) return false;
  const parsed = new Date(`${value}:00Z`);
  return Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0, 16) === value;
}
