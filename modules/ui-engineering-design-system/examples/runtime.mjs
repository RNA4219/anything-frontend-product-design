// Pure boundary helpers. Browser/AT behavior must be tested separately.
export function guardedAction(canExecute, execute) {
  return (...args) => canExecute() === true ? {executed: true, value: execute(...args)} : {executed: false};
}

// For an owned custom-modal layer only; native dialog delegates background to the UA.
export function releaseOwnedLayer(cleanup, restoreFocus) {
  cleanup();
  return restoreFocus();
}

export function needsFallback({modal, focusWasInside, activeIsUsable, requestedNextStep}) {
  if (!modal && !focusWasInside) return false;
  return requestedNextStep === true || activeIsUsable !== true;
}
