"use strict";

const dates = {
  "08": "12月8日 14:00",
  "10": "12月10日 14:00",
  "11": "12月11日 14:00",
};
const scenarios = {
  normal: "通常",
  conflict: "12月10日の枠が送信時に埋まる",
  "unknown-applied": "応答不明（更新済み）",
  "unknown-unapplied": "応答不明（未更新）",
};
const scenarioParam = new URLSearchParams(location.search).get("scenario");
const scenario = Object.hasOwn(scenarios, scenarioParam) ? scenarioParam : "normal";
const storageKey = `booking-change-demo:v1:${scenario}`;
const initialRecord = {
  current: "08",
  blocked10: false,
  incidentSeen: false,
  appliedCount: 0,
  operation: null,
};
const panels = {
  list: "reservation-list",
  choose: "choose-section",
  conflict: "choose-section",
  confirm: "confirm-section",
  pending: "confirm-section",
  unknown: "unknown-section",
  checking: "unknown-section",
  unchanged: "unchanged-section",
  success: "success-section",
  "storage-error": "storage-section",
};
const element = (id) => document.getElementById(id);
const app = element("booking-app");
const status = element("booking-status");
const slotForm = element("slot-form");
const slotInputs = [element("slot-10"), element("slot-11")];
const busyControls = [
  element("submit-change"),
  element("edit-selection"),
  element("check-current"),
  element("reset-demo"),
];

let record;
let state;
let selection = null;
let reviewedFrom;

function isDate(value) {
  return typeof value === "string" && Object.hasOwn(dates, value);
}

function readRecord() {
  const saved = localStorage.getItem(storageKey);
  if (saved === null) return initialRecord;

  const value = JSON.parse(saved);
  const operation = value?.operation;
  const validOperation = operation === null || (
    operation &&
    typeof operation.id === "string" &&
    isDate(operation.from) &&
    slotInputs.some((input) => input.value === operation.to) &&
    operation.from !== operation.to &&
    [operation.from, operation.to].includes(value.current) &&
    (operation.phase === "unknown" ||
      (operation.phase === "unapplied" && value.current === operation.from))
  );
  if (
    !isDate(value?.current) ||
    typeof value.blocked10 !== "boolean" ||
    typeof value.incidentSeen !== "boolean" ||
    !Number.isSafeInteger(value.appliedCount) ||
    value.appliedCount < 0 ||
    !validOperation
  ) {
    throw new Error("Invalid booking sample data");
  }
  return value;
}

function saveRecord(nextRecord) {
  localStorage.setItem(storageKey, JSON.stringify(nextRecord));
  record = nextRecord;
}

function show(nextState, focusId) {
  state = nextState;
  app.dataset.state = state;
  for (const panelId of new Set(Object.values(panels))) {
    element(panelId).hidden = panelId !== panels[state];
  }

  const busy = state === "pending" || state === "checking";
  for (const button of busyControls) {
    if (busy) button.setAttribute("aria-disabled", "true");
    else button.removeAttribute("aria-disabled");
  }
  status.textContent = {
    pending: "予約変更を送信しています。",
    checking: "現在の予約を確認しています。",
  }[state] ?? "";

  if (focusId) element(focusId).focus();
}

function displayDate(id, date) {
  element(id).textContent = dates[date];
}

function showList(focus = true) {
  selection = null;
  displayDate("current-date", record.current);
  show("list", focus ? "open-change" : undefined);
}

function showChoose({ restoreSelection = false, conflictMessage = "" } = {}) {
  displayDate("choose-current-date", record.current);
  const conflict = element("conflict-message");
  const heading = element("choose-heading");
  conflict.hidden = !conflictMessage;
  conflict.textContent = conflictMessage;
  if (conflictMessage) heading.setAttribute("aria-describedby", conflict.id);
  else heading.removeAttribute("aria-describedby");

  let checkedInput;
  for (const input of slotInputs) {
    const currentSlot = input.value === record.current;
    const taken = input.value === "10" && record.blocked10;
    input.disabled = currentSlot || taken;
    input.checked = !input.disabled && input.value === selection;
    element(`${input.id}-note`).textContent = currentSlot
      ? "（予約済みの日時）"
      : taken ? "（空きなし）" : "";
    if (input.checked) checkedInput = input;
  }

  const hasAvailableSlot = slotInputs.some((input) => !input.disabled);
  element("review-change").disabled = !hasAvailableSlot;
  element("slot-help").textContent = hasAvailableSlot
    ? "希望する日時を一つ選んでください。"
    : "現在選べる候補はありません。";
  const focusId = restoreSelection && checkedInput ? checkedInput.id : heading.id;
  show(conflictMessage ? "conflict" : "choose", focusId);
}

