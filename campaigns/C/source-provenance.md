# SESSION C — source acquisition and deduplication

Three rounds produced 46 source records, indexed as 44 canonical documents. Two repeated canonical records were merged by document URL while preserving source-specific sections, source IDs and research pointers. This is document deduplication, not a finding of semantic saturation.

The actual imozuru `fetch.py` was attempted 8 times in round 01, twice in round 02 and twice in round 03. All 12 attempts failed DNS in this execution environment. The failures are retained; neither those attempts nor partial reader extracts are reported as full original-page downloads. Researchers performed source/citation/hyperlink chasing through accessible primary sources and retained partial captures and query records privately. Early batches with incomplete hit records are labeled as such in the research artifacts.

## Complete pinned repository files obtained separately

The formal repository connector returned base64 source files. Their decoded Git blob SHA-1 matched the repository response; SHA-256, byte counts and pinned URLs are in the public source records below. Raw third-party source bytes remain outside the public repository.

| Source record | Repository artifact | Commit | Bytes |
| --- | --- | --- | ---: |
| C-S018 | design-tokens/community-group, 2025.10 Format HTML | 882ebd6716abef9a46d8ef5fb12e82009d6cee2e | 355370 |
| C-S020 | design-tokens/community-group, 2025.10 Color HTML | 882ebd6716abef9a46d8ef5fb12e82009d6cee2e | 153272 |
| C-S033 | w3c/wcag, target-size-minimum source HTML | 2766fae25fc8286f60181d655115cba054b797e1 | 23872 |

These are complete files from the stated repository commits. This does not establish byte identity with live HTTP pages, deployment commit identity, included assets, or embedded/generated sections. Original researcher reports retain their historical partial-reader labels; the repository acquisitions are supplementary provenance, not a retroactive rewrite.

For every instruction, use `registry/C/skills/*` source_refs to reach the research record and section, then the canonical `registry/C/sources/*` record. `campaigns/C/check_registry.py` checks pointer identity and local evidence existence only; it does not judge source quality, interpret source text, or prove implemented behavior.
