"""Reproduce the deliberately shallow control versus the bounded candidate."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


control = module('baseline_control', Path(__file__).with_name('baseline_token_control.py'))
fixtures = module('fixtures', ROOT / 'modules/ui-engineering-design-system/tests/test_tokens.py')
cases = [('valid-booking-themes', fixtures.example(), True)]
cases.extend((name, data, False) for name, data in fixtures.bad_cases().items())
results = []
for name, data, expected in cases:
    result = fixtures.tokens.build(data)
    accepted = result['status'] == 'PASS_SUPPORTED_SCOPE'
    results.append({'case': name, 'expected_accept': expected,
                    'baseline_accept': control.accepts(data), 'candidate_accept': accepted,
                    'candidate_matches_expectation': accepted == expected,
                    'diagnostics': result['diagnostics']})
report = {'comparison': 'authored shallow declaration control, not model-generation effectiveness',
          'cases': results,
          'baseline_false_accepts': sum(r['baseline_accept'] and not r['expected_accept'] for r in results),
          'candidate_false_accepts': sum(r['candidate_accept'] and not r['expected_accept'] for r in results),
          'candidate_false_rejects': sum(not r['candidate_accept'] and r['expected_accept'] for r in results)}
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(not all(r['candidate_matches_expectation'] for r in results))
