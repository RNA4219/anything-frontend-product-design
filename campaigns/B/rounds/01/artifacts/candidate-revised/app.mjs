import { createFlow } from './flow.mjs';
import { createMockService } from './mock-service.mjs';

const $ = id => document.getElementById(id);
const key = 'booking-change-ui-v1';
const initialDate = '2026-12-08T14:00';
const labels = {
  editing: '希望日時の選択', review: '送信前の内容確認', pending: '変更処理は結果待ち',
  unknown: '変更結果は未確認', failed: '変更は不成立', succeeded: '予約日時の変更を確認',
  cancel_requested: '取消要求は受付済み・結果待ち', cancelled: '日時の変更処理は取消済み',
};
const openPhases = new Set(['pending', 'unknown', 'cancel_requested']);
const format = value => value ? `${value.slice(0, 4)}年${Number(value.slice(5, 7))}月${Number(value.slice(8, 10))}日 ${value.slice(11)}` : '未選択';
let flow;
let mock;
let pendingActions = 0;

function save(snapshot) {
  try {
    localStorage.setItem(key, JSON.stringify({ bookingId: 'R-204', ...snapshot }));
  } catch {
    $('storage-error').hidden = false;
    $('storage-error').textContent = '操作記録を保存できません。この画面を閉じずに結果を確認してください。操作番号を控えておくと照合できます。';
  }
}

function render(focus = false) {
  const v = flow.view();
  const isOpen = openPhases.has(v.phase);
  $('phase-label').textContent = labels[v.phase];
  $('status-card').dataset.phase = v.phase;
  $('status-message').textContent = v.message;
  $('current-date').textContent = format(v.currentDate);
  $('current-date').dateTime = v.currentDate;
  $('draft-date').textContent = format(v.draftDate);
  if (v.draftDate) $('draft-date').dateTime = v.draftDate;
  else $('draft-date').removeAttribute('datetime');
  $('operation-row').hidden = !v.operationId;
  $('operation-id').textContent = v.operationId ?? '';
  $('known-note').textContent = isOpen
    ? 'サービス側ですでに変更が成立している可能性があります。上記は最後に確認した日時であり、現在の予約状態の保証ではありません。'
    : '変更成功をサービスで確認できたときに、確認済み日時を更新します。';
  $('editing-panel').hidden = v.phase !== 'editing';
  $('review-panel').hidden = v.phase !== 'review';
  $('recovery-panel').hidden = !isOpen;
  $('finished-panel').hidden = !['failed', 'succeeded', 'cancelled'].includes(v.phase);
  $('review-current').textContent = format(v.currentDate);
  $('review-target').textContent = format(v.draftDate);
  $('review-button').disabled = !v.draftDate || v.draftDate === v.currentDate;
  $('confirm-button').disabled = !v.canSubmit;
  $('check-button').disabled = !v.canCheck;
  $('cancel-button').disabled = !v.canCancel;
  $('scenario').disabled = isOpen;
  $('reset-button').disabled = isOpen || pendingActions > 0;
  $('fail-lookup-button').disabled = !isOpen;
  for (const radio of document.querySelectorAll('input[name="target-date"]')) {
    radio.checked = radio.value === v.draftDate;
    radio.disabled = radio.value === v.currentDate;
  }
  $('finished-title').textContent = labels[v.phase];
  $('finished-detail').textContent = v.phase === 'succeeded'
    ? `予約 R-204 の確認できた日時は ${format(v.currentDate)} です。今回の変更は完了です。`
    : v.phase === 'failed'
      ? '別の候補へ変更するか、同じ希望を新しい依頼として再検討できます。送信前に内容をもう一度確認します。'
      : '今回の日時変更処理は終了しました。新しい日時変更を始めることができます。';
  $('new-change-button').textContent = v.phase === 'succeeded' ? '別の日時変更を始める' : '希望日時を見直す';
  const stats = mock.inspect();
  $('metrics').textContent = `模擬サービスの記録: 変更依頼 ${stats.submitCalls} 回 · 照会 ${stats.lookupCalls} 回 · 取消要求 ${stats.cancelCalls} 回 · 成立した日時変更 ${stats.mutationCount} 回`;
  save(v);
  if (focus) $('phase-label').focus();
}

async function action(name) {
  const previous = flow.view().phase;
  pendingActions += 1;
  try {
    const promise = flow[name]();
    render(previous !== flow.view().phase);
    await promise;
  } finally {
    pendingActions -= 1;
    render(previous !== flow.view().phase);
  }
}

function initialize() {
  // Persistence is required before enabling mutation controls in this demo.
  const probe = `${key}-probe`;
  localStorage.setItem(probe, 'ok');
  localStorage.removeItem(probe);
  const raw = localStorage.getItem(key);
  const saved = raw ? JSON.parse(raw) : null;
  if (saved && saved.bookingId !== 'R-204') throw new Error('保存した操作記録の対象予約が一致しません。');
  mock = createMockService({ storage: localStorage });
  mock.setMode($('scenario').value);
  flow = createFlow(mock, {
    bookingId: 'R-204',
    currentDate: saved?.currentDate ?? initialDate,
    nextId: () => `R-204-${crypto.randomUUID()}`,
    resume: saved ?? undefined,
  });
  render();
}

for (const radio of document.querySelectorAll('input[name="target-date"]')) {
  radio.addEventListener('change', () => { flow.choose(radio.value); render(); });
}
for (const [id, method] of [['review-button', 'review'], ['back-button', 'back'], ['new-change-button', 'back']]) {
  $(id).addEventListener('click', () => { flow[method](); render(true); });
}
for (const [id, method] of [['confirm-button', 'confirm'], ['check-button', 'check'], ['cancel-button', 'cancel']]) {
  $(id).addEventListener('click', () => { void action(method); });
}
$('scenario').addEventListener('change', () => mock.setMode($('scenario').value));
$('fail-lookup-button').addEventListener('click', () => {
  mock.failNextLookup();
  $('demo-message').textContent = '次の結果照会を1回だけ通信エラーにします。その後は同じ操作番号で再照会できます。';
});
$('reset-button').addEventListener('click', () => {
  if (pendingActions || openPhases.has(flow.view().phase)) return;
  mock.reset();
  localStorage.removeItem(key);
  $('demo-message').textContent = 'ローカルデモを初期状態に戻しました。';
  initialize();
  $('phase-label').focus();
});

try { initialize(); } catch (error) {
  $('storage-error').hidden = false;
  $('storage-error').textContent = `デモを開始できません: ${error.message} 操作を送信せず停止しました。保存領域とローカル配信の状態を確認してください。`;
  for (const control of document.querySelectorAll('button, input, select')) control.disabled = true;
}
