# Session B integration and resumption

This branch implements conditional Interaction Design / UX Flow instructions. Root README, root SKILL.md, main, Art Direction and other sessions' directories were not edited. The initial base already routes B to `modules/interaction-ux-flow/SKILL.md`.

## Integration boundary

- B owns task intent, transitions, evidence of completion, review, recovery and decision conditions.
- Art Direction owns typography, colour, composition and visual tone; existing React/data-layer instructions remain references rather than duplicated rules.
- C owns components, keyboard/focus/live-region mechanics, authentication/storage implementation and service adapters. Local trusted-input mocks do not prove backend authorization or secure persistence.
- D owns broader comparative methodology, held-out tasks, real browser/assistive-technology checks and human effectiveness. Controller and DOM passes are not evidence of human task-speed improvement.

## Concurrent PR2

[PR2](https://github.com/RNA4219/anything-frontend-product-design/pull/2) opened after this campaign started and contains overlapping B concepts. See `existing-pr-overlap.json` for the inspected revision and mappings. The new units formalize conditional decisions and add evidence; ordinary retry/review/resume concepts are not claimed as novel principles.

If PR2 is integrated, reconcile its `modules/interaction-ux-flow/SKILL.md` with this branch's entry. Preserve useful PR2 CLI/tests/references and route to the accepted instruction units without duplicating contradictory rules. This campaign did not change PR2, merge main, or choose merge order. No root entry edit is needed against the original base. Inspect later main changes before integrating.

## Reproduce from repository root

Read `modules/interaction-ux-flow/tests/README.md`. Use active R01 v4, not the archived invalid v1–v3 evaluator scores. Original candidate artifacts, evaluator errata and failed exploratory examples remain evidence; they intentionally retain defects and must not be advertised as the corrected product examples.

Use Python 3.12 and Node 24, plus jsdom 26.1.0 for the explicit DOM probes. `B_DOM_JSDOM_PATH` can select an installed jsdom module. Real browser launch was blocked in this environment, so there are no successful visual, keyboard, assistive-technology or human tests. CI was not executed by this campaign.

## Resume safely

1. Read `manifest.json`, then each completed round's `decision.json`; do not repeat their research or register duplicate canonical sources.
2. Inspect `git-checkpoint.json` and PR5's actual current head. The public GitHub commit and local checkpoint commit may have different metadata but their trees were compared before alignment.
3. Read `registry/B/backlog.jsonl` and `source-aliases.json`; reuse captured sections, and record new sections as capture history under the same canonical source.
4. For a substantive round, launch two real independent researchers concurrently; only after their results, launch a sankai analyst; parent registers and implements; then launch a separate critic. Maximum two children running beside the parent.
5. Freeze task criteria before implementation. Keep exploratory defects separate from predeclared scores, preserve initial artifacts and identify the exact tested revision.
6. Publish source URLs, locators, read scope and hashes. Keep third-party originals in the private research archive.

This is a resumable campaign, not completed coverage of all interaction design. The current manifest and later round decisions take precedence over this general handoff.
