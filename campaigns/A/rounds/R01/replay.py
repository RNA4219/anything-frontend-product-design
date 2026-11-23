#!/usr/bin/env python3
"""Replay fixed counterexamples through inherited and context-aware checkers.

The inherited 1.0 contract did not model the extra context. Its PASS is recorded
as a coverage gap, not a measured human or LLM performance rate.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MODULE = ROOT / 'modules/product-information-architecture'
sys.path.insert(0, str(MODULE / 'tests'))
from test_context import case, retire, validator

spec = importlib.util.spec_from_file_location('frozen_baseline', HERE / 'baseline-validator.py')
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


def build_cases():
    cases = []
    b, p = case(); cases.append(('same-context-keep', b, p, 'PASS'))
    b, p = case(); p['features'][1].update(disposition='merge', target='main'); p['screens'][0]['feature_ids']=['main']
    cases.append(('equivalent-alias', b, p, 'PASS'))
    b, p = case(); b['feature_requests'][1]['scope']='all-records'; p['features'][1].update(disposition='merge',target='main'); p['screens'][0]['feature_ids']=['main']
    cases.append(('different-scope-same-label', b, p, 'FAIL'))
    b, p = case(); b['feature_requests'][0]['context_constraints']=['desktop']; p['features'][0]['context_constraints']=['desktop']; retire(p)
    cases.append(('mobile-to-unavailable-desktop', b, p, 'FAIL'))
    b, p = case(); retire(p); b['feature_requests'][0]['availability']='planned'
    cases.append(('roadmap-as-current-replacement', b, p, 'HOLD'))
    b, p = case(); retire(p,'ended')['evidence_refs']=['unobserved']
    cases.append(('missing-observations-as-no-demand', b, p, 'HOLD'))
    b, p = case(); p['features'][1]['disposition']='defer'; p['screens'][0]['feature_ids']=['main']
    cases.append(('unexplained-existing-feature-withdrawal', b, p, 'FAIL'))
    b, p = case(); retire(p,'ended'); cases.append(('documented-optional-retirement', b, p, 'PASS'))
    b, p = case(); retire(p); b['feature_requests'][0]['availability']='partial'; p['features'][0]['verified_outcomes']=['read-record']
    cases.append(('verified-partial-replacement', b, p, 'PASS'))
    b, p = case(); b['feature_requests'][1]['lifecycle']='proposed'; p['features'][1].update(disposition='defer',revisit='Revisit on next discovery result');p['screens'][0]['feature_ids']=['main']
    cases.append(('reversible-new-proposal-deferral', b, p, 'PASS'))
    return cases


rows = []
for name, brief, plan, expected in build_cases():
    old = copy.deepcopy(plan); old['schema_version']='1.0'
    a, b = baseline.validate(brief, old), validator.validate(brief, plan)
    rows.append({'case': name, 'expected_candidate': expected, 'baseline_status': a['status'],
                 'candidate_status': b['status'], 'candidate_codes': sorted({x['code'] for x in b['issues']}),
                 'matches_expected': b['status']==expected})
result = {'evaluation': 'contract-coverage replay', 'cases': rows,
          'matched': sum(x['matches_expected'] for x in rows), 'total': len(rows),
          'newly_detected_context_cases': sum(x['baseline_status']=='PASS' and x['candidate_status']!='PASS' for x in rows),
          'human_usability': 'not measured', 'llm_effect': 'not measured by this replay'}
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if all(x['matches_expected'] for x in rows) else 1)
