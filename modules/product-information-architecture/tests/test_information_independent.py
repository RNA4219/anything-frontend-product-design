"""Replay bounded, mechanically decidable cases authored by the R03 critic."""
import copy
import json
from pathlib import Path
import unittest
from test_validate import validator

ROOT = Path(__file__).parent / 'independent-information-fixtures'


def load_case(name):
    return tuple(json.loads((ROOT / name / n).read_text()) for n in ['brief.json', 'plan.json'])


class IndependentInformationTests(unittest.TestCase):
    def test_independent_information_and_reachability_cases(self):
        for name, expected in json.loads((ROOT / 'expectations.json').read_text())['cases'].items():
            with self.subTest(case=name):
                b, p = load_case(name)
                result = validator.validate(b, p)
                self.assertEqual(expected, result['status'], result)

    def test_mandatory_alias_uses_the_reachable_canonical_capability(self):
        # Parent-authored extension: alias removal must not erase its obligation,
        # and resolving a valid alias must not require an extra owning screen.
        b, p = load_case('control_mandatory_capabilities_separate_stages')
        old = next(f for f in b['feature_requests'] if f['id'] == 'f_preflight')
        canonical = copy.deepcopy(old)
        canonical.update(id='f_checksheet', mandatory=False)
        b['feature_requests'].append(canonical)
        alias = next(f for f in p['features'] if f['id'] == 'f_preflight')
        kept = copy.deepcopy(alias)
        kept['id'] = 'f_checksheet'
        p['features'].append(kept)
        alias.update(disposition='merge', target='f_checksheet')
        for screen in p['screens']:
            screen['feature_ids'] = ['f_checksheet' if fid == 'f_preflight' else fid
                                     for fid in screen['feature_ids']]
        self.assertEqual('PASS', validator.validate(b, p)['status'])
        p['navigation'] = [n for n in p['navigation']
                           if 'f_checksheet' not in next(s for s in p['screens'] if s['id'] == n['to'])['feature_ids']]
        result = validator.validate(b, p)
        self.assertEqual('FAIL', result['status'], result)
        self.assertIn('REQUIRED_CAPABILITY_UNREACHABLE', {i['code'] for i in result['issues']})
