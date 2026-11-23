# Session B integration and resumption

This branch implements conditional Interaction Design / UX Flow instructions. Root README, root SKILL.md, main, Art Direction and other sessions' directories were not edited. The initial base already routes B to `modules/interaction-ux-flow/SKILL.md`.

## Integration boundary

- B owns task intent, transitions, evidence of completion, review, recovery and decision conditions.
- Art Direction owns typography, colour, composition and visual tone; existing React/data-layer instructions remain references rather than duplicated rules.
- C owns components, keyboard/focus/live-region mechanics, authentication/storage implementation and service adapters. Local trusted-input mocks do not prove backend authorization or secure persistence.
- D owns broader comparative methodology, held-out tasks, real browser/assistive-technology checks and human effectiveness. Controller and DOM passes are not evidence of human task-speed improvement.

## Observed main integration and continuation

[PR2](https://github.com/RNA4219/anything-frontend-product-design/pull/2) and this campaign's former [PR5](https://github.com/RNA4219/anything-frontend-product-design/pull/5) were observed merged by an external operation while R04 was being prepared. This campaign did not call merge or update main. `existing-pr-overlap.json` remains the historical inspection record; `integration-r04.json` records the later observed state.

The continuation [Draft PR9](https://github.com/RNA4219/anything-frontend-product-design/pull/9) is open and was not merged by this campaign. The R04 continuation branch is `session-b/interaction-evolution-r04-20261123`, based on main `20f21fb9bb1b4d0921333ca1be683d6b42a60c63`. Its entry retains main's MIT license, task instructions, decisions route and shared fixture/CLI handoff links, alongside the accepted batch route. Main's booking CLI and reference files remain unchanged. No common root entry change is required against this integration base. Check later main changes before merging the continuation Draft PR.

## Reproduce from repository root

Read `modules/interaction-ux-flow/tests/README.md`. Use active R01 v4, not the archived invalid v1–v3 evaluator scores. Original candidate artifacts, evaluator errata and failed exploratory examples remain evidence; they intentionally retain defects and must not be advertised as the corrected product examples.

Use Python 3.12 and Node 24, plus jsdom 26.1.0 for the explicit DOM probes. `B_DOM_JSDOM_PATH` can select an installed jsdom module. Real browser launch was blocked in this environment, so there are no successful visual, keyboard, assistive-technology or human tests. CI was not executed by this campaign.

## Resume safely

1. Read `manifest.json`, then each completed round's `decision.json`; do not repeat their research or register duplicate canonical sources.
2. Inspect `git-checkpoint.json` and the continuation Draft PR's actual current head; PR5 is a merged historical checkpoint. The public GitHub commit and local checkpoint commit may have different metadata but their trees were compared before alignment.
3. Read `registry/B/backlog.jsonl` and `source-aliases.json`; reuse captured sections, and record new sections as capture history under the same canonical source.
4. For a substantive round, launch two real independent researchers concurrently; only after their results, launch a sankai analyst; parent registers and implements; then launch a separate critic. Maximum two children running beside the parent.
5. Freeze task criteria before implementation. Keep exploratory defects separate from predeclared scores, preserve initial artifacts and identify the exact tested revision.
6. Publish source URLs, locators, read scope and hashes. Keep third-party originals in the private research archive.

This is a resumable campaign, not completed coverage of all interaction design. The current manifest and later round decisions take precedence over this general handoff.

## Checkpoint after R04

Four rounds are complete out of the maximum twelve; R05 is queued and has not run. Nine Instruction Units are ACCEPT within their stated conditions. There are 35 canonical sources and 18 completed actual subagents (8 researchers, 4 analysts, 4 critics, 2 task builders). No child is intentionally left running. No saturation or complete-domain claim is made.

Next B priority is `B-008`, with a concrete plan at `rounds/05/plan.json`: multi-step dependent answers, current requirements and invalidated review. Prefer extending B-IU-006 where the decision is already covered. Reuse existing captures before reacquiring material. R04 additionally hands service-specific identity/outcome adapters to C under B-X-C02. Native browser, keyboard/AT and human or held-out efficacy evaluation remain with C/D.

The final local check record is `final-verification.json`. Fixed R01 v4 scores remained equal between baseline and candidate. R01 evaluator errata disclose that a revised criterion was produced after part of the baseline result was seen. Use its results as bounded conformance evidence, not proof of causal improvement. R02–R04 are conformance and independently reviewed defect-detection/repair exercises, not new generated-baseline experiments.

For independent DOM reproduction, read the round-specific instructions and run from the repository root, with jsdom 26.1.0 available:

```sh
B_DOM_JSDOM_PATH=/absolute/path/to/jsdom node campaigns/B/rounds/03/independent/reproduce-dom-events.mjs
B_DOM_JSDOM_PATH=/absolute/path/to/jsdom node campaigns/B/rounds/04/independent/reproduce-dom-events.mjs
```

`publication-map.json` in each independent evidence directory maps private original hashes to public copy hashes. Path redaction or portable harness changes are explicit; raw originals remain in the private checkpoint. Old and intermediate failures are preserved, including R03's authority regression and R04's misleading post-cancellation guidance.

The current PR head is authoritative for the latest Git commit. `git-checkpoint.json` records known prior published/local mappings rather than pretending a commit can embed its own final SHA. The private resume record is updated after publication with the exact latest head.
