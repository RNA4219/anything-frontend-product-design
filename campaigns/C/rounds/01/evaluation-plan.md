# Round 01 frozen evaluation plan

Freeze point: before candidate implementation. Browser outcomes require real browser execution; a static or model-based check cannot substitute.

## Comparison

Use a hand-authored defective component contract as an adversarial baseline and a corrected contract for the same booking task. This measures defect detection in specified cases, not LLM generation uplift or production usability. Preserve both files.

## Oracles

1. Reject a navigation contract without a destination.
2. Reject an action button whose non-submit purpose leaves type unspecified.
3. Reject readonly on an inapplicable input type.
4. Reject a native-disabled field whose required submission value has no separate serialization plan.
5. Reject an aria-disabled action with an unguarded declared activation path.
6. Reject a native modal implemented with show() or by changing open directly.
7. Reject tabindex on native dialog.
8. Reject unconditional background cleanup conditional on an existing invoker.
9. Reject a nonmodal focus trap or unconditional focus return.
10. Accept equivalent valid native or explicitly contracted custom implementations.
11. Fail closed on invalid input structures; never print PASS for malformed contracts.
12. Browser suite must cover actual keyboard activation, FormData, modal/nonmodal focus and invoker deletion; record BLOCKED if browser launch or URL policy prevents execution.

## Decision rule

Source consistency + static contract tests are necessary but insufficient for browser-behavior ACCEPT. Until browser/AT evidence exists, units covering those behaviors remain HOLD. No numerical generation effectiveness claim. Critic must return file/position, symptom, evidence, impact, correction.
