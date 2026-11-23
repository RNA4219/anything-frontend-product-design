# R04 evidence

The 96-record synthetic source/proposal, output contract, D1–D6 rubric, oracle and comparison protocol were fixed before candidate construction. J is baseline (accepted R03 instructions), S candidate. Both scored 6/6 with zero hard failures, once per arm. This does not establish superiority, equivalence or real-user benefit. Explicit assignment paths were not found in the provided artifacts, but methods can make assignment inferable. The critic is an independent thread of the same model family.

The candidate instruction/helper snapshot predates the output-file collision repair. Historical code under `instruction-snapshots/` is evidence, not the recommended executable. Use the current module's helper. The task agents' frozen inputs and generated outputs were not replaced after the repair. The critic verified that normal separate-output results are unchanged.

The critic registered 12 small independent cases before reading the parent's test fixtures or 96-record task; all 12 met the declared expectations. Researcher-proposed tests were visible in its input, so the fixture author was not blind to all hypotheses. A separate parent-originated hypothesis demonstrated input overwriting for same-path and symlink outputs. The original REVISE finding and destructive effects on disposable copies remain under `supplemental-initial/`; original input bytes were preserved in `.original.json` files. The repaired helper rejects same-path, symlink and hardlink aliases without changing either source, and saves normal output: 4/4 independent rechecks passed.

The parent ran the complete 70-method module suite from an isolated temporary copy without `campaigns/`; all passed. This includes 1200 synthetic records with a compensated ID loss, balanced membership swaps and source-preservation controls. It is not a production-scale migration benchmark.

Reproduce the current comparison from repository root:

```sh
python modules/product-information-architecture/checks/compare_inventory.py --before campaigns/A/rounds/R04/source-inventory.json --after campaigns/A/rounds/R04/proposed-inventory.json --output /tmp/afpd-A-R04-comparison.json
python -m unittest discover -s modules/product-information-architecture/tests -v
python campaigns/A/check_registry.py
```

The comparison returns COMPARED / NOT_EVALUATED. Differences are evidence to interpret against intended changes. An authorized rename or an unused concept's removal is not automatically a defect. Unknown external references, unsupported fields and source completeness remain explicit limits.

Both HTML samples were checked against the synthetic source: J 19 displayed rows / 13 unique records, S 16 rows / 13 unique records, zero observed source/value/role/scope mismatches. This is static inspection, not rendering, interaction, actual authorization, redirect/index execution or human usability. Raw third-party retrieval text are excluded from this public repository.

## Published instruction views

The concurrent integration base removed operational recording references. `publication-views.json` identifies the four public files with matching omissions. Frozen input manifests still describe the original experimental bytes, retained privately; these public views are not represented as byte-identical originals. Design instructions and the comparison helper are unchanged. The sampled design outputs retain their original evaluated bytes.
