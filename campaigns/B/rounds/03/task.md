# B-R03: resume with current authority and recover from conflicts

The task is to resume an interrupted edit of a booking or account record. A draft and a pending operation are different objects. The example has a current authenticated account, a stable resource ID, a last-confirmed resource revision, an unsent draft and (only if actually sent) an operation ID. A reopened view may discover a changed revision, expired authorization, a different account, or a lost response whose operation later succeeds.

Predeclared acceptance:

1. An unsent draft is not shown as saved server state; resumption does not submit it automatically.
2. Pending submission resumes by the same operation reference, not by creating a fresh side effect.
3. Data or operation IDs from account A cannot be displayed or applied as account B's task. A known account mismatch does not query a private resource as the new account.
4. Expired authorization yields reauthentication and resumes the intended task after identity/capability are rechecked; it does not claim the operation failed or succeeded.
5. Conditional update uses the last reviewed revision at the server decision point. A mismatch preserves the server's newer value and the user's draft; it offers a comparison and an explicit refreshed decision.
6. Reloading the latest revision does not silently mean the user approved overwriting it. A new confirmed choice is required where the changed facts alter the reviewed action.
7. A delayed reply from an older read/operation cannot overwrite a newer confirmed view or a different current account.
8. A result-query miss or expired idempotency/recovery record is not evidence that the original side effect never happened. Keep an honest unresolved state and the contract's remaining reconciliation route.

Scope: task state, identity of the current task, retained intent, comparison/review and truthful completion. C owns storage APIs, authentication component implementation and browser security mechanisms; B does not invent an authentication protocol or secure-storage guarantee. Fixtures exercise declared contracts, not a live identity provider or production API.

Use the existing PR2 concepts as prior work. New units should formalize and test missing boundary conditions, not claim that ordinary drafts, If-Match, or conflict dialogs are newly discovered principles. No generated efficacy comparison is implied in this round.