function showConfirm() {
  reviewedFrom = record.current;
  displayDate("before-date", reviewedFrom);
  displayDate("after-date", selection);
  show("confirm", "confirm-heading");
}

function showUnknown() {
  displayDate("unknown-target-date", record.operation.to);
  show("unknown", "unknown-heading");
}

function showUnchanged() {
  displayDate("unchanged-date", record.current);
  displayDate("unchanged-target-date", record.operation.to);
  show("unchanged", "unchanged-heading");
}

function showSuccess() {
  displayDate("success-date", record.current);
  show("success", "success-heading");
}

function showStorageError() {
  show("storage-error", "storage-heading");
}

function restoreFromRecord(focus = true) {
  if (record.operation?.phase === "unknown") showUnknown();
  else if (record.operation?.phase === "unapplied") showUnchanged();
  else showList(focus);
}

function resume(focus = true) {
  try {
    record = readRecord();
    restoreFromRecord(focus);
  } catch {
    showStorageError();
  }
}

function leaveSelection() {
  try {
    record = readRecord();
    if (record.operation?.phase === "unknown") {
      showUnknown();
      return;
    }
    if (record.operation) saveRecord({ ...record, operation: null });
    showList();
  } catch {
    showStorageError();
  }
}

function waitForMockResponse() {
  return new Promise((resolve) => setTimeout(resolve, 550));
}

async function submitChange() {
  if (state !== "confirm") return;

  try {
    record = readRecord();
    if (record.operation?.phase === "unknown") {
      showUnknown();
      return;
    }
    if (record.current !== reviewedFrom || (selection === "10" && record.blocked10)) {
      selection = null;
      showChoose({ conflictMessage: "予約または候補の状況が変わりました。空き枠を選び直してください。" });
      return;
    }

    const previous = record.operation;
    const sameChange = previous?.from === reviewedFrom && previous?.to === selection;
    const operation = {
      id: sameChange ? previous.id : crypto.getRandomValues(new Uint32Array(4)).join("-"),
      from: reviewedFrom,
      to: selection,
      phase: "unknown",
    };
    saveRecord({ ...record, operation });
    show("pending");
    await waitForMockResponse();

    record = readRecord();
    if (record.operation?.id !== operation.id || record.operation.phase !== "unknown") {
      restoreFromRecord();
      return;
    }
    if (scenario === "conflict" && operation.to === "10") {
      saveRecord({ ...record, blocked10: true, operation: null });
      selection = null;
      showChoose({ conflictMessage: "12月10日 14:00 の枠が埋まりました。別の空き枠を選んでください。" });
      return;
    }

    const loseResponse = scenario.startsWith("unknown-") && !record.incidentSeen;
    const applyChange = !loseResponse || scenario === "unknown-applied";
    saveRecord({
      ...record,
      current: applyChange ? operation.to : record.current,
      appliedCount: record.appliedCount + Number(applyChange),
      incidentSeen: record.incidentSeen || loseResponse,
      operation: loseResponse ? operation : null,
    });
    if (loseResponse) showUnknown();
    else showSuccess();
  } catch {
    showStorageError();
  }
}

async function checkCurrent() {
  if (state !== "unknown") return;

  const operation = record.operation;
  show("checking");
  await waitForMockResponse();

  try {
    record = readRecord();
    if (record.operation?.id !== operation.id || record.operation.phase !== "unknown") {
      restoreFromRecord();
      return;
    }
    if (record.current === operation.to) {
      saveRecord({ ...record, operation: null });
      showSuccess();
      return;
    }
    saveRecord({ ...record, operation: { ...operation, phase: "unapplied" } });
    showUnchanged();
  } catch {
    showStorageError();
  }
}

element("open-change").addEventListener("click", () => showChoose());
slotForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (state !== "choose" && state !== "conflict") return;

  selection = new FormData(slotForm).get("slot");
  if (selection) showConfirm();
});
element("cancel-change").addEventListener("click", leaveSelection);
element("edit-selection").addEventListener("click", () => {
  if (state === "confirm") showChoose({ restoreSelection: true });
});
element("submit-change").addEventListener("click", submitChange);
element("check-current").addEventListener("click", checkCurrent);
element("retry-change").addEventListener("click", () => {
  selection = record.operation.to;
  showConfirm();
});
element("return-after-unchanged").addEventListener("click", leaveSelection);
element("return-to-list").addEventListener("click", () => resume());
element("retry-storage").addEventListener("click", () => resume());
element("reset-demo").addEventListener("click", () => {
  if (state === "pending" || state === "checking") return;

  try {
    localStorage.removeItem(storageKey);
    resume();
  } catch {
    showStorageError();
  }
});

element("scenario-label").textContent = scenarios[scenario];
element("demo-tools").hidden = false;
resume(false);
