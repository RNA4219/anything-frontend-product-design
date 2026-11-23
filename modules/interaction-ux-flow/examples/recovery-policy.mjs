// Illustrative decision adapter. Callers must supply evidence from their real API.
// This function neither retries requests nor establishes a service guarantee.
export function decideRecovery(input = {}) {
  if (['succeeded', 'failed', 'cancelled'].includes(input.verifiedOutcome))
    return 'show_verified_result';
  if (input.verifiedUnapplied === true) return 'repair_then_submit';
  if (input.methodSemanticsIdempotent === true && input.errorAllowsRetry === true)
    return 'retry_by_contract';
  const r = input.replay;
  if (r && r.supported === true && typeof r.requestId === 'string' && r.requestId.length > 0 &&
      r.samePayload === true && r.scopeMatches === true && r.errorAllowsRetry === true &&
      Number.isFinite(r.now) && Number.isFinite(r.validUntil) && r.now < r.validUntil)
    return 'replay_same_intent';
  return 'reconcile';
}
