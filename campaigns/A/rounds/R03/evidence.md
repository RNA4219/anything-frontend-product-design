# R03 evidence and limits

The fixed D1–D6 rubric and synthetic input predate candidate generation. W is candidate, Z baseline. Each arm was generated once. The critic scored both 6/6 with no hard failure; this is not evidence of superior or equivalent human performance. Assignment concealment was compromised: Z/design.md contains a baseline input path. That leak was reported before scoring and is retained rather than rewritten after the fact.

`instruction-snapshots/` preserves the actual Markdown instructions supplied to each task agent. The candidate freeze preceded C01–C03 repairs. Generated design arms were not regenerated after those repairs. The final accepted module includes the independently rechecked repairs.

The independent original counterexamples, including two semantic blind spots, are retained under `independent-evidence/counterexamples/`. Their original candidate results are not overwritten. Corrected results are under `independent-evidence/corrections/`. `correction-check.json` records 8 independently rechecked cases and the parent's alias pair. The parent ran all 57 unittest methods. The critic ran the original 55-method suite and the bounded post-repair checks.

Reproduce a case from the repository root:

```sh
python modules/product-information-architecture/checks/validate_plan.py --brief campaigns/A/rounds/R03/independent-evidence/counterexamples/ce_mandatory_capability_isolated/brief.json --plan campaigns/A/rounds/R03/independent-evidence/counterexamples/ce_mandatory_capability_isolated/plan.json
python -m unittest discover -s modules/product-information-architecture/tests -v
python campaigns/A/check_registry.py
```

The first command is expected to exit 1 with FAIL after the repair. Original results can be compared with `baseline-validator.py`. Historical absolute paths in critic records identify the original inspection locations; use the portable command above after checkout.

No browser rendering, actual interaction, redirect, permission enforcement, accessibility or human task study was performed. HTML evidence is source inspection. Information values, contextual applicability and prose-only task delivery remain semantic review items. Full third-party source texts are not included.
