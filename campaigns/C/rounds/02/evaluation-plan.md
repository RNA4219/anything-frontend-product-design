# Round 02: pre-implementation evaluation contract

This extends the frozen `plan.json` with research-informed inputs before candidate code is written. It does not change the acceptance rubric.

## Task and scope

Compile a product-owned set of primitive and semantic tokens for a booking interface in two declared themes. The same process must work for another role inventory without prescribing its palette or visual direction. The supported dialect, alias/type policy, theme merge policy, export namespace, and unsupported constructs must be explicit.

Use supported positive controls and deliberately invalid mutations of the same inputs. Compare a frozen, intentionally permissive declaration control with the candidate on missing references, cycles, type mismatch, theme-only defects, unsupported constructs, and output-name collisions. This control is authored for the experiment. It is neither a previous production validator nor a baseline model-generation run. No percentage improvement in design quality is inferred.

## Fixed gates

- Supported positive controls produce exact expected role values, dimensions with units, and deterministic CSS bytes.
- Missing/cyclic/type-invalid graphs fail with a theme/path diagnostic and no CSS result.
- Unsupported syntax is distinguished from a supported invalid value. The tool must never claim full DTCG conformance.
- Resolve the assembled graph independently for each declared theme. A later primitive override must affect its semantic aliases. A theme may intentionally repoint a role without changing its required type.
- Required role coverage is supplied by the product. Do not infer universal roles, palette values, tier counts, or contrast compliance.
- Generated CSS names and declared theme identities must not collide. Unsupported multi-file publication must not be presented as tested.
- No CSS runtime references are emitted in the bounded literal output. Runtime alias mutation, nested scopes, rendered contrast, forced-colors and browser support remain outside acceptance.
- The independent critic may add unseen valid and invalid cases without relaxing these gates. Record initial failures and later rechecks separately.

## Outcome labels

ACCEPT applies only to tested parsing/graph/theme/export contracts. Browser rendering and assistive technology remain unverified. A reproducible counterexample causes REVISE; unresolved interpretation or unavailable evidence causes HOLD. Same-model separate-task review is a useful second check, not human or cross-model evidence.
