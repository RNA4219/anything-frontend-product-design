# B-R02 representative tasks and fixed acceptance

This round extends the previously frozen plan. It tests flow decisions and runnable state/event examples. It does not estimate the causal effect of giving an LLM a Skill: R01 contains the separately generated comparison.

## Application repair and review

An application captures name, email and delivery method (pickup or shipping). Shipping additionally requires an address. The review displays effective answers and offers Change links. Submitting is consequential; before submission the user must see the final effective answers and be able to amend them. A server response may reject the email while accepting all other entered values as draft inputs. Rejection is not successful submission. No client assertion establishes server persistence.

Pass conditions: preserve valid unrelated inputs; identify rejected field and a repair action; a changed effective answer invalidates old review; unrelated unchanged answers need no re-entry. If pickup is selected, stale shipping address must not silently be submitted as an active answer. Server/global errors cannot be attached to a random input. An unknown response uses R01 reconciliation and is not declared a correctable field rejection.

## Reversible archive and asynchronous business compensation

Local archive can be undone using a verified before-state while item identity/revision matches and the offer is valid. At/after the advertised expiry, do not claim restoration without a new verified route. If the item has changed elsewhere, do not silently overwrite the new state. An external compensation API can accept a request, later succeed, or later fail; acceptance does not restore the original state. Show the action's exact scope and any residual effect stated by its contract. A local text edit does not require distributed-system machinery.

Pass conditions: local undo returns the intended item and guards expiry/revision; pending or failed compensation is never 'restored'; failure retains a next action and reference; safe simple edits do not receive unconditional confirmation screens. Each observed outcome is compared with a fixture backend/state, not just a label.

## Evidence boundaries

The parent implements original executable examples after research/analysis. Independent Critic executes them, checks conditions against originals, and injects counterexamples. Deliberately defective controls test fault detection; they are not called generated baseline arms. No claim of user comprehension, real backend conformance or assistive-technology testing is allowed without separate evidence. New exploratory findings are separated from these predeclared acceptance criteria.
